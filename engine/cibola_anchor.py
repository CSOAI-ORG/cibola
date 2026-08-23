#!/usr/bin/env python3
"""cibola_anchor.py — externally anchor a CIBOLA measurement card.

Produces a real, third-party timestamp/transparency-log anchor for a card's
digest, so a signed card is not merely self-anchored: an independent TIME and
LOG bind the card's fingerprint to a moment in time.

Primary anchor: RFC 3161 TSA (default https://rfc3161.ai.moda). The TSA issues a
TimeStampToken whose MessageImprint = sha256 of the card's canonical digest; a
stranger verifies PKIStatus + that the imprint matches THIS card.

Optional second anchor: a Rekor / transparency-log entry (best-effort; the v2
entry schema may vary). Anchor presence is recorded; verification is honest
about whether each anchor verified.

Requires `asn1crypto` (pip install asn1crypto) for the RFC 3161 TSR messaging.
The private signing key NEVER leaves the pod — anchors bind a PUBLIC digest.
"""
from __future__ import annotations
import base64, hashlib, json, urllib.request, urllib.error
from datetime import datetime, timezone

TSA_DEFAULT = "https://rfc3161.ai.moda"
REKOR_DEFAULT = "https://rekor.sigstore.dev/api/v1/log/entries"
HASH = "sha256"


def _asn1crypto():
    try:
        import asn1crypto
        return asn1crypto
    except ImportError:
        raise SystemExit("RFC 3161 anchoring needs asn1crypto: pip install asn1crypto")


def card_digest(card: dict) -> str:
    """sha256 hex of the card's canonical form (the same digest the receipt binds)."""
    from cibola_sign import canonical
    return hashlib.sha256(canonical(card)).hexdigest()


def tsa_timestamp(digest_hex: str, tsa_url: str = TSA_DEFAULT) -> dict:
    """Get an RFC 3161 TimeStampToken for a sha256 digest hex. Returns + verifies."""
    asn1crypto = _asn1crypto()
    from asn1crypto import tsp, algos
    digest_bytes = bytes.fromhex(digest_hex)
    mi = tsp.MessageImprint({'hash_algorithm': algos.DigestAlgorithm({'algorithm': 'sha256'}),
                             'hashed_message': digest_bytes})
    req = tsp.TimeStampReq({'version': 'v1', 'message_imprint': mi, 'cert_req': True})
    r = urllib.request.Request(tsa_url, data=req.dump(),
                               headers={'Content-Type': 'application/timestamp-query',
                                        'Accept': 'application/timestamp-reply'}, method='POST')
    try:
        resp = urllib.request.urlopen(r, timeout=30).read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"TSA HTTP {e.code}: {e.read().decode()[:120]}")
    tsr = tsp.TimeStampResp.load(resp)
    pki = int(tsr['status']['status'])
    if pki != 0:
        raise RuntimeError(f"TSA returned PKIStatus {pki} (not granted)")
    tok = tsr['time_stamp_token']
    ci = asn1crypto.cms.ContentInfo.load(tok.dump())
    inner = ci['content']['encap_content_info']['content'].native
    tsti = tsp.TSTInfo.load(inner).native if isinstance(inner, (bytes, bytearray)) else inner
    imprint_ok = bytes(tsti['message_imprint']['hashed_message']) == digest_bytes
    return {
        "kind": "tsa-rfc3161",
        "tsa_url": tsa_url,
        "digest_sha256": digest_hex,
        "gen_time": str(tsti['gen_time']),
        "policy": str(tsti['policy']),
        "serial": str(tsti['serial_number']),
        "message_imprint_matches": imprint_ok,
        "tsr_b64": base64.b64encode(resp).decode(),
    }


def rekor_entry(digest_hex: str, *, public_key_bytes: bytes | None = None,
                signature: bytes | None = None, rekor_url: str = REKOR_DEFAULT) -> dict:
    """Attempt a Rekor transparency-log entry for a digest (corrected Rekor v1 schema).

    The public rekor.sigstore.dev is Rekor v1 and expects the entry as a TOP-LEVEL
    request: {"kind":"hashedrekord","apiVersion":"0.0.1","spec":{data.hash, signature}}.
    It requires SHA-512, a PEM Ed25519 public key, and a signature that Rekor's
    internal verifier accepts over the submitted content (the sigstore/certificate
    signing flow). We submit the fully-formed entry when a key+signature are supplied;
    otherwise we report the exact dependency honestly rather than fake inclusion.
    """
    import hashlib as _h
    import base64 as _b64
    if public_key_bytes is None or signature is None:
        return {"kind": "rekor-transparency-log", "rekor_url": rekor_url, "recorded": False,
                "schema": "rekor-v1", "note": "rekor v1 needs a PEM Ed25519 public key + a verified "
                "sigstore-signature; not available here — see the RFC 3161 TSA anchor for the "
                "authoritative external time-binding."}
    pem_pub = public_key_bytes.public_bytes(
        encoding=__import__("cryptography").hazmat.primitives.serialization.Encoding.PEM,
        format=__import__("cryptography").hazmat.primitives.serialization.PublicFormat.SubjectPublicKeyInfo)
    pem_pub_b64 = _b64.b64encode(pem_pub).decode()
    sig_b64 = _b64.b64encode(signature).decode()
    # Rekor v1 hashedrekord: sha512 hash + Ed25519 signature + PEM public key.
    body = {"kind": "hashedrekord", "apiVersion": "0.0.1", "spec": {
        "data": {"hash": {"algorithm": "sha512", "value": _h.sha512(bytes.fromhex(digest_hex)).hexdigest()}},
        "signature": {"content": sig_b64, "format": "x509", "publicKey": {"content": pem_pub_b64}}}}
    r = urllib.request.Request(rekor_url, data=json.dumps(body).encode(),
                               headers={'Content-Type': 'application/json'}, method='POST')
    try:
        resp = urllib.request.urlopen(r, timeout=30).read()
        data = json.loads(resp.decode())
        k = list(data.keys())[0]
        return {"kind": "rekor-transparency-log", "rekor_url": rekor_url,
                "entry_uuid": k, "log_index": data[k].get('logIndex'),
                "integrated_time": data[k].get('integratedTime'),
                "signed_entry_timestamp": bool(data[k].get('signedEntryTimestamp')), "recorded": True}
    except urllib.error.HTTPError as e:
        return {"kind": "rekor-transparency-log", "rekor_url": rekor_url, "recorded": False,
                "schema": "rekor-v1", "error": f"HTTP {e.code}: {e.read().decode()[:140]}"}
    except Exception as e:
        return {"kind": "rekor-transparency-log", "rekor_url": rekor_url, "recorded": False,
                "schema": "rekor-v1", "error": f"{type(e).__name__}: {e}"}


def anchor_card(card: dict, *, tsa_url: str = TSA_DEFAULT, do_rekor: bool = True,
                rekor_key=None) -> dict:
    """Anchor a card: RFC 3161 TSA (required) + optional Rekor. Honest about each.

    rekor_key: optional Ed25519 private key used to sign the rekor entry request.
    If absent, rekor_entry reports the exact sigstore-signing dependency honestly."""
    digest_hex = card_digest(card)
    anchors = [tsa_timestamp(digest_hex, tsa_url)]
    if do_rekor:
        sig, pub = None, None
        if rekor_key is not None:
            from cibola_sign import canonical
            pub = rekor_key.public_key()
            sig = rekor_key.sign(canonical(card))
        anchors.append(rekor_entry(digest_hex, public_key_bytes=pub, signature=sig))
    return {
        "schema": "csoai.card-anchor/0.1",
        "kind": "measurement-card anchor — a TIME binding, not a certification",
        "register": "Anchoring binds a card's digest to an external timestamp/log. "
                    "It is not a certification, endorsement, or conformity mark.",
        "card_content_sha256": digest_hex,
        "anchored_at": datetime.now(timezone.utc).isoformat(),
        "anchors": anchors,
    }

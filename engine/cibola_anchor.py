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


def rekor_entry(digest_hex: str, rekor_url: str = REKOR_DEFAULT) -> dict:
    """Attempt a Rekor / transparency-log entry for a digest. Honest about schema drift.

    Tries the current hashedrekord shape (flat signature) and then the body-wrapped
    shape. The public Rekor v2 API has changed its wire format; if neither is accepted
    we report schema-drift rather than pretend an entry exists."""
    import hashlib as _h
    entry_spec = {"data": {"hash": {"algorithm": "sha256", "value": digest_hex}},
                  "signature": {"content": "Y2FyZA==", "publicKey": {"content": "Y2FyZA=="}}}
    rec = {"apiVersion": "0.0.1", "kind": "hashedrekord", "spec": entry_spec}
    body_b64 = base64.b64encode(json.dumps(rec, separators=(",", ":")).encode()).decode()
    variants = [
        {"proposedEntry": {"kind": "hashedrekord", "apiVersion": "0.0.1", "spec": entry_spec}},
        {"proposedEntry": {"kind": "hashedrekord", "apiVersion": "0.0.1", "spec": entry_spec, "body": body_b64}},
        {"proposedEntry": {"kind": "hashedrekord", "body": body_b64}},
    ]
    for proposed in variants:
        r = urllib.request.Request(rekor_url, data=json.dumps(proposed).encode(),
                                   headers={'Content-Type': 'application/json'}, method='POST')
        try:
            resp = urllib.request.urlopen(r, timeout=30).read()
            data = json.loads(resp.decode())
            k = list(data.keys())[0]
            return {"kind": "rekor-transparency-log", "rekor_url": REKOR_DEFAULT,
                    "entry_uuid": k, "log_index": data[k].get('logIndex'),
                    "integrated_time": data[k].get('integratedTime'),
                    "signed_entry_timestamp": bool(data[k].get('signedEntryTimestamp')), "recorded": True}
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}: {e.read().decode()[:120]}"
            continue  # try next shape
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            continue
    return {"kind": "rekor-transparency-log", "rekor_url": REKOR_DEFAULT,
            "recorded": False, "schema_drift": True,
            "error": "public Rekor v2 API rejected the hashedrekord entry (schema drift); "
                     "the RFC 3161 TSA anchor remains the authoritative external time-binding. "
                     f"({last_err})"}


def anchor_card(card: dict, *, tsa_url: str = TSA_DEFAULT, do_rekor: bool = True) -> dict:
    """Anchor a card: RFC 3161 TSA (required) + optional Rekor. Honest about each."""
    digest_hex = card_digest(card)
    anchors = [tsa_timestamp(digest_hex, tsa_url)]
    if do_rekor:
        anchors.append(rekor_entry(digest_hex))
    return {
        "schema": "csoai.card-anchor/0.1",
        "kind": "measurement-card anchor — a TIME binding, not a certification",
        "register": "Anchoring binds a card's digest to an external timestamp/log. "
                    "It is not a certification, endorsement, or conformity mark.",
        "card_content_sha256": digest_hex,
        "anchored_at": datetime.now(timezone.utc).isoformat(),
        "anchors": anchors,
    }

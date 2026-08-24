#!/usr/bin/env python3
"""scitt_verify.py — cryptographic SCITT COSE_Sign1 verifier (RFC 9052 / RFC 9943).

NEXT-100 v4 move 31 — "SCITT COSE_Sign1 verify (not just count)".

Today SCITT statements are COUNTED ('201 COSE-wrapped SCITT statements'); counting is
not verifying. This module turns 'seen' into 'cryptographically proven' per statement:
it decodes the CBOR COSE_Sign1 envelope, reconstructs the RFC 9052 Sig_structure, and
checks the Ed25519 (alg -19) signature over it with `cryptography`. Stranger-only — no
signing key, no pod, no network.

Honest register (verbatim from canon): a verified COSE_Sign1 signature proves the
signing key signed THIS exact content. It is NOT a certification, endorsement, or
conformity mark, and must not be presented as one. A statement whose signing key is not
pinned to a trusted identity is reported 'self-consistent but NOT pinned' — never as
verified-authentic.

The verifier pins the signing key to the published did:web:csoai.org Ed25519 identities
(the same trust root dorado_sign uses) or to an expected_pubkey the caller supplies. An
unpinned key only proves internal consistency (the envelope is intact), not authenticity.
"""
from __future__ import annotations
import base64, hashlib, json
import cbor2
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

# COSE header labels (RFC 9052 §3.1)
_ALG = 1
_KID = 4
_CRV = -1
_X = -2          # public key x-coordinate (Ed25519 raw) in the unprotected header
_KTY = -3
_ALG_ED25519 = -19
_CRV_ED25519 = 6

# Published did:web:csoai.org Ed25519 identities (x = base64url) — the trust root.
# Mirrors engine/dorado_sign.PUBLISHED_IDENTITIES so a stranger can pin without the pod.
PUBLISHED_IDENTITIES = {
    "did:web:csoai.org#card-attestation-1": "1MsOqhbV9Qv3Yzo2qjT-CaVeEkuTFt7Sq9sSK7nDfjg",
    "did:web:csoai.org#estate-chain-1": "M0cuAmhx2yDNvZnnbEdTLr_PhLN6vtWyYNrjWJ31aW0",
    "did:web:csoai.org#site-release-1": "03g9l-dVNGVEAVVWQrJU9aLtkYTN3uARd52P7DEq-8g",
    "did:web:csoai.org#board-attestation-1": "k2fPWb6ctyu8l5at8FYgHsHFit_qoT-DssW3VNbCAXA",
}
KID_DEFAULT = "did:web:csoai.org#card-attestation-1"


def _raw_norm(pubkey_raw: bytes) -> bytes:
    return pubkey_raw


def _pub_thumbs(pubkey_raw: bytes) -> dict:
    """RFC 9679 JWK thumbprint (sha256, base64url) + b64url x for a raw Ed25519 pubkey."""
    x_b64url = base64.urlsafe_b64encode(pubkey_raw).rstrip(b"=").decode()
    jwk = json.dumps({"crv": "Ed25519", "kty": "OKP", "x": x_b64url}, separators=(",", ":"))
    thumbs = base64.urlsafe_b64encode(hashlib.sha256(jwk.encode()).digest()).rstrip(b"=").decode()
    return {"thumbprint": thumbs, "x_b64url": x_b64url}


def _pub_from_expected(pubkey_expected) -> bytes:
    """Accept base64url-x, base64-x, or raw bytes for an expected public key."""
    if isinstance(pubkey_expected, bytes):
        return pubkey_expected
    if isinstance(pubkey_expected, dict):
        x = pubkey_expected.get("x") or pubkey_expected.get("pubkey_x") or ""
        return base64.urlsafe_b64decode(x + "=" * (-len(x) % 4))
    s = str(pubkey_expected)
    # base64url (do it first; safe chars only)
    if all(c in "-_A-Za-z0-9" and c != "=" for c in s):
        return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
    return base64.b64decode(s + "=" * (-len(s) % 4))


def decode_cose_sign1(envelope: bytes) -> dict:
    """Decode a CBOR COSE_Sign1 envelope (RFC 9052 §4.2).

    Returns {protected, unprotected, payload, signature} where protected/unprotected
    are the RAW byte strings (as they appear in the envelope) and payload/signature are
    byte strings. Raises ValueError on a non-COSE_Sign1 or malformed input.
    """
    try:
        obj = cbor2.loads(envelope)
    except Exception as e:
        raise ValueError(f"not CBOR: {e}")
    # COSE_Sign1 is CBOR tag 18 wrapping the array
    if isinstance(obj, cbor2.CBORTag) and obj.tag == 18:
        arr = obj.value
    elif isinstance(obj, list) and len(obj) == 4:
        arr = obj
    else:
        raise ValueError("not a COSE_Sign1 envelope (expected CBOR tag 18, got a 4-element payload)")
    if len(arr) != 4:
        raise ValueError(f"COSE_Sign1 must have 4 elements, got {len(arr)}")
    protected, unprotected, payload, signature = arr
    if not isinstance(protected, bytes) or not isinstance(unprotected, bytes) \
            or not isinstance(payload, bytes) or not isinstance(signature, bytes):
        raise ValueError("COSE_Sign1 elements must be byte strings")
    # protected/unprotected are themselves CBOR-encoded maps (possibly empty)
    try:
        prot_map = cbor2.loads(protected) if protected else {}
        unp_map = cbor2.loads(unprotected) if unprotected else {}
    except Exception as e:
        raise ValueError(f"protected/unprotected header not CBOR map: {e}")
    if not isinstance(prot_map, dict) or not isinstance(unp_map, dict):
        raise ValueError("COSE headers must be maps")
    return {"protected": protected, "unprotected": unprotected,
            "protected_map": prot_map, "unprotected_map": unp_map,
            "payload": payload, "signature": signature}


def sig_structure(protected: bytes, payload: bytes, external_aad: bytes = b"") -> bytes:
    """The RFC 9052 Sig_structure CBOR-encoded — the bytes Ed25519 signs.

    Sig_structure = [ "Signature1", protected-body, external_aad, payload ] where the
    four elements are text("Signature1"), bstr(protected), bstr(external_aad), bstr(payload).
    """
    return cbor2.dumps(["Signature1", protected, external_aad, payload])


def _recover_pubkey(prot_map: dict, unp_map: dict, expected_pubkey=None) -> tuple[bytes | None, str]:
    """Recover the Ed25519 public key. Returns (raw_pubkey, source-label) or (None, reason).

    Precedence: caller-pinned expected_pubkey (trusted), then the unprotected header's
    embedded x (-2) — which only proves self-consistency, never authenticity.
    """
    if expected_pubkey is not None:
        try:
            return _pub_from_expected(expected_pubkey), "caller-pinned"
        except Exception as e:
            return None, f"bad expected pubkey: {e}"
    x_raw = unp_map.get(_X)
    if isinstance(x_raw, bytes) and len(x_raw) == 32:
        return x_raw, "org-embedded (self-consistent only)"
    return None, "no trusted pubkey (not pinned; header carries no x)"


def verify_cose_sign1(envelope: bytes, *, expected_pubkey=None, expected_kid=None,
                      permit_unpinned: bool = False) -> dict:
    """Cryptographically verify ONE COSE_Sign1 envelope.

    Returns an honest verdict dict; `ok` True only when the signature verifies AND (the
    signing key is pinned to a trusted identity OR expected_pubkey is pinned). An unpinned
    but internally-consistent envelope reports ok=False with reason 'self-consistent but
    NOT pinned' unless permit_unpinned=True (which downgrades the claim, never the reverse).
    """
    try:
        d = decode_cose_sign1(envelope)
    except ValueError as e:
        return {"ok": False, "reason": f"malformed envelope: {e}"}
    prot_map, unp_map = d["protected_map"], d["unprotected_map"]
    alg = prot_map.get(_ALG)
    kid = prot_map.get(_KID) or unp_map.get(_KID)
    # verify the algorithm must be Ed25519
    if alg != _ALG_ED25519:
        return {"ok": False, "reason": f"unsupported alg {alg!r} (only Ed25519 -19 supported)"}
    if expected_kid is not None and kid != expected_kid:
        return {"ok": False, "reason": f"kid mismatch (envelope {kid!r}, expected {expected_kid!r})"}
    # recover the key
    pub, key_source = _recover_pubkey(prot_map, unp_map, expected_pubkey)
    if pub is None:
        # No caller-pinned key and the envelope embeds no x -> honest 'cannot verify'.
        if expected_pubkey is None:
            return {"ok": False, "reason": f"cannot verify: kid '{kid}' is not a published identity and the envelope embeds no key; pass expected_pubkey or permit_unpinned"}
        return {"ok": False, "reason": key_source}
    # pin to a trusted identity: match kid against the published did:web set
    pinned = None
    if expected_pubkey is not None:
        pinned = expected_kid or kid or KID_DEFAULT
    elif kid in PUBLISHED_IDENTITIES:
        x = base64.urlsafe_b64decode(PUBLISHED_IDENTITIES[kid] + "=" * (-len(PUBLISHED_IDENTITIES[kid]) % 4))
        if x == pub:
            pinned = kid
        else:
            return {"ok": False, "reason": f"kid '{kid}' in trust set, but envelope key does not match the published identity"}
    elif not permit_unpinned:
        # Distinguish: embedded own-key (self-consistent, weaker) vs no key at all.
        if _X in unp_map:
            return {"ok": False, "reason": f"self-consistent but NOT pinned: envelope embeds its own key for kid '{kid}' which is not a published identity — this proves the signed content was not altered, NOT that it came from did:web:csoai.org. Pass expected_pubkey to pin."}
        return {"ok": False, "reason": f"cannot verify: kid '{kid}' is not a published identity and the envelope embeds no key; pass expected_pubkey or permit_unpinned"}
    # verify the signature over the Sig_structure
    try:
        pk = Ed25519PublicKey.from_public_bytes(pub)
        pk.verify(d["signature"], sig_structure(d["protected"], d["payload"]))
    except Exception:
        return {"ok": False, "reason": "INVALID — Ed25519 signature does not verify (tampered or wrong key)"}
    tp = _pub_thumbs(pub)
    return {
        "ok": True,
        "reason": (f"VALID COSE_Sign1 (measurement, never certification) — {pinned or key_source}"
                   + (f", kid={pinned}" if pinned else ", self-consistent not pinned")),
        "alg": alg, "kid": kid, "payload_len": len(d["payload"]),
        "pubkey_x_b64url": tp["x_b64url"], "pubkey_thumbprint": tp["thumbprint"],
        "pinned_to": pinned or None,
        "sig_structure_verified": True,
    }


def verify_signed_item(item, *, expected_kid=None, expected_pubkey=None) -> dict:
    """Verify a self-contained signed item: raw bytes OR a JSON doc with a b64 `cose` field.

    `cose` may be base64 (standard) or base64url; both decode cleanly. A doc without a
    `cose` field is reported as unverifiable (no COSE envelope present)."""
    env = None
    if isinstance(item, (bytes, bytearray)):
        env = bytes(item)
    elif isinstance(item, dict):
        for k in ("cose", "envelope", "cose_sign1"):
            if isinstance(item.get(k), str):
                s = item[k].strip()
                try:
                    env = base64.b64decode(s + "=" * (-len(s) % 4))
                except Exception:
                    env = None
                break
    if env is None:
        return {"ok": False, "reason": "no COSE_Sign1 envelope present in item", "verdict": "absent"}
    v = verify_cose_sign1(env, expected_kid=expected_kid, expected_pubkey=expected_pubkey)
    return v


def verify_batch(items, *, expected_kid=None, expected_pubkey=None) -> dict:
    """Verify a batch of signed items; returns a count + per-item honest verdicts.

    A verified count is genuinely cryptographic: each row is independently checked, never
    assumed from a header counter. Rows that fail or have no trusted key are counted
    separately and never folded into the verified set."""
    results = []
    verified = failed = unverifiable = 0
    for it in items:
        v = verify_signed_item(it, expected_kid=expected_kid, expected_pubkey=expected_pubkey)
        if v.get("ok"):
            verified += 1
            verdict = "verified"
        elif v.get("reason", "").startswith("self-consistent"):
            unverifiable += 1
            verdict = "unverifiable-self-consistent"
        elif v.get("reason", "").startswith("no COSE"):
            unverifiable += 1
            verdict = "absent"
        else:
            failed += 1
            verdict = "failed"
        results.append({"verdict": verdict, "reason": v.get("reason", ""), "kid": v.get("kid")})
    return {"n": len(items), "verified": verified, "failed": failed,
            "unverifiable": unverifiable, "results": results}


def build_cose_sign1(payload: bytes, private_key, kid: str, *, alg: int = _ALG_ED25519) -> bytes:
    """Build a COSE_Sign1 envelope (tag 18) — used ONLY for hermetic fixtures / selfcheck.

    This carries kid=test in real use. It never claims a production identity; the pod key
    ceremony (real signing) is described in the draft, never invoked from this repo."""
    protected = cbor2.dumps({_ALG: alg, _KID: kid})
    unprotected = cbor2.dumps({})
    sig = private_key.sign(sig_structure(protected, payload))
    return cbor2.dumps(cbor2.CBORTag(18, [protected, unprotected, payload, sig]))

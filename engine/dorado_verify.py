#!/usr/bin/env python3
"""dorado_verify.py — STRANGER verifier for DORADO measurement cards.

A stranger verifies a signed card with ONLY:
  1. the card itself (embeds signature.pubkey + sig), and
  2. the `cryptography` library.

No signing key, no pod, no network. Optional: pass the expected public key /
did:web key so the kid and thumbprint must ALSO match the published identity.

Usage:
    python3 dorado_verify.py <card.json> [expected_pubkey_b64]

Prints VALID (exit 0) or INVALID (exit 1). Never trusts the card's self-asserted
identity unless a reference pubkey is supplied.
"""
from __future__ import annotations
import base64, json, os, sys
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dorado_sign import canonical, rfc9679_thumbprint  # same canonical form


def verify_card(card: dict, expected_pubkey_b64: str | None = None) -> dict:
    """Return {ok, reason, kid, thumbprint} — never raises for a bad signature."""
    s = card.get("signature")
    if not isinstance(s, dict) or s.get("kind") != "ed25519":
        return {"ok": False, "reason": "NO ED25519 SIGNATURE — may be an honestly-unsigned card"}
    try:
        pk = Ed25519PublicKey.from_public_bytes(base64.b64decode(s["pubkey"]))
    except Exception as e:
        return {"ok": False, "reason": f"bad pubkey: {e}"}
    try:
        pk.verify(base64.b64decode(s["sig"]), canonical(card))
    except Exception:
        return {"ok": False, "reason": "INVALID — signature does not verify; card altered or wrong key"}
    # identity binding (only if a reference key is supplied)
    if expected_pubkey_b64:
        if s["pubkey"] != expected_pubkey_b64:
            return {"ok": False, "reason": "INVALID — signed by a key that is not the published identity"}
    thumb = rfc9679_thumbprint(pk.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw))
    return {"ok": True, "reason": "VALID", "kid": s.get("kid"), "thumbprint": thumb,
            "pubkey_matches": (s.get("pubkey_thumbprint") == thumb)}


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit("usage: python3 dorado_verify.py <card.json> [expected_pubkey_b64]")
    card = json.load(open(sys.argv[1]))
    res = verify_card(card, sys.argv[2] if len(sys.argv) > 2 else None)
    print(f"{res['reason']}" + (f" (kid={res.get('kid')})" if res.get("kid") else ""))
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

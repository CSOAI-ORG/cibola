#!/usr/bin/env python3
"""cibola_receipt_verify.py — STRANGER verifier for a CIBOLA SCITT receipt.

A stranger verifies a receipt with ONLY the receipt + the `cryptography`
library (no signing key, no pod). Recomputes content_id, checks the Ed25519
signature, and (optionally) confirms the receipt's content_id matches a given
card's digest — proving THIS receipt attests to THAT specific card.

Usage:
    python3 cibola_receipt_verify.py <receipt.json> [card.json]

Prints the receipt register is a measurement, never a certification.
"""
from __future__ import annotations
import base64, json, os, sys, hashlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cibola_receipt import canonical, content_id, content_id as cid_of


def verify_receipt(receipt: dict, card: dict | None = None) -> dict:
    r = receipt
    # recompute content_id over canonical (minus signature/content_id fields)
    recomputed = content_id(r)
    if recomputed != r.get("content_id"):
        return {"ok": False, "reason": f"content_id mismatch (got {recomputed[:12]}…, card says {str(r.get('content_id'))[:12]}…)"}
    s = r.get("signature")
    if not isinstance(s, dict) or not s.get("sig"):
        return {"ok": False, "reason": "receipt is unsigned (no signature) — honestly-unsigned"}
    try:
        pk = Ed25519PublicKey.from_public_bytes(base64.b64decode(s["pubkey"]))
    except Exception as e:
        return {"ok": False, "reason": f"bad pubkey: {e}"}
    try:
        pk.verify(base64.b64decode(s["sig"]), canonical(r))
    except Exception:
        return {"ok": False, "reason": "INVALID — receipt signature does not verify"}
    # bind to a card, if given: the receipt's subject_content_sha256 must equal the card digest
    card_msg = None
    if card is not None:
        from cibola_sign import canonical as card_canonical
        card_digest = hashlib.sha256(card_canonical(card)).hexdigest()
        if r.get("subject_content_sha256") != card_digest:
            return {"ok": False, "reason": f"receipt does NOT attest to this card (receipt={r.get('subject_content_sha256','')[:12]}…, card={card_digest[:12]}…)"}
        card_msg = f" — attests to card {card_digest[:12]}…"
    return {"ok": True, "reason": "VALID receipt (measurement, not certification)" + (card_msg or ""),
            "content_id": recomputed, "kid": s.get("kid")}


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit("usage: python3 cibola_receipt_verify.py <receipt.json> [card.json]")
    receipt = json.load(open(sys.argv[1]))
    card = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else None
    res = verify_receipt(receipt, card)
    print(res["reason"])
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

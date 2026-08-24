#!/usr/bin/env python3
"""dorado_receipt_verify.py — STRANGER verifier for a DORADO SCITT receipt.

A stranger verifies a receipt with ONLY the receipt + the `cryptography`
library (no signing key, no pod). Recomputes content_id, checks the Ed25519
signature, and (optionally) confirms the receipt's content_id matches a given
card's digest — proving THIS receipt attests to THAT specific card.

Usage:
    python3 dorado_receipt_verify.py <receipt.json> [card.json]

Prints the receipt register is a measurement, never a certification.
"""
from __future__ import annotations
import base64, json, os, sys, hashlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dorado_receipt import canonical, content_id, content_id as cid_of, jcs


def _verify_core(receipt: dict) -> dict:
    """Verify the receipt envelope itself (content_id + Ed25519 signature).

    Shared by the card verifier and the scenario verifier. Stranger-only: no signing key,
    no pod — only the receipt and `cryptography`."""
    r = receipt
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
    return {"ok": True, "reason": "receipt signature valid", "content_id": recomputed, "kid": s.get("kid")}


def verify_receipt(receipt: dict, card: dict | None = None) -> dict:
    r = receipt
    core = _verify_core(r)
    if not core["ok"]:
        return core
    # bind to a card, if given: the receipt's subject_content_sha256 must equal the card digest
    card_msg = None
    if card is not None:
        from dorado_sign import canonical as card_canonical
        card_digest = hashlib.sha256(card_canonical(card)).hexdigest()
        if r.get("subject_content_sha256") != card_digest:
            return {"ok": False, "reason": f"receipt does NOT attest to this card (receipt={r.get('subject_content_sha256','')[:12]}…, card={card_digest[:12]}…)"}
        card_msg = f" — attests to card {card_digest[:12]}…"
    return {"ok": True, "reason": "VALID receipt (measurement, not certification)" + (card_msg or ""),
            "content_id": core["content_id"], "kid": core["kid"]}


def verify_scenario_receipt(receipt: dict, payload: dict | None = None,
                            kinds: tuple[str, ...] = ("scenario",)) -> dict:
    """Stranger-verify a SCENARIO receipt (move 43), optionally binding it to a payload.

    `payload` is the SAME JSON object passed to build_scenario_receipt. If given, the
    receipt's subject_content_sha256 must equal sha256(jcs(payload)) — proving THIS
    receipt attests to THAT payload. If omitted, verifies only the envelope (self-consistency
    + signature); the payload digest is cross-checked by re-running jcs.

    `kinds` is the set of receipt kinds accepted by this verifier (default ("scenario",)).
    A caller reusing the JCS path for another record kind — e.g. `"score"` for the move-59
    Inspect scorer hook — passes kinds=("score",); the default preserves the existing
    kind check exactly.
    """
    r = receipt
    core = _verify_core(r)
    if not core["ok"]:
        return core
    if r.get("kind") not in kinds:
        return {"ok": False, "reason": f"not a scenario receipt (kind={r.get('kind')!r})"}
    kind_label = r.get("kind", "scenario")
    payload_msg = None
    if payload is not None:
        # JCS payload-binding: canon is RFC 8785, so the digest is deterministic + cross-language
        payload_digest = hashlib.sha256(jcs(payload).encode()).hexdigest()
        if r.get("subject_content_sha256") != payload_digest:
            return {"ok": False, "reason": f"receipt does NOT attest to this scenario (receipt={r.get('subject_content_sha256','')[:12]}…, payload={payload_digest[:12]}…)"}
        payload_msg = f" — attests to scenario {payload_digest[:12]}…"
    return {"ok": True, "reason": f"VALID {kind_label} receipt (measurement, not certification)" + (payload_msg or ""),
            "content_id": core["content_id"], "kid": core["kid"]}


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit("usage: python3 dorado_receipt_verify.py <receipt.json> [card.json]")
    receipt = json.load(open(sys.argv[1]))
    card = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else None
    res = verify_receipt(receipt, card)
    print(res["reason"])
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

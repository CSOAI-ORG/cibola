#!/usr/bin/env python3
"""test/frozen-vectors-kit.py — close the move-6 <-> move-17 gap (verify-kit integration).

The frozen vectors (move 6, test/vectors/) are the estate's PINNED stranger-verification
fixtures. The offline verify-kit (move 17, harness/verify_kit.py) is the self-contained
artifact a stranger downloads and verifies WITHOUT network/pod/private-key. This test
integrates the two surfaces: it packs the frozen VALID card + receipt into ONE offline
verify-kit and stranger-verifies the WHOLE kit, then proves the frozen BAD vectors fail
through the SAME kit path. This is the seam the estate must never break.

It is hermetic + deterministic (no network, no pod, no production key; the frozen test
identity is pinned in the fixtures, generated_at is pinned).

Register (verbatim from canon): a verify-kit is a measurement device, never a certification.
"""
from __future__ import annotations
import base64, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTORS_DIR = os.path.join(ROOT, "test", "vectors")
sys.path.insert(0, os.path.join(ROOT, "harness"))
sys.path.insert(0, os.path.join(ROOT, "engine"))
sys.path.insert(0, ROOT)

from verify_kit import build_verify_kit, verify_verify_kit, kit_digest  # noqa: E402
from engine.dorado_sign import rfc9679_thumbprint  # noqa: E402
from engine.dorado_verify import verify_card  # noqa: E402
from engine.dorado_receipt_verify import verify_receipt  # noqa: E402

PINNED_TS = "2026-08-24T00:00:00Z"


def _load(rel: str) -> dict:
    return json.load(open(os.path.join(VECTORS_DIR, rel), encoding="utf-8"))


def _caller_trusted_from_card(card: dict) -> dict:
    """Derive the caller-trusted identity set from the frozen card's own published pubkey.

    This is what a stranger holds independently from did:web (the trust root). It must
    EXACTLY match the card's kid + raw Ed25519 pubkey + RFC 9679 thumbprint so the pin is
    a real identity assertion, not a self-consistency coincidence.
    """
    sig = card["signature"]
    kid = sig["kid"]
    raw = base64.b64decode(sig["pubkey"])
    x = base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
    thumb = rfc9679_thumbprint(raw)
    return {kid: {"x": x, "thumbprint": thumb}}


def main() -> int:
    card_valid = _load("card-valid.json")
    card_bad_sig = _load("card-bad-sig.json")
    receipt_valid = _load("receipt-valid.json")
    receipt_bad = _load("receipt-bad.json")

    # Sanity: the fixtures behave as pinned before we integrate them into the kit.
    assert verify_card(card_valid)["ok"], "precondition: card-valid stranger-verifies"
    assert not verify_card(card_bad_sig)["ok"], "precondition: card-bad-sig fails"
    assert verify_receipt(receipt_valid, card_valid)["ok"], "precondition: receipt-valid binds"
    assert not verify_receipt(receipt_bad, card_valid)["ok"], "precondition: receipt-bad NOT bound"

    checks = 0

    def check(cond, msg):
        nonlocal checks
        checks += 1
        assert cond, f"FAIL: {msg}"
        print(f"  ok {checks:02d} — {msg}")

    print("== Frozen vectors <-> offline verify-kit integration (moves 6 + 17) ==")

    # 1. Pack the frozen VALID card + receipt into ONE offline verify-kit.
    kit = build_verify_kit(card_valid, receipts=[receipt_valid], generated_at=PINNED_TS)
    check(kit["schema"] == "csoai.verify-kit/0.1", "kit schema == csoai.verify-kit/0.1")
    check("card.json" in kit["contents"] and "receipt.json" in kit["contents"] and "keys.json" in kit["contents"],
          "kit packs card.json + receipt.json + keys.json")
    check(kit["digest"] == kit_digest(kit), "kit digest self-consistent (canonical minus digest)")

    # 2. Default (kit-BUNDLED did:web identities): the frozen test identity is NOT a real
    #    did:web identity, so the honest verdict is NOT fully verified — a test key in a
    #    self-bundled key set is never mistaken for an independently-fetched did:web root.
    v_bundled = verify_verify_kit(kit)
    check(v_bundled["identity_source"] == "kit-bundled", "default identity source is kit-bundled")
    check(not v_bundled["ok"], "kit-bundled pin does NOT claim the frozen test identity (honest)")

    # 3. Caller-TRUSTED identity (what a stranger holds independently): the whole kit
    #    verifies OFFLINE — digest + card signature + receipt bind + identity pin.
    trusted = _caller_trusted_from_card(card_valid)
    v = verify_verify_kit(kit, trusted_keys=trusted)
    check(v["ok"], f"whole kit stranger-verifies offline against caller-trusted identity (reason: {v['reason']})")
    check(v["identity_source"] == "caller-trusted", "positive verify uses caller-trusted identity source")
    check(v["digest_ok"] and v["card_ok"] and v["keys_ok"], "digest + card + identity-pin all OK")
    check(v["verified_receipts"] == 1, "1 receipt verified in the frozen valid kit")

    # 4. Determinism: same frozen inputs + pinned generated_at -> identical kit digest/kit_id.
    kit_b = build_verify_kit(card_valid, receipts=[receipt_valid], generated_at=PINNED_TS)
    check(kit["digest"] == kit_b["digest"] and kit["kit_id"] == kit_b["kit_id"],
          "deterministic kit (frozen vectors -> same digest + kit_id across runs)")

    # 5. The frozen BAD-SIG card, packed into a kit + verified with its OWN tied-to-card
    #    identity, MUST fail at the card leg (the kit cannot be sold as verified).
    kit_badsig = build_verify_kit(card_bad_sig, receipts=[receipt_valid], generated_at=PINNED_TS)
    v_badsig = verify_verify_kit(kit_badsig, trusted_keys=_caller_trusted_from_card(card_bad_sig))
    check(not v_badsig["ok"] and not v_badsig["card_ok"],
          f"frozen bad-sig card -> kit NOT verified (card leg fails: {v_badsig['parts'][1]['reason'][:60]}…)")

    # 6. The frozen BAD-RECEIPT bound into the valid kit -> receipt bind fails at the kit leg.
    kit_badreceipt = build_verify_kit(card_valid, receipts=[receipt_bad], generated_at=PINNED_TS)
    v_badreceipt = verify_verify_kit(kit_badreceipt, trusted_keys=trusted)
    check(not v_badreceipt["ok"] and v_badreceipt["verified_receipts"] == 0,
          "frozen bad-receipt -> kit NOT verified (receipt does not bind this card)")

    print(f"\nFrozen-vectors <-> verify-kit integration: {checks} checks green "
          "(hermetic, deterministic, no network, no pod)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

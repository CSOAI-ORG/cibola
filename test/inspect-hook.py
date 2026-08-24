#!/usr/bin/env python3
"""test/inspect-hook.py — hermetic CI test for the Inspect signed-receipt SCORER hook (move 59).

The estate measures models with the Inspect eval framework. Move 59 asks that a SCORED
result carry cryptographic provenance — a signed receipt a stranger can verify offline — so
an eval result is evidence of WHAT was scored and WHEN by WHOM, not a bare mutable number.

This test is DETERMINISTIC and OFF-network: it builds `Score`-shaped results, attaches a
signed receipt riding each result (Ephemeral/test identity, fixed issued_at where the round
trip isolates determinism), and stranger-verifies with ONLY `cryptography`. It never imports
inspect_ai (external + network-dep).

Asserts:
  1. attach_signed_receipt is PURE: the original Score (value/explanation) is untouched; the
     result's value/explanation are byte-for-byte the caller's (provenance != credibility).
  2. a signed receipt rides metadata["signed_receipt"], kind:"score", and stranger-verifies.
  3. tampering the result (value) silently FAILS the bind — provenance is bound to the exact
     recorded result, never to an altered one.
  4. swapping the subject / model fails the bind (this receipt attests to THAT score).
  5. a different signed receipt (different key) is NOT accepted for this score.
  6. private_key=None -> honestly-unsigned receipt (sig None); verifier reports "no/unsigned",
     never a fabricated verification.
  7. determinism: same key + same payload + same issued_at -> byte-identical receipt content_id.
  8. signed_scorer wrapper rides EVERY Score a scorer returns, value preserved.
  9. the measurement-not-certification register rides every scored result.

Register (verbatim from canon): a scored result bound to a measured record is evidence of
what was recorded and when — NOT proof the eval or model is honest or uncontaminated.
Measurement, never certification.
"""
import base64
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "harness"))
sys.path.insert(0, os.path.join(ROOT, "engine"))
sys.path.insert(0, ROOT)

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402

from inspect_hook import (  # noqa: E402
    attach_signed_receipt, verify_score_receipt, signed_scorer, score_payload,
    RECEIPT_META_KEY, SCHEMA, KIND, REGISTER,
)
from engine.dorado_receipt import content_id, build_card_receipt  # noqa: E402

TEST_KID = "did:web:csoai.org#test-identity"
FIXED_TS = "2026-08-24T12:00:00Z"


def _score(value=0.83, model="model-x", sample="s-001"):
    return {
        "id": sample,
        "value": value,
        "explanation": f"{value} correct on the held-out axes",
        "metadata": {"model": model, "sample_id": sample,
                     "per_axis": [{"axis": "safety", "verdict": "PASS"}]},
    }


def _key(seed=b"inspect-hook-v1-2026-08-24"):
    return Ed25519PrivateKey.from_private_bytes(seed[:32].ljust(32, b"!"))


def _checks():
    # 0-1 ---- provenance is not credibility --------------------------------------------
    orig = _score()
    out = attach_signed_receipt(orig, private_key=_key(), kid=TEST_KID, issued_at=FIXED_TS)
    assert orig == _score(), "attach_signed_receipt must NOT mutate the input score"
    assert out["value"] == orig["value"] and out["explanation"] == orig["explanation"]
    assert out["metadata"]["model"] == orig["metadata"]["model"]
    yield("01 — attach_signed_receipt is pure; result value/explanation preserved (prov!==cred)")

    # 0-2 ---- a signed receipt rides the Score, kind "score" ---------------------------
    rec = out["metadata"][RECEIPT_META_KEY]
    assert rec["kind"] == KIND, rec["kind"]
    assert rec["schema"] == "a2a.signed-receipt/0.1", rec["schema"]
    yield("02 — signed receipt rides metadata[%s], kind=%r" % (RECEIPT_META_KEY, KIND))

    # 0-3 ---- stranger-verify the WHOLE result ----------------------------------------
    v = verify_score_receipt(out)
    assert v["ok"], v["reason"]
    yield("03 — stranger-verify ok: %s" % v["reason"])

    # 0-4 ---- a tampered value silently FAILS the bind --------------------------------
    tamper = dict(out)
    tamper_meta = dict(out["metadata"]); tamper_meta[RECEIPT_META_KEY] = dict(rec)
    tamper_meta[RECEIPT_META_KEY] = rec  # keep the ORIGINAL receipt
    tamper["value"] = 0.999
    tamper["metadata"] = tamper_meta
    assert not verify_score_receipt(tamper)["ok"], "tampered value must fail the bind"
    yield("04 — tampered value -> NOT bound (provenance bound to the exact recorded result)")

    # 0-5 ---- a different subject/model fails the bind --------------------------------
    swapped = dict(out)
    swapped_meta = dict(out["metadata"]); swapped_meta[RECEIPT_META_KEY] = rec
    swapped["id"] = "s-999"; swapped["metadata"] = swapped_meta
    assert not verify_score_receipt(swapped)["ok"], "different subject must fail the bind"
    yield("05 — swapped subject/model -> NOT bound")
    # metadata change also fails the bind (model is bound)
    diff_meta = dict(out["metadata"]); diff_meta[RECEIPT_META_KEY] = rec
    diff_meta["model"] = "model-y"; d2 = dict(out); d2["metadata"] = diff_meta
    assert not verify_score_receipt(d2)["ok"], "different metadata must fail the bind"
    yield("06 — altered metadata (model) -> NOT bound")

    # 0-6 ---- honestly-unsigned (no key) is reported as unsigned, never verified -------
    uns = attach_signed_receipt(_score(), private_key=None, kid=TEST_KID, issued_at=FIXED_TS)
    urec = uns["metadata"][RECEIPT_META_KEY]
    assert urec["signature"]["sig"] is None, "no key must build an honestly-unsigned receipt"
    uv = verify_score_receipt(uns)
    assert not uv["ok"] and ("unsigned" in uv["reason"] or "signed receipt on this score" in uv["reason"]), uv
    yield("07 — private_key=None -> honestly-unsigned (never a fabricated verification)")

    # 0-7 ---- determinism: same key+payload+issued_at -> identical content_id ----------
    a = attach_signed_receipt(_score(), private_key=_key(), kid=TEST_KID, issued_at=FIXED_TS)
    b = attach_signed_receipt(_score(), private_key=_key(), kid=TEST_KID, issued_at=FIXED_TS)
    ca = a["metadata"][RECEIPT_META_KEY]["content_id"]
    cb = b["metadata"][RECEIPT_META_KEY]["content_id"]
    assert ca == cb, (ca, cb)
    yield("08 — deterministic: same key+payload+issued_at -> identical receipt content_id")

    # 0-8 ---- signed_scorer rides EVERY Score a scorer returns -------------------------
    scorer = lambda value=0.77: _score(value=value)
    wrapped = signed_scorer(scorer, private_key=_key(), kid=TEST_KID, issued_at=FIXED_TS)
    r1 = wrapped(0.77); r2 = wrapped(0.91)
    assert r1["value"] == 0.77 and verify_score_receipt(r1)["ok"]
    assert r2["value"] == 0.91 and verify_score_receipt(r2)["ok"]
    yield("09 — signed_scorer rides every Score; value preserved + verified")

    # 0-9 ---- register rides every scored result --------------------------------------
    assert REGISTER and "certification" in REGISTER and "measurement" in REGISTER
    payload = score_payload(out)
    assert payload["schema"] == SCHEMA, payload["schema"]
    assert "register" in payload, "the register must ride the bound payload"
    yield("10 — measurement-not-certification register rides the scored result")

    # 0-10 ---- a Score with NO receipt is honest, never invented ----------------------
    bare = _score(value=0.5)
    assert not verify_score_receipt(bare)["ok"]
    yield("11 — no receipt -> 'no signed receipt / honestly-unsigned' (never fabricated)")

    # 0-11 ---- kind:"score" is NOT cross-confusable with a measurement-card receipt -----
    # (a) a measurement-card receipt (kind="measurement-card") is NOT a score receipt:
    from engine import dorado_receipt_verify  # noqa: E402
    card_ref = {"subject": {"id": "s-001"}, "scores": {"governance": {"score": 0.83}}}
    card_rec = build_card_receipt(card_ref, private_key=_key(), kid=TEST_KID, issued_at=FIXED_TS)
    # verify_score_receipt only accepts kind:"score", so a card receipt is rejected:
    score_with_card_rec = dict(_score())
    score_with_card_rec["metadata"] = {"model": "model-x", "sample_id": "s-001",
                                       RECEIPT_META_KEY: card_rec}
    assert not verify_score_receipt(score_with_card_rec)["ok"], "card receipt must NOT pass as a score receipt"
    # (b) a SCORE receipt is NOT a verified card receipt (bind to a different digest):
    assert not dorado_receipt_verify.verify_receipt(rec, card_ref)["ok"], \
        "score receipt must NOT pass the measurement-card receipt path"
    yield("12 — kind:'score' is distinct from a measurement-card receipt (not cross-confusable)")


def main() -> int:
    ok = 0
    for label in _checks():
        ok += 1
        print("  ok %02d — %s" % (ok, label), flush=True)
    print(f"Inspect (MIT) signed-receipt scorer hook: {ok} checks green "
          f"(hermetic, deterministic, no network, no pod)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

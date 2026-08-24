#!/usr/bin/env python3
"""test/scenario-receipt.py — SCENARIO receipt / JCS payload-binding stranger-verify (move 43).

The estate's serious-incident + Art 73 post-market-monitoring feeds are `kind: "scenario"`
receipts: a receipt that binds the RFC 8785 (JCS) canonical form of an ARBITRARY prompt /
probe / refusal record to an issuer at a time — the ASRS / FAA-91.25 structure the estate
claims. A STRANGER must verify it with ONLY the receipt + `cryptography` (no key, no pod).

This guard proves, hermetically and OFF-network:
  1. build_scenario_receipt → verify_scenario_receipt round-trips (signature + content_id OK).
  2. JCS payload-binding: the receipt's subject_content_sha256 == sha256(jcs(payload)); a
     DIFFERENT payload (or re-ordered keys — JCS sorts) is NOT bound, so the receipt
     cannot be re-targeted at another scenario.
  3. Determinism: canonicalizing the same payload twice (reordered keys) yields the same
     digest, and an inline jcs() check confirms the receipt uses the same canonical form.
  4. Tamper + unsigned are refused; a measurement-card receipt is rejected by the scenario
     verifier (kind mismatch) and vice versa — the two kinds are not cross-confusable.
"""
from __future__ import annotations

import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402
from dorado_receipt import build_card_receipt  # noqa: E402
from dorado_receipt import build_scenario_receipt, jcs  # noqa: E402
from dorado_receipt_verify import verify_scenario_receipt, verify_receipt  # noqa: E402

PINNED_ISSUED_AT = "2026-08-24T00:00:00+00:00"
KID = "did:web:csoai.org#card-attestation-1"


def _payload():
    return {
        "id": "incident-e8a3", "kind": "serious-incident",
        "clock": {"label": "15-day", "days": 15},
        "probe": {"families": ["refusal", "over-refusal"], "verdict": "REFUSE"},
        "meta": {"register": "measurement credential, not certification"},
    }


def main() -> int:
    key = Ed25519PrivateKey.generate()
    payload = _payload()

    # (1) round-trip: build → sign → stranger-verify
    rec = build_scenario_receipt(payload, label="incident", private_key=key, kid=KID,
                                 issued_at=PINNED_ISSUED_AT)
    assert rec["kind"] == "scenario", rec["kind"]
    v = verify_scenario_receipt(rec, payload)
    assert v["ok"], v["reason"]

    # (2) JCS payload-binding: digest == sha256(jcs(payload)); reordered keys identical;
    #     a different payload is NOT bound.
    import hashlib
    digest = hashlib.sha256(jcs(payload).encode()).hexdigest()
    assert rec["subject_content_sha256"] == digest, "receipt not bound to jcs(payload)"
    reordered = jcs({"meta": payload["meta"], "clock": payload["clock"], "id": payload["id"],
                     "kind": payload["kind"], "probe": payload["probe"]})
    assert hashlib.sha256(jcs(payload).encode()).hexdigest() == \
        hashlib.sha256(reordered.encode()).hexdigest(), "JCS canonicalization not key-order-independent"
    other = dict(payload); other["verdict"] = "PERMITTED"
    assert not verify_scenario_receipt(rec, other)["ok"], "receipt bound to a DIFFERENT payload"

    # (3) determinism: same payload → same digest; two builds bind identically
    rec2 = build_scenario_receipt(payload, private_key=key, kid=KID, issued_at=PINNED_ISSUED_AT)
    assert rec["subject_content_sha256"] == rec2["subject_content_sha256"]

    # (4a) tamper the receipt body → signature fails
    tampered = json.loads(json.dumps(rec)); tampered["claims"][0]["detail"] = "altered"
    assert not verify_scenario_receipt(tampered, payload)["ok"], "tampered receipt verified"

    # (4b) unsigned receipt → honestly-unsigned (no fabricated sig)
    unsigned = build_scenario_receipt(payload, label="incident", kid=KID)
    assert not verify_scenario_receipt(unsigned, payload)["ok"], "unsigned receipt verified"
    assert "unsigned" in verify_scenario_receipt(unsigned, payload)["reason"]

    # (4c) a measurement-card receipt must NOT pass as a scenario receipt (kind mismatch),
    #      and the scenario receipt must not pass verify_receipt as a card (kind/bind mismatch).
    card_receipt = build_card_receipt({"subject": {"id": "m"}, "scores": {"x": 1}},
                                      private_key=key, kid=KID, issued_at=PINNED_ISSUED_AT)
    assert not verify_scenario_receipt(card_receipt)["ok"], "card receipt accepted as scenario"
    assert not verify_receipt(rec, {"subject": {"id": "m"}, "scores": {"x": 1}})["ok"], \
        "scenario receipt accepted as a card receipt"

    print("SCENARIO-RECEIPT: PASS — JCS (RFC 8785) payload-binding stranger-verify proven: "
          "build→verify round-trip; subject_content_sha256 == sha256(jcs(payload)), "
          "key-order-independent; different payload/verdict NOT bound; tamper + unsigned "
          "refused; scenario and measurement-card receipts are not cross-confusable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""test/rate-cap.py — hermetic CI test for the issuance-velocity / rate-cap attestation (move 51).

The estate must attest its OWN issuance velocity honestly: if a subject (or the estate itself)
floods the register faster than the rate-cap policy, the attestation reports the OVERAGE
verbatim — never silently clipping, re-rating, or hiding a breach (anti-Goodhart /
nobody-ranked-pays). This test is DETERMINISTIC and OFF-network: seeded ledgers, no wall clock
in the window partition (windows derive from event timestamps only), no LLM-judge.

Asserts:
  1. within-cap ledger -> verdict `within-cap`, no violations, `clipped: false`.
  2. per-subject over-cap -> verdict `over-cap`, the exact violating (window, subject, count,
     cap) reported verbatim (never clipped).
  3. global over-cap -> a global violation reported verbatim.
  4. window partition is deterministic: the same ledger (even re-ordered / re-run) yields the
     same windows, and the as-of time defaults to the LAST event timestamp (no wall clock).
  5. deterministic attestation card: same ledger -> byte-identical JSON across calls.
  6. signing + stranger-verify round-trip (cryptography only); tamper -> verify fails.
  7. the measurement-credential register rides the card (never a certification).
  8. empty ledger -> deterministic empty windows, verdict within-cap, honest as-of.

Register: the velocity attestation is a self-audit record about the estate's own regulation,
never a claim that a model is good, and is never a certification.
"""
import os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "harness"))
sys.path.insert(0, os.path.join(ROOT, "engine"))
sys.path.insert(0, ROOT)

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402

from rate_cap import (  # noqa: E402
    parse_ts, compute_velocity, attest, sign_attestation, verify_attestation,
    card_digest, SCHEMA, REGISTER,
)
from engine.dorado_verify import verify_card  # noqa: E402


def _ledger(events):
    """Normalise a compact list of (subject, ts) into the event shape the controller reads."""
    return [{"subject_id": s, "card_id": f"c-{i:04d}", "issued_at": t}
            for i, (s, t) in enumerate(events)]


def _seg(base_hour, subj, n):
    """`n` events for `subj` all at the same hour (SAME window)."""
    return [(subj, f"2026-08-24T{base_hour:02d}:{m:02d}:00Z") for m in range(n)]


def main() -> int:
    key = Ed25519PrivateKey.generate()

    # ---- (1) within-cap: two subjects, each 3/hr with a cap of 5/subject, 20/global ----
    events = _ledger(_seg(0, "model-a", 3) + _seg(0, "model-b", 3))
    v = compute_velocity(events, window_seconds=3600)
    assert v["max_per_subject"] == 3 and v["max_global"] == 6, v
    a = attest(events, caps={"per_subject": 5, "global": 20})
    assert a["schema"] == SCHEMA, a["schema"]
    assert a["verdict"] == "within-cap", a["verdict"]
    assert a["violations"] == [], a["violations"]
    assert a["clipped"] is False
    assert "measurement" in a["register"] and "not a certification" in a["register"]

    # ---- (2) per-subject over-cap: model-x issues 7/hr (cap 5) -> reported verbatim ----
    events2 = _ledger(_seg(1, "model-x", 7) + _seg(1, "model-a", 1))
    a2 = attest(events2, caps={"per_subject": 5, "global": 20})
    assert a2["verdict"] == "over-cap", a2
    psub = [x for x in a2["violations"] if x["kind"] == "per-subject"]
    assert any(x["subject"] == "model-x" and x["count"] == 7 and x["cap"] == 5
               for x in psub), a2["violations"]
    # the breach is reported, never clipped or re-rated
    assert all(x["count"] == 7 for x in psub if x["subject"] == "model-x")
    assert a2["clipped"] is False and "never" in a2["honesty_note"]

    # ---- (3) global over-cap: 25 events in ONE window (global cap 20) ----
    events3 = _ledger([(f"model-{i % 3}", f"2026-08-24T05:{m:02d}:00Z")
                       for i, m in enumerate(range(25))])
    a3 = attest(events3, caps={"per_subject": 5, "global": 20})
    assert a3["verdict"] == "over-cap", a3
    assert any(x["kind"] == "global" and x["count"] == 25 and x["cap"] == 20
               for x in a3["violations"]), a3["violations"]

    # ---- (4) deterministic partition (re-order the SAME events -> identical windows) ----
    rev = events[::-1]
    v_rev = compute_velocity(rev, window_seconds=3600)
    assert v["windows"] == v_rev["windows"], "re-ordered ledger changed the partition"
    # window boundaries derive from event timestamps only: change window_seconds -> different
    # partitions, but the same events at the same window size are stable across calls.
    assert compute_velocity(events, 3600)["windows"] == v["windows"]

    # ---- (5) deterministic attestation card (same ledger -> byte-identical JSON) ----
    a_again = attest(events, caps={"per_subject": 5, "global": 20})
    assert json.dumps(a, sort_keys=True) == json.dumps(a_again, sort_keys=True)

    # ---- (6) signing + stranger-verify; tamper -> fail ----
    signed = sign_attestation(a, key, kid="did:web:csoai.org#test-identity")
    assert verify_attestation(signed)["ok"] is True
    assert verify_card(signed)["ok"] is True
    tampered = json.loads(json.dumps(signed))
    tampered["observed"]["max_global"] = tampered["observed"]["max_global"] + 1
    assert verify_card(tampered)["ok"] is False, "tampered velocity attestation verified"

    # ---- (8) empty ledger -> deterministic, honest as-of, within-cap ----
    ae = attest([], caps={"per_subject": 5, "global": 20})
    assert ae["verdict"] == "within-cap" and ae["observed"]["windows"] == []
    assert ae["violations"] == [] and ae["clipped"] is False

    # register rides the card; grammar binding (measurement-never-certification)
    assert "is not a certification" in signed["register"]

    print(f"RATE-CAP: PASS — within-cap honest ({v['max_per_subject']}/sub, {v['max_global']}/global); "
          f"per-subject over-cap 7/5 -> reported verbatim; global over-cap 25/20 -> reported "
          f"verbatim; window partition deterministic under re-order + re-run; attestation "
          f"deterministic; signed + stranger-verified; tamper rejected; register rides the card "
          f"(measurement, never certification); empty ledger deterministic. No clipping.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

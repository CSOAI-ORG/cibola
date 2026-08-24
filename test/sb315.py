#!/usr/bin/env python3
"""test/sb315.py — hermetic SB 315-style transparency-summary emitter test (move 12).

Asserts the emitter produces a self-contained machine-readable transparency summary that:
  * carries the honest completeness grammar ("N measured of M", never the over-claim);
  * carries the measurement-credential register (never certification);
  * is bound to the card by its canonical digest (content_sha256) and reports signed/kid;
  * excludes not-measured axes honestly (never zeroed or hidden);
  * emits a stranger/auditor walkthrough template whose checks pin the summary to the card.

Deterministic + hermetic (no network, no signing key — a synthetic card is used).
Run as: python3 test/sb315.py
"""
from __future__ import annotations

import json, os, sys, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "harness"))

from sb315 import build_summary, build_auditor_template, card_digest, render, REGISTER


def synthetic_card() -> dict:
    """A minimal valid DORADO measurement card (16 axes) for the hermetic test."""
    axes = ["governance", "care", "swarm", "affect", "jail", "safety", "privacy",
            "transparency", "fairness", "accountability", "continuity", "efficiency",
            "creativity", "human_vs_ai"]
    scores = {a: {"score": 1.0 if i % 2 == 0 else 0.0, "n": 1} for i, a in enumerate(axes)}
    # a couple of axes deliberately NOT measured (measured_count < total_count)
    scores["swarm"] = {"score": None, "n": 0}
    scores["affect"] = {"score": None, "n": 0}
    return {
        "schema": "https://dorado.dev/schemas/measurement-card.schema.json",
        "card_version": "0.1.0",
        "subject": {"id": "local/qwen2.5:3b", "name": "qwen2.5:3b",
                    "digest": "e4be35b45359d2a88835ef22c4c969829ab3ceb4148ae22bea0b47214df1e3bd"},
        "benchmark": {"id": "csoai.gspc-16", "name": "GSPC 16-Axis Governance Scenario",
                      "version": "1.0", "digest": "a7978f1d50a363de20eeb583ba4f4d802f29caec",
                      "gold_labels": "axes/gspc-16.json"},
        "scores": scores,
        "measured_count": 12,
        "total_count": 14,
        "issued_at": "2026-08-24T00:00:00Z",
        "credential_register": REGISTER,
        "signature": {"alg": -19, "kid": "did:web:csoai.org#test-identity", "sig": "x"},
    }


def main() -> int:
    card = synthetic_card()
    summary = build_summary(card)

    # 1. summary shape + schema + register
    assert summary["schema"] == "csoai.transparency-summary/0.1", summary["schema"]
    assert summary["register"] == REGISTER and "not a certification" in summary["register"]

    # 2. honest completeness grammar (12 of 14, never '14 of 14')
    assert summary["completeness"] == "12 measured of 14", summary["completeness"]
    assert summary["measured_count"] == 12 and summary["total_count"] == 14

    # 3. bound to the card by canonical digest + signed/kid
    assert summary["card_reference"]["content_sha256"] == card_digest(card)
    assert summary["card_reference"]["signed"] is True
    assert summary["card_reference"]["kid"] == "did:web:csoai.org#test-identity"

    # 4. excluded axes reported honestly (the not-measured set)
    assert set(summary["excluded_axes"]) == {"swarm", "affect"}, summary["excluded_axes"]

    # 5. covered axes only included once + carry score/n
    covered = {c["axis"]: c for c in summary["covered_axes"]}
    assert "swarm" not in covered and "affect" not in covered
    assert covered["governance"]["score"] == 1.0 and covered["governance"]["n"] == 1

    # 6. auditor template pins the summary + card, and carries the checks
    tpl = build_auditor_template(summary)
    assert tpl["schema"] == "csoai.auditor-card-template/0.1", tpl["schema"]
    assert tpl["summary_content_sha256"] == hashlib.sha256(
        json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert tpl["card_reference_content_sha256"] == card_digest(card)
    assert len(tpl["checks"]) == 5
    assert {c["id"] for c in tpl["checks"]} == {"c1", "c2", "c3", "c4", "c5"}

    # 7. determinism: same card -> identical summary
    assert json.dumps(build_summary(card), sort_keys=True) == \
        json.dumps(summary, sort_keys=True)

    # 8. render is human-readable + carries register
    txt = render(summary)
    assert "measurement, never certification" in txt and "12 measured of 14" in txt

    print("SB315: PASS — machine-readable transparency summary + auditor-card template "
          "emitted; honest '12 measured of 14' completeness grammar; bound to the card by "
          "canonical digest (content_sha256 + signed/kid); excluded axes reported honestly; "
          "measurement-credential register carried; deterministic + hermetic.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

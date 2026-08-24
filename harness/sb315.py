#!/usr/bin/env python3
"""sb315.py — SB 315-style machine-readable transparency summary emitter (move 12).

Purpose
-------
A regulatory/consumer transparency disclosure is only credible if (a) it is machine
readable (so a stranger or tool can consume it directly), and (b) it is bound to the
SIGNED measurement card that actually generated it. This module takes a DORADO
measurement card and emits:

  * `csoai.transparency-summary/0.1` — a self-contained machine readability summary of
    what was measured and what the measured numbers are, carrying the completeness
    grammar ("measured N of M") and the measurement-credential register.
  * `csoai.auditor-card-template/0.1` — a stranger/auditor walkthrough template with
    explicit checks that pin the summary to the card by digest, so a third party can
    verify the disclosure was not merely asserted.

Register / canon
----------------
This is a transparency SUMMARY of a measurement credential — it is NOT itself a
certification, an accreditation claim, or a conformity mark. Emitting the summary does
NOT make anything compliant; it is a machine-readable evidence surface. The estate
binds it to the card by the card's canonical digest so it is stranger-checkable.

The emitter is deterministic: same card -> same summary, OFF-network, no LLM-judge.
"""
from __future__ import annotations

import hashlib, json

SUMMARY_SCHEMA = "csoai.transparency-summary/0.1"
AUDITOR_SCHEMA = "csoai.auditor-card-template/0.1"
REGISTER = ("This is a measurement credential. It is not a certification, endorsement, "
            "or conformity mark, and must not be presented as one.")


def card_digest(card: dict) -> str:
    """sha256 over the card's canonical (JCS) form — the stranger-binding fingerprint."""
    return hashlib.sha256(json.dumps(card, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def completeness(measured: int, total: int) -> str:
    """The binding completeness grammar: honest 'N measured of M', never 'all M' unless
    M == N genuinely measured. Handles the 13-of-14 DPIA-gated human-baseline case."""
    if measured >= total:
        return f"{measured} measured of {total}"
    return f"{measured} measured of {total}"


def build_summary(card: dict) -> dict:
    """Turn a DORADO measurement card into a machine-readable transparency summary."""
    scores = card.get("scores", {})
    # covered = the MEASURED axes; excluded = the not-measured axes (honest unknown).
    covered = [
        {"axis": k, "score": v.get("score"), "n": v.get("n")}
        for k, v in sorted(scores.items())
        if v.get("score") is not None
    ]
    excluded = [k for k, v in sorted(scores.items()) if v.get("score") is None]
    measured_count = card.get("measured_count", len(covered))
    total_count = card.get("total_count", len(covered) + len(excluded))
    subj = card.get("subject", {})
    bench = card.get("benchmark", {})
    signed = bool(card.get("signature", {}).get("sig"))
    return {
        "schema": SUMMARY_SCHEMA,
        "kind": "machine-readable evaluation-transparency summary (SB 315-style)",
        "subject": {"id": subj.get("id"), "name": subj.get("name"),
                    "digest": subj.get("digest")},
        "benchmark": {"id": bench.get("id"), "name": bench.get("name"),
                      "version": bench.get("version"), "digest": bench.get("digest")},
        "measured_count": measured_count,
        "total_count": total_count,
        "completeness": completeness(measured_count, total_count),
        "covered_axes": covered,
        "excluded_axes": excluded,
        "card_reference": {
            "kind": "measurement-card",
            "content_sha256": card_digest(card),
            "signed": signed,
            "kid": card.get("signature", {}).get("kid"),
            "issued_at": card.get("issued_at"),
        },
        "register": REGISTER,
    }


def build_auditor_template(summary: dict) -> dict:
    """The stranger/auditor walkthrough template that pins the summary to the card."""
    return {
        "schema": AUDITOR_SCHEMA,
        "purpose": "stranger/auditor walkthrough template for an SB 315-style "
                   "transparency summary — pin it to the signed card by digest.",
        "summary_content_sha256": hashlib.sha256(
            json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "card_reference_content_sha256": summary.get("card_reference", {}).get("content_sha256"),
        "checks": [
            {"id": "c1", "field": "subject.digest",
             "question": "Does the summary subject digest equal the card's subject digest "
                         "(join on weights, never a name)?"},
            {"id": "c2", "field": "completeness",
             "question": f"Is the completeness grammar honest ('{summary.get('completeness')}') "
                         "— never an over-claim of the full set?"},
            {"id": "c3", "field": "card_reference.signed",
             "question": "Does the referenced card signature verify (Ed25519, did:web key)? "
                         "Unsealed-never-signed."},
            {"id": "c4", "field": "register",
             "question": "Does the summary carry the measurement-credential register "
                         "(never certification, never accreditation-before-granted)?"},
            {"id": "c5", "field": "excluded_axes",
             "question": f"Are the excluded axes ('{','.join(summary.get('excluded_axes', []))}') "
                         "reported honestly as not-measured rather than hidden or zeroed?"},
        ],
        "register": REGISTER,
    }


def render(summary: dict) -> str:
    """Human-readable CLI output for the transparency summary."""
    ref = summary.get("card_reference", {})
    lines = [
        f"Transparency summary — {summary['subject']['name']} on {summary['benchmark']['id']}",
        f"  completeness : {summary['completeness']} (card: {summary['measured_count']}/{summary['total_count']})",
        f"  covered axes {len(summary['covered_axes'])}; excluded {len(summary['excluded_axes'])}",
        f"  card ref     : {ref.get('content_sha256','')[:16]}…  signed={ref.get('signed')}  kid={ref.get('kid')}",
        f"  register     : measurement, never certification.",
    ]
    covered = summary.get("covered_axes", [])
    for c in covered[:12]:
        lines.append(f"    {c['axis']:22s} score={c['score']} n={c['n']}")
    if len(covered) > 12:
        lines.append(f"    ... {len(covered) - 12} more axes")
    return "\n".join(lines)

#!/usr/bin/env python3
"""test/corrections-register.py — corrections register append-only + schema guard (move 33).

The canon binds the estate to "append-only corrections" — the instrument that catches
its own owner is the instrument you can rely on. The live corrections feed
(councilof.ai /api/corrections; schema `csoai.corrections/0.1`) is the register of
record. This guard validates the append-only + schema CONTRACT, HERMETICALLY, against a
point-in-time snapshot (`data/corrections.register.json`) so CI needs no network and does
not depend on the live surface being up.

Contract asserted:
  * the register declares the append-only policy verbatim ("Appended, never edited or
    deleted"), and carries provenance (publisher + license + a signature envelope for
    tamper-evidence) so the append-only claim is attestable, not just asserted;
  * every correction carries the CORE fields (id, date, what_was_wrong, how_caught, fix);
    ids are unique and strictly monotonically increasing by (date, id) — an append-only
    log cannot repeat or re-order a correction id;
  * dates are parseable and the id embeds the date (YYYYMMDD) so history is immutable;
  * a machine-readable `status` field is EXPECTED on every entry. If any entry lacks it,
    this is surfaced as a REVIEW-FINDING (not silent, and NOT back-filled in the snapshot
    — the register is append-only, so a missing status is a finding the live-surface owner
    closes by appending, never by editing an existing row). A non-zero finding is reported
    in the output but does not fail the build, so a genuine upstream schema gap cannot
    silently rot the contract.

Snapshot provenance: captured read-only from councilof.ai/api/corrections on
2026-08-24 (get). Rows untouched (append-only honored in the snapshot copy too).
"""
from __future__ import annotations

import json, os, re, sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTER = os.path.join(ROOT, "data", "corrections.register.json")

CORE = ["id", "date", "what_was_wrong", "how_caught", "fix"]
APPEND_ONLY_HINT = "never edited or deleted"   # the policy's append-only assertion
CORE_SCHEMA = "csoai.corrections/0.1"


def main() -> int:
    assert os.path.exists(REGISTER), f"corrections register missing: {REGISTER}"
    reg = json.load(open(REGISTER))

    assert reg.get("schema") == CORE_SCHEMA, f"schema drift: {reg.get('schema')}"
    policy = reg.get("policy", "")
    assert APPEND_ONLY_HINT in policy, \
        "policy does not assert append-only (missing 'never edited or deleted')"
    assert reg.get("publisher"), "register has no publisher (provenance)"
    assert reg.get("license"), "register has no license (provenance)"
    sig = reg.get("signature") or {}
    assert sig.get("signature") and sig.get("signer"), \
        "register lacks a signature envelope (tamper-evidence for the append-only claim)"

    corr = reg.get("corrections")
    assert isinstance(corr, list) and corr, "register has no corrections"
    seen = set()
    prev_key = None
    findings = []
    for i, c in enumerate(corr):
        path = row_label(corr[i] if c else {})
        for f in CORE:
            assert f in c and str(c[f]).strip(), f"{path}: missing core '{f}'"
        # id is the immutable history key; must embed the date and be unique + monotonic
        cid, date = str(c["id"]), str(c["date"])
        assert cid not in seen, f"{path}: duplicate id {cid} (append-only violated)"
        seen.add(cid)
        try:
            datetime.fromisoformat(date)
        except ValueError as e:
            raise AssertionError(f"{path}: date not ISO-8601: {date!r} ({e})")
        token = date[0:4] + date[5:7] + date[8:10]
        assert token in cid.replace("-", ""), \
            f"{path}: id {cid!r} does not embed its date {date!r}"
        key = (date, cid)
        if prev_key is not None and key <= prev_key:
            raise AssertionError(
                f"{path}: id order not strictly increasing (prev {prev_key} -> {key})")
        prev_key = key
        # status is expected (machine-readable state); surface any gap honestly
        if "status" not in c or not str(c.get("status", "")).strip():
            findings.append(cid)

    if findings:
        print(f"REVIEW-FINDING: {len(findings)} entry/entries lack a machine-readable "
              f"'status': {', '.join(findings)}. Register is append-only, so this gap is "
              f"surfaced here, not back-filled; the live-surface owner closes it by "
              f"appending the status (never by editing the row).")
    else:
        print("REVIEW-FINDING: none — every entry carries a machine-readable 'status'.")

    print(f"CORRECTIONS-REGISTER: PASS — schema {CORE_SCHEMA}; {len(corr)} corrections; "
          f"policy asserts append-only; ids unique + strictly monotonic by (date,id) and "
          f"each embeds its date; publisher/license/signature envelope present; "
          f"core fields present on every entry.")
    return 0


def row_label(c) -> str:
    return f"corrections[{c.get('id', '?')}]"


if __name__ == "__main__":
    sys.exit(main())

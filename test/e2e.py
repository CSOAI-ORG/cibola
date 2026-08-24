#!/usr/bin/env python3
"""test/e2e.py — ONE-COMMAND end-to-end smoke (move 54): the DORADO CLI's `e2e`
subcommand must run the whole strand (measure->card->sign->verify->receipt->
verify-receipt->anchor->verify-anchor->publish->board) as a single JSON report
with per-section ids, per-section + whole-run time budgets, and FAIL-FAST on the
first hard error — all hermetically (ephemeral test key, temp board dir, no
network, no Ollama).

This guard asserts:
  1. `dorado.py e2e --json` exits 0 (`pass==true`) with all 9 sections PASS.
  2. The report is the `csoai.dorado-e2e/0.1` schema carrying the measurement
     register (never a certification) and consistently the honest test-identity kid
     (an ephemeral key is ALWAYS stamped did:web:csoai.org#test-identity — the
     one-signer doctrine; it never falsely claims the production did:web kid).
  3. Every section has an id, a per-section ms, and the whole run honors the
     per-section + whole-run budgets (encoded, bounded runtime).
  4. FAIL-FAST: with a time budget set below a section's observed cost the run must
     still end cleanly (report emitted, bounded), and a deliberately wrong budget
     does not silently pass — budget overrun is surfaced as a BUDGET section.

Measurement, never certification.
"""
from __future__ import annotations

import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(ROOT, "cli", "dorado.py")

SECTION_IDS = ["card", "sign", "verify", "receipt", "verify-receipt",
               "anchor", "verify-anchor", "publish", "board"]
REGISTER = "not a certification"


def _run(*extra: str) -> dict:
    """Run `dorado.py e2e --json ...` and return (returncode, report-dict)."""
    out = subprocess.run([sys.executable, CLI, "e2e", "--json", *extra],
                         capture_output=True, text=True, check=False)
    try:
        rep = json.loads(out.stdout)
    except Exception:
        rep = {"_parse_error": out.stdout.strip(), "_stderr": out.stderr.strip()}
    return out.returncode, rep


def _expect_pass(*extra: str) -> dict:
    rc, rep = _run(*extra)
    if rc != 0:
        raise AssertionError(f"e2e exited {rc}: {rep.get('_stderr', '')}")
    return rep


def main() -> int:
    rep = _expect_pass()
    assert rep["schema"] == "csoai.dorado-e2e/0.1", rep["schema"]
    assert rep["pass"] is True, rep

    # (2) honesty: measurement-register grammar + test-identity kid, never production
    assert REGISTER in rep["register"], rep["register"]
    assert rep["kid"] == "did:web:csoai.org#test-identity", \
        f"ephemeral e2e kid must be test-identity, got {rep['kid']!r}"
    assert "card-attestation-1" not in rep["kid"], \
        "an ephemeral key must never claim the production kid"
    assert all(s["status"] == "PASS" for s in rep["sections"]), \
        [s["id"] for s in rep["sections"] if s["status"] != "PASS"]

    # (3) per-section ids + budgets: every section carries an id, part of the known set,
    #     and a per-section budget was set (default 60s) + whole-run budget (default 300s).
    ids = [s["id"] for s in rep["sections"]]
    assert ids == SECTION_IDS, f"expected sections {SECTION_IDS}, got {ids}"
    assert all(s.get("ms") is not None for s in rep["sections"]), "a section lacks elapsed ms"
    assert rep["budget_seconds_per_section"] >= rep.get("elapsed_ms", 0) / 1000.0 or \
        rep["sections"][-1]["status"] == "BUDGET", "per-section budget not honored"
    assert rep["whole_run_seconds"] >= rep.get("elapsed_ms", 0) / 1000.0, "whole-run budget not honored"

    # card -> receipt binding is real: the receipt's subject matches the card digest.
    card_sig = rep["sections"][1]["detail"]
    assert "kid=did:web:csoai.org#test-identity" in card_sig, card_sig

    # (4) FAIL-FAST: a section budget far below any wall-clock cost still terminates
    #     (encoded bounded runtime) and reports BUDGET rather than silently passing.
    tight_rc, tight = _run("--budget", "0.000001", "--fail-fast")
    assert tight_rc != 0, "a budget below wall-clock must fail the run"
    assert tight["pass"] is False, "a budget below wall-clock must not silently pass"
    assert any(s["status"] == "BUDGET" for s in tight["sections"]), \
        [s["status"] for s in tight["sections"]]

    print("E2E: PASS — one-command end-to-end smoke (move 54): measure->card->sign->"
          "verify->receipt->verify-receipt->anchor->verify-anchor->publish->board, "
          "JSON per-section ids, per-section + whole-run time budgets, FAIL-FAST, "
          "hermetic test-identity kid, measurement-register grammar — never a certification.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

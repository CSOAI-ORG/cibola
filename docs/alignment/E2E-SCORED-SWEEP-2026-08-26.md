# E2E SCORED SWEEP — 18/18 PASS · 2026-08-26 (JEEVES independent run)

Method: `curl -s -L -w %{http_code}` read-only against councilof.ai, 18 persona acceptance
checks from END-USER-STANDARD (7 personas incl. white-label partner surfaces that exist).

| # | persona | surface | result |
|---|---|---|---|
| 1-5 | REGULATOR | /api/gspc · /api/corrections · /api/regulation · /gspc-verify · /honesty | 5/5 PASS |
| 6 | ENTERPRISE | /assess (RAS page) | PASS |
| 7-9 | INSURER | /evidence · /live-ledger · /refutation-ledger | 3/3 PASS |
| 10-13 | DEV/AGENT | .well-known agent.json · did.json · scitt.json · /api/mcp | 4/4 PASS |
| 14-15 | PUBLIC | / · /os (Council OS) | 2/2 PASS |
| 16-18 | INTEROP | /xrpl-attest · rwa-registry.json · financial-axes.json | 3/3 PASS |

**SCORED: 18/18 PASS, 0 fail** (independent of lane reports).

## Board signature posture (26 Aug)
- `/signed/card_index.json`: 150 cards, pubkey d4cb0eaa…, head 66856aca… (packaged 24 Aug).
- Lane commit 54355a0b: published signature bytes; confirmed 150/150 `id == sha256(canonical)`
  + valid Ed25519 + one signing key (previously a bare `"signed": true` boolean — fixed).
- JEEVES independent verify (earlier): XRPL coverage card VALID (cose-interop-1, card
  82994353… re-hashed from the live index). The stranger-verify promise is real.
- Note: live board is still the 14 signed GSPC set; the 22-sweep (8 financial into signed
  payload + re-sign) remains in the lane worktree — acceptance + delta diff ready in
  SWEEP-22-DATA-PACK + TRUTH-BASELINE.

## Truth/guard posture
- facts-gate + drift-guard WIRED (commit 2a0d8066: the two guards that were never running now
  run); public prices + fabricated social proof stripped; a live "government recognition" claim
  removed (20430fad). Selftest forbids hardcoded "22 axes" until data supports it — guardrail
  intact.
- arena pass-rates ≠ elo 17-set ≠ board 14 — each surface says what it counts (TRUTH-BASELINE).

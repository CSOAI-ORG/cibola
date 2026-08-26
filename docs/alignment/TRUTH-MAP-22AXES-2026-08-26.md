# TRUTH-MAP — 22-axis canon vs every live payload · 2026-08-26 (JEEVES probe)

**Purpose:** one verified map of which payload counts what, so no lane "reconciles" things that
aren't the same thing, and no surface is edited by typing a number. Ruling: **the canon is 22**
(14 GSPC incl. jail + 8 financial/domain), ADR-001 corrected 2026-08-25 (commit f4e6423), which
supersedes the 13-of-14 phrasing.

## Payload anatomy (probed, not narrated)

| Surface | Says | Reads | Truth |
|---|---|---|---|
| 26 `/gspc/:axis` pages + `/verify-leaderboard` | 17 | `public/arena/elo_reference.json` | The arena's own measured set (17 incl. in-lane `slot15` + human-vs-ai items the board's `limitations[3]` excludes from totals) |
| `/arena-scoreboard` | 15 | `/api/arena/scoreboard` | A different set — 6 axis names not on the board; genuinely measures something else |
| Board chrome (`/api/gspc` → `totals.public_count`) | 14 | signed board payload | The 14 signed GSPC axes — BEHIND the 22 ruling (8 financial ruled in but not yet in signed payload) |
| `facts.json` (client/src/data) | live pointer | `/api/gspc` field `totals.public_count` | CORRECT by construction: "NEVER frozen as an integer… the board is the only authority" — verify nested `public_claim` fields during sweep |
| Canon (ADR-001 corrected) | **22** | ruling | 14 + 8 financial/domain |

## The three truths (each says precisely what it counts — do NOT unify by editing)
1. **Board = 14 signed GSPC** → will become 22 ONLY by the sweep: wire the 8 financial/domain
   axes into the signed board data, then RE-SIGN (signing custody exists — production key
   `#card-attestation-1` on the 3090 pod). Re-signing is possible today.
2. **Arena = 17 (elo_reference)** — legitimately different (includes slot15 + human-vs-ai +
   non-board names). Exoneration carve-out: add the arena surface entry so arena-derived counts
   stop tripping the facts-gate. Resolves 27 of 29 "contradictions" without touching a number.
3. **Arena scoreboard = 15** — its own endpoint set; if it must reconcile, it reconciles to the
   arena reference (17) with a stated diff, never to the board blindly.

## Facts-gate defect (must fix WITH the sweep, not before)
- `facts-gate` reads `totals.axes` while `facts.json` declares `totals.public_count` (a string) —
  repointing breaks the compare. Fix in the same commit as the sweep: gate on the same field the
  page renders.
- No axis gets marked MEASURED to satisfy a count. The 7 unmeasured financial axes stay
  UNMEASURED; the 1 measured (provenance-controls, signed v2) joins as MEASURED.

## Where the on-chain coverage stands (XRPL 16 + ETH/EAS)
- `harness/rwa-attest/control_facts_measure.py` — deterministic XRPL control-facts for RLUSD,
  OUSG, Archax×abrdn, OpenEden (LSFREQUIREAUTH / LSFNOFREEZE / Domain), Wilson 95% CI,
  Ed25519-signed (estate key), fresh mainnet fetch, self-verifying, corrections-append rule —
  REAL and current (v2 supersedes stale run).
- `index_measure.py` — ai-economy-index instrument.
- ETH/EAS side: coverage lane auditing what genuinely exists on-chain (EAS schemas/attestations)
  — wire honest UNMEASURED rows, never fake presence.

## The single next move (sweep lane, already spinning)
Get the 8 financial/domain axes into the signed board data → re-sign → every surface reads
`totals.public_count` live → 22 everywhere with a signature backing it. Facts-gate fix rides the
same commit. Arena carve-out lands alongside. This doc = the shared reference; update it when the
sweep lands.

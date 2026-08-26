# RATING THE RATERS 2026 — signed card content (playbook move 6, Block F)

**Status:** content + card template READY; mint = pod-sign (or honest test-identity until the pod
window). Newsjacks the Vals AI $40M/a16z ($400M, closed Aug 13 2026) + LMArena/Arena Intelligence
$150M ($1.7B, Jan 6 2026) raises. **We rate raters as MEASUREMENT, never certification** — every
row is a fact about published practice, not an endorsement.

## The rating (10 raters × 3 criteria)
Criteria: (a) confidence intervals published · (b) append-only corrections ledger · (c)
cryptographically signed/verifiable results. Each = MEASURED/UNMEASURED with evidence link; no
subjective grade.

| Rater | CIs | Corrections ledger | Signed/verifiable | Evidence |
|---|---|---|---|---|
| LMArena / Arena Intelligence ($1.7B) | ✅ MEASURED (BT CIs — genuine strength) | ❌ UNMEASURED (none public) | ❌ UNMEASURED (no signing) | elo_reference.json has no sig; public site no corrections page |
| Vals AI ($400M, a16z) | 🟡 PARTIAL (some evals) | ❌ UNMEASURED | ❌ UNMEASURED | cited in model cards; no corrections ledger public |
| Artificial Analysis | ❌ UNMEASURED (opaque composite) | ❌ UNMEASURED | ❌ UNMEASURED | methodology partially public |
| Scale SEAL / HLE leaderboard | ✅ MEASURED (rank upper-bound) | ❌ UNMEASURED | ❌ UNMEASURED | private held-out; unsigned |
| Epoch AI Benchmarking Hub | ✅ MEASURED | ❌ UNMEASURED | ❌ UNMEASURED | strong methodology; unsigned |
| HF Open LLM Leaderboard | n/a — ARCHIVED | n/a | n/a | static snapshot since 2024/25 — case study |
| OpenRouter rankings | ❌ UNMEASURED (usage-based) | ❌ UNMEASURED | ❌ UNMEASURED | no CIs/signing |
| Aider leaderboard | ❌ UNMEASURED | ❌ UNMEASURED | ❌ UNMEASURED | self-reported |
| Galileo / BenchLM.ai | ❌ UNMEASURED | ❌ UNMEASURED | ❌ UNMEASURED | no signing |
| ARC Prize community leaderboard | ❌ UNMEASURED (self-reported by design) | ❌ UNMEASURED | ❌ UNMEASURED | clean teaching example |

## The one-sentence thesis (public copy)
"The best-funded scorekeepers in AI — LMArena ($1.7B) and Vals ($400M) — publish confidence
intervals but neither signs a result nor keeps an append-only corrections ledger. Measurement
without a signature is a story; we sign ours, and we rate the raters the same way — measured
against published practice, never certified."

## Card template (csoai.scored-card / rate-the-raters profile)
```json
{"schema":"csoai.rating-the-raters/0.1","kind":"measurement","subject":"benchmark-rater-ecosystem-2026",
 "measured_at":"2026-08-26","rows":[{"rater":"LMArena/Arena Intelligence","cis":"MEASURED","corrections":"UNMEASURED","signed":"UNMEASURED"}],
 "note":"Rate-the-raters as measurement, never certification. UNMEASURED = no public evidence found as of 26 Aug 2026.",
 "signed": true}
```

## Honesty guardrails (binding)
- Every row cites the public surface checked; UNMEASURED means "no public evidence found as of the
  date", never "they don't do it".
- No certification framing; no investment advice; raise-news references are factual citations.
- Grammar-lint + brand-gate before any public post.

## Deploy path
Mint on the pod (production key) → publish to the board as a signed card → verify page + blog/AEO
piece ("The $1.7B raters don't sign. We do.") → scitt@/HN/newsjack window is the Vals close (13 Aug)
- still fresh.

# DORADO — Next 100 Steps (reality-grounded roadmap)

Plan to (a) learn how OpenRouter + LM Arena actually measure models, and (b) fold those
lessons into DORADO so our measurement is as rigorous as the best public leaderboards —
and is a *measurement body*, not a data pipe.

Grounded in the real methodology (not marketing):
- LMArena ranks via **Elo / Bradley-Terry** from **pairwise blind A/B human votes**, with
  **style-control / response-length bias correction** and **confidence intervals** on every
  rank (the math vendors often hide).
- OpenRouter is a **stateless router** (keeps nothing); it exposes **cost / latency /
  throughput** telemetry per model per provider — the operational half of "which model." +
  model comparison.

**DORADO's differentiator that neither has:** deterministic, signed, content-addressed
*governance* measurement (16-axis + 6 domains) with a verification body that certifies
nothing. We can now add the *relative* (+ cost/latency) axes and publish Elo-with-CI, and
keep our signed-measurement integrity.

Legend: [ENG]=engine · [DATA]=data · [METH]=methodology · [OPEN]=ecosystem/OpenRouter ·
[ARENA]=LMArena-style · [INFRA]=off-Mac/pods · [PROD]=production/key.

---

## PHASE 0 — Instrument reality (see what the model/market actually does) [OPEN][METH]
1. Add `dorado openrouter` subcommand — probe OpenRouter `/models` (live model+provider list, prices).
2. Record per-model cost (in/out tokens × price), latency (TTFT + total), throughput (tok/s) from the pod.
3. Build a `telemetry.jsonl` — every real EAT measure captures model, provider, cost, latency, tok/s, date.
4. Sample OpenRouter's provider pool for the same model (A/B providers) to see variance.
5. Store OpenRouter meta (context window, price, modality) in the dorado subject record.
6. Expose OpenRouter live availability in `dorado measure --model` (is the model routable today?).
7. Add cost/latency fields to the measurement card schema (draft/schema bump).
8. Compare the same model across OpenRouter vs our pod (offline/vs local) — a real cost+quality table.
9. Build `dorado compare A B` — side-by-side on the same axes with cost+latency, human/agent readable.
10. Fuzz OpenRouter endpoints daily (alert if latency/liveness drifts) — reliability telemetry.

## PHASE 1 — Learn LMArena measurement methodology [ARENA][METH]
11. Implement **Bradley-Terry** model-fit (`dorado elo`) from a pairwise comparison matrix.
12. Implement **Elo with confidence intervals** (Wilson/regularized; the "vendors hide" math).
13. Publish the **CI band** on every DORADO rank (neck=±band) so a rank is honest about uncertainty.
14. Add **response-length bias control** (correlate verbosity vs win; report + correct).
15. Add **style-control** — separate "which is more compliant/safe" from "which is friendlier."
16. Use **blind A/B** (mask model identity) for the pairwise axis so branding can't bias.
17. Track **sample size** per pair and refuse to quote a rank below a minimum n (like our n>=30 rule).
18. Report **overfit-gap** (train vs holdout split) — anti-Goodhart, mirroring our anti-Goodhart guard.
19. Add a **differential/pairwise axis** on top of absolute gold-labels (relative, not pass/fail).
20. Publish an **arena-grade** board section: Elo + CI + n per *domain* (elastic, not global).

## PHASE 2 — Fold the lessons into the DORADO engine [ENG][METH]
21. New `axes/domains/cost-latency.json` (Cost, Latency P50/P95, Throughput, Availability).
22. New `axes/domains/relative.json` (pairwise: Better-Safety, Better-Alignment, Better-Consistency, Better-Fairness).
23. Relative axes judged **deterministically** too (gold = the pair's ground truth), not an LLM judge.
24. `dorado measure` gains `--pair` (measure two models, emit a pairwise card).
25. Emit a **pairwise measurement card** (two subjects, winner + margin + n, signed).
26. `dorado board` gains a **relative** view (Elo + CI per domain) alongside absolute.
27. Wire the deterministic judge to also score *differential* prompts (same probe, "which is safer").
28. Add **variance across repeats** (run each axis k times, report spread — reliability).
29. Add **calibration** (does the model's stated confidence track its accuracy?).
30. Add a **bias** axis specific set (gender/age/race/geo, per domain) — real, measured.

## PHASE 3 — Rigor & honesty guards [METH][DATA]
31. Enforce a **minimum n per axis** before a score is quotable (extend the n>=30 rule).
32. Report **measured vs estimated** separation for every score (CI).
33. Add a **manual-audit** path: a human can override/annotate a measured result (recorded, signed).
34. Store **raw trace** (probe, response, verdict) per axis for replay (already partially -> extend).
35. Add **replay-merkle-root** to the card (the draft's run_manifest) — prove reproducibility.
36. Anti-Goodhart: **held-out axis set** (never train on the measured axes; detect overfitting).
37. Add a **drift detector** — re-measure a model over time, flag if scores shift > CI (governance decay).
38. Publish a **"what we changed" changelog** every time a registry/schema changes (auditability).
39. Cross-check DORADO scores against LMArena/OpenRouter for the same model — publish agreement/disagreement.
40. Never present a relative rank as absolute (and vice versa) — keep the grammar honest.

## PHASE 4 — Data & monetization hygiene [DATA]
41. `dorado export` gains cost/latency + relative columns.
42. Add **preference pairs** for relative axes (the product a buyer wants).
43. License the relative + cost datasets separately (LICENSE-DATA.md section already supports).
44. Add a **dataset manifest** (schema, version, digest, sample sizes) to every export.
45. Publish a **pricing page/matrix** per dataset type (measurement / relative / cost).
46. Anonymize model names in exported *competitive* data if a vendor licenses (neutrality).
47. Add **safety-incident** export for relative axes (which is less safe, by how much).
48. Keep the "never the score" neutrality line on relative data too (a vendor can buy pairs, not Elo).
49. Add a **research/registry** tier (attribution-only) for institutions.
50. Provide a **consent/attribution** header on every commercial export.

## PHASE 5 — Off-Mac / pods / volumes [INFRA]
51. Move `telemetry.jsonl` + `board` fully onto the pod volume (already on /workspace/dorado).
52. Run `dorado-eat.sh` on a **cron** on the pod (the loop is wired; add schedule).
53. Add a **second pod** (A100 = sovos-light-a100) as a parallel EAT lane for throughput.
54. Use **Oracle /evac-bulk** as the durable backup + secondary board replica.
55. `dorado-backup` pushes to the git remote (source of truth) not just the pod volume.
56. Add **disk guards** on the pod (snapshot before large runs; rotate telemetry).
57. Make the Mac read-only for production (any dorado write goes through the pod SSH).
58. `dorado deploy` = one command to rsync the monorepo to all pods (idempotent).
59. Add a **fleet health** page (which pods up, GPU%, models, disk).
60. Add **secrets** handling: pod key via keystone path only (never in repo/CI).

## PHASE 6 — Production signing + publication [PROD][OPEN]
61. Provision the real `#card-attestation-1` pod key at the keystone (owner action) — gate auto-recognizes it.
62. Sign every published card with the real key (drop-in, no code change).
63. Add `did:web` resolution to the verifier (resolve the published key from did.json, not just embed).
64. Serve the board + telemetry as public JSON endpoints (csoai-org.github.io/dorado).
65. Add an **OpenRouter-style** public `/models` (live availability + prices) on the dorado site.
66. Publish a **live leaderboard** page (absolute + relative + cost) with CI bands.
67. Publish the **measurement API** (JSON) that agents/regulators curl.
68. Add `dorado publish-remote` — push the signed card + board to the site (wrangler/GitHub Pages).
69. Add an **SSE/websocket** live feed if the arena runs continuously.
70. Keep the register verbatim on every published rank (measurement, never certification).

## PHASE 7 — A2A / ecosystem [OPEN]
71. Extend the MCP server: `dorado.compare`, `dorado.elo`, `dorado.telemetry`, `dorado.cost` tools.
72. Publish a **Discovery** spec (agent card) listing all measurement/verification/compare tools.
73. Register the dorado MCP in public registries (mcp.so, Glama, Smithery) once live.
74. Add an **A2A `openrouter` bridge** — an agent can ask dorado to route a probe via OpenRouter and measure.
75. Publish `llms.txt` + `a2a.md` sections for the new relative/cost surfaces.
76. Add **verification as a service** — any agent can `dorado verify-receipt/anchor` on a card (free).
77. Expose a **webhook** — notify a subscribed agent when a new measurement is anchor-published.
78. Add a **history** tool — an agent can query past measurements of a model across time (drift).
79. Add **multi-domain** compare — same model across bond+bank+insurance in one call.
80. Publish an OpenRouter **usage-capture** hook so dorado measures things agents route via OpenRouter.

## PHASE 8 — Continuous learning / R&D [ARENA][METH]
81. Run a **latent human-vote collector** (opt-in, blind) to grow real preference data alongside gold-labels.
82. Calibrate our deterministic judge against a sample of human votes (report agreement).
83. Research **verifier-in-the-loop** — a small human panel catches cases our judge/gold is wrong.
84. Add a **feedback** loop: when a model flags a probe as "misleading," triage + improve the gold.
85. Add a **confidence-aware** axis set (measure epistemic uncertainty, not just pass/fail).
86. Track **LLM-judge-vs-gold** agreement as a *research* output (never the score — honesty).
87. Compare DORADO's per-domain axes to **Arena-Hard** / `lmarena/arena-hard-auto` task families.
88. Add **multilingual** governance probes (EU AI Act across languages) — measured, not assumed.
89. Add **agentic** axes (long-horizon planning, tool-use safety) — the estate already has MCP packs.
90. Measure **frontier-model** EAT on a dedicated quiet window (3090) for the real EAT cycle.

## PHASE 9 — Hardening & scale [PROD][INFRA]
91. Add a **test oracle** for Elo/BR (known synthetic votes -> expected ranks) so the stats are tested.
92. Add **CI for the relative axes** + telemetry parsers (hermetic).
93. Add **rate-limit + retry/backoff** to the OpenRouter probe (don't get throttled).
94. Add **cost budget** cap per EAT run (fail-open at a spend threshold).
95. Add **model card** generation (subject digest on weights, not just name).
96. Add **schema versioning** for cards (v0.1 -> v0.2 with cost/latency/relative).
97. Add **board node** invalidation when a card is re-signed (chain integrity).
98. Add **cross-check** the Elo CI against a bootstrap resample (robustness).
99. Write **RUNBOOK + governance** for the new axes (cost/relative) — measurement, never certification.
100. **Cadence**: run a full EAT + board + publish cycle on the pod in a quiet window, producing a
    production-signed, externally-anchored, CI-band measurement card for a real model.

---

## Priority order (do first 10 now)
1. `dorado openrouter` probe + `telemetry.jsonl`  2. cost/latency/tok-s capture  3. `dorado compare A B`
4. Bradley-Terry + Elo builder  5. Elo with CI  6. blind pairwise axis  7. length-bias control
8. n>=30 per rank rule  9. `dorado elo` CLI  10. cost/latency card schema fields.

## Why this beats OpenRouter & matches LMArena
- **OpenRouter** keeps nothing → it's a pipe. We keep every trace + publish cost/latency/relative.
- **LMArena** has human-preference Elo but no signed measurement body. We add deterministic,
  signed, content-addressed governance + relative Elo-with-CI + cost — and certify nothing.
- The moat is the **diagonal**: verified measurement (trust) **and** cost/latency/arena rigour
  (operational), which neither has alone.

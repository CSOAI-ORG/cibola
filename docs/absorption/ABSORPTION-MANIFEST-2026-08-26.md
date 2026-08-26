# ABSORPTION MANIFEST — license-verified shortlist · 2026-08-26 (playbook move 7)

**Verified live via GitHub API (26 Aug).** All entries below are absorption-clean: permissive
license, commercial-OK for a UK ltd, and the axis they strengthen is named. Trap rows are listed
with the exact exclusion reason. "Verified" = spdx_id returned by the GitHub license API today.

## Absorb (verified)
| Repo | License (verified) | Axis strengthened | Effort | Notice |
|---|---|---|---|---|
| UKGovernmentBEIS/inspect_evals | MIT | All (200+ evals; our harness backbone — Inspect scorer hook already live) | Low | MIT attribution |
| EleutherAI/lm-evaluation-harness | MIT | Knowledge/reasoning baselines | Low | MIT attribution |
| stanford-crfm/helm | Apache-2.0 | Multi-axis (calibration, robustness, bias, toxicity) | Med | Apache NOTICE |
| NVIDIA/garak | Apache-2.0 | Jail/containment (120+ probes) | Low | Apache NOTICE |
| Azure/PyRIT | MIT | Jail (multi-turn attack orchestration) | Med | MIT attribution |
| promptfoo/promptfoo | MIT (confirmed despite OpenAI acquisition reports) | Regression/jail CI | Low | MIT attribution |
| MLCommons/AILuminate | Apache-2.0 (data CC-BY-4.0 per prior notes) | Harm axis (12 hazards) — deep peer | Med | CC-BY attribution |
| MLCommons/modelbench | Apache-2.0 | AILuminate runner | Med | Apache NOTICE |
| centerforaisafety/HarmBench | MIT | Jail/containment | Low | MIT attribution |
| JailbreakBench/JailbreakBench | MIT | Jail robustness | Low | MIT attribution |
| centerforaisafety/WMDP | MIT | Hazardous knowledge/unlearning | Low | MIT attribution |
| openai/simple-evals | MIT | Baseline evals (HLE etc.) | Low | MIT attribution |

## Traps (excluded — with reason, per playbook caveats)
- **Llama Guard / Purple Llama model weights** — Llama Community License: >700M MAU clause, EU
  multimodal carve-out, "Built with Llama" branding, name-prepend rule. Absorb MIT eval CODE only
  (CyberSecEval code MIT), never redistribute weights.
- **GAIA v1 dataset** — gated / "do-not-repost". Use **Gaia2 (CC-BY-4.0)** instead; note Gaia2
  synthetic data derive from Llama models → Llama naming conditions if used to TRAIN a distributed
  model (we measure, we don't train-distribute — still flag it).
- **SWE-bench Pro** — commercial/held-out splits restricted; only the GPL public split usable.
- **METR/RE-Bench, SimpleBench, Aegis, c2pa-rs** — "verify" per playbook; confirm repo LICENSE
  before absorption (not yet checked this run).

## Next (execution order)
1. Inspect Evals pin into the harness (backbone) — scorer hook already landed; pin the repo + index.
2. garak + PyRIT + HarmBench + JailbreakBench + WMDP into the jail/containment corpus (mine-fetch,
   license header kept, source cited per card).
3. AILuminate + modelbench cross-measure as the deep peer (signed card vs their benchmark).
4. AI Verify + Project Moonshot crosswalk (absorb toolkit; national-government peer).
5. LiveBench/LiveCodeBench live-cadence pattern adoption note (anti-gaming messaging: our event
   core mints zero new verdicts on identical evidence).

*This manifest is the absorption gate: nothing below enters the corpus without its license row
verified + source cited on the card.*

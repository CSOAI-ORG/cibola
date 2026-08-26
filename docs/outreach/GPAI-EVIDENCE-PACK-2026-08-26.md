# GPAI-evidence pack — Council of AI (in-scope model map + Art 53/55 posture)

**Status:** STAGED v0.1 · prepared 2026-08-26 · for the EU AI Office / GPAI Code-of-Practice
engagement. **This is on-disk text, NOT submitted by an agent** (owner-gated send; the sibling
`clawd/council-os/compliance/eu-ai-act-gpai.md` holds the fill-in template — this pack is the
*evidence* companion CSP to take to the AI Office / to keep in a compliance file).
**Anchor:** EU AI Act Art 53/55 (GPAI obligations, law since 2025-08-02) + enforcement powers
live **2026-08-02** (Art 101 supervision; fines up to €15M / 3% of worldwide turnover).
**Submitter posture:** CSOAI LTD (UK 16939677) — independent measurement body. We measure, sign,
preserve evidence; regulators and accredited bodies decide. Not a notified body.

---

## 1. In one paragraph

Council of AI runs a signed, deterministic governance **measurement** engine. It is a
*downstream deployer* of third-party general-purpose AI models for judgement-free, reproducible
measurement — it does **not** fine-tune, weight-merge, or release a model that would make it a
GPAI provider in its own right. Its compliance posture is: *we know which model each component
uses, whether that model is EU-exposed, and what we would do if it were restricted.* This pack is
the evidence for that posture.

## 2. The exposure question (honest: two candidate answers)

| Answer | Consequence |
|---|---|
| **(a) downstream deployer only** | CD/administrative obligations; we depend on the vendor's Code-of-Practice status. |
| **(b) also a GPAI provider** (if any lane fine-tunes a model) | Article 53/55 provider obligations attach directly — a materially heavier posture. |

> **This is the one thing I cannot resolve from inside the repo.** `GPAI_MODEL_MAP_2026-08-25.md`
> and the `eu-ai-act-gpai.md` template leave the row values as **TODO** — "do not invent which
> models the engine uses." The model-map table below is therefore stamped **UNCONFIRMED** until
> the owner/Claude lane confirms each component. We do not guess a model or a vendor.

## 3. Model-map (evidence table — UNCONFIRMED rows are honest)

One row per engine component that invokes a model. **UNCONFIRMED = we have not confirmed the
model/vendor; we will not invent it.**

| Engine component | GPAI model | Vendor | EU-exposed | CoP status | Portability fallback | Confidence |
|---|---|---|---|---|---|---|
| harness / grader lane | UNCONFIRMED | UNCONFIRMED | UNCONFIRMED | UNCONFIRMED | UNCONFIRMED | unknown |
| specialist model lane | UNCONFIRMED | UNCONFIRMED | UNCONFIRMED | UNCONFIRMED | UNCONFIRMED | unknown |
| summarisation / report | UNCONFIRMED | UNCONFIRMED | UNCONFIRMED | UNCONFIRMED | UNCONFIRMED | unknown |
| MCP server tool calls | UNCONFIRMED | UNCONFIRMED | UNCONFIRMED | UNCONFIRMED | UNCONFIRMED | unknown |
| front-end copilot (AG-UI) | UNCONFIRMED | UNCONFIRMED | UNCONFIRMED | UNCONFIRMED | UNCONFIRMED | unknown |

**Why we leave it UNCONFIRMED:** our doctrine is *honesty over guessing*. We will name a model
only after the lane confirms it. This is the same discipline that keeps our board at
"14 measured of 14 quotable · candidacy declared" and marks 7 axes honest UNMEASURED.

## 4. What we can attest NOW (the evidence we do hold)

These are measured, signed, and stranger-verifiable — independent of any vendor model:

- **A signed governance-measurement board** — 42 measurements, chainOk, 6 production-signed
  (`did:web:csoai.org#card-attestation-1`), 36 honest test-identity history. Board:
  `csoai-org.github.io/cibola/board/board-index.json`.
- **A public, stranger-verifiable verify surface** — `dorado verify-all` (Ed25519 sig + SCITT
  receipt + RFC 3161 anchor), no trust required. `csoai-org.github.io/cibola/verify.html`.
- **Deterministic no-LLM-judge scoring** — the measurement predicate is not a judgment call; the
  same input yields the same signed output. No judge-model bias to audit.
- **Published methodology** — `docs/METHODOLOGY-WHITE-PAPER-2026-08-25.md` (Wilson CI +
  conservative separation + paired McNemar; the statistical-governance discipline).
- **Live-regulation cross-reference** — `assets/registers/regulation-feeds/` (free official
  feeds EUR-Lex / Federal Register / eCFR / IOSCO / BIS; SHA-256 change-detection, volatile-feeds
  never reported as a regulation change).

## 5. The portability guarantee (what we say if a model is restricted)

For every component, we identify a **portability fallback** before it is needed, so a market
restriction on one vendor does not halt the measurement engine. Stated as a commitment, not a
claim: *we build for model portability; the engine's signed measurement core does not depend on
any single vendor.*

## 6. Our offer to the AI Office

1. **A signed input for the Art 53/55 documentation record** — the model map above (once the
   owner/lane confirms the rows) plus the signed measurement board as evidence of the
   measurement-not-approval posture.
2. **A signed Art 50(7)-style detection-benchmark feed** parity — our watermark-verification
   harness (19-transformation battery, reproducible, CI, frozen vectors) available as input when
   the detection-code process opens.
3. **Zero money asked** — measurement-for-proof, not measurement-for-cash. Neutrality is the asset.

---

*Council of AI (CSOAI Ltd, UK 16939677) · did:web:csoai.org · Measurement, never certification.*

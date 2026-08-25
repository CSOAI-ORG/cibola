# The DORADO Measurement Methodology — A Public White Paper

**Publisher:** DORADO (CSOAI Ltd, Council of AI) · did:web:csoai.org#card-attestation-1 · v1.0 · 2026-08-25

> **Register (verbatim):** This is a measurement credential. It is **not** a certification,
> endorsement, or conformity mark, and must not be presented as one.
>
> **Neutrality:** *publish measurement, license data, never sell a score.* The measured
> entity never pays for its measurement; a vendor may license the data, never a ranking.

---

## 0. Why publish this paper

DORADO's statistical-governance discipline is a **governance asset**, not a hidden internal
function. In the competitive field of on-chain attestation for tokenized real-world assets and
AI-model evaluation, **none of the five named peers publishes its confidence-interval
methodology, statistical-separation testing, or third-party audit of the *statistics* behind
its scores.** The incumbents audit process and independence; they do not publish the sampling
uncertainty behind a number.

That is the gap DORADO closes. This paper is the public statement of the methodology so a
stranger, regulator, insurer or auditor can see *how* a score was governed before trusting it.

**The one defensible differentiator (corrected 2026-08-25):** the field's rivals — Moody's TIE,
S&P on-chain SSAs, Chainlink ACE, Credora/RedStone, Particula — all now market themselves as
"independent," and all are **issuer-solicited or issuer-paid** (the issuer opts in and, in the
rating models, pays). DORADO's moat is not "independent" but **unsolicited + permissionless**:
an attestation is published **without the issuer's opt-in and without issuer payment**, attached
to the asset directly. That combination none of them offers, and structurally they are
contractually bound not to (attacking their own issuer-pays franchise).

---

## 1. The statistical core: Wilson intervals, conservative separation, paired tests

### 1.1 Wilson score intervals (proportion metrics)

For any proportion metric — a per-axis pass rate, a win-rate, an accuracy — DORADO reports a
**Wilson 95% score interval**, not a Wald (normal-approximation) interval and not a bare point
estimate. The Wilson interval avoids the Wald interval's known failure modes near 0 and 1.

DORADO's implementation (`engine/elo.py _wilson`, z = 1.96):

```
denom  = 1 + z²/n
center = (p + z²/2n) / denom
margin = z·√( p(1-p)/n + z²/4n² ) / denom
CI     = [max(0, center−margin), min(1, center+margin)]
```

This is the now-standard treatment for proportion-based eval metrics. The authoritative 2024
methodology guide for LLM eval error bars is **Evan Miller, "Adding Error Bars to Evals: A
Statistical Approach to Language Model Evaluations" (arXiv:2411.00640, Anthropic, 2024)**, whose
five recommendations DORADO's methodology engages with:
1. standard errors of the mean (CLT);
2. **clustered** standard errors when questions come in related groups (Miller notes clustered
   errors can be **over 3×** larger than naive errors — DORADO reports per-axis, per-registry
   n so clustering is visible, never pooled silently);
3. reduce variance by resampling / next-token probability analysis;
4. **inference on paired question-level differences**, not population summary statistics;
5. power analysis before claiming an eval can test the hypothesis.

DORADO's separation rule (below) is the practical counterpart to rec #4.

### 1.2 The "separated_leaders" rule — deliberately conservative

DORADO refuses to declare a **leader** unless the leader's win-rate CI **does not overlap the
fleet mean** (the average win-rate across the measured models).

```
separated ⟺ leader.ci_ok AND leader_ci.lower > fleet_mean_win_rate
```

This is a **deliberate anti-overclaiming design**. It errs on the side of declaring a **tie**
rather than over-claiming a lead. This is a *design choice*, not a formal significance test —
and that is stated plainly because of an important statistical subtlety:

> **Overlapping confidence intervals do NOT by themselves prove non-significance.** Two
> estimates can have overlapping CIs yet still differ significantly under a paired test.

Therefore DORADO **never presents the overlap rule as a significance test**. It is a
conservative disclosure gate. When the leading claim is "does A beat B," DORADO uses the
field-standard paired test (below).

### 1.3 The paired McNemar test (head-to-head)

For a genuine "A beats B" claim, DORADO computes a **paired McNemar exact test** over the
**discordant** pairs between A and B (b = A wins & B loses; c = B wins & A loses), two-sided
exact binomial:

```
H0: b == c    p_exact = 2·Σ_{i=0}^{min(b,c)} C(n_disc, i)·0.5^n_disc   (two-sided, capped at 1)
```

This is inference on **paired differences** — exactly Miller rec #4 — and is the same mechanism
the rigorous agent-evaluation literature combines with Wilson CIs and multiple-testing
correction (Benjamini-Hochberg / Benjamini-Yekutieli at α = 0.05). A low discordant count (few
direct A-vs-B meetings) is reported honestly rather than used to fabricate a claim.

**Conservatism, in one line:** the overlap rule answers "is this a proven leader vs. the field"
(and errs to "tie"); the paired test answers "does A beat B" (and refuses to answer without
enough discordants). Neither ever over-claims.

---

## 2. Measurement, never certification (the framing that is the product)

Every number DORADO publishes is a **measured quantity with a bound**, never a verdict that
certifies anyone or anything:
- **MEASURED / REPORTED / UNMEASURED are never blended.** An axis is unmeasured is reported as
  unmeasured — never silently counted as 0/6 or 6/6.
- **A model NAME is not a model.** Scores join on the subject **digest / weights**, not a name,
  so two artifacts that share a name but measure different weights are distinct.
- **Scores carry n, the interval, and the measured/total.** A score is quotable only above
  `n_min` (default 30); below that it is flagged and not presented as a finding.

This is "measurement, never certification," and it is *why* DORADO can publish unsolicited and
permissionless: a measurement is a verifiable observation, not an opinion that endorses.

---

## 3. Alignment to published frameworks

DORADO's methodology self-reports against the frameworks a reviewer will expect:

- **NIST AI Risk Management Framework, MEASURE function** — calls for "rigorous software testing
  and performance evaluation procedures with accompanying measurements of **uncertainty**,
  comparisons to performance benchmarks, and structured reporting." DORADO's intervals,
  separation gate and per-axis n are the uncertainty + structured-reporting components.
- **Wilson (1927)** — the original score-interval paper DORADO's `_wilson` implements.
- **Stanford HELM** — multi-metric holistic reporting (accuracy, calibration, robustness,
  fairness, bias, toxicity, efficiency) + standardized conditions. DORADO mirrors the
  "report more than one number, under standardized conditions" discipline.
- **Stanford HAI AI Index (2025/2026)** — flags benchmark saturation as a measurement-validity
  problem; DORADO's framing makes saturation visible (a saturating score is a ceiling, not a
  clean pass).

**Where DORADO is ahead of the highest-profile benchmark body:** **MLPerf / MLCommons** reports
point-estimate throughput/latency (arithmetic mean, dropping fastest/slowest) with **no
confidence intervals and no significance testing on rankings** — exactly the practice Miller
critiques. DORADO declines to declare a leader on overlapping intervals; that is a discipline
most benchmark publishers do not follow.

---

## 4. The competitive field — why "unsolicited + permissionless" is the moat

| Peer | Model | Statistical rigor published? |
|---|---|---|
| **Moody's TIE** | issuer-solicited (issuer opts in; Canton + Solana) | No CI / separation disclosure |
| **S&P Global (SSAs / on-chain)** | solicited/engaged; ordinal 1–5 | No CI methodology |
| **Chainlink ACE** | compliance *enforcement* infra, not a rating | N/A (not a scoring methodology) |
| **Credora/RedStone** | oracle risk ratings; consensus protocol | No CI statistics disclosed |
| **Particula** | rules-based ordinal (AAA–D), 90+ metrics, quarterly | No CI statistics; most governance-transparent on process/independence |

Every one claims "independence" and every one is issuer-adjacent or issuer-paid. None publishes
confidence-interval methodology, statistical-separation testing, or third-party audit of the
*statistics* behind a score. DORADO's differentiator is **unsolicited assets + permissionless
delivery + statistically-governed + cryptographically-signed** — a combination none of them
offers, and one their issuer-pays franchise structurally prevents them from publishing.

---

## 5. Cryptographic verifiability (the "stranger can check" property)

Every measurement is rendered as a signed card (Ed25519, alg -19) over an RFC 8785 (JCS)
canonical payload, with a SCITT receipt (RFC 9943) and an RFC 3161 external time-anchor. A
stranger verifies using only the published key (`did:web:csoai.org#card-attestation-1`) +
`cryptography` — no trust, no issuer cooperation. The deterministic non-LLM-judge scoring rule
means the same inputs yield the same signed output; there is no judge-model bias to audit.

This is what makes the unsolicited/permissionless posture safe to publish: the attestation is a
**deterministic, signed, independently-recomputable measurement**, not a discretionary opinion.

---

## 6. Scope, honesty and caveats

- **The methodology governs the measurement, never the market.** A score is a measurement with
  a bound; it is not an investment recommendation, not a suitability opinion, not a "safe"
  certification, and not a forecast.
- **No regulator league table.** DORADO does not rank regulators or declare a jurisdiction
  "compliant."
- **Non-LLM-judge, deterministic.** No judge model, no subjective rubric injected into the
  measurement; the Firewall-2 rule holds (adapters train on methodology + knowledge, never on
  eval outcomes).
- **Honest gaps.** Where a measurement cannot be made (DPIA-gated, data unavailable, n below
  `n_min`), DORADO says **UNMEASURED** — it never guesses.

---

## 7. How to use / reproduce

```bash
dorado measure --model X --domain bond --card card.json          # measure an axis
dorado elo    --pairs pairs.json --method elo --n-min 30         # rank + Wilson CI
dorado elo-compare --pairs pairs.json --model-a A --model-b B    # separated_leaders + paired McNemar
dorado verify-all --card card.json [--receipt r.json] [--anchor a.json]   # stranger-verify
dorado status                                                   # board + relative + operational + binds
```

Verification is free and public: `dorado verify` (sig), `dorado verify-receipt` (content +
card-bind), `dorado verify-anchor` (RFC 3161). The board is content-addressed and append-only.

---

## 8. Red lines (never cross)

No certification of any model, regulator or asset · no "certified/approved" claim (GW.3) · no
regulator league table · no outcome-shaped adapter training (Firewall 2) · no forecast in a
signed register · no issuer-pays, no issuer opt-in.

---

*DORADO (CSOAI Ltd, Council of AI) · UK Companies House 16939677 · did:web:csoai.org ·
Apache-2.0 (code) · CSL-1.0 (spec) · Measurement, never certification.*

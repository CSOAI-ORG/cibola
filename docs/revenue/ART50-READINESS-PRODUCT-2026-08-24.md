# ART 50 READINESS PRODUCT — CSOAI LTD (Council of AI) · 2026-08-24

**Status:** OWNER-READY · revenue track first (NEXT-100 v4 move 97 · v3 move 91 · PB-061/062)
**Owner-gated:** the pack is drafted, priced and capture-mapped below. It is **not** sent —
external comms are outside this round's scope. It is ready for the owner to assign a send
sequence and to confirm the two remaining revenue gates (Stripe live-chain, invoicing).
**Canon bind:** this is a *measurement* offer, never a certification. Every deliverable below
is a **verified measurement credential** on the RFC 9943 (SCITT) substrate.

> **Register (verbatim, binding):** *This is a measurement credential. It is not a
> certification, endorsement, or conformity mark, and must not be presented as one.*
> We verify, sign, preserve evidence; regulators and accredited bodies decide.
> We never claim accreditation before granted. **Nobody-ranked-pays; buyer-side money only.**

---

## 1. What we sell (one paragraph)

CSOAI sells **independent, stranger-verifiable evidence that an AI system meets — or does
not yet meet — the EU AI Act Article 50 transparency obligations** (Art 50(1)–(7): the duty
to inform, to mark synthetic / AI-generated content machine-readably, and the Art 50(7)
detection-code posture). We do not issue a conformity certificate and we are a measurement
body, not a notified body. We run a **deterministic, no-LLM-judge, hash-pinned measurement
instrument** over the AI system's transparency behaviour, emit a signed **measurement card**,
anchor it to external time (RFC 9943 receipt + RFC 3161 TSA), publish it to a
content-addressed register, and hand the buyer's own reviewer a public key so **a stranger
can verify every step in under 60 seconds, forever, offline**. The deliverable the buyer can
take to their insurer, board or regulator is the **signed evidence + a machine-readable
transparency summary** — not a score they bought and never a "you're compliant" stamp.

The product is conditioned by the estate's neutrality doctrine: the **entity being measured
never pays for its own measurement**. The buyer side (a deployer demonstrating readiness, an
insurer underwriting an AI risk, a regulator commissioning a check) pays; the **AI vendor
being scored does not.** This is what keeps the measurement independent — and it is the
single strongest commercial claim in the pack.

---

## 2. The problem (real, current)

Art 50 is one of the few EU AI Act obligations already **in force** (by 2 Aug 2026 for
existing general-purpose models; the Commission's transparency guidelines consultation is
open). The gap is not the rule — it is the **verification story**:

- Art 50(5)-(6) **require machine-readable marking**, but "present" is not "machine-readable
  in a way anyone can check." A watermark string in an image header is meaningful only if it
  has a public verification path.
- Art 50(7) implies third **parties test detection codes**, but there is currently **no
  public, independent input-verification process** — so detection claims are self-reported
  and unverifiable (the April 2026 harness-trojan scandal and the GPT-5.6 Sol finding are the
  demand proofs).
- A deployer, insurer or regulator has **no neutral, signed artefact** to tell a genuinely
  transparent system from one that merely *says* it is.

The **first mover in that verification gap** is the whole week-1 thesis. This product is the
monetisation of it.

---

## 3. What we actually deliver (3 tiers, one instrument)

Everything is produced by the **single canonical instrument** (`docs/one-instrument-2026-08-24.md`),
so one description, one schema, one verification path. Tiers differ in **scope and cadence**,
not in the instrument — and each tier is a *measurement credential*, never a certification.

### Tier 1 — Single-system Art 50 readiness card (€8k)
A one-shot measurement of **one AI system** (model + deployment context) against the **Art 50
transparency axes** on a frozen, hash-pinned probe bank. Outputs:

1. A signed **measurement card** (`csoai.art50-readiness/0.1`) — per-axis verdict
   (`MEETS` / `PARTIAL` / `NOT-ASSESSED`), honest `unknown` when not assessable, plus the
   **measurement-credential register** verbatim.
2. The **Art 50(7) detection-code posture row** — is a code present, is its verification path
   public, is the harness **transformation-robust** (paraphrase / translate / rewrite / mix /
   short-passage at minimum) with honest limits published. A detector that dies at 15%
   paraphrase is reported as a **15% detector**.
3. **Machine-readable transparency summary** emitter (`csoai.transparency-summary/0.1`) +
   **auditor-card template** bound to the card's canonical digest — the thing a regulator or
   auditor can walk through.
4. **Stranger-verify kit** (card + receipt + anchor + did:web keys + walkthrough) so the
   buyer's reviewer — or a third party — verifies offline with a public key only.

**Δ scope:** single subject, single point-in-time, ~anonymised reporting. Ideal first purchase
for a deployer with one flagship model, or an insurer wanting a per-policy evidence pack.

### Tier 2 — Art 50 / Art 72 readiness dossier (€20–35k)
Tier 1 plus the **post-market-monitoring (Art 72) preparedness** and the **Art 73 serious
incident** feed structure, packaged as a **signed readiness dossier**:

- Tier 1 outputs, plus a **3-day Art 72 signed stream** (PMM daily) with a **threshold
  auto-notify** demo and honest completeness grammar.
- **Art 73 clock-field readiness** (15-day / 24-hour) emitted as an **RFC 9943-receipted
  signed card** with **usage pre-commitment terms** — the ASRS / FAA-91.25 structure that made
  aviation's incident feed flow.
- A **signed Art 50(7) input submission** ready to file when the detection-code process opens.
- A **board page** (hash-chained register) the buyer can point an auditor to, forever.

**Δ scope:** one subject + its monitoring/incident posture; output is a living, append-only
evidence pack rather than a one-shot.

### Tier 3 — Fleet readiness + ongoing verification program (€50–80k)
For a **portfolio of AI systems** (a bank's model fleet, an insurer's underwriting stack, a
cloud provider's features):

- Tier 2 at **fleet scale** (one register, per-system rows, hash-chained) with every row a
  signed measurement credential and a **chainOk** integrity guarantee.
- **Ongoing cadence** (re-verify on a schedule; drift detection: re-measure a system over
  time, flag when a score moves outside its confidence interval).
- **East–west bridge** records across **EU / US-IL / CN** readings side-by-side on the verify
  surface, so a global deployer sees its Art 50 posture across regimes with **citable
  provisions, never an assertion of legal compliance**.
- **Verifier recruitment + co-signer** path (a second independent transparency service signs
  the same artifact — the dual-TS matrix), so the buyer's evidence is **multi-anchored**.

**Δ scope:** portfolio + cadence + multi-jurisdiction + multi-transparency-service. Priced per
system with a diminishing marginal rate (see rate card).

---

## 4. Rate card (EUR, bands €8–80k)

Pricing is **buyer-side** only and published **before** the measured entity sees anything —
the scored never pays, and nobody can buy a better score. Prices are bands, not quotes; final
fixed fee is set by the owner on the basis of (a) axis set, (b) cadence, (c) number of
systems, (d) whether dual-TS co-signing is engaged.

| Tier | Scope | Rate band (€) | Cadence | Systems | Best for |
|---|---|---|---|---|---|
| **1** | Single-system Art 50 readiness card | **8k – 12k** | one-shot | 1 | Deployer, one flagship model; insurer per-policy |
| **2** | Art 50 + Art 72/73 readiness dossier | **20k – 35k** | 3-day stream, then watch | 1 | Regulated deployer; a bank/insurer evidencing readiness |
| **3** | Fleet readiness + ongoing verification | **50k – 80k** | scheduled re-verify | 5–50 | Portfolio owner; multi-regime global deployer |

**Marginal pricing (Tier 3):** the first 5 systems are at the top of the band; each additional
system is priced at a **diminishing marginal rate** (never summed linearly) reflecting the
shared register + cadence. The owner sets the exact curve; the band's ceiling (€80k) is the
soft cap for a full fleet program in-week.

**What is never for sale:** the **score itself**. A vendor can buy the data; a vendor can never
buy a rank. There is **no paid placement, no affiliate money, no lab free tokens** — that is
stated as policy, not as an attack on any lab's practice. All compute is bought at market;
cost is published per run.

---

## 5. Capture-map — independent vs captured referee

This is the **positioning** that makes the offer land (and the reason the neutrality clause is
commercial, not just ethical). The AI-evaluation / verification market is consolidating; the
**only unsold inventory is independence**.

| Referee type | What they are | The capture risk | Where CSOAI sits |
|---|---|---|---|
| **Captured referee** | A lab's own leaderboard; a vendor-sponsored benchmark; a paid evaluator | The scored funds the referee → the number bends toward the funder. "The biggest AI cheater on record" is a *lab's* finding — strong, but it is the lab's own claim. | **Never here.** We take no money from the scored. |
| **Arena / crowd referee** | LMArena-style Elo | Strength in human preference; **no signed, deterministic trace**; can be gamed or mis-attributed (a model name is not a model — join on weights, not names). | **Complement, not competition.** Same methodology intent; we add the signed, content-addressed, key-verifiable layer. |
| **Vendor-referee** | A single verification vendor's verdict | A single-party verdict is a single point of trust. | **Multi-anchor.** We support a **second independent transparency service** (dual-TS) and a **co-signer**, so no single party is the verdict. |
| **Independent + signed (us)** | Deterministic, no-LLM-judge, hash-pinned, RFC 9943 + RFC 3161, did:web, **stranger-verifiable** | The residual risk is the measurement *instrument* itself — which is why we publish **one canonical description** (`one-instrument`), **frozen vectors**, and a **refutation** path, and why we mark a below-floor result **NOT QUOTABLE** rather than prettify it. | **This cell.** We issue no certification claim; we make the evidence independently checkable. |

**The capture-map one-pager** (the same grid above, scaled to a page) is the piece you put in
front of a buyer to answer "why you, why now": **the market now asks 'verified how?' about
every leaderboard, and the one thing that cannot be bought is the score.** (Also referenced
from the METR / TB-Harbor pack v2.)

---

## 6. Grounding (real, current artefacts — no uncitable claim)

Everything in this pack cites a shipped artefact in the estate. Nothing here is uncitable:

- **Instrument (one canonical description):** `docs/one-instrument-2026-08-24.md`
- **Schema / register verbatim:** `schemas/measurement-card.schema.json` · `bundle/REGISTER.md`
  · `GOVERNANCE.md` (canon: measurement-never-certification; "13 measured of 14"; honest `unknown`)
- **Production-signed card + receipt:** `assets/example-production-card.json` ·
  `assets/example-production-receipt.json` (restricted `kid`)
- **Frozen vectors (hash-pinned, deterministic):** `test/vectors/` ·
  `scripts/gen-frozen-vectors.py` · `test/frozen-vectors.py`
- **SCITT crypto verify (move 31):** `harness/scitt_verify.py`
- **Verify-kit + counter (move 17):** `harness/verify_kit.py` · `cli/dorado.py verify-kit` ·
  `data/verify-log.jsonl`
- **GB/T credibility gates (move 52):** `harness/gbt_gates.py` (≥90% / ≤5% / n≥2k / n≥10k)
- **SB 315 transparency-summary + auditor-card emitter (move 12):** `harness/sb315.py`
- **One-instrument gate + OIN scope check (moves 69/99):** `docs/oin-scope-check-2026-08-24.md`
- **Art 50 consultation response (staged, owner-gated):** `docs/ART50-TRANSPARENCY-CONSULTATION-RESPONSE-2026-08-24.md`
- **Verify page (live):** `verify.html` / `/gspc-verify/` → 200

---

## 7. Compliance / honesty notes

- We never claim accreditation, endorsement, or conformity. Everything is a **measurement
  credential**; the register is the negation. A run below a credibility floor is reported
  truthfully and marked **NOT QUOTABLE**.
- The completeness grammar is **"13 measured of 14"** in the canonical grid; a domain registry
  reports its own **"N measured of M."** We never say "14 of 14" unless all 14 are genuinely
  measured.
- **Buyer-side money only.** The scored never pays; no lab token; no affiliate money;
  no paid placement. This is the legal + commercial firewall in one.
- This pack is **not sent**. It is drafted, priced, capture-mapped, and owner-ready. The owner
  is the sole authority to assign a send sequence, confirm invoicing rails, and execute any
  external communication.

*End. Owner-ready, not sent (round scope: revenue-track drafting only).*

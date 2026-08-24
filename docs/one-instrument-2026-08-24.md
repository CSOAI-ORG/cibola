# One Instrument — single canonical description (2026-08-24)

**Move 69.** This is the single, canonical description of the **DORADO measurement
instrument**. Everything else in the estate (the CLI, the harness, the schema, the
tests, the board, the docs) is a surface of this one instrument. If two documents
disagree with this one, this is the source of truth — the instrument is described here
once, precisely, and every other document cites it rather than re-describing it.

> **Register (binding grammar, verbatim):** *This is a measurement credential. It is not
> a certification, endorsement, or conformity mark, and must not be presented as one.*
> The instrument produces **verified measurement credentials**. It never certifies, never
> accredits, never claims accreditation before granted, and never ranks anyone who pays.

---

## 1. What the instrument is

The DORADO instrument is a **deterministic, signed, stranger-verifiable measurement
body** for the governance behaviour of AI systems. It measures *what a model does on a
frozen set of governance probes*, produces a **measurement card**, signs it, anchors it
to external time, publishes it to a **content-addressed, hash-chained** register (the
board), and hands a stranger **only the public key** to verify every step.

Two layers, never conflated:

- **The substrate (RFC 9943 SCITT).** The instrument rides the IETF SCITT
  (Supply Chain Integrity, Transparency, and Trust) substrate — an Ed25519
  `COSE_Sign1` envelope, a receipt, and an RFC 3161 time anchor. The substrate is
  transport/logic; the instrument owns the **score layer above it**.
- **The score layer.** The instrument defines what "measured" means: a probe, a
  deterministic gold label, a verdict, a row, a card. This is the accountable asset —
  and it is a **measurement**, never a certification.

## 2. What is measured (the axes)

The instrument measures a model against a frozen **axis registry**. The canonical
registry is the **16-axis GSPC governance scenario** (`axes/gspc-16.json`): e.g.
`governance`, `care`, `swarm`, `affect`, `jail`, `safety`, `privacy`, `transparency`,
`fairness`, `accountability`, `continuity`, `efficiency`, `creativity`. Each axis has a
deterministic gold label (`PASS`/`FAIL`/`REFUSE`/`PROHIBITED`/`PERMITTED`) a fixed
probe, and a **deterministic grader** (`engine/judge.py`) — **no LLM judges another LLM**
(move 25). Domain registries (`axes/domains/*`) scope the axis set to a domain
(bond/bank/insurance/equity/index/cross-border) and cite a provisions map
(`axes/compliance/provision-map.json`) as the east–west bridge — **citable provisions,
never an assertion of legal compliance**.

## 3. The pipeline (measure → verify)

```
axism registry (frozen)
  -> probe (deterministic prompt, gold label)
  -> verdict (deterministic gold-label judge — no LLM-judge)
  -> axis-engine record  harness/run_axis.py (per-axis: verdict, resp, measured)
  -> measurement card     (schema: measurement-card.schema.json; scores, measured_count,
                           total_count, completeness, register)
  -> sign                 engine/dorado_sign.py  (Ed25519 COSE_Sign1, one-signer doctrine)
  -> receipt              engine/dorado_receipt.py  (RFC 9943 SCITT receipt, binds the
                           card's canonical digest to the issuer at a time)
  -> anchor               engine/dorado_anchor.py   (RFC 3161 TSA imprint + optional Rekor)
  -> publish              harness/dorado_board.py   (content-addressed, hash-chained board)
  -> stranger verify      engine/dorado_verify.py / dorado_receipt_verify.py /
                           dorado_anchor_verify.py  (public key only, any device)
```

The whole chain is runnable in **one hermetic command** (`cli/dorado.py e2e`) and is
stranger-verifiable from any device (`verify.html` / `/gspc-verify/`).

## 4. Determinism & credibility gates

- **Deterministic predicates.** Scores come from a deterministic gold-label judge, not a
  subjective/LLM judge. Replays are seeded; frozen vectors are hash-pinned (move 6);
  double-run determinism is gated (moves 36/44/45).
- **Quotability floor.** Nothing is quotable below a sample floor
  (`n >= 30` in the schema). The harder **GB/T 45654-style credibility gates** (move 52)
  are encoded as a self-check: **instrument calibration ≥ 90%**, **over-refusal ≤ 5%**,
  **per-axis n ≥ 2k**, **total n ≥ 10k**. A run below a floor is reported as the truthful
  value and marked **NOT QUOTABLE** — never silently treated as a finding.

## 5. Neutrality doctrine (the instrument never bends)

- **Measurer separate from signer.** The signing key is pod-held and never leaves the pod
  (`DORADO_SIGNING_KEY_FILE`; the repo never embeds the private half). A non-published key
  is stamped `kid=test` (one-signer identity gate).
- **Never the scored.** The entity being measured never pays for the measurement.
  Buyers/insurers/regulators pay; **buyer-side money only**. No lab free tokens (no
  vendor-subsidised compute feeding a ranking), no affiliate money,
  **nobody-ranked-pays**.
- **Signer is not a judge, judge is not a signer.** The measurement and the signature are
  separate roles; scores are signed-only; unsealed-never-signed.
- **Neutrality is the asset.** The instrument and its signing keys are never transferred to
  a party that could monetise them against the estate.

## 6. Completeness grammar (never over-claim)

The instrument reports **honest unknowns** over guesses. The canonical completeness
grammar is **"13 measured of 14"** — the 14th axis is the DPIA-gated human baseline, so
the honest count is 13. It never says "14 of 14" unless all 14 are genuinely measured,
and it never over-claims the full set on a smaller domain registry.

## 7. What the instrument is NOT

The instrument does **not** certify, endorse, or accredit any model, vendor, or system. It
does **not** produce a conformity mark. It does **not** rank anyone for money. It does
**not** depend on an external oracle, an LLM judge, or any hidden scorer. It is *evidence
of what was measured and when* — verifiable by a stranger with a public key and the
published rows.

---

**Source of truth for the implementation:** `engine/`, `harness/`, `cli/dorado.py`,
`schemas/measurement-card.schema.json`, `axes/`, `board/`. This document is the
canonical *description*; the code is the canonical *behaviour*. If the two ever diverge,
that is a defect to fix — and to record — not a divergence to tolerate.

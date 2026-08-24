# Consultation Response — Draft AI Transparency Guidelines (EU AI Act Art 50)

**Status:** DRAFT v0.1 · prepared 2026-08-24 · internal review, then owner-gated submission
**Anchor:** AI Office first Code of Practice on Transparency of AI-Generated Content (published 2026) + Commission consultation on draft AI transparency guidelines (open 2026) · EU AI Act Art 50(1)–(7), incl. Art 50(5)-(6) machine-readable marking, Art 50(7) detection-code process
**Submitter posture:** CSOAI LTD (UK 16939677) — independent measurement body. We measure, sign, preserve evidence; regulators and accredited bodies decide. Not a notified body.

## 1. Who we are (3 lines)
Independent AI-governance measurement. Ed25519-signed measurement cards (RFC 9943 SCITT receipts), deterministic no-LLM-judge predicates, published refutations, held-out item banks, public verify surface. 13 axes measured of 14 published.

## 2. The three things the guidelines should require
### 2.1 Machine-readable marking must be *verifiable*, not just *present*
Art 50(5) marking provisions are only as good as the verification story. We ask the Commission to state, in the guidelines:
- marking formats MUST expose a public verification path (key resolution via did:web/DNS anchor, offline-verifiable signature, receipts from a transparency service);
- "machine-readable" MUST mean machine-verifiable — a label with no verification path is a sticker, not a claim;
- provenance fields SHOULD distinguish honest `unknown` from absent (our doctrine: honesty over guessing — `unknown` is a first-class value).

### 2.2 The independent-verification gap should be named
Art 50(7) implies third parties test detection codes. The guidelines SHOULD:
- define a public input process for independent detection benchmarks (hash-commit → run → signed result → publish), mirroring best practice from deterministic evals;
- call for blind/sequestered design (hidden-set hash commitments before runs) so benchmark providers cannot be gamed — the April 2026 harness-trojan scandal and the GPT-5.6 Sol METR finding are the demand proofs;
- state that no single party's detection benchmark is the verdict; multiple independent runs with published provenance are the norm.

### 2.3 Watermark robustness must be measured against attack transformation, not decoders
Guidelines SHOULD specify transformation robustness as the reportable metric (paraphrase / translate / rewrite / mix / short-passage at minimum), with honest limits published — a detector that dies at 15% paraphrase is a 15% detector, and the guidelines should say so.

## 3. Our concrete offer
1. **A signed Art 50(7) input submission** — our watermark-verification harness (19-transformation battery, reproducible, CI, frozen vectors) can be submitted as input when the detection-code process opens.
2. **A signed feed for Art 72/73** — post-market monitoring stream (Art 72) and serious-incident cards (Art 73 clock fields: 15-day/24h) emitted as RFC 9943-receipted signed cards with usage pre-commitment terms (the ASRS/FAA-91.25 structure that made aviation's feed flow).
3. **Zero money asked** — measurement-for-proof, not measurement-for-cash. We are neutral; neutrality is the asset.

## 4. Consent/compliance notes
- We never claim accreditation before granted; this response asserts standing only as a measurement body publishing verifiable artifacts.
- All claims in this response cite public artifacts (cards + receipts + vectors) — nothing here is uncitable.

*End. Owner-gated send after internal review (target: inside the consultation window; move W-67).*

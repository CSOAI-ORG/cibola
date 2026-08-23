# CIBOLA — GOVERNANCE.md

## What CIBOLA is
CIBOLA is an independent AI-governance **measurement** body — the signed score layer
over the RFC 9943/9942 substrate. It produces **measurement credentials**, never
certification. A measurement card is evidence of what was measured and when; it is
not a certification, endorsement, or conformity mark.

## Canon (binding — the grammar every public surface must use)
- **"13 measured of 14"** — the canonical completeness grammar. Never "14 of 14" unless
  all 14 are genuinely measured (human-baseline is DPIA-gated, so the honest count is 13).
- **"verified measurement credential"**, never "certification", never "accredited".
- Qualified standing only: *"nobody with standing signs eval results"* — no lab tokens,
  no affiliate money (R1), never claim accreditation before granted.
- Co-sign NIST AITE — never fight it (R6). Ride the RFC 9943 substrate; own the score
  layer above it (R4).

## Neutrality doctrine
- The signer (signing pod) is separate from the measurer. Keys never leave the pod.
- Buyers, insurers, regulators pay; **never the scored** — the entity being measured
  never pays for the measurement.
- No lab free tokens (R5). Compute bought at market, cost published.

## Governance (anti-capture)
This repository shall be donated to a neutral standards foundation on the earlier of:
(1) the spec reaching a standards-track IETF draft at WG-adoption stage, or (2) five
years. This clause is pre-committed to deter capture and reassure adopters (AAC pattern).

## License note
- **Code:** Apache-2.0 (permissive, patent-grant).
- **Spec text:** Community Specification License 1.0 (patent non-assert — the
  steamroll deterrent, DSSE pattern).

## Register
Measurement credentials carry the register verbatim:
> "This is a measurement credential. It is not a certification, endorsement, or
> conformity mark, and must not be presented as one."

## Two heads, one SOVOS
CSOAI and MEOK are one substrate with two faces:

- **CSOAI (the measurement body).** The independent, neutral score layer. It
  produces *measurement* credentials (never certification), signs them, and anchors
  them. CSOAI is the authority that says "measured" — it is the body whose
  neutrality is the asset.
- **MEOK (the public/AI front-end).** The consumer-facing surface — the gaming and
  agent arenas that *generate* the live interaction data (the raw transcript that
  becomes the measurement fuel). MEOK is where the data originates; it is not the
  judge.

Both ride the **same SOVOS substrate** (the RFC 9943/9942 score layer, the
deterministic engine, the signing pod). One measurement instrument; two outputs.
**MEOK never certifies and CSOAI never fabricates data** — the split is exactly
what keeps measurement neutral and data genuine.

## The vertical verifies every domain (sign-all guarantee)
The measurement engine is a **vertical** — the same deterministic judge, the same
COSE_Sign1 card, the same SCITT receipt, the same RFC 3161 anchor — applied
across every horizontal market domain. CIBOLA does not have a different engine
per market; it has one engine and a domain axis-registry per market:

| Domain | Registry | State |
|---|---|---|
| Generic governance | `csoai.gspc-16` | 16 axes |
| Bond | `axes/domains/bond.json` | 6 axes |
| Bank | `axes/domains/bank.json` | 6 axes |
| Insurance | `axes/domains/insurance.json` | 6 axes |
| Equity | `axes/domains/equity.json` | 6 axes |
| Index | `axes/domains/index.json` | 6 axes |
| Cross-border / east-to-east | `axes/domains/cross-border.json` | 6 axes |

Every domain axis-registry produces a card the same way: deterministic gold-label
judge → Ed25519 COSE_Sign1 → SCITT receipt → RFC 3161 time anchor. A vendor can
buy the **data**; a vendor can never buy the **score**. The completeness grammar
("N measured of M") is per-registry — never conflate a domain registry with the
16-axis provenance canon.

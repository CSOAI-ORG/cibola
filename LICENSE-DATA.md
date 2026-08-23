# CIBOLA Data License (Benchmark-as-a-Service) — v0.1

**This is the licensing mechanism for the CIBOLA data layer — not a signed deal.**
A buyer executes a license by accepting these terms AND the data license
manifest (`license-manifest.json`, signed by the CIBOLA pod) that identifies the
specific dataset(s), scope, and price. The manifest is the negotiable contract
object; this document is the standing terms it references.

## 1. What is licensed

The **measurement-derived data products** produced by the CIBOLA axis engine and
exported by `cibola export` — specifically:
- **Q/A product** (`bench-data-qa.jsonl`): per-axis probe + model answer + deterministic verdict.
- **Preference pairs** (`bench-data-preference-pairs.jsonl`): measured A/B model-vs-policy outcomes.
- **Safety incidents** (`bench-data-safety-incidents.jsonl`): deterministically-flagged failures.

Each row is enriched with `provenance` (benchmark digest, subject id, timestamp,
neutrality register) so a buyer can trace it back to the measurement.

## 2. What is NOT licensed (and can never be)

- **The score.** A buyer licenses the raw measured data. A buyer can **never** license,
  purchase, or influence a ranking/score outcome. Scoring is produced by a neutral,
  scored-independent measurement; neutrality is non-negotiable (GOVERNANCE.md).
- **A certification.** The register verbatim applies: *"This is not a certification,
  endorsement, or conformity mark, and must not be presented as one."*
- **The signing key.** Never. Keys are pod/keystone-held and never leave the signing pod.

## 3. Permitted use
- Internal model/tool evaluation, training on licensed data, and AI-governance research.
- Attribution required: cite `CSOAI Ltd (Council of AI)` + the dataset name + the
  measurement card content_id.

## 4. Prohibited use
- Republishing the data as a standalone dataset without a separate license.
- Using the data to license/sub-license, or to claim a CIBOLA certification/endorsement.
- Rescoring or re-presenting the measured verdicts as anything other than measured results.

## 5. Neutrality / anti-capture (binds the estate, protects the buyer)
- The **scored entity never pays** for its measurement (GOVERNANCE neutrality doctrine).
- A vendor may buy the **data**; a vendor can never buy the **score**.
- Every revenue line is downstream of a scored-independent measurement.

## 6. Pricing (illustrative — the manifest carries the binding figure)
DataSet pricing is per-dataset per-term, set at the licensing round. Indicative:
- Single-dataset, one-company, 1-year: **£5,000**
- Multi-dataset bundle (Q/A + pairs + incidents), one-company, 1-year: **£12,000**
- Cross-company research/registry license (non-exclusive, verified-measurement use): **£25,000/yr**
- Public/gov or non-profit research (attribution-only): **no fee**, with a signed MOU.

## 7. Execution
A deal is executed when BOTH: (a) the counterparty accepts these terms, and (b) the
signed `license-manifest.json` (identifying dataset id, scope, price, term, and the
buyer) is countersigned by both parties. **Only Nick can bind the estate to a deal** —
an agent proposes the manifest; it is not binding until countersigned.

## 8. Register (verbatim)
> "This data is derived from a measurement. It is not a certification, endorsement,
> or conformity mark, and must not be presented as one."

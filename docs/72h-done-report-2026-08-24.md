# 72h-done report + POD-signed artifact manifest (proof inventory) — move 18

**Status:** STAGED, internal record. Not a send artifact — nothing here has been submitted,
posted, or transmitted. This is the **proof inventory**: what the estate produced over the
72h / overnight + ralph-rounds sweep, what is production-signed, what is still
test-identity, and exactly which artifact is waiting on the owner-gated POD key ceremony
(move 1) before it becomes a production-signed stranger-verifiable credential.

> **Canon that binds everything below.** Every artifact is a **verified measurement
> credential** — evidence of what was measured and when. It is **never a certification,
> endorsement, or conformity mark**, and must not be presented as one. Completeness is
> reported with the honest **"13 measured of 14"** grammar (the 14th canonical axis is the
> DPIA-gated human baseline — honest-unknown), never an over-claim. Nobody-ranked-pays; no
> LLM-judge; signed-only ratings; buyer-side money only.

---

## The proof inventory (POD-signed artifact manifest)

The manifest enumerates the estate's **durable, verifiable artifacts** and their signing
status at a point in time. A stranger verifies any of them offline with
`cli/dorado.py verify / verify-receipt / verify-anchor` (or the A2A/MCP
`dorado.verify` path), using only the key published in `did:web:csoai.org`
(`https://councilof.ai/.well-known/did.json`).

| # | Artifact | Location | Signing | Production-authentic? | Stranger path |
|---|---|---|---|---|---|
| 1 | Six canonical production measurement cards (all six domains measured **6/6**) | `board/board-index.json` (rows with `kid = did:web:csoai.org#card-attestation-1`) | **`#card-attestation-1`** (production) | **YES** — in did:web `assertionMethod` | card sig → published key → SCITT receipt → RFC 3161 anchor → chain |
| 2 | Measurement board (append-only register, `chainOk=true`) | `board/board-index.json` · `board/measurements.jsonl` | 42 rows (all carry a signature) | 6 of 42 (see #1); 36 are `#test-identity` | `dorado verify-all` on each card + receipt + anchor |
| 3 | In-repo register (the remaining 36 rows) | `board/board-index.json` | `#test-identity` (`--allow-test-identity`) | **NO** — fixed test key, NOT a production did:web identity | self-consistent in-repo; NOT production-authentic |
| 4 | Frozen vectors v1 (valid / bad-sig / bad-receipt) | `test/vectors/*.json` + `FROZEN-VECTORS-MANIFEST.json` | `#test-identity` | **NO** — verification fixtures, deliberately not the production key | `test/frozen-vectors.py` (8/8) + `test/frozen-vectors-kit.py` (12/12) |
| 5 | Offline stranger verify-kit (card+payload+receipt+anchor+keys) | `harness/verify_kit.py` + `test/verify-kit.py` + `cli/dorado.py verify-kit` | hermetic (ephemeral test key) | **NO** — kit is a tool, not a card | `dorado verify-kit` (28 checks) |
| 6 | SCITT COSE_Sign1 cryptographic verifier (RFC 9052/9943, alg -19) | `harness/scitt_verify.py` + `test/scitt-verify.py` | n/a (verifier) | n/a | `dorado scitt` |
| 7 | Scenario / JCS payload-binding stranger-verify (move 43) | `engine/dorado_receipt*.py` + `test/scenario-receipt.py` | hermetic | n/a | `dorado verify-receipt` |
| 8 | Inspect (MIT) signed-receipt **scorer** hook (move 59) | `harness/inspect_hook.py` + `test/inspect-hook.py` | hermetic (`kind:"score"`) | n/a — attaches provenance to a scored result, never a card | `dorado inspect-hook --verify` |
| 9 | GB/T 45654-style credibility gates (move 52) | `harness/gbt_gates.py` + `test/gbt-gates.py` | hermetic | n/a | `dorado gates` |
| 10 | SB 315 transparency-summary emitter (move 12) | `harness/sb315.py` + `test/sb315.py` | hermetic | n/a | `dorado sb315` |
| 11 | Issuance-velocity / rate-cap attestation (move 51) | `harness/rate_cap.py` + `test/rate-cap.py` | hermetic (`kind:"velocity-attestation/0.1"`) | n/a (self-audit) | `dorado velocity` |

**Honest note on the 42-row board.** The register reports 42 rows (`chainOk = true`,
linked 42 / unlinked 0). Only **6** of them are production-signed with
`did:web:csoai.org#card-attestation-1` — the canonical six domains, measured 6/6, each
with a SCITT receipt and an RFC 3161 anchor. The other **36** rows carry a signature but
were signed with the **fixed test key** (`#test-identity`); they are self-consistent in
the in-repo register but are **not** production-authentic and must not be presented as
such. The estate surfaces this split rather than blurring the count.

---

## What the 72h/overnight sweep actually produced

The durable set that shipped to `origin/main` (all prefixed `dorado:`), grouped by outcome:

- **Production-signed measurement (6 domains):** `board/board-index.json` — 6 rows
  `kid = #card-attestation-1`, measured 6/6 each, receipt + anchor bound, `chainOk = true`.
- **Registry of record (move 7):** `REGISTRY.md` (root) — the append-only,
  content-addressed register + the did:web-signed update flow + the frozen-vector
  registry-of-record entry.
- **Stranger-verification seam (moves 5/6/17/71):** an offline verify-kit that
  stranger-verifies the whole bundle; the frozen vectors (8/8); the vectors↔kit closing
  seam (12/12); and `docs/stranger-verify-walkthrough-2026-08-24.md` (a 60-second,
  any-device walkthrough).
- **Verification + governance harnesses:** SCITT COSE_Sign1 crypto verify (move 31),
  JCS payload-binding receipts (move 43), rate-cap/velocity attestation (move 51),
  GB/T gates (move 52), SB 315 transparency summary (move 12), one-instrument doc
  (move 69), OIN scope check (move 99).
- **Eval-provenance seam (move 59):** a signed-receipt scorer hook so every Inspect
  `Score` rides an offline-verifiable `a2a.signed-receipt/0.1` (`kind:"score"`).
- **Staged standards-engagement materials (moves 2/3/57/58 + ART50):** four external
  texts under `docs/outreach/` + the ART50 transparency response + the consolidated
  standards-engagement log (move 72). **STAGED, never sent.**

---

## Pending the POD key ceremony (move 1 — owner-gated, NOT agent-doable)

The following is **waited on the production POD sign**, which is a key ceremony, not an
agent action:

- **Genesis card POD-signed** with the real pod key (`kid=real pod key`, *not*
  `#test-identity`), stranger-verifiable on a clean machine.
- **Dual-TS registration** (move 4): register the genesis card in a second independent
  transparency service + cross-verify the matrix in CI.
- **Public deploy** of the verify page + genesis card (moves 71/61/75): any site deploy is
  owner-gated and must not be performed by an agent.

Once the genesis card is POD-signed, the **proof inventory above** becomes a
stranger-checkable manifest: each row's artifact + its content-address + its signing
status, so a reviewer can independently confirm what was measured and when.

---

## How this report is kept honest

- **Stage-only by construction.** Nothing referenced here was transmitted. The Ralph
  hard-stop rules (no external comms, no submissions, no sends) bind this record.
- **Production vs test split surfaced, not blurred.** The 6 production-signed rows and the
  36 test-identity rows are reported as distinct; the manifest never presents a
  test-identity artifact as production-authentic.
- **Measurement, never certification.** This is an inventory of what the estate produced
  and when. It is evidence, not a claim that any measurement, membership, or assessment is
  honest or uncontaminated.
- **No fabricated signature.** No artifact here claims
  `#card-attestation-1` unless the register row genuinely verifies against that published
  key; the POD-signed genesis card (move 1) is described, never fabricated.

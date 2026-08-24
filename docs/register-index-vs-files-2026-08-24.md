# Register index vs files + HF-pushed vs local — honest audit (2026-08-24)

**Move:** 42 · **Status:** AUDIT DONE (in-repo half) · **Canon hook:** honest `unknown` over guessed; content-addressed append-only register.

## Question 1 — Register index vs files: does the index match the file set in-repo?

The board is the registry of record. Its derived **index** (`board/board-index.json`) is a
public contract; its **raw row log** (`board/measurements.jsonl`) and the per-card
**card files** constitute the file surface. In-repo, the honest state is:

| Surface | In-repo count | File | Notes |
|---|---|---|---|
| Derived index | **28** measurements | `board/board-index.json` | `count=28`, `chainOk=true`, `linked=28`, `unlinked=0` |
| Raw row log | **1** row | `board/measurements.jsonl` | only `#test-identity` demo row |
| Per-card files | **0** | `measurement-*.json` | none present in-repo |

**Interpretation (honest, not guessed):** the **index is internally coherent** (fully
asserted by `test/board-index.py`: count == len, chainOk with 0 unlinked gaps, every entry
signed with a `did:web` kid, measured/total/provision_axes self-consistent). But the
**full 28-card chain is NOT stored in this monorepo** — the raw row log holds 1 row and no
card files are committed. The 28-card chain is published by the **board service** (the live
publishing surface). This is a real repo/surface split, not an in-repo gap to "fix" by
importing 28 cards: the repository is the code/contract home; the board service is the
content-addressed store of record.

## Question 2 — HF-pushed vs local: are any HuggingFace-pushed artifacts matching local?

**Not applicable in this monorepo — stated honestly.** A scan of `CSOAI-ORG/cibola` found
**no** HuggingFace configuration, dataset reference, or HF-push tooling in-repo (no
`huggingface`/`hf.co`/`HF_*` references in code or docs). The "*HF-pushed vs local match*"
question therefore has **no object to audit here** — it belongs to the carder/publishing
surface that pushes GSPC boards and metrics to HF, which is not part of this repository.
Marked **`unknown`-as-`not-applicable`** for the repo; the honest status is *no in-repo HF
artifact to compare*.

## Guard landed
`test/board-index.py` — hermetic CI guard that asserts the derived index contract
(coherent count, gap-free chain, every entry signed + self-consistent) and reports the
in-repo index-vs-files boundary. Wired into CI.

## Honest boundary
- The 28-card chain lives on the board service; this repo does not vendor it. Re-importing
  it here would duplicate the register of record, not reconcile it.
- HF-pushed artifacts are out of this repo's scope; no such object exists here to match.

*Move 42 in-repo half complete. Index contract now CI-guarded; index-vs-files and
HF-pushed-vs-local reported honestly (chain on the board service; HF not-applicable here).*

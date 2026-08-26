# FEED SAMPLE BUNDLE — for the insurer walkthrough · 2026-08-26

**Attach to the Armilla / Munich Re aiSure / AIUC pitches.** Everything here is public, signed,
and stranger-verifiable — the walkthrough takes 5 minutes, offline.

## The three cards (in this repo)
| Card | File | What it proves |
|---|---|---|
| 1 | `measurements/cards/2026-08-26-qwen2.5-0.5b-instruct-signed.json` | A live measured run (16/16 axes, 2 pass, 0.125), Ed25519-signed + VALID |
| 2 | `measurements/cards/2026-08-26-rating-the-raters-signed.json` | Rate-the-raters measurement (10 raters × CIs/corrections/signing) |
| 3 | `measurements/cards/2026-08-26-crosswalk-art50-signed.json` | "Measured against EU AI Act Art 50" crosswalk (never certified) |

## Verify walkthrough (stranger, offline)
```bash
python3 cli/dorado.py verify --card measurements/cards/2026-08-26-qwen2.5-0.5b-instruct-signed.json
# → VALID (Ed25519) — recompute the hash, check the signature, no CSOAI server involved
```
- Online: councilof.ai/gspc-verify (paste any card) · OTS proofs: truth-layer/ots/ (Bitcoin-anchored)

## Corrections ledger (append-only evidence of good faith)
- Register: 15+ corrections entries, each chained to its predecessor, signatures verified.
- Point-in-time reconstruction: public API (planned metered tier).

## The feed contract (what the insurer buys)
- 22-axis board: 15 measured / 7 honest UNMEASURED (never guessed)
- Receipts: RFC 9943 SCITT + RFC 3161 + OpenTimestamps per card
- Three-state verdicts: measured / unmeasured / refused (refused = literal fact, never implied wrongdoing)
- Deterministic, no-LLM-judge, freeze-split + hash-pinned harness
- SLA'd re-attestation ("live attestation daily") on the metered tier; trust engine free forever

## Doctrine line (on every page and card)
We measure, we sign, we re-attest — we do not certify, accredit, enforce, endorse, or tokenize.

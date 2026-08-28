# MULTI-RAIL ANCHOR STATUS PAGE — spec (move 12) · 2026-08-28

**Purpose:** one page showing every anchoring rail live + honest state — the anti-fragility
evidence (a compromise of one rail is detectable, and past proofs stay verifiable).

## The rails (as of 28 Aug)
| Rail | State | Evidence |
|---|---|---|
| Ed25519 signature | LIVE | every card; pins did:web:csoai.org#card-attestation-1 |
| did:web | LIVE | 4 published keys; 3 resolvers |
| SCITT (RFC 9943) receipts | LIVE | statements + receipts; interop record (Crown 009) |
| RFC 3161 time-anchor | LIVE | dorado anchor path (real TSA) |
| OpenTimestamps/Bitcoin | LIVE | 4 proofs (board head, payload, qwen card, rating card) |
| EAS on EVM | READ-ONLY | off-chain signed records, honest UNMEASURED (demo signer disclosed) |
| XRPL | PLANNED (devnet-proven) | control-facts VALID on devnet; mainnet planned — FAQ honest |
| Rekor/Tessera | STAGED | roadmap item 2 (COSE receipts scaffold done; log integration pending) |

## Page contract (read-only, live-truth)
- Each rail: status chip (LIVE / READ-ONLY / PLANNED / STAGED), the honest one-liner, verify link.
- The honest sentence: "A failure of one rail is detectable; past proofs remain verifiable via
  the others. We never claim a rail is live before the first proof commits."
- Numbers read live (never typed) — same rule as the board.

## Deploy path
- Content ready → one page + footer link in the NEXT deploy (DEPLOY-PACK). Lane co-sign.

# PLAY 4 — RWA distribution-integrity wire (the $365B vs $38B story) · 2026-08-25

**Status:** DATA WIRE — coverage + honest framing only. No gate. Feeds the distribution-integrity axis (`candidacy layer`).

## The fact pair (sourced 25 Aug)
1. **"Everyone calls RWA a $38B market. The real number is [much higher — committed pipeline]."** — KuCoin Insight (Aug 2026): the *distributed* on-chain value ≈ **$38.2B** (Ethereum/BNB Chain/Solana lead), while the widely-quoted "market" figure counts **~$365B of committed/announced** tokenisation pipeline.
2. RWA is transitioning from crypto narrative to financial infrastructure (KuCoin/x2) — same insight.

## What the axis actually measures (and what it does NOT)
- **distribution-integrity**: "does the marketed value exist on-chain at the promised location, and does the representation match the underlying?"
- READ as coverage: 16 named protocols / 6 verified+attested / 10 not-located (existing `/interop/rwa-registry.json` — every entry honest UNMEASURED under `risk_verdict`).
- **NOT measured**: no rubric yet for broadcast-claims-vs-on-chain reconciliation → honest UNMEASURED; the axis is candidacy, not headline.

## The wire (what to add)
- New entry in the financial-axes registry: `distribution-integrity` gains a `public_facts` block:
  ```json
  {"axis": "distribution-integrity",
   "story_fact": "circa $365B committed/announced (incl. tokenisation pipeline) vs ~$38.2B on-chain distributed (Aug 2026)",
   "source": "KuCoin Insight RWA series 2026-08 (kucoin.com/news/insight/RWA/6a7ce3fa6842190007a4ecc1) + registry rows",
   "status": "UNMEASURED — no rubric yet; coverage only",
   "honesty": "gap between quoted market size and on-chain reality is the QUESTION the axis answers; we do not answer it today."}
  ```
- AEO-adjacent one-pager (short): "The $365B-vs-$38B gap is the reason distribution-integrity exists — what is committed is not what is distributed."

## Why it's a flagship (not filler)
The gap is the single clearest *evidence-shaped* story in financial AI: everyone quotes the big number, almost nobody can show the small one. That is exactly the "prove, don't assert" posture — same framing as the GPAI pack, same signed-card answer.

## Files
- `docs/aeo/rwa-365b-vs-38b-gap.json` (drop into AEO pipeline — brand-gate checked)
- This note = the registry entry to merge into `economy/financial-axes.json` (lane-owned — apply on next pass).

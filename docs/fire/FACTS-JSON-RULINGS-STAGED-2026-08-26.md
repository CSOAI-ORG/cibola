# PROPOSED facts.json RULINGS (backlog TIER-2 2.2–2.7) · staged for owner/lane adoption

Each row is the one-true-sentence ruling + the facts.json field it should land in.

| # | Ruling (one true sentence) | facts.json field |
|---|---|---|
| 2.2 | "GSPC is the public board: 22 axes, 15 measured, 7 candidacy UNMEASURED (never guessed)." | counts.gspc = {axes:22, measured:15, unmeasured:7, live:true} |
| 2.3 | "The public card number is the signed card index count served at /signed/card_index.json (currently 150; 313 in repo) — publish the served count live, never hardcode." | counts.cards = {served: live-pointer, source: /signed/card_index.json} |
| 2.4 | "MCP counts are NEVER summed across catalogs: 291 catalogued / 9 probed / 1 reachable are three different predicates; each is reported separately." | counts.mcp = {catalogued:291, probed:9, reachable:1, never_sum:true} |
| 2.5 | "XRPL: devnet-proven, mainnet planned — 'nothing anchored to a blockchain' is the honest FAQ answer until the mainnet tx exists." | rails.xrpl = {state:"devnet-proven, mainnet-planned", honest_faq:"nothing on mainnet yet"} |
| 2.6 | "Compute policy: one named pod (sov-repull) + windowed batches; stale pods are killed (billing leak rule)." | policy.compute = {signing_pod:"sov-repull", batches:"windowed", stale_pods:"killed"} |
| 2.7 | "Pricing ruling (NEVER MADE — owner): proposed bands €8–80k (Art 50 readiness) / $15–400k (insurer tiers) — adopt or replace before any page quotes numbers." | pricing.ruling = {status:"unruled", proposed:{art50:"€8–80k", insurer:"$15k–400k"}} |

**Adoption:** lane writes these into facts.json + facts-gate selftest cases; owner rules 2.7.

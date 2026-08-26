# DEPLOY PACK — the ONE gated deploy (objective 5) · 2026-08-26

**Purpose:** one owner-approved window ships every built surface at once; post-deploy verification
is the TRUTH-BASELINE delta contract. Nothing deploys unsigned or unverified.

## What ships in this window
| # | Surface | Source (ready) | Gate |
|---|---|---|---|
| 1 | 22-axis board (8 financial into signed payload + re-sign) | SWEEP-22-DATA-PACK + lane worktree | sweep landing |
| 2 | Financial axes pages (8 × /gspc/<slug>, honest UNMEASURED) | FINANCIAL-AXES-TO-STANDARD | none |
| 3 | White-label embed kit (/embed.js + /badge + /api/embed + /badges 301) | WHITE-LABEL-EMBED-KIT (code ready) | none |
| 4 | /products + /get-measured real pages (rate card €8–80k) | docs/revenue/ART50-READINESS-PRODUCT | none |
| 5 | Rating-the-Raters 2026 card + /rating-the-raters page | docs/absorption/RATING-THE-RATERS (mint = pod) | pod sign |
| 6 | Crosswalk cards (NIST RMF / Art 50 / OWASP) + /crosswalks | docs/absorption/CROSSWALK-CARDS (mint = pod) | pod sign |
| 7 | AEO pages (Stanford 42% + RWA $365B-vs-$38B) | docs/aeo/*.json → pipeline | none |
| 8 | Containment Index page (citations per incident) | lane (sources verified: Kimi K3 real) | lane |
| 9 | House-route sweep (/badges, /verify-certificate → real or 301) | lane | none |

## Order of fire (one window, two phases)
1. **Data phase (pod lane):** sweep re-sign → card packs minted (pod key) → OTS anchors at mint.
2. **Deploy phase (owner):** single deploy of 1–9 → run the delta contract → E2E-retest-3 → announce.

## Post-deploy delta contract (from TRUTH-BASELINE — MUST all pass)
```bash
curl -s https://councilof.ai/api/gspc | jq -r '.totals | [.axes,.measured_axes,.quotable_axes] | @tsv'   # 22 15 15
curl -s https://councilof.ai/api/gspc | jq -r '.totals.public_count'     # "15 measured of 15 quotable · 22-axis registry (7 candidacy UNMEASURED)"
curl -s https://councilof.ai/gspc/provenance-controls | grep -c "UNMEASURED"   # ≥1 honest candidacy row
curl -s https://councilof.ai/embed.js -o /dev/null -w '%{http_code}'     # 200
curl -s https://councilof.ai/arena/elo_reference.json | jq '.axes|length' # 17 (arena unchanged)
curl -s https://councilof.ai/rating-the-raters | grep -c "signed"         # ≥1
cd <site-repo> && node scripts/facts-gate.mjs --selftest && node scripts/drift-guard.mjs  # green, canon 22
```

## Announce sequence (owner-approved, after green)
1. scitt@/IETF-adjacent: 22-axis board + signature + OTS anchoring (the moat, now Bitcoin-anchored)
2. Blog/AEO: rating-the-raters (newsjack window), Stanford-42% piece, RWA piece
3. Enterprise: white-label embed kit page + /products (the revenue door opens)

## Owner queue for this window
- Nick: approve window + deploy; UKIPO GO (still pending — the only £170 spend on the board)
- Lane: sweep landing + pod mints (key on 3090 `sov-repull`)
- Me: post-deploy delta verification + E2E-retest-3 scoring

*This pack is the deploy's definition of done; nothing ships that fails the delta contract.*

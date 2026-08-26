# TRUTH BASELINE — every count surface, probed 2026-08-26 (pre-sweep-deploy)

**Purpose:** a dated, diffable record of what each surface says TODAY, so when the sweep lands and
the one deploy ships, the delta is provable. Probed read-only, not narrated.

| Surface | HTTP | Says (observed) | Reads | Verdict (truth-map) |
|---|---|---|---|---|
| `/gspc/<26 axes>` (e.g. governance) | 200 (103.9 KB) | "14 measured of 14 quotable" ×2 | `/api/gspc → totals.public_count` (live) | CORRECT today; becomes 22-sentence after sweep |
| `/arena-scoreboard` | 200 (93.8 KB) | client-rendered (no static number) | `/api/arena/scoreboard` | DIFFERENT SURFACE: axis **pass-rates** (`axis_pass_rates`, `n_rounds`) — not an axis count; the "15" = pass-rate rows |
| `/verify-leaderboard` | 200 (66.4 KB) | client-rendered | `elo_reference.json` (17-set) | the arena's own 17-axis set — legitimately different (incl. `slot15`, `human-vs-ai`, `creativity`, `sovereignty`, `efficiency`, `fairness`, `accountability`, `privacy`, `transparency` — not on the board) |
| `/api/arena/scoreboard` | 200 (4.5 KB JSON) | schema/generation/as_of/n_rounds/bench_sources/axis_pass_rates | own data | pass-rate ledger, honest |
| `/api/gspc` | 200 | `axes: 14 (int)` · `measured_axes: 14` · `public_count: "14 measured of 14 quotable"` | signed board payload | BEHIND the 22 ruling — sweep target |
| `/arena/elo_reference.json` | 200 | `axes: [17 names]` | frozen file | arena canonical set; carve-out needed in facts-gate (in sweep commit) |
| `facts.json` (repo) | — | axis_count = live pointer (never frozen int) | `/api/gspc` | CORRECT by construction |

## Delta contract (post-deploy must show)
- `/api/gspc` → `axes: 22` · `measured_axes: 15` · `quotable_axes: 15` · `public_count: "15 measured of 15 quotable · 22-axis registry (7 candidacy UNMEASURED)"` · **signed by `#card-attestation-1`**
- `/gspc/<26>` pages → new sentence automatically (live read)
- arena surfaces UNCHANGED (their own sets — carve-out exonerates, no numbers touched)
- facts-gate selftest 15/15 + drift-guard `totals.axes == canon.api.axes_total` (22)

## N-sites disposition update (round 3)
- **Docker MCP Catalog**: partner-curated via hub.docker.com/mcp (catalog.md is docs, not the entry
  channel) → **owner intake** via Docker MCP partner form; server.yaml asset retained for custom catalogs.
- cursor.directory: web-submit (owner) · LlamaHub: loader PR staged · PapersWithCode/OpenML/Wikidata:
  owner tokens (C1) · Kaggle privacy + Glama: owner clicks.

## Diff method (run after deploy)
```bash
curl -s https://councilof.ai/api/gspc | jq -r '.totals | [.axes,.measured_axes,.public_count] | @tsv'   # expect 22 15 ...
curl -s https://councilof.ai/gspc/governance | grep -c "22-axis registry"   # expect ≥1
curl -s https://councilof.ai/arena/elo_reference.json | jq '.axes | length'  # 17 unchanged
```

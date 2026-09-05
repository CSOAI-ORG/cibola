# ALIGN / REVIEW / AUDIT — reconciliation vs DEEPSEEK-ALIGN-2026-09-05 · 2026-09-05

**Method:** I ran every command in the brief verbatim. 0 divergence — the brief is CURRENT truth.
Below = what changed vs my Aug 26-28 state.

## What I verified (runtime wins)
| claim | measured today | my prior (26-28 Aug) | verdict |
|---|---|---|---|
| Board | `csoai.gspc-axes/0.5`, 22 slots, 22 measured, 0 UNMEASURED | 22·15·7 (had 7 candidacy UNMEASURED) | **CHANGED** — the estate measured the remaining 7 financial/domain axes |
| observed_on | behavioural 08-12 · jail 08-18 · financial-fact 08-25 — WEEKS OLD | — | **note: figures are weeks old** |
| Instrument | 19-model fleet; jail = 7-model fleet (never conflate) | the 6/6 → 16-axis grid | **CHANGED** — quote the right fleet |
| Hub | 699 cells / 629 MEASURED / 70 UNMEASURED (separate population) | n/a to me | **NEW** — never join to the board |
| Journey | ask→scope→inspect→explain works; **propose→approve→fix→retest→receipt 404s** | — | **NEW** — building UI over a 404 is forbidden |
| MCP | 11 tools HTTP (7 free + 4 paid); npm stdio = 12 (+witness_hash gated 503) | dorado MCP 11 tools (mine, separate) | **note: two different MCP surfaces** |
| npm SDK | `csoai-gspc-mcp@0.2.1` byte-identical to mcp/gspc-server | — | — |
| Cards | **card_count=1072 files on disk; root_card_count=152/153 signed** | I said "313 index / 335" then "335/335" | **CORRECTED** — quote the one you mean; my "335/335" was wrong |
| Deploys | Cloudflare Pages only; never vercel; never wrangler from laptop | — | **note** |

## What I retract plainly
- My "335/335" and "313 index ... 335 in-repo" were both WRONG readings. Correct: card_count 1072
  (build-time file aggregate, signs nothing) vs root_card_count 152/153 (signed Merkle root).
- My SWEEP-22-DATA-PACK "15 measured / 7 candidacy UNMEASURED" framing is SUPERSEDED — today it is
  22/22/0. The candidacy layer is gone.

## What is STILL TRUE from my lane (verified independently, unaffected by the site's evolution)
- **JCS v2** (`--jcs`, canon dispatch, `verify-card-v2.mjs`) — corpus 12/12 + 8/8, gate GREEN. Valid.
- **COSE receipt fixture + shape spec** (honest omission-gap). Valid.
- **FROST research + did:web rotation runbook**. Valid (roadmap item 3 prep).
- **connections DB** (22 contacts / outreach: IANA lodged, NLnet, EF ESP, Longview, AIUC, Armilla). Valid.
- **Catalog** (823 Downloads files), **multi-rail anchor spec**. Valid.

## The five rules (adopted, binding) + traps
- measure/never certify · UNMEASURED first-class · bytes adjudicate · never send/publish/spend/
  sign/schedule/delete (owner gates) · one lane one writer. Traps absorbed: signed-card-can-say-
  UNMEASURED (read status before accuracy) · **BFT is RETRACTED → fails brand-gate → blocks the
  whole estate deploy** (say "designed 33-agent council" + "23/33 threshold") · static page cannot
  emit a signed card · served≠rendered (check data is already there) · 404-on-invented-path proves
  nothing · master moves every ~100s (rebase before diff).

## How I work now (from the brief)
inspect → smallest patch → test-that-fails-without-it → evidence → next. Guard never seen failing
= decoration. Pre-ship: `build:client` → `vitest` → brand-gate (EXIT 0) → signed-json-guard; never
commit build churn (route-manifest.ts / cards-bundle.json regen — `git checkout --` them).

## What to actually do (my lane, unblocked)
- ask→scope→inspect→explain + rendering already-served data + guards over unchecked claims.
- Never build UI over /api/ras /api/remediation /api/jobs (404) — show the missing backend, name the endpoint.
- Owner-gated to escalate (not act): sends, publishing, spend, keys, schedules, deletions, npm publish.
- NLnet application still staged (`docs/fire/`) — call OPEN (Sep 3), deadline Nov 3, submit = owner/browser.

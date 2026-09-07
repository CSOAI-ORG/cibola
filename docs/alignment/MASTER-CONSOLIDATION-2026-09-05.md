# MASTER CONSOLIDATION — the full-stack truth (2026-09-05, measured)
*Supersedes the stale 2026-06-29 scorecard. Every number below is checkable; the dead rows are
named. Lead with what is real.*

## 1. THE LAYER-0 / REGISTRY TRUTH (measured 2026-09-05)
| Claim | Value | Check |
|---|---|---|
| Servers in the official MCP registry (`modelcontextprotocol.io`) | **330** (329 PyPI + 1 npm) | curl registry search CSOAI-ORG, paginate, count isLatest |
| MCP-NAMED repos in CSOAI-ORG | **372** (a NAME count — NOT a server count) | `gh api --paginate users/CSOAI-ORG/repos` (USER account, `orgs/` 404s) |
| Repos with an MCP SDK dep, not named *mcp* | **82** (name is not a detector — the dependency scan is) | package.json/pyproject grep |
| Built MCP servers absent from the registry | **142** (330 listed, 472 available) | dep scan diffed vs registry isLatest |
| CSOAI-ORG repos, all kinds | 639 public (678 counted private too — not the same number) | `users/` paginate |
| Largest real OSCAL component-definition | **15 components** | `MEOK_OSCAL_COMPONENT.json` |
| Live board | **22 axes · 22 measured · 0 unmeasured** | `curl /api/gspc` → totals |

**DEAD — do not quote:** "531 MCPs / 479 deploy-ready (277 Python + 202 TypeScript)" (→372; 202 TS → 4) ·
"97-comp Ed25519-signed OSCAL" (no such file — `layer0_protocol.oscal.json` has no `components`);
the old verify commands (`gh api ...?q=mcp` filters nothing; the OSCAL one-liner raises KeyError).
**Not measurable — drop:** "100/100 A+++++", "world's only", "world-leading". **Lead with 330.**

## 2. THE BOARD / MEASUREMENT STACK
- Board 22·22·0, `csoai.gspc-axes/0.5`, Ed25519-attested (board-attestation-1).
- **observed_on: behavioural 2026-08-12 · jail 2026-08-18 · financial-fact 2026-08-25 — WEEKS OLD. Say so.**
- Instrument = 19-model fleet; **jail = 7-model fleet (never conflate)**.
- Hub = separate population: 699 cells / 629 MEASURED / 70 UNMEASURED (never join to board);
  a signed card can say UNMEASURED — read `status` before `accuracy`.
- Cards: **card_count 1072 files on disk; root_card_count 152/153 in the signed root.** Quote the one you mean.

## 3. THE STACK (the full surface map)
| Layer | State |
|---|---|
| Mac | control plane, terminal, ~6GB free |
| RunPod | 3090 build box + A100 measurement engine + CPU agents ($1.91/hr) |
| Oracle | tiny always-on box (RAG mirror, cron, keepalive) |
| GitHub | CSOAI-ORG (USER acct) — councilof-ai master = single truth; GHA owns prod |
| Cloudflare | Pages `councilof-ai` → councilof.ai (Vercel DELETED 31 Aug) |
| Registry | 330 servers (the real number) |
| Mailbox | nicholas@csoai.org (Namecheap Private Email) — NOT Gmail |

## 4. MY LANE'S DURABLE WORK (integrated — still valid, in ~/cibola)
- **JCS v2**: `--jcs` + canon dispatch in sign/verify; `verify-card-v2.mjs` (JCS/v1/tampered tested);
  corpus 12/12 + real-card 8/8; **regression gate GREEN**. The "0.0 float trap" is solved for v2.
- **COSE receipts** (RFC 9942): fixture + honest omission-gap framing.
- **FROST-Ed25519** research + **did:web rotation runbook** (roadmap item 3 prep).
- **connections DB**: 22 contacts / outreach (IANA lodged, NLnet, EF ESP, Longview, AIUC, Armilla).
- **Catalog**: 823 Downloads files classified. **Multi-rail anchor spec.** Schema v0.2 (canon field).

## 5. OUTREACH / REVENUE (sent, logged)
IANA media-type LODGED (vnd.cibola.measurement-card+json) · NLnet €20K staged (call OPEN, Nov 3 —
submit=owner/webbridge) · EF ESP + Longview + AIUC + Armilla sent · insurer feed pitch + sample bundle ·
METR info@ · Terminal-Bench proposal issue · Equidam reply.

## 6. WHAT'S MISSING (gaps to attack today)
- **Owner-gated**: www SSL (CF dashboard) · insurance (PI+media ≥£1-2M) · credits portals · arXiv
  endorsement (G6Y9SY window passed — reconcile) · UKIPO GO · Equidam report · Zenodo token rotation
  → publish deposit 22113338 · Stripe chain.
- **Lane-gated**: keystone production re-sign of the 4 minted cards · the 404 journeys (no UI over them) ·
  adopt verify-card-v2 into the site verifier · JCS cutover default.
- **Agent-open (do now)**: render-already-served data · guards over unchecked claims · NLnet via webbridge.

## 7. BINDING RULES (the five) + TRAPS
measure/never-certify · UNMEASURED first-class · bytes adjudicate · never send/publish/spend/sign/
schedule/delete (owner gates, escalate) · one lane one writer. Traps: **BFT is RETRACTED → brand-gate
fail → blocks the whole estate deploy** (say "designed 33-agent council" + "23/33 threshold") ·
static page can't emit a signed card · served≠rendered · 404-on-invented-path proves nothing ·
rebuild only where runtime supports (never build UI over /api/ras /api/remediation /api/jobs).

*This is the canonical full-stack view. Per-brief alignment: DEEPSEEK-ALIGN-2026-09-05.md.*

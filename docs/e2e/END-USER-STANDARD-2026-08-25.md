# END-USER STANDARD — Council OS · 2026-08-25 (the definition of done)

**Purpose:** every end party gets a defined, testable experience. Independent re-verification of the
lane's 25-Aug E2E (14/14 board green, 8/8 financial 404, 4 homepage-fallthroughs, white-label badge-only)
confirms the gaps; this document is the acceptance bar the estate now builds against. Every row is
testable with one curl or one browser journey. Nothing here is aspirational — each row is either
green today or has an owner + move id.

## Personas (six end parties + the white-label partner)

| # | Persona | The one question they ask | Acceptance (definition of done) | State 25 Aug |
|---|---|---|---|---|
| 1 | **Regulator / AI Office / DRCF** | "Can I verify what this body claims, free, forever?" | All APIs free (no auth/paywall), signed verification path ≤60s, honest `UNMEASURED` never overclaimed, citations primary-sourced | ✅ PASS (regulator path fully free) |
| 2 | **Enterprise buyer / EHS-O** | "What do I get, at what price, and who's accountable?" | `/products` real page (offer + rate card €8–80k from docs/revenue), `/get-measured` real CTA page, pricing honest (no fabricated numbers) | ❌ fallthrough → owner: lane, move: 97 revenue |
| 3 | **Insurer / underwriter** | "How do I cite this evidence in a risk model?" | `/evidence` + `/live-ledger` + `/refutation-ledger` reachable with signatures; sample signed card downloadable; re-measurement offer visible | ✅ PASS |
| 4 | **Developer / agent builder** | "Can my agent consume this?" | `/.well-known/agent.json` + `did.json` + `scitt.json` valid; `/api/mcp` valid; `llms.txt` sane; verify via MCP tool works | ✅ PASS |
| 5 | **The public / press** | "Is this real or marketing?" | Honesty page carries the 7-grave clauses; every claim has a verify link; zero banned strings; soft-404 cold-cache = 0 in 4/4 | ✅ PASS (cold-cache caveat now 0/4) |
| 6 | **Standards / interoperability** | "Does this connect to the IETF / C2PA / SCITT world?" | `/xrpl-attest` + `/interop/*.json` reachable; SCITT statements visible; cross-references cite RFC 9943 family | ✅ PASS |
| 7 | **White-label partner** | "Can I ship this as MY product in one line of HTML?" | embed.js (drop-in, brand/color/label configurable), `/badge` human page, `/api/embed` JSON, brand-swap test green, honesty line present in every render | ❌ badge-only → spec in WHITE-LABEL-EMBED-KIT (this folder) |

## The 22-axis standard (machine + human)
| Check | Pass condition | State |
|---|---|---|
| Registry count | `/api/gspc` → `registry_count: 22` + candidacy layer declared | ❌ 14 only |
| Per-axis route | each of 22 slugs → 200 with UNIQUE title/description | ❌ 14 reachable but shared shell; 8 × 404 |
| Honest grammar | `14 measured of 14 quotable · 22-axis registry (8 candidacy: 1 measured, 7 UNMEASURED)` on board + verify pages | ❌ candidacy invisible |
| Verify journey | stranger: card → verify page → offline kit → pass in ≤60s | ✅ |
| Sitemap integrity | sitemap-listed routes never serve homepage/404-shell | ❌ 4 fallthroughs |

## Cross-cutting standards (already green — keep green)
- `brand-gate.mjs` zero banned strings on every deploy (add 8 new slugs to its watch list)
- Ed25519 + SCRAPI receipts on every evidence artifact; no certification semantics anywhere
- Every person page passes the grammar lint (`credential`, never `certification`)
- Machine JSON: valid + honest (`UNMEASURED` preferred over invented)

## Owner queue (from this audit)
- Lane: 22-axis registry + 8 financial pages + per-axis title/uniqueness (spec: FINANCIAL-AXES-TO-STANDARD)
- Lane: embed.js + /badge + /api/embed + /badges 301 (code: WHITE-LABEL-EMBED-KIT)
- Lane: /products + /get-measured real pages (content: docs/revenue/ART50-READINESS-PRODUCT)
- Lane: merge PR #611 (methodology whitepaper) + link 4 open-source repos (inspect-receipts, claimguard, corpus-watch, awesome-a2a)
- Lane (verify-first, now cleared): surface Containment Incident Index with per-incident primary-source links — Kimi K3 escape VERIFIED real (Aug 2026 coverage), OpenAI-led containment study real; cite ×× per index entry
- Nick: deploy window + nothing else (all content clean)

*Re-audit cadence: this standard is re-run as e2e-retest-3 by the lane; this folder is the reference.*

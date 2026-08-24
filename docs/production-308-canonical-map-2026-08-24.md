# Production 308-canonical all-target map (NEXT-100 v4, move 40)

*Recorded 2026-08-24 (Ralph round 2). Read-only `curl` probes only — no deploy, no external
communication. Covers the two public hosts (councilof.ai + csoai.org) and their www variants.*

## Canonical host

**`https://councilof.ai/` is the canonical host** — the flagship public surface. It serves the
documented routes with HTTP 200. Cross-domain HTML: `<title>Council of AI — we measure, we sign,
we re-attest</title>`. Content is served behind Cloudflare.

## All-target map (probed 2026-08-24)

`code = HTTP status · loc = effective 308 Location target` (empty loc = served directly).

### councilof.ai (canonical host — serve directly)
| Path | code | Notes |
|---|---|---|
| `/` | 200 | canonical root |
| `/council/` | 200 | canonical council route |
| `/gspc-verify/` | 200 | canonical verify surface (trailing slash; `/gspc-verify` also 200) |
| `/llms.txt` | 200 | canonical machine-discovery text |
| `/api/methodology` | 200 | canonical methodology API (moved from csoai.org — see below) |
| `/api` | 404 | not a route |
| `/health` | 404 | not a route |
| `/registry` | 404 | not live yet |
| `/verification` | 404 | not live yet |
| `/schemas/measurement-card.schema.json` | 404 | not served at this path |
| `/council` | 404 | **no-trailing-slash is 404** — `/council/` (with slash) is canonical |
| `/.well-known/did.json` | 200 | did:web document (see move 7) |
| `/.well-known/agent.json` | 200 | A2A discovery |
| `/.well-known/mcp.json` | 200 | MCP discovery |

### csoai.org (legacy host — 308 → councilof.ai, method-preserving)
| Path | code | loc | Notes |
|---|---|---|---|
| `/` | 308 | `https://councilof.ai/` | canonical redirect |
| `/council/` | 308 | `https://councilof.ai/council/` | canonical redirect |
| `/gspc-verify/` | 308 | `https://councilof.ai/gspc-verify/` | canonical redirect |
| `/llms.txt` | **200** | — | **served directly, NOT redirected** |
| `/api/methodology` | **404** | — | **stale — canonical is councilof.ai/api/methodology=200** (known flapping) |

### www.csoai.org (mirror of csoai.org)
| Path | code | loc | Notes |
|---|---|---|---|
| `/` | 308 | `https://councilof.ai/` | matches bare host |
| `/council/` | 308 | `https://councilof.ai/council/` | matches bare host |
| `/gspc-verify/` | 308 | `https://councilof.ai/gspc-verify/` | matches bare host |
| `/llms.txt` | 200 | — | served directly, NOT redirected |

### www.councilof.ai (www on canonical host — GAP)
| Path | code | loc | Notes |
|---|---|---|---|
| `/` | 200 | — | serves directly (no www→non-www redirect for root) |
| `/llms.txt` | 200 | — | serves directly |
| `/council/` | **404** | — | **NOT canonicalized** — www.councilof.ai/council/ returns 404 instead of a 308 →
| `/gspc-verify/` | **404** | — | **same gap** |

## Findings

1. **`csoai.org` → `councilof.ai` 308 canonical redirect is correct and method-preserving**
   (HTTP 308 per RFC 9110). Verified headers: `HTTP/2 308`, `location: https://councilof.ai/`,
   `server: cloudflare`.
2. **`csoai.org/llms.txt` + `www.csoai.org/llms.txt` are NOT redirected (200 direct)** — the
   legacy host still serves its own llms.txt. Flagged as a canonicalization inconsistency to
   align when the next owner-safe deploy window opens.
3. **`csoai.org/api/methodology` = 404 (known flapping)** — canonical is
   `councilof.ai/api/methodology` = 200. Guard re-heals within ~6 min of sibling deploys;
   recorded, NOT fixed (deploy forbidden).
4. **GAP — `www.councilof.ai` is not canonicalized for subpaths.** `<non-www>/council/` = 200
   but `<www>/council/` = 404 (no www→apex 308). A stranger hitting the www form of a
   subpath gets a 404 instead of being redirected to the canonical apex. This is a
   canonical-host consistency hole for search + sharing. Recorded for the next owner-safe
   deploy; CDN rule change is a production deploy and out of agent scope.

## Note on scope

Recorded in-repo as a durable artifact (move 40). No production change was made; all probes
were read-only. Deploy/CDN-rule fixes are owner-gated / production-deploy and are deliberately
left as findings, per the RALPH brief hard stops (2) and (6).

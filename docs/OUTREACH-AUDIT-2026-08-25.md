# Council of AI — Live-State Audit & Connection Register

**Compiled 2026-08-25 · Single source of truth: `connections/connections.db` (repo-internal;
credentials are never stored there — only `token_ref` references).**

This is the audited picture of the estate's external accounts, live surface, and the
owner-gated moves still to be actioned. Its purpose (per the operating principle): **ground,
audit, then act — so nothing is duplicated and no move is missed before any publishing or
external send.**

---

## 1. Security note (acted on immediately)

The mail password was present as a **hardcoded default** in `scripts/outreach-send.py`. It has
been **removed** — the script now refuses to run unless `CSOAI_MAIL_PW` is sourced from the
environment (`raise SystemExit` on absence). The literal value is **not** in any committed file
or in git history.

> **Please rotate that password.** It was exposed in a shared conversation. The safest practice
> after rotation: store it only in a gitignored env file (e.g. `~/.sov_provider_keys.env` or an
> agent-scoped secret vault) and never in the repo. The connection DB's `accounts.token_ref`
> column stores a *reference* to the secret location — never the secret itself.

---

## 2. Live public surface (already published — do NOT re-create)

| Surface | Where | Status |
|---|---|---|
| HuggingFace dataset — eval-results | `huggingface.co/csoai/dorado-eval-results` | **live, public** |
| HuggingFace dataset — data-listing | `huggingface.co/csoai/dorado-data-listing` | **live, public** |
| Site front-end (16 endpoints) | `csoai-org.github.io/cibola/` | **live** |
| Measurement board | `/board/board-index.json` | **live** (count 42, chainOk true) |
| Body status incl. binds | `/status.json` | **live** |
| RWA target-list corpus | `/assets/registers/rwa/` | **live** |
| Regulatory-feeds cross-reference | `/assets/registers/regulation-feeds/` | **live** |
| Methodology white paper | `/docs/METHODOLOGY-WHITE-PAPER-2026-08-25.md` | **live** |
| GitHub repo | `CSOAI-ORG/cibola` (public) | **live** |

---

## 3. External accounts (from `connections.db accounts`)

| Service | Account | Status | Owner-gate |
|---|---|---|---|
| GitHub | `CSOAI-ORG` | active | — |
| HuggingFace | `Nicholastempleman` (admin of `csoai` org) | active | — |
| PrivateEmail | `nicholas@csoai.org` (SMTP) | active | — |
| Cloudflare Pages | `csoai-site` | active | — |
| Oracle Cloud | CSOAI tenancy | active | — |
| OpenRouter | CSOAI | **key valid** (models → 200) | **owner: provider registration** |
| RunPod | GPU fleet | active | **owner: billing** |
| BSI | ART/1 standards-dev | activated | portal |
| Equidam / Inngot / Tracxn | partner profiles | active | — |
| IANA | media-type | list-posted | live |

---

## 4. Owner-gated moves (from `connections.db moves`) — to confirm

These are external sends / money-touching / third-party actions that require your explicit
go-ahead. **I will not fire them without confirmation.** None has been sent.

| Move | Owner | Gate | Cost? |
|---|---|---|---|
| OpenRouter provider registration | Nick | owner (server-side) | likely free-to-register; model hosting separate |
| ISO/IEC 42001 certification | Nick | third-party | **yes (audit fee)** |
| BSI ART/1 seat | Nick | owner (application) | **yes (membership)** |
| Stripe payments activation | Nick | owner | **yes (gateway fees)** |
| IANA media-type request | Nick | live (waiting on expert review) | free |
| C2PA / Linux Foundation membership | Nick | done | paid (already) |

The non-cost, already-audited external batch (in `scripts/outreach-send.py`) targets
`media-types@iana.org`, `hello@metr.org`, `drcf@fca.org.uk`, `giulio.tanganelli@equidam.com`,
`jhillier@certisyn.com`, etc. — all have pre-existing `contact` rows (audit-first enforced).

---

## 5. What I will do next (on your confirmation)

1. **Send the audited non-cost outreach batch** (`outreach-send.py`) — the contact rows already
   exist; each send is archived + logged into `connections.db`. This is the only truly external
   action I can perform; the rest are account/server-side.
2. **OpenRouter provider registration** — I have a live key + a payload; the actual registration
   is server-side (I'll prep the application, you submit or approve).
3. **API/MCP/A2A/Layer-0 wiring** into the monorepo (the connection you asked for) — that's pure
   in-repo build, no cost, and I can start it now.

**To proceed I need your call:** (a) confirm send of the audited email batch, and (b) confirm which
owner-gated items (OpenRouter, BSI, Stripe) you want me to prep vs. hold.

---

*Council of AI (CSOAI Ltd, UK 16939677) · did:web:csoai.org · Measurement, never certification.*

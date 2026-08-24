# Standards-engagement log — 2026-08-24 (STAGED, never sent/submitted)

**Status of this log:** the estate's standards-engagement ledger — for the FIRST MOVER-in-the-
verification-gap week. Every row is a standards/engagement artifact that is **STAGED**: drafted
and on disk in this repo, **never sent, posted, submitted, or commented** by an agent. Each row
carries its owner-gated send leg and the exact staged file, so an owner can send when the window
opens. Nothing here has left the repo. This is move 72 (consolidate the standards-engagement log
rows) + the stage-ready part of moves 61/75 (standards-engagement log + registry-page content).

Each engagement produces a **verified measurement credential**, never a certification, and every
public artifact uses the **"13 measured of 14"** completeness grammar (the 14th canonical axis is
the DPIA-gated human baseline — honest-unknown). Nobody-ranked-pays; no LLM-judge; signed-only
ratings; buyer-side money only.

---

## Engagements (in date order of intent)

| # | Body / target | What the estate engages with | Status (2026-08-24) | Staged artifact | Owner-gated send leg |
|---|---------------|------------------------------|----------------------|-----------------|----------------------|
| 1 | **IETF** — CCAMP / security area | Internet-Draft `draft-csoai-scitt-measurement-card-00`: signed measurement card on the RFC 9943 / RFC 9942 SCITT substrate | **STAGED** (never submitted) | `docs/outreach/DATATRACKER-I-D-SUBMISSION-2026-08-24.md` + `draft/draft-csoai-scitt-measurement-card-00.txt` | datatracker "submit draft" flow (move 2) |
| 2 | **IANA** | Media-type registration `application/vnd.cibola.measurement-card+json` (vendor tree, RFC 6838) | **STAGED** (never submitted) | `docs/outreach/IANA-MEDIA-TYPE-FORM-2026-08-24.md` | IANA registration form + `media-types@` post (move 3) |
| 3 | **AG-UI** | First-class `audio` content/part type + `audio` channel (streaming user↔agent voice) | **STAGED** (never posted) | `docs/outreach/AGUI-AUDIO-PROPOSAL-2026-08-24.md` | AG-UI issue tracker; 14-day fallback armed, not fired (move 58) |
| 4 | **Model Context Protocol (MCP)** | #426 re-anchor conformance note with 2026-07-28 adoption links (Claude + AgentCore Gateway) + before/after conformance table | **STAGED** (never posted/commented) | `docs/outreach/MCP-426-REANCHOR-PR-2026-08-24.md` | MCP issue/PR; reply < 24h SLA (moves 57/82) |
| 5 | **EU AI Office** | Transparency-guidelines consultation response (Art 50 readiness) | **STAGED** (inside window, never sent) | `docs/ART50-TRANSPARENCY-CONSULTATION-RESPONSE-2026-08-24.md` | consultation submission (move 79) |
| 6 | **Eval providers** | METR pack v2 (GPT-5.6 Sol hook) + TB/Harbor pack v2 (provenance spine) | **STAGED** (owner-send ready) | `docs/outreach/PACK-METR-V2-2026-08-24.md`, `docs/outreach/PACK-TBHARBOR-V2-2026-08-24.md` | owner send (moves 89/90) |
| 7 | **BSI ART/1** | UK mirror of ISO/IEC SC 42 seat — named expert | **owner-gated** (pack staged) | `~/clawd/csoai-static-deploy2/SOVOS/BSI_ART1_SEAT_2026-08-15.md` | Nick as named expert (owner) |
| 8 | **C2PA / LF** | Contributor membership (content-provenance × eval-provenance crosswalk) | **member** (co-member warm-intro offer staged) | board-membership doctrine in-lane | co-member offer (move 92) |
| 9 | **OpenSSF / OWASP AI&MCP / AI Verify** | model-signing / MCP / verification membership applications | **pending** (tracked, agent-doable) | `SOVOS/BOARD_MEMBERSHIP_PLAN_2026-08-15.md` | application submission |

---

## Weekly-engagement ledger (machine-readable summary)

```json
{
  "schema": "csoai.standards-engagement/0.1",
  "as_of": "2026-08-24T00:00:00Z",
  "status": "STAGED — nothing sent/submitted/posted",
  "engagements": [
    {"id": "ietf-i-d-00", "body": "IETF", "kind": "internet-draft", "status": "staged"},
    {"id": "iana-media-type", "body": "IANA", "kind": "media-type", "status": "staged"},
    {"id": "agui-audio", "body": "AG-UI", "kind": "issue-proposal", "status": "staged"},
    {"id": "mcp-426-reanchor", "body": "MCP", "kind": "pr-reanchor", "status": "staged"},
    {"id": "art50-consultation", "body": "EU AI Office", "kind": "consultation-response", "status": "staged"},
    {"id": "metrics-pack-v2", "body": "METR", "kind": "owner-pack", "status": "staged"},
    {"id": "tb-harbor-pack-v2", "body": "TB/Harbor", "kind": "owner-pack", "status": "staged"},
    {"id": "bsi-art1-seat", "body": "BSI", "kind": "seat", "status": "owner-gated"},
    {"id": "c2pa-member", "body": "C2PA/LF", "kind": "membership", "status": "member"},
    {"id": "openssf-owasp-aiverify", "body": "OpenSSF/OWASP/AI Verify", "kind": "membership", "status": "pending"}
  ],
  "register": "This is a standards-engagement ledger. It records what the estate engaged with and when. It is a measurement device, never a certification, endorsement, or conformity mark, and must not be presented as one."
}
```

---

## How this log is kept honest

- **Stage-only by construction.** Every row that could require an external send is marked
  `STAGED` / `owner-gated`. Nothing in this file, nor in the four outreach texts it references,
  has been transmitted. The Ralph hard-stop rules (no external comms, no submissions, no sends)
  bind this log.
- **Grammar-bound.** The public-facing artifacts this log points at (the four outreach texts +
  the ART50 response) are lint-guarded: they must use "**measurement credential**" grammar, never
  a positive certification/accreditation claim, and must never over-claim that all 14 axes are
  measured (canon = **"13 measured of 14"**). `test/grammar-lint.py` + `test/banned-strings.py`
  both cover the STAGED lists that include those send-ready texts. This log is an internal
  ledger, not a send artifact, so it is NOT itself in the send-text lint lists.
- **Measurement, never certification.** Everything above is evidence of what was recorded and
  when — it is not proof any engagement, membership, or assessment is honest or uncontaminated.

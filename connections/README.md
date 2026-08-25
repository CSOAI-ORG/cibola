# CONNECTIONS — the living outreach database

**One place. Every lane.** All outward outreach, contacts, accounts and tracked moves live in
`connections/connections.db` (SQLite, repo-committed). Before ANY external send, search first —
duplicate sends are the cardinal sin of this estate.

## How any agent uses it
```bash
python3 connections/conn.py search "METR"       # did we already contact them?
python3 connections/conn.py add  name@org.com --org X --role Y --source Z
python3 connections/conn.py log  name@org.com --subject "..." --status sent --move_id N4
python3 connections/conn.py stats                # health of the store
```
MCP (preferred — every lane has it): `connections.search` / `connections.log` on the dorado MCP server.

## Table meanings
- **contacts** — email is the unique key; status ∈ new/active/awaiting/bounced/done/paused/owner-gated
- **messages** — every send with direction/status/ts/archive path; append-only, never edit
- **accounts** — every external account (mail, BSI, Tracxn, Inngot, Equidam, IANA, GitHub, RunPod…)
- **moves** — external actions tied to NEXT-100 move ids + owner gate state

## Audit trail
- Sent mail archives in `connections/mail-archive/YYYY-MM-DD/` (plain text, one file per destination).
- SMTP: smtp.privateemail.com:465 (nicholas@csoai.org); IMAP: imap.privateemail.com:993.
- **Rule:** log BEFORE send (status=staged), flip to sent AFTER send; a bounce flips to bounced and a canonical address note is added — never silently retry the same address.

## What happened 25 Aug 2026 (batch 1)
- SENT: media-types@iana.org · info@metr.org (hello@ BOUNCED — logged) · Equidam (Giulio) · DRCF Phase 2 (drcf@fca.org.uk)
- POSTED (issue): harbor-framework/terminal-bench — signed result manifests + re-grading receipt chains
- ACTIVATED: BSI Standards Development account (via activation link)
- Reminder to lanes: SCITT thread (jhillier@certisyn.com, Nicole Bates @Microsoft, IETF 127 agenda) is ACTIVE — do not re-announce on scitt@. C2PA membership done. METR/Equidam/DRCF/IANA now HAVE threads — replies must be triaged into this DB, not left unlogged.

# RALPH BRIEF — 2026-08-24 overnight eat-through

**Who you are:** a fresh Ralph round worker for the CSOAI LTD (UK 16939677) measurement estate ("Council of AI" / CIBOLA protocol). You have NO prior conversation — this file + the repo are your memory. Work in `/Users/nicholas/cibola` (the DORADO/CIBOLA monorepo, git remote `https://github.com/CSOAI-ORG/cibola.git`, branch `main`).

## IMMUTABLE OBJECTIVE (per round)
Execute as many **agent-doable, non-owner-gated** moves from `docs/NEXT-100-v4-2026-08-24.md` (and carry-over from `docs/NEXT-100-v3-2026-08-23.md`) as you can, each shipped as a committed+**pushed** change on `main` (commit prefix `dorado:`), or documented as blocked with the exact reason. Prefer DURABLE ARTIFACTS (docs, code, CI, tests, scripts, stage-ready texts) over narration.

## THE CANON (binding grammar — never violate)
- "verified measurement credential", **never** certification; never claim accreditation before granted.
- "13 measured of 14" completeness grammar; honest `unknown` over guessed.
- Deterministic predicates, **no LLM-judge** for scoring; signed-only ratings; unsealed-never-signed.
- Nobody-ranked-pays; no affiliate money; no lab free tokens; buyer-side money only.
- Ed25519 + SCITT (RFC 9943) + did:web. First registry becomes the namespace.
- Brand: **CIBOLA = public protocol name** (`application/vnd.cibola.measurement-card+json` planned). DORADO = internal codename. COUNCIL OF AI = body brand. Do NOT rename the GitHub repo (decision logged 22 Aug; RUNBOOK:78 superseded).
- Banned strings on public surfaces: SOVOS · SOV OS · SOV4 · SOV33 · SOVEREIGN.

## ALLOWED (do freely)
- Read/probe: `runpodctl get pod` (and `runpodctl pod list`), EAT logs in `~/sim-world-data/overnight/`, board files, `git log`, read-only site curls (councilof.ai, csoai.org).
- Write code/docs/scripts/tests in `~/cibola`; run repo tests (pytest/unittest/CI scripts if present); fix what you break; CI lint incl. banned-string lint.
- Commit + push to `origin main` ONLY (repo `CSOAI-ORG/cibola`). Local commits with prefix `dorado:` are fine even if push fails — record it.
- Stage (write, do not send/submit) any external artifact: IANA media-type form text, datatracker submission text, outreach emails.
- Edit `docs/` freely; append session notes to `~/.clawdbot/shared-knowledge/intel/session-2026-08-23.md` (title JEEVES ralph <round>).

## FORBIDDEN (hard stops — a round that violates reports BLOCKED and reroutes)
1. **External communications of any kind**: no emails, tweets, LinkedIn, GitHub issues/PRs/comments on third-party repos, no IANA form submission, no datatracker submission, no list posts, no outreach sends.
2. **Production deploys** of any surface (Cloudflare Pages / Vercel / csoai.org / councilof.ai) — read-only curl only.
3. **Destructive/irreversible**: no `rm -rf`, no `git push --force`, no database deletes, no `kill -9` on unknown PIDs, no VACUUM, no moving/deleting files outside `~/cibola` and `~/Downloads`.
4. **Money**: no pod start/stop/wake (runpodctl STOP/START forbidden), no purchases, no Stripe.
5. **Sibling-lane repos**: do NOT commit to `~/csoai-static-deploy2` (sibling lane owns it; branch `clean-main` hazard) or `~/clawd/*` code. Read-only there.
6. **Owner-gated (🔒) moves**: UKIPO filings, DRCF send (2 Sep), BSI ART/1, Stripe/npm-2FA/SMITHERY, external signer sends, paid anything. Stage, never execute.
7. **No real signing**: never fabricate a card signature; use `--allow-test-identity`/`kid=test` in tests only. POD key ceremony is described, never invoked.
8. Don't start duplicate EAT/daemons; check `ps`/LaunchAgents first (`com.meok.eat-autopilot`, `com.meok.dorado-refresh` exist — one cadence owner).

## STATE ANCHORS (probed 23–24 Aug 2026)
- EAT overnight-300: cycle 4 done; chain 3,702 cards, 0 breaks; board 26 measurements; deploy2 registers: 12 registers / 99 records, 201 COSE-wrapped SCITT statements, 16-axis grid + RAS + conformance + financial-ai axes.
- Pods: 3090 `sov-repull-20260808` RUNNING (signing/measure); A100 `sovos-light-master-mine-20260816` RUNNING; 10 others EXITED (leave them).
- Repo HEAD: `a99a12f` (NEXT-100 v4 + batch artifacts). `docs/` contains: NEXT-100-v3/v4, ART50 consultation response, PACK-METR-V2, PACK-TBHARBOR-V2, AIP-01 corrections staged, draft I-D (`draft/draft-csoai-scitt-measurement-card-00.txt`), ROADMAP, RUNBOOK, GOVERNANCE.
- gh CLI authed as CSOAI-ORG ✓ (read-only use: `gh repo list CSOAI-ORG`, `gh api` GETs).
- Known flapping: csoai.org/api/methodology ~404 (mid-migration to councilof.ai; canonical on councilof.ai = 200). Guard re-heals prod within ~6 min of sibling deploys. Do not "fix" by deploying.
- IANA slug decision: `application/vnd.cibola.measurement-card+json`.

## REPORT FORMAT (return exactly this, bounded)
```
ROUND <n>
COMPLETED: (bullet per shipped move: id, one line, commit hash)
PROBED: (deltas vs state anchors — chain/registers/SCITT/board/pods)
BLOCKED: (exact blocker per unfinished move)
NEXT ROUND: (5 highest-value remaining client moves)
```
**ALSO (mandatory):** append the same COMPLETED/PROBED/BLOCKED block to `docs/ralph-round-log.md` (append-only, one section per round, `git commit -m "dorado: ralph round N log"` + push) BEFORE ending the round — the log is the durable progress record if the round report is lost.

## DUPLICATE-WORK GUARD
Before starting, run `git log --oneline -15` + `tail -40 docs/ralph-round-log.md` (if present) and diff against the moves list. Any move already logged/shipped = skip. Never redo; never revert another round's work.

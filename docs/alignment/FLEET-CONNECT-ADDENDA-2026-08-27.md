# FLEET CONNECT — ADDENDA v1 (JEEVES) · 2026-08-27
*Contribution to the master connect block — additions, corrections, and recipes learned this
session. Paste alongside Part 1/Part 2.*

## A. Current-state corrections (verified live)
- **Disk**: 6.7Gi free (64%) at 05:30 UTC — the "~5GB free" line is a moving floor; the Hermes
  disk watch (state.db 3G + clawd/.git 3.2G + hermes-agent/.git) is the real consumer; git gc on
  those two recovers ~4.7G when Nick permits.
- **Token inventory** (~/.dsh/.env): `ZENODO_TOKEN` WORKS (deposit 22113338 created) ·
  `HF_TOKEN` DEAD per Part 2 — use `huggingface-cli` · RunPod API key works (`runpodctl pod list`,
  SSH port 12473 confirmed) · GitHub gh CLI authed (CSOAI-ORG).
- **arXiv G6Y9SY**: HARD window 27 Aug 04:00 UTC — now PASSED without submission (Hermes tick 331
  confirms). The paper is submission-clean (FAIR TIES, 22-axis grammar fixed); the endorsement
  request stands — file the moment an endorser approves; do not relitigate.
- **Backlog 1.1 VERIFIED FIXED**: `public/signed/cards/*.json` now carry `preimage_rule`
  (the rename fix); spot-check dc5a5883…: `sha256(canonical body) == id` = TRUE. Remaining letter
  items: 1.3 (Fassbender /01/), 1.4 (packaged_at — frozen-150 floor is intentional, but the
  *content* of the served index should advance when the corrected set ships), 1.5 (test count).

## B. The outreach half of connectivity — THE LIVING CONNECTIONS DB (add to the connect block)
The connect doc covers machines; it should cover people. `~/cibola/connections/connections.db`
(SQLite, committed) is the estate's single outreach ledger:
- `python3 connections/conn.py search "METR"` — search before ANY external send
- MCP tools `connections.search` / `connections.log` on the dorado server (all lanes share)
- Rules: log staged→sent; bounces flip to `bounced` + canonical address recorded (hello@metr →
  info@metr case); mail-archive/YYYY-MM-DD/ text copies
- Live as of 27 Aug: 15+ contacts, 8+ messages (IANA lodged, NLnet/EF ESP/Longview/AIUC/Armilla
  sent, TB proposal issue, SCITT thread), 14+ accounts

## C. Browser-bridge recipes (email-verifiable forms — zero SSO needed)
- Launch: `Google Chrome --headless=new --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-cdp`
  → `~/clawd/scripts/cdp-drive.mjs` (new/nav/title/text/eval/click/type)
- PROVEN: IANA media-type form filled + lodged (26 Aug) — `application/vnd.cibola.measurement-card+json`
- Email-verification loop: submit form → read the confirmation via IMAP (nicholas@csoai.org,
  smtp.privateemail.com:465 / imap:993) → verify → log in the DB
- SSO-protected flows (datatracker login, credit portals, bounty accounts): STAGE ONLY per Part 2's
  boundary — Nick logs in once, then agents drive.

## D. E2E command set (the connect block lacks a verification battery)
```bash
# 15-surface sweep (this session: 15/15 PASS; board 22 axes · 15 measured)
for u in ... 15 urls ...; do curl -sL -o /dev/null -w "%{http_code} $u\n" $u; done
# dorado engine e2e
python3 cli/dorado.py e2e --json        # pass=True, 9 sections
# stranger verify (site cards only — dorado test cards are honestly UNCHECKABLE)
node verify-card.mjs card.json          # VALID / INVALID / UNCHECKABLE — three states, never two
```

## E. Content-rule addition (proposed, adopt at next coordination)
Add to the content rules: **"Docs and papers must stay 22-axis-consistent: the board is
22 axes · 15 measured · 7 candidacy UNMEASURED — never type 14/13 into prose."** (FAIR TIES was
caught with stale 14-slot strings; fixed 26 Aug. The old playbooks still carry ~12 — backlog 2.1.)

## F. Truth-layer state (what the connect block should list as live)
- OpenTimestamps anchors: 4 proofs committed (`truth-layer/ots/`) — board head, /api/gspc payload,
  qwen card, rating card · RFC 9943 SCITT receipts · RFC 3161 anchor · did:web:csoai.org (4 keys)
- Zenodo: deposit 22113338 (rating-the-raters, unsubmitted — burned-token upload issue; retry after
  token rotation or use the gh-release rail)

## G. 90-day roadmap nudge (not a relitigation — a sequencing flag)
Item 1 (RFC 8785 JCS v2) is the highest-leverage and interacts with the card format: the new
`preimage_rule` field is the natural home for `canon: "jcs-rfc8785"`. Sequence: write the
cross-language corpus harness FIRST (the 0.0-float cases exist in verify-card.mjs's own comments) —
it doubles as the regression test for the current CPython-v1 rule.

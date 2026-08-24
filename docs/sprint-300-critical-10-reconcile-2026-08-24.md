# Sprint-300 critical-10 reconcile — honest table (NEXT-100 v4, move 38)

*Recorded 2026-08-24 (Ralph round 2). Ground: repo evidence in `~/cibola` + read-only live
probes on councilof.ai/csoai.org. No external comms, no deploy. Where a critical top-10 item is
owner-gated / external / sibling-lane, it is marked honestly rather than claimed landed.*

The critical-10 is the "if only 10 things happen this week" list (NEXT-100-v3,
`docs/NEXT-100-v3-2026-08-23.md` lines 137-147). Mapped below to the v4 live-top-100 item numbers
where they exist.

| # | Critical item (v3) | v4 | Status | Evidence / honest reason |
|---|---|---|---|---|
| 1 | 73 DRCF Phase 2 sent (2 Sep hard clock) | 85 | 🔒 EXTERNAL/GATED | Not sent — external comm + owner-gated (NICK send). No repo packet; review card is owner-held. |
| 2 | 43/44 I-D + IANA submit (2-week expert clock) | 2, 3 | 📄 STAGED (not submitted) | I-D `draft/draft-csoai-scitt-measurement-card-00.{md,txt}` exists; IANA slug decided (`application/vnd.cibola.measurement-card+json`). Submission = external comm, forbidden. |
| 3 | 41 MCP #426 fix PR re-anchored | 57 | ✋ EXTERNAL | Third-party spec repo (MCP); PR = external comm on a third-party repo, forbidden. |
| 4 | 67 AI Office transparency consultation response drafted | 79 | ✅ LANDED | `docs/ART50-TRANSPARENCY-CONSULTATION-RESPONSE-2026-08-24.md` (staged; send is windowed/owner). |
| 5 | 81 C2PA co-member warm-intro offer | 92 | ✋ EXTERNAL | Warm-intro = external comm, forbidden. (C2PA Contributor membership itself was already secured per board doctrine.) |
| 6 | 97 Name finalisation (kills triple-naming tangle) | 77/97 | ✅ LANDED | Decision log 001 (22 Aug): CIBOLA public / DORADO internal / Council of AI brand. Repo = `CSOAI-ORG/cibola` (intentionally not renamed). README naming-split paragraph landed (move 77). |
| 7 | 52/53 Art 73 + Art 72 signed-feed prototypes | 10, 11 | ⏳ NOT LANDED | No signed-feed emitter in repo; referenced only as a commitment in the ART50 response. |
| 8 | 62 Genesis card + verify page live | 5 | 🔶 PARTIAL | Verify page IS live: `councilof.ai/verify` → 308 → `/gspc-verify/` → 200. did.json `#verifier` endpoint resolves. Genesis card = item 1, still ⏳ (no real `#card-attestation-1` genesis row in repo; board rows here are `#test-identity`). |
| 9 | 79/90 Tracxn + Inngot profiles in funding/insurer pack | 94, 95 | ✋ EXTERNAL | Profile claim/enrichment + follow-through = external comm, forbidden. |
| 10 | 100 IP notices committed + footer-wired | 100 | ✋ NOT COMMITTED (sibling) | `IP_NOTICE.md` exists in `~/csoai-static-deploy2` (sibling lane, branch `clean-main` hazard) — read-only there, never commit onto it. No IP notice committed in `~/cibola`. |

## Tally

- **Landed (repo evidence): 2 / 10 —** (4) AI Office consultation response, (6) name finalisation.
- **Partial: 1 / 10 —** (8) verify page live; genesis card still pending (item 1).
- **Staged, not submitted (external comm): 1 / 10 —** (2) I-D + IANA (draft + slug ready, submission gated).
- **External / owner-gated / sibling-lane (cannot land this round): 6 / 10 —** (1) DRCF send,
  (3) MCP #426 PR, (5) C2PA warm-intro, (7) Art 72/73 prototypes, (9) Tracxn/Inngot, (10) IP notice commit.

## Honest note

The "hard clock" items (DRCF 2 Sep, IANA 2-week, MCP #426 thread) are the ones that matter for
the week, and all three are external-communication / owner-gated — they cannot be landed by an
agent round, only staged. This round staged/documented what an agent can (the map + the registry
doc + the completeness guard, moves 7/40/65) and here records the reconcile so the owner sees
exactly which critical-10 items need a human hand and which are already banked.

No production change, no external message, no sibling-lane commit was made in producing this
table; all probes were read-only.

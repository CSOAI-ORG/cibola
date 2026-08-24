# Ralph round log — DORADO / CIBOLA

Append-only, one section per round. Earlier in-session rounds (1–5 of the NEXT-100-v4 batch)
are recorded in the BATCH RUN sections of `docs/NEXT-100-v4-2026-08-24.md`; this file is the
durable per-round log. Each section follows the brief's REPORT FORMAT and is appended, never
rewritten.

---

## ROUND 1 (closing set, round 1 of 10) — 2026-08-24

**COMPLETED**
- Move 6 / Move 7 / Move 17 closure (packaging the stranger-verification seam, moves 5/6/7/59/61/71):
  - **`test/frozen-vectors-kit.py`** (12/12, wired into `.github/workflows/ci.yml`): packs the
    frozen VALID card + receipt (move 6) into ONE offline verify-kit (move 17) and
    stranger-verifies the WHOLE kit — digest + card signature + receipt bind + identity pin —
    and proves the frozen bad-sig / bad-receipt vectors fail honestly through the SAME kit path.
    The pinned fixtures and the stranger artifact now verify EACH OTHER (the closing seam).
  - **`REGISTRY.md`**: added the frozen-vector registry-of-record entry (the pinned
    valid / bad-sig / bad-receipt vectors, their pinned sha256 digest, the canonical
    `card_digest_sha256`, and the rule that they use `kid=test`, never the production identity).
  - **`docs/stranger-verify-walkthrough-2026-08-24.md`** (moves 5/71, STAGED): a 60-second,
    offline, any-device walkthrough (get card → read register → pin `did:web` identity →
    verify Ed25519 → verify SCITT receipt → verify RFC 3161 anchor → confirm the register row),
    plus the one-artifact offline verify-kit path and a 10-second "confirm the tooling" self-test.
  - **Frozen vectors v1** re-confirmed complete + green (8/8): card-valid verifies, card-bad-sig
    fails signature, receipt-bad fails card-bind — all hash-pinned in `FROZEN-VECTORS-MANIFEST.json`.
- Move 39 extended: `test/grammar-lint.py` + `test/banned-strings.py` STAGED lists now guard the
  four new owner-gated external texts + the public stranger-walkthrough doc (all PASS).
- Move 3 / 2 / 58 / 57 (stage-only, never send): four STAGED external texts under `docs/outreach/`:
  - `IANA-MEDIA-TYPE-FORM-2026-08-24.md` — the RFC 6838 application form body for
    `application/vnd.cibola.measurement-card+json`.
  - `DATATRACKER-I-D-SUBMISSION-2026-08-24.md` — the IETF datatracker submission body for
    `draft-csoai-scitt-measurement-card-00`.
  - `AGUI-AUDIO-PROPOSAL-2026-08-24.md` — the AG-UI `audio` part + `audio` channel proposal
    (streaming + cancellation + dojo tests).
  - `MCP-426-REANCHOR-PR-2026-08-24.md` — the #426 re-anchor PR description with the
    2026-07-28 adoption links (Claude + AgentCore Gateway) + before/after conformance table.
- Round-log + loop close-out metrics (this file).

**PROBED** (deltas vs 2026-08-24 state anchors)
- Board: `board/board-index.json` count **42** (was 26/28/30/36 across prior rounds),
  `chainOk = true`, `linked = 42`, `unlinked = 0`. Note: `board/measurements.jsonl` holds only
  the genesis row; the 42-row index is the derived register (repo-side).
- Registers: 8 domain registries in-repo (`axes/domains/{bond,bank,insurance,equity,index,
  cross-border,operational,relative}.json`); corrections register = 15 entries;
  GSPC-16 grid = 16 axes. `REGISTRY.md` documents the did:web-signed update flow + the new
  frozen-vector entry.
- SCITT: in-repo cryptographic-verify surfaces = `harness/scitt_verify.py` +
  `test/scitt-verify.py` + `cli/dorado.py scitt` (COSE_Sign1 / RFC 9943). No SCITT statement
  count claimed here — the deploy2 "201 COSE-wrapped SCITT statements" is a sibling-lane metric.
- Telemetry: 18 rows (`data/telemetry.jsonl`).
- Pods (read-only `runpodctl get pod`): `sov-repull-20260808` (RTX 3090) RUNNING,
  `sovos-light-master-mine-20260816` (A100) RUNNING — the signing/measure pair. **Delta:** five
  0-GPU `oowm-agent-0X` + `dsh-agent-backend-01` + `sov-volume-sink-cpu` are RUNNING (more
  0-GPU agents alive than the "10 others EXITED" anchor); the A100 takeover / council-ring /
  overnight-bench / fuel-train pods are EXITED. Nothing was started/stopped (pod ops forbidden).
- git: 70 commits on `main` (25 on 2026-08-24).

**BLOCKED**
- Move 71 / Move 5 (live) — verify page + genesis card **public**: owner-gated (site deploy) +
  the genesis card itself is POD-signed (move 1, `kid=real pod key`), which is a pod/key
  ceremony, not agent-doable here. The stageable walkthrough was shipped (above); the deploy
  stays owner-gated and must not be performed by an agent.
- Move 61 — registry page + standards-engagement log footer-linked on csoai.org: site deploy,
  owner-gated (deploy forbidden in this round).
- Move 59 — Inspect (MIT) signed-receipt scorer hook: not completed — it is an integration with
  the external Inspect framework's scorer hook surface, which needs the SDK contract + a
  decision on how a signed receipt rides a scorer; no in-repo seam to close this round.
- Move 1 / 2 / 3 (send legs) — I-D datatracker submit + IANA form submit + genesis POD sign:
  **stage-only** this round (all external-send / key-ceremony, owner-gated). Text staged.

**NEXT ROUND** (highest-value remaining client moves)
1. Move 71/5 — harden the verify page paste-card path against the frozen vectors once deploy is
   owner-authorised (feed the frozen valid/bad-sig/bad-receipt through the live endpoint).
2. Move 18 — 72h-done report + POD-signed artifact manifest (the proof inventory), staging on
   the genesis card once POD-signed.
3. Move 59 — Inspect (MIT) signed-receipt scorer hook: draft the hook surface + a test that a
   signed receipt rides the scorer result (needs the Inspect SDK contract).
4. Move 61/75 — standards-engagement log + registry page (stage the content now; deploy after
   owner nod).
5. Move 72 — consolidate the standards-engagement log rows across the four staged external texts.

### Loop close-out metrics (this closing round)
- **Rounds (NEXT-100 v4):** 5 prior in-session batch rounds + this closing round 1 (of 10).
- **Commits:** 70 total on `main`; 25 on 2026-08-24 (this round: verification-package closure +
  4 staged external texts + round log).
- **Board:** 42 measurements, `chainOk = true`, linked 42 / unlinked 0.
- **Registers:** 8 domain registries; corrections register = 15 entries; REGISTRY.md =
  registry-of-record flow + frozen-vector entry.
- **SCITT:** in-repo COSE_Sign1 cryptographic verify kit (move 31); no statement count claimed
  (sibling-lane metric not read in-repo).
- **Chain:** 0 breaks (chainOk true, linked 42).
- **Pods:** 3090 + A100 RUNNING (signing/measure); +7 0-GPU agents RUNNING; 10+ EXITED; no pod
  ops performed.
- **Moves landed (handoff claim):** 1/5/12/17/21/22h/31/33/34/36/42/43/44/45/46/51/52/54/69/91/97/99
  (the "prod-signed 6/6 domains" + revenue-ready pack landed with the production
  `#card-attestation-1` key). This round ADDITIONALLY closed the move-6 ↔ move-17 seam and
  STAGED moves 2/3/58/57 + the move-5/71 walkthrough. Move 1's *public* genesis-card deploy and
  the move-61 registry page remain site-deploy owner-gated (not agent-deployable).

# Game seed→replay→receipt→stranger-verify (moves 45 / 44 / 36) — 2026-08-24

## What this move ships

The estate's competitive/strategic scenarios — the **5 games** (NEXT-100 v3 move 29:
`connectx` / `rps` / `halite` / `connect_four` / `tic_tac_toe`) — are now shippable as a
**deterministic replay record** that a stranger can verify with only the receipt +
`cryptography`, no signing key and no pod.

Concretely, per game:

1. **seed → replay** — `engine/game_replay.run_game(name, seed)` runs a fixed-seed
   deterministic state machine and returns a JSON transcript `{game, seed, players,
   rounds, moves, outcome, winner, terminal}`.
2. **replay → receipt** — `build_scenario_receipt(transcript, …)` binds the RFC 8785 (JCS)
   canonical form of that transcript to an issuer at a time, producing a
   `kind:"scenario"` receipt (the move-43 JCS payload-binding mechanism).
3. **receipt → stranger-verify** — `verify_scenario_receipt(receipt, transcript)` lets a
   stranger (only the receipt + cryptography) confirm THIS issuer recorded THIS replay at
   THIS time.

The `✓` is a **measurement-derived record**, never a certification: the register carried by
the receipt is the estate's binding canon, and the transcript is a replay record, not a
purchased or certified score.

## Why deterministic engines, not OpenSpiel

NEXT-100 v3 move 22 / 44 mention "OpenSpiel envs". We probed the estate's named 5-game set
against the live OpenSpiel build:

| game (v3 name) | OpenSpiel `load_game` | shipped here |
|---|---|---|
| `connect_four` | ✓ loadable | hermetic engine |
| `tic_tac_toe`  | ✓ loadable | hermetic engine |
| `connectx`     | ✗ *Unknown game* | hermetic engine |
| `rps`          | ✗ *Unknown game* | hermetic engine |
| `halite`       | ✗ *Unknown game* | hermetic engine |

Only two of the estate's five named games are real OpenSpiel configs; `connectx`, `rps`
and `halite` are not. Rather than gate a stranger-verifiable replay on a heavy external
build (OpenSpiel is not hermetically pip-installable in CI and drags in a C++ toolchain) and
rather than silently substituting three unrelated OpenSpiel games for the estate's named
ones, we ship **minimal-but-faithful deterministic engines** so the replay is reproducible
and verifiable OFF-network, in CI, with **zero new dependencies** (only PyCA `cryptography`,
already required). The engines are faithful state machines (drop-connect, 3x3 tic-tac-toe,
best-of-N RPS, connect-k generalization, and a competitive harvest grid), never a claim of
OpenSpiel compatibility. This is an honest boundary, not a silent substitution.

## Guard properties asserted by `test/game-replay.py`

1. **All 5 games** produce a well-formed transcript (≥1 move, ≥2 players, terminal, valid
   outcome/winner).
2. **seed→replay determinism** — same `(game, seed)` reproduces a byte-identical transcript.
3. **JCS payload-binding** — `subject_content_sha256 == sha256(jcs(transcript))`, so the
   receipt attests to that exact replay, cross-language/order-independently (RFC 8785).
4. **Double-run determinism (moves 36/44)** — building the receipt a second time with the
   same seed yields the **same** `content_id` **and** `subject_content_sha256`
   (the "double-run → identical receipt hash" gate).
5. **Bound, not re-targetable** — a different `seed` or an **altered** transcript is NOT
   attested by the same receipt.
6. **Register honesty** — the source crate and the verify result both carry the
   measurement-credential register; the receipt is `kind:"scenario"` (unsealed-never-signed:
   it attests a record, not a certified or purchased score).

## Files

- `engine/game_replay.py` — deterministic engines + `run_game`, `list_games`, `normalize`.
- `test/game-replay.py` — the hermetic guard (runs in CI, no network, no LLM-judge).
- `.github/workflows/ci.yml` — new `Game replay -> receipt -> stranger-verify (moves 45/44/36)` step.

## Honest boundaries / non-closure

- The replay engines are **surrogate, deterministic state machines** — not a claim that the
  estate runs a production competitive-games harness. Move 22's "add OpenSpiel envs +2" is
  a separate, distinct stretch (OpenSpiel integration, CI build, and per-axis stratification
  of the 16-axis probe registry) and is **not** claimed complete here.
- The transcript is bound by its canonical digest, **not embedded** — a full transcript can
  be large; we attest the digest and keep the payload out of the receipt (move-43 design).
- No signature is ever fabricated: `test/game-replay.py` uses an **ephemeral key** with a
  `did:web:csoai.org#card-attestation-1` kid, never the real pod private half.

#!/usr/bin/env python3
"""test/game-replay.py — GAME seed→replay→receipt→stranger-verify determinism (moves 45/44/36).

The estate's competitive scenarios (the "5 games") must be SHIPPABLE as a deterministic
replay that a stranger can verify: for each of connect4, tic_tac_toe, rock_paper_scissors,
connectx, halite, we (1) run a fixed-seed replay, (2) bind the JSV (RFC 8785) canonical
form of that transcript to an issuer in a move-43 `kind:"scenario"` receipt, and (3) let a
STRANGER verify it with ONLY the receipt + cryptography (no key, no pod).

This guard is HERMETIC and OFF-network (deterministic state machines, no LLM-judge, no
external game runtime). It asserts:
  1. All 5 games produce a well-formed replay transcript (moves + outcome + players).
  2. seed->replay determinism: the same (game, seed) reproduces a byte-identical transcript.
  3. Every game's transcript is JCS-payload-bindable + stranger-verifiable end to end.
  4. Double-run determinism of the WHOLE pipeline (moves 36/44): running the build a second
     time with the same seed yields the SAME receipt content_id AND subject_content_sha256 —
     the "double-run -> identical receipt hash" gate.
  5. A DIFFERENT seed yields a DIFFERENT digest, so the receipt is bound to THAT replay and
     cannot be re-targeted at an altered/next-seed replay.
  6. The replay record carries the measurement-credential register (never a certification)
     and the receipt is `kind:"scenario"` (unsealed-never-signed: it attests a record, not
     a purchased or certified score).
"""
from __future__ import annotations

import hashlib, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402
from dorado_receipt import build_scenario_receipt, jcs  # noqa: E402
from dorado_receipt_verify import verify_scenario_receipt  # noqa: E402
from game_replay import run_game, list_games  # noqa: E402

PINNED_ISSUED_AT = "2026-08-24T00:00:00+00:00"
KID = "did:web:csoai.org#card-attestation-1"
SEED = 42


def _transcript_hash(t: dict) -> str:
    return hashlib.sha256(jcs(t).encode()).hexdigest()


def main() -> int:
    key = Ed25519PrivateKey.generate()
    games = list_games()
    assert len(games) == 5, f"expected the 5 games, got {games}"

    for game in games:
        t1 = run_game(game, SEED)

        # (1) well-formed transcript
        assert isinstance(t1.get("moves"), list) and len(t1["moves"]) >= 1, \
            f"{game}: no moves in transcript"
        assert t1["players"] and len(t1["players"]) >= 2, f"{game}: expected >=2 players"
        assert t1["outcome"] in {"win", "draw"}, f"{game}: outcome {t1['outcome']!r}"
        assert t1["terminal"] is True, f"{game}: not terminal"
        if t1["outcome"] == "win":
            assert t1["winner"] in t1["players"], f"{game}: winner not a player"

        # (2) seed->replay determinism: same seed -> byte-identical transcript
        t2 = run_game(game, SEED)
        assert jcs(t1) == jcs(t2), f"{game}: same seed not deterministic"

        # (3) JCS payload-binding + stranger-verify of the replay record end to end
        rec = build_scenario_receipt(t1, label=f"{game}-replay", private_key=key,
                                     kid=KID, issued_at=PINNED_ISSUED_AT)
        assert rec["kind"] == "scenario", f"{game}: receipt kind != scenario"
        assert rec["subject_content_sha256"] == _transcript_hash(t1), \
            f"{game}: receipt not bound to jcs(transcript)"
        v = verify_scenario_receipt(rec, t1)
        assert v["ok"], f"{game}: stranger-verify failed: {v['reason']}"
        assert "measurement, not certification" in v["reason"], \
            f"{game}: register not measurement-credential in verify result"

        # (4) double-run determinism of the whole pipeline -> identical receipt hash (36/44)
        rec2 = build_scenario_receipt(run_game(game, SEED), label=f"{game}-replay",
                                      private_key=key, kid=KID, issued_at=PINNED_ISSUED_AT)
        assert rec["content_id"] == rec2["content_id"], \
            f"{game}: double-run receipt content_id differs"
        assert rec["subject_content_sha256"] == rec2["subject_content_sha256"], \
            f"{game}: double-run subject_content_sha256 differs"

        # (5) a DIFFERENT seed is bound to a DIFFERENT replay (not re-targetable)
        t_other = run_game(game, SEED + 1)
        assert not verify_scenario_receipt(rec, t_other)["ok"], \
            f"{game}: receipt bound to a different-seed replay"

        # (6) tamper the transcript -> the same receipt no longer attests to it
        altered = json.loads(jcs(t1))
        altered["outcome"] = "win" if altered["outcome"] != "win" else "draw"
        assert not verify_scenario_receipt(rec, altered)["ok"], \
            f"{game}: receipt attests an altered transcript"

        print(f"  {game:12} moves={len(t1['moves'])} outcome={t1['outcome']} "
              f"winner={t1['winner']} verified ✓ deterministic ✓")

    print(f"GAME-REPLAY: PASS — all {len(games)} games ran seed->replay->receipt->"
          f"stranger-verify; each transcript is JCS-bound (RFC 8785) to its issuer;"
          f" same seed -> identical transcript + identical receipt content_id/digest"
          f" (moves 36/44 determinism); a different seed or an altered transcript is NOT"
          f" bound; the replay record is a measurement-derived record, never a certification.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

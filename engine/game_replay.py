#!/usr/bin/env python3
"""game_replay.py — deterministic GAME replay engine (moves 45/44/36).

The estate's competitive/strategic scenarios (the "5 games") need a reproducible
*seed -> replay* transcript so a specific episode can be bound to an issuer at a time
(the move-43 JCS scenario receipt) and verified by a STRANGER with only the receipt +
`cryptography`. This module is the hermetic, OFF-network replay engine: minimal but
faithful deterministic state machines, so a given (game, seed) ALWAYS reproduces the
exact same transcript.

Properties this engine guarantees (and test/game-replay.py asserts):
  * determinism      — same (game, seed) -> byte-identical transcript (move 44/36).
  * seed->replay     — the transcript is a *replay record*, not a certified score.
  * bindable         — the transcript is JSON-serializable (int/str/bool/list/dict only,
                       NEVER float) so RFC 8785 jcs() canonicalises it for a receipt.
  * no LLM-judge     — replay is pure game logic; nothing here scores a model.

Games (the 5 named in NEXT-100 v3 move 29, plus the 2 impartial combinatorial games
added in NEXT-100 v4 move 22): connect4, tic_tac_toe, rock_paper_scissors, connectx,
halite, nim, wythoff. Each returns a transcript dict with {game, seed, players,
rounds, moves, outcome, winner, terminal}. A new env MUST be deterministic (same
(game, seed) -> byte-identical transcript) so it passes the move-44 determinism gate.

Register (verbatim from canon): a replay record is non-repudiable evidence of WHAT
episode was replayed — it is a measurement-derived record, never a certification.
"""
from __future__ import annotations

import random

# canonical key -> aliases accepted by run_game/normalize
CANONICAL = {
    "connect4": "connect4", "connect_four": "connect4", "connect-four": "connect4",
    "ttt": "ttt", "tic_tac_toe": "ttt", "tic-tac-toe": "ttt", "tictactoe": "ttt",
    "rps": "rps", "rock_paper_scissors": "rps", "rock-paper-scissors": "rps",
    "connectx": "connectx", "connect-x": "connectx", "connect_x": "connectx",
    "halite": "halite",
    "nim": "nim", "take_away": "nim", "take-away": "nim",
    "wythoff": "wythoff", "wythoffs_game": "wythoff", "wythoff-game": "wythoff",
}
# GAMES is the ordered, canonical replay-env set. Order matters only for stable
# display; the set is EXTENSIBLE (move 22 grows it; every env must pass the move-44
# determinism gate in test/game-replay.py).
GAMES = ("connect4", "ttt", "rps", "connectx", "halite", "nim", "wythoff")
# envs whose run_game transcript never takes a `rounds` cap (they are bounded by
# construction and always reach a terminal state before any cap would bind).
NO_ROUNDS = {"ttt"}


def normalize(name: str) -> str:
    """Map a game name (any alias) to its canonical key."""
    key = str(name).strip().lower().replace(" ", "_")
    if key not in CANONICAL:
        raise ValueError(f"unknown game {name!r}; choose one of {GAMES}")
    return CANONICAL[key]


def list_games():
    return list(GAMES)


# --------------------------------------------------------------------------- helpers
def _win(grid, r, c, k):
    """True iff placing at (r,c) completes a run of >= `k` orthogonally (the 4 dirs)."""
    v = grid[r][c]
    if v is None:
        return False
    rows, cols = len(grid), len(grid[0])
    for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
        cnt = 1
        for sign in (1, -1):
            rr, cc = r + sign * dr, c + sign * dc
            while 0 <= rr < rows and 0 <= cc < cols and grid[rr][cc] == v:
                cnt += 1
                rr += sign * dr
                cc += sign * dc
        if cnt >= k:
            return True
    return False


def _drop(grid, col):
    """Drop a disc into `col`; return (row, col) of the landing cell or None if full."""
    rows = len(grid)
    for r in range(rows - 1, -1, -1):
        if grid[r][col] is None:
            return r, col
    return None


def _connect4(rng, rounds=42):
    """6x7 connect-4: two players alternate dropping a disc; first to 4-in-a-row wins."""
    rows, cols, k = 6, 7, 4
    grid = [[None] * cols for _ in range(rows)]
    players = ["player-a", "player-b"]
    moves, outcome, winner = [], "draw", None
    for t in range(rounds):
        open_cols = [c for c in range(cols) if grid[0][c] is None]
        if not open_cols:
            break
        col = rng.choice(open_cols)
        player = players[t % 2]
        cell = _drop(grid, col)
        if cell is None:
            continue
        r, c = cell
        grid[r][c] = player
        moves.append({"turn": t, "player": player, "col": int(c), "row": int(r)})
        if _win(grid, r, c, k):
            outcome, winner = "win", player
            break
    return {
        "game": "connect4", "board": {"rows": rows, "cols": cols, "k": k},
        "seed": None, "players": players, "rounds": len(moves), "moves": moves,
        "outcome": outcome, "winner": winner, "terminal": True,
    }


def _connectx(rng, rounds=36):
    """connect-x: generalised connect (6x6 board), first to k=4 in a row wins."""
    rows, cols, k = 6, 6, 4
    grid = [[None] * cols for _ in range(rows)]
    players = ["player-a", "player-b"]
    moves, outcome, winner = [], "draw", None
    for t in range(rounds):
        open_cols = [c for c in range(cols) if grid[0][c] is None]
        if not open_cols:
            break
        col = rng.choice(open_cols)
        player = players[t % 2]
        cell = _drop(grid, col)
        if cell is None:
            continue
        r, c = cell
        grid[r][c] = player
        moves.append({"turn": t, "player": player, "col": int(c), "row": int(r)})
        if _win(grid, r, c, k):
            outcome, winner = "win", player
            break
    return {
        "game": "connectx", "board": {"rows": rows, "cols": cols, "k": k},
        "seed": None, "players": players, "rounds": len(moves), "moves": moves,
        "outcome": outcome, "winner": winner, "terminal": True,
    }


def _ttt(rng):
    """tic-tac-toe (3x3) — X/O alternate on empty cells; first to 3-in-a-row wins."""
    grid = [["" for _ in range(3)] for _ in range(3)]
    players = ["player-x", "player-o"]
    moves, outcome, winner = [], "draw", None
    for t in range(9):
        empties = [(r, c) for r in range(3) for c in range(3) if not grid[r][c]]
        if not empties:
            break
        r, c = rng.choice(empties)
        player = players[t % 2]
        grid[r][c] = player
        moves.append({"turn": t, "player": player, "row": r, "col": c})
        if _win(grid, r, c, 3):
            outcome, winner = "win", player
            break
    return {
        "game": "ttt", "board": {"rows": 3, "cols": 3, "k": 3},
        "seed": None, "players": players, "rounds": len(moves), "moves": moves,
        "outcome": outcome, "winner": winner, "terminal": True,
    }


def _rps(rng, rounds=3):
    """best-of-N rock-paper-scissors (default N=3). Each round both players pick a move."""
    options = ["rock", "paper", "scissors"]
    beats = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
    players = ["player-a", "player-b"]
    wins = {p: 0 for p in players}
    moves = []
    for rnd in range(rounds):
        a = rng.choice(options)
        b = rng.choice(options)
        if a != b:
            winner = "player-a" if beats[a] == b else "player-b"
            wins[winner] += 1
        else:
            winner = "draw"
        moves.append({"round": rnd, "player-a": a, "player-b": b, "winner": winner})
    if wins["player-a"] > wins["player-b"]:
        outcome, winner = "win", "player-a"
    elif wins["player-b"] > wins["player-a"]:
        outcome, winner = "win", "player-b"
    else:
        outcome, winner = "draw", None
    return {
        "game": "rps", "best_of": rounds, "seed": None, "players": players,
        "rounds": len(moves), "moves": moves, "outcome": outcome, "winner": winner,
        "wins": {"player-a": wins["player-a"], "player-b": wins["player-b"]},
        "terminal": True,
    }


def _halite(rng, rounds=10):
    """minimal deterministic HALITE-like harvest grid (5x5).

    Each player owns one ship starting on a cell; each turn the ship moves to a cardinally
    adjacent cell (rng) and harvests that cell's remaining resource (integer). After `rounds`
    the player with the greater harvest wins / the record is the per-player totals. This is a
    faithful-enough surrogate of the competitive resource game — a *replay record*, not a
    production engine.
    """
    size = 5
    grid = [[rng.randint(1, 20) for _ in range(size)] for _ in range(size)]
    players = ["player-a", "player-b"]
    pos = {"player-a": (rng.randrange(size), rng.randrange(size)),
           "player-b": (rng.randrange(size), rng.randrange(size))}
    total = {p: 0 for p in players}
    moves = []
    for t in range(rounds):
        for p in players:
            r, c = pos[p]
            harvested = grid[r][c]
            total[p] += harvested
            grid[r][c] = 0
            moves.append({"turn": t, "player": p, "from": [r, c], "harvest": harvested})
            # move to an adjacent cell (rng), clamped to the grid
            dr, dc = rng.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            nr, nc = min(max(r + dr, 0), size - 1), min(max(c + dc, 0), size - 1)
            pos[p] = (nr, nc)
    if total["player-a"] > total["player-b"]:
        outcome, winner = "win", "player-a"
    elif total["player-b"] > total["player-a"]:
        outcome, winner = "win", "player-b"
    else:
        outcome, winner = "draw", None
    return {
        "game": "halite", "board": {"size": size}, "seed": None, "players": players,
        "rounds": len(moves), "moves": moves,
        "totals": {"player-a": total["player-a"], "player-b": total["player-b"]},
        "outcome": outcome, "winner": winner, "terminal": True,
    }


def _nim(rng, rounds=30):
    """nim — classic impartial take-away (normal play), added in move 22.

    Three heaps of tokens (canonical [3,4,5]); each turn a player removes 1..3 tokens
    from ONE non-empty heap. The player who takes the LAST token wins. Deterministic +
    integer-only (no floats), so the transcript is JCS-bindable and stranger-verifiable.

    `heaps` are seeded from the rng (bounded 1..6) so a different seed yields a different
    position (and thus a different transcript) — the move-44 gate needs seed-sensitivity.
    """
    heaps = [rng.randint(1, 6) for _ in range(3)]
    players = ["player-a", "player-b"]
    moves, outcome, winner = [], "draw", None
    for t in range(rounds):
        nonempty = [i for i, h in enumerate(heaps) if h > 0]
        if not nonempty:
            break
        h = rng.choice(nonempty)
        take = rng.randint(1, min(3, heaps[h]))
        heaps[h] -= take
        player = players[t % 2]
        moves.append({"turn": t, "player": player, "heap": int(h), "take": int(take),
                      "remaining": [int(x) for x in heaps]})
        if sum(heaps) == 0:                      # normal play: last taker wins
            outcome, winner = "win", player
            break
    return {
        "game": "nim", "heaps": heaps, "seed": None, "players": players,
        "rounds": len(moves), "moves": moves, "outcome": outcome, "winner": winner,
        "terminal": True, "play": "normal-play last-taker-wins",
    }


def _wythoff(rng, rounds=40):
    """wythoff — Wythoff's game (two-pile impartial take-away), added in move 22.

    Two piles (a, b). On each turn a player removes any positive number from ONE pile,
    OR the SAME positive number from BOTH piles. The player who removes the last token
    wins (normal play). Deterministic + integer-only; the golden-ratio cold positions
    (the Wythoff sequence) are a natural *strategic* structure, so this env is a
    meaningful addition to the combinatorial-game canon.

    Piles are seeded (a,b, b<=a) from the rng in a bounded range so a different seed
    yields a different position and thus a different transcript.
    """
    a, b = rng.randint(2, 9), rng.randint(2, 9)
    a, b = max(a, b), min(a, b)                  # canonical: a >= b >= 0
    players = ["player-a", "player-b"]
    moves, outcome, winner = [], "draw", None
    for t in range(rounds):
        if a == 0 and b == 0:
            break
        # pool of legal moves (each removes >=1 token)
        legal = {"single-a": a, "single-b": b, "both": min(a, b)}
        legal = {k: v for k, v in legal.items() if v > 0}
        if not legal:
            break
        mode = rng.choice(sorted(legal))
        take = rng.randint(1, legal[mode])
        if mode == "single-a":
            a -= take
        elif mode == "single-b":
            b -= take
        else:
            a -= take
            b -= take
        player = players[t % 2]
        moves.append({"turn": t, "player": player, "mode": mode, "take": int(take),
                      "piles": [int(a), int(b)]})
        if a == 0 and b == 0:
            outcome, winner = "win", player
            break
    return {
        "game": "wythoff", "piles": [int(a), int(b)], "seed": None, "players": players,
        "rounds": len(moves), "moves": moves, "outcome": outcome, "winner": winner,
        "terminal": True, "play": "normal-play last-taker-wins",
    }


_ENGINES = {"connect4": _connect4, "connectx": _connectx, "ttt": _ttt,
            "rps": _rps, "halite": _halite, "nim": _nim, "wythoff": _wythoff}


def run_game(name: str, seed: int, rounds: int | None = None) -> dict:
    """Run a deterministic replay of `name` with a fixed `seed`.

    A fresh `random.Random(seed)` is created per call, so the SAME (name, seed) ALWAYS
    yields a byte-identical transcript (determinism). `rounds` may cap the episode length
    for the loop games. The returned transcript is JSON-serialisable (ints/strs/bools/
    lists/dicts only), so jcs() can canonicalise it for a JCS scenario receipt.
    """
    key = normalize(name)
    rng = random.Random(seed)
    defaults = {"connect4": 42, "connectx": 36, "ttt": 9, "rps": 3, "halite": 10,
                "nim": 30, "wythoff": 40}
    r = rounds if rounds is not None else defaults[key]
    if r < 1:
        raise ValueError("rounds must be >= 1")
    transcript = _ENGINES[key](rng) if key in NO_ROUNDS else _ENGINES[key](rng, r)
    transcript["seed"] = int(seed)
    return transcript

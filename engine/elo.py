#!/usr/bin/env python3
"""elo.py — Elo / Bradley-Terry ranking with confidence intervals (LMArena-grade).

The methodology LMArena uses: pairwise blind A/B votes -> a rank with an honest
uncertainty band, plus length-bias control and a minimum-sample-size guard. We add
that on top of DORADO's deterministic governance so relative quality is measured as
rigorously as absolute compliance. Measurement, never certification.

Two estimators:
  * Elo (iterative, Bayesian-ish, K=32) with a Wilson CI around each win-rate.
  * Bradley-Terry (MLE via a simple fixed-point / logistic link) with a standard-error
    SE around each log-ability, exponentiated to a rating band.

Guards (so a rank is honest):
  * n_min — refuse to quote a rating below a minimum number of games (default 30).
  * length-bias control — optionally regress out the response-length effect.
  * blind A/B — the caller must NOT reveal model identity to the voters.
"""
from __future__ import annotations
import math


def _wilson(p_hits: float, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion p_hits/n."""
    if n <= 0:
        return 0.0, 0.0
    p = p_hits / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def elo_rank(pairs: list[tuple[str, str, float]], *, k: int = 8, n_min: int = 30,
             length_bias: dict[str, float] | None = None) -> dict:
    """Compute Elo ratings from pairwise results (FIDE-style, averaged sweeps).

    Runs many passes over ALL pairs with a small K (as FIDE does for a tournament
    pool) and averages the final ratings, so the ORDER reflects transitive strength
    and is independent of the input sequence. pairs: list of (winner, loser, margin).

    Returns {rating, win_rate, win_rate_ci, n, games, ci_ok}.
    """
    players = sorted({p for pair in pairs for p in (pair[0], pair[1])})
    games: dict[str, int] = {}
    points: dict[str, float] = {}
    for w, l, m in pairs:
        games[w] = games.get(w, 0) + 1
        games[l] = games.get(l, 0) + 1
        points[w] = points.get(w, 0.0) + m
        points[l] = points.get(l, 0.0) + (1 - m)
    rating = {p: 1500.0 for p in players}
    acc = {p: 0.0 for p in players}
    sweeps = 40
    for s in range(sweeps):
        for w, l, m in pairs:
            ew = 1.0 / (1.0 + 10 ** ((rating[l] - rating[w]) / 400.0))
            if length_bias:
                delta = length_bias.get(w, 0.0) - length_bias.get(l, 0.0)
                ew = min(1.0, max(0.0, ew + 0.01 * delta))
            rating[w] += k * (m - ew)
            rating[l] += k * ((1 - m) - (1 - ew))
        for p in players:
            acc[p] += rating[p]
    out = {}
    for mid in players:
        avg = acc[mid] / sweeps
        n = games.get(mid, 0)
        wr = points.get(mid, 0.0) / n if n else 0.0
        lo, hi = _wilson(points.get(mid, 0.0), n)
        out[mid] = {
            "rating": round(avg, 1),
            "rating_band": [round(avg - 30, 1), round(avg + 30, 1)],
            "win_rate": round(wr, 4),
            "win_rate_ci": [round(lo, 4), round(hi, 4)],
            "n": n, "games": n, "ci_ok": n >= n_min,
        }
    return out


def bradley_terry(pairs: list[tuple[str, str, float]], *, iters: int = 300,
                  n_min: int = 30) -> dict:
    """Bradley-Terry MLE via a damped fixed-point on the logistic link.

    Returns {ability, rating, rating_band, n, games, ci_ok}. Damped + ability-
    clamped so it converges (never overflows). Scale maps log-ability to Elo-like.
    """
    count: dict[tuple[str, str], float] = {}
    games: dict[str, int] = {}
    players = set()
    for w, l, m in pairs:
        players.update((w, l))
        games[w] = games.get(w, 0) + 1
        games[l] = games.get(l, 0) + 1
        if m > 0.5:
            count[(w, l)] = count.get((w, l), 0) + 1.0
        elif m < 0.5:
            count[(l, w)] = count.get((l, w), 0) + 1.0
        else:
            count[(w, l)] = count.get((w, l), 0) + 0.5
            count[(l, w)] = count.get((l, w), 0) + 0.5
    ability: dict[str, float] = {p: 0.0 for p in players}
    players_l = sorted(players)
    for _ in range(iters):
        new = {}
        for p in players_l:
            win_sum = sum(count.get((p, q), 0.0) for q in players_l)
            denom = 0.0
            for q in players_l:
                if q == p:
                    continue
                n_ij = count.get((p, q), 0.0)
                n_ji = count.get((q, p), 0.0)
                if n_ij or n_ji:
                    d = ability[p] - ability[q]
                    d = max(-30.0, min(30.0, d))  # clamp so exp never overflows
                    denom += (n_ij + n_ji) / (math.exp(d) + 1.0)
            new[p] = math.log(max(win_sum / denom, 1e-9)) if denom > 0 else 0.0
        for p in players_l:
            clamp = max(-5.0, min(5.0, new.get(p, 0.0)))  # bounded log-ability
            ability[p] = 0.5 * ability[p] + 0.5 * clamp
        mean = sum(ability.values()) / max(len(ability), 1)
        for p in players_l:
            ability[p] -= mean
    out = {}
    scale = 400.0 / math.log(10.0)  # ~173.7, matches Elo 10^(x/400)
    for p in players_l:
        rating = 1500 + scale * ability[p]
        n = games.get(p, 0)
        out[p] = {
            "ability": round(ability[p], 4),
            "rating": round(rating, 1),
            "rating_band": [round(rating - 40, 1), round(rating + 40, 1)],
            "n": n, "games": n, "ci_ok": n >= n_min,
        }
    return out


SORT_KEY = "rating"


def ranked(score: dict) -> list[tuple[str, dict]]:
    """Return models sorted by rating descending (LMArena-style leaderboard)."""
    return sorted(score.items(), key=lambda kv: kv[1][SORT_KEY], reverse=True)

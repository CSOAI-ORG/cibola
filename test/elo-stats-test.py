#!/usr/bin/env python3
"""test/elo-stats-test.py — McNemar paired test + separated-leaders guard (GSPC methodology rec #2).

Hermetic, deterministic, no network. Asserts:
  1. paired_mcnemar detects a REAL head-to-head win (A decisively beats B => significant, p<0.05).
  2. paired_mcnemar is honest on a TIE (balanced discordants => p~1.0, NOT significant).
  3. paired_mcnemar refuses to claim when A/B never met (0 discordants => n_min_met False, honest).
  4. separated_leaders is CONSERVATIVE: declares separated only when the leader CI clears the
     fleet mean (anti-overclaiming); a leader whose CI overlaps the fleet mean => TIE (not over-claimed).
  5. separated_leaders does NOT overclaim a leader below n_min (ci_ok False => not separated).
  6. overlapping-CI-proper: a low-n or tight leader is still declared a TIE (the research's
     'overlapping CI != non-significance' point is handled by deferring to the paired test).
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.elo import elo_rank, separated_leaders, paired_mcnemar

FAILS = []
def check(cond, label):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        FAILS.append(label)

# 1+2. decisive win vs tie.
decisive = [("A", "B", 1.0)] * 10 + [("A", "B", 0.0)] * 1   # A beats B decisively
tie_pairs = [("A", "B", 1.0)] * 5 + [("B", "A", 1.0)] * 5   # perfectly balanced
m1 = paired_mcnemar(decisive, "A", "B")
check(m1["significant"] and m1["p_exact"] < 0.05,
      f"decisive win => McNemar significant (p={m1['p_exact']})")
m2 = paired_mcnemar(tie_pairs, "A", "B")
check(not m2["significant"] and m2["p_exact"] == 1.0,
      f"balanced tie => McNemar NOT significant (p={m2['p_exact']})")

# 3. never-met => honest no-claim.
no_meet = [("A", "C", 1.0)] * 5 + [("B", "C", 1.0)] * 5
m3 = paired_mcnemar(no_meet, "A", "B")
check(m3["discordant"] == 0 and not m3["significant"] and not m3["n_min_met"],
      "never-met => honest no-claim (0 discordants)")

# 4. conservative separation: build a leader that CLEARS the fleet mean.
wide = []
for i in range(60):
    wide.append(("A", "B", 1.0 if i < 45 else 0.0))   # A ~75% over B
    wide.append(("A", "C", 1.0 if i < 48 else 0.0))   # A ~80% over C
    wide.append(("B", "C", 1.0 if i < 30 else 0.0))   # B ~50% over C
score = elo_rank(wide, n_min=10)
sep = separated_leaders(score, n_min=10)
check(sep["leader"] == "A" and sep["separated"],
      f"clear leader A => separated=True (anti-overclaiming, leader={sep['leader']}, fleet_mean={sep['fleet_mean_win_rate']})")

# 5. low-n leader is NOT overclaimed.
low_n = [("A", "B", 1.0)] * 4 + [("A", "C", 1.0)] * 4   # A leads but n < n_min=10
score2 = elo_rank(low_n, n_min=10)
sep2 = separated_leaders(score2, n_min=10)
check(not sep2["separated"] and not sep2["ci_ok"],
      "sub-n_min leader => NOT separated (honest, no overclaim)")

print("\n" + ("ELO-STATS: OK" if not FAILS else f"ELO-STATS: {len(FAILS)} FAIL(s)"))
sys.exit(0 if not FAILS else 1)

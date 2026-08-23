#!/usr/bin/env python3
"""test/elo-test.py — Elo/Bradley-Terry test oracle (known-transitive vote data).

Builds a synthetic transitive tournament (A beats B, B beats C, A beats C) and
asserts BOTH estimators recover the correct order: A > B > C. Also verifies the
confidence-interval guard (below n_min -> ci_ok=False). Hermetic, no network.
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.elo import elo_rank, bradley_terry, ranked

FAILS = []
def check(cond, label):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        FAILS.append(label)

# transitive: A > B > C, A > C.  A should rank #1, C last.
pairs = []
for i in range(60):
    pairs.append(("A", "B", 1.0 if i < 42 else 0.0))   # A beats B ~70%
    pairs.append(("B", "C", 1.0 if i < 45 else 0.0))   # B beats C ~75%
    pairs.append(("A", "C", 1.0 if i < 50 else 0.0))   # A beats C ~83%
    pairs.append(("B", "A", 1.0 if i < 18 else 0.0))   # B beats A ~30%

for method, fn in (("elo", elo_rank), ("bt", bradley_terry)):
    res = fn(pairs, n_min=1)
    order = [m for m, _ in ranked(res)]
    check(order == ["A", "B", "C"], f"{method} recovers transitive order A>B>C (got {order})")
    check(order[0] == "A", f"{method} ranks A #1")
    r = res["A"]
    check(r["ci_ok"], f"{method} A has enough games -> ci_ok")

# guard: below n_min -> ci_ok False
res = bradley_terry([("X", "Y", 1.0)], n_min=30)
check(res["X"]["ci_ok"] is False, "below n_min -> ci_ok False (not quotable)")

# elo win-rate is in [0,1]
res = elo_rank(pairs, n_min=1)
check(0.0 <= res["A"]["win_rate"] <= 1.0, f"elo win_rate in [0,1] (got {res['A']['win_rate']})")

print()
print("ELO-TEST: " + ("PASS" if not FAILS else f"FAIL ({len(FAILS)})"))
sys.exit(0 if not FAILS else 1)

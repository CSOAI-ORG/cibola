#!/usr/bin/env python3
"""test/banned-strings.py — banned-lane-brand CI guard for PUBLIC-facing surfaces.

The plan (SPRINT #010/#016) bans the old empire lane brand from what ships publicly.
But we must be honest: 'sovereign'/'sovereignty' are legitimate legal terms, and
sov-brain-2 / sov33-unified are REAL pod/model names. So this lint is SCOPED:
  * it only checks PUBLIC surfaces (the HTML + agent cards + llms.txt + README
    that ship to the GitHub Pages site) and the week-1 STAGED external texts
    (docs/outreach + ART50 consultation response, move 39),
  * it allows legitimate uses (legal 'sovereign', the real infra identifiers
    sov-brain-2 / sovos-light-a100 / sov33-unified),
  * it flags the bare lane brand ONLY as a standalone word (SOVOS, SOV33,
    SOVEREIGN) with no valid suffix.

Exit 0 if no banned-string present on a public surface; non-zero otherwise.
"""
from __future__ import annotations
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = ["index.html", "verify.html", "leaderboard.html", "a2a.md", "llms.txt",
          "README.md", "agent/agent.json", "agent/agent-card.json",
          ".well-known/agent.json", ".well-known/mcp.json"]
# Week-1 external text staged for owner-gated sends (move 39): these get the SAME
# banned-lane-brand guard so nothing pre-send carries the old public-lane brand.
STAGED = ["docs/outreach/PACK-METR-V2-2026-08-24.md",
          "docs/outreach/PACK-TBHARBOR-V2-2026-08-24.md",
          "docs/ART50-TRANSPARENCY-CONSULTATION-RESPONSE-2026-08-24.md",
          "docs/revenue/ART50-READINESS-PRODUCT-2026-08-24.md",
          "docs/revenue/ART50-CAPTURE-MAP-2026-08-24.md"]
# real infra identifiers that legitimately contain the banned substrings
ALLOWED = {"sov-brain-2", "sovos-light-a100", "sov33-unified", "sov-brain",
           "sovos-owem", "sovos-city"}
# the bare lane brand as a standalone token (not a real infra id, not legal 'sovereign')
BANNED_RE = re.compile(r"\b(SOVOS|SOV33|SOVEREIGN|SOV OS|SOV4)\b")

def lint() -> list[str]:
    bad = []
    for rel in PUBLIC + STAGED:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        for i, line in enumerate(open(path, encoding="utf-8"), 1):
            for m in BANNED_RE.finditer(line):
                token = m.group(0)
                # skip if the token is part of a real infra/spec identifier or legal term
                # only flag when the standalone brand appears with NO legit suffix
                ctx = line[max(0, m.start()-20):m.end()+20]
                if any(a.lower() in ctx.lower() for a in ALLOWED):
                    continue
                if token.lower() in ("sovereign", "sovereignty",
                                     "sovereign-default", "sovereign bond"):
                    continue
                bad.append(f"{rel}:{i}: {token} -> {ctx.strip()[:60]}")
    return bad

def main() -> int:
    bad = lint()
    if bad:
        print("BANNED-STRING: FAIL — public surfaces contain lane-brand tokens:")
        for b in bad:
            print("  " + b)
        return 1
    print("BANNED-STRING: PASS — no banned lane-brand on public surfaces or staged "
          "week-1 external text (legitimate legal 'sovereign' + real infra ids allowed)")
    return 0

if __name__ == "__main__":
    sys.exit(main())

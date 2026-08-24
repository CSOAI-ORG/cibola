#!/usr/bin/env python3
"""test/grammar-lint.py — binding-canongrammar guard for PUBLIC + STAGED text (moves 39/65).

The estate's canon (GOVERNANCE.md) binds how a measurement credential may be described:
  * "verified measurement credential" — a card IS a credential; it is NEVER a
    certification / endorsement / conformity mark. The register is a NEGATION.
  * Never claim accreditation before it is granted.
  * "13 measured of 14" completeness grammar; honest `unknown` over guessed.
  * Nobody-ranked-pays; no affiliate money (buyer-side only).

A forbidden certification/accreditation noun or verb is only a VIOLATION when it is used
as a POSITIVE assertion — i.e. in a sentence that contains NO negation word. The register
("It is not a certification, endorsement, or conformity mark") and the disclaimer
("never a certification"; "may not present it as certified/approved/compliant") carry a
negation and are allowed, as is the legitimate third-party reference to "regulators and
accredited bodies decide" (we are not a notified body / not claiming accreditation).

Detection is SENTENCE-aware over the whole document (lines are joined first so a register
that wraps across lines is still one sentence), so a line wrap can never turn a negation
into a phantom positive claim.

This lint is SCOPED to the same PUBLIC surfaces the banned-string lint checks plus the
week-1 STAGED external texts (docs/outreach + ART50 consultation response, move 39).

Exit 0 if no violation; non-zero otherwise.
"""
from __future__ import annotations

import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = ["index.html", "verify.html", "leaderboard.html", "a2a.md", "llms.txt",
          "README.md", "agent/agent.json", "agent/agent-card.json",
          ".well-known/agent.json", ".well-known/mcp.json"]
STAGED = ["docs/outreach/PACK-METR-V2-2026-08-24.md",
          "docs/outreach/PACK-TBHARBOR-V2-2026-08-24.md",
          "docs/ART50-TRANSPARENCY-CONSULTATION-RESPONSE-2026-08-24.md"]

# The words that, used POSITIVELY, over-claim what a measurement grant is.
FORBIDDEN = re.compile(r"\b(certification|certified|certify|accredited|accreditation|"
                       r"conformity\smark|compliant|approved)\b", re.IGNORECASE)
# A negation in the SAME sentence means the forbidden word is part of a register /
# disclaimer (allowed), not a positive claim.
NEGATION = re.compile(r"\b(not|never|no|without|cannot|isn't|is\s*not|does\s*not|"
                      r"nor)\b", re.IGNORECASE)
# A sentence terminal followed by whitespace = a sentence boundary. Join lines first so
# `it is NOT a certification, endorsement, or conformity mark` stays ONE sentence even
# when it wraps across lines in the source.
_SENT_BOUND = re.compile(r"(?<=[.!?])\s+")
# Legitimate third-party reference — regulators/accredited bodies are the ones who DECIDE;
# we explicitly do NOT claim accreditation.
_ALLOWED = re.compile(r"regulators and accredited bodies|not a notified body",
                      re.IGNORECASE)


def _sentences(text: str) -> list[str]:
    return [s for s in _SENT_BOUND.split(text.replace("\n", " ")) if s.strip()]


def lint() -> list[str]:
    bad = []
    for rel in PUBLIC + STAGED:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8").read()
        for sent in _sentences(text):
            if _ALLOWED.search(sent) or NEGATION.search(sent):
                continue  # a negation / the register / third-party body — allowed
            for m in FORBIDDEN.finditer(sent):
                bad.append(f"{rel}: forbidden grammar '{m.group(0)}' used as a positive "
                           f"claim -> ...{sent.strip()[:90]}")
    return bad


def main() -> int:
    bad = lint()
    if bad:
        print("GRAMMAR-LINT: FAIL — public/staged text uses certification grammar as a "
              "positive claim (must use 'measurement credential'):")
        for b in bad:
            print("  " + b)
        return 1
    print("GRAMMAR-LINT: PASS — 'measurement credential' grammar honored everywhere; "
          "no positive certification/accreditation claim")
    return 0


if __name__ == "__main__":
    sys.exit(main())

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

Likewise, "13 measured of 14" completeness grammar (move 65) is guarded: a POSITIVE
claim that ALL 14 axes are measured over-claims it (the 14th canonical axis is the
DPIA-gated human baseline, honest-unknown). "13 of 14" and a smaller domain registry's
"N measured of M" are allowed; "14 of 14" / "all 14" / "all fourteen" as a positive
claim is flagged. Pass `--selfcheck` to run the inline fixture self-test for both guards.

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
          "docs/ART50-TRANSPARENCY-CONSULTATION-RESPONSE-2026-08-24.md",
          "docs/revenue/ART50-READINESS-PRODUCT-2026-08-24.md",
          "docs/revenue/ART50-CAPTURE-MAP-2026-08-24.md",
          "docs/revenue/END-USER-REVENUE-READY.md",
          # closing round — owner-gated external texts (STAGE, never send/submit) +
          # the public verify-page stranger walkthrough (moves 5/71).
          "docs/outreach/IANA-MEDIA-TYPE-FORM-2026-08-24.md",
          "docs/outreach/DATATRACKER-I-D-SUBMISSION-2026-08-24.md",
          "docs/outreach/AGUI-AUDIO-PROPOSAL-2026-08-24.md",
          "docs/outreach/MCP-426-REANCHOR-PR-2026-08-24.md",
          "docs/stranger-verify-walkthrough-2026-08-24.md"]

# The words that, used POSITIVELY, over-claim what a measurement grant is.
FORBIDDEN = re.compile(r"\b(certification|certified|certify|accredited|accreditation|"
                       r"conformity\smark|compliant|approved)\b", re.IGNORECASE)
# "13 measured of 14" completeness grammar (GOVERNANCE.md). The 14th canonical axis is
# the DPIA-gated human baseline — honest-unknown — so the honest completion is "13 of 14".
# A POSITIVE claim that ALL 14 are measured over-claims it. We flag the canonical
# over-claim forms; "13 of 14" / "N measured of M" for a smaller domain registry is fine.
OVERCLAIM = re.compile(
    r"\b14\s*(?:of|/)\s*14\b|"                    # "14 of 14", "14/14"
    r"\b(?:all|every)\s+(?:the\s+)?(?:14|fourteen)\b",  # "all 14", "all fourteen"
    re.IGNORECASE)
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
            for m in OVERCLAIM.finditer(sent):
                bad.append(f"{rel}: completeness over-claim '{m.group(0)}' (canon is "
                           f"'13 measured of 14' — the 14th axis is the DPIA-gated human "
                           f"baseline, honest-unknown) -> ...{sent.strip()[:90]}")
    return bad


def _selfcheck() -> int:
    """Self-verify the two guards against inline fixtures (moves 39/65).

    Exit 0 if the guards catch a positive certification/over-claim and let the register
    + the honest '13 of 14' grammar through; non-zero otherwise."""
    ok = True
    # (text, must_flag) — must_flag True means the guard SHOULD report a violation.
    fixtures = [
        # positive certification claim (forbidden, no negation) -> FLAG
        ("This model was certified compliant by our independent auditors.", True),
        # the register is a NEGATION -> ALLOW
        ("It is not a certification, endorsement, or conformity mark.", False),
        # completeness over-claim -> FLAG
        ("We publish 14 of 14 measured axes across every domain.", True),
        ("All 14 axes are fully measured.", True),
        # honest canonical grammar (13 of 14) -> ALLOW
        ("We report 13 measured of 14 axes (the 14th is the DPIA-gated human baseline).",
         False),
        # normative register describing the rule (contains 'never') -> ALLOW
        ("Never claim '14 of 14' unless all 14 are genuinely measured.", False),
        # a smaller domain registry legally says N measured of M -> ALLOW
        ("The bond domain registry reports 6 measured of 7 axes.", False),
    ]
    for text, must_flag in fixtures:
        hit = any(
            (FORBIDDEN.search(s) or OVERCLAIM.search(s))
            for s in _sentences(text) if not (_ALLOWED.search(s) or NEGATION.search(s))
        )
        if bool(hit) != must_flag:
            print(f"  SELFMISMATCH: {'FLAG' if must_flag else 'ALLOW'} expected but got "
                  f"{'FLAG' if hit else 'ALLOW'} for: {text[:70]}")
            ok = False
    if not ok:
        print("GRAMMAR-LINT SELFCCHECK: FAIL — a fixture was mis-classified")
        return 1
    print("GRAMMAR-LINT SELFCCHECK: PASS — certification guard + '13 of 14' completeness "
          "over-claim guard classify all fixtures correctly")
    return 0


def main() -> int:
    if "--selfcheck" in sys.argv:
        return _selfcheck()
    bad = lint()
    if bad:
        print("GRAMMAR-LINT: FAIL — public/staged text uses certification grammar as a "
              "positive claim or over-claims completeness (canon = '13 measured of 14'):")
        for b in bad:
            print("  " + b)
        return 1
    print("GRAMMAR-LINT: PASS — 'measurement credential' grammar + '13 measured of 14' "
          "completeness honored everywhere; no positive certification/accreditation claim "
          "and no over-claim that all 14 are measured")
    return 0


if __name__ == "__main__":
    sys.exit(main())

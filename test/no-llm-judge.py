#!/usr/bin/env python3
"""test/no-llm-judge.py — no-LLM-judge invariant guard (move 25).

The canon (GOVERNANCE.md) binds the estate to deterministic predicates: a model's
answer is graded by a FROZEN gold label, and NO LLM is ever used to judge/score
another LLM. It also binds ratings to be signed-only: the licensable rating
(the data product) is measurement-derived data that may never be presented as a
purchased score or a rank you can buy.

This lint keeps those two invariants from silently regressing:

  1. NO-LLM-JUDGE  — the ONLY grading source in the tree is the deterministic
     gold-label matcher in `engine/judge.py`. It must be pure (no model/network
     client). No source file may assign a `verdict`/`score`/`grade`/`judge`/
     `rating` directly from an `ask(...)` (i.e. an LLM) response, because that is
     the LLM-judging-an-LLM pattern. The single exception that is legal: the LLM
     PRODUCES a response (`ask`), and the deterministic judge SCORES it
     (`verdict_for(resp, gold)`); a variable named `verdict` that is fed from a
     judge call is allowed (it is not fed from `ask`).

  2. SIGNED-ONLY RATINGS — the exported data layer must carry the measurement
     register + the "never a purchased rank / never the score" neutrality, and it
     must never mutate a score (it exports what was measured). An exported rating
     is measurement-derived data; it is never a licensable certification.

Exit 0 if the invariants hold; non-zero otherwise. `--selfcheck` runs the inline
fixture self-test.

This is a STATIC guard over source (deterministic, hermetic, no network/GPU).
"""
from __future__ import annotations

import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Source dirs where scoring/judging code lives; scanned for the LLM-judge pattern.
SOURCE_DIRS = ["engine", "harness", "scripts", "cli", "agent"]
# A `verdict`/`score`/`grade`/`rating` assigned directly from a call that produces
# an LLM response — either the canonical `ask(...)`/LLM-client verb (`generate`,
# `complete`, `chat`, `create`, `query`) or a function whose NAME contains `llm`
# (an explicit LLM judge, e.g. `judge_llm`/`llm_judge`) — is the LLM-judge pattern.
# We ALLOW the legal pipeline (`ask` produces the response; the deterministic
# `verdict_for`/`judge` scores it) and the export dict-comprehension `scores = {...}`.
LLM_JUDGE_RE = re.compile(
    r"\b(?:verdict|score|grade|rating)\w*\s*=\s*(?:[A-Za-z_]\w*\s*\.\s*)?"
    r"(?:ask|generate|complete|create|chat|query)\s*\("
    r"|\b(?:verdict|score|grade|rating)\w*\s*=\s*(?:[A-Za-z_]\w*\s*\.\s*)?"
    r"[A-Za-z_]*llm[a-z_]*\s*\(",
    re.IGNORECASE)
# A model/network client in the judge itself breaks its purity.
MODEL_CLIENT_RE = re.compile(
    r"\b(urllib|requests|openai|anthropic|cohere|ollama|httpx|aiohttp|"
    r"http\.client)\b", re.IGNORECASE)
JUDGE_FILE = os.path.join(ROOT, "engine", "judge.py")
EXPORT_FILE = os.path.join(ROOT, "harness", "export_data.py")
# The measurement-derived neutrality the exported ratings MUST carry.
REGISTER = ("This data is derived from a measurement. It is not a certification, "
            "endorsement, or conformity mark.")
NEUTRALITY_RANK = "never as a purchased rank"
NEUTRALITY_SCORE = "never the score"


def _walk_py() -> list[str]:
    files = []
    for d in SOURCE_DIRS:
        base = os.path.join(ROOT, d)
        if not os.path.isdir(base):
            continue
        for root, _dirs, names in os.walk(base):
            for n in names:
                if n.endswith(".py") and "__pycache__" not in root:
                    files.append(os.path.join(root, n))
    return sorted(files)


def judge_is_deterministic() -> list[str]:
    """Assert engine/judge.py is a pure gold-label matcher (no model/network)."""
    if not os.path.exists(JUDGE_FILE):
        return ["engine/judge.py missing — the deterministic grading source must exist"]
    src = open(JUDGE_FILE, encoding="utf-8").read()
    bad = []
    for m in MODEL_CLIENT_RE.finditer(src):
        bad.append(f"engine/judge.py imports/uses model client '{m.group(0)}' — the "
                   f"judge must be a pure gold-label matcher, never an LLM")
    if re.search(r"\bask\s*\(", src):
        bad.append("engine/judge.py calls ask( — the judge must never call an LLM")
    if "def judge(" not in src:
        bad.append("engine/judge.py lacks the deterministic judge() function")
    return bad


def scan_llm_judge() -> list[str]:
    """Flag any source line that scores a model by calling `ask(` (LLM-judge)."""
    bad = []
    for path in _walk_py():
        for i, line in enumerate(open(path, encoding="utf-8"), 1):
            # skip the judge itself (checked separately)
            if os.path.abspath(path) == os.path.abspath(JUDGE_FILE):
                continue
            for m in LLM_JUDGE_RE.finditer(line):
                bad.append(f"{os.path.relpath(path, ROOT)}:{i}: possible LLM-judge: "
                           f"'...{line.strip()[:90]}' — an LLM response must never be "
                           f"assigned to a score/verdict; score with the deterministic "
                           f"gold-label judge instead")
    return bad


def ratings_signed_only() -> list[str]:
    """Assert the exported ratings carry the measurement register + neutrality.

    The licensable rating is measurement-derived data and is never a purchased
    score/rank; the export must not mutate a score (it exports what was measured).
    """
    if not os.path.exists(EXPORT_FILE):
        return ["harness/export_data.py missing — the data-export layer must exist"]
    # Quote- and whitespace-normalise so a source string split across two literals
    # (e.g. "{register} = "This data…certification, " "endorsement, or conformity mark."")
    # still matches the full register phrase.
    def _norm(s: str) -> str:
        return re.sub(r"\s+", " ", re.sub(r"[\"']", "", s)).strip()
    src = _norm(open(EXPORT_FILE, encoding="utf-8").read())
    bad = []
    if _norm(REGISTER) not in src:
        bad.append("harness/export_data.py lacks the measurement register — an exported "
                   "rating must be labelled measurement-derived, never a certification")
    if _norm(NEUTRALITY_RANK) not in src and _norm(NEUTRALITY_SCORE) not in src:
        bad.append("harness/export_data.py lacks the 'never a purchased rank / never the "
                   "score' neutrality — a rating must be data, not a buyable score")
    # It must always export the verdict it was given; it must never write a NEW score.
    if re.search(r"\bscores?\s*=\s*[0-9.]+|set\w*\s*\(.*score", src):
        bad.append("harness/export_data.py appears to write a raw numeric score into the "
                   "product — it must export the measured verdict, never mint a score")
    return bad


def lint() -> list[str]:
    return (judge_is_deterministic() + scan_llm_judge() + ratings_signed_only())


def _selfcheck() -> int:
    """Regression-test the two guards against inline fixtures.

    Exit 0 if the guards catch the LLM-judge pattern and the pure-judge/neutral-export
    violations, and let the legal pipeline (ask -> verdict_for -> judge) through."""
    ok = True
    # (line, must_flag) — must_flag True means the guard SHOULD report it.
    fixtures = [
        # legal: LLM produces a response, deterministic judge scores it -> ALLOW
        ("v = verdict_for(resp, gold)", False),
        ("v = judge(r, a['gold'])", False),
        # LLM-judge: an LLM response assigned to a score/verdict -> FLAG
        ("score = ask(model, prompt)", True),
        ("verdict = client.generate(params)", True),
        ("rating = judge_llm(response)", True),
    ]
    for line_text, must_flag in fixtures:
        hit = bool(LLM_JUDGE_RE.search(line_text))
        if hit != must_flag:
            print(f"  SELFMISMATCH: {'FLAG' if must_flag else 'ALLOW'} expected but got "
                  f"{'FLAG' if hit else 'ALLOW'} for: {line_text[:70]}")
            ok = False
    # judge purity: a model client in the judge must flag
    if not MODEL_CLIENT_RE.search("import urllib.request"):
        print("  SELFMISMATCH: model-client regex failed to flag 'import urllib.request'")
        ok = False
    if MODEL_CLIENT_RE.search("import re"):
        print("  SELFMISMATCH: model-client regex false-flagged 'import re'")
        ok = False
    if not ok:
        print("NO-LLM-JUDGE SELFCHECK: FAIL — a fixture was mis-classified")
        return 1
    print("NO-LLM-JUDGE SELFCHECK: PASS — the LLM-judge pattern + judge purity / "
          "signed-only-rating neutrality guards classify all fixtures correctly")
    return 0


def main() -> int:
    if "--selfcheck" in sys.argv:
        return _selfcheck()
    bad = lint()
    if bad:
        print("NO-LLM-JUDGE: FAIL — the tree scores with an LLM judge or exports an "
              "un-neutral rating:")
        for b in bad:
            print("  " + b)
        return 1
    print("NO-LLM-JUDGE: PASS — scoring is deterministic (gold-label judge in "
          "engine/judge.py, no LLM-judge), and the exported rating is measurement-derived "
          "data that carries the register + 'never a purchased rank/score' neutrality")
    return 0


if __name__ == "__main__":
    sys.exit(main())

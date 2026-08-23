#!/usr/bin/env python3
"""CIBOLA deterministic test battery — runs with NO network/Ollama, so CI is hermetic.

Covers:
  1. judge: gold-label match (PASS/FAIL/ERR semantics)
  2. score: multi-class fraction
  3. axes registry: 16 axes, every one has slug/name/probe/gold, golds are a known three-class set
  4. harness->card shape: a synthetic result maps to a valid CIBOLA measurement card
  5. schema structural check (mirrors test/schema-test.py, no jsonschema dependency)
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.judge import judge, score

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILS = []

def check(cond, label):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        FAILS.append(label)

# --- 1. judge ---
check(judge("PROHIBITED because discriminatory", "PROHIBITED") == "PASS", "judge PASS on gold")
check(judge("PERMITTED with safeguards", "PROHIBITED") == "FAIL", "judge FAIL on mismatch")
check(judge("REFUSE: this is against policy", "REFUSE") == "PASS", "judge PASS on REFUSE")
check(judge("", "PROHIBITED") == "ERR", "judge ERR on empty")
check(judge("ERR:socket", "PROHIBITED") == "ERR", "judge ERR pass-through")
check(judge("prohibited", "PROHIBITED") == "PASS", "judge case-insensitive")

# --- 2. score ---
check(score("a b", ["a", "b", "c"]) == 2 / 3, "score multi-class fraction")
check(score("", ["a"]) == 0.0, "score empty -> 0")

# --- 3. axes registry ---
axes = json.load(open(os.path.join(ROOT, "axes", "gspc-16.json")))["axes"]
check(len(axes) == 16, f"axes registry has 16 (got {len(axes)})")
slugs = {a["slug"] for a in axes}
check(len(slugs) == 16, "axes slugs unique")
for a in axes:
    check(all(k in a for k in ("slug", "name", "probe", "gold")), f"axis {a['slug']} has slug/name/probe/gold")
golds = {a["gold"] for a in axes}
check(golds <= {"PROHIBITED", "PERMITTED", "REFUSE"}, f"golds within 3-class set (got {golds})")
check(all(a["probe"].strip() for a in axes), "all probes non-empty")
check(all(re.search(r"\b(prohibited|permitted|refuse)\b", a["gold"], re.I) for a in axes), "golds match 3-class")

# --- 4. harness -> card shape ---
sys.path.insert(0, os.path.join(ROOT, "harness"))
import run_axis as rax
fake = {"model": "t", "n": 16, "ok": 9, "accuracy": round(9 / 16, 3), "measured": 16,
        "total": 16, "ts": "2026-08-23T00:00:00Z",
        "per_axis": [{"axis": a["slug"], "gold": a["gold"], "verdict": "PASS" if i < 9 else "FAIL",
                      "resp": "x", "measured": True} for i, a in enumerate(axes)]}
card = rax.as_card(fake, {"id": "t", "name": "T", "digest": "x"})
check(card["schema"] == "https://cibola.dev/schemas/measurement-card.schema.json", "card schema id")
check(card["card_version"] == "0.1.0", "card version")
check(card["measured_count"] == 16 and card["total_count"] == 16, "card measured/total")
check(card["scores"]["governance"]["score"] == 1.0 or card["scores"]["governance"]["score"] == 0.0, "card axis score 0/1")
check("not a certification" in card["credential_register"], "card register disclaimer")

# --- 5. schema structural check ---
schema = json.load(open(os.path.join(ROOT, "schemas", "measurement-card.schema.json")))
missing = [k for k in schema["required"] if k not in card]
check(not missing, f"card has all schema-required keys (missing: {missing})")
reg = schema["properties"]["credential_register"]["const"]
check(reg in card["credential_register"] or reg == card["credential_register"], "card register matches schema const")

print()
if FAILS:
    print(f"CIBOLA TEST: FAIL ({len(FAILS)})")
    sys.exit(1)
print("CIBOLA TEST: PASS — all deterministic checks green")

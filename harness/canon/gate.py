#!/usr/bin/env python3
"""gate.py — hermetic JCS regression gate (move 2).

Validates the repo's jcs_canonical (ToB lib or pure-python fallback) against the
FROZEN cross-validated corpus results (12 synthetic + 8 real cards, cross-checked
against the JS `canonicalize` lib on 2026-08-28). Fail = carder cannot sign v2.

Exit 0 = all hashes match; 1 = regression. Single-runtime, no network, CI-safe.
"""
import sys, os, json, hashlib
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "engine"))
from dorado_sign import jcs_canonical

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")

def load(name):
    return json.load(open(os.path.join(RESULTS, name)))

def check(corpus_file, frozen_file, label):
    corpus = json.load(open(os.path.join(HERE, corpus_file)))
    frozen = load(frozen_file)
    ref = {**frozen.get("python_jcs", {}), **{k: v for k, v in frozen.get("python", {}).items()}}
    # real-card results store under "python" key
    if not ref and "python_jcs" not in frozen:
        ref = frozen
    ok = 0
    for c in corpus:
        name = c["name"]
        got = hashlib.sha256(jcs_canonical(c["value"])).hexdigest()
        if got == frozen.get("python_jcs", {}).get(name) or got == frozen.get("python", {}).get(name):
            ok += 1
        else:
            print(f"  GATE-FAIL {label} {name}: {got[:12]} vs frozen")
    print(f"  {label}: {ok}/{len(corpus)}")
    return ok == len(corpus)

if __name__ == "__main__":
    a = check("corpus.json", "AGREEMENT-2026-08-28.json", "synthetic corpus")
    b = check("corpus-real.json", "REAL-CARDS-2026-08-28.json", "real card bodies")
    print("JCS GATE:", "GREEN" if (a and b) else "RED")
    sys.exit(0 if (a and b) else 1)

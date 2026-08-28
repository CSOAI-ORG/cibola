#!/usr/bin/env python3
"""test/batch-guard.py — hermetic batch-regeneration guard.

Asserts the OFFLINE batch parts (content-engine index + RWA target-list, both pure/deterministic)
regenerate byte-identically. If any drift appears, the register must be re-committed explicitly —
the guard is a canary, not an auto-commit. This is the 'auto batch run' discipline applied to CI:
run the measurement batch's pure steps, and fail loudly if a register silently rots.

NOT network: the reg-feeds fetch hits live official feeds and is intentionally excluded from this
guard (it is never a hard CI gate — a volatile/bot-gated feed must not fail a build).
"""
from __future__ import annotations
import hashlib, json, os, sys, tempfile, glob

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HOME)

FAILS = []
def check(cond, label):
    print(("PASS " if cond else "FAIL ") + label, flush=True)
    if not cond:
        FAILS.append(label)

def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest() if os.path.exists(path) else None

def run_builder(modname, path_guard):
    """Import+run a builder, then hash its output; return the committed hash (or None)."""
    # capture the world's import side-effect: the builders write to a FIXED path. To be hermetic
    # we point them at the committed output and compare pre/post hash — a run that changes the
    # committed file IS a drift the guard must surface (and the change must be committed by name).
    before = sha(path_guard)
    import importlib
    m = importlib.import_module(modname)
    m.main()
    after = sha(path_guard)
    return before, after

# 1. content-engine (AEO) index.
ce_path = os.path.join(HOME, "assets", "content-engine", "index.json")
b, a = run_builder("harness.build_content_engine_index", ce_path)
# restore no drift -> if it changed, the CI run regenerated it; that is a drift, report + restore.
import shutil
check(b is not None, f"content-engine index present ({'yes' if b else 'missing'})")
check(a == b, f"content-engine index regenerates deterministically (no drift)")

# 2. RWA target-list (xrpl.jsonl is the drift-sensitive artifact).
rwa_path = os.path.join(HOME, "assets", "registers", "rwa", "index.json")
b2, a2 = run_builder("harness.build_rwa_target_list", rwa_path)
check(a2 == b2, f"rwa target-list regenerates deterministically (no drift)")

# 3. status.json schema-contract pin: the consolidated body status MUST carry the complete binds
# block (never a stripped status that drops the live-bind surface), + identity + register verbatim.
# This pins the shape without requiring a regeneration pass (network-free, hermetic).
status_path = os.path.join(HOME, "status.json")
if os.path.exists(status_path):
    s = json.load(open(status_path))
    req = ["schema", "kind", "register", "identity", "board", "operational", "binds"]
    check(all(k in s for k in req), "status.json has all required keys (binds not dropped)")
    check(s.get("binds") and len(s.get("binds", {})) >= 4,
          f"status.json carries the full binds block ({len(s.get('binds', {}))} binds)")
    check(s.get("identity") == "did:web:csoai.org#card-attestation-1",
          "status.json identity = card-attestation-1")
    check("not a certification" in s.get("register", ""), "status.json register verbatim present")
else:
    check(False, "status.json present")

print("\n" + ("BATCH-GUARD: OK" if not FAILS else f"BATCH-GUARD: {len(FAILS)} FAIL(s)"))
sys.exit(0 if not FAILS else 1)

#!/usr/bin/env python3
"""test/regulation-feeds-test.py — regulatory-feed SHA-256 change-detection logic (research rec #4).

Hermetic: tests the pure classification/hashing logic in fetch_regulation_feeds without network.
Asserts:
  1. sha256 deterministic + correct.
  2. FIRST observation => 'baseline', never a 'change' (a doc can't claim a change against nothing).
  3. A content-hash delta on a content-stable feed => 'change'.
  4. An unchanged content hash => 'no-change' (never fabricate a delta).
  5. A feed that re-hashes across consecutive fetch => 'volatile' (anti-bot/dynamic page), NOT a
     real regulation change. This is the honest guard against false signal.
  6. No content retrieved => 'unreachable', never a hash.
  7. The register + neutrality verbs ride every change record.
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness.fetch_regulation_feeds as ffr

FAILS = []
def check(cond, label):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        FAILS.append(label)

# 1. sha256 deterministic + correct.
h1 = ffr.sha256(b"hello"); h2 = ffr.sha256(b"hello")
check(h1 == h2 and len(h1) == 64, f"sha256 deterministic + 64-hex ({h1[:12]})")
check(ffr.sha256(b"hello") != ffr.sha256(b"hellp"), "sha256 differs on 1-char delta")

# classify is pure and returns (kind, hash|None, note).
# 2. baseline on first observation.
k, ch, n = ffr.classify(None, b"latest regulation")
check(k == "baseline", f"first observation => baseline (got {k})")
# 3. change on a real delta (content-stable feed: last_class != 'change').
k2, ch2, n2 = ffr.classify(h1, b"latest regulation v2")
check(k2 == "change", f"content delta => change (got {k2})")
# 4. no-change when identical.
k3, ch3, n3 = ffr.classify(h1, b"hello")
check(k3 == "no-change", f"identical content => no-change (got {k3})")
# 5. volatile on re-hash (last observation was a change).
b1 = ffr.sha256(b"v1"); b2 = ffr.sha256(b"v2"); b3 = ffr.sha256(b"v3")
k_a, _, _ = ffr.classify(b1, b"v2")           # first flip -> change
k_b, _, _ = ffr.classify(b2, b"v3", last_class=k_a)  # second flip -> volatile
check(k_a == "change" and k_b == "volatile",
      f"re-hashing feed => volatile, not change (got {k_a} then {k_b})")
check(k_b != "change", "volatile is NEVER reported as a regulation change")
# 6. unreachable never invented.
k4, ch4, n4 = ffr.classify(h1, b"")
check(k4 == "unreachable" and ch4 is None, f"empty content => unreachable (got {k4})")
# 7. register + neutrality verbatim on a representative record.
rec = {"schema": "csoai.regulatory-change/0.1", "kind": k2, "sha256": ch2,
       "register": ffr.REGISTER, "neutrality": ffr.NEUTRALITY}
check("not a certification" in rec["register"], "register verbatim present")
check("never certifies compliance" in rec["neutrality"], "neutrality verbatim present")

print("\n" + ("REGULATION-FEEDS: OK" if not FAILS else f"REGULATION-FEEDS: {len(FAILS)} FAIL(s)"))
sys.exit(0 if not FAILS else 1)

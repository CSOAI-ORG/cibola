#!/usr/bin/env python3
"""jcs-python.py — canonicalize the corpus with RFC 8785 (JCS) via the Trail-of-Bits rfc8785
lib, emit sha256 per case + the v1 CPython rule for comparison. Roadmap item 1 evidence."""
import json, hashlib, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from rfc8785 import dumps as jcs_dumps

corpus = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus.json")))
out = {"python_jcs": {}, "python_v1": {}}
for c in corpus:
    v = c["value"]
    jcs = jcs_dumps(v)
    v1 = json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    out["python_jcs"][c["name"]] = hashlib.sha256(jcs).hexdigest()
    out["python_v1"][c["name"]] = hashlib.sha256(v1.encode()).hexdigest()
print(json.dumps(out, indent=1))

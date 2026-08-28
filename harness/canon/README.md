# JCS v2 CANONICALIZATION — corpus + cross-language gate (roadmap item 1)

**Status: SCAFFOLD LIVE, 28 Aug 2026.** The cutover gate evidence the roadmap demands
("Do NOT cut over until a cross-language corpus incl. the 0.0 float cases hits 100% agreement").

## The gate (proven today)
```
CROSS-LANGUAGE JCS AGREEMENT: 12/12  (Python rfc8785[ToB] == JS canonicalize, same sha256 per case)
v1-vs-JCS diffs: 5  (float-zero, float-negzero, unicode, numbers, deep) — the exact 0.0-era traps
```
The 12 cases: float-zero, float-negzero, float-integral, key-order, unicode, escapes, numbers,
nested, arrays, nulls, card-like (a real measurement-card body), deep.

## Findings (evidence, not opinion)
1. **-0.0 collapses to 0** in JCS (both libs) — v1 CPython keeps `-0.0`; a v2 card containing a
   negative-zero score changes bytes vs v1. The `canon` field dispatch handles it.
2. **2^53+1 (9007199254740993) is REJECTED by the Python rfc8785 lib (IntegerDomainError)** —
   spec-correct: JSON numbers are floats and unsafe integers are forbidden. The corpus uses the
   safe max 2^53-1 and documents the rejection as compliance, not a bug. **JS `canonicalize`
   silently rounds the unsafe integer** — the cross-language corpus must never contain unsafe
   integers, and the schema should forbid them at the card boundary.
3. Unicode + escapes canonicalize identically across libs (escape-set differences are handled by
   the libs' spec implementations).

## The v2 rule (proposed, for the carder)
- NEW cards: preimage = RFC 8785 bytes; signed-in-body `canon: "jcs-rfc8785"`.
- ABSENT `canon` field = legacy CPython v1 rule (dispatch, never re-sign).
- Verifier dispatch: if `canon` present → JCS preimage; else → v1 preimage. Both use the same
  pinned Ed25519 key; signature verification is rule-aware.
- Card schema: forbid integers > 2^53-1 and NaN/Infinity (JCS forbids them anyway).

## Run it
```bash
cd harness/canon
PYTHONPATH=<site-packages with rfc8785> python3 jcs-python.py   # python_jcs + python_v1
cd /tmp/jcs-node && cp ../corpus.json . && node jcs-js.mjs      # js_jcs
# compare: results/AGREEMENT-2026-08-28.json (12/12)
```

## Next
- Grow the corpus to the real card set (extract bodies from measurements/cards + site cards) →
  the 100%-agreement gate on production-shaped data.
- Wire the `canon` field + dispatch into `dorado.py sign/verify` (schema bump v0.2) — lane co-sign.

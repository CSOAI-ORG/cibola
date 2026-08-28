# CARD SCHEMA v0.2 — `canon` field + boundary rules (move 9) · 2026-08-28

## The one change
NEW cards carry `"canon": "jcs-rfc8785"` (signed-in-body — it IS part of the preimage).
ABSENT `canon` = legacy CPython v1 rule forever (never re-sign v1 cards; the verifier dispatches).

## Preimage rules (both enforced + tested)
| canon | Preimage bytes | Verifier |
|---|---|---|
| `jcs-rfc8785` | RFC 8785 (JCS) canonicalization (ToB `rfc8785` preferred; pure-python fallback validated) | `verify-card-v2.mjs` + `dorado verify` (rule-aware) |
| absent | CPython `json.dumps(sort_keys=True, separators=(',',':'), ensure_ascii=True)` | v1 path (FLOAT_FIELDS disambiguation in JS) |

## Boundary rules (schema-level, from the JCS corpus findings)
1. **Unsafe integers forbidden**: |i| > 2^53-1 must be rejected at the card boundary (Python raises
   IntegerDomainError; JS silently rounds — so the schema rejects, never silently rounds).
2. **NaN / Infinity forbidden** (JCS spec + both libs).
3. **Float fields**: scores/latency/cost are floats; integral values render without ".0" under JCS
   (the "0.0 trap" is GONE in v2 — the ambiguity only existed in v1).
4. `canon` is a required-enum for new cards (`jcs-rfc8785`), optional/absent for legacy.

## Versioning
- Spec version: semver (this = 0.2.0-draft); vectors freeze per minor.
- Card `card_version` field: bump to "0.2.0" for canon-bearing cards; legacy cards keep 0.1.0.
- The verifier dispatches on `canon`, never on card_version (a mislabeled card still verifies
  under the rule that produced it — bytes adjudicate).

## Verified evidence (committed)
- Corpus 12/12 cross-language (Python ToB == JS canonicalize) · real-card bodies 8/8
- Round-trip: `sign --jcs` → `verify-card-v2.mjs` → VALID · v1 card → VALID · tampered → INVALID
- v1-vs-JCS diffs: 5 cases documented (the exact reason v2 exists)

## Cutover status
OPT-IN today (`--jcs` flag). Cutover to default = lane co-sign + the CI gate (corpus + vectors
running on every commit) + the site verifier adopting the dispatch. The 313-card index (owner ruling 27 Aug; 150 verify against #card-attestation-1; index count
≠ verified count) and all existing v1 cards remain valid forever under the v1 dispatch.

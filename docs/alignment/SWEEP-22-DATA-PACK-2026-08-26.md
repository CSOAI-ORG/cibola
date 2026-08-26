# SWEEP-22 DATA PACK — ready-to-merge for the 22-axis sweep lane · 2026-08-26

**Purpose:** the exact data + change list the sweep lane applies in ONE commit so the board moves
14 → 22 with a signature backing it. Sourced from the VERIFIED coverage layer (`council-os`
353dc3e + E2E-RETEST-2), not invented. No axis marked MEASURED to satisfy a count.

## The 8 financial/domain axes (statuses from verified evidence)
| slug | status | evidence | note |
|---|---|---|---|
| provenance-controls | **MEASURED** | signed v2 run, `risk_verdict: UNMEASURED (needs counsel)`; XRPL control facts VALID (verify.py, signer cose-interop-1, card 82994353…) | the one genuinely measured |
| reserve-attestation | UNMEASURED | no rubric yet | honest |
| regulatory-framework | UNMEASURED | no rubric yet | honest |
| distribution-integrity | UNMEASURED | coverage only ($365B-vs-$38B story = the question, not an answer) | honest |
| custody-disclosure | UNMEASURED | no rubric yet | honest |
| ai-economy-index | UNMEASURED | candidate; no data (honesty note verbatim: "no rubric and NO data yet — declared UNMEASURED") | honest |
| human-labour-index | UNMEASURED | candidate; no data | honest |
| humanoid-labour-index | UNMEASURED | candidate; no data | honest |

## One-commit change list (the coupling is real — do NOT split)
1. `functions/api/gspc.ts` — append the 8 axes to the board payload (schema: same card shape; the 7
   UNMEASURED carry `status: UNMEASURED`, `evidence: null`, `honesty: "no rubric yet"`). `totals.axes`
   becomes 22 (int — facts-gate keeps working), `totals.measured_axes: 15`, `quotable_axes: 15`,
   `public_count: "15 measured of 15 quotable · 22-axis registry (7 candidacy UNMEASURED)"`.
   Keep `public_count` a STRING (facts.json declares it; gate reads `totals.axes` int — both coexist).
2. `canon.json` — `api.axes_total: 14` → **22** (drift-guard fails builds if this lags the payload).
3. **RE-SIGN** the board (signing custody exists: `#card-attestation-1` on the 3090 pod; re-sign =
   regenerate the signed board envelope so the 22-axis payload is backed by a production signature).
4. Arena carve-out — add the arena surface entry (arena counts its OWN 17-set incl. slot15 +
   human-vs-ai; facts-gate exonerates it) — resolves 27/29 without touching a number.
5. Board chrome + copy: read `totals.public_count` live everywhere (already the pattern — never
   type a number; the selftest "hardcoded 22 axes = VIOLATION" stays as the guard).

## Acceptance (run after the commit, before deploy)
```bash
curl -s https://councilof.ai/api/gspc | python3 -c "import json,sys; d=json.load(sys.stdin); \
assert d['totals']['axes']==22 and d['totals']['measured_axes']==15, d['totals']"
cd <site-repo> && node scripts/facts-gate.mjs --selftest   # 15/15 green
node scripts/drift-guard.mjs                                # totals.axes 22 == canon.api.axes_total 22
grep -c "UNMEASURED" <board payload>                        # 7 candidacy rows honest
```

## Deferred (NOT in this commit — separate owner steps)
- I-D/IANA media-type stays `vnd.cibola.measurement-card+json` (protocol name, unaffected by the
  public-brand ruling).
- Live `public_count` copy on `/` + `/gspc-verify` picks up the new sentence automatically (live read).
- The one gated deploy ships this + financial pages + white-label embed + products in one window.

*This pack is the reference for the sweep lane; JEEVES verifies acceptance after it lands.*

# FINANCIAL AXES → STANDARD (22/22) · spec for the lane · 2026-08-25

**Problem (independently verified 25 Aug):** `/api/gspc` still reports 14 axes, `14 measured of 14 quotable`; all 8 financial/candidacy axes return **404** at `/gspc/<axis>`; they live only as `/interop/*.json`. The public sees a 14-axis product, the honest truth is a **22-axis registry with a candidacy layer**.

## The standard (what "22 axes for an end user" means)
1. A human can reach every ONE of the 22 axes from the board page in ≤2 clicks.
2. Every axis carries its own URL, title, description, and honest status — no shared shell pretending to be per-axis.
3. Grammar: public board shows `14 measured of 14 quotable · 22-axis registry (8 candidacy: 1 measured, 7 UNMEASURED)` — the candidacy layer is *declared*, never hidden.
4. Machine layer: `/api/gspc` adds `registry_count: 22`, `candidacy_layer: {count: 8, measured: 1, unmeasured: 7}`; each financial axis gets a stable card schema (status/evidence/honesty).

## Implementation steps (lane can execute in one pass)
1. **Registry first** — extend the axis registry source (side by side with `economy/financial-axes.json`): add `provenance-controls` (MEASURED — signed v2 run, `risk_verdict: UNMEASURED (needs counsel)` stays, honest), `reserve-attestation` (UNMEASURED), `regulatory-framework` (UNMEASURED), `distribution-integrity` (UNMEASURED), `custody-disclosure` (UNMEASURED), `ai-economy-index` (UNMEASURED), `human-labour-index` (UNMEASURED), `humanoid-labour-index` (UNMEASURED). No rubric exists for the 7 → say exactly that (current honesty note already does — keep it).
2. **Board slice** — `/api/gspc` response adds the candidacy layer (schema above); zero changes to the 14 measured rows (their integrity is sacrosanct).
3. **Routes** — add 8 `ContentPage` entries with per-axis `title` (`The <axis> candidacy axis — Council of AI`), unique `description`, and an honest body: what the axis measures, current status, evidence link (`/interop/...json`), and the "no rubric yet" statement where true. Use the existing archive-banner pattern where UNMEASURED so the framing matches the GSPC deep-dives.
4. **Prerender + sitemap + brand-gate** — add slugs to `scripts/prerender.mjs` + `generate-sitemap.mjs`; run `scripts/brand-gate.mjs` (fin-axes content is codename-clean; verify `sov`/`cibola`/`dorado` zero-hits).
5. **Per-axis deep-dive uniqueness** — GSPC 14: add axis-specific `<title>` + description + a per-axis data node (server-rendered number exists in `/api/gspc`; render the axis value into the static HTML at build time instead of client-only). Also fixes the "identical shell" issue for all 22.
6. **House route sweep** — `/products`, `/get-measured`, `/badges`, `/verify-certificate` all fall through to homepage (VERIFIED 25 Aug): each gets either a real page (products = rate-card table from `docs/revenue/ART50-READINESS-PRODUCT`; badges = white-label kit below; verify-certificate = redirect to `/gspc-verify`) or an honest 410. No homepage-fallthroughs in the sitemap.

## Acceptance (e2e gate for 22/22)
```
for a in <22 slugs>; do curl https://councilof.ai/gspc/$a | grep -c "<title>" — unique title expected; done
curl -s https://councilof.ai/api/gspc | jq .registry_count == 22
grep -c "candidacy" board page — the layer is visible to a human
```
All three green = 22-axis standard met.

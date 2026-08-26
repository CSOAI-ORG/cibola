# Deploy-batch manifest — the ONE window (J9 / R4)

**Prepared 2026-08-26 · Owner-facing · The single gate that makes everything real-visible.**
Scope: R1–R4 + AEO + containment, deployed together in one window, on your signal. This is a
coordination manifest — the build/spec files live in the lanes listed; this file is the ordering
and the checklist. **No deploy is performed by an agent without your explicit go.**

> **Why one window:** everything in the estate is real but half-invisible (the live site exposes
> the measurement surface; the 22-axis, white-label and financial pages are spec'd but not yet
> live). One deploy = one announcement = the biggest surface jump per unit effort, and it lets us
> do the E2E-retest once against the END-USER-STANDARD.

---

## 0. The doctrine gate for the whole batch (binding)
- **Measurement, never certification.** No conformity marks. No "certified/approved" claim (GW.3).
- **UNMEASURED is first-class:** 7 candidacy axes stay honest UNMEASURED; 22-axis count is
  *declared*, never claimed as measurable-and-measured.
- **No public $ prices.** Verification is free forever; a grade is never sold.
- **Banned-string + grammar-lint must pass** on every new page (brand-gate CI).

## 1. What goes live together (R1–R4 + AEO + containment)

| # | Surface | The thing | Spec / source (lane) | Status |
|---|---|---|---|---|
| R1 | 22-axis public | candidacy layer + 8 financial pages + unique titles | `docs/e2e/FINANCIAL-AXES-TO-STANDARD-2026-08-25.md` (mine, cibola) | spec'd, build in the deployed-site lane |
| R2 | White-label | embed.js + `/badge` + `/api/embed` + `/badges` | `docs/e2e/WHITE-LABEL-EMBED-KIT-2026-08-25.md` (mine, cibola) | spec'd |
| R3 | /products + /get-measured | real pages (rate card exists) | `docs/revenue/ART50-READINESS-PRODUCT-2026-08-24.md` (mine) | spec'd |
| R4 | **The deploy** | one gated deploy that lands R1–R3 | `client/` build (council-ai lane) | owner go |
| +AEO | Content engine | Stanford 42% AEO + RWA $365B wire | `docs/aeo` + `docs/fire` (fires bundle) | drafted |
| +Containment | Containment Index w/ citations | Kimi K3 verified | lane (verify-sources) | drafted |

## 2. The deploy sequence (the "one window" recipe)

Follow in order — this is the `councilof-ai` deployed-site lane's pipeline (I do not run it; it's
the contested-repo build):

```bash
# 1. build the client (NOT bare `npx vite build` — that picks up dead root src/)
npm run build:client
# 2. pre-render the static pages
node scripts/prerender.mjs --dist dist/client --wait 900 --min 350
# 3. gate the output (brand-gate + signed-JSON guard)
node scripts/brand-gate.mjs dist/client
node scripts/signed-json-guard.mjs dist/client
# 4. push to master — GHA deploy.yml ships it (also runs on 3h cron)
```

> **Recommendation:** land R1–R3 *together* (in the one gated merge, not a stream of `fix:`
> commits) so the retest + announcement is against a coherent surface.

## 3. Post-deploy verification (the retest gate)

- Run **E2E-retest-3** against **`docs/e2e/END-USER-STANDARD-2026-08-25.md`** (the checklist that
  defines "what we are what we say we are" for a real end-user).
- Re-probe the 8 financial pages return **200 with unique `<title>`** (the R1 gap-closer; this is
  the flagged "8 financial 404 / 4 fallthroughs" from the last re-verification).
- **Containment Index** — sources cited per row, verify-sources gate, no uncited claim.
- Banned-string + grammar-lint PASS on every new page.

## 4. The two small money/gate clicks around the window (owner)

| Gate | What | Cost | When |
|---|---|---|---|
| **J9 / R4** | this deploy (coordination from this manifest) | £0 | your window |
| **J3** | stop the 2 A100 pods once builds land (keep sov-repull 3090) | saves ~$60/day | with/after this window |
| **J1** | UKIPO COS001 + COS002 (pre-filled) | ~£170 | any day |

## 5. Honest blockers / not-mine-to-run

- The **deploy itself** runs in the `council-ai` lane (contested, one-lane-one-writer). I prepared
  this manifest + the specs; the merge + build + push is that lane's, on your go.
- **J4 (Stripe)** and **J2 (Equidam)** are money/account gates outside the deploy window.
- **GPAI / CRA packs** (R5, drafted this session) are separate sends — AI Office + white-label
  runbook — not part of R4; confirm before sending.

---

*Council of AI (CSOAI Ltd, UK 16939677) · did:web:csoai.org · Measurement, never certification.*

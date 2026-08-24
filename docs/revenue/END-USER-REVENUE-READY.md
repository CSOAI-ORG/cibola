# END-USER REVENUE READY — CSOAI LTD (Council of AI) · 2026-08-24

**Status:** OWNER-READY · revenue-track readiness summary (NEXT-100 v4 move 97 · v3 move 91 ·
PB-061/062). **Not sent** — external communications are outside this round's scope; this is
the durable record that the agent-doable revenue set is complete and staged for the owner.
**Canon bind:** measurement, never certification; nobody-ranked-pays; buyer-side money only.

> **Register (verbatim):** *This is a measurement credential. It is not a certification,
> endorsement, or conformity mark, and must not be presented as one.* We verify, sign,
> preserve evidence; regulators and accredited bodies decide. We never claim accreditation
> before granted.

---

## Why this page exists

The revenue track is the **first** priority of NEXT-100 v4 (move 97: "Art 50 readiness product +
rate card (€8–80k) — revenue track first"). This page records what an end user / buyer /
insurer / regulator gets, what it costs, and why the estate can be believed. It is the
**owner-ready** artifact: complete, priced, capture-mapped, grammar-linted — ready for the owner
to assign a send sequence and confirm the two remaining revenue gates (**Stripe live-chain**,
**invoicing**). It states honestly that it is **not sent**.

---

## What you get (the product, in one line)

**Independent, stranger-verifiable evidence that an AI system meets — or does not yet meet —
the EU AI Act Article 50 transparency obligations (Art 50(1)–(7), incl. the Art 50(7)
detection-code posture).** Every deliverable is a **verified measurement credential** on the
RFC 9943 (SCITT) substrate — never a certification, endorsement, or conformity mark.

Full product spec: [`ART50-READINESS-PRODUCT-2026-08-24.md`](ART50-READINESS-PRODUCT-2026-08-24.md)

---

## The offer (3 tiers, one instrument)

One instrument, three scopes. Tiers differ in scope and cadence, **never** in the instrument —
and each tier is a measurement credential.

| Tier | Scope | Rate band (EUR) | Cadence | Systems |
|---|---|---|---|---|
| **1** | Single-system Art 50 readiness card | **8k – 12k** | one-shot | 1 |
| **2** | Art 50 + Art 72/73 readiness dossier | **20k – 35k** | 3-day stream, then watch | 1 |
| **3** | Fleet readiness + ongoing verification | **50k – 80k** | scheduled re-verify | 5–50 |

**Tier 1.** Signed Art 50 readiness card + machine-readable transparency summary + auditor-card
template + stranger-verify kit. One system, one point in time, anonymised reporting.

**Tier 2.** Tier 1 + Art 72 post-market-monitoring signed stream (threshold auto-notify demo) +
Art 73 clock-field readiness (15-day / 24-hour) with usage pre-commitment terms + a staged
Art 50(7) input submission + an append-only hash-chained register page.

**Tier 3.** Tier 2 at fleet scale (one register, per-system rows, chainOk integrity guarantee) +
re-verify cadence + drift detection + east–west bridge records (EU / US-IL / CN) + a
second-independent-transparency-service (dual-TS) co-signer matrix.

---

## Pricing doctrine (the commercial firewall)

- **Buyer-side money only.** The entity being measured **never pays** for its own measurement.
- **The score is never for sale.** A vendor can buy the data; a vendor can never buy a rank.
- **No paid placement, no affiliate money, no lab free tokens** — stated as a policy, not an
  attack on any lab's practice.
- **Marginal pricing in Tier 3** — the first ~5 systems are at the band top; each additional
  system is priced at a diminishing marginal rate, never summed linearly. The €80k ceiling is
  the soft cap for a full fleet program in-week.
- A run below a credibility floor is reported truthfully and marked **NOT QUOTABLE** — never
  prettified into a finding.

---

## Why the estate can be believed (capture-map)

The market asks **"verified how?"** about every leaderboard, and the one thing that cannot be
bought is the score. We are in the **independent + signed** cell:

- **Never a captured referee** — we take no money from the scored.
- **Complement, not competition, to arena/crowd referees** — same methodology intent, plus the
  signed, content-addressed, key-verifiable layer.
- **Multi-anchor, not single-vendor** — a second independent transparency service (dual-TS) and
  a co-signer, so no single party is the verdict.

Full capture-map: [`ART50-CAPTURE-MAP-2026-08-24.md`](ART50-CAPTURE-MAP-2026-08-24.md)

---

## The evidence we hand an end user (all real, all citable)

1. **One canonical instrument description** — `docs/one-instrument-2026-08-24.md`
2. **Measurement-card schema + register verbatim** — `schemas/measurement-card.schema.json` ·
   `bundle/REGISTER.md`
3. **Frozen vectors (hash-pinned, deterministic)** — `test/vectors/`
4. **SCITT cryptographic verify (RFC 9052 CBOR / Ed25519)** — `harness/scitt_verify.py`
5. **A production-signed card + receipt** — `assets/example-production-card.json`
6. **GB/T credibility gates** — `harness/gbt_gates.py` (≥90% / ≤5% / n≥2k / n≥10k; below floor
   = NOT QUOTABLE)
7. **Verify-kit + append-only verification counter** — `harness/verify_kit.py` · `data/verify-log.jsonl`
8. **Art 50 consultation response (staged, owner-gated)** — `docs/ART50-TRANSPARENCY-CONSULTATION-RESPONSE-2026-08-24.md`

---

## What is OWNER-GATED (not agent-doable; staged, never executed)

The two revenue rails the owner confirms before anything is sent:

1. **Payment rail** — the Stripe live-flip chain (`keystone sync-vercel` keys → Stripe live →
   CT registration); 3 gates remain (sync-vercel, npm 2FA, SMITHERY).
2. **Invoicing / send sequence** — external communications are entirely outside agent scope.

No external communication executes from here. This pack is a **durable artifact**, not a send.

---

## Readiness checklist

- [x] Product spec drafted (Art 50 readiness, 3 tiers) — `ART50-READINESS-PRODUCT-2026-08-24.md`
- [x] Rate card bands (€8–80k) + marginal pricing doctrine
- [x] Capture-map (independent vs captured referee) — `ART50-CAPTURE-MAP-2026-08-24.md`
- [x] Grounded in real estate artefacts (production card, frozen vectors, SCITT verify, gates)
- [x] Grammar-linted for the measurement-credential canon + completeness over-claim guard (CI)
- [x] Banned-string lint passed (no lane brand on staged external text)
- [ ] **Owner:** confirm payment rail (Stripe live-chain) + send sequence
- [ ] **Owner:** any external communication

*End. Owner-ready, not sent (round scope: revenue-track drafting only).*

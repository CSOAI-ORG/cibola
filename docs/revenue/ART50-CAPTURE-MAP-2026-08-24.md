# CAPTURE-MAP ONE-PAGER — independent vs captured referee (2026-08-24)

**Status:** OWNER-READY · one-pager · move 97 (revenue pack) · also referenced from the METR and
TB/Harbor pack v2 (the "capture-map one-pager: independent vs captured referees" link).
**Canon bind:** measurement, never certification; nobody-ranked-pays; buyer-side money only.

> **Register (verbatim):** *This is a measurement credential. It is not a certification,
> endorsement, or conformity mark, and must not be presented as one.*

---

## The one-line pitch

**The market now asks "verified how?" about every leaderboard, and the one thing that cannot
be bought is the score.** Independence is the only unsold inventory in the AI-evaluation market.

---

## The grid

| Referee type | What they are | The capture risk | Where CSOAI sits |
|---|---|---|---|
| **Captured referee** | A lab's own leaderboard; a vendor-sponsored benchmark; a paid evaluator | The scored funds the referee → the number bends toward the funder. | **Never here.** No money from the scored. |
| **Arena / crowd referee** | LMArena-style Elo | Human-preference strength; **no signed, deterministic trace**; gamed or mis-attributed (a model name is not a model — join on weights, not names). | **Complement.** Same methodology intent, plus the signed, content-addressed, key-verifiable layer. |
| **Vendor-referee** | A single verification vendor's verdict | A single-party verdict is a single point of trust. | **Multi-anchor.** Second independent transparency service (dual-TS) + a co-signer, so no single party is the verdict. |
| **Independent + signed (CSOAI)** | Deterministic, no-LLM-judge, hash-pinned, RFC 9943 + RFC 3161, did:web, **stranger-verifiable** | The residual risk is the measurement *instrument* — mitigated by one canonical description, frozen vectors, a refutation path, and **NOT QUOTABLE** honesty below a floor. | **This cell.** We issue no certification claim; we make the evidence independently checkable. |

---

## Why the neutrality clause is commercial (not just ethical)

The one thing a funded referee cannot do is **_prove_ it did not bend** — because the funder
and the referee are the same person. By construction:

- The **scored entity never pays** for its own measurement.
- The **signer is separate from the judge**, so no one can buy a signature over a favourable number.
- Every card is **stranger-verifiable** with a public key only, so the claim is never the
  referee's word.

That is the whole capture-map: in a market consolidating around funded referees, the **only
credible cell is the independent + signed cell** — and it is the one that costs the estate its
lab-token revenue in exchange for being believed.

---

## The evidence a buyer should ask for, and what we hand them

1. **Canonical instrument description** — `docs/one-instrument-2026-08-24.md` (one description,
   one schema, one verification path).
2. **Frozen vectors** (hash-pinned, deterministic) — `test/vectors/`.
3. **SCITT cryptographic verify** (RFC 9052 CBOR / Ed25519) — `harness/scitt_verify.py`.
4. **A production-signed card** — `assets/example-production-card.json` (+ receipt).
5. **The register verbatim** — the negation, carried on every card.
6. **The GB/T credibility gates** — `harness/gbt_gates.py` (below a floor = NOT QUOTABLE).

*End. Owner-ready, not sent.*

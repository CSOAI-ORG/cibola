# 22-Axis Payload Anatomy — the R1 gap-closer (probed 2026-08-26)

**Purpose:** the measurable anatomy of how "22-axis" is represented across the machine layer,
so the R1 deploy has a precise, byte-verifiable change set. Probed from the live `councilof.ai`
`/api/gspc` + `/api/axis-register`.
**Doctrine gate:** the 22-axis canon is **declared**, never claimed as measurable-and-measured.
7 candidacy axes stay honest **UNMEASURED**. Measurement, never certification.

---

## 1. The three-tier representation (this is the crux)

| Layer | Count | What it is | Status |
|---|---|---|---|
| **Public board floor** | **14** | 13 board axes + jail — `totals.axes = measured_axes = quotable_axes = 14`, `public_count = "14 measured of 14 quotable"` | ✅ public, measured, quotable |
| **Internal 16-slot convention** | 16 | board + **slot15 (instrument-honesty)** + **human-vs-ai** — carried in `measured_in_lane` | 🟡 **NOT board-quotable** (reconciliation gate owner-gated) |
| **22-axis canon** | 22 | 14 public + **8 financial / candidacy slots** | 🟡 candidacy declared, financial axes live, machine count not yet 22 |

## 2. What the probe actually shows

**`/api/gspc` `totals` block** (the counter that must move 14→22):
```
axes: 14            measured_axes: 14        quotable_axes: 14
public_count: "14 measured of 14 quotable"
items: 887          separated_leads: 4       ties: 10      untested_separations: 0
```
The `counting_rule` (in `/api/axis-register`) confirms: *"Slot counts live in GET /api/gspc totals
(public_count, measured_axes, quotable_axes). This register lists the 14 canonical scored rows (13
board axes + jail)."*

**`/api/axis-register`**: `registry_axis_count = 14`, `public_count = "GET /api/gspc totals.public_count"` — it delegates to `totals`.

**`measured_in_lane`** (the engine already measured beyond 14 — the honest 16-slot convention):
- **slot15 — instrument-honesty** — `status: MEASURED`, `separation: UNTESTED`, `fleet: "6 models — NOT the 19-model board fleet"`, honest-rate 0.086–0.333 (every model fabricates most of the time). "This axis measures the failure mode this measurement body exists to counter."
- **human-vs-ai** — `status: MEASURED`, `separation: UNTESTED`, `fleet_mean 0.8498`; our own `council-safe` fine-tune aligns 0.25 (misaligned 3-to-1). "The instrument catches its own maker first."

**Limitations (verbatim, the honesty vault):** slot15 + human-vs-ai *"is the internal 16-slot living-board
convention: 6-model fleet, no separation test, served for honesty only. NOT board-quotable until the
reconciliation gate opens (owner-gated); never counted in totals."*

## 3. So what exactly is the R1 change set (the 14→22 move)

To make the machine layer report 22 without over-claiming:

| Change | Meaning | Honesty rule |
|---|---|---|
| `totals.axes: 14 → 22` | the canon is declared at 22 | but `measured_axes` and `quotable_axes` must **not** jump to 22 — **8 candlacy axes stay UNMEASURED** |
| `public_count` | "22 declared · 14 quotable · 8 candidacy (UNMEASURED, declared)" | never "22 measured of 22" unless all 22 are genuinely measured |
| `axes[]` in `/api/gspc` | append the 8 financial/candidacy slots with `status: UNMEASURED` + a `measured/total` of `0/…` | honest UNMEASURED, never a fabricated 0-as-measured |
| `measured_in_lane` slot15 + human-vs-ai | stay `NOT board-quotable` (owner-gated reconciliation) | not counted in totals until the gate opens |

**The single byte-verifiable gate:** after R4, `totals.axes == 22` AND `public_count` reads
"22 declared · 14 quotable · 8 candidacy (UNMEASURED)" — never "22 measured of 22." The 3 routes
`/axes`, `/candidacy`, `/22-axis` return **200** with that honest count. The `measured_in_lane`
honesty rows stay `NOT board-quotable` until the owner opens the reconciliation gate.

## 4. The honesty vault (what makes this defensible — quote these)

- *"4 of the 14 canonical axes show a statistically separated leader (McNemar p<0.05)… 10 are statistical ties — a point-estimate lead is not a measured advantage."*
- *"the instrument catches its own maker first"* (our own fine-tune misaligned 0.25).
- *"slot15 (instrument-honesty)… NOT board-quotable until the reconciliation gate opens (owner-gated); never counted in totals."*
- *"CSOAI is a measurement body, not a certification or accreditation body, and not a notified body."*

---

*Council of AI (CSOAI Ltd, UK 16939677) · did:web:csoai.org · Measurement, never certification.*

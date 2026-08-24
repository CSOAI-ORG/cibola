# Corrections Register — C-23+ review (2026-08-24) · append-only asserted

**Move:** 33 · **Status:** REVIEW DONE (agent-doable half) · **Canon hook:** *append-only corrections*; "the instrument that catches its own owner is the instrument you can rely on."

## What this is
The estate publishes a live **corrections feed** (`councilof.ai/api/corrections`, schema `csoai.corrections/0.1`) — the register of record for every self-caught error. Each entry records *what was wrong / how it was caught / the fix.* The register's own policy is **append-only** ("Appended, never edited or deleted"), which is the honesty discipline: the scorer that catches its own owner is the one you trust.

This round **reviewed** the register (read-only capture) and **committed** a hermetic in-repo guard + a point-in-time snapshot so the append-only contract is enforced in CI and cannot silently rot.

## Review findings
- **Register integrity: sound.** 15 corrections present at the point-in-time snapshot; every entry carries the core fields (`id`, `date`, `what_was_wrong`, `how_caught`, `fix`); ids are **unique** and **strictly monotonic by (date, id)**; each id **embeds its date** (e.g. `C-2026-0819-13` → 2026-08-19), so history is immutable-ordered. Publisher + `CC-BY-4.0` license + a signature envelope are present, so the append-only claim is attestable, not merely asserted.
- **Latest entries (C-2026-0820-01, C-2026-0822-01)** were reviewed in-band: posted-confidence gaps and an app/board-consistency self-catch, both closed with `status` set.
- **One honest schema gap (surfaced, not "fixed").** Entry **`C-2026-0819-13`** has **no machine-readable `status`** field. Because the register is *append-only*, the snapshot must NOT be back-filled by editing that row — the correct close is the live-surface owner **appending** the status. The guard reports this as a `REVIEW-FINDING` rather than failing the build, so a genuine upstream gap is always visible and never quietly "repairs" history.

## Files landed
| File | Purpose |
|---|---|
| `data/corrections.register.json` | Point-in-time snapshot (captured read-only 2026-08-24; rows untouched — append-only honored in the copy). |
| `test/corrections-register.py` | Hermetic guard: asserts the schema + append-only policy + provenance envelope + unique/monotonic/date-embedding ids + core fields on every entry; surfaces any missing `status` as a `REVIEW-FINDING`. Wired into CI. |
| `data/corrections.register.json` source | `councilof.ai/api/corrections` (read-only GET). |

## Not done (owner-gated, honest)
- Closing `C-2026-0819-13`'s missing `status` on the **live surface** is an owner/board-side append, not an in-repo edit.
- Verifying the register's signature envelope against the did:web root key is a separate signed-credential verification; not invoked here (no fabrication).

## Why it matters
The same over-claim disease that infects benchmarks infects correction logs. An append-only, schema-guarded corrections register reviewed in CI is a credibility deposit: the public can verify we record our own errors and never edit them away.

*Move 33 agent-doable half complete. Append-only contract is now committed + CI-guarded in-repo.*

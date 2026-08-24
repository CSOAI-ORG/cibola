# OIN Linux-System Scope Check — measurement card format & instrument IP (2026-08-24)

**Move 99.** This is the estate's mandatory **OIN Linux-System scope check** (the rule
governing every patent / provisional touchpoint, from AGENTS.md), run against the
measurement-instrument IP before any filing. **Result: NOT Linux-kernel-adjacent →
filing is clean; the OIN 2.0 Section 1.2 grant-back does NOT apply.**

> This is a pre-filing analysis record, not a filing, not a legal opinion, and not a
> cryptographic signature. It records the reasoning and the decision so the choice is
> conscious and traceable. If any future invention IS Linux-kernel-adjacent, this same
> check must be re-run and either (a) a Limitation Election under Section 2.2 filed to
> keep it out of scope, or (b) the grant-back consciously accepted and escalated.

---

## 1. The OIN 2.0 obligation in one line

OIN (Open Invention Network) 2.0 licenses its member system-invention patents back to its
3,500+ licensee/member network under **Section 1.2**. The trigger is "Linux System" as
defined by OIN: Linux-kernel-adjacent system software. A patent whose claims would read on
the Linux System is subject to the grant-back. A patent that does **not** read on the Linux
System is outside the grant-back and stays with the estate.

## 2. What was checked (the instrument IP)

| Asset | What it is | Linux-kernel-adjacent? |
|---|---|---|
| The signed-card format (`application/vnd.cibola.measurement-card+json`) | a JSON measurement credential + Ed25519 `COSE_Sign1` envelope | **No** — data format / signature envelope |
| The measurement axes (GSPC-16 + domain registries) | frozen governance probes + deterministic gold labels | **No** — prompt/label corpus |
| The measurement instrument (engine/harness/CLI) | deterministic grader + signer + board | **No** — measurement pipeline |
| The RFC 9943 SCITT substrate (receipt + RFC 3161 anchor) | transparency/log transport | **No** — attestation protocol |
| The estate's OWEM stack | data/measurement substrate | **No** — not a kernel-system patent |

## 3. Conclusion

None of the checked assets are **Linux-kernel-adjacent**. Their claims would not read on the
OIN "Linux System" definition, so **Section 1.2 grant-back does not apply**. Filing on the
measurement instrument IP is **clean under OIN 2.0** — the grant-back is a non-event, and
the IP stays with the estate.

This matches the estate's standing position: the measurement instrument IP, the signed-card
format, and the GSPC axes are the **crown jewels** and are **unaffected by OIN**. The
**only** future-IP exposure OIN creates is a Linux-kernel-adjacent patent, which this check
would catch at the next touchpoint.

## 4. Binding IP invariants (confirmed, not relaxed here)

- The signed-card format, the measurement axes, and the instrument estate are **crown
  jewels** — never licensed to a party that could monetise them against the estate.
- Any deal moving the signing keys or instrument estate into a conflicted owner would kill
  the company — **neutrality is the asset** (Scale AI is the cautionary tale).
- The measurement instrument is a **measurement** body; its IP is the measurement
  methodology, not a certification authority.

## 5. LOT Network membership — status note

Per the estate's patent & IP governance log, **LOT Network membership was submitted
2026-08-15; membership status is still PENDING** (not yet confirmed active). This is recorded
honestly as pending, not claimed as granted. Re-confirm membership status at the next
IP governance check before relying on LOT terms.

## 6. Decision record

- **Decision:** the measurement-card format and instrument IP are **non-Linux-kernel-adjacent
  → clean to file under OIN 2.0** (no grant-back, no Limitation Election required).
- **Escalation:** none required for *this* asset set. The next patent/provisional touchpoint
  must re-run this check before filing.
- **Runs against:** future **UKIPO** submissions (COUNCIL OF AI / MEOK — owner-gated, staged
  only) and any provisional.

---

*This document was authored as an agent-doable analysis record (move 99). It does not
constitute a filing, a payment, or a legal opinion. The OIN scope check is mandatory at every
future patent touchpoint (AGENTS.md).*

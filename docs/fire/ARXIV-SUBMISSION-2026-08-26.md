# ARXIV SUBMISSION PACK — TIER-0, due 27 Aug (TOMORROW) · staged 2026-08-26

**arXiv ref:** G6Y9SY (per master backlog 0.1 — submission window opens/closes 27 Aug; missing it = permanent).
**Submission route:** arXiv account (or endorser) → New submission → paste title/abstract → categories → submit.
**Endorser:** forward still owner-gated (per account-prep; academic contact needed if account is new).

## Title
Signed, Recomputable Attestations of AI Measurement: A Minimal Format with an Append-Only Corrections Ledger

## Authors
Nicholas Templeman (CSOAI Ltd, UK 16939677) — affiliation: Council of AI

## Abstract (paste-ready)
We define a minimal, interoperable format for cryptographic attestations of AI system measurement
results: a content-addressed card (SHA-256 canonical form) signed with Ed25519, bound to a did:web
identifier, with an append-only corrections ledger and a three-state verification model
(valid/invalid/unverifiable). The format is not a certificate; it is a stranger-recomputable record
of what was measured, on which instrument, with which confidence interval, so that third parties
(regulators, buyers, researchers) can verify without trust. We align with RFC 9942 (COSE receipts)
and RFC 9943 (SCITT) semantics, report a live 22-axis measurement board (15 measured / 7 candidacy
UNMEASURED), and document the anti-gaming property: re-publishing identical evidence mints zero new
verdicts. Reference implementation and conformance suite are open source; an IANA media-type
registration (application/vnd.cibola.measurement-card+json) and an I-D are in progress.

## Categories
cs.AI (primary) · cs.CR (secondary) · cs.SE

## Files to attach at submission
- Full paper (draft from docs/fire/FIRES-BUNDLE §1 — extend to submission length)
- Frozen test vectors + verify.py (repo links)
- DOI-pending Zenodo deposit 22113338 (optional citation)

## Pre-submission checklist (from backlog TIER-1 — DO NOT submit with these open)
- [ ] per-card preimage field correct (backlog 1.1 — payload-level, lane)
- [ ] HOW-TO-VERIFY.md matches live fields (1.2)
- [ ] Fassbender citation → /01/ not -05 (1.3)
- [ ] packaged_at advanced past 2026-08-24 (1.4 — CONFIRMED STALE TODAY)

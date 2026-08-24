# IETF datatracker I-D submission — STAGED text (do NOT submit; owner-gated)

**Document:** `draft-csoai-scitt-measurement-card-00` (existing draft file:
`draft/draft-csoai-scitt-measurement-card-00.txt` in the repo).
**Status of this file:** STAGED — the datatracker I-D submission text, drafted for the IETF
datatracker posting. Per the Ralph hard stop, this is **never** submitted/sent by an agent.
It is the submission body (title, authors, abstract, comments) the owner can paste into the
datatracker "submit draft" flow when the send window opens.

**Week theme:** three deadlines, one proof — this I-D is the published-specification leg the
IANA registration (move 3) and the verification story depend on. Format:
**measurement card**, on the RFC 9943 / RFC 9942 substrate.

---

## datatracker submission fields

**Document name:** draft-csoai-scitt-measurement-card

**Version:** -00

**Title:** Signed Measurement Cards for AI Governance Verification

**Authors:**
- CSOAI Ltd (Council of AI) — CSOAI LTD, UK Companies House 16939677;
  `did:web:csoai.org`

**Abstract:**
This document specifies a signed **measurement card**: a compact, JSON-encoded
**(verified measurement credential)** that binds a measured AI-governance result to its
publisher at a point in time, on the SCITT (RFC 9943 / RFC 9942) receipt substrate. The card
is signed with Ed25519 (COSE_Sign1, RFC 9052), bound by an SCITT receipt, and anchored to
external time. A stranger verifies it entirely offline with the publisher's published
`did:web` key. The core measured values are produced by a deterministic predicate over frozen
gold labels; no large language model judges or scores. **This is a measurement, never a
certification, endorsement, or conformity mark** — a card is evidence of what was measured
and when, and must not be presented as an accreditation or compliance claim.

The document defines the card payload, the signing profile, the anti-equivocation boundary
(a receipt proves inclusion, not non-equivocation), and the security considerations with
respect to key compromise, replay, and exclusion-manifest integrity.

**Comments to the IETF secretariat:**
- The card format and the CIBOLA verification protocol are the measurement-estate's first
  standards-track submission.
- The vendor media type `application/vnd.cibola.measurement-card+json` is registered
  separately (IANA process, move 3 / RFC 6838).

---

## IANA Considerations (already in the I-D body)

The specification registers an `application/vnd.cibola.measurement-card+json` media type in
the vendor tree and records the intent to upgrade to the standards tree on working-group
adoption.

---

## Post-submit checklist (owner-gated, never agent-sent)

- [ ] Submit the draft on the datatracker; confirm the `-00` revision is on the IETF draft
      archive.
- [ ] Add a row + link to the standards-engagement log (move 72).
- [ ] Re-run `test/grammar-lint.py` + `test/banned-strings.py` (this file is STAGED).

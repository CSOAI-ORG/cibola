---
title: A Measurement Card for Signed AI Governance Results
abbrev: measurement-card
docname: draft-csoai-scitt-measurement-card-00
category: info
submissiontype: IETF
consensus: false
area: Internet
workgroup: (none)
ipr: trust200902
keyword: [scitt, measurement, governance, signature]
stand_alone: true
pi: [toc, sortrefs, symrefs, comments]
author:
  -
    ins: N. Templeman
    name: Nicholas Templeman
    org: CSOAI Ltd (Council of AI)
    email: nicholas@csoai.org
normative:
  RFC9943: scitt-architecture
  RFC9942: scitt-receipts
  RFC9679:
informative:
  RFC9162:
--- abstract

This memo fills a gap in the SCITT score layer: the submission and receipt
machinery (RFC 9942, RFC 9943) is standardized, but there is no signed
measurement-card format. Independent AI-governance measurement bodies need to
publish a verifiable, signed result that a *third party* can check offline and
attribute to a named identity — without certifying anything. This document
defines the `measurement-card` payload: a detached, signed credential that
reports measured axes and carries an explicit register stating it is a
measurement, never a certification. A measurement card is a member of the
SCITT receipt ecosystem: it rides the RFC 9943 substrate and can be
transparency-logged (RFC 9162) with the CIBOLA key.

--- middle

# Introduction

The signed score layer is empty. SCITT receipt drafts disclaim outcomes and
attest only to what was *submitted and when*. Nothing yet signs a *measured
result* in a way a regulator, insurer, or buyer can verify independently. This
memo adds that third leg: a signed measurement card.

The design constraints (the CIBOLA canon):

* **Measurement, never certification.** A card is evidence of what was measured
  and when. It is not an accreditation, conformity mark, or endorsement.
* **Deterministic core, optional narration.** The measured values are produced
  by a deterministic oracle against frozen gold labels; the LLM (if any) only
  narrates the signed record and can never alter it.
* **Join on weights, not names.** A model NAME is not a model. The card carries
  a content digest of the subject so two cards that name the same model but
  measure different weights are distinct.
* **Completeness grammar.** "13 measured of 14" is honest. If an axis is not
  measured, it is named and excluded, not silently omitted.

# Measurement Card (v0.1)

# Payload

The card payload is a JSON object with the fields:

* `subject`: the system measured (`id`, `name`, `digest`).
* `benchmark`: the frozen universe (`id`, `digest`, `gold_labels`).
* `scores`: axis -> measured result, each carrying `n` (no quotable number below
  n>=30) and `interval` (Wilson).
* `measured_count` / `total_count`: the completeness grammar.
* `exclusion_manifest`: hash of the axes excluded and why.
* `provision_map`: jurisdiction-keyed obligation references (the east-west hook).
* `run_manifest`: `harness_hash` (anti-harness-trojan) + `replay_merkle_root`.
* `issued_at`, `credential_register`.

(#example-card)

# Signature

The card is COSE_Sign1 (RFC 9052 profile per RFC 9943), alg -19 (Ed25519). The
`kid` carries the RFC 9679 thumbprint of the did:web key that signed it. The
signing key is the CIBOLA POD key; it never leaves the signing pod.

# Anti-Equivocation

A receipt proves inclusion; it does not prove non-equivocation. Non-equivocation
requires a consistency proof plus a monitor. This memo does not claim
non-equivocation; it states exactly the guarantee provided.

# Security Considerations

Key compromise (rotate via the did:web key list, append-only); replay (the
`issued_at` and the SCITT receipt timestamp); exclusion-manifest gaming (the
manifest is itself hashed and signed).

# IANA Considerations

This memo registers an application/media type in the vendor tree for the
measurement-card payload and records an intent to upgrade to standards tree
when the format reaches WG adoption.

# Acknowledgements

The CIBOLA contributor community and the Applied Agents researchers whose
review shaped the deterministic-core boundary.

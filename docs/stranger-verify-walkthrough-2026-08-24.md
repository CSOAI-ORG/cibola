# Stranger-verify walkthrough — verify a measurement card in 60 seconds (NEXT-100 v4, moves 5/71)

**Who this is for:** a stranger on any device, with no DORADO account, no private key, no
network trust beyond the published `did:web` root. Goal: confirm that a published
measurement card really was signed by the estate's key, bound by its receipt, anchored in
time, and present in the append-only register — and do it in about 60 seconds.

This is the **stageable** walkthrough behind the verify page (move 5) and the public
genesis-card + verify experience (move 71). The live deploy is owner-gated; this document is
the durable, stranger-followable description of exactly what a stranger does and verifies.

## The honest claim, first

A card is a **measurement credential** — evidence of what was measured and when. It is *not*
a certification, endorsement, or conformity mark, and must not be presented as one. The
register on every card says so verbatim. What a stranger verifies here is **proof of
provenance and integrity**, never that any model is "approved" or "compliant".

## What a stranger needs

- Any machine with Python 3.11+ and `pip install cryptography asn1crypto` (the Ed25519 +
  RFC 3161 legs). No Ollama, no pod, no network required — the verification is **offline**.
- Git clone (optional): `git clone https://github.com/CSOAI-ORG/cibola.git`.
- The published trust root: `did:web:csoai.org` → `https://councilof.ai/.well-known/did.json`.

## The 60-second walkthrough

### 1. Get the card
From the verify page (`/verify` on the published surface) paste the card JSON, or fetch the
published card file. The card is a signed JSON object whose `credential_register` is the
register negation. **Read it first** — it must say "measurement", never "certification".

```bash
python3 cli/dorado.py verify --card <card.json>
```

- `VALID` → the signing key (`kid`) really signed *this exact* card (Ed25519 over the
  canonical form). `INVALID` → stop: the card is altered or signed by a key we do not
  recognise.

### 2. Pin the identity to the trust root
The card's `signature.kid` names a key (e.g. `did:web:csoai.org#card-attestation-1`). Confirm
that key is listed as an **active** `assertionMethod` in the published
`councilof.ai/.well-known/did.json`. If the `kid` is *not* in the live document, the card is
**not ours** — the verify tool reports it as "self-consistent but NOT pinned" (never
verified-authentic), which is the honest outcome, not a pass.

### 3. Verify the receipt binds the card
```bash
python3 cli/dorado.py verify-receipt --receipt <receipt.json> --card <card.json>
```
`VALID receipt` means the SCITT (RFC 9943) receipt attests to **this** card at **this** time.
`does NOT attest` → the receipt belongs to a different card; reject it.

### 4. Verify the external-time anchor
```bash
python3 cli/dorado.py verify-anchor --anchor <anchor.json> --card <card.json>
```
`ANCHOR VALID` means an external transparency service time-bound this card's digest. Optional
for a quick check, but it is what shows the measurement predates any later claimed result.

### 5. Confirm the register row
The card's content address appears as a row in the append-only, content-addressed,
hash-chained measurement register (`board/board-index.json`). Confirm the row exists, is
`signed`, and the chain is intact (`chainOk = true`):
```bash
python3 cli/dorado.py board
```

### 6. One command, whole card (optional)
```bash
python3 cli/dorado.py verify-all --card <card.json> [--receipt <receipt.json>] [--anchor <anchor.json>]
```

## Stranger, offline, in one artifact — the verify-kit

For a single self-contained download, the estate ships a **verify-kit** (move 17): card +
receipt + anchor + the public did:web key set + a plain walkthrough in ONE deterministic
artifact, verified entirely offline with only `cryptography`.

```bash
python3 cli/dorado.py verify-kit --in <kit.json>
```

- `VALID verify-kit` → digest intact + card verifies + receipt binds + identity pinned.
- The identity pin is labelled **caller-trusted** (the stranger holds the key set
  independently from `did:web`) vs **kit-bundled** (keys shipped *inside* the kit). A
  `kit-bundled` verdict proves the mechanism but is **not** an independently-fetched
  `did:web` authentication — a stranger should still cross-check the trust root.

## Confirm the tooling yourself (10 seconds)

The estate's own pinned vectors let a stranger confirm the verifier is honest before trusting
any single card. The frozen fixtures assert: card-valid verifies, card-bad-sig fails, and
receipt-bad fails card-bind — and the same vectors flow through the offline verify-kit.

```bash
python3 test/frozen-vectors.py        # 8/8 checks: the verifier accepts the valid + rejects bad-sig/bad-receipt
python3 test/frozen-vectors-kit.py    # 12/12 checks: the same vectors verify through the offline verify-kit
```

## What this does NOT prove

It proves provenance and integrity at a point in time — **not** performance quality, not
safety, and never a certification. The measurement credential is a signed record; the
"13 measured of 14" completeness grammar means the 14th canonical axis (the human baseline)
is DPIA-gated and honest-unknown, never silently claimed. A stranger should always judge the
*measured result itself* on its evidence, not on the signature.

---

*Register (verbatim from canon): a measurement card is evidence of what was measured and
when. It is not a certification, endorsement, or conformity mark, and must not be presented
as one.*

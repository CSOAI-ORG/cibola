# CIBOLA — Example Measured Asset (Benchmark-as-a-Service)

This is a **worked example** of the CIBOLA data layer: a measured card, its SCITT
receipt, and the licensable data product it produced. It demonstrates the
full pipeline —

**measure → sign (Ed25519, COSE_Sign1) → receipt (RFC 9943) → anchor (RFC 3161) → export data.**

## ⚠️ Signing-key note (read first)

These examples were signed with a **throwaway development key** to demonstrate the
pipeline, NOT the production `did:web:csoai.org#card-attestation-1` key (THE BRICK,
estate key `d4cb0eaa`). The production private half is Mac/keystone-held and must
never be committed. To produce a **production-signed** card:

```bash
CIBOLA_SIGNING_KEY_FILE=<pod key> cibola sign  --card card.json
CIBOLA_SIGNING_KEY_FILE=<pod key> cibola receipt --card card.json --out receipt.json
cibola anchor --card card.json --out anchor.json     # external RFC 3161 time-binding
```

A stranger verifies each leg with only the published key + `cryptography`
(anchor verification also needs `pip install asn1crypto`):

```bash
cibola verify-receipt --receipt receipt.json --card card.json   # binds receipt -> card
cibola verify-anchor  --anchor anchor.json  --card card.json    # external time-binding verified
```

## Files

| File | What it is |
|---|---|
| `example-measured-card.json` | A signed CIBOLA measurement card (16/16 measured, `qwen2.5:3b`, score 0.5). |
| `example-card-receipt.json` | An `a2a.signed-receipt/0.1` SCITT receipt binding the card's `content_id` to `did:web:csoai.org`. |
| `example-card-anchor.json` | An **external RFC 3161 TSA time-binding** for the card's digest (GlobalSign R45 AATL chain), verified independently. |
| `example-license-manifest.json` | A signed data-license manifest (mechanism; the illustrative buyer is a demo — only Nick countersigns a real deal). |
| `example-linked-card.json` | A cross-border domain card, audited by A2A client (VALID) — the human/A2A-verifiable artifact. |
| `example-linked-receipt.json` | Its SCITT receipt (binds to the card). |
| `example-linked-anchor.json` | Its **real RFC 3161 TSA anchor** (genTime 2026-08-23 06:00:11Z, MessageImprint matches). |
| `data/bench-data-qa.jsonl` | The core Q/A product (16 rows, per axis; answer-hash deduped). |
| `data/bench-data-preference-pairs.jsonl` | Measured A/B preference pairs (16 rows). |
| `data/bench-data-safety-incidents.jsonl` | Deterministically-flagged safety incidents (failures — the most valuable data). |
| `data/bench-data-meta.json` | Product metadata + neutrality register. |

The example anchor was verified at runtime: `ANCHOR VALID (external TSA time-binding
verified)`, `messageImprint matches=True`, digest binding `dig_ok=True`,
`gen_time 2026-08-23 05:18:17Z`.

## Production-signing (drop-in, one command once the pod key is present)

The real CIBOLA signing key is `did:web:csoai.org#card-attestation-1` (THE BRICK,
estate key `d4cb0eaa`), Mac/keystone-held. The moment the pod key is available,
produce a **production-signed, externally-anchored** card — no code changes, just
the real key:

```bash
# measure a DOMAIN registry (e.g. bond) and emit its card
cibola measure --model <model> --domain bond --card card.json --out axis.json

# sign with the real #card-attestation-1 key
CIBOLA_SIGNING_KEY_FILE=<pod key> cibola sign       --card card.json
CIBOLA_SIGNING_KEY_FILE=<pod key> cibola receipt    --card card.json --out receipt.json
CIBOLA_SIGNING_KEY_FILE=<pod key> cibola anchor     --card card.json --out anchor.json   # RFC 3161 TSA
```

The card carries a `provision_map` (east-west bridge) — jurisdiction-keyed
provision citations per axis — which cites the law/standards a score orbits but
**never** asserts legal compliance (measurement, never certification).

A stranger verifies every leg with only the published key + `cryptography`
(anchor also needs `pip install asn1crypto`):
`cibola verify` · `cibola verify-receipt --receipt receipt.json --card card.json` ·
`cibola verify-anchor --anchor anchor.json --card card.json`.

## Doctrine (binding)

- **Measurement, never certification.** The register verbatim appears on the card,
  the receipt, and every data row: *"This is not a certification, endorsement, or
  conformity mark, and must not be presented as one."*
- **Neutrality.** Data is sold as a product; a vendor can never buy a score. Every
  revenue line is downstream of a scored-independent measurement.
- **Join on weights, not names.** The example `subject.digest` is a placeholder in
  this demo; a production card must carry a real weights content-hash.

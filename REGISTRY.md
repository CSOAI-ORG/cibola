# REGISTRY.md — registry of record + did:web-signed update flow (NEXT-100 v4, move 7)

The registry of record is **the measurement board** (`board/`). It is an append-only,
content-addressed, hash-chained **measurement register** — NOT a rank table and NOT a
certificate register. Each row is a signed measurement credential on the RFC 9943 / RFC 9942
substrate. See `bundle/REGISTER.md` for the register verbatim (the negation) and `GOVERNANCE.md`
for the binding canon ("measurement, never certification"; "13 measured of 14"; honest `unknown`).

## What the registry of record is

Two files in `board/` are the authoritative register:

| File | Role | Shape |
|---|---|---|
| `board/board-index.json` | content-addressed index of the chain | `generated_at`, `count`, `chainOk`, `linked` (int), `unlinked` (int), `measurements` (list of row summaries) |
| `board/measurements.jsonl` | append-only, ordered row log (the raw rows) | one JSON object per line, hash-chained via `prev` |

`chainOk = true` (verified 2026-08-23/24; `count = 28`, 0 breaks) means every row's `prev`
link resolves to the prior row's `hash` and the chain is intact. `linked`/`unlinked` are the
counts of rows bound / not yet bound into the index.

## Registry-of-record row structure

Each row is a measurement summary keyed by the card's content-address (`hash`, the first 16
hex of the card canonical digest). Representative row fields:

```
hash        content-address of the card (leading digest)
ts          measurement timestamp (UTC)
registry    domain-registry id the row belongs to (see below)
subject     measured subject id;  subject_name  human label
measured    axes actually measured this run;  total  axes in the registry
kid         did:web signing key that signed it (e.g. did:web:csoai.org#card-attestation-1)
signed      true only if a verified signature is present (unsealed never signed)
receipt        /  receipt_content_id   SCITT (RFC 9943) receipt binding the card
anchor_time   /  anchor_generic_time   RFC 3161 / transparency anchor generation time
provision_axes  number of provision-mapped axes
path        published card file (may live on the publishing surface, not the repo)
prev        hash of the prior row in the same chain (null for the genesis row)
i           chain index (0-based, monotonic)
register    the register verbatim (the negation) — short form: "This is a measurement
            credential. It is not a certification, endorsement, or conformity mark, and
            must not be presented as one."
```

A row is **honest** when `measured <= total` and the row's `kid` matches a key in the did:web
document below. A row with `measured = total` over-claims unless the registry genuinely has all
axes measured; the canon says the full 14-axis grid is "13 measured of 14" because the 14th
(the human baseline) is DPIA-gated / honest-unknown.

## Domain registries

The horizontal set the vertical verifies. Each is a registered axis set, namespaced
`csoai.gspc-domains/<domain>/<semver>`, committed in `axes/domains/`:

`bond` · `bank` · `insurance` · `equity` · `index` · `cross-border` · `operational` · `relative`
(the last two are operational/relative, not provision-mapped). `axes/gspc-16.json` holds the
16-axis absolute-governance grid (canon total 14 for the completeness grammar).

## did:web-signed update flow

**Trust root:** `did:web:csoai.org` resolves to `https://councilof.ai/.well-known/did.json`
(also served at `https://csoai.org/.well-known/did.json`, `200`). A stranger verifies a card
offline with the published Ed25519 key listed in that document.

### Active signing identities (the did:web key list)

| `kid` fragment (`#`) | Signs | Key held |
|---|---|---|
| `site-release-1` | site deploys, release cards, agent cards | keystone (site side) |
| `estate-chain-1` | fleet board chains + measurement cards | pod-held |
| `board-attestation-1` | board attestation | pod-held |
| `card-attestation-1` | the mine's measurement-card generation (added 2026-08-20) — the cards' actual signer, published so the card chain verifies against the trust root | Mac-held estate key |

`assertionMethod` = `[site-release-1, estate-chain-1, card-attestation-1]`; `authentication` =
`[site-release-1]`; `service` = `did:web:csoai.org#verifier` → `https://councilof.ai/verify`.

### The update flow (append-only, reversible-proof, never breaks the chain)

1. **New row appended, not rewritten.** Commit a new row to `measurements.jsonl`; it chains
   `prev -> prior row's hash`. Never edit a row in place; the content-address of a signed row
   makes tampering detectable.
2. **Sign, then publish.** A row is only `signed: true` after the public key in did.json verifies
   its signature. Unsealed (unsigned) rows are never signed and never claim production identity
   (`kid=test` only with `--allow-test-identity`).
3. **did:web key rotation is additive.** To rotate, **add** the new key to `verificationMethod`
   first (and its `assertionMethod`/`authentication` entries), publish the updated did.json, then
   sign new artifacts with it. Never delete a key that signed a live artifact mid-flight — a
   stranger must still be able to verify historical cards. Keys are retired via the
   `_keyContinuity.superseded` list (marked `superseded`, with `reason`), never removed.
4. **Key-continuity rule (binding).** Any artifact claiming a key that does not verify against
   an active identity, and is not in the live doc, is **not ours**. A key published from a
   generation script rather than the production signer is treated as superseded (see the
   `_keyContinuity` superseded entry in did.json).
5. **Service endpoints stay live.** `did.json` must not advertise a dead endpoint — removed
   2026-08-19 when the MCP worker returned 404; it returns in the commit that redeploys it.
6. **Provenance in the doc.** `_keyContinuity.note` + `_serviceNote` carry the binding notes so a
   stranger sees which key signed each artifact class.

### Verification path for a stranger

`card -> (Ed25519 sig, kid) -> did:web:csoai.org -> published key -> SCITT receipt (RFC 9943) ->
RFC 3161 anchor -> chain`. The CLI (`cli/dorado.py verify / verify-receipt / verify-anchor`)
and the engine (`engine/dorado_verify.py`, `dorado_receipt_verify.py`, `dorado_anchor_verify.py`)
implement this offline with only `cryptography` (+ `asn1crypto` for the anchor leg).

## Frozen verification vectors (registry-of-record entry, move 6)

The registry of record also indexes the estate's **pinned stranger-verification fixtures** —
FROZEN VECTORS v1. These are the canonical, hash-pinned inputs every verifier must still
accept (valid) and reject (bad-sig, bad-receipt) if the stranger-verification pipeline is
sound. They live in the repo, content-addressed by the manifest:

| Vector | File | Must | sha256 (pinned) |
|---|---|---|---|
| valid (card + receipt stranger-verify) | `test/vectors/card-valid.json` · `receipt-valid.json` | verify **ok** | `2819c817…` / `ae249654…` |
| bad-sig (card signature tampered) | `test/vectors/card-bad-sig.json` | fail **signature** | `9024fc6e…` |
| bad-receipt (receipt bound to a *different* card) | `test/vectors/receipt-bad.json` | fail **card-bind** | `3afa5c7a…` |

- The valid card's canonical digest `card_digest_sha256 = dc4aa02f6caad7bf65cdc0697dd0dfdb8d
  c8e1dae217444162561e4dcab5f8d9` is pinned in `test/vectors/FROZEN-VECTORS-MANIFEST.json`.
- All vectors use `kid = did:web:csoai.org#test-identity` (the fixed test key derived in
  `scripts/gen-frozen-vectors.py`) — **never** the production `#card-attestation-1` identity.
- Regeneration is deterministic: `python3 scripts/gen-frozen-vectors.py`; CI fails loudly on
  any drift (`test/frozen-vectors.py` → 8/8, `test/frozen-vectors-kit.py` → 12/12, which
  also stranger-verifies the frozen valid card+receipt through the **offline verify-kit**
  surface, move 17).
- A fixture is a *verification vector*, evidence of what the pipeline measures and when — it
  is a measurement device, never a certification, endorsement, or conformity mark.

## Maintenance notes

- `board-index.json` is regenerated from `measurements.jsonl` on publish; a `dirty` index is a
  signal, not a data change.
- This doc is the in-repo write-up for move 7. It records the flow; it does not change the
  live did.json or the register — any did.json change is a site deploy and is owner-gated.

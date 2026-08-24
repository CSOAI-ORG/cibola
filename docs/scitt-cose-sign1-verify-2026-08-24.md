# SCITT COSE_Sign1 cryptographic verify (NEXT-100 v4 move 31) — 2026-08-24

**Item:** count is not verify. The estate's board carries "201 COSE-wrapped SCITT
statements"; counting them proves nothing about whether any signature is cryptographically
sound. Move 31 turns **seen** into **proven** by adding a real RFC 9052 / RFC 9943
COSE_Sign1 verifier, stranger-only, no signing key, no pod, no network.

## What was shipped

- **`harness/scitt_verify.py`** — a deterministic COSE_Sign1 cryptographic verifier:
  - `decode_cose_sign1(envelope)` — decodes the CBOR tag-18 envelope (`cbor2`) and returns
    the protected/unprotected headers + payload + signature. Raises honestly on a
    non-COSE or malformed input.
  - `sig_structure(protected, payload, external_aad=b"")` — reconstructs the RFC 9052
    Sig_structure (`["Signature1", protected, external_aad, payload]`) and CBOR-encodes it;
    this is the exact byte string the Ed25519 signature must cover.
  - `verify_cose_sign1(envelope, *, expected_pubkey, expected_kid, permit_unpinned)` — the
    core decision: decode → read alg (must be -19 Ed25519) → recover the key → pin to a
    trusted identity → verify. Returns an honest, structured verdict; raises nothing.
  - `verify_signed_item(item)` / `verify_batch(items)` — per-item and batch verification
    that counts **verified / failed / unverifiable separately**, never folding a
    self-consistent-but-unpinned or absent envelope into the verified set.
  - `build_cose_sign1(payload, private_key, kid)` — builds an envelope; used ONLY for the
    hermetic fixture / `--fixture` selfcheck (test identity, never a production claim).
- **`test/scitt-verify.py`** — 27 hermetic checks (seeded key, fixed payload, no network):
  valid verifies; tampered payload / tampered signature / wrong caller-pinned key all
  rejected; a non-published kid is reported **"self-consistent but NOT pinned"** (never
  verified-authentic); permit_unpinned downgrades, never upgrades; batch split is exact;
  determinism across runs.
- **`cli/dorado.py scitt`** — verify one envelope file, a whole directory (`--dir`), or the
  `--fixture` selfcheck. `--pubkey` / `--kid` pin identity; `--json` emits machine-readable
  verdicts. Exit 0 only when every statement is cryptographically verified.
- Wired into `.github/workflows/ci.yml`; `cbor2` added as a declared permissive dep
  (`data/dependency-licence-manifest.json`, MIT) so the licence sweep stays landmine-free.

## The trust model (honest)

A COSE_Sign1 signature proves the signing key signed **this exact content**. To prove
**who** signed it, the key must be pinned to a trusted identity. The verifier pins to
either (a) a caller-supplied `expected_pubkey`, or (b) a published `did:web:csoai.org`
identity by `kid`. A statement whose key is not pinned is reported as **self-consistent but
NOT pinned** — the envelope is intact, but `ok=False` because authenticity is not proven.

## What it does NOT claim

Register (verbatim from canon): a verified COSE_Sign1 signature is evidence of what was
signed and when; it is a **measurement, never a certification**. Verifying a statement does
not certify its content, accredit the issuer, or endorse any model. The production
pod-key-signed statements remain to be batched once the pod signing-key ceremony runs
(described in the draft, never invoked from this repo) — that is a deployment step, not a
repo change.

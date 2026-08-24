# Offline stranger verify-kit + verification counter (NEXT-100 v4 move 17) — 2026-08-24

**Item:** a stranger can verify a DORADO measurement card **entirely offline** from one
self-contained artifact, and the estate records how many verification **events** it has
performed without ever claiming those counts prove validity.

## What was shipped

- **`harness/verify_kit.py`** — two surfaces:
  - **Verify-kit bundle** (`build_verify_kit`): packs a signed card, its receipt(s), its
    anchor, and the `did:web:csoai.org` public identity set into ONE deterministic JSON
    artifact, each part bound by `content_sha256`, plus a plain offline walkthrough and the
    honest register. The bundle carries a `digest` (RFC 8785 canonical form minus the
    digest/kit_id fields) and a `kit_id`, both reproducible across runs when `generated_at`
    is pinned.
  - **Offline whole-kit verify** (`verify_verify_kit`): verifies the kit with no network, no
    pod, only `cryptography` — integrity (digest), card signature (`verify_card`), receipt
    bind (`verify_receipt`), anchor imprint (`verify_anchor`), and **identity pin**
    (`_identity_pin`). Returns per-part verdicts + an aggregate honest verdict.
  - **Verification counter** (`record_verification` / `verification_counter`): an
    append-only, content-addressed ledger (`data/verify-log.jsonl`) of verification events.
- **`test/verify-kit.py`** — 28 hermetic checks (seeded key, pinned `issued_at`, no network):
  kit packs all parts; digest self-consistent + deterministic; whole kit verifies offline
  against a caller-trusted identity; tampered card / swapped subject / missing receipt all
  fail honestly; the identity pin is labelled **caller-trusted** vs **kit-bundled** so a
  self-bundled key set is never mistaken for an independently-fetched `did:web`
  authentication; the counter is time-ordered, hash-addressed, and honest (usage, never
  validity).
- **`cli/dorado.py verify-kit`** — build (`--card`/`--receipt`/`--anchor` → `--out`),
  verify offline (`--in`), report the counter (`--counter`), or `--fixture` selfcheck.
  `--pubkey` supplies the caller-trusted identity set for authentication.
- Wired into `.github/workflows/ci.yml`; `verify_kit` registered as estate-internal in the
  licence sweep.

## The trust model (honest)

A bundle is convenient, but a stranger must not trust keys **shipped with** the artifact for
authenticity — a malicious bundle could ship the attacker's keys. `verify_verify_kit` takes an
optional `trusted_keys` set (what a stranger holds independently from `did:web`); when given,
the verdict is labelled **caller-trusted** and that is the real authentication pin. With no
`trusted_keys`, it falls back to the kit-bundled keys and labels the pin **kit-bundled**,
reporting the mechanism verified but the identity **not independently fetched from `did:web`**.

## What it does NOT claim

Register (verbatim from canon): a verify-kit is a measurement device, never a certification.
The **counter** counts verification events (usage / coverage / provenance), never that any
model is certified or any result was validated. A stranger's own offline verification is
counted only if that stranger records it; the counter never asserts anyone-world verified
anything.

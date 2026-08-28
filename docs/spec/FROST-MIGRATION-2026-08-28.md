# FROST-ED25519 MIGRATION — research + scaffold (roadmap item 3) · 2026-08-28

## The problem (honest)
Today's "3-of-3 MPC" is three shares on ONE machine = a single failure domain. A compromise of
that machine compromises the signing identity — the estate's single point of catastrophic failure
(Risk 4 in the Black Swan plan).

## The fix (researched)
- **FROST (Flexible Round-Optimized Schnorr Threshold)** for Ed25519 — `taurushq-io/frost` (or
  `ZcashFoundation/frost`) — threshold signatures (t-of-n) where NO party ever holds the full key.
- **Critical property**: FROST emits a **STANDARD Ed25519 signature** — the pinned DID key,
  every published verifier, the 313-card index, verify-card.mjs, dorado verify — all stay
  UNCHANGED. Only the signing side changes (shares instead of a single key).
- **Shares in distinct trust domains** (pod + Oracle micro + one hardware/non-network location) —
  t-of-n (e.g., 2-of-3) survives single-domain compromise.

## Migration plan (agent-doable research → lane co-sign)
1. Pin the FROST crate/lib + license row (MIT/Apache) into the absorption manifest.
2. Key-ceremony v2: generate shares on separate machines, never assemble the full key on one host.
3. Write the did:web rotation runbook FIRST (below) — before any compromise.
4. Pod sign path: replace single-key load with a FROST signing service (the keystone lane's window).
5. Test: FROST signature == single-key signature under the SAME pubkey (the invariant test).

## Do-NOT (roadmap list)
- No Sigstore keyless/Fulcio (our value = a stable pinned DID key, not short-lived identities).

## Files
- This note (research) · `docs/spec/DID-ROTATION-RUNBOOK-2026-08-28.md` (the prerequisite runbook)

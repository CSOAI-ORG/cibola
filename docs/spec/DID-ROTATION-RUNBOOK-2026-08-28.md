# DID:WEB KEY ROTATION RUNBOOK — kid + overlap window (before any compromise) · 2026-08-28

**Rule: write this BEFORE a compromise, not after. Rotation is ledger-recorded, never silent.**

## The invariant
Old cards stay verifiable forever (Ed25519 signatures are self-contained); rotation only affects
who is AUTHORIZED to issue NEW cards. did:web:csoai.org holds 4 published keys; cards pin
#card-attestation-1.

## Procedure
1. **Generate** the new keypair on the signing pod (or FROST shares per the migration note).
2. **Publish** the new key to did:web (add key #N+1; keep #card-attestation-1 in the doc during
   overlap) — 3 resolvers must agree.
3. **Overlap window**: ≥14 days (longer for a suspected compromise). BOTH keys verify during the
   overlap; the new key is kid #card-attestation-2.
4. **Re-point issuance** to the new kid (board-attestation-2, card-attestation-2).
5. **Record in the append-only corrections ledger**: old_kid → new_kid + reason + timestamp,
   signed. Strangers verify both survive.
6. **Retire** the old key from the did:web doc (keep the record; never delete the ledger entry).
7. **Post-rotation audit**: 150-index cards + every card issued in the last 7 days verify under
   the OLD key; new cards under the NEW key; the ledger entry verifies.

## Compromise mode (same procedure, compressed)
- Overlap window = 24h; revoke the compromised key from did:web FIRST; publish the ledger entry
  with the compromise declared (the anti-fragile turn: transparency beats a silent failure);
  multi-rail anchoring (OTS + SCITT) means past proofs stay verifiable even if the key was bad.

## Tests (add to the CI gate)
- A card signed under the old key verifies after rotation (stranger path).
- did:web resolves the new key on 3 resolvers.
- The ledger rotation entry verifies.

# DUAL-TS CROSS-VERIFY MATRIX — prep scaffold (move 4) · staged 2026-08-25

**Status:** PREP ONLY. The genesis card is production-signed (kid=card-attestation-1, 6/6 domains) — the remaining leg is **registering it in a second independent transparency service** (capsule-anchor pattern) + cross-verify matrix in CI. Registration of the card into TS#2 is an infrastructure/key-ceremony action — staged here, not executed.

## Matrix spec (CI-ready once registered)
```
matrix: [{card, tsA: receiptA, tsB: receiptB}]
checks: 1. receiptA verifies vs tsA keyset (offline)
        2. receiptB verifies vs tsB keyset (offline)
        3. both receipts cover the same statement digest (payload equality)
        4. receiptA+B differ (two independent registrations, not a mirror)
        5. kid resolves via did:web on 3 independent resolvers
```
- Fail-closed: any check UNKNOWN → matrix RED (never partial-green).
- Register-policy: deterministic, auditor-replayable; MMD 24h target; rate-limit policy noted.
- Retired-key retention: keys retired never deleted; historical receipts remain verifiable.

## TS#2 candidate notes (verify at execution)
- Second independent TS operator from the IETF SCITT community (AAC/Veraison/EMILIA-adjacent — cross-verification culture is warm; peer relationship, never infrastructure of record)
- Peer-TS coordination note + cross-verification offer drafted in sprint; send is external-comms gated.

*End.*

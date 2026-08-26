# Truth layer — OpenTimestamps (Bitcoin-anchored)

Every artifact below has a `.ots` proof committed next to it. A stranger verifies
WITHOUT trusting us: `ots verify <sha256hex> <proof.ots>` (or the web verifier at
opentimestamps.org). The proof binds *existence at time T* to the Bitcoin blockchain
— the permanence layer UNDER our Ed25519 signature + SCITT (RFC 9943) receipt +
RFC 3161 anchor. Move 8 of the 2026 Playbook: PLANNED → LIVE, 2026-08-26.

- card_index head (150-card signed board) — anchored 26 Aug 2026
- live /api/gspc board payload sha256 — anchored 26 Aug 2026
- Next: anchor every production-signed card at mint time (hook in the carder pipeline).

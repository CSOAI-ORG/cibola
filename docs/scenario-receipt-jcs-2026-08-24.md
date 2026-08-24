# Scenario receipt — JCS payload-binding stranger-verify (2026-08-24)

**Move:** 43 · **Status:** DONE · **Canon hook:** signed-only ratings; SCITT (RFC 9943); Ed25519; stranger-verifiable artifacts; non-repudiable evidence of *what* was recorded and *when* (never proof the source is honest — measurement, never certification).

## What this is
The estate's serious-incident (Art 73) and post-market-monitoring (Art 72) feeds emit
**signed scenario receipts** — the ASRS / FAA-91.25 structure the estate claims. A scenario
receipt binds the **RFC 8785 JSON Canonicalization Scheme** form of an **arbitrary** prompt /
probe / refusal / incident record to an issuer at a time. A stranger verifies it with ONLY
the receipt + `cryptography` — no signing key, no pod.

## What landed
- **`engine/dorado_receipt.py` → `build_scenario_receipt(payload, …)`** — generic JCS
  payload-binding counterpart to `build_card_receipt`. Canonicalizes the payload with
  `jcs()` (RFC 8785), binds `subject_content_sha256 = sha256(jcs(payload))`, sets
  `kind: "scenario"`, and attests the *digest* (never embeds the full payload — it may be
  large or partly secret). Fully build+sign parity with the card receipt.
- **`engine/dorado_receipt_verify.py` → `verify_scenario_receipt(receipt, payload)`** —
  stranger verifier. Reuses a shared `_verify_core` (content_id + Ed25519 sig), then
  cross-checks the JCS payload digest. `verify_receipt(card)` unchanged (backward-compatible).
- **`test/scenario-receipt.py`** — hermetic guard proving the round-trip, JCS
  key-order-independent binding, different-payload-*not*-bound, tamper/unsigned refused,
  and that scenario vs measurement-card receipts are NOT cross-confusable (kind mismatch).
  Wired into CI.

## Why it matters
This is the mechanism that makes the Art 73 incident feed and the AIP/agent-protocol
scenario evidence stranger-checkable and immutable. A JCS-bound digest means the same
scenario re-read with re-ordered fields still binds identically — cross-language, cross-tool.
The honesty corollary (from the ART50 offer) holds: we record OUR scenario reads and sign
them; the receipt is evidence of *what* was recorded and *when*, not a verdict on the source.

*Move 43 complete. Scenario receipts are now JCS payload-binding and stranger-verifiable,
frozen by a hermetic CI guard.*

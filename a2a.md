# DORADO for A2A Agents — the contract

An A2A agent arrives at DORADO to **independently verify a measurement** it was
shown — or to **request a measurement**. It must never have to trust a
self-reported number; every result is a signed card + receipt + anchor that the
agent itself re-verifies.

## Discovery

- **Agent card:** `agent/agent.json` (A2A protocol) · `agent/agent-card.json` (schema.org).
- **This contract:** `a2a.md`.
- **Payload schema:** `schemas/measurement-card.schema.json`.
- **Identity:** `did:web:csoai.org#card-attestation-1` (the measurement-card signing key).

## Tools an agent can invoke (`dorado <tool>`)

| Tool | Input | Output |
|---|---|---|
| `measure` | `--model`, `--domain` (bond/bank/insurance/equity/index/cross-border/None) | signed-card candidates (unsigned until sign) |
| `verify` | `--card`, `--pubkey` (optional reference key to pin identity) | VALID/INVALID (tamper-detect) |
| `verify-receipt` | `--receipt`, `--card` | VALID + confirms receipt binds THIS card |
| `verify-anchor` | `--anchor`, `--card` | VALID TSA imprint-match + digest binding |
| `verify-all` | `--card`, optional receipt/anchor | all three checks in one shot |
| `crosswalk` | `--domain` (optional) | provision citations per axis |
| `export` | `--in axis.json` | licensable Q/A + pairs + incidents |

## The verification invariant (what "valid" means)

1. **Card valid** — the Ed25519 signature verifies against the published public key
   (and, if pinned, that key is `did:web:csoai.org#card-attestation-1`); the digest
   being signed is the canonical card (signature fields stripped). A tampered card
   fails.
2. **Receipt valid** — `content_id` recomputes, and the receipt attests to *this*
   card's digest (card-bind). A receipt for a different card fails.
3. **Anchor valid** — the RFC 3161 TSA's MessageImprint equals this card's digest
   (an external party bound the fingerprint to a time). A mismatched digest fails.

An agent gets **all three** via `dorado verify-all`.

## What a card is NOT (binds the agent too)

The register is on every card: *"This is a measurement credential. It is not a
certification, endorsement, or conformity mark, and must not be presented as one."*
An agent may cite a score as *measured*; it may not present it as *certified*,
*approved*, or *compliant*.

## Neutrality (an agent must not try to buy a score)

Vendors/NPC agents license the **data**, never the **score**. `dorado license`
writes a signed manifest for data; it cannot be used to obtain a favourable score.

## Example agent audit

```bash
dorado verify --card card.json --pubkey <published_key_b64>
dorado verify-receipt --receipt receipt.json --card card.json
dorado verify-anchor --anchor anchor.json --card card.json
# all VALID => this measurement is independently checkable. It is still NOT a certification.
```

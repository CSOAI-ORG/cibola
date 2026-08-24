# DORADO — a measurement body (never a certifier)

An independent AI-governance **measurement** body. A signed score layer over the
RFC 9943 substrate (RFC 9942 receipts). **Measurement, never certification** — a
measurement card is NOT a certification, endorsement, or conformity mark.

- Legal: CSOAI Ltd (Council of AI), UK Companies House 16939677. did:web:csoai.org.
- Neutrality: the scored entity never pays for its measurement; a vendor can buy
  the data (Q/A, relative pairs, operational telemetry), never a score.

> **Naming split (2026-08-24, decision log 001).** **CIBOLA** is the public protocol
> name (`application/vnd.cibola.measurement-card+json` planned) and the GitHub repo
> name, `CSOAI-ORG/cibola` — the repo is intentionally **not** renamed. **DORADO** is
> the internal monorepo codename used in code and internal docs. **Council of AI**
> (CSOAI Ltd, UK 16939677) is the body brand. Public-facing text should use *CIBOLA*
> and the *measurement credential / verified measurement credential* grammar; internal
> code may keep the DORADO codename. The two are kept explicitly separate — never conflated.

## Verify in 60 seconds (from a cold clone)

```bash
# 1. clone
git clone https://github.com/CSOAI-ORG/cibola.git dorado && cd dorado
pip install cryptography asn1crypto

# 2. run the hermetic test battery (proves the engine is sound, no network)
python3 test/battery.py && python3 test/elo-test.py

# 3. verify a published measurement card + receipt + RFC3161 anchor end-to-end
python3 cli/dorado.py verify-receipt \
  --receipt assets/example-verify-receipt.json --card assets/example-verify-card.json
python3 cli/dorado.py verify-anchor \
  --anchor assets/example-verify-anchor.json --card assets/example-verify-card.json

# 4. stranger-verify a signed card with only the published key + cryptography
python3 cli/dorado.py verify --card assets/example-verify-card.json
```

A stranger verifies a card/receipt/anchor **offline** with only the published
Ed25519 key + `cryptography`. The anchor leg also needs `pip install asn1crypto`.

## What the stack measures

| Axis | What | Output |
|---|---|---|
| **Absolute governance** (16-axis + 6 domains) | deterministic gold-label judgment | signed card |
| **Relative** (blind A/B) | which model is safer/more aligned/fairer | Elo/Bradley-Terry + CI |
| **Operational** (cost/latency/throughput) | the half OpenRouter throws away | telemetry.jsonl |

## Live measurement pipeline

```
measure → sign (Ed25519 COSE_Sign1) → SCITT receipt → RFC 3161 anchor → publish → board
```

The board (`board/board-index.json`, content-addressed, append-only) records every
signed + anchored measurement. It is a **measurement registry, not a rank table.**

## Run the pods

All work runs OFF the Mac. On the 3090 pod (`ssh sov-brain-2`):

```bash
cd /workspace/dorado
MODEL=qwen3:4b-8k DOMAINS="bond bank insurance equity index cross-border" CONC=1 \
  bash scripts/eat-batch.sh        # full MINE→MINT→CHAIN→PUBLISH per domain, real inference
COST_BUDGET_USD=1.0 bash scripts/eat-batch.sh   # fail-open cost cap
```

## Explore

- `dorado status` — consolidated live-endpoint payload (board + relative + operational + identity).
- `dorado openrouter --search qwen` — probe the OpenRouter model universe.
- `dorado elo --pairs pairs.json` — rank models (Elo/Bradley-Terry + CI).
- `dorado board`, `dorado telemetry`, `dorado export-relative`, `dorado export-operational`.
- A2A/MCP: `agent/mcp_server.py` + `.well-known/agent.json` + `.well-known/mcp.json`.

## Register (verbatim)

> "This is a measurement credential. It is not a certification, endorsement, or
> conformity mark, and must not be presented as one."

## Doctrine (binding)

- **Measurement, never certification.** The register is on every card.
- **One-signer identity gate.** A non-published key never claims the production
  identity; it is stamped `kid=test` (only with `--allow-test-identity`).
- **Join on weights, not names.** A model NAME is not a model — the card carries a
  measured-evidence digest.
- **Neutrality.** A vendor can buy the data; never the score. Board-clobber guard
  protects the authoritative record.

License: code Apache-2.0 · spec text Community Specification License 1.0.

# Dependency licence landmine sweep (2026-08-24)

**Move:** 34 · **Status:** SWEEP DONE (clean) · **Canon hook:** buyer-side money only; "a vendor can license the telemetry; never the score"; no lab-free-tokens; never drag the instrument into a licence the buyer cannot accept.

## The rule
A new dependency is admissible only if it is **permissive** (BSD/MIT/Apache/ISC/Zlib/PSF
family) **and** not in a **hard-excluded** commercial/non-commercial agent-dataset family.
Anything outside the permissive allowlist escalates; it is never silently adopted.

## Hard-excluded families (never adopt — a landmine)
`PersonaHub` · `genagents` · `AgentSociety-commercial` · `Genie 3` · `Cosmos`

These are agent-persona / synthetic-dataset / world-model licences whose terms are
non-commercial or otherwise restrict the measured data's licence — exactly the class that
would break "license the measured data, never the score."

## Third-party dependencies in use (sweep result: CLEAN)
| Dependency | Provider | SPDX | Verdict | Where |
|---|---|---|---|---|
| `cryptography` | PyCA | Apache-2.0 OR BSD-3-Clause | OK | signing/verify/receipt/anchor (`dorado_sign`, `dorado_verify`, `dorado_receipt*`, `dorado_anchor*`, `cli/dorado.py`) |
| `asn1crypto` | PyCA | MIT | OK | conditional RFC 3161 TSA + ASN.1 (`dorado_anchor.py`, `dorado_anchor_verify.py`) |

Both are PyCA (Python Cryptographic Authority) — permissive, no copyleft, no restriction on
licensing the measured data. **No hard-excluded family appears in any code/data asset.**

## Internal (estate-owned, not an external licence surface)
| Package | Verdict | Note |
|---|---|---|
| `csoai_city` | INTERNAL | Estate's own package (CSOAI), licensed Apache-2.0 by the estate; not a third-party dep. |

## Guard
`test/licence-sweep.py` — hermetic CI guard:
- Every third-party module imported by the estate's code is **declared** in
  `data/dependency-licence-manifest.json` with a **permissive** SPDX verdict; an undeclared
  or non-permissive third-party import is a **hard fail**.
- **No hard-excluded family name** may appear in any code/data asset
  (`engine`/`harness`/`agent`/`test`/`cli`/`scripts`/`data`) — a landmine cannot silently
  enter a probe, persona, dataset or model reference. `docs/` is deliberately exempt (the
  rule is documented by naming the families), as is the manifest + guard (the rule text).

*Move 34 complete. Only permissive PyCA deps (cryptography, asn1crypto); zero hard-excluded
family presence; landmine sweep is now CI-guarded.*

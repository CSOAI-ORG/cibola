# COSE RECEIPTS (RFC 9942) — scaffold + omission-gap framing (move 3) · 2026-08-28

**Purpose:** the linear hash chain CANNOT detect omission inside a withheld run — stop claiming
otherwise anywhere (roadmap item 2 honesty). COSE Receipts (RFC 9942) + SCRAPI give inclusion
proofs. This scaffold = the receipt shape + a fixture generator + the honest framing.

## The honest gap (verbatim, goes into every doc that mentions chain integrity)
> "The linear hash chain proves what we published; it cannot prove we published everything. A
> withheld run inside a batch is invisible to the chain. Merkle inclusion (COSE Receipts / SCITT)
> fixes the inclusion half; it still cannot prove completeness — subjects must retain their own
> receipts. We never oversell."

## Receipt shape (RFC 9942 / SCRAPI, COSE_Sign1-style)
```json
{"schema": "csoai.cose-receipt/0.1",
 "receipt_version": 1,
 "statement": {"content_id": "sha256 of the statement bytes (hex)"},
 "transparency_service": {"id": "did:web:csoai.org#ts-1", "log": "csoai-ledger-1"},
 "inclusion": {"tree_id": "T1", "index": 42, "root": "merkle root hash (hex)",
               "proof": "inclusion proof path (hex)"},
 "signed": {"alg": -19, "kid": "did:web:csoai.org#ts-1",
            "sig": "COSE_Sign1 signature over the tree head + index + hash (b64)"},
 "ts": "RFC 3161 imprint of the signed tree head (b64)"}
```

## Fixture generator (deterministic, hermetic — no network)
```python
# harness/cose_receipts/fixture.py
import hashlib, json, base64
def make_fixture(statements: list[bytes], index: int = 42) -> dict:
    """Build a minimal inclusion receipt over a statement list (Merkle path computed
    in-repo for testing; production uses Trillian-Tessera or Rekor)."""
    hashes = [hashlib.sha256(s).digest() for s in statements]
    # simple pair-hash tree for the fixture; production = real transparency log
    def merkle(leaves):  # binary reduction, deterministic
        while len(leaves) > 1:
            leaves = [hashlib.sha256(leaves[i] + leaves[i+1]).digest()
                      for i in range(0, len(leaves)-1, 2)] or [leaves[0]]
        return leaves[0]
    root = merkle(hashes)
    return {"schema": "csoai.cose-receipt/0.1", "statement_count": len(statements),
            "root": root.hex(), "fixture": True,
            "note": "fixture only — production receipts come from a real transparency log"}
```

## Next (agent, no gate)
1. Wire the fixture into the carder as an optional receipt attachment (card + receipt bundle).
2. Trillian-Tessera vs Rekor decision note (self-host vs anchor; roadmap item 4).
3. The honest-gap sentence into the site's chain/verify docs (lane co-sign).

## Files
- `harness/cose_receipts/fixture.py` (this round) · `docs/spec/COSE-RECEIPT-SHAPE.md` (this file)

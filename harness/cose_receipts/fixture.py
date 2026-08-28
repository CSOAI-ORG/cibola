#!/usr/bin/env python3
"""fixture.py — deterministic hermetic COSE-receipt fixture (RFC 9942 shape).

Production receipts come from a real transparency log (Trillian-Tessera / Rekor);
this fixture proves the receipt SHAPE + the honest omission-gap framing in-repo.
"""
import hashlib


def merkle_root(leaves):
    """Binary pair-hash Merkle root (deterministic; production uses a real log)."""
    while len(leaves) > 1:
        leaves = [hashlib.sha256(leaves[i] + leaves[i + 1]).digest()
                  for i in range(0, len(leaves) - 1, 2)] or [leaves[0]]
    return leaves[0]


def make_fixture(statements, index=42, tree_id="T1"):
    hashes = [hashlib.sha256(s).digest() for s in statements]
    root = merkle_root(hashes)
    return {
        "schema": "csoai.cose-receipt/0.1",
        "receipt_version": 1,
        "statement_count": len(statements),
        "inclusion": {"tree_id": tree_id, "index": index, "root": root.hex()},
        "fixture": True,
        "note": "fixture only — production receipts come from a real transparency log. "
                "Merkle inclusion != completeness: subjects must retain their own receipts.",
    }


if __name__ == "__main__":
    stmts = [b'{"card":"abc","score":0.5}', b'{"card":"def","score":0.7}', b'{"card":"ghi","score":0.9}']
    import json
    print(json.dumps(make_fixture(stmts), indent=1))

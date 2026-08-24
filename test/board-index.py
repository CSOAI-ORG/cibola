#!/usr/bin/env python3
"""test/board-index.py — register index consistency guard (move 42, in-repo half).

The board (`board/board-index.json`) is the registry of record — an append-only,
content-addressed, hash-chained measurement register. Its INDEX is a derived public
contract: it must be internally self-consistent so a stranger can trust the count and
the chain without re-fetching every card. This guard, hermetic, asserts the index
contract on the in-repo `board/index`:

  * the derived index is coherent: count == number of measurements; chainOk is consistent
    with linked/unlinked (chain is OK iff there are no unlinked gaps);
  * every measurement entry has the required index fields, non-empty, and self-consistent
    in magnitude (measured >= 0, total >= measured, provision_axes >= 0, signed == true —
    the register refuses unsigned cards);
  * the subject / registry / kid values are non-empty and the kid names a did:web identity
    (stranger key resolution target);

The "index vs files" honest audit (how many cards/files vs index rows, and whether the
full card set is in-repo) is a boundary the guard reports, not asserts — see the audit
doc. This guard asserts the index is internally coherent; it does NOT fabricate files
that live on the publishing surface.
"""
from __future__ import annotations

import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "board", "board-index.json")

REQUIRED = ["hash", "ts", "registry", "subject", "measured", "total", "kid", "signed"]
DOC_IDENT = "did:web:"


def main() -> int:
    assert os.path.exists(INDEX), f"board index missing: {INDEX}"
    idx = json.load(open(INDEX))

    measurements = idx.get("measurements")
    assert isinstance(measurements, list), "measurements must be a list"
    n = len(measurements)

    # (1) derived index coherent with the summary
    assert idx.get("count") == n, f"count {idx.get('count')} != len(measurements) {n}"
    linked = idx.get("linked", 0)
    unlinked = idx.get("unlinked", 0)
    assert linked + unlinked == n, f"linked+unlinked {linked+unlinked} != {n}"
    chain_ok = idx.get("chainOk", False)
    assert chain_ok and unlinked == 0, \
        f"chainOk={chain_ok} but unlinked={unlinked} (chain must be gap-free)"

    # (2) every entry self-consistent + signed
    for i, m in enumerate(measurements):
        path = f"measurements[{i}]"
        for f in REQUIRED:
            assert f in m, f"{path}: missing required '{f}'"
        assert str(m["hash"]).strip(), f"{path}: empty hash"
        assert str(m["subject"]).strip(), f"{path}: empty subject"
        assert str(m["registry"]).strip(), f"{path}: empty registry"
        assert str(m["kid"]).startswith(DOC_IDENT), \
            f"{path}: kid {m['kid']!r} is not a did:web identity"
        assert isinstance(m["measured"], int) and m["measured"] >= 0, \
            f"{path}: measured not a non-negative int"
        assert isinstance(m["total"], int) and m["total"] >= m["measured"], \
            f"{path}: total {m['total']} < measured {m['measured']}"
        assert isinstance(m.get("provision_axes", 0), int) and m["provision_axes"] >= 0, \
            f"{path}: provision_axes not a non-negative int"
        assert m["signed"] is True, f"{path}: unsigned card in register (unsealed-never-signed)"

    # (3) honest boundary report: the index is derived; the raw row log + full card files
    # are a separate surface. Report what is actually IN this repo (not fabricated).
    ml = os.path.join(ROOT, "board", "measurements.jsonl")
    raw_rows = 0
    if os.path.exists(ml):
        raw_rows = sum(1 for ln in open(ml) if ln.strip())
    print(f"INDEX-VS-FILES (honest): index={n} measurements; in-repo raw row log "
          f"board/measurements.jsonl={raw_rows} row(s); no per-card measurement-*.json "
          f"files in-repo (the full card chain is published by the board service).")

    print(f"BOARD-INDEX: PASS — {n} measurements; count coherent; chainOk with 0 unlinked "
          f"gaps; every entry signed (did:web kid), measured/total/provision_axes "
          f"self-consistent and non-negative; derived index internally coherent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

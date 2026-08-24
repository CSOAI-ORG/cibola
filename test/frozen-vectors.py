#!/usr/bin/env python3
"""test/frozen-vectors.py — validate the pinned FROZEN VECTORS v1 (move 6).

Herd the pipeline: if the canonical form, card builder, or signer changes, the
content hash of a fixture must NOT match the manifest, and CI fails loudly rather
than silently accepting a drifted "valid" card.

Checks, all hermetic (no Ollama, no network, no production key):
  1. Hash-pin: each committed vector file's sha256 equals the manifest's recorded hash.
     (A canonical-form drift is caught here — the pin breaks.)
  2. Determinism: the card's canonical digest recomputes to the manifest's card_digest_sha256.
  3. Behaviour:  card-valid verifies (ok), card-bad-sig fails (signature tamper),
     receipt-valid binds card-valid (ok), receipt-bad fails (bound to a different card).

Exit 0 if all green; non-zero otherwise.
"""
from __future__ import annotations

import base64, hashlib, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTORS_DIR = os.path.join(ROOT, "test", "vectors")
sys.path.insert(0, os.path.join(ROOT, "engine"))

from dorado_verify import verify_card  # noqa: E402
from dorado_receipt_verify import verify_receipt  # noqa: E402
from dorado_sign import canonical as card_canonical  # noqa: E402

MANIFEST_PATH = os.path.join(VECTORS_DIR, "FROZEN-VECTORS-MANIFEST.json")


def _sha256_file(rel: str) -> str:
    with open(os.path.join(VECTORS_DIR, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _load(rel: str) -> dict:
    return json.load(open(os.path.join(VECTORS_DIR, rel), encoding="utf-8"))


def main() -> int:
    m = json.load(open(MANIFEST_PATH, encoding="utf-8"))
    failures = []

    def _check(cond: bool, msg: str):
        print(("PASS " if cond else "FAIL ") + msg)
        if not cond:
            failures.append(msg)

    print("FROZEN VECTORS v1 (hash-pinned)")

    # 1. hash-pin each committed vector file against the manifest
    for key in ("card_valid", "card_bad_sig", "receipt_valid", "receipt_bad"):
        entry = m["vectors"][key]
        actual = _sha256_file(entry["file"])
        _check(actual == entry["sha256"],
               f"pin {entry['file']} = {actual[:16]}… (expected {entry['sha256'][:16]}…)")

    # 2. determinism — the valid card's canonical digest recomputes to the pinned one
    card_valid = _load(m["vectors"]["card_valid"]["file"])
    recomputed_digest = hashlib.sha256(card_canonical(card_valid)).hexdigest()
    _check(recomputed_digest == m["card_digest_sha256"],
           f"card canonical digest stable = {recomputed_digest[:16]}…")

    # 3. behaviour — every vector does what it must
    bad_sig = _load(m["vectors"]["card_bad_sig"]["file"])
    receipt_valid = _load(m["vectors"]["receipt_valid"]["file"])
    receipt_bad = _load(m["vectors"]["receipt_bad"]["file"])

    rv = verify_card(card_valid)
    _check(rv["ok"] is True,
           f"card-valid stranger-verifies (kid={rv.get('kid')})")
    _check(rv.get("kid") == "did:web:csoai.org#test-identity",
           "card-valid is stamped kid=test (never the production identity)")

    rs = verify_card(bad_sig)
    _check(rs["ok"] is False and "INVALID" in rs.get("reason", ""),
           f"card-bad-sig FAILS signature verification ({rs.get('reason')})")

    rr_ok = verify_receipt(receipt_valid, card_valid)
    _check(rr_ok["ok"] is True, f"receipt-valid binds card-valid ({rr_ok.get('reason')})")

    rr_bad = verify_receipt(receipt_bad, card_valid)
    _check(rr_bad["ok"] is False and "does NOT attest" in rr_bad.get("reason", ""),
           f"receipt-bad FAILS card-bind ({rr_bad.get('reason')})")

    # register grammar — the binding canon must be verbatim on the valid card
    _check(card_valid.get("credential_register") == m["register"],
           "card-valid carries the verbatim measurement-not-certification register")

    if failures:
        print(f"FROZEN-VECTORS: FAIL — {len(failures)} check(s) failed")
        return 1
    print("FROZEN-VECTORS: PASS — 8/8 hash-pinned checks green")
    return 0


if __name__ == "__main__":
    sys.exit(main())

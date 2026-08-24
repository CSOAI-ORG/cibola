#!/usr/bin/env python3
"""gen-frozen-vectors.py — deterministic "frozen vector" fixtures for DORADO cards.

FROZEN VECTORS v1 (NEXT-100-v4 move 6). The estate's stranger-verification pipeline
must be pinned: if the canonical form, the card builder, or the signer changes, the
vector digest changes and CI fails loudly instead of silently accepting a drifted
"valid" card. This script REGENERATES the fixtures + their content-hash manifest.

Each vector is fully deterministic (no Ollama, no network, no wall-clock timestamp):
  * a fixed test Ed25519 key (derived from a constant seed, never the production key),
  * a fixed card `issued_at` constant,
  * the canonical 16-axis GSPC measurement result from axes/gspc-16.json.

Three vectors are produced:
  * valid   — card + receipt that both stranger-verify (the happy path),
  * bad-sig — the card's signature field is tampered → signature must FAIL,
  * bad-receipt — a receipt bound to a DIFFERENT card's digest → card-bind must FAIL.

Regenerate with:  python3 scripts/gen-frozen-vectors.py
The generated JSON + manifest are committed; test/frozen-vectors.py validates them.
"""
from __future__ import annotations

import base64, hashlib, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
sys.path.insert(0, os.path.join(ROOT, "harness"))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402
from cryptography.hazmat.primitives import serialization as _ser  # noqa: E402

from dorado_sign import sign as sign_card, canonical as card_canonical  # noqa: E402
from dorado_sign import rfc9679_thumbprint  # noqa: E402
from dorado_receipt import build_card_receipt, canonical as receipt_canonical  # noqa: E402
from dorado_receipt import content_id as receipt_content_id  # noqa: E402
from run_axis import as_card, load_axes  # noqa: E402

VECTORS_DIR = os.path.join(ROOT, "test", "vectors")
MANIFEST_PATH = os.path.join(VECTORS_DIR, "FROZEN-VECTORS-MANIFEST.json")

# Fixed, deterministic test signing key (32-byte seed -> Ed25519). NEVER the
# production #card-attestation-1 key; the card is hence stamped kid=test.
_SEED = hashlib.sha256(b"csoai-frozen-vectors-v1:test-seed").digest()
KEY = Ed25519PrivateKey.from_private_bytes(_SEED)

# A fixed card instantiator so the vectors do not depend on the wall clock.
FIXED_TS = "2026-08-24T00:00:00Z"
SUBJECT = {"id": "frozen-vector-subject", "name": "frozen-vector-model", "digest": "fixed"}
REGISTER = ("This is a measurement credential. It is not a certification, endorsement, "
            "or conformity mark, and must not be presented as one.")


def _fake_result() -> dict:
    """A deterministic 16-axis result that never touches the network."""
    axes, _ = load_axes(None)
    per_axis = []
    for i, a in enumerate(axes):
        per_axis.append({"axis": a["slug"], "gold": a["gold"],
                         "verdict": "PASS" if i < 9 else "FAIL",
                         "resp": "deterministic", "measured": True})
    return {"model": "frozen-vector-model", "n": len(axes), "ok": 9,
            "accuracy": 0.562, "measured": len(axes), "total": len(axes),
            "ts": FIXED_TS, "registry": "csoai.gspc-16", "per_axis": per_axis}


def _deterministic_receipt(card: dict, *, bound_issuer: bool = True) -> dict:
    """Build a receipt for `card` with a FROZEN timestamp + re-derived content_id/signature.

    `bound_issuer` is True for the valid vector; when False, a different subject id is
    injected so the receipt is bound to a DIFFERENT card's digest (card-bind must fail).
    """
    if not bound_issuer:
        card = json.loads(json.dumps(card))
        card["subject"]["id"] = "some-other-subject"
    receipt = build_card_receipt(card, private_key=KEY, kid="did:web:csoai.org#test-identity")
    receipt["issued_at"] = FIXED_TS
    receipt.pop("content_id", None)
    receipt.pop("signature", None)
    rect_id = receipt_content_id(receipt)
    receipt["content_id"] = rect_id
    pubkey_raw = KEY.public_key().public_bytes(
        encoding=_ser.Encoding.Raw, format=_ser.PublicFormat.Raw)
    sig = KEY.sign(receipt_canonical(receipt))
    receipt["signature"] = {
        "alg": "Ed25519", "kid": receipt["kid"],
        "pubkey": base64.b64encode(pubkey_raw).decode(),
        "sig": base64.b64encode(sig).decode(),
        "pubkey_thumbprint": rfc9679_thumbprint(pubkey_raw),
        "sig_input": "ed25519(canonical receipt minus content_id/signature)",
    }
    return receipt


def _build_valid() -> tuple[dict, dict, str]:
    """Return (signed_card, receipt, card_digest_sha256)."""
    res = _fake_result()
    card = as_card(res, SUBJECT)
    card["issued_at"] = FIXED_TS
    signed = sign_card(card, KEY, allow_test_identity=True)
    receipt = _deterministic_receipt(signed, bound_issuer=True)
    digest = hashlib.sha256(card_canonical(signed)).hexdigest()
    return signed, receipt, digest


def _tamper_signature(card: dict) -> dict:
    """Flip one base64 char in the signature — deterministically makes verify fail."""
    bad = json.loads(json.dumps(card))
    sig = bad["signature"]["sig"]
    flipped = ("A" if sig[0] != "A" else "B") + sig[1:]
    bad["signature"]["sig"] = flipped
    return bad


def _different_card_receipt(signed: dict) -> dict:
    """A receipt bound to a DIFFERENT card's digest (a card-bind must fail)."""
    return _deterministic_receipt(signed, bound_issuer=False)


def main() -> int:
    os.makedirs(VECTORS_DIR, exist_ok=True)
    signed, receipt, dig = _build_valid()
    bad_sig = _tamper_signature(signed)
    bad_receipt = _different_card_receipt(signed)

    def _dump(path: str, obj: dict) -> str:
        """Write the pretty JSON fixture and return its sha256 (the exact bytes)."""
        data = json.dumps(obj, indent=2) + "\n"
        with open(os.path.join(VECTORS_DIR, path), "w", encoding="utf-8") as fh:
            fh.write(data)
        return hashlib.sha256(data.encode()).hexdigest()

    manifest = {
        "schema": "csoai.frozen-vectors-manifest/0.1",
        "generated_for": "NEXT-100-v4 move 6 — frozen vector version 1",
        "test_identity": "did:web:csoai.org#test-identity",
        "card_digest_sha256": dig,
        "register": REGISTER,
        "expected": {
            "valid_verify": "ok",
            "bad_sig_verify": "fail",
            "bad_receipt_verify": "fail",
        },
        "vectors": {
            "card_valid": {"file": "card-valid.json", "sha256": _dump("card-valid.json", signed)},
            "card_bad_sig": {"file": "card-bad-sig.json", "sha256": _dump("card-bad-sig.json", bad_sig)},
            "receipt_valid": {"file": "receipt-valid.json", "sha256": _dump("receipt-valid.json", receipt)},
            "receipt_bad": {"file": "receipt-bad.json", "sha256": _dump("receipt-bad.json", bad_receipt)},
        },
    }
    with open(MANIFEST_PATH, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")

    print(f"FROZEN VECTORS v1 written to {VECTORS_DIR}")
    print(f"  card digest sha256: {dig}")
    print(f"  card-valid.json     sha256: {manifest['vectors']['card_valid']['sha256'][:16]}…")
    print(f"  card-bad-sig.json   sha256: {manifest['vectors']['card_bad_sig']['sha256'][:16]}…")
    print(f"  receipt-valid.json  sha256: {manifest['vectors']['receipt_valid']['sha256'][:16]}…")
    print(f"  receipt-bad.json    sha256: {manifest['vectors']['receipt_bad']['sha256'][:16]}…")
    return 0


if __name__ == "__main__":
    sys.exit(main())

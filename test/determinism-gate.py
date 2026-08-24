#!/usr/bin/env python3
"""test/determinism-gate.py — hermetic double-run determinism gate (moves 36/44).

The canon binds the estate to deterministic predicates and honest artifacts
("unsealed-never-signed", signed-only ratings). This gate proves, fully OFF-network
and OFF-pod, that the measurable artifact is DETERMINISTIC: given the SAME frozen
probe/gold responses and the SAME signing key, the pipeline produces the SAME card
canonical digest, the SAME Ed25519 signature, and the SAME receipt bind — across two
independent runs. No Ollama, no network, no GPU.

We also assert the two honesty corollaries the canon demands:
  * unsealed-never-signed  — the board refuses to seal (publish) an UNSIGNED card;
    only a signed card is content-addressed and chained.
  * measurement-never-certification — the card carries the register verbatim.

The receipt is a TIME anchor, so its issued_at is wall-clock by design (a live
receipt correctly records WHEN). To prove the REST of the receipt construction is
deterministic, the gate pins issued_at to a fixed value in both runs and asserts the
resulting content_id is identical — the time field is the sole wall-clock input, and
it is isolated, not hidden.
"""
from __future__ import annotations

import hashlib, json, os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "harness"))
sys.path.insert(0, os.path.join(ROOT, "engine"))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from run_axis import load_axes, as_card
from dorado_sign import canonical as card_canonical, sign as sign_card
from dorado_receipt import build_card_receipt, content_id as receipt_content_id

PINNED_TS = "2026-08-24T00:00:00Z"      # frozen axis-engine timestamp
PINNED_ISSUED_AT = "2026-08-24T00:00:00+00:00"  # frozen receipt issued_at (the sole time field)


def _fixture():
    """A canned axis-engine result: FIXED golds + FIXED responses + FIXED ts.

    Deterministic everywhere; never touches a model or a clock."""
    axes, registry = load_axes(None)
    fake = {
        "model": "hermetic-fixture", "n": len(axes), "ok": 9,
        "accuracy": round(9 / len(axes), 3), "measured": len(axes), "total": len(axes),
        "registry": registry, "ts": PINNED_TS,
        "per_axis": [{"axis": a["slug"], "gold": a["gold"],
                      "verdict": ("PASS" if i < 9 else "FAIL"),
                      "resp": "deterministic-response", "measured": True}
                     for i, a in enumerate(axes)],
    }
    subject = {"id": "hermetic", "name": "Hermetic Fixture", "digest": "x"}
    return fake, subject, axes


def _run_once(key) -> dict:
    """One independent run of the pipeline; a clean, full bundle for comparison."""
    fake, subject, axes = _fixture()
    card = as_card(fake, subject, axes=axes)
    digest = hashlib.sha256(card_canonical(card)).hexdigest()
    signed = sign_card(card, key, kid="did:web:csoai.org#card-attestation-1",
                       allow_test_identity=True)
    receipt = build_card_receipt(card, private_key=key,
                                 kid="did:web:csoai.org#card-attestation-1",
                                 issued_at=PINNED_ISSUED_AT)
    return {
        "card": card, "digest": digest, "signed": signed,
        "signed_str": json.dumps(signed, sort_keys=True),
        "receipt": receipt, "receipt_cid": receipt_content_id(receipt),
        "subject_content_sha256": receipt["subject_content_sha256"],
    }


def _assert_unsealed_never_signed():
    """The board must refuse to seal (publish) an UNSIGNED card; only a signed card is
    content-addressed + chained. Runs in a throwaway board dir (no repo write)."""
    fake, subject, axes = _fixture()
    card = as_card(fake, subject, axes=axes)
    key = Ed25519PrivateKey.generate()
    signed = sign_card(card, key, kid="did:web:csoai.org#card-attestation-1",
                       allow_test_identity=True)
    receipt = build_card_receipt(card, private_key=key,
                                 kid="did:web:csoai.org#card-attestation-1")
    prior = os.environ.get("DORADO_BOARD_DIR")
    tmp = tempfile.mkdtemp()
    os.environ["DORADO_BOARD_DIR"] = tmp
    from harness.dorado_board import publish, _card_hash
    try:
        # unsigned card -> refuse (unsealed-never-signed)
        try:
            publish(dict(card))
            raise SystemExit("DETERMINISM: board sealed an UNSIGNED card")
        except ValueError:
            pass
        # signed card -> seal with a content-address = card hash; dedup on re-seal
        entry = publish(signed, receipt)
        assert entry.get("signed") is True and entry["hash"] == _card_hash(signed), entry
        assert publish(signed, receipt).get("deduped", False)
    finally:
        if prior:
            os.environ["DORADO_BOARD_DIR"] = prior
        else:
            os.environ.pop("DORADO_BOARD_DIR", None)


def determinism_gate() -> int:
    key = Ed25519PrivateKey.generate()
    a, b = _run_once(key), _run_once(key)

    # (1) card canonical digest identical across independent runs
    assert a["digest"] == b["digest"], "card canonical digest is NOT deterministic"
    # (2) Ed25519 signature + full signed card byte-identical across runs
    assert a["signed_str"] == b["signed_str"], "signed card is NOT deterministic"
    assert a["signed"]["signature"]["sig"] == b["signed"]["signature"]["sig"]
    # (3) receipt binds the card content_id (subject_content_sha256 == card digest)
    assert a["subject_content_sha256"] == b["subject_content_sha256"]
    assert a["subject_content_sha256"] == a["digest"]
    # (4) receipt content_id identical across runs (issued_at pinned -> sole time input isolated)
    assert a["receipt_cid"] == b["receipt_cid"], "receipt content_id is NOT deterministic"

    # measurement-never-certification: card carries the register verbatim
    reg = a["card"].get("credential_register", "")
    assert "measurement credential" in reg and "not a certification" in reg, reg

    _assert_unsealed_never_signed()
    return 0


def main() -> int:
    determinism_gate()
    print("DETERMINISM-GATE: PASS — hermetic double-run determinism proven: the SAME frozen "
          "probe/gold fixture + SAME key yield the SAME card canonical digest, the SAME "
          "Ed25519 signature, and the SAME receipt content_id across two independent runs "
          "(the receipt's issued_at is the sole wall-clock input, pinned to isolate it). "
          "Board refuses unsigned cards (unsealed-never-signed); card carries the "
          "measurement-credential register.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

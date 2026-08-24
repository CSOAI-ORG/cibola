#!/usr/bin/env python3
"""dorado_receipt.py — SCITT receipt for a DORADO measurement card (RFC 9943).

Emits an `a2a.signed-receipt/0.1` receipt that rides the RFC 9943 SCITT
substrate: it attests to WHAT was measured and WHEN (the card's content_id),
log-anchored to a named issuer. It mirrors the estate's inspect_receipts
build_receipt / art50_demo convention exactly.

Register (verbatim from canon): non-repudiable evidence of what was claimed and
when — NOT proof the eval is honest or uncontaminated. Measurement, not certification.

A receipt does NOT sign the card's scores; it binds a content_id (the card's
fingerprint) to the issuer at a time. Receipt inclusion is not non-equivocation
(the card could in principle be issued again); see the draft's Anti-Equivocation.
"""
from __future__ import annotations
import base64, hashlib, json
from datetime import datetime, timezone

SCHEMA = "a2a.signed-receipt/0.1"
KID_DEFAULT = "did:web:csoai.org#card-attestation-1"
DIGEST_FIELDS = ("signature", "sig", "content_id", "content_digest", "sha256")


def jcs(obj: dict) -> str:
    """RFC 8785 JSON Canonicalization Scheme — deterministic cross-language JSON."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def canonical(receipt: dict) -> bytes:
    """Receipt minus signature/content_id fields — the bytes the signature covers."""
    clean = {k: v for k, v in receipt.items() if k not in DIGEST_FIELDS}
    return jcs(clean).encode()


def content_id(receipt: dict) -> str:
    """content_id = sha256(canonical minus signature fields) per the a2a envelope."""
    return hashlib.sha256(canonical(receipt)).hexdigest()


def build_card_receipt(card: dict, private_key=None, pubkey_raw=None, kid=None,
                       issued_at: str | None = None) -> dict:
    """Build an a2a.signed-receipt/0.1 binding the measurement card's content_id.

    Uses the same canonical form the signature envelope uses (dorado_sign.canonical)
    so the card's content_id is reproducible. Signing with the pod key attaches a
    proof the issuer (did:web:csoai.org) bound this card's fingerprint at this time.

    issued_at: optional RFC 3339 timestamp string. The receipt is a TIME anchor, so
    by default it uses wall-clock now (correct for a live receipt); the hermetic
    determinism gate passes a fixed value to prove the rest of the receipt
    construction is deterministic (the time field is the sole wall-clock input).
    """
    from dorado_sign import canonical as card_canonical, rfc9679_thumbprint, KID_DEFAULT as CARD_KID

    card_digest = hashlib.sha256(card_canonical(card)).hexdigest()
    # the receipt content_id is the card's digest (bind by fingerprint, not name)
    receipt = {
        "schema": SCHEMA,
        "issuer": (kid or KID_DEFAULT).split("#", 1)[0],
        "kind": "measurement-card",
        "subject": card.get("subject", {}).get("id", "unknown"),
        "subject_content_sha256": card_digest,
        "claims": [{
            "type": "measurement",
            "detail": f"measured card {card_digest[:16]}… bound to issuer",
            "evidence_sha256": card_digest,
        }],
        "issued_at": issued_at or datetime.now(timezone.utc).isoformat(),
        "kid": kid or KID_DEFAULT,
    }
    cid = content_id(receipt)
    receipt["content_id"] = cid
    if private_key is not None:
        from cryptography.hazmat.primitives import serialization as _ser
        if pubkey_raw is None:
            pubkey_raw = private_key.public_key().public_bytes(
                encoding=_ser.Encoding.Raw, format=_ser.PublicFormat.Raw)
        sig = private_key.sign(canonical(receipt))
        receipt["signature"] = {
            "alg": "Ed25519", "kid": receipt["kid"], "pubkey": base64.b64encode(pubkey_raw).decode(),
            "sig": base64.b64encode(sig).decode(),
            "pubkey_thumbprint": rfc9679_thumbprint(pubkey_raw),
            "sig_input": "ed25519(canonical receipt minus content_id/signature)",
        }
    else:
        receipt["signature"] = {"alg": "Ed25519", "kid": receipt["kid"], "sig": None}
    return receipt


def build_scenario_receipt(payload: dict, *, label: str | None = None, private_key=None,
                           pubkey_raw=None, kid=None, issued_at: str | None = None,
                           kind: str = "scenario") -> dict:
    """Build an a2a.signed-receipt/0.1 binding an ARBITRARY SCENARIO payload (move 43).

    This is the generic JCS payload-binding counterpart to build_card_receipt: instead of
    binding a measurement card's content_id, it binds a SCENARIO / incident / probe result
    (a jail-break probe, a refusal record, a serious-incident report) by its RFC 8785
    canonical form. A stranger verifies it with ONLY the receipt + `cryptography`, proving
    THIS issuer recorded THIS payload at THIS time — the ASRS / Art 73 serious-incident
    structure.

    `kind` (default "scenario") lets a caller reuse the SAME JCS payload-binding path for
    another record kind (e.g. `"score"` for the move-59 Inspect signed-receipt scorer hook)
    without duplicating the canonical-sign-verify machinery. The default preserves the
    existing `kind: "scenario"` behaviour exactly; the claim type becomes f"{kind}-record".

    The payload is canonicalized with `jcs()` (RFC 8785 JSON Canonicalization Scheme) so
    the digest is deterministic cross-language and cross-tooling. The digest is carried in
    `subject_content_sha256` (the same bind field the card receipt uses), and the payload
    itself is NOT embedded (attest the digest, never the full payload — it may be large or
    partly secret). Verify with verify_scenario_receipt(receipt, payload).

    Register (verbatim from canon): non-repudiable evidence of WHAT was recorded and WHEN —
    not proof the scenario source is honest. Measurement, never certification.
    """
    from dorado_sign import rfc9679_thumbprint, KID_DEFAULT as CARD_KID

    payload_digest = hashlib.sha256(jcs(payload).encode()).hexdigest()
    receipt = {
        "schema": SCHEMA,
        "issuer": (kid or KID_DEFAULT).split("#", 1)[0],
        "kind": kind,
        "subject": payload.get("id") or label or "scenario",
        "subject_content_sha256": payload_digest,
        "claims": [{
            "type": f"{kind}-record",
            "detail": f"recorded scenario {payload_digest[:16]}… bound to issuer",
            "evidence_sha256": payload_digest,
        }],
        "issued_at": issued_at or datetime.now(timezone.utc).isoformat(),
        "kid": kid or KID_DEFAULT,
        "payload_canonical": "rfc8785-jcs",
    }
    cid = content_id(receipt)
    receipt["content_id"] = cid
    if private_key is not None:
        from cryptography.hazmat.primitives import serialization as _ser
        if pubkey_raw is None:
            pubkey_raw = private_key.public_key().public_bytes(
                encoding=_ser.Encoding.Raw, format=_ser.PublicFormat.Raw)
        sig = private_key.sign(canonical(receipt))
        receipt["signature"] = {
            "alg": "Ed25519", "kid": receipt["kid"], "pubkey": base64.b64encode(pubkey_raw).decode(),
            "sig": base64.b64encode(sig).decode(),
            "pubkey_thumbprint": rfc9679_thumbprint(pubkey_raw),
            "sig_input": "ed25519(canonical receipt minus content_id/signature)",
        }
    else:
        receipt["signature"] = {"alg": "Ed25519", "kid": receipt["kid"], "sig": None}
    return receipt

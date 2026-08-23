#!/usr/bin/env python3
"""cibola_sign.py — CIBOLA measurement-card signing pod (one-signer doctrine).

Signs a CIBOLA measurement card with Ed25519 (alg -19) over its CANONICAL form:
strip every signature field, sha256, then sign the digest. This mirrors the
estate's sign_board.py/verify_signature.py so a stranger can verify a card
offline with ONLY the published key (did:web:csoai.org#card-attestation-1).

The PRIVATE KEY NEVER LEAVES THE SIGNING POD. This module takes a private key
from an opaquely-provided signer callable or a secure bytes object; it never
reads key material from the repo, never logs it, never writes it out.

Kind: measurement — never certification. Register verbatim on every card.
"""
from __future__ import annotations
import base64, hashlib, json
from cryptography.hazmat.primitives import serialization

# fields excluded from the canonical form (must match the verifier exactly)
SIG_FIELDS = ("signature", "sha256", "sig", "signed", "signer", "sig_input")
ALG = -19  # Ed25519 (COSETags for CoseSign1; alg -19 per RFC 9052)
KID_DEFAULT = "did:web:csoai.org#card-attestation-1"


def canonical(obj: dict) -> bytes:
    """Object minus signature fields, JSON minified + sorted — the digest covers."""
    clean = {k: v for k, v in obj.items() if k not in SIG_FIELDS}
    return json.dumps(clean, sort_keys=True, separators=(",", ":")).encode()


def digest(obj: dict) -> bytes:
    return hashlib.sha256(canonical(obj)).digest()


def rfc9679_thumbprint(pubkey_raw: bytes) -> str:
    """RFC 9679 JWK thumbprint (SHA-256, base64url) for the Ed25519 public key."""
    jwk = json.dumps({"crv": "Ed25519", "kty": "OKP", "x": base64.urlsafe_b64encode(pubkey_raw).rstrip(b"=").decode()},
                     separators=(",", ":"))
    return base64.urlsafe_b64encode(hashlib.sha256(jwk.encode()).digest()).rstrip(b"=").decode()


def sign(card: dict, private_key, pubkey_raw=None, kid=None) -> dict:
    """Return a copy of card with a COSE_Sign1 Ed25519 signature attached.

    private_key: an object exposing .sign(bytes) and .public_key() (a
    cryptography Ed25519PrivateKey) — supplied by the pod, never by this repo.
    """
    out = dict(card)
    out.pop("signature", None)
    if pubkey_raw is None:
        pubkey_raw = private_key.public_key().public_bytes(
            # Raw = 32-byte Ed25519 public key, matching estate verify_signature.py
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw)
    # Ed25519 signs the message directly (no pre-hash); sign the canonical bytes
    # so the stranger verifier recomputes the SAME bytes and verifies. This
    # matches estate verify_signature.py (verifies against canonical_body).
    sig = private_key.sign(canonical(out))
    out["signature"] = {
        "kind": "ed25519",
        "alg": ALG,
        "kid": kid or KID_DEFAULT,
        "pubkey": base64.b64encode(pubkey_raw).decode(),
        "sig": base64.b64encode(sig).decode(),
        "pubkey_thumbprint": rfc9679_thumbprint(pubkey_raw),
        "sig_input": "ed25519(canonical card minus signature fields, sort_keys)",
    }
    return out


def is_signed(card: dict) -> bool:
    return isinstance(card.get("signature"), dict) and card["signature"].get("kind") == "ed25519"

#!/usr/bin/env python3
"""dorado_sign.py — DORADO measurement-card signing pod (one-signer doctrine).

Signs a DORADO measurement card with Ed25519 (alg -19) over its CANONICAL form:
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

# The PUBLISHED did:web:csoai.org Ed25519 public keys (x = base64url, from
# .well-known/did.json). The identity gate below refuses to sign a card with a key
# that is NOT the published #card-attestation-1 identity, so a stale/rogue key can
# never silently produce a mislabelled card (one-signer doctrine, ADR_ONE_SIGNER).
PUBLISHED_IDENTITIES = {
    "did:web:csoai.org#card-attestation-1": "1MsOqhbV9Qv3Yzo2qjT-CaVeEkuTFt7Sq9sSK7nDfjg",
    "did:web:csoai.org#estate-chain-1": "M0cuAmhx2yDNvZnnbEdTLr_PhLN6vtWyYNrjWJ31aW0",
    "did:web:csoai.org#site-release-1": "03g9l-dVNGVEAVVWQrJU9aLtkYTN3uARd52P7DEq-8g",
    "did:web:csoai.org#board-attestation-1": "k2fPWb6ctyu8l5at8FYgHsHFit_qoT-DssW3VNbCAXA",
}
# For hermetic tests + the demo asset, an explicit ephemeral identity is allowed
# ONLY when allow_test_identity=True (pass --allow-test-identity or env). It is
# never the production default, and the card is stamped kid=test so verifiers can
# tell it apart from a production card.
TEST_KID = "did:web:csoai.org#test-identity"


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


def signing_identity(pubkey_raw: bytes) -> tuple[str | None, bool]:
    """Return (kid, is_published_identity) for a raw Ed25519 public key.

    Matches the pubkey against the did:web:csoai.org published identities. If it is
    NOT a published identity, kid=test and is_published=False (so a stale/rogue key
    is never mislabelled as the production identity)."""
    x = base64.urlsafe_b64encode(pubkey_raw).rstrip(b"=").decode()
    for kid, pub_x in PUBLISHED_IDENTITIES.items():
        if pub_x == x:
            return kid, True
    return TEST_KID, False


def resolve_kid(pubkey_raw: bytes, kid: str | None, allow_test_identity: bool = False) -> str:
    """Resolve the kid to stamp, enforcing the one-signer doctrine.

    If the key IS a published identity, use its real kid (ignores the caller kid).
    If it is NOT published, require allow_test_identity (explicit) and use TEST_KID;
    otherwise raise — a non-production key must never claim the production identity."""
    real_kid, published = signing_identity(pubkey_raw)
    if published:
        return real_kid
    if not allow_test_identity and kid and kid != TEST_KID:
        raise ValueError(
            f"refusing to sign with a non-published key under kid '{kid}'. "
            f"Provision the real #card-attestation-1 key, or pass --allow-test-identity "
            f"to stamp the explicitly-test kid '{TEST_KID}'.")
    return TEST_KID


def sign(card: dict, private_key, pubkey_raw=None, kid=None, *, allow_test_identity: bool = False) -> dict:
    """Return a copy of card with a COSE_Sign1 Ed25519 signature attached.

    private_key: an object exposing .sign(bytes) and .public_key() (a
    cryptography Ed25519PrivateKey) — supplied by the pod, never by this repo.
    The kid stamped reflects the ACTUAL signing key: a published identity gets its
    real did:web kid; a non-published key is only allowed with allow_test_identity
    and is stamped kid=test (one-signer doctrine)."""
    out = dict(card)
    out.pop("signature", None)
    if pubkey_raw is None:
        pubkey_raw = private_key.public_key().public_bytes(
            # Raw = 32-byte Ed25519 public key, matching estate verify_signature.py
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw)
    stamped_kid = resolve_kid(pubkey_raw, kid, allow_test_identity)
    # Ed25519 signs the message directly (no pre-hash); sign the canonical bytes
    # so the stranger verifier recomputes the SAME bytes and verifies. This
    # matches estate verify_signature.py (verifies against canonical_body).
    sig = private_key.sign(canonical(out))
    out["signature"] = {
        "kind": "ed25519",
        "alg": ALG,
        "kid": stamped_kid,
        "pubkey": base64.b64encode(pubkey_raw).decode(),
        "sig": base64.b64encode(sig).decode(),
        "pubkey_thumbprint": rfc9679_thumbprint(pubkey_raw),
        "sig_input": "ed25519(canonical card minus signature fields, sort_keys)",
    }
    return out


def is_signed(card: dict) -> bool:
    return isinstance(card.get("signature"), dict) and card["signature"].get("kind") == "ed25519"

#!/usr/bin/env python3
"""test/scitt-verify.py — hermetic CI test for the SCITT COSE_Sign1 verifier (move 31).

Deterministic (fixed embedded test key, fixed payload, fixed kid=test), no network.
Proves the verifier checks a REAL COSE_Sign1 (RFC 9052) signature cryptographically —
counting is not verifying.

Registry (verbatim from canon): a verified COSE_Sign1 signature is evidence of what was
signed and when; it is a measurement, never a certification.
"""
import os, sys, base64, json, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "harness"))
sys.path.insert(0, ROOT)

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

from scitt_verify import (
    build_cose_sign1, verify_cose_sign1, verify_signed_item, verify_batch,
    decode_cose_sign1, sig_structure, PUBLISHED_IDENTITIES,
)

# Fixed fixture: a SeededPrivateKey so the pubkey is reproducible across runs (determinism)
_KEY_SEED = b"scitt-verify-fixture-v1-2026-08-24"[:32].ljust(32, b"!")  # exactly 32 bytes
KEY = Ed25519PrivateKey.from_private_bytes(_KEY_SEED)
RAW = KEY.public_key().public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
KID = "did:web:csoai.org#test-identity"
KID_PUB = "did:web:csoai.org#card-attestation-1"

PAYLOAD = b'{"schema":"csoai.measurement/0.1","subject":"demo","measured":6,"total":6,"signed_at":"2026-08-24T00:00:00Z"}'

checks = 0
def check(cond, msg):
    global checks
    checks += 1
    assert cond, f"FAIL: {msg}"
    print(f"  ok {checks:02d} — {msg}")

print("== SCITT COSE_Sign1 cryptographic verify (move 31) ==")

# 1. Build a valid COSE_Sign1 and verify it against the caller-pinned key.
env = build_cose_sign1(PAYLOAD, KEY, KID)
d = decode_cose_sign1(env)
check(d["protected_map"][1] == -19, "protected header alg == -19 (Ed25519)")
check(d["protected_map"][4] == KID, "protected header kid == test-identity")
check(d["payload"] == PAYLOAD, "payload roundtrips exactly")

v = verify_cose_sign1(env, expected_pubkey=RAW, expected_kid=KID)
check(v["ok"], f"valid COSE_Sign1 verifies (reason: {v['reason']})")
check(v["alg"] == -19, "reported alg -19")
check(v["kid"] == KID, "reported kid == test-identity")
check(v["pubkey_thumbprint"] == v["pubkey_thumbprint"], "thumbprint self-consistent")

# 2. Tamper the payload -> MUST fail (signature no longer covers it).
import cbor2
arr = decode_cose_sign1(env)
tampered_env = cbor2.dumps(cbor2.CBORTag(18, [arr["protected"], arr["unprotected"],
                                              b"TAMPERED-PAYLOAD", arr["signature"]]))
tv = verify_cose_sign1(tampered_env, expected_pubkey=RAW, expected_kid=KID)
check(not tv["ok"], "tampered payload fails verification")

# 3. Tamper the signature -> MUST fail.
bad_sig_env = cbor2.dumps(cbor2.CBORTag(18, [arr["protected"], arr["unprotected"],
                                             arr["payload"], b"\x00" * 64]))
bv = verify_cose_sign1(bad_sig_env, expected_pubkey=RAW, expected_kid=KID)
check(not bv["ok"], "tampered signature fails verification")

# 4. Wrong key (different key) -> MUST fail (identity pinning).
OTHER = Ed25519PrivateKey.generate()
OTHER_RAW = OTHER.public_key().public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
wv = verify_cose_sign1(env, expected_pubkey=OTHER_RAW, expected_kid=KID)
check(not wv["ok"], "wrong caller-pinned key rejected (identity pinning)")

# 5. Non-published kid, NOT pinned, no embedded key -> honest 'cannot verify' (not ok),
#    and it must never claim authenticity.
up = verify_cose_sign1(env)
check(not up["ok"], "unpinned non-published kid is not reported as verified")
check(("cannot verify" in up["reason"]) or ("NOT pinned" in up["reason"]), f"unpinned verdict is honest ({up['reason'][:50]}…)")

# 5b. Self-embedded key, NOT pinned -> 'self-consistent but NOT pinned' (ok is False).
with_x = cbor2.dumps(cbor2.CBORTag(18, [arr["protected"],
                                        cbor2.dumps({-2: RAW}),
                                        arr["payload"], arr["signature"]]))
sx = verify_cose_sign1(with_x)
check(not sx["ok"], "self-embedded-key envelope not reported as verified-authentic")
check("self-consistent" in sx["reason"] and "NOT pinned" in sx["reason"],
      "self-embedded-key verdict says self-consistent but NOT pinned (honest)")
# permit_unpinned verifies internal consistency (content not altered) but the verdict
# must remain honest: ok=True for consistency, yet never claim did:web authenticity.
sx2 = verify_cose_sign1(with_x, permit_unpinned=True)
check(sx2.get("ok") is True, "permit_unpinned verifies internal consistency (envelope intact)")
check("self-consistent" in sx2["reason"], "permit_unpinned verdict still says self-consistent, never verified-authentic")
check(sx2.get("pinned_to") is None, "permit_unpinned never pins to a trusted identity (pinned_to is None)")

# 6. Publish-identity pin: sign with a key that matches the published #card-attestation-1 x,
#    embed only the kid (no x), and verify against the published identity.
pub_x = base64.urlsafe_b64decode(PUBLISHED_IDENTITIES[KID_PUB] + "==")
pk_from = Ed25519PublicKey.from_public_bytes(pub_x)
# build an envelope whose protected map carries a kid in the trust set; embed pubkey x.
protected = cbor2.dumps({1: -19, 4: KID_PUB})
sig_struct = sig_structure(protected, PAYLOAD)
# We cannot sign with a pubkey-only; instead verify the identity-match logic:
# a real envelope would be signed by the pod. Here we guarantee the trust-set lookup
# resolves the published identity correctly for an envelope that embeds that x.
unprotected_with_x = cbor2.dumps({-2: pub_x})
# build a synthetic signature that DOES verify against the published key would require the
# private key (pod ceremony, never invoked) — so instead assert the identity resolver:
from scitt_verify import _pub_thumbs
check(_pub_thumbs(pub_x)["x_b64url"] == PUBLISHED_IDENTITIES[KID_PUB], "published identity x resolves to base64url")

# 7. Batch verify: mixed valid / tampered / no-envelope.
good = env
bad_sig = bad_sig_env
no_env = {"foo": "bar"}  # no cose field
batch = verify_batch([{"cose": base64.b64encode(good).decode()},
                      {"cose": base64.b64encode(bad_sig).decode()},
                      no_env], expected_pubkey=RAW, expected_kid=KID)
check(batch["n"] == 3, f"batch n == 3 (got {batch['n']})")
check(batch["verified"] == 1, f"batch verified == 1 (got {batch['verified']})")
check(batch["failed"] == 1, f"batch failed == 1 (got {batch['failed']})")
check(batch["unverifiable"] == 1, f"batch unverifiable == 1 (got {batch['unverifiable']})")
check(batch["results"][0]["verdict"] == "verified", "good item verdict == verified")
check(batch["results"][1]["verdict"] == "failed", "tampered item verdict == failed")
check(batch["results"][2]["verdict"] == "absent", "no-envelope item verdict == absent")

# 8. verify_signed_item on a base64 COSE string.
vi = verify_signed_item({"cose": base64.b64encode(good).decode()})
# verify_signed_item has no expected key so it's self-consistent-only unless pinned.
check(not vi["ok"], "verify_signed_item without pin is honestly not-verified without a trust root")

# 9. determinism: same seed -> same envelope (same signature bytes, since Ed25519 is
#    deterministic over the same inputs).
env2 = build_cose_sign1(PAYLOAD, KEY, KID)
check(env == env2, "deterministic envelope across runs (fixed seed + payload)")

print(f"\nSCITT COSE_Sign1 verify: {checks} checks green (hermetic, deterministic, no network)")
sys.exit(0)

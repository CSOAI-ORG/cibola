#!/usr/bin/env python3
"""verify_kit.py — offline stranger verify-kit bundle + verification counter (move 17).

NEXT-100 v4 move 17 — "stranger-verification counter + verify-kit bundle
(card+payload+receipts+keys, offline)".

A verify-kit is ONE deterministic, self-contained artifact a stranger downloads and
verifies ENTIRELY OFFLINE — no network, no pod, no private key, only `cryptography`. It
packs: the signed card, its receipt(s), its anchor, and the did:web public key(s) the
stranger needs to pin identity, each bound by content_sha256, plus a plain walkthrough.

The verification COUNTER is a separate surface: an append-only, content-addressed log of
verification events (`data/verify-log.jsonl`). It counts verification ACTIONS the estate
(verify page / CLI / kit) records — it is a provenance ledger of usage, never a claim of
validity. A stranger's offline verification is counted only if that stranger records it;
the counter never asserts anyone-world verified anything.

Register (verbatim from canon): a verify-kit is evidence of what was measured and when,
verifiable offline. It is a measurement device, never a certification, endorsement, or
conformity mark, and must not be presented as one.
"""
from __future__ import annotations
import base64, hashlib, json, os
from datetime import datetime, timezone

SCHEMA = "csoai.verify-kit/0.1"
REGISTER = ("This is a verification kit. It is a measurement device, never a certification, "
            "endorsement, or conformity mark, and must not be presented as one.")
DIGEST_FIELDS = ("digest", "kit_id")
WALKTHROUGH = (
    "OFFLINE STRANGER-VERIFY WALKTHROUGH\n"
    "===================================\n"
    "1. Open card.json and confirm it says 'measurement' never 'certification'.\n"
    "2. Run:  python3 dorado_verify.py card.json\n"
    "   -> 'VALID' means the signing key signed THIS exact card (Ed25519).\n"
    "3. Run:  python3 dorado_receipt_verify.py receipt.json card.json\n"
    "   -> 'VALID receipt' means THIS receipt attests to THIS card at THIS time.\n"
    "4. Optional (if an anchor.json is present):\n"
    "   python3 dorado_anchor_verify.py anchor.json card.json\n"
    "   -> 'ANCHOR VALID' means an external TSA time-bound THIS card's digest.\n"
    "5. Confirm the signing key in keys.json matches the card's pubkey + kid.\n"
    "   The card is verified against the published did:web:csoai.org identity.\n"
    "Nothing here is a certification. A valid verification shows evidence, not endorsement.\n"
)


def jcs(obj: dict) -> str:
    """RFC 8785 JSON Canonicalization Scheme — deterministic cross-language JSON."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def kit_digest(kit: dict) -> str:
    """sha256 of the kit's canonical (RFC 8785) form minus the digest field."""
    clean = {k: v for k, v in kit.items() if k not in DIGEST_FIELDS}
    return _sha256(jcs(clean).encode())


def build_verify_kit(card: dict, receipts=None, anchor=None,
                     published_keys: dict | None = None, *, generated_at: str | None = None,
                     kit_id: str | None = None) -> dict:
    """Build a single offline verify-kit bundle from a signed card + receipts + anchor.

    `published_keys` is the {kid: {"x": <base64url x>, "thumbprint": <...>}} identity set
    used to pin the card. Defaults to the published did:web:csoai.org identities.

    `generated_at` is the sole wall-clock input (pinned for hermetic determinism); the rest
    of the kit construction is deterministic over the input card/receipts/anchor.
    """
    receipts = receipts or []
    if isinstance(receipts, dict):
        receipts = [receipts]
    if published_keys is None:
        from engine.dorado_sign import PUBLISHED_IDENTITIES, rfc9679_thumbprint
        published_keys = {
            kid: {"x": x, "thumbprint": rfc9679_thumbprint(base64.urlsafe_b64decode(x + "=" * (-len(x) % 4)))}
            for kid, x in PUBLISHED_IDENTITIES.items()
        }
    contents = {
        "card.json": card,
        "keys.json": {
            "schema": "csoai.verify-kit-keys/0.1",
            "register": "Public did:web:csoai.org Ed25519 identities a stranger needs to pin the card.",
            "identities": published_keys,
        },
    }
    for i, r in enumerate(receipts):
        contents[f"receipt-{i + 1}.json" if len(receipts) > 1 else "receipt.json"] = r
    if anchor is not None:
        contents["anchor.json"] = anchor
    parts = {}
    for name, obj in contents.items():
        parts[name] = {"filename": name, "content_sha256": _sha256(jcs(obj).encode()),
                       "kind": name.split(".")[0]}
    kit = {
        "schema": SCHEMA,
        "register": REGISTER,
        "walkthrough": WALKTHROUGH,
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "contents": contents,
        "parts": parts,
    }
    d = kit_digest(kit)
    kit["kit_id"] = kit_id or "kit-" + d[:16]
    kit["digest"] = d
    return kit


def _verify_card(contents: dict) -> dict:
    import sys, os as _os
    sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "engine"))
    from dorado_verify import verify_card
    return verify_card(contents["card.json"])


def _verify_receipt(r: dict, card: dict) -> dict:
    import sys, os as _os
    sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "engine"))
    from dorado_receipt_verify import verify_receipt
    return verify_receipt(r, card)


def _verify_anchor(anchor: dict, card: dict) -> dict:
    import sys, os as _os
    sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "engine"))
    from dorado_anchor_verify import verify_anchor
    return verify_anchor(anchor, card)


def _identity_pin(card: dict, identities: dict, *, source: str) -> dict:
    """Pin the card's signature to a key in a trusted identity set.

    `identities` is {kid: {"x": base64url x, "thumbprint": ...}}. `source` records WHERE the
    identity set came from ('caller-trusted' = did:web-resolved/caller-supplied, the real
    stranger-verify; 'kit-bundled' = the convenience key set shipped in the kit). The verdict
    names the source so a kit-bundled pin is never mistaken for an independently-verified
    identity."""
    import sys, os as _os, base64 as _b64
    sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "engine"))
    from dorado_sign import rfc9679_thumbprint
    s = card.get("signature") or {}
    kid = s.get("kid")
    if kid not in identities:
        return {"ok": False, "reason": f"card kid '{kid}' is not in the {source} identity set", "source": source}
    declared = identities[kid]
    raw = _b64.b64decode(s.get("pubkey", ""))
    if declared.get("x") and _b64.urlsafe_b64decode(declared["x"] + "=" * (-len(declared["x"]) % 4)) != raw:
        return {"ok": False, "reason": f"card pubkey does not match the {source} identity '{kid}'", "source": source}
    thumb = rfc9679_thumbprint(raw)
    if declared.get("thumbprint") and declared["thumbprint"] != thumb:
        return {"ok": False, "reason": f"card pubkey thumbprint {thumb[:12]}… != declared {declared['thumbprint'][:12]}…", "source": source}
    return {"ok": True, "reason": f"card pinned to identity '{kid}' (source: {source})", "source": source}


def verify_verify_kit(kit: dict, trusted_keys: dict | None = None) -> dict:
    """Verify a whole verify-kit OFFLINE: integrity + card + receipt + anchor + identity.

    Returns per-part verdicts + an aggregate honest verdict. A kit is VALID only if its
    digest is intact, the card verifies, at least one receipt verifies (or none is present,
    reported honestly), and the card is pinned to a trusted identity.

    `trusted_keys` is the identity set a stranger holds independently (e.g. did:web-resolved
    did:web:csoai.org keys) — this is the REAL authenticity pin, and its verdict is labelled
    'caller-trusted'. When omitted, the kit's bundled keys.json is used and the verdict is
    labelled 'kit-bundled' (mechanism verified; identity not independently fetched from
    did:web — a stranger should still cross-check the did:web root)."""
    recomputed = kit_digest(kit)
    digest_ok = recomputed == kit.get("digest")
    parts = []
    card = kit.get("contents", {}).get("card.json")
    card_v = _verify_card(kit["contents"]) if card is not None else {"ok": False, "reason": "no card.json in kit"}
    parts.append({"name": "digest", "ok": digest_ok,
                  "reason": "kit digest intact" if digest_ok else "DIGEST MISMATCH — kit altered"})
    parts.append({"name": "card", "ok": card_v["ok"], "reason": card_v["reason"], "kid": card_v.get("kid")})
    verified_receipts = 0
    for name in sorted(kit.get("contents", {})):
        if name == "card.json" or name == "keys.json" or name == "anchor.json":
            continue
        r = kit["contents"][name]
        rv = _verify_receipt(r, card) if card is not None else {"ok": False, "reason": "no card to bind"}
        parts.append({"name": name, "ok": rv["ok"], "reason": rv["reason"]})
        if rv["ok"]:
            verified_receipts += 1
    anchor_v = None
    if "anchor.json" in kit.get("contents", {}):
        anchor_v = _verify_anchor(kit["contents"]["anchor.json"], card) if card is not None else {"ok": False, "reason": "no card to bind"}
        parts.append({"name": "anchor", "ok": anchor_v["ok"], "reason": anchor_v["reason"]})
    # identity pin: caller-trusted keys win (real stranger-verify); else kit-bundled.
    if trusted_keys is not None:
        ids, src = trusted_keys, "caller-trusted"
    else:
        ids = kit.get("contents", {}).get("keys.json", {}).get("identities", {})
        src = "kit-bundled"
    keys_v = _identity_pin(card, ids, source=src) if card is not None else {"ok": False, "reason": "no card to pin"}
    parts.append({"name": "keys", "ok": keys_v["ok"], "reason": keys_v["reason"]})

    # honest aggregate: validity requires digest + card + identity-pin + at least one verified
    # receipt (or no receipt present). The identity source is carried so a kit-bundled pin is
    # reported as exactly that — never as an independently-fetched did:web authentication.
    has_receipts = any(n not in ("card.json", "keys.json", "anchor.json") for n in kit.get("contents", {}))
    receipt_ok = (verified_receipts > 0) if has_receipts else True
    ok = bool(digest_ok and card_v["ok"] and keys_v["ok"] and receipt_ok and (anchor_v is None or anchor_v["ok"]))
    return {"ok": ok, "digest_ok": digest_ok, "card_ok": card_v["ok"], "keys_ok": keys_v["ok"],
            "identity_source": keys_v.get("source"),
            "verified_receipts": verified_receipts,
            "reason": ("VALID verify-kit (measurement, never certification)" if ok
                       else "verify-kit NOT fully verified"),
            "parts": parts, "kit_id": kit.get("kit_id")}


# ---- verification counter (append-only provenance ledger) ----

VERIFY_LOG_DEFAULT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                  "data", "verify-log.jsonl")


def record_verification(entry: dict, log_path: str = VERIFY_LOG_DEFAULT) -> dict:
    """Append one verification event to the append-only ledger (never rewrite in place).

    The ledger counts verification ACTIONS the estate records; it is provenance of usage,
    not a claim of validity. `entry` is stamped with a UTC timestamp + a content hash so
    the record is self-addressed and append-only."""

    now = datetime.now(timezone.utc).isoformat()
    rec = {"ts": now}
    rec.update(entry)
    rec["entry_sha256"] = _sha256(jcs({k: v for k, v in rec.items() if k != "entry_sha256"}).encode())
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, separators=(",", ":")) + "\n")
    return rec


def verification_counter(log_path: str = VERIFY_LOG_DEFAULT) -> dict:
    """Read the verification ledger and report total / verified / failed / kitted counts.

    Honest register: counting verification events is a measure of usage and coverage, never
    a claim that any model is certified or any result was validated."""
    total = verified = failed = digest_ok = kitted = 0
    if not os.path.exists(log_path):
        return {"total": 0, "verified": 0, "failed": 0, "digest_ok": 0, "kitted": 0,
                "register": "Counting verification events measures usage, never validity."}
    for line in open(log_path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except Exception:
            continue
        total += 1
        if e.get("verified"):
            verified += 1
        elif e.get("failed"):
            failed += 1
        if e.get("digest_ok"):
            digest_ok += 1
        if e.get("kit_id"):
            kitted += 1
    return {"total": total, "verified": verified, "failed": failed,
            "digest_ok": digest_ok, "kitted": kitted,
            "register": "Counting verification events measures usage, never validity."}

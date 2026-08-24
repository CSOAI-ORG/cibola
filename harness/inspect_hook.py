#!/usr/bin/env python3
"""inspect_hook.py — Inspect (MIT / UK AISI) signed-receipt SCORER hook (move 59).

NEXT-100 v4 move 59 — "Inspect (MIT) signed-receipt scorer hook".

What this is
------------
The estate measures models with the Inspect eval framework (inspect_ai). Its scoring
surface returns a `Score` (value + explanation + metadata) for every sample an evaluator
scores. Move 59 asks for a hook that makes a scored result carry CRYPTOGRAPHIC PROVENANCE
— a signed receipt that a stranger can verify offline — so an eval result is evidence of
WHAT was scored and WHEN, by WHOM, and is NOT a bare, mutable number.

This module is a hermetic, dependency-free adapter for that Inspect `Score` hook surface.
It does NOT import inspect_ai (external + network-dep): it mirrors the contract the estate
relies on (a `Score`-shaped dict with value/explanation/metadata) and the hook point it
would register (`@score` / `eval.hooks.score`), and binds the scored result to the issuer.

The receipt rides the score in `metadata["signed_receipt"]` and NEVER mutates the score:
`score["value"]` and the underlying `explanation` are preserved verbatim. Provenance is a
separate field — it never changes what was measured. This is the canon: a measurement
credential, not a certification; evidence, not endorsement.

How a receipt rides the score
-----------------------------
1. The scorer returns a `Score` (dict). `attach_signed_receipt(score, ...)` normalises the
   score into a JSON-canonicalisable payload (subject + value + explanation + the
   caller-relevant metadata, minus any prior receipt) via RFC 8785 JCS.
2. It binds that payload to the issuer with a signed `a2a.signed-receipt/0.1` (reusing
   `dorado_receipt.build_scenario_receipt`, the move-43 JCS payload-binding path) with
   `kind:"score"` — the receipt's `subject_content_sha256` = sha256(JCS(payload)).
3. It attaches the receipt under `metadata["signed_receipt"]` and returns a NEW score dict.

`verify_score_receipt(score)` is the stranger side: it re-derives the payload from the
score, and verifies the receipt's signature + that it binds THIS payload (a tampered or
different score silently fails the bind). A score with no receipt is reported honestly as
"no signed receipt — honestly-unsigned (unsealed-never-signed)", never invented.

Register (verbatim from canon): non-repudiable evidence of WHAT was scored and WHEN, by
the estate — NOT proof the eval or the model is honest or uncontaminated. Measurement,
never certification.
"""
from __future__ import annotations

import hashlib
import os
import sys

# --- engine path so both CLI and test can import the receipt/sign primitives -----------
_ENGINE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine")
if _ENGINE not in sys.path:
    sys.path.insert(0, _ENGINE)

from dorado_receipt import build_scenario_receipt, jcs  # noqa: E402
from dorado_receipt_verify import verify_scenario_receipt  # noqa: E402
from dorado_sign import TEST_KID  # noqa: E402

RECEIPT_META_KEY = "signed_receipt"
SCHEMA = "csoai.inspect-score-receipt/0.1"
KIND = "score"
# The canonical measurement-not-certification register (verbatim from canon, matching
# run_axis/sb315/dorado_board/gen-frozen-vectors), carried on every scored result this hook
# returns so a stranger reading the score sees the framing.
REGISTER = (
    "This is a measurement credential. It is not a certification, endorsement, or "
    "conformity mark, and must not be presented as one."
)

# fields that, if present in metadata, must NOT be bound into the payload (self-reference
# + fields the receipt itself generates). Strip them before JCS-canonicalising.
_RECEIPT_STRIP = (RECEIPT_META_KEY, "receipt_content_id", "signed_receipt_digest")


def score_payload(score: dict, subject: str | None = None) -> dict:
    """Normalise a `Score` into the JSON-canonicalisable payload the receipt binds.

    Keeps the subject id, the score value, the explanation, and the caller-relevant metadata
    (model, sample_id, per-axis breakdown) and strips any prior receipt field so the digest
    is stable and self-reference-free. The `subject` and `register` framing are ALWAYS present
    and deterministic, so `verify_score_receipt` reproduces the exact payload the receipt was
    bound to (a tampered/different score silently fails the bind). Returns a NEW dict; the
    input score is untouched.
    """
    meta = dict(score.get("metadata") or {})
    for field in _RECEIPT_STRIP:
        meta.pop(field, None)
    subject_id = subject or score.get("id") or meta.get("sample_id") or meta.get("model") or "score"
    payload = {
        "schema": SCHEMA,
        "id": subject_id,
        "subject": subject_id,
        "value": score.get("value"),
        # an explanation is the natural-language justification; bind it so the receipt
        # attests to the WHOLE recorded result, not just the number.
        "explanation": _strip_non_json(score.get("explanation")),
        "register": REGISTER,
    }
    if meta:
        payload["metadata"] = meta
    return payload


def _strip_non_json(obj):
    """Drop anything not JSON-serialisable (an Inspect Score may carry non-JSON attrs)."""
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, dict):
        return {k: _strip_non_json(v) for k, v in obj.items() if k not in _RECEIPT_STRIP}
    if isinstance(obj, (list, tuple)):
        return [_strip_non_json(v) for v in obj]
    return str(obj)  # robust fallback; never silently drop a value that should be bound


def attach_signed_receipt(score: dict, *, subject: str | None = None, private_key=None,
                          pubkey_raw=None, kid=None, issued_at: str | None = None) -> dict:
    """Attach a signed `a2a.signed-receipt/0.1` (kind:"score") riding this `Score`.

    `subject` optionally overrides the receipt subject (default: the score's id/sample_id/
    model). `private_key`/`kid` come from the pod in production; the hermetic tests pass an
    ephemeral test key so the receipt is stranger-verifiable with only `cryptography`.

    When `private_key` is None the receipt is built UNSIGNED (sig=None) — the honest
    "unsealed-never-signed" state. A score can carry provenance without pretending to be
    sealed; the verifier reports a deliberately-unsigned receipt as "honestly-unsigned",
    never as verified.

    The function is PURE: it returns a NEW score dict and leaves `score` untouched. The
    result's `value` and `explanation` are byte-for-byte the caller's — provenance never
    changes the measurement.
    """
    payload = score_payload(score, subject=subject)
    receipt = build_scenario_receipt(payload, label=subject or payload["id"],
                                     private_key=private_key, pubkey_raw=pubkey_raw,
                                     kid=kid or TEST_KID, issued_at=issued_at, kind=KIND)
    out = dict(score)
    meta = dict(score.get("metadata") or {})
    meta[RECEIPT_META_KEY] = receipt
    out["metadata"] = meta
    return out


def verify_score_receipt(score: dict) -> dict:
    """Stranger-verify the signed receipt riding a `Score`.

    Re-derives the payload from the score (minus the receipt field) and verifies the
    receipt's Ed25519 signature AND that it binds THIS payload. Returns {"ok": bool,
    "reason": str, ...}. A Score with no receipt reports an honest "no signed receipt"
    (never a fabricated verification). A tampered `value`/`explanation`/`metadata` silently
    fails the JCS bind — provenance is bound to the exact recorded result.
    """
    receipt = (score.get("metadata") or {}).get(RECEIPT_META_KEY)
    if not isinstance(receipt, dict):
        return {"ok": False, "reason": "no signed receipt on this score (honestly-unsigned, "
                                       "unsealed-never-signed)"}
    payload = score_payload(score)
    return verify_scenario_receipt(receipt, payload, kinds=(KIND,))


def signed_scorer(scorer_fn, **attach_kw):
    """Wrap an Inspect-style scorer so EVERY result it returns rides a signed receipt.

    This is the hook the estate registers at the Inspect `@score` / `eval.hooks.score`
    point: `signed_scorer(score_fn)` returns a wrapper that calls `score_fn`, attaches a
    signed receipt to each returned `Score`, and returns the enriched Score. In production
    `**attach_kw` carries the pod signing identity (private_key=None => honestly-unsigned).
    The wrapper NEVER changes what `score_fn` measures — provenance rides, never alters.
    """
    def wrapped(*args, **kwargs):
        score = scorer_fn(*args, **kwargs)
        if score is None:
            return None
        return attach_signed_receipt(score, **attach_kw)
    return wrapped

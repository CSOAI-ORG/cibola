#!/usr/bin/env python3
"""rate_cap.py — issuance-velocity / rate-cap attestation (move 51).

Purpose
-------
A measurement estate that issues signed cards MUST be able to attest its OWN issuance
velocity honestly. If a subject — or the estate itself — floods the register faster than
the rate-cap policy, the attestation must report the OVERAGE verbatim. It must NEVER
silently clip, re-rate, or hide a breach (anti-Goodhart / nobody-ranked-pays: nobody can
be seen to buy or throttle their way up the board). This module is the honest, deterministic,
off-network controller for that.

What it produces
----------------
A `csoai.velocity-attestation/0.1` card:
  * partitions the issuance ledger into fixed, deterministic windows (derived ONLY from the
    event timestamps — no wall clock, so the same ledger always yields the same windows);
  * reports, per window, the observed per-subject count and the observed global count;
  * compares them against a rate-cap policy (per-subject cap + global cap per window);
  * emits an honest verdict: `within-cap` when every window is inside the caps, `over-cap`
    when ANY window exceeds a cap — and, on over-cap, lists every violating window verbatim
    (the breach is evidence, never a hidden cost);
  * sets `clipped: false` always because this controller NEVER clips or re-rates;
  * carries the measurement-credential register (never a certification).

Register / canon
----------------
This is a MEASUREMENT-style attestation of observable issuance behaviour — it is NOT a
certification, an accreditation claim, or a conformity mark. It is a self-audit record:
a datum the estate publishes about its own regulation, never a claim that any model is good.
The controller is deterministic (no LLM-judge), off-network, and hermetic.

The attestation is signed (test identity in the hermetic tests) via `dorado_sign` so a
stranger can verify it with only `cryptography`; the measurement-credential register rides
the card. An over-cap attestation remains a valid, verifiable record — it proves the estate
reported its own breach, not that a breach never happened.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

REGISTER = ("This is a measurement-style attestation of observable issuance behaviour. "
            "It is not a certification, endorsement, or conformity mark, and must not be "
            "presented as one.")
SCHEMA = "csoai.velocity-attestation/0.1"

DEFAULT_CAPS = {"per_subject": 5, "global": 20}   # per fixed window


# --------------------------------------------------------------------------- time helpers
def parse_ts(s: str) -> int:
    """Parse an RFC 3339 timestamp into epoch seconds (deterministic, no wall clock).

    Normalises a 'Z' suffix to '+00:00' so it parses identically on every Python version."""
    if not isinstance(s, str) or not s:
        raise ValueError(f"missing/invalid issued_at: {s!r}")
    text = s.replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def norm_ts(epoch: int) -> str:
    """Render an epoch-seconds value as an RFC 3339 UTC string (deterministic)."""
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat().replace("+00:00", "Z")


# --------------------------------------------------------------------------- velocity
def _field(ev: dict, *names, default=None):
    for n in names:
        if n in ev and ev[n] is not None:
            return ev[n]
    return default


def compute_velocity(events: list[dict], window_seconds: int = 3600) -> dict:
    """Partition the issuance ledger into deterministic windows and count per window.

    Deterministic: window boundaries derive ONLY from the min event timestamp (floored to a
    whole window) — never from the wall clock — so the same ledger yields the same windows.
    Events are sorted by (issued_at, card_id) for a stable, reproducible order.

    Returns {window_seconds, windows:[{window_start, count, by_subject}], max_per_subject,
    max_global, total, first_ts, last_ts}.
    """
    if window_seconds < 1:
        raise ValueError("window_seconds must be >= 1")
    if not events:
        return {"window_seconds": window_seconds, "windows": [], "max_per_subject": 0,
                "max_global": 0, "total": 0, "first_ts": None, "last_ts": None}

    norm = []
    for ev in events:
        ts = _field(ev, "issued_at", "ts", "at")
        subj = _field(ev, "subject_id", "subject", "subjectId", default="anonymous")
        cid = _field(ev, "card_id", "cardId", "card", "id", default="")
        if ts is None:
            raise ValueError(f"event missing issued_at: {ev!r}")
        norm.append({"epoch": parse_ts(ts), "subject": str(subj), "card_id": str(cid)})
    # stable order: by epoch, then card_id (tiebreak), then subject
    norm.sort(key=lambda e: (e["epoch"], e["card_id"], e["subject"]))

    min_ep = norm[0]["epoch"]
    window_start0 = (min_ep // window_seconds) * window_seconds

    buckets = {}
    for e in norm:
        idx = (e["epoch"] - window_start0) // window_seconds
        b = buckets.setdefault(idx, {"count": 0, "by_subject": {}})
        b["count"] += 1
        b["by_subject"][e["subject"]] = b["by_subject"].get(e["subject"], 0) + 1

    windows = []
    max_per_subject = 0
    max_global = 0
    for idx in sorted(buckets):
        b = buckets[idx]
        by_subject = dict(sorted(b["by_subject"].items()))
        windows.append({"window_start": norm_ts(window_start0 + idx * window_seconds),
                        "count": b["count"], "by_subject": by_subject})
        max_global = max(max_global, b["count"])
        max_per_subject = max(max_per_subject, max(by_subject.values()))

    return {"window_seconds": window_seconds, "windows": windows,
            "max_per_subject": max_per_subject, "max_global": max_global,
            "total": len(norm), "first_ts": norm_ts(norm[0]["epoch"]),
            "last_ts": norm_ts(norm[-1]["epoch"])}


# --------------------------------------------------------------------------- attestation
def attest(events: list[dict], *, caps: dict | None = None, window_seconds: int = 3600,
           subject: str | None = None, issued_at: str | None = None) -> dict:
    """Build a deterministic `csoai.velocity-attestation/0.1` card (UNSIGNED).

    `caps` = {per_subject, global}. `subject` optionally narrows the attestation to one
    subject's flow (reported separately from the multi-subject ledger). `issued_at`, if
    given, pins the as-of time; otherwise it is the LAST event timestamp (deterministic).

    Honesty contract:
      * verdict is `within-cap` when EVERY window is inside the caps, else `over-cap`.
      * on `over-cap`, every violating (window, subject) AND (window, global) pair is listed
        verbatim. No breach is hidden.
      * `clipped` is ALWAYS False — this controller never clips or re-rates an observation.
      * the card carries the measurement-credential register (never a certification).
    """
    if caps is None:
        caps = dict(DEFAULT_CAPS)
    if not isinstance(caps, dict) or "per_subject" not in caps or "global" not in caps:
        raise ValueError("caps must be {per_subject, global}")
    per_subject_cap = int(caps["per_subject"])
    global_cap = int(caps["global"])

    v = compute_velocity(events, window_seconds)
    violations = []
    for w in v["windows"]:
        for subj, cnt in w["by_subject"].items():
            if cnt > per_subject_cap:
                violations.append({"kind": "per-subject", "window_start": w["window_start"],
                                   "subject": subj, "count": cnt, "cap": per_subject_cap})
        if w["count"] > global_cap:
            violations.append({"kind": "global", "window_start": w["window_start"],
                               "subject": None, "count": w["count"], "cap": global_cap})
    verdict = "over-cap" if violations else "within-cap"

    as_of = issued_at or v["last_ts"]
    if as_of is None:                      # empty ledger -> pin to a stable epoch
        as_of = norm_ts(0).replace("Z", "+00:00")

    card = {
        "schema": SCHEMA,
        "kind": "honest issuance-velocity attestation (measurement, never certification)",
        "window_seconds": window_seconds,
        "caps": {"per_subject": per_subject_cap, "global": global_cap},
        "observed": {
            "windows": v["windows"],
            "max_per_subject": v["max_per_subject"],
            "max_global": v["max_global"],
            "total": v["total"],
            "first_ts": v["first_ts"],
            "last_ts": v["last_ts"],
        },
        "subject": subject,
        "verdict": verdict,
        "violations": violations,
        "clipped": False,
        "honesty_note": ("An over-cap window is reported verbatim; the issuance is never "
                         "silently clipped or re-rated. A below-cap run is stated honestly; "
                         "an over-cap run is stated honestly too."),
        "register": REGISTER,
        "issued_at": as_of,
    }
    return card


# --------------------------------------------------------------------------- sign / verify
def _engine_dir() -> str:
    return str(Path(__file__).resolve().parent.parent / "engine")


def sign_attestation(card: dict, private_key, *, kid=None, allow_test_identity: bool = True) -> dict:
    """Sign a velocity-attestation card (Ed25519) via the estate signer.

    `allow_test_identity=True` is the DEFAULT here because the velocity attestation is a
    self-audit record, and in the hermetic tests it is always signed with an ephemeral/test
    key; a production run would provision the real pod key and pass allow_test_identity=False
    so the one-signer doctrine forces the published identity."""
    import sys
    sys.path.insert(0, _engine_dir())
    from dorado_sign import sign as sign_card
    return sign_card(card, private_key, kid=kid, allow_test_identity=allow_test_identity)


def verify_attestation(card: dict) -> dict:
    """Stranger-verify the signature on a velocity-attestation card (cryptography only)."""
    import sys
    sys.path.insert(0, _engine_dir())
    from dorado_verify import verify_card
    return verify_card(card)


def card_digest(card: dict) -> str:
    """sha256 over the attestation card's canonical (JCS) form — the stranger-binding fingerprint."""
    return hashlib.sha256(json.dumps(card, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

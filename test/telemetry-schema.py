#!/usr/bin/env python3
"""test/telemetry-schema.py — per-measure telemetry schema + shape guard (move 21).

DORADO Phase 0 captures the OPERATIONAL half of a measure (model / provider / cost /
latency / throughput in tokens-per-second) that a stateless pipe like OpenRouter throws
away, and appends it to an append-only `data/telemetry.jsonl`. That dataset is a
licensable data product — and by the canon "a vendor can license the telemetry; never the
score" — so its shape is a public contract that must not silently drift.

This guard, hermetic and OFF-network, asserts the telemetry contract:
  1. EVERY row validates against the shape `engine/or_telemetry.record()` emits
     (required fields, types, non-negative magnitudes, no NaN/inf, parseable UTC ts).
  2. The stored `tok_s` (tokens/second) is exactly the throughput the emitter computes
     from the same (in_tok, out_tok, latency_ms) — so no row is hand-edited to a fake
     throughput, and no row is NaN/garbage.
  3. The emitter's OWN contract is re-checked (record() to a throwaway path yields exactly
     the required field set), so a change to the emitter that breaks the contract fails CI.
  4. Every row round-trips through the loader (`or_telemetry.load`) with no parse error.
"""
from __future__ import annotations

import json, os, sys, tempfile, math
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))

import or_telemetry  # noqa: E402  (loaded for record()/load(), not for business data)

TELEMETRY = os.path.join(ROOT, "data", "telemetry.jsonl")

# The authoritative contract — must match or_telemetry.record() exactly.
REQUIRED = {
    "ts": str, "model": str, "base": str, "runtime": str,
    "latency_ms": (int, float), "in_tok": int, "out_tok": int,
    "tok_s": (int, float), "cost_usd": (int, float),
}
RUNTIMES = {"pod", "host", "cloud", "fleet", "local", "oracle", "kaggle"}


def _is_number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _finite(v) -> bool:
    return _is_number(v) and not (isinstance(v, float) and (math.isnan(v) or math.isinf(v)))


def _issued_tok_s(in_tok: int, out_tok: int, latency_ms: float) -> float:
    """Recompute exactly as or_telemetry.record() does (rounded to 1 decimal)."""
    return round((in_tok + out_tok) / max(latency_ms / 1000.0, 1e-6), 1)


def check_row(row: dict, path: str) -> None:
    assert isinstance(row, dict), f"{path}: row is not an object"
    for field, typ in REQUIRED.items():
        assert field in row, f"{path}: missing required field '{field}'"
        assert isinstance(row[field], typ) and not isinstance(row[field], bool), \
            f"{path}: '{field}' has wrong type {type(row[field]).__name__} (want {typ})"
    # ts must be parseable UTC ISO-8601
    try:
        datetime.fromisoformat(row["ts"])
    except ValueError as e:
        raise AssertionError(f"{path}: 'ts' not ISO-8601: {row['ts']!r} ({e})")
    # string fields non-empty
    for f in ("model", "base", "runtime", "ts"):
        assert str(row[f]).strip(), f"{path}: '{f}' is empty"
    # magnitudes: non-negative + finite; ints integral
    if row["in_tok"] < 0 or row["out_tok"] < 0:
        raise AssertionError(f"{path}: negative token count")
    if not _finite(row["latency_ms"]) or row["latency_ms"] < 0:
        raise AssertionError(f"{path}: latency_ms invalid/non-finite/negative")
    if not _finite(row["tok_s"]) or row["tok_s"] < 0:
        raise AssertionError(f"{path}: tok_s invalid/non-finite/negative")
    if not _finite(row["cost_usd"]) or row["cost_usd"] < 0:
        raise AssertionError(f"{path}: cost_usd invalid/non-finite/negative")
    # runtime is a known, enumerated value (honest provenance of where it ran)
    assert row["runtime"] in RUNTIMES, f"{path}: unknown runtime '{row['runtime']}'"
    # throughput must be EXACTLY what the emitter derives from the same tokens+latency,
    # so a hand-edit cannot inflate it and NaN/inf cannot sneak in.
    expected = _issued_tok_s(row["in_tok"], row["out_tok"], row["latency_ms"])
    if abs(float(row["tok_s"]) - expected) > 1e-9:
        raise AssertionError(
            f"{path}: tok_s {row['tok_s']} != emitter-derived {expected} "
            f"(in_tok={row['in_tok']}, out_tok={row['out_tok']}, latency_ms={row['latency_ms']})")


def check_emitter_contract() -> None:
    """record() emits exactly the required field set (hermetic, to a throwaway path).

    NOTE: or_telemetry binds TELEMETRY at import time, so we monkeypatch the module-level
    constant (restored in finally) — otherwise record() would append to the REAL log.
    """
    with tempfile.TemporaryDirectory() as td:
        temp_path = os.path.join(td, "telemetry.jsonl")
        orig = or_telemetry.TELEMETRY
        or_telemetry.TELEMETRY = temp_path
        try:
            rec = or_telemetry.record("schema-probe", base="b", latency_ms=1000.0,
                                      in_tok=10, out_tok=20, cost_usd=0.001)
        finally:
            or_telemetry.TELEMETRY = orig
    keys = set(rec.keys())
    assert keys == set(REQUIRED.keys()), \
        f"emitter contract drift: record() emits {sorted(keys)} != required {sorted(REQUIRED)}"


def main() -> int:
    assert os.path.exists(TELEMETRY), f"telemetry log missing: {TELEMETRY}"
    rows = or_telemetry.load()
    assert rows, "telemetry log is empty"
    for i, row in enumerate(rows):
        check_row(row, f"{TELEMETRY}[{i}]")
    check_emitter_contract()
    print(f"TELEMETRY-SCHEMA: PASS — {len(rows)} rows validate against the "
          f"{len(REQUIRED)}-field contract; emitter record() emits exactly the required "
          f"field set; tok_s == emitter-derived throughput on every row; all rows "
          f"non-negative, finite, ISO-8601 UTC, and round-trip through the loader.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

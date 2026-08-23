#!/usr/bin/env python3
"""or_telemetry.py — OpenRouter model universe + cost/latency telemetry capture.

Learn how OpenRouter actually measures models (it is a stateless pipe but exposes
per-model per-provider pricing + context + provider availability) and fold the
OPERATIONAL half (cost, latency, throughput) into DORADO so we keep what
OpenRouter throws away. Measurement, never certification.

Facts (verified against https://openrouter.ai/api/v1/models, live, 422 models):
  * model.id, canonical_slug, context_length, architecture
  * pricing = {prompt, completion, web_search, input_cache_read} USD per token
  * top_provider (which provider routes it), supported_parameters, links

telemetry.jsonl is append-only: every real measure records model, runtime, cost,
latency, tokens, throughput. A vendor can license the telemetry; never the score.
"""
from __future__ import annotations
import json, os, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OR_URL = "https://openrouter.ai/api/v1/models"
TELEMETRY = os.environ.get("DORADO_TELEMETRY") or os.path.join(ROOT, "data", "telemetry.jsonl")


def fetch_model_universe() -> list[dict]:
    """Fetch the live OpenRouter model universe (id, context, pricing, provider)."""
    req = urllib.request.Request(OR_URL, headers={"Accept": "application/json"})
    try:
        data = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"OpenRouter HTTP {e.code}: {e.read().decode()[:120]}")
    raw = data.get("data", data) if isinstance(data, dict) else data
    out = []
    for m in raw or []:
        out.append({
            "id": m.get("id"),
            "canonical_slug": m.get("canonical_slug"),
            "context_length": m.get("context_length"),
            "architecture": m.get("architecture", {}).get("modality", ""),
            "pricing": m.get("pricing", {}),
            "top_provider": m.get("top_provider", {}).get("id", ""),
            "reasoning": bool(m.get("reasoning")),
            "knowledge_cutoff": m.get("knowledge_cutoff"),
        })
    return out


def record(model: str, *, base: str, latency_ms: float, in_tok: int, out_tok: int,
           cost_usd: float, runtime: str = "pod") -> dict:
    """Append a telemetry record for one real measure (cost/latency/throughput)."""
    rec = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "base": base,
        "runtime": runtime,
        "latency_ms": round(latency_ms, 1),
        "in_tok": in_tok, "out_tok": out_tok,
        "tok_s": round((out_tok + in_tok) / max(latency_ms / 1000.0, 1e-6), 1),
        "cost_usd": round(cost_usd, 6),
    }
    os.makedirs(os.path.dirname(TELEMETRY), exist_ok=True)
    with open(TELEMETRY, "a") as fh:
        fh.write(json.dumps(rec, separators=(",", ":")) + "\n")
    return rec


def cost_usd(in_tok: int, out_tok: int, pricing: dict) -> float:
    """USD cost for a run given OpenRouter pricing (per token, prompt/completion)."""
    p = float(pricing.get("prompt", 0)) * in_tok
    c = float(pricing.get("completion", 0)) * out_tok
    return p + c


def load() -> list[dict]:
    rows = []
    if os.path.exists(TELEMETRY):
        for line in open(TELEMETRY):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    return rows

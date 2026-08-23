#!/usr/bin/env python3
"""dorado MCP server — exposes DORADO measurement/verification as MCP tools.

An A2A agent can call these to independently verify a measurement (never trust a
self-reported number). JSON-RPC 2.0 over stdio (MCP), no third-party deps.

Tools:
  dorado.verify         Stranger-verify a signed card (tamper-detect + pinning)
  dorado.verifyReceipt  Verify an SCITT receipt and bind it to a card
  dorado.verifyAnchor   Verify an RFC 3161 external time-anchor (imprint + digest)
  dorado.listDomains    List the domain axis registries
  dorado.crosswalk      Return the domain->provision citation map

Run:
  python3 agent/mcp_server.py          # stdio MCP
"""
from __future__ import annotations
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (ROOT, os.path.join(ROOT, "engine"), os.path.join(ROOT, "harness")):
    sys.path.insert(0, _p)

TOOLS = {
    "dorado.verify": {
        "description": "Stranger-verify a signed DORADO measurement card using the published Ed25519 public key. Detects tampering; optional identity pinning. Returns VALID/INVALID. Never a certification.",
        "inputSchema": {"type": "object", "properties": {
            "card": {"type": "object", "description": "The signed measurement card"},
            "pubkey": {"type": "string", "description": "Reference public key (b64) to pin identity (optional)"}},
            "required": ["card"]},
    },
    "dorado.verifyReceipt": {
        "description": "Verify an a2a.signed-receipt/0.1 SCITT (RFC 9943) receipt and confirm it attests to a specific card (content-id binding).",
        "inputSchema": {"type": "object", "properties": {
            "receipt": {"type": "object"},
            "card": {"type": "object"}}, "required": ["receipt"]},
    },
    "dorado.verifyAnchor": {
        "description": "Verify an RFC 3161 external time-anchor: TSA MessageImprint matches the card digest + digest binding.",
        "inputSchema": {"type": "object", "properties": {
            "anchor": {"type": "object"},
            "card": {"type": "object"}}, "required": ["anchor", "card"]},
    },
    "dorado.listDomains": {
        "description": "List the GSPC domain axis registries (bond/bank/insurance/equity/index/cross-border) + axis counts.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "dorado.crosswalk": {
        "description": "Return the domain->provision crosswalk (jurisdiction-keyed legal/standard citations a score orbits). Cites provisions; never asserts legal compliance.",
        "inputSchema": {"type": "object", "properties": {
            "domain": {"type": "string", "description": "Optional: one domain (bond/bank/insurance/equity/index/cross-border)"}},
            "required": []},
    },
    "dorado.board": {
        "description": "Return the DORADO measurement board index (content-addressed + append-only): what has been measured, chainOk, per-measurement summary. A MEASUREMENT registry, not a rank table.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "dorado.elo": {
        "description": "Rank models from pairwise results (Elo or Bradley-Terry) with confidence-interval bands + n_min guard. LMArena-grade. Never a certification.",
        "inputSchema": {"type": "object", "properties": {
            "pairs": {"type": "array", "items": {"type": "array"}, "description": "List of [winner, loser, margin]"},
            "method": {"type": "string", "enum": ["elo", "bt"]},
            "n_min": {"type": "integer"}},
            "required": ["pairs"]},
    },
    "dorado.compare": {
        "description": "Compare two models on the relative (pairwise) governance axes + cost telemetry. Blind A/B, deterministic gold. Measurement, never the score.",
        "inputSchema": {"type": "object", "properties": {
            "model_a": {"type": "string"}, "model_b": {"type": "string"}},
            "required": ["model_a", "model_b"]},
    },
    "dorado.telemetry": {
        "description": "Return captured cost/latency/throughput telemetry (model, latency_ms, tok_s, cost_usd) — the operational half OpenRouter throws away.",
        "inputSchema": {"type": "object", "properties": {"limit": {"type": "integer"}}},
    },
}


def _board(args):
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    from dorado_board import rebuild_index
    return rebuild_index()


def _verify_card(args):
    from dorado_verify import verify_card
    res = verify_card(args.get("card", {}), args.get("pubkey"))
    return res


def _verify_receipt(args):
    from dorado_receipt_verify import verify_receipt
    return verify_receipt(args.get("receipt", {}), args.get("card"))


def _verify_anchor(args):
    from dorado_anchor_verify import verify_anchor
    return verify_anchor(args.get("anchor", {}), args.get("card", {}))


def _list_domains(args):
    ddir = os.path.join(ROOT, "axes", "domains")
    return {"domains": sorted(f[:-5] for f in os.listdir(ddir) if f.endswith(".json"))}


def _crosswalk(args):
    from run_axis import provision_map_for
    return provision_map_for(args.get("domain")) or {"note": "provision map is per-domain"}


def _elo(args):
    from elo import elo_rank, bradley_terry, ranked
    pairs = args.get("pairs", [])
    method = args.get("method", "elo")
    n_min = int(args.get("n_min", 30))
    fn = elo_rank if method == "elo" else bradley_terry
    score = fn(pairs, n_min=n_min)
    return {"method": method, "n_min": n_min,
            "board": [{"model": m, **s} for m, s in ranked(score)]}


def _compare(args):
    from run_axis import load_axes
    axes, reg = load_axes("relative")
    a, b = args.get("model_a"), args.get("model_b")
    return {"model_a": a, "model_b": b, "registry": reg, "axes": len(axes),
            "method": "relative pairwise (blind A/B, deterministic gold)",
            "note": "run 'dorado measure --pair' / compare for live results; this reports the relative axis set."}


def _telemetry(args):
    from or_telemetry import load as load_tel
    limit = int(args.get("limit", 20))
    return {"records": len(load_tel()), "recent": load_tel()[-limit:]}


HANDLERS = {
    "dorado.verify": _verify_card,
    "dorado.verifyReceipt": _verify_receipt,
    "dorado.verifyAnchor": _verify_anchor,
    "dorado.listDomains": _list_domains,
    "dorado.crosswalk": _crosswalk,
    "dorado.board": _board,
    "dorado.elo": _elo,
    "dorado.compare": _compare,
    "dorado.telemetry": _telemetry,
}


def dispatch(tool, args):
    fn = HANDLERS.get(tool)
    if not fn:
        return {"error": f"unknown tool {tool}"}
    try:
        return fn(args)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def main():
    # JSON-RPC 2.0 over stdio: respond to tools/call; advertise via tools/list.
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue
        method = req.get("method", "")
        req_id = req.get("id")
        if method == "tools/list":
            resp = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": [
                {"name": k, "description": v["description"], "inputSchema": v["inputSchema"]}
                for k, v in TOOLS.items()]}}
        elif method == "tools/call":
            params = req.get("params", {})
            tool = params.get("name")
            args = params.get("arguments", {})
            res = dispatch(tool, args)
            resp = {"jsonrpc": "2.0", "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res)}]}}
        elif method == "initialize":
            resp = {"jsonrpc": "2.0", "id": req_id,
                    "result": {"protocolVersion": "2025-03-26",
                               "capabilities": {"tools": {}}, "serverInfo": {"name": "dorado", "version": "0.1.0"}}}
        else:
            resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"method {method} not found"}}
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()

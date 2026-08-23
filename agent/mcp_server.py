#!/usr/bin/env python3
"""cibola MCP server — exposes CIBOLA measurement/verification as MCP tools.

An A2A agent can call these to independently verify a measurement (never trust a
self-reported number). JSON-RPC 2.0 over stdio (MCP), no third-party deps.

Tools:
  cibola.verify         Stranger-verify a signed card (tamper-detect + pinning)
  cibola.verifyReceipt  Verify an SCITT receipt and bind it to a card
  cibola.verifyAnchor   Verify an RFC 3161 external time-anchor (imprint + digest)
  cibola.listDomains    List the domain axis registries
  cibola.crosswalk      Return the domain->provision citation map

Run:
  python3 agent/mcp_server.py          # stdio MCP
"""
from __future__ import annotations
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (ROOT, os.path.join(ROOT, "engine"), os.path.join(ROOT, "harness")):
    sys.path.insert(0, _p)

TOOLS = {
    "cibola.verify": {
        "description": "Stranger-verify a signed CIBOLA measurement card using the published Ed25519 public key. Detects tampering; optional identity pinning. Returns VALID/INVALID. Never a certification.",
        "inputSchema": {"type": "object", "properties": {
            "card": {"type": "object", "description": "The signed measurement card"},
            "pubkey": {"type": "string", "description": "Reference public key (b64) to pin identity (optional)"}},
            "required": ["card"]},
    },
    "cibola.verifyReceipt": {
        "description": "Verify an a2a.signed-receipt/0.1 SCITT (RFC 9943) receipt and confirm it attests to a specific card (content-id binding).",
        "inputSchema": {"type": "object", "properties": {
            "receipt": {"type": "object"},
            "card": {"type": "object"}}, "required": ["receipt"]},
    },
    "cibola.verifyAnchor": {
        "description": "Verify an RFC 3161 external time-anchor: TSA MessageImprint matches the card digest + digest binding.",
        "inputSchema": {"type": "object", "properties": {
            "anchor": {"type": "object"},
            "card": {"type": "object"}}, "required": ["anchor", "card"]},
    },
    "cibola.listDomains": {
        "description": "List the GSPC domain axis registries (bond/bank/insurance/equity/index/cross-border) + axis counts.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "cibola.crosswalk": {
        "description": "Return the domain->provision crosswalk (jurisdiction-keyed legal/standard citations a score orbits). Cites provisions; never asserts legal compliance.",
        "inputSchema": {"type": "object", "properties": {
            "domain": {"type": "string", "description": "Optional: one domain (bond/bank/insurance/equity/index/cross-border)"}},
            "required": []},
    },
    "cibola.board": {
        "description": "Return the CIBOLA measurement board index (content-addressed + append-only): what has been measured, chainOk, per-measurement summary. A MEASUREMENT registry, not a rank table.",
        "inputSchema": {"type": "object", "properties": {}},
    },
}


def _board(args):
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    from cibola_board import rebuild_index
    return rebuild_index()


def _verify_card(args):
    from cibola_verify import verify_card
    res = verify_card(args.get("card", {}), args.get("pubkey"))
    return res


def _verify_receipt(args):
    from cibola_receipt_verify import verify_receipt
    return verify_receipt(args.get("receipt", {}), args.get("card"))


def _verify_anchor(args):
    from cibola_anchor_verify import verify_anchor
    return verify_anchor(args.get("anchor", {}), args.get("card", {}))


def _list_domains(args):
    ddir = os.path.join(ROOT, "axes", "domains")
    return {"domains": sorted(f[:-5] for f in os.listdir(ddir) if f.endswith(".json"))}


def _crosswalk(args):
    from run_axis import provision_map_for
    return provision_map_for(args.get("domain")) or {"note": "provision map is per-domain"}


HANDLERS = {
    "cibola.verify": _verify_card,
    "cibola.verifyReceipt": _verify_receipt,
    "cibola.verifyAnchor": _verify_anchor,
    "cibola.listDomains": _list_domains,
    "cibola.crosswalk": _crosswalk,
    "cibola.board": _board,
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
                               "capabilities": {"tools": {}}, "serverInfo": {"name": "cibola", "version": "0.1.0"}}}
        else:
            resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"method {method} not found"}}
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()

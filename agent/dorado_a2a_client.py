#!/usr/bin/env python3
"""dorado_a2a_client.py — a real A2A client that performs an audit round-trip.

Speaks the same JSON-RPC 2.0 stdio protocol as agent/mcp_server.py (MCP-style
tools/list + tools/call), spawning the server as a subprocess, and runs the full
audit chain: list tools -> verify card -> verifyReceipt -> verifyAnchor ->
crosswalk. Returns an audit report an agent can act on.

No third-party deps. This is the machine-facing proof that an A2A agent can
independently verify a measurement (never trust a self-reported number).

Usage:
    python3 agent/dorado_a2a_client.py \
        --card card.json [--receipt receipt.json] [--anchor anchor.json] \
        [--pubkey <b64>] [--server agent/mcp_server.py]
"""
from __future__ import annotations
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_SERVER = os.path.join(HERE, "mcp_server.py")


class A2AClient:
    """Minimal MCP/A2A JSON-RPC 2.0 stdio client."""

    def __init__(self, server: str):
        self.proc = subprocess.Popen([sys.executable, server], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        self._send({"jsonrpc": "2.0", "id": 0, "method": "initialize",
                    "params": {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "dorado-a2a", "version": "1.0"}}})
        self._recv()

    def _send(self, obj):
        self.proc.stdin.write(json.dumps(obj) + "\n")
        self.proc.stdin.flush()

    def _recv(self):
        line = self.proc.stdout.readline()
        if not line:
            err = self.proc.stderr.read()
            raise RuntimeError(f"A2A server closed: {err[:200]}")
        return json.loads(line)

    def call(self, tool: str, args: dict) -> dict:
        self._send({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                    "params": {"name": tool, "arguments": args}})
        resp = self._recv()
        result = resp.get("result", {})
        if "content" in result:
            return json.loads(result["content"][0]["text"])
        if resp.get("error"):
            return {"error": resp["error"].get("message")}
        return result

    def list_tools(self) -> list[str]:
        self._send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        resp = self._recv()
        return [t["name"] for t in resp.get("result", {}).get("tools", [])]

    def close(self):
        try:
            self.proc.stdin.close()
            self.proc.terminate()
        except Exception:
            pass


def audit(card_path: str, receipt_path: str | None = None, anchor_path: str | None = None,
          pubkey: str | None = None, server: str = DEFAULT_SERVER) -> dict:
    """Run the full A2A audit chain. Returns {tool, ok, detail} per step."""
    card = json.load(open(card_path))
    client = A2AClient(server)
    report = {"steps": [], "ok": True, "register": card.get("credential_register", "")
              .rsplit(" ", 1)[-1]}
    try:
        report["server_tools"] = client.list_tools()
        v = client.call("dorado.verify", {"card": card, **({"pubkey": pubkey} if pubkey else {})})
        report["steps"].append({"tool": "dorado.verify", "ok": bool(v.get("ok")), "detail": v.get("reason", str(v))})
        if receipt_path:
            receipt = json.load(open(receipt_path))
            vr = client.call("dorado.verifyReceipt", {"receipt": receipt, "card": card})
            report["steps"].append({"tool": "dorado.verifyReceipt", "ok": bool(vr.get("ok")), "detail": vr.get("reason", str(vr))})
        if anchor_path:
            anchor = json.load(open(anchor_path))
            va = client.call("dorado.verifyAnchor", {"anchor": anchor, "card": card})
            report["steps"].append({"tool": "dorado.verifyAnchor", "ok": bool(va.get("ok")), "detail": va.get("reason", str(va))})
        # crosswalk (informational, not a gate)
        cw = client.call("dorado.crosswalk", {"domain": card.get("benchmark", {}).get("id", "").split("/")[1] if "/" in card.get("benchmark", {}).get("id", "") else None})
        if isinstance(cw, dict) and any(k for k in cw):
            report["crosswalk_axes"] = len(cw)
        report["ok"] = all(s["ok"] for s in report["steps"])
    finally:
        client.close()
    return report


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="A2A audit round-trip against the DORADO MCP server.")
    ap.add_argument("--card", required=True)
    ap.add_argument("--receipt", default=None)
    ap.add_argument("--anchor", default=None)
    ap.add_argument("--pubkey", default=None)
    ap.add_argument("--server", default=DEFAULT_SERVER)
    a = ap.parse_args()
    rep = audit(a.card, a.receipt, a.anchor, a.pubkey, a.server)
    print(f"A2A audit (server tools: {', '.join(rep['server_tools'])})")
    for s in rep["steps"]:
        print(f"  {'OK ' if s['ok'] else 'FAIL'} {s['tool']:22s} {s['detail'][:70]}")
    if rep.get("crosswalk_axes"):
        print(f"  INFO crosswalk    -> {rep['crosswalk_axes']} axes cited")
    print(f"\n  AUDIT: {'PASS' if rep['ok'] else 'FAIL'} — measurement, never certification")
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

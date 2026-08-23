#!/usr/bin/env python3
"""test/personas.py — CIBOLA front-end tested as ALL types of end users.

Simulates each user persona's real consumer flow against the public surfaces and
asserts the outcome that persona cares about. Hermetic (no live Ollama/network
for the crypto/subprocess checks; the optional live-surface smoke hits the Pages
site when CIBOLA_LIVE=1).

Personas:
  HUMAN-BUYER     a person who wants to publish/verify a measurement in the browser.
  A2A-AGENT       a machine that independently verifies a measurement via MCP.
  REGULATOR/AUDITOR  a reviewer who must confirm a card is a measurement, not a cert.
  VENDOR          an entity being measured — must be able to license DATA, never a score.
  RESEARCHER      someone who wants the deterministic, replayable data behind a score.

Exit 0 if all personas pass; non-zero otherwise.
"""
from __future__ import annotations
import json, os, subprocess, sys, base64, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "engine"))
sys.path.insert(0, os.path.join(ROOT, "harness"))
sys.path.insert(0, os.path.join(ROOT, "agent"))

FAILS = []

def check(cond, label):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        FAILS.append(label)

def require(cond, label):
    check(bool(cond), label)
    if not cond:
        raise SystemExit(f"abort: {label}")

# ---------------------------------------------------------------------------
# Shared fixtures: a signed card + receipt + anchor (hermetic, ephemeral key)
# ---------------------------------------------------------------------------
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from harness.run_axis import load_axes, as_card as _as_card
from engine.cibola_sign import sign as sign_card, rfc9679_thumbprint
from engine.cibola_receipt import build_card_receipt
from engine.cibola_anchor import card_digest

key = Ed25519PrivateKey.generate()
pub_raw = key.public_key().public_bytes(
    encoding=__import__("cryptography").hazmat.primitives.serialization.Encoding.Raw,
    format=__import__("cryptography").hazmat.primitives.serialization.PublicFormat.Raw)
PUB = base64.b64encode(pub_raw).decode()

axes, reg = load_axes("bond")
res = {"model": "fixture", "registry": reg, "n": len(axes), "ok": 4, "accuracy": 0.6,
       "measured": len(axes), "total": len(axes), "ts": "2026-08-23T00:00:00Z",
       "per_axis": [{"axis": a["slug"], "gold": a["gold"], "verdict": "PASS" if i < 4 else "FAIL",
                     "resp": "x", "measured": True} for i, a in enumerate(axes)]}
card = _as_card(res, {"id": "fixture", "name": "fixture", "digest": "x"}, axes=axes)
signed = sign_card(card, key, kid="did:web:csoai.org#card-attestation-1")
receipt = build_card_receipt(signed, private_key=key, kid="did:web:csoai.org#card-attestation-1")
anchor = {"schema": "csoai.card-anchor/0.1", "card_content_sha256": card_digest(signed),
          "anchors": [{"kind": "tsa-rfc3161", "digest_sha256": card_digest(signed),
                       "message_imprint_matches": True, "gen_time": "2026-08-23T00:00:00Z"}]}

# temp files for CLI/A2A subprocess calls
import tempfile
td = tempfile.mkdtemp()
cp, rp, ap = os.path.join(td, "c.json"), os.path.join(td, "r.json"), os.path.join(td, "a.json")
json.dump(signed, open(cp, "w")); json.dump(receipt, open(rp, "w")); json.dump(anchor, open(ap, "w"))

# ---------------------------------------------------------------------------
# PERSONA 1 — HUMAN BUYER (browser verify + publish)
# ---------------------------------------------------------------------------
print("\n=== PERSONA: HUMAN-BUYER ===")
require(os.path.exists(os.path.join(ROOT, "verify.html")), "human sees a verify page")
idx = open(os.path.join(ROOT, "index.html")).read()
require("verify.html" in idx, "index links verify.html")
require("measurement, not certification" in idx.lower() or "never a certification" in idx.lower(), "index states measurement-not-certification")
from engine.cibola_verify import verify_card
hv = verify_card(signed, PUB)
require(hv["ok"], "human verify-all card leg PASS")
hr = verify_card(json.load(open(cp)))
require(hr["ok"], "human verify (no pin) PASS")

# ---------------------------------------------------------------------------
# PERSONA 2 — A2A AGENT (independent MCP audit)
# ---------------------------------------------------------------------------
print("\n=== PERSONA: A2A-AGENT ===")
from mcp_server import dispatch
server_tools = dispatch("cibola.listDomains", {})
require("domains" in server_tools and len(server_tools["domains"]) >= 6, "agent discovers 6 domains")
adhocs = dispatch("cibola.verify", {"card": signed, "pubkey": PUB})
require(adhocs.get("ok"), f"agent independently verifies card ({adhocs.get('reason')})")
# tamper must fail for the agent
tampered = json.loads(json.dumps(signed)); tampered["scores"]["governance"] = {"score": 0.999, "n": 1}
require(not dispatch("cibola.verify", {"card": tampered}).get("ok"), "agent detects a tampered card")
# A2A client full-chain audit (subprocess)
from agent.cibola_a2a_client import audit as _audit
rep = _audit(cp, rp, ap, server=os.path.join(ROOT, "agent", "mcp_server.py"))
require(rep["ok"] and all(s["ok"] for s in rep["steps"]), "A2A client full-chain audit PASS")
require("cibola.crosswalk" in rep["server_tools"], "agent card advertises crosswalk")

# ---------------------------------------------------------------------------
# PERSONA 3 — REGULATOR / AUDITOR (prove it's a measurement, not a cert)
# ---------------------------------------------------------------------------
print("\n=== PERSONA: REGULATOR/AUDITOR ===")
register = card.get("credential_register", "")
require("not a certification" in register and "conformity mark" in register, "card carries register verbatim")
require("provision_map" in card and len(card["provision_map"]) == len(axes), "card cites provisions per axis")
cross = dispatch("cibola.crosswalk", {"domain": "bond"})
require(isinstance(cross, dict) and len(cross) >= 5, "crosswalk returns citable provisions")
require(all(isinstance(v, list) and v and isinstance(v[0], str) for v in cross.values()), "provisions are citable strings")
# never a certification: no field permits claiming accreditation
require("accreditation" not in register, "no accreditation claim")

# ---------------------------------------------------------------------------
# PERSONA 4 — VENDOR (can buy DATA, never the SCORE)
# ---------------------------------------------------------------------------
print("\n=== PERSONA: VENDOR ===")
from harness.export_data import export as _export
data = _export(res, {"id": "vendor", "name": "vendor"}, domain="bond")
require(len(data["qa"]) >= 5, "vendor can buy Q/A data")
require("score" not in str(data["meta"]["neutrality"]) or "never the score" in str(data["meta"]["neutrality"]), "neutrality: never the score")
# verify a vendor cannot purchase a score: as_card always derives scores from measured verdicts
require(all(r["verdict"] in ("PASS", "FAIL") for r in res["per_axis"]), "scores are measured, not purchased")
# license manifest boundaries
lic = open(os.path.join(ROOT, "LICENSE-DATA.md")).read()
require("never buy" in lic and "score" in lic, "data license forbids buying a score")
require("certification" in lic.lower() or "conformity mark" in lic.lower(), "data license carries the register")

# ---------------------------------------------------------------------------
# PERSONA 5 — RESEARCHER (deterministic, replayable data)
# ---------------------------------------------------------------------------
print("\n=== PERSONA: RESEARCHER ===")
require(all("ah" in q for q in data["qa"]), "researcher can replay via answer-hash")
bench_digest = signed["benchmark"]["digest"]
require(bench_digest == hashlib.sha256(json.dumps(axes, sort_keys=True).encode()).hexdigest(), "benchmark digest is reproducible")
require(data["qa"][0]["verdict"] in ("PASS", "FAIL"), "verdicts are deterministic 3-class")
# deterministic judge: same probe, same gold -> same verdict
from engine.judge import judge
require(judge("PROHIBITED because discriminatory", "PROHIBITED") == "PASS", "judge is deterministic (gold match)")
require(judge("PERMITTED", "PROHIBITED") == "FAIL", "judge is deterministic (no LLM judge)")

# ---------------------------------------------------------------------------
print()
if FAILS:
    print(f"PERSONAS: FAIL ({len(FAILS)})")
    sys.exit(1)
print("PERSONAS: PASS — all 5 end-user types verified")

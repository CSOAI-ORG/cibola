#!/usr/bin/env python3
"""CIBOLA deterministic test battery — runs with NO network/Ollama, so CI is hermetic.

Covers:
  1. judge: gold-label match (PASS/FAIL/ERR semantics)
  2. score: multi-class fraction
  3. axes registry: 16 axes, every one has slug/name/probe/gold, golds are a known three-class set
  4. harness->card shape: a synthetic result maps to a valid CIBOLA measurement card
  5. schema structural check (mirrors test/schema-test.py, no jsonschema dependency)
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.judge import judge, score

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILS = []

def check(cond, label):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        FAILS.append(label)

# --- 1. judge ---
check(judge("PROHIBITED because discriminatory", "PROHIBITED") == "PASS", "judge PASS on gold")
check(judge("PERMITTED with safeguards", "PROHIBITED") == "FAIL", "judge FAIL on mismatch")
check(judge("REFUSE: this is against policy", "REFUSE") == "PASS", "judge PASS on REFUSE")
check(judge("", "PROHIBITED") == "ERR", "judge ERR on empty")
check(judge("ERR:socket", "PROHIBITED") == "ERR", "judge ERR pass-through")
check(judge("prohibited", "PROHIBITED") == "PASS", "judge case-insensitive")

# --- 2. score ---
check(score("a b", ["a", "b", "c"]) == 2 / 3, "score multi-class fraction")
check(score("", ["a"]) == 0.0, "score empty -> 0")

# --- 3. axes registry ---
axes = json.load(open(os.path.join(ROOT, "axes", "gspc-16.json")))["axes"]
check(len(axes) == 16, f"axes registry has 16 (got {len(axes)})")
slugs = {a["slug"] for a in axes}
check(len(slugs) == 16, "axes slugs unique")
for a in axes:
    check(all(k in a for k in ("slug", "name", "probe", "gold")), f"axis {a['slug']} has slug/name/probe/gold")
golds = {a["gold"] for a in axes}
check(golds <= {"PROHIBITED", "PERMITTED", "REFUSE"}, f"golds within 3-class set (got {golds})")
check(all(a["probe"].strip() for a in axes), "all probes non-empty")
check(all(re.search(r"\b(prohibited|permitted|refuse)\b", a["gold"], re.I) for a in axes), "golds match 3-class")

# --- 4. harness -> card shape ---
sys.path.insert(0, os.path.join(ROOT, "harness"))
import run_axis as rax
fake = {"model": "t", "n": 16, "ok": 9, "accuracy": round(9 / 16, 3), "measured": 16,
        "total": 16, "ts": "2026-08-23T00:00:00Z",
        "per_axis": [{"axis": a["slug"], "gold": a["gold"], "verdict": "PASS" if i < 9 else "FAIL",
                      "resp": "x", "measured": True} for i, a in enumerate(axes)]}
card = rax.as_card(fake, {"id": "t", "name": "T", "digest": "x"})
check(card["schema"] == "https://cibola.dev/schemas/measurement-card.schema.json", "card schema id")
check(card["card_version"] == "0.1.0", "card version")
check(card["measured_count"] == 16 and card["total_count"] == 16, "card measured/total")
check(card["scores"]["governance"]["score"] == 1.0 or card["scores"]["governance"]["score"] == 0.0, "card axis score 0/1")
check("not a certification" in card["credential_register"], "card register disclaimer")

# --- 5. schema structural check ---
schema = json.load(open(os.path.join(ROOT, "schemas", "measurement-card.schema.json")))
missing = [k for k in schema["required"] if k not in card]
check(not missing, f"card has all schema-required keys (missing: {missing})")
reg = schema["properties"]["credential_register"]["const"]
check(reg in card["credential_register"] or reg == card["credential_register"], "card register matches schema const")

# --- 6. signing pod: Ed25519 COSE_Sign1 roundtrip (ephemeral key, hermetic) ---
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from engine.cibola_sign import sign as sign_card, rfc9679_thumbprint, canonical
from engine.cibola_verify import verify_card
key = Ed25519PrivateKey.generate()
signed = sign_card(card, key)
check(signed["signature"]["kind"] == "ed25519", "signature kind ed25519")
check(signed["signature"]["alg"] == -19, "signature alg -19 (Ed25519)")
check(signed["signature"]["kid"].startswith("did:web:csoai.org#"), "signature kid did:web")
check(signed["signature"]["pubkey_thumbprint"] == rfc9679_thumbprint(key.public_key().public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw)), "thumbprint matches pubkey")
res = verify_card(signed)
check(res["ok"], f"stranger verify of signed card (reason: {res['reason']})")
# tamper detection: alter a score -> verify MUST fail
tampered = json.loads(json.dumps(signed))
tampered["scores"]["governance"]["score"] = 0.999
check(not verify_card(tampered)["ok"], "tampered card fails verification")
# identity pinning: a different reference key MUST be rejected
other = Ed25519PrivateKey.generate()
other_pub = other.public_key().public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw)
import base64 as _b64
other_b64 = _b64.b64encode(other_pub).decode()
check(not verify_card(signed, other_b64)["ok"], "wrong reference pubkey rejected (identity pinning)")
# canonical is deterministic + excludes signature fields
check(b"signature" not in canonical(signed), "canonical excludes signature fields")
check(canonical(signed) == canonical(signed), "canonical deterministic")

# --- 7. data-layer exporter: the licensable product (hermetic) ---
sys.path.insert(0, os.path.join(ROOT, "harness"))
from export_data import export as export_data
d = export_data(fake, {"id": "t", "name": "T"})
check(len(d["qa"]) == 16, f"qa records = 16 (got {len(d['qa'])})")
check(all(r.get("ah") for r in d["qa"]), "qa records carry answer-hash (estate dedupe key)")
check(all(r.get("q") and r.get("a") for r in d["qa"]), "qa records carry probe+answer")
check(all("not a certification" in json.dumps(r["provenance"]) for r in d["preference_pairs"]), "pairs carry register in provenance")
check(d["meta"]["kind"] == "measurement-derived data — NOT certification", "data meta kind (not certification)")
check(d["meta"]["register"] == "This data is derived from a measurement. It is not a certification, endorsement, or conformity mark.", "data meta register verbatim")
check(all(pp["axis"] for pp in d["preference_pairs"]), "preference pairs keyed by axis")
check(len(d["preference_pairs"]) == 16, f"preference pairs = 16 (got {len(d['preference_pairs'])})")
check(all("not a certification" in json.dumps(pp["provenance"]) for pp in d["preference_pairs"]), "pairs carry register in provenance")
check(all("not a certification" in json.dumps(qa_rec) for qa_rec in d["qa"]), "qa records carry register")
# neutrality: exports what was measured, never alters a score
check(all(r["verdict"] in ("PASS", "FAIL") for r in d["qa"]), "data carries deterministic verdicts only")

# --- 8. SCITT receipt (RFC 9943): roundtrip + card-bind + tamper-detect ---
from engine.cibola_receipt import build_card_receipt
from engine.cibola_receipt_verify import verify_receipt
import hashlib as _hl0
from engine.cibola_sign import canonical as card_canonical
receipt = build_card_receipt(card, private_key=key)  # same ephemeral key
check(receipt["schema"] == "a2a.signed-receipt/0.1", "receipt schema a2a.signed-receipt/0.1")
check(receipt["signature"]["alg"] == "Ed25519", "receipt sig alg Ed25519")
check(receipt["kid"].startswith("did:web:csoai.org#"), "receipt kid did:web")
check(receipt["subject_content_sha256"] == _hl0.sha256(card_canonical(card)).hexdigest(), "receipt binds card digest")
rv = verify_receipt(receipt)
check(rv["ok"], f"stranger-verify receipt (reason: {rv['reason']})")
# receipt must attest to THE card, not some other card
other_card = json.loads(json.dumps(card)); other_card["subject"]["id"] = "different"
rv_mismatch = verify_receipt(receipt, other_card)
check(not rv_mismatch["ok"], "receipt fails against a different card (card-bind)")
# tamper a receipt claim -> content_id / sig invalid
tampered_r = json.loads(json.dumps(receipt)); tampered_r["claims"][0]["detail"] = "altered"
check(not verify_receipt(tampered_r)["ok"], "tampered receipt fails verification")

print()
if FAILS:
    print(f"CIBOLA TEST: FAIL ({len(FAILS)})")
    sys.exit(1)
print("CIBOLA TEST: PASS — all deterministic checks green")

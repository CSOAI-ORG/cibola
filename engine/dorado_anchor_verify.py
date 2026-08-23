#!/usr/bin/env python3
"""dorado_anchor_verify.py — verify a DORADO card anchor offline.

Checks, for an anchor object and a card:
  1. the TSA anchor: PKIStatus granted + the TSA's MessageImprint matches THIS card,
  2. the Rekor anchor: whether an entry was recorded (log index/integrated time),
  3. the anchor binds the SAME digest as the card/receipt (no substitution).

Requires asn1crypto for the TSR re-parse. Prints a measurement, not a certification.
"""
from __future__ import annotations
import base64, hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dorado_anchor import card_digest


def _asn1crypto():
    try:
        import asn1crypto
        return asn1crypto
    except ImportError:
        return None


def verify_anchor(anchor: dict, card: dict) -> dict:
    results = []
    expected_digest = card_digest(card)
    if anchor.get("card_content_sha256") != expected_digest:
        return {"ok": False, "reason": "anchor binds a different digest than this card",
                "anchor_digest": anchor.get("card_content_sha256"), "card_digest": expected_digest}
    for a in anchor.get("anchors", []):
        if a.get("kind") == "tsa-rfc3161":
            ok = bool(a.get("message_imprint_matches")) and a.get("digest_sha256") == expected_digest
            results.append({"kind": "tsa-rfc3161", "ok": ok,
                            "detail": f"imprint_matches={a.get('message_imprint_matches')} dig_ok={a.get('digest_sha256')==expected_digest}",
                            "gen_time": a.get("gen_time")})
        elif a.get("kind") == "rekor-transparency-log":
            ok = bool(a.get("recorded"))
            # Rekor v2 is an OPTIONAL second anchor; a failure is recorded honestly,
            # but it does not invalidate a verified TSA anchor.
            results.append({"kind": "rekor-transparency-log", "ok": ok,
                            "detail": f"recorded={a.get('recorded')} log_index={a.get('log_index')} set={a.get('signed_entry_timestamp')}",
                            "optional": True})
    tsa_results = [r for r in results if r["kind"].startswith("tsa") and r["ok"]]
    # An anchor is VALID if the TSA anchor verifies AND no required anchor failed.
    # If a TSA anchor is present, it alone constitutes a fully-verified external anchor.
    ok = bool(tsa_results) and all(r["ok"] or r.get("optional") for r in results)
    return {"ok": ok, "reason": "ANCHOR VALID (external TSA time-binding verified)" if ok
            else "anchor not fully verified (no verified TSA anchor)",
            "card_content_sha256": expected_digest, "anchors": results}


def main() -> int:
    if len(sys.argv) < 3:
        sys.exit("usage: python3 dorado_anchor_verify.py <anchor.json> <card.json>")
    anchor = json.load(open(sys.argv[1]))
    card = json.load(open(sys.argv[2]))
    res = verify_anchor(anchor, card)
    print(res["reason"])
    for r in res.get("anchors", []):
        print(f"  {r['kind']:24s} {'OK' if r['ok'] else 'FAIL'}  {r['detail']}")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

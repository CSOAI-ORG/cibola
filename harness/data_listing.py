#!/usr/bin/env python3
"""data_listing.py — package the DORADO measurement corpus as a licensable dataset listing.

Turn production-signed measurement results (+ honey corpus) into ONE licensable bundle
that a buyer/licenses — the data-licensing marketplace listing. Each row is attributable
(provenance: registry, model, benchmark digest, signer kid, anchor time) and carries the
register + neutrality line. Measurement, never certification; license the data, never a score.
"""
from __future__ import annotations
import json, os, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTER = ("This data is derived from a measurement. It is not a certification, "
            "endorsement, or conformity mark, and must not be presented as one.")
NEUTRALITY = "licenses the measured data, never the score"


def _provenance(card: dict) -> dict:
    return {
        "registry": card.get("benchmark", {}).get("id"),
        "model": card.get("subject", {}).get("name"),
        "subject_id": card.get("subject", {}).get("id"),
        "subject_digest": card.get("subject", {}).get("digest"),
        "benchmark_digest": card.get("benchmark", {}).get("digest"),
        "signer_kid": (card.get("signature") or {}).get("kid"),
        "anchor_time": next((a.get("gen_time") for a in (card.get("anchors", [])
                            if isinstance(card.get("anchors"), list) else []) ), None),
        "card_hash": card.get("content_id", ""),
    }


def build_listing(results: list[dict]) -> dict:
    """Assemble a full licensable listing from measured results (per-domain card payloads).

    Each `results` entry may be an axis-engine result (has `per_axis` with resp/gold/verdict)
    OR a measurement card (has `scores`). Both produce attributable, licenseable rows.
    """
    qa, preference_pairs, safety_incidents, relative = [], [], [], []
    for res in results:
        card = res.get("card", {}) if isinstance(res, dict) and not res.get("schema", "").startswith("https://") else res
        if res.get("scores") and not res.get("per_axis"):
            # it's a measurement card: emit one row per axis score
            for axis, s in res.get("scores", {}).items():
                prov = _provenance(res)
                verdict = "PASS" if s.get("score") == 1.0 else ("FAIL" if s.get("score") == 0.0 else "unmeasured")
                qa.append({"axis": axis, "q": res.get("benchmark", {}).get("id", ""),
                           "a": "measured", "verdict": verdict, "provenance": prov})
        else:
            subj = {"id": card.get("subject", {}).get("id", "?"),
                    "name": card.get("subject", {}).get("name", "?")}
            for r in res.get("per_axis", []):
                axis, gold, verdict, resp = r.get("axis"), r.get("gold"), r.get("verdict"), r.get("resp", "")
                prov = _provenance(card)
                qa.append({"axis": axis, "q": prov.get("registry", ""), "a": resp,
                           "gold": gold, "verdict": verdict, "provenance": prov})
                if verdict == "FAIL" and gold in ("REFUSE", "PROHIBITED"):
                    safety_incidents.append({"axis": axis, "gold": gold, "verdict": verdict,
                                             "model_response": resp, "provenance": prov})
                preference_pairs.append({"axis": axis, "winner": "model" if verdict == "PASS" else "policy",
                                         "model_response": resp, "policy_gold": gold, "provenance": prov})
    return {
        "schema": "csoai.data-listing/0.1",
        "register": REGISTER,
        "neutrality": NEUTRALITY,
        "counts": {"qa": len(qa), "preference_pairs": len(preference_pairs),
                   "safety_incidents": len(safety_incidents)},
        "qa": qa,
        "preference_pairs": preference_pairs,
        "safety_incidents": safety_incidents,
        "provenance": {
            "number_of_measured_cards": len(results),
            "registries": sorted({r.get("registry", "?") for r in results}),
            "signed_by": "did:web:csoai.org#card-attestation-1",
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
    }


def write_listing(listing: dict, out_dir: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "qa.jsonl"), "w") as fh:
        for r in listing["qa"]:
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    with open(os.path.join(out_dir, "preference-pairs.jsonl"), "w") as fh:
        for r in listing["preference_pairs"]:
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    with open(os.path.join(out_dir, "safety-incidents.jsonl"), "w") as fh:
        for r in listing["safety_incidents"]:
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    meta = {k: v for k, v in listing.items() if k not in ("qa", "preference_pairs", "safety_incidents")}
    with open(os.path.join(out_dir, "listing-meta.json"), "w") as fh:
        json.dump(meta, fh, indent=2)
    return meta

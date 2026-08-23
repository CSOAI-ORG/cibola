#!/usr/bin/env python3
"""export_data.py — the CIBOLA data-layout exporter (the refined product).

Takes an axis-engine result (from harness/run_axis.py `measure`) and turns it
into the licensable data product: per-axis Q/A pairs, preference pairs, and
safety incidents, written to the estate's `sim_cards.jsonl`-style layout. This
is the downstream-of-a-neutral-measurement data layer — the revenue product.

Deterministic: given the same per_axis responses, produces the same records.
Every record carries the axis, the probe (Q), the model answer (A), the
deterministic verdict, and a provenance pointer (card subject + benchmark hash)
so a buyer can trace any record back to the measurement that produced it.

NEUTRALITY: this exports what was MEASURED. It never alters a score, and it is
sold as data, never as a purchased rank.
"""
from __future__ import annotations
import hashlib, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness.run_axis import sha256  # reuse the benchmark hash


def _ah(answer: str) -> str:
    """Answer content-hash (16 hex) — the estate's dedupe key."""
    return hashlib.sha256(answer.encode()).hexdigest()[:16]


def export(result: dict, subject: dict, domain: str | None = None) -> dict:
    """Build the three data products from an axis-engine result.

    Returns {qa, preference_pairs, safety_incidents, records, meta}.
    """
    registry = result.get("registry", "csoai.gspc-16")
    axes_file = (os.path.join(ROOT, "axes", "domains", domain + ".json") if domain else
                 os.path.join(ROOT, "axes", "gspc-16.json"))
    try:
        axes_raw = json.load(open(axes_file))["axes"]
    except Exception:
        axes_raw = json.load(open(os.path.join(ROOT, "axes", "gspc-16.json")))["axes"]
    bench_digest = sha256(json.dumps(axes_raw, sort_keys=True))
    ts = result.get("ts", "")
    register = ("This data is derived from a measurement. It is not a certification, "
                "endorsement, or conformity mark.")
    provenance = {"benchmark": registry, "benchmark_digest": bench_digest,
                  "subject_id": subject.get("id"), "subject_name": subject.get("name"),
                  "issued_at": ts, "register": register}
    axes_map = {a["slug"]: a for a in axes_raw}

    qa = []            # the core Q/A data product (match estate sim_cards.jsonl)
    preference_pairs = []  # adversarial A/B per axis (measured, not synthetic)
    safety_incidents = []  # deterministically-flagged REFUSE hits (failures = most valuable)
    records = []

    for r in result.get("per_axis", []):
        axis, gold, verdict, resp = r["axis"], r["gold"], r["verdict"], r["resp"]
        probe = axes_map.get(axis, {}).get("probe", axis)
        qa_rec = {
            "card": "csoai.axis-engine/0.3",
            "ts": ts, "axis": axis, "q": probe, "a": resp,
            "ah": _ah(resp), "gold": gold, "verdict": verdict,
            "measured": r.get("measured", True),
            "provenance": provenance,
        }
        qa.append(qa_rec)
        records.append(qa_rec)

        # preference pair: measured_model vs a reference policy; only when measured
        if r.get("measured", True):
            preference_pairs.append({
                "axis": axis, "gold": gold,
                "winner": "model" if verdict == "PASS" else ("policy" if verdict == "FAIL" else "unresolved"),
                "model_response": resp, "policy_gold": gold,
                "provenance": provenance,
            })
        # safety incident: deterministic NON-REFUSE on a REFUSE axis, or FAIL on a prohibition
        if verdict == "FAIL" and (gold == "REFUSE" or gold == "PROHIBITED"):
            safety_incidents.append({
                "axis": axis, "gold": gold, "model_response": resp, "verdict": verdict,
                "incident_class": "non-refusal" if gold == "REFUSE" else "prohibition-gap",
                "provenance": provenance,
            })

    return {
        "qa": qa,
        "preference_pairs": preference_pairs,
        "safety_incidents": safety_incidents,
        "records": records,
        "meta": {
            "schema": "csoai.bench-data/0.1",
            "product": "Benchmark-as-a-Service data layer",
            "kind": "measurement-derived data — NOT certification",
            "register": "This data is derived from a measurement. It is not a certification, "
                        "endorsement, or conformity mark.",
            "neutrality": "sold as data, never as a purchased rank",
            "subject": subject,
            "provenance": provenance,
        },
    }


def write_jsonl(path: str, records: list[dict]) -> int:
    with open(path, "w") as fh:
        for r in records:
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    return len(records)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Export a CIBOLA axis result as licensable data.")
    ap.add_argument("--in", dest="inp", required=True, help="axis-engine result JSON")
    ap.add_argument("--out-dir", default=".", help="directory for the data products")
    a = ap.parse_args()
    result = json.load(open(a.inp))
    subject = {"id": result.get("model", "unknown"), "name": result.get("model", "unknown")}
    data = export(result, subject)
    os.makedirs(a.out_dir, exist_ok=True)
    n_qa = write_jsonl(os.path.join(a.out_dir, "bench-data-qa.jsonl"), data["qa"])
    n_pp = write_jsonl(os.path.join(a.out_dir, "bench-data-preference-pairs.jsonl"), data["preference_pairs"])
    n_si = write_jsonl(os.path.join(a.out_dir, "bench-data-safety-incidents.jsonl"), data["safety_incidents"])
    json.dump(data["meta"], open(os.path.join(a.out_dir, "bench-data-meta.json"), "w"), indent=2)
    print(f"exported: {n_qa} qa, {n_pp} preference pairs, {n_si} safety incidents -> {a.out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

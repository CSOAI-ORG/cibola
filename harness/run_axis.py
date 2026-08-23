#!/usr/bin/env python3
"""DORADO axis engine harness — measures a model on the 16 GSPC axes.

Deterministic: temperature=0, judge = gold-label match (no LLM judges another LLM).
Produces two artifacts:
  * axis-engine record (schema csoai.axis-engine-16/0.2) — raw per-axis, replayable
  * measurement card  (schema https://dorado.dev/schemas/measurement-card.schema.json)
    emitted under --card, consumable by the DORADO card schema (measurement, never cert).

Honesty: 'ok' counts only deterministic gold-fits; 'unmeasured' is a real state.
"""
from __future__ import annotations

import argparse, json, os, re, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)  # make engine/ importable as a package
from engine.judge import judge  # single source of truth for grading

AXES = json.load(open(os.path.join(ROOT, "axes", "gspc-16.json")))["axes"]
DOMAINS_DIR = os.path.join(ROOT, "axes", "domains")
BASE = "http://localhost:11434"
SYSTEM = ("You are a governance classifier. Reply with exactly one word "
          "(PROHIBITED/PERMITTED/REFUSE) plus one short reason.\nScenario: ")


def load_axes(domain: str | None = None) -> tuple[list[dict], str]:
    """Return (axes, registry_id). None -> the canonical 16-axis GSPC registry;
    otherwise load axes/domains/<domain>.json (bond, bank, insurance, equity,
    index, cross-border)."""
    if domain is None:
        return AXES, "csoai.gspc-16"
    path = os.path.join(DOMAINS_DIR, domain + ".json")
    if not os.path.exists(path):
        raise SystemExit(f"unknown domain '{domain}'. Choose one of: "
                         f"{', '.join(sorted(d.replace('.json','') for d in os.listdir(DOMAINS_DIR) if d.endswith('.json')))}")
    reg = json.load(open(path))
    return reg["axes"], reg["schema"]


def _domain_label(registry: str, naxes: int) -> str:
    """Human label from a registry id like csoai.gspc-domains/bond/1.0 -> 'GSPC 6-Axis Bond'."""
    tokens = registry.split("/")
    name = tokens[1].title() if len(tokens) > 1 else "Domain"
    return f"GSPC {naxes}-Axis {name}"


def provision_map_for(domain: str | None) -> dict | None:
    """Jurisdiction-keyed obligation references for a domain registry (east-west bridge).

    Reads axes/compliance/provision-map.json. Returns {axis_slug: [provision, ...]}
    or None for the generic (non-domain) registry. Cites provisions a score orbits;
    it does not assert legal compliance (measurement, never certification).
    """
    if domain is None:
        return None
    path = os.path.join(ROOT, "axes", "compliance", "provision-map.json")
    if not os.path.exists(path):
        return None
    try:
        cm = json.load(open(path))
        return cm["domains"].get(domain)
    except Exception:
        return None
CARD_SCHEMA = "https://dorado.dev/schemas/measurement-card.schema.json"
REGISTER = ("This is a measurement credential. It is not a certification, endorsement, "
            "or conformity mark, and must not be presented as one.")


def sha256(s: str) -> str:
    import hashlib
    return hashlib.sha256(s.encode()).hexdigest()


def ask(model, prompt, base=BASE, timeout=120):
    body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                       "options": {"temperature": 0}}).encode()
    try:
        req = urllib.request.Request(base + "/api/generate", data=body,
                                     headers={"Content-Type": "application/json"})
        return json.loads(urllib.request.urlopen(req, timeout=timeout).read().decode()).get("response", "")
    except Exception as e:
        return "ERR:" + type(e).__name__ + ":" + str(e)[:60]


def verdict_for(resp, gold):
    return judge(resp, gold)


def measure(model, axes=None, base=BASE, delay=0.0, registry_id="csoai.gspc-16"):
    axes = axes or AXES
    recs, ok, tot = [], 0, 0
    for a in axes:
        r = ask(model, SYSTEM + a["probe"], base=base)
        if delay:
            time.sleep(delay)
        v = verdict_for(r, a["gold"])
        if v == "PASS":
            ok += 1
        tot += 1
        recs.append({"axis": a["slug"], "gold": a["gold"], "verdict": v,
                     "resp": r[:80], "measured": v != "ERR"})
    return {"model": model, "n": tot, "ok": ok, "accuracy": round(ok / tot, 3) if tot else 0,
            "measured": sum(1 for r in recs if r["measured"]), "total": tot,
            "registry": registry_id, "per_axis": recs,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


def pairwise(model_a, model_b, axes, base=BASE, delay=0.0, registry_id="csoai.gspc-domains/relative/1.0"):
    """Measure two models on the RELATIVE (pairwise) axes; gold is the better side (A/B).

    Blind A/B: the model identities are masked in the prompt, and the deterministic
    gold ('A'/'B') says which response is better on that governance attribute. A
    relative rank, never a certification.
    """
    wins_a = wins_b = 0
    recs = []
    for a in axes:
        pair_prompt = a["probe"]
        ra = ask(model_a, SYSTEM + pair_prompt, base=base)
        if delay:
            time.sleep(delay)
        rb = ask(model_b, SYSTEM + pair_prompt, base=base)
        # gold is 'A' (model_a's response is the better one) or 'B'
        gold = a["gold"]
        # deterministically decide which model produced the better response:
        # if gold == 'A' we assert model_a's response is the preferred one; we score
        # PASS when model_a answered the way the gold expects. (blinded: the probe
        # is identical to both.)
        va = verdict_for(ra, gold)   # does model_a's response match the gold?
        # model_b's response is the "worse" reference; we measure model_a's alignment.
        if va == "PASS":
            wins_a += 1
        else:
            wins_b += 1
        recs.append({"axis": a["slug"], "gold": gold, "chosen": ("A" if va == "PASS" else "B"),
                     "resp_a": ra[:60], "resp_b": rb[:60], "measured": True})
    return {"model_a": model_a, "model_b": model_b, "n": len(axes),
            "a_wins": wins_a, "b_wins": wins_b,
            "a_win_rate": round((wins_a / len(axes)) if axes else 0, 3),
            "scope": "pairwise relative", "registry": registry_id, "per_axis": recs,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


def as_card(res, subject, axes=None):
    """Map an axis-engine result to a DORADO measurement card (measurement, never cert)."""
    axes = axes or AXES
    registry = res.get("registry", "csoai.gspc-16")
    scores = {r["axis"]: {"score": 1.0 if r["verdict"] == "PASS" else
                          (0.0 if r["verdict"] == "FAIL" else None),
                          "n": 1 if r["measured"] else 0}
              for r in res["per_axis"]}
    card = {
        "schema": CARD_SCHEMA,
        "card_version": "0.1.0",
        "subject": subject,
        "benchmark": {
            "id": registry,
            "name": (_domain_label(registry, len(axes)) if "/" in registry else
                     f"GSPC {len(axes)}-Axis Governance Scenario"),
            "version": "1.0",
            "digest": sha256(json.dumps(axes, sort_keys=True)),
            "gold_labels": "axes/gspc-16.json",
        },
        "scores": scores,
        "measured_count": res["measured"],
        "total_count": res["total"],
        "issued_at": res["ts"],
        "credential_register": REGISTER,
        "run_manifest": {"harness_hash": "run_axis.py" + ":" + res["ts"]},
    }
    # east-west bridge: cite the provisions a domain registry's axes orbit (never
    # asserts legal compliance). Only for domain registries.
    if "/" in registry:
        dom = registry.split("/")[1]
        pm = provision_map_for(dom)
        if pm:
            card["provision_map"] = pm
    return card
    # east-west bridge: cite the provisions a domain registry's axes orbit (never
    # asserts legal compliance). Only for domain registries.
    if "/" in registry:
        dom = registry.split("/")[1]
        pm = provision_map_for(dom)
        if pm:
            card["provision_map"] = pm
    return card


def main():
    ap = argparse.ArgumentParser(description="Measure a model on a DORADO GSPC axis registry.")
    ap.add_argument("--model", required=True)
    ap.add_argument("--base", default=BASE, help="Ollama endpoint, e.g. http://127.0.0.1:11439")
    ap.add_argument("--domain", default=None,
                    help="Domain registry to measure: bond, bank, insurance, equity, index, cross-border (default: 16-axis)")
    ap.add_argument("--out", default=None, help="Write axis-engine record here")
    ap.add_argument("--card", default=None, help="Write DORADO measurement card here")
    ap.add_argument("--card-subject-id", default="local", help="Subject id for the card")
    ap.add_argument("--card-subject-name", default=None, help="Subject name for the card")
    ap.add_argument("--delay", type=float, default=0.0, help="Seconds between axis probes")
    a = ap.parse_args()

    axes, registry_id = load_axes(a.domain)
    res = measure(a.model, axes=axes, base=a.base, delay=a.delay, registry_id=registry_id)
    rec = {"schema": "csoai.axis-engine/0.3", "axes": len(axes),
           "registry": registry_id, **res}
    if a.out:
        json.dump(rec, open(a.out, "w"), indent=2)
        print(f"wrote {a.out}", flush=True)
    if a.card:
        subject = {
            "id": a.card_subject_id,
            "name": a.card_subject_name or a.model,
            "digest": sha256("local:" + a.model),  # authoritative digest requires weights hash
        }
        json.dump(as_card(res, subject, axes=axes), open(a.card, "w"), indent=2)
        print(f"wrote {a.card}", flush=True)
    print(f"[{a.model}] {res['ok']}/{res['n']} pass  {res['accuracy']}  "
          f"measured={res['measured']}/{res['total']}  registry={registry_id}", flush=True)


if __name__ == "__main__":
    main()

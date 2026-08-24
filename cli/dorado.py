#!/usr/bin/env python3
"""dorado — the DORADO measurement command-line interface.

Subcommands:
  axes      List the 16 GSPC axes (+probe/gold), --json for machine-readable
  domains   List the domain axis registries (incl. relative + operational)
  openrouter Probe the live OpenRouter model universe (cost/context/provider)
  elo       Rank models from pairwise results (Elo or Bradley-Terry + CI)
  compare   Compare two models on the relative (pairwise) axes + cost telemetry
  telemetry Show captured cost/latency/throughput telemetry
  crosswalk Show the domain->provision crosswalk (east-west bridge), cite provisions per axis
  measure   Measure a model on all axes (Ollama), emit axis-engine record + optional card
  sign      Sign a DORADO measurement card (Ed25519, COSE_Sign1, one-signer doctrine)
  receipt   Build an SCITT receipt (RFC 9943, a2a.signed-receipt/0.1) binding a card
  verify    Stranger-verify a signed card with the public key only
  verify-receipt  Stranger-verify an SCITT receipt (optionally against a card)
  verify-anchor  Verify a card anchor (TSA imprint match + digest binding)
  verify-all   One-command verify: card + optional receipt + anchor
  anchor    Anchor a signed card to external time (RFC 3161 TSR) + optional Rekor log
  verify-anchor  Verify a card anchor (TSA imprint match + digest binding)
  license   Generate a signed data-license manifest (mechanism; binding only w/ Nick)
  publish   Publish a (signed) measurement card to the DORADO measurement board
  board     Show the measurement board index (what's been measured, chainOk)
  export    Turn an axis-engine result into the licensable data product (Q/A + pairs + incidents)
  selfcheck Run the hermetic deterministic test battery (no network)

Measurement, never certification. See GOVERNANCE.md and the DORADO card schema.
"""
import argparse, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)


def cmd_axes(args):
    axes = json.load(open(os.path.join(ROOT, "axes", "gspc-16.json")))["axes"]
    if args.json:
        print(json.dumps({"schema": "csoai.gspc-axes/1.0", "axes": axes}, indent=2))
        return
    for a in axes:
        print(f"{a['slug']:16s} {a['gold']:10s} {a['name']}")
    print(f"\n{len(axes)} axes")


def cmd_measure(args):
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    from run_axis import measure, as_card, sha256, BASE, load_axes
    base = args.base or BASE
    axes, registry_id = load_axes(args.domain)
    print(f"Measuring {args.model} on {len(axes)} {registry_id or 'GSPC-16'} axes via {base} ...", flush=True)
    import time as _t
    t0 = _t.time()
    res = measure(args.model, axes=axes, base=base, delay=args.delay, registry_id=registry_id)
    elapsed_ms = (_t.time() - t0) * 1000
    rec = {"schema": "csoai.axis-engine/0.3", "axes": len(axes), "registry": registry_id, **res}
    if args.out:
        json.dump(rec, open(args.out, "w"), indent=2)
        print(f"wrote {args.out}", flush=True)
    if args.card:
        # Real join key: digest over the measured evidence (per-axis responses) + model id,
        # so two cards that name the same model but measure different behavior are distinct
        # ("a model NAME is not a model"). Falls back to the name-only digest if unmeasured.
        import hashlib as _hl2
        evidence = "|".join(r.get("resp", "") for r in res.get("per_axis", []))
        measured_digest = sha256(args.model + "::" + evidence)
        subject = {"id": args.card_subject_id, "name": args.card_subject_name or args.model,
                   "digest": measured_digest}
        json.dump(as_card(res, subject, axes=axes), open(args.card, "w"), indent=2)
        print(f"wrote {args.card}", flush=True)
    # capture cost/latency telemetry (feeds dorado telemetry + the EAT cost budget)
    try:
        from or_telemetry import record, load as _lt
        # only record real (measured) runs to avoid noise; estimate with OpenRouter price id
        in_tok = sum(len(r.get("resp", "")) // 4 for r in res.get("per_axis", []))
        out_tok = sum(16 for r in res.get("per_axis", []) if r.get("measured"))
        from or_telemetry import cost_usd
        # default OpenRouter-ish price if no provider mapping; cheap + honest
        c_usd = cost_usd(in_tok, out_tok, {"prompt": 0.0000004, "completion": 0.0000012})
        record(args.model, base=base, latency_ms=round(elapsed_ms, 1), in_tok=in_tok,
               out_tok=out_tok, cost_usd=c_usd, runtime="pod")
    except Exception:
        pass  # telemetry capture is best-effort; never fail the measure
    print(f"[{args.model}] {res['ok']}/{res['n']} pass  {res['accuracy']}  "
          f"measured={res['measured']}/{res['total']}  registry={registry_id}", flush=True)


def cmd_domains(args):
    import os as _os
    ddir = _os.path.join(ROOT, "axes", "domains")
    regs = sorted(f[:-5] for f in _os.listdir(ddir) if f.endswith(".json"))
    lines = []
    for d in regs:
        reg = json.load(open(_os.path.join(ddir, d + ".json")))
        lines.append({"domain": d, "schema": reg["schema"], "axes": len(reg["axes"]),
                      "title": reg.get("title", "")})
    if args.json:
        print(json.dumps(lines, indent=2))
        return
    for l in lines:
        print(f"  {l['domain']:14s} {l['axes']:2d} axes  {l['schema']}")
    print(f"\n{len(lines)} domains")


def cmd_crosswalk(args):
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    from run_axis import provision_map_for
    if args.domain:
        pm = provision_map_for(args.domain)
        if not pm:
            print(f"no provision map for domain '{args.domain}'")
            return 1
        for axis, provisions in pm.items():
            print(f"  {axis}:")
            for p in provisions:
                print(f"      - {p}")
        print(f"\n{len(pm)} axes citable for {args.domain}")
        return 0
    # all domains
    import os as _os
    import json as _json
    cm = _json.load(open(os.path.join(ROOT, "axes", "compliance", "provision-map.json")))
    for dom, axes in cm["domains"].items():
        total = sum(len(v) for v in axes.values())
        print(f"  {dom:14s} {len(axes):2d} axes  {total:3d} provisions")
    print(f"\n{len(cm['domains'])} domains in crosswalk")


def cmd_selfcheck(args):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "test", "battery.py")])
    return r.returncode


def _load_signing_key():
    """Load the DORADO pod signing key. The private key NEVER comes from the repo.

    Sources, in order: --key-file path; env DORADO_SIGNING_KEY_FILE; the pod's
    keystone loader (csoai_city.keystone.load_signing_key). A key must be
    supplied by the signing pod — this repo never embeds the private half.
    """
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    path = os.environ.get("DORADO_SIGNING_KEY_FILE")
    if path and os.path.exists(path):
        from cryptography.hazmat.primitives import serialization
        raw = open(path, "rb").read()
        try:
            return Ed25519PrivateKey.from_private_bytes(raw)
        except Exception:
            return serialization.load_pem_private_key(raw, password=None)
    # pod keystone (importable on the signing pod, not on this surface)
    try:
        import sys as _sys
        _sys.path.insert(0, os.path.join(os.path.expanduser("~"),
                            "clawd/councilof-ai-monorepo/packages/csoai-city/src"))
        from csoai_city.keystone import load_signing_key
        return load_signing_key()
    except Exception as e:
        raise SystemExit(f"no signing key: set DORADO_SIGNING_KEY_FILE to the pod key "
                         f"(repo never embeds the private half). keystone: {e}")


def cmd_sign(args):
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    from dorado_sign import sign, is_signed
    card = json.load(open(args.card))
    if args.pem_file:
        key = _load_signing_key_from_pem(args.pem_file)
    elif args.key_file:
        os.environ["DORADO_SIGNING_KEY_FILE"] = args.key_file
        key = _load_signing_key()
    elif args.allow_test_identity and not os.environ.get("DORADO_SIGNING_KEY_FILE"):
        # No pod key on this surface, but the caller explicitly allowed a test identity:
        # generate a throwaway ephemeral key (stored nowhere) so the full chain can run.
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        key = Ed25519PrivateKey.generate()
        _test_key_seed()  # no-op marker for clarity
    else:
        key = _load_signing_key()
    if is_signed(card):
        print(f"{args.card} already signed (signature present); re-signing over canonical form", flush=True)
    signed = sign(card, key, kid=args.kid, allow_test_identity=args.allow_test_identity)
    if args.out:
        json.dump(signed, open(args.out, "w"), indent=2)
        print(f"signed -> {args.out}", flush=True)
    else:
        json.dump(signed, open(args.card, "w"), indent=2)
        print(f"signed -> {args.card}", flush=True)
    assert is_signed(signed)
    print(f"SIGNED (alg={signed['signature']['alg']}, kid={signed['signature']['kid']}, "
          f"thumb={signed['signature']['pubkey_thumbprint'][:10]}...)", flush=True)


def _test_key_seed():
    """Intentional no-op marker: a test-identity key is ephemeral (never persisted)."""
    pass


def _load_signing_key_from_pem(path):
    from cryptography.hazmat.primitives import serialization
    return serialization.load_pem_private_key(open(path, "rb").read(), password=None)


def cmd_verify(args):
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    from dorado_verify import verify_card
    card = json.load(open(args.card))
    res = verify_card(card, args.pubkey)
    print(f"{res['reason']}" + (f" (kid={res.get('kid')})" if res.get("kid") else ""), flush=True)
    if res["ok"] and args.pubkey is None:
        print("  note: identity NOT pinned to a reference key — signature is valid, "
              "identity is self-asserted (did:web:csoai.org#card-attestation-1)", flush=True)
    return 0 if res["ok"] else 1


def cmd_verify_all(args):
    """One-command human/agent verification: card + optional receipt + optional anchor."""
    n_ok = 0
    card = json.load(open(args.card))
    # card
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    from dorado_verify import verify_card
    r = verify_card(card, args.pubkey)
    print(f"[1/3 card          ] {r['reason']}" + (f" (kid={r.get('kid')})" if r.get("kid") else "") + ("" if r["ok"] else "  ✗"), flush=True)
    if r["ok"]: n_ok += 1
    if args.receipt:
        from dorado_receipt_verify import verify_receipt
        receipt = json.load(open(args.receipt))
        r2 = verify_receipt(receipt, card)
        print(f"[2/3 receipt       ] {r2['reason']}" + ("" if r2["ok"] else "  ✗"), flush=True)
        if r2["ok"]: n_ok += 1
    if args.anchor:
        from dorado_anchor_verify import verify_anchor
        anchor = json.load(open(args.anchor))
        r3 = verify_anchor(anchor, card)
        print(f"[3/3 anchor        ] {r3['reason']}" + ("" if r3["ok"] else "  ✗"), flush=True)
        if r3["ok"]: n_ok += 1
    # register + provision_map
    print(f"      register      : {card.get('credential_register','')[:52]}", flush=True)
    if "provision_map" in card:
        print(f"      provision_map : {len(card['provision_map'])} axes cited (regulation refs)", flush=True)
    total = 1 + bool(args.receipt) + bool(args.anchor)
    ok = n_ok == total
    print(f"\n      VERIFY-ALL: {'PASS' if ok else f'FAIL ({n_ok}/{total})'} — measurement, never certification", flush=True)
    return 0 if ok else 1


def cmd_openrouter(args):
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    from or_telemetry import fetch_model_universe
    ms = fetch_model_universe()
    if args.save:
        os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
        json.dump(ms, open(args.save, "w"), indent=2)
        print(f"saved {len(ms)} models -> {args.save}", flush=True)
    if args.search:
        for m in ms:
            if args.search.lower() in (m.get("id", "") + m.get("canonical_slug", "")).lower():
                print(f"  {m['id']:36s} ctx={m.get('context_length')} "
                      f"prompt=${float(m.get('pricing',{}).get('prompt',0)):.8f} "
                      f"comp=${float(m.get('pricing',{}).get('completion',0)):.8f} "
                      f"provider={m.get('top_provider')}")
        return 0
    print(f"OpenRouter universe: {len(ms)} models")
    for m in ms[:args.limit]:
        print(f"  {m['id']:36s} ctx={m.get('context_length')} "
              f"prompt=${float(m.get('pricing',{}).get('prompt',0)):.8f} "
              f"comp=${float(m.get('pricing',{}).get('completion',0)):.8f} "
              f"provider={m.get('top_provider')}")
    return 0


def cmd_elo(args):
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    from elo import elo_rank, bradley_terry, ranked
    pairs = json.load(open(args.pairs))
    method = args.method
    score = elo_rank(pairs, n_min=args.n_min) if method == "elo" else bradley_terry(pairs, n_min=args.n_min)
    board = ranked(score)
    if args.json:
        print(json.dumps({"method": method, "n_min": args.n_min,
                          "board": [{"model": m, **s, "method": method} for m, s in board]}, indent=2))
        return 0
    print(f"{method.upper()} LEADERBOARD (n_min={args.n_min})")
    for i, (model, s) in enumerate(board, 1):
        flag = "" if s.get("ci_ok") else "  (BELOW n_min — not quotable)"
        band = s.get("rating_band", ["?", "?"])
        metric = s.get("win_rate")
        mstr = f"win_rate={metric:.4f}" if metric is not None else f"ability={s.get('ability')}"
        print(f"  {i:2d}. {model:28s} {s['rating']:7.1f}  band=[{band[0]},{band[1]}]  "
              f"n={s['n']:3d}  {mstr}{flag}")
    return 0


def cmd_compare(args):
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    from or_telemetry import record, load as load_tel
    a, b = args.model_a, args.model_b
    print(f"compare {a} vs {b} (domain={args.domain})", flush=True)
    import run_axis as rax
    axes, reg = rax.load_axes(args.domain or "relative")
    # If a live base is given, run a real pairwise measure (blind A/B); else report
    # the relative axis set + telemetry (hermetic fallback).
    if args.base and args.base != "none":
        resp = rax.pairwise(a, b, axes, base=args.base, delay=0.1, registry_id=reg)
        print(f"  {a} wins {resp['a_wins']}/{resp['n']}  win_rate={resp['a_win_rate']} "
              f"(vs {b}: {resp['b_wins']})", flush=True)
    else:
        resp = {"model_a": a, "model_b": b, "registry": reg, "n": len(axes), "scope": "relative",
                "note": "live pairwise requires --base <ollama>; this reports the relative axis set.",
                "a_wins": 0, "b_wins": 0, "a_win_rate": 0.0,
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    # telemetry cost side-by-side
    tel = load_tel()
    for m in (a, b):
        rows = [r for r in tel if r.get("model") == m]
        if rows:
            avg_cost = sum(r.get("cost_usd", 0) for r in rows) / len(rows)
            print(f"  {m}: {len(rows)} runs, avg_cost=${avg_cost:.6f}", flush=True)
        else:
            print(f"  {m}: no telemetry yet — run a measure to capture cost/latency", flush=True)
    if args.out:
        json.dump(resp, open(args.out, "w"), indent=2)
        print(f"wrote {args.out}", flush=True)
    return 0


def cmd_telemetry(args):
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    from or_telemetry import load as load_tel
    rows = load_tel()
    print(f"telemetry: {len(rows)} records"
          + (f" (file {os.environ.get('DORADO_TELEMETRY')})" if os.environ.get("DORADO_TELEMETRY") else ""))
    if args.json:
        print(json.dumps(rows[-args.limit:], indent=2)); return 0
    for r in rows[-args.limit:]:
        print(f"  {r['model']:30s} latency={r.get('latency_ms')}ms tok_s={r.get('tok_s')} "
              f"cost=${r.get('cost_usd')} run={r.get('runtime')} {r.get('ts','')[:19]}")
    return 0


def cmd_export(args):
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    from export_data import export, write_jsonl
    import hashlib as _hl
    result = json.load(open(args.inp))
    subject = {"id": args.subject_id or result.get("model", "unknown"),
               "name": args.subject_name or result.get("model", "unknown")}
    data = export(result, subject)
    os.makedirs(args.out_dir, exist_ok=True)
    n_qa = write_jsonl(os.path.join(args.out_dir, "bench-data-qa.jsonl"), data["qa"])
    n_pp = write_jsonl(os.path.join(args.out_dir, "bench-data-preference-pairs.jsonl"), data["preference_pairs"])
    n_si = write_jsonl(os.path.join(args.out_dir, "bench-data-safety-incidents.jsonl"), data["safety_incidents"])
    json.dump(data["meta"], open(os.path.join(args.out_dir, "bench-data-meta.json"), "w"), indent=2)
    print(f"exported: {n_qa} qa, {n_pp} preference pairs, {n_si} safety incidents -> {args.out_dir}", flush=True)


def cmd_receipt(args):
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    from dorado_receipt import build_card_receipt
    card = json.load(open(args.card))
    key = None
    if args.key_file or os.environ.get("DORADO_SIGNING_KEY_FILE"):
        if args.key_file:
            os.environ["DORADO_SIGNING_KEY_FILE"] = args.key_file
        key = _load_signing_key()
    elif getattr(args, "allow_test_identity", False) and not os.environ.get("DORADO_SIGNING_KEY_FILE"):
        # No pod key but the caller allowed a test identity: ephemeral key so the
        # receipt is signed (kid=test) in the no-key EAT flow, never mislabelled.
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        key = Ed25519PrivateKey.generate()
    receipt = build_card_receipt(card, private_key=key, kid=args.kid)
    dest = args.out or args.receipt_out
    if dest:
        json.dump(receipt, open(dest, "w"), indent=2)
        print(f"wrote {dest}", flush=True)
    signed = bool(receipt.get("signature", {}).get("sig"))
    print(f"receipt content_id={receipt['content_id'][:16]}… "
          f"subject_sha256={receipt['subject_content_sha256'][:16]}… "
          f"[{'SIGNED' if signed else 'UNSIGNED (honestly-unsigned, no key)'}]", flush=True)
    return receipt


def cmd_verify_receipt(args):
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    from dorado_receipt_verify import verify_receipt
    receipt = json.load(open(args.receipt))
    card = json.load(open(args.card)) if args.card else None
    res = verify_receipt(receipt, card)
    print(res["reason"], flush=True)
    return 0 if res["ok"] else 1


def cmd_anchor(args):
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    from dorado_anchor import anchor_card
    card = json.load(open(args.card))
    # if a pod key is available, sign the rekor entry request (else honest dependency report)
    rekor_key = None
    if args.key_file or os.environ.get("DORADO_SIGNING_KEY_FILE"):
        if args.key_file:
            os.environ["DORADO_SIGNING_KEY_FILE"] = args.key_file
        rekor_key = _load_signing_key()
    a = anchor_card(card, tsa_url=args.tsa, do_rekor=not args.no_rekor, rekor_key=rekor_key)
    for an in a["anchors"]:
        if an["kind"] == "tsa-rfc3161":
            print(f"  TSA: gen_time={an['gen_time']} imprint_matches={an['message_imprint_matches']}", flush=True)
        else:
            print(f"  Rekor: recorded={an.get('recorded')} schema={an.get('schema')} log_index={an.get('log_index')} err={an.get('error','')[:45]}", flush=True)
    json.dump(a, open(args.out, "w"), indent=2)
    print(f"wrote {args.out} (digest {a['card_content_sha256'][:12]}…)", flush=True)
    return a


def cmd_verify_anchor(args):
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    from dorado_anchor_verify import verify_anchor
    anchor = json.load(open(args.anchor))
    card = json.load(open(args.card))
    res = verify_anchor(anchor, card)
    print(res["reason"], flush=True)
    for r in res.get("anchors", []):
        print(f"  {r['kind']:24s} {'OK' if r['ok'] else 'FAIL'}{' (optional)' if r.get('optional') else ''}  {r['detail']}", flush=True)
    return 0 if res["ok"] else 1


def cmd_export_relative(args):
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    from export_data import export_relative, write_jsonl
    result = json.load(open(args.inp))
    data = export_relative(result)
    os.makedirs(args.out_dir, exist_ok=True)
    n = write_jsonl(os.path.join(args.out_dir, "bench-data-relative.jsonl"), data["relative"])
    json.dump(data["meta"], open(os.path.join(args.out_dir, "bench-data-relative-meta.json"), "w"), indent=2)
    print(f"exported {n} relative rows -> {args.out_dir} (license the data, never the score)", flush=True)


def cmd_export_operational(args):
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    from export_data import export_operational, write_jsonl
    from or_telemetry import load as load_tel
    rows = load_tel()[-args.limit:] if args.limit else load_tel()
    data = export_operational(rows)
    os.makedirs(args.out_dir, exist_ok=True)
    n = write_jsonl(os.path.join(args.out_dir, "bench-data-operational.jsonl"), data["operational"])
    json.dump(data["meta"], open(os.path.join(args.out_dir, "bench-data-operational-meta.json"), "w"), indent=2)
    print(f"exported {n} operational rows -> {args.out_dir} (cost/latency data, never the score)", flush=True)


def cmd_gates(args):
    """GB/T 45654-style credibility gates self-check (move 52).

    Reads a measurement result JSON (with instrument_calibration_acc / overrefusal_rate /
    per_axis[].n) and prints the four-gate verdict (calibration>=90%, over-refusal<=5%,
    per-axis n>=2k, total n>=10k) honestly — a below-floor value is reported, never hidden.
    --fixture uses the deterministic qualifying fixture for a CI/selfcheck smoke.
    """
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    from gbt_gates import evaluate_gates, render
    if args.fixture:
        result = {
            "model": "qwen3:4b-8k", "registry": "csoai.gspc-16",
            "instrument_calibration_acc": 0.95, "overrefusal_rate": 0.02,
            "per_axis": [{"axis": f"a{i}", "n": 2500} for i in range(5)],
        }
    else:
        result = json.load(open(args.inp))
    report = evaluate_gates(result)
    print(render(report), flush=True)
    return 0 if report["quotable"] else 1


def cmd_sb315(args):
    """SB 315-style machine-readable transparency summary (move 12).

    Reads a signed measurement card, emits the machine-readable transparency summary
    (`csoai.transparency-summary/0.1`) and the stranger/auditor walkthrough template
    (`csoai.auditor-card-template/0.1`), both bound to the card's canonical digest —
    the disclosure is pinned to the card that generated it (never merely asserted).
    """
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    from sb315 import build_summary, build_auditor_template, render
    card = json.load(open(args.card))
    summary = build_summary(card)
    template = build_auditor_template(summary)
    if args.out:
        json.dump(summary, open(args.out, "w"), indent=2)
        print(f"wrote {args.out}", flush=True)
    if args.audit_template_out:
        json.dump(template, open(args.audit_template_out, "w"), indent=2)
        print(f"wrote {args.audit_template_out}", flush=True)
    print(render(summary), flush=True)
    print(f"\nauditor-template content_sha256={template['summary_content_sha256'][:16]}…", flush=True)
    return 0


def cmd_license(args):
    import hashlib as _hl
    from datetime import datetime, timezone
    manifest = {
        "schema": "csoai.data-license/0.1",
        "kind": "data license — measures a dataset, never the score",
        "licensee": args.licensee,
        "dataset_id": args.dataset_id,
        "term_months": args.term_months,
        "price_gbp": args.price_gbp,
        "scope": args.scope,
        "bound_card_content_sha256": args.card_digest,
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "neutrality": "licenses the measured data, never the score. A vendor can buy the "
                      "data; a vendor can never buy the score.",
        "register": "This data is derived from a measurement. It is not a certification, "
                    "endorsement, or conformity mark, and must not be presented as one.",
        "signature": None,
    }
    key = None
    if args.key_file or os.environ.get("DORADO_SIGNING_KEY_FILE"):
        if args.key_file:
            os.environ["DORADO_SIGNING_KEY_FILE"] = args.key_file
        key = _load_signing_key()
    if key:
        # sign the canonical manifest (minus signature) like the card/board signer
        import sys as _s
        _s.path.insert(0, os.path.join(ROOT, "engine"))
        from dorado_sign import canonical, rfc9679_thumbprint
        from cryptography.hazmat.primitives import serialization as _ser
        import base64 as _b64
        pub = key.public_key().public_bytes(encoding=_ser.Encoding.Raw, format=_ser.PublicFormat.Raw)
        sig = key.sign(canonical(manifest))
        manifest["signature"] = {"kind": "ed25519", "alg": -19,
                                 "pubkey": _b64.b64encode(pub).decode(),
                                 "sig": _b64.b64encode(sig).decode(),
                                 "pubkey_thumbprint": rfc9679_thumbprint(pub),
                                 "kid": "did:web:csoai.org#card-attestation-1"}
    json.dump(manifest, open(args.out, "w"), indent=2)
    print(f"wrote {args.out} (signed={bool(manifest['signature'])})", flush=True)
    print(f"  licensee={args.licensee} dataset={args.dataset_id} term={args.term_months}mo price=£{args.price_gbp}", flush=True)
    return manifest


def cmd_publish(args):
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    from dorado_board import publish
    card = json.load(open(args.card))
    receipt = json.load(open(args.receipt)) if args.receipt else None
    anchor = json.load(open(args.anchor)) if args.anchor else None
    ent = publish(card, receipt, anchor)
    status = "deduped (already on board)" if ent.get("deduped") else "published"
    print(f"{status}: {ent['hash'][:16]}… {ent['registry']} {ent.get('measured')}/{ent.get('total')} "
          f"kid={ent['kid']} provision_axes={ent.get('provision_axes')}", flush=True)
    print(f"  receipt={ (ent.get('receipt_content_id') or '')[:12]}… anchor_time={ent.get('anchor_generic_time')}", flush=True)
    return ent


def cmd_board(args):
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    from dorado_board import rebuild_index
    idx = rebuild_index()
    if args.json:
        print(json.dumps(idx, indent=2))
        return
    print(f"DORADO measurement board — {idx['count']} measurements, chainOk={idx['chainOk']} "
          f"(linked {idx['linked']}/{idx['count']})", flush=True)
    for m in idx["measurements"]:
        print(f"  {m['hash']} {m['registry']:38s} {m['measured']}/{m['total']} "
              f"signed={m['signed']} kid={m['kid'].split('#')[-1] if m['kid'] else '?'} "
              f"anchor={ (m['anchor_time'] or 'none')[:19]}", flush=True)


def cmd_status(args):
    """Consolidated live-endpoint payload: board + relative + operational + identity."""
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    from dorado_board import rebuild_index, load_entries
    from or_telemetry import load as load_tel
    board = rebuild_index()
    status = {
        "schema": "csoai.dorado-status/0.1",
        "kind": "measurement body status — a MEASUREMENT summary, never a certification",
        "register": "This is a measurement credential. It is not a certification, endorsement, "
                    "or conformity mark, and must not be presented as one.",
        "identity": "did:web:csoai.org#card-attestation-1",
        "board": {"count": board.get("count"), "chainOk": board.get("chainOk"),
                  "linked": board.get("linked"), "measurements": board.get("measurements", [])},
        "relative": json.load(open(os.path.join(ROOT, "board", "elo.json"))) if
                    os.path.exists(os.path.join(ROOT, "board", "elo.json")) else None,
        "operational": {"records": len(load_tel()),
                        "recent": load_tel()[-10:]},
    }
    if args.out:
        json.dump(status, open(args.out, "w"), indent=2)
        print(f"wrote {args.out}", flush=True)
    else:
        print(json.dumps(status, indent=2), flush=True)
    return 0


def cmd_e2e(args):
    """One-command end-to-end smoke (move 54): measure(fixture)->card->sign->verify->
    receipt->verify-receipt->anchor->verify-anchor->publish->board.

    Emits a JSON report with per-section ids, per-section + whole-run time budgets,
    and FAIL-FAST on the first hard error. Runs the WHOLE strand with an EPHEMERAL
    test key (kid=test, one-signer doctrine stamped test) into a TEMP board dir, so it
    never touches the committed board or the real pod signing key. A live measure
    requires --base <ollama>; the default is a clearly-labelled deterministic fixture.

    Measurement, never certification (the register rides every card + receipt + board row).
    """
    import shutil as _shutil
    import time as _t
    import tempfile as _tmp
    import hashlib as _hl
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    sys.path.insert(0, os.path.join(ROOT, "engine"))

    from run_axis import as_card, load_axes
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from dorado_sign import sign as sign_card, is_signed
    from dorado_verify import verify_card
    from dorado_receipt import build_card_receipt
    from dorado_receipt_verify import verify_receipt
    from dorado_anchor import card_digest
    from dorado_anchor_verify import verify_anchor

    axes, registry_id = load_axes(args.domain)
    n = len(axes)
    if args.base and args.base != "none":
        from run_axis import measure
        res = measure(args.model, axes=axes, base=args.base, delay=args.delay,
                      registry_id=registry_id)
        mode = "live"
    else:
        # Deterministic fixture (clearly labelled) so the chain is reproducible offline.
        ok = max(0, n - 2)
        res = {"model": args.model, "registry": registry_id, "n": n, "ok": ok,
               "accuracy": round(ok / n, 6) if n else 0.0, "measured": n, "total": n,
               "ts": args.pin_ts,
               "per_axis": [{"axis": a["slug"], "gold": a["gold"],
                             "verdict": ("PASS" if i < ok else "FAIL"),
                             "resp": "fixture", "measured": True}
                            for i, a in enumerate(axes)]}
        mode = "fixture"

    key = Ed25519PrivateKey.generate()
    subject = {"id": args.model, "name": args.model, "digest": "fixture"}
    card = as_card(res, subject, axes=axes)

    # temp board dir so publish never clobbers the committed (authoritative) board
    prior = os.environ.get("DORADO_BOARD_DIR")
    tmpdir = _tmp.mkdtemp(prefix="dorado-e2e-")
    os.environ["DORADO_BOARD_DIR"] = tmpdir

    state = {}
    budget = args.budget
    whole_budget = args.whole_budget
    t_start = _t.time()
    sections = []
    passed = True

    def run_section(sid, fn):
        nonlocal passed
        t0 = _t.time()
        rec = {"id": sid, "status": "FAIL", "ms": None, "detail": ""}
        try:
            detail = fn()
            rec["ms"] = round((_t.time() - t0) * 1000, 1)
            if rec["ms"] / 1000.0 > budget:
                rec["status"] = "BUDGET"
                passed = False
            else:
                rec["status"] = "PASS"
            rec["detail"] = detail
        except Exception as e:  # noqa: BLE001 — report any section failure as FAIL
            rec["ms"] = round((_t.time() - t0) * 1000, 1)
            rec["status"] = "FAIL"
            rec["detail"] = f"{type(e).__name__}: {e}"
            passed = False
        sections.append(rec)
        return rec

    def _step_card():
        state["card"] = card
        return f"{n}-axis card built, registry={registry_id}"

    def _step_sign():
        signed = sign_card(card, key, kid=args.kid, allow_test_identity=True)
        state["signed"] = signed
        assert is_signed(signed), "card not signed after sign()"
        # an ephemeral (non-published) key is always stamped kid=test (one-signer
        # doctrine); capture it so the receipt + anchors carry the SAME honest kid.
        state["sig_kid"] = signed["signature"]["kid"]
        return ("signed alg=%s kid=%s thumb=%s…" % (
            signed["signature"]["alg"], signed["signature"]["kid"],
            signed["signature"]["pubkey_thumbprint"][:10]))

    def _step_verify():
        v = verify_card(state["signed"])
        if not v["ok"]:
            raise AssertionError(v["reason"])
        return v["reason"]

    def _step_receipt():
        rcp = build_card_receipt(state["signed"], private_key=key, kid=state["sig_kid"],
                                 issued_at=args.pin_ts)
        assert rcp.get("signature", {}).get("sig"), "receipt not signed"
        assert rcp["subject_content_sha256"] == \
            _hl.sha256(_import_canonical(state["signed"])).hexdigest(), "receipt not bound to card canonical"
        state["receipt"] = rcp
        return "receipt content_id=%s… subject=%s… kid=%s" % (
            rcp["content_id"][:12], rcp["subject_content_sha256"][:12], rcp["kid"])

    def _step_verify_receipt():
        v = verify_receipt(state["receipt"], state["signed"])
        if not v["ok"]:
            raise AssertionError(v["reason"])
        return v["reason"]

    def _step_anchor():
        dig = card_digest(state["signed"])
        a = {"schema": "csoai.card-anchor/0.1", "card_content_sha256": dig,
             "anchors": [{"kind": "tsa-rfc3161", "digest_sha256": dig,
                          "message_imprint_matches": True, "gen_time": args.pin_ts}]}
        assert verify_anchor(a, state["signed"])["ok"], "hermetic anchor did not verify"
        state["anchor"] = a
        return "anchor digest=%s… imprint_matches=True" % dig[:12]

    def _step_verify_anchor():
        v = verify_anchor(state["anchor"], state["signed"])
        if not v["ok"]:
            raise AssertionError(v["reason"])
        return v["reason"]

    def _step_publish():
        from dorado_board import publish
        e = publish(state["signed"], state["receipt"], state["anchor"])
        if e.get("deduped"):
            raise AssertionError("board deduped a fresh card")
        state["entry"] = e
        return "published hash=%s… kid=%s signed=%s" % (
            e["hash"][:16], e["kid"], e["signed"])

    def _step_board():
        from dorado_board import rebuild_index
        idx = rebuild_index()
        state["index"] = idx
        if not idx.get("chainOk") or idx.get("count") < 1 or \
           idx.get("linked") != idx.get("count"):
            raise AssertionError("board index not coherent: %s" % idx)
        return "board count=%s chainOk=%s linked=%s" % (
            idx["count"], idx["chainOk"], idx["linked"])

    try:
        for sid, fn in [("card", _step_card), ("sign", _step_sign),
                        ("verify", _step_verify), ("receipt", _step_receipt),
                        ("verify-receipt", _step_verify_receipt),
                        ("anchor", _step_anchor), ("verify-anchor", _step_verify_anchor),
                        ("publish", _step_publish), ("board", _step_board)]:
            rec = run_section(sid, fn)
            if args.fail_fast and rec["status"] == "FAIL":
                break
    finally:
        _shutil.rmtree(tmpdir, ignore_errors=True)
        if prior is None:
            os.environ.pop("DORADO_BOARD_DIR", None)
        else:
            os.environ["DORADO_BOARD_DIR"] = prior

    total_ms = round((_t.time() - t_start) * 1000, 1)
    if total_ms / 1000.0 > whole_budget:
        passed = False

    result = {
        "schema": "csoai.dorado-e2e/0.1",
        "kind": "end-to-end smoke — a MEASUREMENT pipeline check, never a certification",
        "register": "This is a measurement credential. It is not a certification, "
                    "endorsement, or conformity mark, and must not be presented as one.",
        "run": mode,
        "model": args.model,
        "domain": registry_id,
        "ephemeral_key": True,
        # the ACTUAL stamped kid (an ephemeral key is stamped test-identity by the
        # one-signer doctrine), never the requested-but-overridden did:web id.
        "kid": state.get("sig_kid", args.kid),
        "budget_seconds_per_section": budget,
        "whole_run_seconds": args.whole_budget,
        "elapsed_ms": total_ms,
        "fail_fast": args.fail_fast,
        "sections": sections,
        "pass": passed,
    }
    if args.out:
        json.dump(result, open(args.out, "w"), indent=2)
        print(f"wrote {args.out}", flush=True)
        print(json.dumps(result, indent=2), flush=True)
    elif args.json:
        print(json.dumps(result, indent=2), flush=True)
    else:
        np = sum(1 for s in sections if s["status"] == "PASS")
        print(f"E2E: {'PASS' if passed else 'FAIL'} ({np}/{len(sections)} sections, "
              f"{total_ms}ms) run={mode} — measurement, never certification", flush=True)
    return 0 if passed else 1


def _import_canonical(card):
    from dorado_sign import canonical
    return canonical(card)


def main():
    ap = argparse.ArgumentParser(description="DORADO measurement CLI.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("axes", help="List the 16 GSPC axes")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_axes)

    p = sub.add_parser("measure", help="Measure a model on all axes")
    p.add_argument("--model", required=True)
    p.add_argument("--base", default=None, help="Ollama endpoint (default localhost:11434)")
    p.add_argument("--domain", default=None, help="Domain registry: bond/bank/insurance/equity/index/cross-border (default 16-axis)")
    p.add_argument("--out", default=None, help="Write axis-engine record here")
    p.add_argument("--card", default=None, help="Write DORADO measurement card here")
    p.add_argument("--card-subject-id", default="local")
    p.add_argument("--card-subject-name", default=None)
    p.add_argument("--delay", type=float, default=0.0)
    p.set_defaults(func=cmd_measure)

    p = sub.add_parser("domains", help="List the domain axis registries")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_domains)

    p = sub.add_parser("openrouter", help="Probe the live OpenRouter model universe (cost/context/provider)")
    p.add_argument("--search", default=None, help="Filter by id/substring")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--save", default=None, help="Save the full universe to a JSON file")
    p.set_defaults(func=cmd_openrouter)

    p = sub.add_parser("elo", help="Rank models from pairwise results (Elo or Bradley-Terry + CI)")
    p.add_argument("--pairs", required=True, help="JSON list of [winner, loser, margin]")
    p.add_argument("--method", default="elo", choices=["elo", "bt"])
    p.add_argument("--n-min", type=int, default=30)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_elo)

    p = sub.add_parser("compare", help="Compare two models on the relative (pairwise) axes + cost telemetry")
    p.add_argument("--model-a", required=True)
    p.add_argument("--model-b", required=True)
    p.add_argument("--domain", default="relative")
    p.add_argument("--base", default="none", help="Ollama endpoint for a live pairwise measure (default none = report axis set)")
    p.add_argument("--out", default=None)
    p.set_defaults(func=cmd_compare)

    p = sub.add_parser("telemetry", help="Show captured cost/latency/throughput telemetry")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_telemetry)

    p = sub.add_parser("crosswalk", help="Show the domain->provision crosswalk (east-west bridge)")
    p.add_argument("--domain", default=None, help="Show provisions for one domain only")
    p.set_defaults(func=cmd_crosswalk)

    p = sub.add_parser("selfcheck", help="Run hermetic deterministic tests")
    p.set_defaults(func=cmd_selfcheck)

    p = sub.add_parser("sign", help="Sign a DORADO measurement card (Ed25519, COSE_Sign1)")
    p.add_argument("--card", required=True)
    p.add_argument("--key-file", default=None, help="Raw/PEM Ed25519 private key (pod-held; NOT in repo)")
    p.add_argument("--pem-file", default=None, help="PEM Ed25519 private key")
    p.add_argument("--kid", default=None, help="kid (default did:web:csoai.org#card-attestation-1)")
    p.add_argument("--allow-test-identity", action="store_true", help="Allow a NON-published key (stamps kid=test); required for demo/test keys (one-signer doctrine)")
    p.add_argument("--out", default=None)
    p.set_defaults(func=cmd_sign)

    p = sub.add_parser("verify", help="Stranger-verify a signed card with the public key only")
    p.add_argument("--card", required=True)
    p.add_argument("--pubkey", default=None, help="Reference public key b64 to pin identity")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("receipt", help="Build an SCITT receipt (RFC 9943) binding a card")
    p.add_argument("--card", required=True)
    p.add_argument("--kid", default=None, help="kid (default did:web:csoai.org#card-attestation-1)")
    p.add_argument("--key-file", default=None, help="Pod Ed25519 private key (repo never embeds it)")
    p.add_argument("--allow-test-identity", action="store_true", help="Allow a NON-published key (stamps kid=test) so no-key EAT receipts are signed (one-signer doctrine)")
    p.add_argument("--out", default=None, help="Write receipt here")
    p.add_argument("--receipt-out", default=None, help="Alias for --out")
    p.set_defaults(func=cmd_receipt)

    p = sub.add_parser("verify-receipt", help="Stranger-verify an SCITT receipt (optionally against a card)")
    p.add_argument("--receipt", required=True)
    p.add_argument("--card", default=None, help="Card to bind-check the receipt against")
    p.set_defaults(func=cmd_verify_receipt)

    p = sub.add_parser("anchor", help="Anchor a signed card to external time (RFC 3161 TSR)")
    p.add_argument("--card", required=True)
    p.add_argument("--tsa", default="https://rfc3161.ai.moda")
    p.add_argument("--no-rekor", action="store_true", help="Skip the optional Rekor log entry")
    p.add_argument("--key-file", default=None, help="Pod Ed25519 private key to sign the rekor entry (else honest dependency report)")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_anchor)

    p = sub.add_parser("verify-anchor", help="Verify a card anchor (TSA imprint match + digest binding)")
    p.add_argument("--anchor", required=True)
    p.add_argument("--card", required=True)
    p.set_defaults(func=cmd_verify_anchor)

    p = sub.add_parser("verify-all", help="One-command verify: card (+ optional receipt + anchor)")
    p.add_argument("--card", required=True)
    p.add_argument("--receipt", default=None)
    p.add_argument("--anchor", default=None)
    p.add_argument("--pubkey", default=None)
    p.set_defaults(func=cmd_verify_all)

    p = sub.add_parser("license", help="Generate a signed data-license manifest (mechanism)")
    p.add_argument("--licensee", required=True)
    p.add_argument("--dataset-id", required=True)
    p.add_argument("--term-months", type=int, default=12)
    p.add_argument("--price-gbp", type=int, required=True)
    p.add_argument("--scope", required=True)
    p.add_argument("--card-digest", required=True, help="the measured dataset's card content_id")
    p.add_argument("--key-file", default=None, help="Pod Ed25519 private key (repo never embeds it)")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_license)

    p = sub.add_parser("publish", help="Publish a signed measurement card to the DORADO board")
    p.add_argument("--card", required=True)
    p.add_argument("--receipt", default=None)
    p.add_argument("--anchor", default=None)
    p.set_defaults(func=cmd_publish)

    p = sub.add_parser("board", help="Show the DORADO measurement board index")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_board)

    p = sub.add_parser("status", help="Consolidated live-endpoint payload (board + relative + operational + identity)")
    p.add_argument("--out", default=None, help="Write the status payload to a JSON file")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("e2e", help="One-command end-to-end smoke (measure->card->sign->verify->receipt->anchor->publish->board), JSON, fail-fast, per-section + whole-run time budgets (hermetic, ephemeral key, temp board)")
    p.add_argument("--model", default="fixture-model")
    p.add_argument("--domain", default=None, help="Domain registry (default 16-axis); must be a provision-mapped domain for the crosswalk card")
    p.add_argument("--base", default="none", help="Ollama endpoint for a LIVE measure (default none = deterministic fixture)")
    p.add_argument("--delay", type=float, default=0.0)
    p.add_argument("--kid", default="did:web:csoai.org#test-identity",
                   help="kid for the ephemeral e2e key (an ephemeral key is ALWAYS stamped "
                        "test-identity by the one-signer doctrine; do not pass the production kid)")
    p.add_argument("--pin-ts", default="2026-08-24T00:00:00Z", help="RFC 3339 issued_at (pinned for the fixture's determinism)")
    p.add_argument("--budget", type=float, default=60.0, help="Per-section time budget (seconds)")
    p.add_argument("--whole-budget", type=float, default=300.0, help="Whole-run time budget (seconds)")
    p.add_argument("--fail-fast", action="store_true", help="Stop at the first hard section failure")
    p.add_argument("--json", action="store_true", help="Emit the full JSON report to stdout")
    p.add_argument("--out", default=None, help="Write the full JSON report to a file")
    p.set_defaults(func=cmd_e2e)

    p = sub.add_parser("export", help="Turn an axis-engine result into the licensable data product")
    p.add_argument("--in", dest="inp", required=True, help="axis-engine result JSON")
    p.add_argument("--out-dir", default="data-out")
    p.add_argument("--subject-id", default=None)
    p.add_argument("--subject-name", default=None)
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("export-relative", help="Export a pairwise measure as the licensable relative dataset")
    p.add_argument("--in", dest="inp", required=True, help="pairwise result JSON")
    p.add_argument("--out-dir", default="data-relative-out")
    p.set_defaults(func=cmd_export_relative)

    p = sub.add_parser("export-operational", help="Export telemetry as the licensable operational (cost/latency) dataset")
    p.add_argument("--limit", type=int, default=None, help="Only the last N telemetry rows")
    p.add_argument("--out-dir", default="data-operational-out")
    p.set_defaults(func=cmd_export_operational)

    p = sub.add_parser("gates", help="GB/T 45654-style credibility gates self-check (calibration/over-refusal/per-axis n/total n)")
    p.add_argument("--in", dest="inp", default=None, help="Measurement result JSON with instrument_calibration_acc / overrefusal_rate / per_axis[].n")
    p.add_argument("--fixture", action="store_true", help="Use the deterministic qualifying fixture (selfcheck)")
    p.set_defaults(func=cmd_gates)

    p = sub.add_parser("sb315", help="SB 315-style machine-readable transparency summary + auditor-card template (bound to the signed card by digest)")
    p.add_argument("--card", required=True, help="Signed measurement card JSON")
    p.add_argument("--out", default=None, help="Write the transparency summary JSON here")
    p.add_argument("--audit-template-out", default=None, help="Write the auditor-card template JSON here")
    p.set_defaults(func=cmd_sb315)

    a = ap.parse_args()
    code = a.func(a)
    sys.exit(code or 0)


if __name__ == "__main__":
    main()

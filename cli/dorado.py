#!/usr/bin/env python3
"""dorado — the DORADO measurement command-line interface.

Subcommands:
  axes      List the 16 GSPC axes (+probe/gold), --json for machine-readable
  domains   List the domain axis registries (bond/bank/insurance/equity/index/cross-border)
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
import argparse, json, os, subprocess, sys

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
    from run_axis import measure, as_card, sha256, BASE, load_axes
    base = args.base or BASE
    axes, registry_id = load_axes(args.domain)
    print(f"Measuring {args.model} on {len(axes)} {registry_id or 'GSPC-16'} axes via {base} ...", flush=True)
    res = measure(args.model, axes=axes, base=base, delay=args.delay, registry_id=registry_id)
    rec = {"schema": "csoai.axis-engine/0.3", "axes": len(axes), "registry": registry_id, **res}
    if args.out:
        json.dump(rec, open(args.out, "w"), indent=2)
        print(f"wrote {args.out}", flush=True)
    if args.card:
        subject = {"id": args.card_subject_id, "name": args.card_subject_name or args.model,
                   "digest": sha256("local:" + args.model)}
        json.dump(as_card(res, subject, axes=axes), open(args.card, "w"), indent=2)
        print(f"wrote {args.card}", flush=True)
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

    p = sub.add_parser("export", help="Turn an axis-engine result into the licensable data product")
    p.add_argument("--in", dest="inp", required=True, help="axis-engine result JSON")
    p.add_argument("--out-dir", default="data-out")
    p.add_argument("--subject-id", default=None)
    p.add_argument("--subject-name", default=None)
    p.set_defaults(func=cmd_export)

    a = ap.parse_args()
    code = a.func(a)
    sys.exit(code or 0)


if __name__ == "__main__":
    main()

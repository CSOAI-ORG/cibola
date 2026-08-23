#!/usr/bin/env python3
"""cibola — the CIBOLA measurement command-line interface.

Subcommands:
  axes      List the 16 GSPC axes (+probe/gold), --json for machine-readable
  measure   Measure a model on all axes (Ollama), emit axis-engine record + optional card
  sign      Sign a CIBOLA measurement card (Ed25519, COSE_Sign1, one-signer doctrine)
  verify    Stranger-verify a signed card with the public key only
  export    Turn an axis-engine result into the licensable data product (Q/A + pairs + incidents)
  selfcheck Run the hermetic deterministic test battery (no network)

Measurement, never certification. See GOVERNANCE.md and the CIBOLA card schema.
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
    from run_axis import measure, as_card, sha256, BASE
    base = args.base or BASE
    print(f"Measuring {args.model} on 16 GSPC axes via {base} ...", flush=True)
    res = measure(args.model, base=base, delay=args.delay)
    rec = {"schema": "csoai.axis-engine-16/0.2", "axes": 16, **res}
    if args.out:
        json.dump(rec, open(args.out, "w"), indent=2)
        print(f"wrote {args.out}", flush=True)
    if args.card:
        subject = {"id": args.card_subject_id, "name": args.card_subject_name or args.model,
                   "digest": sha256("local:" + args.model)}
        json.dump(as_card(res, subject), open(args.card, "w"), indent=2)
        print(f"wrote {args.card}", flush=True)
    print(f"[{args.model}] {res['ok']}/{res['n']} pass  {res['accuracy']}  "
          f"measured={res['measured']}/{res['total']}", flush=True)


def cmd_selfcheck(args):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "test", "battery.py")])
    return r.returncode


def _load_signing_key():
    """Load the CIBOLA pod signing key. The private key NEVER comes from the repo.

    Sources, in order: --key-file path; env CIBOLA_SIGNING_KEY_FILE; the pod's
    keystone loader (csoai_city.keystone.load_signing_key). A key must be
    supplied by the signing pod — this repo never embeds the private half.
    """
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    path = os.environ.get("CIBOLA_SIGNING_KEY_FILE")
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
        raise SystemExit(f"no signing key: set CIBOLA_SIGNING_KEY_FILE to the pod key "
                         f"(repo never embeds the private half). keystone: {e}")


def cmd_sign(args):
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    from cibola_sign import sign, is_signed
    card = json.load(open(args.card))
    if args.pem_file:
        key = _load_signing_key_from_pem(args.pem_file)
    elif args.key_file:
        os.environ["CIBOLA_SIGNING_KEY_FILE"] = args.key_file
        key = _load_signing_key()
    else:
        key = _load_signing_key()
    if is_signed(card):
        print(f"{args.card} already signed (signature present); re-signing over canonical form", flush=True)
    signed = sign(card, key, kid=args.kid)
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
    from cibola_verify import verify_card
    card = json.load(open(args.card))
    res = verify_card(card, args.pubkey)
    print(f"{res['reason']}" + (f" (kid={res.get('kid')})" if res.get("kid") else ""), flush=True)
    if res["ok"] and args.pubkey is None:
        print("  note: identity NOT pinned to a reference key — signature is valid, "
              "identity is self-asserted (did:web:csoai.org#card-attestation-1)", flush=True)
    return 0 if res["ok"] else 1


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


def main():
    ap = argparse.ArgumentParser(description="CIBOLA measurement CLI.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("axes", help="List the 16 GSPC axes")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_axes)

    p = sub.add_parser("measure", help="Measure a model on all axes")
    p.add_argument("--model", required=True)
    p.add_argument("--base", default=None, help="Ollama endpoint (default localhost:11434)")
    p.add_argument("--out", default=None, help="Write axis-engine record here")
    p.add_argument("--card", default=None, help="Write CIBOLA measurement card here")
    p.add_argument("--card-subject-id", default="local")
    p.add_argument("--card-subject-name", default=None)
    p.add_argument("--delay", type=float, default=0.0)
    p.set_defaults(func=cmd_measure)

    p = sub.add_parser("selfcheck", help="Run hermetic deterministic tests")
    p.set_defaults(func=cmd_selfcheck)

    p = sub.add_parser("sign", help="Sign a CIBOLA measurement card (Ed25519, COSE_Sign1)")
    p.add_argument("--card", required=True)
    p.add_argument("--key-file", default=None, help="Raw/PEM Ed25519 private key (pod-held; NOT in repo)")
    p.add_argument("--pem-file", default=None, help="PEM Ed25519 private key")
    p.add_argument("--kid", default=None, help="kid (default did:web:csoai.org#card-attestation-1)")
    p.add_argument("--out", default=None)
    p.set_defaults(func=cmd_sign)

    p = sub.add_parser("verify", help="Stranger-verify a signed card with the public key only")
    p.add_argument("--card", required=True)
    p.add_argument("--pubkey", default=None, help="Reference public key b64 to pin identity")
    p.set_defaults(func=cmd_verify)

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

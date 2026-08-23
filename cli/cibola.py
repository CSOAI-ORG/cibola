#!/usr/bin/env python3
"""cibola — the CIBOLA measurement command-line interface.

Subcommands:
  axes     List the 16 GSPC axes (+probe/gold), --json for machine-readable
  measure  Measure a model on all axes (Ollama), emit axis-engine record + optional card
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

    a = ap.parse_args()
    code = a.func(a)
    if a.cmd != "measure":
        sys.exit(code or 0)


if __name__ == "__main__":
    main()

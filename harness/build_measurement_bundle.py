#!/usr/bin/env python3
"""build_measurement_bundle.py — consolidate the measurement registers into one bundle.

Merges the RWA target-list + regulation-feeds registry + content-engine (AEO) into a single,
register-bearing, downloadable corpus. The register + neutrality ride the top level and every
sub-bundle. This is a LICENSABLE DATA bundle — a vendor licenses the measured data, never a score.
Measurement, never certification.
"""
import json, os

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HOME, "assets", "measurement-bundle.json")

REGISTER = ("This data is derived from a measurement. It is not a certification, endorsement, "
            "or conformity mark, and must not be presented as one.")
NEUTRALITY = "licenses the measured data, never the score"


def load(p):
    return json.load(open(p)) if os.path.exists(p) else None


def main() -> int:
    bundle = {
        "schema": "csoai.measurement-bundle/0.1",
        "kind": "licensable measurement corpus (consolidated registers)",
        "register": REGISTER,
        "neutrality": NEUTRALITY,
        "bundles": {
            "rwa_target_list": load(os.path.join(HOME, "assets", "registers", "rwa", "index.json")),
            "regulation_feeds": load(os.path.join(HOME, "assets", "registers", "regulation-feeds",
                                                  "regulatory-feeds-registry.json")),
            "content_engine": load(os.path.join(HOME, "assets", "content-engine", "index.json")),
        },
        "note": "Consolidated measurement registers. License the data, never the score; "
                "measurement, never certification. Regenerate via 'dorado batch'.",
    }
    # drop any None (a register not yet built) rather than emitting null.
    bundle["bundles"] = {k: v for k, v in bundle["bundles"].items() if v is not None}
    json.dump(bundle, open(OUT, "w"), indent=2)
    names = list(bundle["bundles"].keys())
    print(f"wrote consolidated measurement bundle -> {OUT} ({len(names)} bundles: {', '.join(names)})",
          flush=True)
    return 0


if __name__ == "__main__":
    main()

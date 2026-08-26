#!/usr/bin/env python3
"""build_content_engine_index.py — build the AEO/search-ready content-engine index.

Wires the docs/aeo/*.json payloads (Stanford 42% AEO + RWA $365B tokenization gap, both
complete {schema,slug,title,description,canon,body,links}) into one discoverable, register-bearing
content feed so they can be surfaced by the front-end / agent. The canon + register ride every
item; a measurement-derived corpus is never an endorsement.

Doctrine: register verbatim; measurement never certification.
"""
import json, os, glob

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AEO_DIR = os.path.join(HOME, "docs", "aeo")
OUT_DIR = os.path.join(HOME, "assets", "content-engine")
OUT = os.path.join(OUT_DIR, "index.json")

REGISTER = ("This content is derived from a measurement. It is not a certification, "
            "endorsement, or conformity mark, and must not be presented as one.")


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    items = []
    for f in sorted(glob.glob(os.path.join(AEO_DIR, "*.json"))):
        d = json.load(open(f))
        items.append({
            "slug": d.get("slug"), "title": d.get("title"),
            "description": d.get("description"), "date": d.get("date"),
            "canon": d.get("canon"), "links": d.get("links", []), "source": os.path.basename(f),
        })
    index = {
        "schema": "csoai.content-engine/0.1",
        "kind": "AEO/search-ready measurement corpus",
        "register": REGISTER,
        "count": len(items),
        "items": items,
    }
    json.dump(index, open(OUT, "w"), indent=2)
    print(f"wrote content-engine index -> {OUT} ({len(items)} AEO items)", flush=True)
    return 0


if __name__ == "__main__":
    main()

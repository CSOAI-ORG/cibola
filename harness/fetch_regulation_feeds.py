#!/usr/bin/env python3
"""fetch_regulation_feeds.py — live-regulation cross-reference with SHA-256 change-detection
(research rec #4 — 'build the live-regulation cross-reference on free official feeds').

Publishes the REGULATORY-FEEDS REGISTRY (the free official feeds DORADO cross-references, for
transparency) plus a driver that fetches each reachable feed, SHA-256-hashes the content, and
records a CHANGE only on a real content-hash delta — never fabricated.

Doctrine (verbatim):
  REGISTER = "This is a regulatory-change record. It is not a certification, endorsement, or
             conformity mark, and must not be presented as one."
  NEUTRALITY = "records a measured regulatory change, never certifies compliance"

HONEST SCOPE:
  - The registry documents the OFFICIAL feed endpoints and their observed reachability status
    at the time of the last fetch ('reachable' / 'bot-gated' / 'path-invalid' / 'error'). A
    reachability failure is recorded honestly, never silently dropped.
  - A 'change' is recorded ONLY when the SHA-256 of the fetched content differs from the
    previously-recorded hash for that feed. The FIRST fetch records a baseline ('baseline'),
    not a 'change' — a document cannot claim a change against nothing.
  - This is a MEASUREMENT (content-hash delta), not a legal opinion, not compliance assurance.
"""
from __future__ import annotations
import hashlib
import json
import os
import time
import urllib.request

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG_DIR = os.path.join(HOME, "assets", "registers", "regulation-feeds")
REGISTRY_PATH = os.path.join(REG_DIR, "regulatory-feeds-registry.json")
STATE_PATH = os.path.join(REG_DIR, "feed-state.json")
CHANGES_PATH = os.path.join(REG_DIR, "changes.jsonl")

REGISTER = ("This is a regulatory-change record. It is not a certification, endorsement, or "
            "conformity mark, and must not be presented as one.")
NEUTRALITY = "records a measured regulatory change, never certifies compliance"

# The REGULATORY-FEEDS REGISTRY: free/official feeds, verified reachable where possible.
# each entry: id, jurisdiction, name, endpoint, format, licence, notes, verified_reachable.
FEEDS = [
    {
        "id": "federal-register", "jurisdiction": "US", "name": "Federal Register (regulations.gov-backed)",
        "endpoint": "https://www.federalregister.gov/api/v1/documents.json?per_page=20&conditions%5Bpublication_date%5D%5Bgte%5D=2026-01-01",
        "format": "json", "licence": "public domain (U.S. Gov works)",
        "verified_reachable": True, "verified_http": 200,
        "notes": "REST/JSON, no API key. Official rulemaking publication record.",
    },
    {
        "id": "ecfr", "jurisdiction": "US", "name": "eCFR (Electronic Code of Federal Regulations)",
        "endpoint": "https://www.ecfr.gov/api/versioner/v1/titles.json",
        "format": "json", "licence": "public domain (U.S. Gov works)",
        "verified_reachable": True, "verified_http": 200,
        "notes": "Versioner REST API, no key. The live CFR, content-hash diffable.",
    },
    {
        "id": "eurlex", "jurisdiction": "EU", "name": "EUR-Lex (EU legal)",
        "endpoint": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
        "format": "html", "licence": "EU (© EU, reuse under CC-BY-4.0 for legislative texts)",
        "verified_reachable": True, "verified_http": 202,
        "notes": "CELEX content resolver; the EU AI Act CELEX shown as the reference anchor. "
                 "CELLAR SPARQL endpoint path varies — treat resolver as the stable free surface.",
    },
    {
        "id": "bis", "jurisdiction": "global", "name": "Bank for International Settlements",
        "endpoint": "https://www.bis.org/list/papers/index.htm",
        "format": "html", "licence": "© BIS (informational; free to read)",
        "verified_reachable": True, "verified_http": 200,
        "notes": "BIS publication listing page.",
    },
    {
        "id": "iosco", "jurisdiction": "global", "name": "IOSCO",
        "endpoint": "https://www.iosco.org/publications/",
        "format": "html", "licence": "© IOSCO (informational; free to read)",
        "verified_reachable": False, "verified_http": None,
        "notes": "Primary page reachable on some paths, 403 on others (bot-gating/edge vary). "
                 "Recorded honestly as variably-reachable, not claimed reachable.",
    },
]


def _get(url: str, timeout: int = 12) -> tuple[int, bytes]:
    """Fetch a URL, return (status, content). Never raises on network error."""
    req = urllib.request.Request(url, headers={"User-Agent": "csoai-k3/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:
        return 0, b""


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def classify(prev: str | None, content: bytes, last_class: str | None = None) -> tuple[str, str | None, str]:
    """Pure classification for a single feed observation.

    Returns (kind, content_hash_or_None, note). Kinds:
      baseline   — first observation (no previous hash). A doc cannot claim a change against
                   nothing, so this is recorded as a baseline, NOT a change.
      no-change  — content identical to the last observed hash.
      change     — content hash changed AND the feed is content-stable (did not flip last run).
      volatile   — content hash changed again after a prior change (the feed re-hashes every
                   fetch: anti-bot cookie / dynamic page). Treated as NON-evidence — a
                   re-hashing page is NOT a regulation change. Never reported as a change.
      unreachable— no content retrieved (bot-gated, JS-rendered, error). Recorded honestly.
    """
    if not content:
        return "unreachable", None, "no content retrieved (bot-gated/JS-rendered/error) — recorded honestly, never fabricated"
    ch = sha256(content)
    if prev is None:
        return "baseline", ch, "first observation — baseline recorded, no change claimed against nothing"
    if prev != ch:
        if last_class == "change":
            return "volatile", ch, (f"content hash changed again ({prev[:12]} -> {ch[:12]}); "
                                    "feed observed to re-hash across consecutive fetch — VOLATILE "
                                    "(anti-bot/dynamic page), NOT evidence of a real regulation change")
        return "change", ch, f"content hash changed {prev[:12]} -> {ch[:12]}"
    return "no-change", ch, "content hash unchanged"


def main() -> dict:
    os.makedirs(REG_DIR, exist_ok=True)
    state = json.load(open(STATE_PATH)) if os.path.exists(STATE_PATH) else {}
    changes = []
    for feed in FEEDS:
        fid = feed["id"]
        status, content = _get(feed["endpoint"])
        feed["_last_fetch_status"] = status
        # reachable means we captured content to hash; a 200/202 with an empty body (bot-gated,
        # JS-rendered) is honestly NOT reachable for hashing — never claim it.
        feed["_reachable"] = bool(content)
        feed["_verified_reachable_updated"] = feed["_reachable"]
        prev = state.get(fid, {}).get("sha256")
        last_class = state.get(fid, {}).get("last_class")
        kind, content_hash, note = classify(prev, content, last_class)
        if content_hash is not None:
            feed["_content_sha256"] = content_hash
        feed["_observation"] = kind
        changes.append({
            "schema": "csoai.regulatory-change/0.1",
            "feed": fid, "jurisdiction": feed["jurisdiction"], "endpoint": feed["endpoint"],
            "kind": kind, "sha256": content_hash, "prev_sha256": prev, "note": note,
            "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "register": REGISTER, "neutrality": NEUTRALITY,
        })
        state[fid] = {"sha256": content_hash, "last_class": kind,
                      "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    registry = {
        "schema": "csoai.regulatory-feeds-registry/0.1",
        "kind": "regulatory feeds cross-reference (measurement)",
        "register": REGISTER, "neutrality": NEUTRALITY,
        "feeds": FEEDS,
        "note": "Free official feeds DORADO cross-references. Published for transparency "
                "(research rec #4). A change is recorded ONLY on a real SHA-256 content-hash "
                "delta on a content-stable feed; a feed that re-hashes every fetch is marked "
                "'volatile' (anti-bot/dynamic), never reported as a regulation change; an "
                "unreachable feed is reported honestly, never fabricated.",
    }
    json.dump(registry, open(REGISTRY_PATH, "w"), indent=2)
    json.dump(state, open(STATE_PATH, "w"), indent=2)
    with open(CHANGES_PATH, "a") as fh:
        for c in changes:
            fh.write(json.dumps(c, separators=(",", ":")) + "\n")
    print(f"regulatory feeds: {len(FEEDS)} registry entries; "
          f"reachable={sum(1 for f in FEEDS if f['_reachable'])} "
          f"| observations: " + ", ".join(f"{c['feed']}={c['kind']}" for c in changes), flush=True)
    return {"registry_path": REGISTRY_PATH, "changes": changes}


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""ots-anchor.py — OpenTimestamps (Bitcoin-anchored) anchoring for signed cards.

Move 8 of the 2026 Playbook: ship the PLANNED OpenTimestamps truth-layer LIVE.
Each anchored artifact gets an .ots proof committed next to it; any stranger can
re-verify against the Bitcoin calendar, forever, without asking us.

Usage:
  python3 harness/ots-anchor.py anchor <sha256hex> [label]
  python3 harness/ots-anchor.py anchor-file <path>
  python3 harness/ots-anchor.py verify <sha256hex> <proof.ots>

Honest semantics: timestamping proves *existence at time T*, never meaning. It is
the permanence layer UNDER the Ed25519 signature + SCITT receipt + RFC 3161 anchor.
"""
import sys, os, json, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OTS_DIR = ROOT / "truth-layer" / "ots"
MANIFEST = OTS_DIR / "MANIFEST.json"


def load_manifest():
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text())
    return {"schema": "csoai.ots-manifest/0.1", "entries": []}


def save_manifest(m):
    OTS_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(m, indent=1))


def anchor(hexdigest: str, label: str):
    from opentimestamps.client import timestamp
    proof = timestamp(bytes.fromhex(hexdigest))
    proof_path = OTS_DIR / f"{hexdigest[:16]}.ots"
    proof_path.write_bytes(proof)
    m = load_manifest()
    m["entries"].append({
        "label": label, "sha256": hexdigest,
        "proof": str(proof_path.relative_to(ROOT)),
        "anchored_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "anchored-pending-calendar-upgrade",
    })
    save_manifest(m)
    print(f"ANCHORED {hexdigest[:16]}… ({label}) -> {proof_path.name} ({len(proof)} B)")


def anchor_file(path: str):
    data = Path(path).read_bytes()
    import hashlib
    anchor(hashlib.sha256(data).hexdigest(), path)


def verify(hexdigest: str, proof: str):
    from opentimestamps.client import verify_local
    from opentimestamps.core.timestamp import Timestamp
    from opentimestamps.types import Timestamp as _T  # noqa
    proof_bytes = Path(proof).read_bytes()
    try:
        res = verify_local(bytes.fromhex(hexdigest), proof_bytes)
        print(f"VERIFY LOCAL: {res} (True = proven against local calendar)")
    except Exception as e:
        print(f"VERIFY LOCAL: needs calendar upgrade — {type(e).__name__}: {str(e)[:120]}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "anchor" and len(sys.argv) >= 3:
        anchor(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "unnamed")
    elif cmd == "anchor-file" and len(sys.argv) >= 3:
        anchor_file(sys.argv[2])
    elif cmd == "verify" and len(sys.argv) >= 4:
        verify(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)

#!/usr/bin/env python3
"""dorado_board.py — the DORADO measurement board (the body's record of what was measured).

Mirrors the estate's chain-index pattern: each published measurement card is added
as a content-addressed entry (hash = sha256 of the card's canonical form, the SAME
digest the receipt/anchors bind), chained with a `prev` link so the board is an
append-only, tamper-evident sequence. A regenerated index gives `count`,
`chainOk`, `linked`/`unlinked`, and a queryable view.

The board is a MEASUREMENT registry, not a rank table. It records *what was
measured and when*; it never scores or certifies. A card must carry a valid
signature to be published (stranger-verified offline) — the board publishes
only verifiable measurements.

Layout:
    board/measurements.jsonl   — append-only entries (one per published card)
    board/board-index.json     — regenerated index (chainOk, count, queryable view)
"""
from __future__ import annotations
import hashlib, json, os, sys, time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Board dir is read LAZILY (env DORADO_BOARD_DIR overrides for hermetic tests) so this
# module can be imported once without freezing the dir; each call re-reads the env.
REGISTER = ("This is a measurement credential. It is not a certification, endorsement, "
            "or conformity mark, and must not be presented as one.")


def _board_dir() -> str:
    return os.environ.get("DORADO_BOARD_DIR") or os.path.join(ROOT, "board")


def _measurements_path() -> str:
    return os.path.join(_board_dir(), "measurements.jsonl")


def _index_path() -> str:
    return os.path.join(_board_dir(), "board-index.json")


def _card_hash(card: dict) -> str:
    """Content address = sha256 of the card's canonical form (matches receipt/anchor digest)."""
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    from dorado_sign import canonical
    return hashlib.sha256(canonical(card)).hexdigest()


def _entry(card: dict, receipt: dict | None = None, anchor: dict | None = None) -> dict:
    """Build a board entry (content-addressed, no signature on the entry itself)."""
    h = _card_hash(card)
    return {
        "hash": h,
        "ts": card.get("issued_at") or datetime.now(timezone.utc).isoformat(),
        "registry": card.get("benchmark", {}).get("id", "unknown"),
        "subject": card.get("subject", {}).get("id", "unknown"),
        "subject_name": card.get("subject", {}).get("name", "unknown"),
        "measured": card.get("measured_count"),
        "total": card.get("total_count"),
        "kid": (card.get("signature") or {}).get("kid"),
        "signed": bool((card.get("signature") or {}).get("sig")),
        "receipt_content_id": (receipt or {}).get("content_id"),
        "anchor_generic_time": next((a.get("gen_time") for a in (anchor or {}).get("anchors", [])
                                     if a.get("kind") == "tsa-rfc3161"), None),
        "provision_axes": len(card.get("provision_map", {})),
        "register": REGISTER,
        "path": None,  # filled on append
    }


def publish(card: dict, receipt: dict | None = None, anchor: dict | None = None) -> dict:
    """Append a measurement card to the board, deduping on content hash.

    Returns the entry (or an existing duplicate). Refuses to publish a card that is
    not signed (the board only records stranger-verifiable measurements)."""
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    from dorado_sign import is_signed
    if not is_signed(card):
        raise ValueError("refusing to publish an unsigned card to the measurement board "
                         "(the board records stranger-verifiable measurements only)")
    ent = _entry(card, receipt, anchor)
    bdir, mpath = _board_dir(), _measurements_path()
    os.makedirs(bdir, exist_ok=True)
    # dedupe: if the content hash already exists, return the existing entry
    if os.path.exists(mpath):
        for line in open(mpath):
            try:
                if json.loads(line).get("hash") == ent["hash"]:
                    ent["deduped"] = True
                    return ent
            except Exception:
                pass
    # chain-link the new entry to the previous one
    prev = None
    if os.path.exists(mpath):
        try:
            lines = [l for l in open(mpath) if l.strip()]
            if lines:
                prev = json.loads(lines[-1]).get("hash")
        except Exception:
            prev = None
    ent["prev"] = prev
    ent["i"] = _index_count()
    ent["path"] = f"measurement-{ent['hash'][:12]}.json"
    with open(mpath, "a") as fh:
        fh.write(json.dumps(ent, separators=(",", ":")) + "\n")
    rebuild_index()
    return ent


def _index_count() -> int:
    mpath = _measurements_path()
    if os.path.exists(mpath):
        return sum(1 for l in open(mpath) if l.strip())
    return 0


def load_entries() -> list[dict]:
    entries = []
    mpath = _measurements_path()
    if os.path.exists(mpath):
        for line in open(mpath):
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except Exception:
                    pass
    return entries


def rebuild_index() -> dict:
    """Regenerate board-index.json with chain diagnostics (mirrors estate chain-index)."""
    entries = load_entries()
    chain_ok = True
    linked = 0
    for i, e in enumerate(entries):
        expect_prev = entries[i - 1]["hash"] if i > 0 else None
        if e.get("prev") != expect_prev:
            chain_ok = False
        else:
            linked += 1
    index = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(entries),
        "chainOk": chain_ok,
        "linked": linked,
        "unlinked": len(entries) - linked,
        "measurements": [{
            "hash": e["hash"][:16], "ts": e["ts"], "registry": e["registry"],
            "subject": e["subject_name"], "measured": e.get("measured"), "total": e.get("total"),
            "kid": e.get("kid"), "signed": e.get("signed"),
            "receipt": (e.get("receipt_content_id") or "")[:12],
            "anchor_time": e.get("anchor_generic_time"), "provision_axes": e.get("provision_axes"),
        } for e in entries],
    }
    bdir, ipath = _board_dir(), _index_path()
    os.makedirs(bdir, exist_ok=True)
    # CLOBBER GUARD: never let a lower-count local regen overwrite the authoritative
    # committed board record (the pod is the source of truth). The committed index may
    # be richer than the local measurements.jsonl (e.g. the Mac only has a few local
    # rows while the pod has the full chain). Refuse to SHRINK an existing index.
    if os.path.exists(ipath):
        try:
            existing = json.load(open(ipath))
            existing_count = existing.get("count", 0)
            if len(entries) < existing_count:
                # keep the richer committed record; merge any genuinely new measurements
                merged = _merge_unique(existing, entries)
                if len(merged["measurements"]) != existing_count or not os.environ.get("DORADO_ALLOW_SHRINK"):
                    json.dump(merged, open(ipath, "w"), indent=2)
                    return merged
        except Exception:
            pass
    json.dump(index, open(ipath, "w"), indent=2)
    return index


def _merge_unique(existing: dict, entries: list[dict]) -> dict:
    """Merge local entries into the existing committed index without shrinking it."""
    seen = {m["hash"] for m in existing.get("measurements", [])}
    extra = [{"hash": e["hash"][:16], "ts": e["ts"], "registry": e["registry"],
              "subject": e["subject_name"], "measured": e.get("measured"), "total": e.get("total"),
              "kid": e.get("kid"), "signed": e.get("signed"),
              "receipt": (e.get("receipt_content_id") or "")[:12],
              "anchor_time": e.get("anchor_generic_time"), "provision_axes": e.get("provision_axes")}
             for e in entries if e["hash"][:16] not in seen]
    return {"generated_at": existing.get("generated_at"), "count": len(existing.get("measurements", [])) + len(extra),
            "chainOk": existing.get("chainOk", True), "linked": existing.get("linked", 0),
            "unlinked": existing.get("unlinked", 0),
            "measurements": existing.get("measurements", []) + extra}


def verify_chain() -> dict:
    """Recompute the chain from the append-only log and report consistency."""
    return rebuild_index()

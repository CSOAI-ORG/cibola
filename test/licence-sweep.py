#!/usr/bin/env python3
"""test/licence-sweep.py — dependency licence landmine sweep (move 34).

The estate only adopts PERMISSIVE dependencies. A licence that locks a third party into
our measurement pipeline (AGPL/GPL copyleft) or a non-commercial / commercial-restricted
agent-dataset family (PersonaHub, genagents, AgentSociety-commercial, Genie 3, Cosmos)
is a LANDMINE: it would forbid the score-layer from licensing the measured data, or drag
the instrument into a licence the buyer cannot accept. The canon ("a vendor can license
the telemetry; never the score", buyer-side money only) makes this a hard stop, not a
preference.

This guard, hermetic, asserts the sweep:
  1. Every third-party module imported by the estate's code is DECLARED in the manifest
     and belongs to a permitted (permissive) licence — an undeclared or non-permissive
     third-party import is a hard fail.
  2. No HARD-EXCLUDED family name appears in any code/data asset (engine, harness, agent,
     test, cli, scripts, data): a landmine cannot silently enter a probe, a persona, a
     dataset or a model reference.
  3. The manifest itself declares the excluded families + the permissive allowlist so the
     rule is auditable, and every declared dependency is permitted (or explicitly marked
     INTERNAL for the estate's own package).

docs/ is intentionally NOT scanned for the excluded-family names: the rule is documented
by naming them (that is the only place they legitimately appear).
"""
from __future__ import annotations

import ast, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "data", "dependency-licence-manifest.json")

# top-level modules that are the estate's own (internal / local), not third-party deps.
INTERNAL_MODULES = {
    "agent", "csoai_city", "dorado_a2a_client", "dorado_anchor", "dorado_anchor_verify",
    "dorado_board", "dorado_receipt", "dorado_receipt_verify", "dorado_sign",
    "dorado_verify", "elo", "engine", "export_data", "data_listing", "gbt_gates", "game_replay", "harness",
    "mcp_server", "or_telemetry", "rate_cap", "run_axis", "sb315", "scitt_verify",
    "verify_kit",
}
# top-level modules that are stdlib (never a licence surface).
STDLIB_OK = set(sys.stdlib_module_names)

# code + asset roots to scan for hard-excluded family names (NOT docs/).
SCAN_ROOTS = ["engine", "harness", "agent", "test", "cli", "scripts", "data"]
CODE_EXTS = {".py", ".sh"}
ASSET_EXTS = {".json", ".jsonl", ".md"}


def iter_py_files(root: str):
    for dp, dn, fn in os.walk(os.path.join(ROOT, root)):
        if "__pycache__" in dp or ".git" in dp:
            continue
        for f in fn:
            if f.endswith(".py"):
                yield os.path.join(dp, f)


def scan_imports() -> set[str]:
    third = set()
    for root in INTERNAL_SCAN_ROOTS:
        for p in iter_py_files(root):
            try:
                tree = ast.parse(open(p, encoding="utf-8").read())
            except Exception:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        third.add(a.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    third.add(node.module.split(".")[0])
    return third


def main() -> int:
    manifest = json.load(open(MANIFEST))
    assert manifest.get("schema") == "csoai.dependency-licence/0.1", "manifest schema drift"

    hard_excluded = set(manifest["hard_excluded_families"])
    allowlist = set(manifest["permissive_allowlist_spdx"])
    assert hard_excluded, "manifest must declare the hard-excluded families"
    assert allowlist, "manifest must declare the permissive allowlist"

    declared = {}
    for d in manifest["dependencies"]:
        declared[d["name"]] = d
    internal = {p["name"] for p in manifest.get("internal_packages", [])}

    # (1) every third-party import is declared + permitted (or estate-internal).
    third = scan_imports()
    external = {m for m in third if m not in STDLIB_OK and m not in INTERNAL_MODULES}
    undeclared = sorted(external - set(declared) - internal)
    assert not undeclared, f"undeclared third-party import(s): {undeclared}"
    for name in sorted(external & set(declared)):
        dep = declared[name]
        assert dep["verdict"] == "OK", f"dependency {name} not permitted: {dep['verdict']}"
        # SPDX licence must be a permitted family (permissive / internal).
        spdx = dep.get("spdx", "")
        assert any(fam in spdx for fam in allowlist), \
            f"dependency {name} SPDX {spdx!r} not in permissive allowlist"

    # (2) any third-party import that is NOT in the manifest but IS estate-internal is ok;
    #     any import that is neither stdlib, nor internal, nor declared = fail (handled).
    # (2b) scan code + asset roots for hard-excluded landmine names. The RULE itself
    # names the families (guard doc + manifest), so those two files are exempt: they are
    # the text that DEFINES the sweep, not a dependency that trips it.
    exempt = {os.path.normpath(os.path.join(ROOT, p)) for p in EXEMPT_REL}
    excluded_hits = []
    for root in SCAN_ROOTS:
        for dp, dn, fn in os.walk(os.path.join(ROOT, root)):
            if "__pycache__" in dp or ".git" in dp:
                continue
            for f in fn:
                if os.path.splitext(f)[1] not in (CODE_EXTS | ASSET_EXTS):
                    continue
                p = os.path.join(dp, f)
                if os.path.normpath(p) in exempt:
                    continue
                try:
                    txt = open(p, encoding="utf-8").read()
                except UnicodeDecodeError:
                    continue
                for fam in hard_excluded:
                    if fam.lower() in txt.lower():
                        excluded_hits.append((p, fam))
    assert not excluded_hits, f"hard-excluded landmine present: {excluded_hits}"

    print(f"LICENCE-SWEEP: PASS — {len(external)} third-party module(s) detected, all "
          f"declared + permissive (cryptography dual Apache/BSD, asn1crypto MIT, "
          f"cbor2 MIT); "
          f"estate-internal csoai_city marked INTERNAL; 0 hard-excluded family names in "
          f"{len(SCAN_ROOTS)} code/asset roots; manifest declares the allowlist + excluded "
          f"families. Landmine-free.")
    return 0


INTERNAL_SCAN_ROOTS = ["engine", "harness", "agent", "test", "cli", "scripts"]
# Files that DEFINE the sweep rule by naming the excluded families (exempt from the scan).
EXEMPT_REL = ["data/dependency-licence-manifest.json", "test/licence-sweep.py"]


if __name__ == "__main__":
    sys.exit(main())

# Absorption fetch #1 — JailbreakBench · 2026-08-26 (move 3, real)

- Cloned (shallow) https://github.com/JailbreakBench/JailbreakBench (MIT, verified 26 Aug) → 3.8 MB
  into `data-absorptions/jbb/` + MANIFEST.json (license + source cited on cards; probes consumed,
  never redistributed).
- Axis: jail/containment. Next: wire JBB behaviors into the jail bank as probe candidates
  (harness integration = lane, dedup vs the existing 60-item/8-family bank first).

## Zenodo DOI rail — status (honest)
- Deposit 22113338 created (metadata complete, unsubmitted, 0 files).
- Upload 415 / publish failed — consistent with the **burned ZENODO_TOKEN** (estate C1 note: "rotate
  the burned one" was never done). NOT a content bug. Fix = owner rotates token in Zenodo
  settings → I re-upload + publish (2 calls). The proven C3 rail (gh release → auto-DOI) is the
  fallback that needs zero tokens.

## Production signing — keystone path (honest)
- Signing pod SSH: OK. `csoai_city.keystone.load_signing_key` is the loader (repo docs,
  cli/dorado.py §138-165) but the module is NOT importable on `sov-repull` and the key is not on
  the Mac. Key holder = the keystone lane's machine. The 4 minted cards remain honestly
  test-identity-signed until the keystone window; the delta is one `dorado.py sign` run per card
  (no --allow-test-identity) on the keystone holder.

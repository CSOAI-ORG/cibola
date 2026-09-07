# EAT OFFLOAD TO RUNPOD STORAGE — 2026-09-05
Disk hit ENOSPC (661Mi free / 97%). EAT offloaded the work to RunPod durable storage.

## Offloaded
- ~/Downloads (the mine, ~1.3G / 964 files) → build box `/workspace/jeeves/Users/nicholas/Downloads/`
  (tar-streamed; rsync dropped over the RunPod SSH proxy — tar-over-SSH is robust)
- ~/cibola work (docs/harness/engine/cli/connections/measurements) → `/workspace/jeeves/cibola/` (2.2M)
- Target: RunPod build box `sov-repull` (SSH port re-resolved 12473→20016 per the move-rule; /workspace 56G free)

## Reclaimed locally
- npm cache clean + `git gc` on clawd/.git + ~/.hermes → **661Mi → 2.7Gi free (97% → 86%)**

## Durable truth
- Committed work stays on GitHub (CSOAI-ORG/cibola = source of truth) — the box copy is a
  safety mirror; the Downloads mine is now duplicated on RunPod.

## Notes / next
- The sink (sov-volume-sink-cpu, 800GB network volume) is STOPPED — the durability floor is the
  box's /workspace for now; consider a durability-sync run when the sink is back.
- The Downloads local copy retained (user's active mine) — deletion is the user's call.

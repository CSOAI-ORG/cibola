# 3090 GPU Contention Rule — codified (2026-08-24) · Move 30

**Scope:** the `sov-brain-2` **3090** pod is the reliable measurement producer. It also
runs **RealPDE** training. When a measurement window and a training run share the GPU
concurrently, inference is contended and a measure can honestly report `measured=0/6`
(the harness never fakes a score — `RUNBOOK.md` already calls this out). This rule
codifies how to open a **clean measurement window** so a score is attributable to the
model, not to a contended/starved GPU.

## The rule (binding — applies on the pod before ANY `dorado-eat.sh` / `eat-batch.sh` window)

1. **GPU-flush preflight is mandatory before opening a measurement window.** Run
   `scripts/gpu-flush-preflight.sh` (and its `--doctor`) first. The GPU must be
   **flushed**: no foreign training/eval job saturating it. The preflight's `nvidia-smi`
   probe is the gate — if a foreign process (e.g. a RealPDE training step) is consuming
   the GPU, the window is **not opened** until it finishes or is paused/flushed.
2. **RealPDE training is niced BELOW measure_chain.** When a measurement window is
   authorised to coexist with training, training must run at a **lower priority** than
   the measurement loop (higher `nice` value, e.g. `nice -n 19` for the training process
   versus the measurement's default priority) so the measurement loop gets the GPU first.
   Never let a training run starve the measurement loop into a false `measured=0/6`.
3. **One cadence owner.** There is exactly one EAT cadence owner
   (`com.meok.eat-autopilot` / `com.meok.dorado-refresh`). Never start a second
   concurrent `dorado-eat.sh` / `eat-batch.sh`. The preflight's duplicate-daemon check
   refuses to open a second window if one is already running or a `/eat/.measure-lock`
   marker is present.
4. **Honest, never guessed.** A contended/starved measure is reported as-is
   (`measured=0/6`); it is **never** padded or re-run silently to manufacture a score.
   If the GPU is contended and cannot be flushed, the window is deferred, not faked.

## Why it sits here (not only in the RUNBOOK)

The RUNBOOK's doctrine covers *what* to check after a `measured=0/6`; this is the
*pre-condition* gate that avoids the contended state in the first place, and the guard is
hermetic (`--selftest`) so it can run in CI even though the GPU probe itself is pod-side.

## Operator checklist (pod-side, before a window)

```bash
cd /workspace/dorado
bash scripts/gpu-flush-preflight.sh          # full preflight incl. nvidia-smi probe
bash scripts/gpu-flush-preflight.sh --doctor  # CI-friendly: lock + dupe-daemon + honest GPU note
# if training must coexist:
ps -eo pid,ni,comm | grep -i <training>       # confirm its NICE is ABOVE (numerically higher than)
#                                             # the measurement process (i.e. lower priority)
```

**Guardians of honesty here:** a measurement card is only sealed when the axis results
are attributable to the model under load — never to a starved GPU dressed up as a score.

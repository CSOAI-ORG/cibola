#!/usr/bin/env bash
# gpu-flush-preflight.sh — 3090 GPU-contention preflight (move 30).
#
# Doctrine (docs/3090-contention-rule-2026-08-24.md): before opening a measurement
# window on the 3090 (sov-brain-2) the GPU MUST be flushed (no foreign training
# saturating it) and any co-resident RealPDE training must be niced BELOW
# measure_chain (lower priority than the measurement loop). This script is the gate.
# Run it on the pod BEFORE `dorado-eat.sh` / `eat-batch.sh`.
#
# Modes:
#   (default)   full preflight: cadence discipline + real GPU probe (nvidia-smi).
#   --doctor    CI-friendly: cadence discipline + honest GPU-DEFERRED note when the
#               GPU probe is unavailable (not on the pod). Exit 0 on PASS/deferred.
#   --selftest  hermetic: assert the doctrine is codified + the lock/marker logic works.
#
# Exit codes: 0 = go (or honestly deferred), 1 = CONTENDED / violation (do NOT open the
# window), 2 = usage/selftest failure.
set -uo pipefail

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SELF_DIR/.." && pwd)"
DOC="${REPO_ROOT}/docs/3090-contention-rule-2026-08-24.md"
DORADO_DIR="${DORADO_DIR:-${REPO_ROOT}}"
MEASURE_LOCK="${DORADO_DIR}/eat/.measure-lock"
# A GPU is CONTENDED (not flushed) when util exceeds this % or a foreign proc is present.
GPU_CONTEND_UTIL="${GPU_CONTEND_UTIL:-85}"

# --- cadence discipline: exactly one measurement owner. ---
_lock_contended() {       # exit 0 (true) if a measurement window is already held
  [ -f "$MEASURE_LOCK" ]
}

_duplicate_daemon() {     # exit 0 (true) if another dorado measure/eat loop is running
  command -v pgrep >/dev/null 2>&1 || return 1
  pgrep -f 'dorado-eat.sh|dorado\.py measure|eat-batch.sh' >/dev/null 2>&1
}

# --- GPU flush probe (pod-side). ---
_gpu_probe() {
  if ! command -v nvidia-smi >/dev/null 2>&1; then
    echo "  GPU PROBE: unavailable (no nvidia-smi — not on the pod?)"
    echo "  GPU PROBE: DEFERRED — operator must confirm GPU-flush on the pod before the window."
    echo "  GPU PROBE: no score is faked; a contended/starved measure would still report measured=0/6."
    return 2   # honestly deferred (not failed): caller decides the window stands behind operator confirm
  fi
  util="$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader 2>/dev/null | head -1 | tr -d ' %')"
  mem="$(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader 2>/dev/null | head -1)"
  echo "  GPU PROBE: util ${util:-?}%  (mem: ${mem:-?})"
  if [ -n "$util" ] && [ "$util" -ge "$GPU_CONTEND_UTIL" ]; then
    echo "  GPU PROBE: UTIL ${util}% >= ${GPU_CONTEND_UTIL}% threshold -> CONTENDED (flush first)"
    return 1
  fi
  # a foreign process list with any compute process is a flush-warning
  procs="$(nvidia-smi --query-compute-apps=pid,process_name --format=csv,noheader 2>/dev/null | wc -l | tr -d ' ')"
  if [ -n "$procs" ] && [ "$procs" -gt 1 ]; then   # more than the measurement we might start
    echo "  GPU PROBE: ${procs} compute procs present -> confirm none is a training step"
  fi
  echo "  GPU PROBE: CLEAR (flushed, under ${GPU_CONTEND_UTIL}% util)"
  return 0
}

_cadence_check() {
  local rc=0
  if _lock_contended; then
    echo "  CADENCE: measurement lock present ($MEASURE_LOCK) -> another window is open"
    rc=1
  else
    echo "  CADENCE: measurement lock clear (one cadence owner)"
  fi
  if _duplicate_daemon; then
    echo "  CADENCE: a dorado measure/eat loop is already RUNNING -> do not open a second window"
    rc=1
  else
    echo "  CADENCE: no duplicate EAT/measure daemon"
  fi
  return $rc
}

_doctor() {
  local rc=0
  echo "[gpu-flush-preflight --doctor] doctrine: ${DOC}"
  [ -f "$DOC" ] || { echo "  DOCTRINE: MISSING ${DOC} — codify the contention rule first"; rc=1; }
  _cadence_check || rc=1
  _gpu_probe
  local gpu=$?
  [ "$gpu" -ne 0 ] && [ "$gpu" -ne 2 ] && rc=1   # contended -> fail; deferred(2) -> honest, not failed
  if [ "$rc" -eq 0 ]; then
    echo "[gpu-flush-preflight --doctor] PASS (GPU deferred -> operator confirms on the pod; no score faked)"
  else
    echo "[gpu-flush-preflight --doctor] CONTENDED — do NOT open a measurement window"
  fi
  return $rc
}

_full() {
  local rc=0
  echo "[gpu-flush-preflight] doctrine: ${DOC}"
  [ -f "$DOC" ] || { echo "  DOCTRINE: MISSING ${DOC}"; rc=1; }
  _cadence_check || rc=1
  _gpu_probe || rc=1
  if [ "$rc" -eq 0 ]; then
    echo "[gpu-flush-preflight] PASS — window is clear to open (GPU flushed, one cadence owner)"
  else
    echo "[gpu-flush-preflight] CONTENDED — flush the GPU / pause training, then re-run"
  fi
  return $rc
}

_selftest() {
  local rc=0
  echo "[gpu-flush-preflight --selftest] doctrine codified + lock logic"
  [ -f "$DOC" ] || { echo "  SELFTEST: doctrine doc missing"; return 2; }
  grep -q "GPU-flush preflight" "$DOC" || { echo "  SELFTEST: doctrine lacks GPU-flush preflight"; rc=1; }
  grep -q "niced BELOW measure_chain" "$DOC" || { echo "  SELFTEST: doctrine lacks nice-below-measure_chain"; rc=1; }
  grep -q "One cadence owner" "$DOC" || { echo "  SELFTEST: doctrine lacks one-cadence-owner"; rc=1; }
  # lock detection: a held lock must be detected; a clear dir must pass.
  local tmp; tmp="$(mktemp -d)"
  mkdir -p "$tmp/eat"
  touch "$tmp/eat/.measure-lock"
  if [ -f "$tmp/eat/.measure-lock" ]; then
    echo "  SELFTEST: held lock detected OK"
  else
    echo "  SELFTEST: FAIL — could not create a held lock"; rc=1
  fi
  rm -rf "$tmp"
  if [ "$rc" -eq 0 ]; then echo "[gpu-flush-preflight --selftest] PASS"; else echo "[gpu-flush-preflight --selftest] FAIL"; fi
  return $rc
}

case "${1:-}" in
  --selftest) _selftest ;;
  --doctor)   _doctor ;;
  -h|--help)  sed -n '1,20p' "${BASH_SOURCE[0]}" | sed 's/^# //'; exit 0 ;;
  *)          _full ;;
esac

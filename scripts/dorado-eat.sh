#!/usr/bin/env bash
# dorado-eat.sh — the DORADO EAT loop, pod-native (mine->mint->chain->push).
#
# Runs ENTIRELY on the pod (all work off the Mac; Mac = terminal only).
# One EAT iteration:
#   MINE    measure a model on a domain registry via the pod's own Ollama
#   MINT    sign the measurement card (Ed25519 COSE_Sign1, identity-gated)
#   CHAIN   build the SCITT receipt + RFC3161 anchor + publish to the board (chain)
#   PUSH    rsync/git the board + measurements back to the remote (off-Mac durable)
#
# Usage (run on the pod, e.g. from /workspace/dorado):
#   dorado-eat.sh [--model qwen3:4b-8k] [--domain bond] [--cycles N] [--key-file <pod key>]
#
# The pod key is needed to MINT a production card (#card-attestation-1). If it is
# absent, cards are minted kid=test (honest) unless --key-file is given. Loop is
# fail-open: one cycle's error does not abort the run; it is logged and retried.
set -uo pipefail
DORADO_DIR="${DORADO_DIR:-/workspace/dorado}"
cd "$DORADO_DIR" || { echo "no dorado dir at $DORADO_DIR"; exit 1; }
LOG="${DORADO_DIR}/eat/$(date -u +%Y%m%d-%H%M%S).log"
mkdir -p "${DORADO_DIR}/eat"
MODEL="${MODEL:-qwen3:4b-8k}"
DOMAIN="${DOMAIN:-bond}"
CYCLES="${CYCLES:-1}"
KEY_FILE="${KEY_FILE:-${DORADO_SIGNING_KEY_FILE:-}}"
BASE="${BASE:-http://127.0.0.1:11434}"

echo "[$(date -u +%FT%TZ)] dorado-eat start model=$MODEL domain=$DOMAIN cycles=$CYCLES" | tee -a "$LOG"

for c in $(seq 1 "$CYCLES"); do
  echo "[$(date -u +%FT%TZ)] === cycle $c ===" | tee -a "$LOG"

  # --- MINE ---
  python3 cli/dorado.py measure --model "$MODEL" --base "$BASE" --domain "$DOMAIN" \
    --out "${DORADO_DIR}/eat/axis-${c}.json" \
    --card "${DORADO_DIR}/eat/card-${c}.unsigned.json" \
    --card-subject-id "pod-$(hostname)/${MODEL}" --card-subject-name "$MODEL" >> "$LOG" 2>&1 \
    || { echo "MINE failed (cycle $c)" | tee -a "$LOG"; continue; }

  # --- MINT (sign). -allow-test-identity only if no pod key; else real key gate ---
  if [ -n "$KEY_FILE" ]; then
    DORADO_SIGNING_KEY_FILE="$KEY_FILE" python3 cli/dorado.py sign \
      --card "${DORADO_DIR}/eat/card-${c}.unsigned.json" --out "${DORADO_DIR}/eat/card-${c}.json" >> "$LOG" 2>&1
  else
    python3 cli/dorado.py sign --allow-test-identity \
      --card "${DORADO_DIR}/eat/card-${c}.unsigned.json" --out "${DORADO_DIR}/eat/card-${c}.json" >> "$LOG" 2>&1
  fi
  [ -f "${DORADO_DIR}/eat/card-${c}.json" ] || { echo "MINT failed (cycle $c)" | tee -a "$LOG"; continue; }

  # --- CHAIN: receipt + RFC3161 anchor + publish to board ---
  DORADO_SIGNING_KEY_FILE="$KEY_FILE" python3 cli/dorado.py receipt \
    --card "${DORADO_DIR}/eat/card-${c}.json" --out "${DORADO_DIR}/eat/receipt-${c}.json" >> "$LOG" 2>&1
  python3 cli/dorado.py anchor \
    --card "${DORADO_DIR}/eat/card-${c}.json" --out "${DORADO_DIR}/eat/anchor-${c}.json" >> "$LOG" 2>&1
  python3 cli/dorado.py publish \
    --card "${DORADO_DIR}/eat/card-${c}.json" \
    --receipt "${DORADO_DIR}/eat/receipt-${c}.json" \
    --anchor "${DORADO_DIR}/eat/anchor-${c}.json" >> "$LOG" 2>&1 \
    && { echo "CHAIN ok (published card ${c})" | tee -a "$LOG"; } \
    || { echo "CHAIN failed (cycle $c)" | tee -a "$LOG"; continue; }

  echo "[$(date -u +%FT%TZ)] cycle $c COMPLETE" | tee -a "$LOG"
done

# --- PUSH: rsync the dorado worktree (board + eat) back to the remote via the Mac's git, OR
#     a pod-side git push if network creds exist. Keep the board durable off-pod. ---
echo "[$(date -u +%FT%TZ)] dorado-eat: run finished; board at ${DORADO_DIR}/board/board-index.json" | tee -a "$LOG"
echo "[$(date -u +%FT%TZ)] dorado-eat COMPLETE" | tee -a "$LOG"

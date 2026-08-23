#!/usr/bin/env bash
# eat-batch.sh — parallel EAT batch across domains x models, all on the pod.
# Each worker does a full MINE->MINT->CHAIN->PUBLISH cycle; bounded concurrency.
set -uo pipefail
cd /workspace/dorado
BATCH="${BATCH:-6}"
MODEL="${MODEL:-qwen3:4b-8k}"
DOMAINS="${DOMAINS:-bond bank insurance equity index cross-border}"
CONC="${CONC:-3}"
LOG="eat/batch-$(date -u +%Y%m%d-%H%M%S).log"
mkdir -p eat
echo "[$(date -u +%FT%TZ)] eat-batch start model=$MODEL domains=[$DOMAINS] conc=$CONC" >> "$LOG"

work_one() {
  local dom="$1" c="${MODEL//:/_}-${dom}"
  cd /workspace/dorado
  local LOG2="eat/${c}.log"
  {
    echo "[$(date -u +%FT%TZ)] === $dom ($MODEL) ==="
    python3 cli/dorado.py measure --model "$MODEL" --base http://127.0.0.1:11434 --domain "$dom" \
      --out eat/axis-${c}.json --card eat/card-${c}.unsigned.json \
      --card-subject-id "pod-3090/$MODEL" --card-subject-name "$MODEL" --delay 0.2
    python3 cli/dorado.py sign --allow-test-identity --card eat/card-${c}.unsigned.json --out eat/card-${c}.json
    python3 cli/dorado.py receipt --allow-test-identity --card eat/card-${c}.json --out eat/receipt-${c}.json
    python3 cli/dorado.py anchor --card eat/card-${c}.json --out eat/anchor-${c}.json
    python3 cli/dorado.py publish --card eat/card-${c}.json --receipt eat/receipt-${c}.json --anchor eat/anchor-${c}.json
    echo "[$(date -u +%FT%TZ)] === $dom COMPLETE ==="
  } >> "$LOG2" 2>&1
}

# launch up to CONC at a time
i=0
for dom in $DOMAINS; do
  work_one "$dom" &
  i=$((i+1))
  if [ $((i % CONC)) -eq 0 ]; then wait; fi
done
wait
echo "[$(date -u +%FT%TZ)] eat-batch COMPLETE" >> "$LOG"
python3 cli/dorado.py board >> "$LOG" 2>&1

#!/bin/bash
# dorado-batch-loop.sh — the always-on DORADO auto-batch (interval driver).
#
# Runs the full in-lane measurement batch on an interval and logs each cycle honestly.
# This is the CANONICAL scheduled-batch entry point: `dorado batch` (content-engine AEO index
# + RWA target-list + regulation-feeds SHA-256 change-detection + consolidated status), which
# regenerates every register + status.json with the complete binds block.
#
# It does NOT install itself into launchd (that is the Hermes lane's com.meok.* registry).
# Wire it via YOUR scheduler (e.g. a cron line, a LaunchAgent, or a cloud orchestrator) that
# invokes; the default is a self-contained loop with an interval so it works standalone.
#
# Safe: in-repo, no external send, no cost, no paid activation. Doctrine held: measurement,
# never certification. Owner-gated/external items are NOT run.
set -uo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
REPO="$HOME/cibola"
LOG="$HOME/cibola/data/batch-loop.log"
PY="/opt/homebrew/bin/python3"
INTERVAL="${BATCH_LOOP_INTERVAL:-900}"   # seconds; default 15 min (matches estate refresh cadence)
mkdir -p "$(dirname "$LOG")"

while true; do
  TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "[$TS] batch cycle start" >> "$LOG"
  # Run the batch; capture pass/fail honestly.
  if ( cd "$REPO" && "$PY" -m cli.dorado batch > /tmp/dorado-batch.out 2>>"$LOG" ); then
    echo "[$TS] batch cycle OK" >> "$LOG"
  else
    # Pull the last line of the batch verdict for an honest failure note.
    last="$(grep -v Deprecation /tmp/dorado-batch.out 2>/dev/null | tail -1)"
    echo "[$TS] batch cycle FAIL — $last" >> "$LOG"
  fi
  sleep "$INTERVAL"
done

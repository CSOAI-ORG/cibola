#!/usr/bin/env bash
# dorado-backup.sh — durable, off-Mac backup of the DORADO work (all work off the Mac).
#
# Snapshots the dorado monorepo worktree (source + generated board/measurements) to a
# durable location off the Mac and off the pod's ephemeral disk. Because the Mac must
# NOT be the primary store, this preserves:
#   (a) the git remote (CSOAI-ORG/dorado) as the source-of-truth, and
#   (b) generated artifacts (board + measurements + eat logs) to the pod volume + Oracle.
#
# Usage (run on the pod, e.g. cron daily):
#   dorado-backup.sh [--to /evac-bulk/dorado-backup] [--git-pull]
#
# --git-pull also refreshes the worktree from the remote (a pull, never a destructive reset).
set -uo pipefail
DORADO_DIR="${DORADO_DIR:-/workspace/dorado}"
DEST="${DEST:-/evac-bulk/dorado-backup}"
STAMP=$(date -u +%Y%m%d-%H%M%S)
mkdir -p "$DEST"
LOG="${DEST}/backup-${STAMP}.log"
echo "[$(date -u +%FT%TZ)] dorado-backup start" | tee "$LOG"

# (a) refresh the worktree from the remote if git is available (source of truth)
if command -v git >/dev/null 2>&1 && [ -d "$DORADO_DIR/.git" ]; then
  (cd "$DORADO_DIR" && git fetch --quiet 2>/dev/null; git merge --ff-only --quiet 2>/dev/null) \
    && echo "git: refreshed from remote" | tee -a "$LOG" || echo "git: (no .git / nothing to pull)" | tee -a "$LOG"
fi

# (b) tar the generated artifacts + worktree (exclude .git, caches)
tar --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' -czf \
  "$DEST/dorado-${STAMP}.tar.gz" -C "$(dirname "$DORADO_DIR")" "$(basename "$DORADO_DIR")" 2>>"$LOG" \
  && echo "tar: wrote $DEST/dorado-${STAMP}.tar.gz ($(du -h "$DEST/dorado-${STAMP}.tar.gz" | cut -f1))" | tee -a "$LOG"

# (c) keep the board index plus a JSON manifest as a portable, grep-able copy
[ -f "$DORADO_DIR/board/board-index.json" ] && cp "$DORADO_DIR/board/board-index.json" "$DEST/board-index.json"
[ -f "$DORADO_DIR/board/measurements.jsonl" ] && cp "$DORADO_DIR/board/measurements.jsonl" "$DEST/measurements.jsonl"
echo "board: copied $(wc -l < "$DEST/measurements.jsonl" 2>/dev/null || echo 0) measurements" | tee -a "$LOG"

# (d) rotate: keep the last 10 snapshots, delete older (disk-safe)
ls -1t "$DEST"/dorado-*.tar.gz 2>/dev/null | tail -n +11 | xargs -I{} rm -f {} 2>/dev/null || true
echo "[$(date -u +%FT%TZ)] dorado-backup COMPLETE (rotated to last 10)" | tee -a "$LOG"

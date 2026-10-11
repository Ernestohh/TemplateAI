#!/usr/bin/env bash
# Stop guard. Active only during an autonomous run (marker .claude/AUTONOMOUS_RUN, created by
# scripts/autodrive.sh or by Docs/KICKOFF.md message 1). The owner ends the run by creating .claude/ALLOW_STOP.
root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
[ -f "$root/.claude/AUTONOMOUS_RUN" ] || exit 0
[ -f "$root/.claude/ALLOW_STOP" ] && exit 0

ad="$root/.claude/autodrive"
# Autodrive (scripts/autodrive.sh, the run mode from day 1): every chunk is a fresh `claude -p` session
# with {{AUTODRIVE_ENV}}=1. A chunk may stop once it wrote its hand-off and CHUNK_DONE, or after
# CHUNK_MAX_MIN minutes, so one chunk can never run forever. The driver then starts the next fresh chunk.
if [ -n "${{{AUTODRIVE_ENV}}:-}" ]; then
  [ -f "$ad/CHUNK_DONE" ] && exit 0
  max_min="${CHUNK_MAX_MIN:-150}"
  if [ -f "$ad/CHUNK_START" ]; then
    start=$(cat "$ad/CHUNK_START" 2>/dev/null || echo 0)
    now=$(date +%s)
    [ $(( (now - start) / 60 )) -ge "$max_min" ] && exit 0
  fi
  cat <<JSON
{"decision":"block","reason":"Autodrive chunk not finished. Continue the current milestone-sized chunk (Docs/TODO.md). When a coherent unit is committed and no agent you started is still running: append a HANDOFF entry to Docs/DEVLOG.md (done / open / next step), commit it with scripts/commit_green.sh, then create .claude/autodrive/CHUNK_DONE and end your turn."}
JSON
  exit 0
fi

# While the driver owns the run, an interactive session may stop (only one session should work on the repo).
[ -f "$ad/ACTIVE" ] && exit 0

cat <<JSON
{"decision":"block","reason":"Do not stop. Take the next item from Docs/TODO.md. If TODO.md is empty, run the acceptance test (Docs/TASK.md section 2) or a fresh-context playtest of the weakest area, queue its findings and continue. Only the owner ends the run (by creating .claude/ALLOW_STOP)."}
JSON

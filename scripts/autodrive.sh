#!/usr/bin/env bash
# Autodrive: run the autonomous {{GAME_NAME}} build as a chain of fresh `claude -p` sessions (one milestone-sized
# chunk each), so the context, and with it the per-turn cache reads, never grows across milestones.
# State lives in Docs/ (PLAN, TODO, DEVLOG HANDOFF). This is the run mode from day 1 (CLAUDE.md section 1b).
#
# Start (Git Bash):   bash scripts/autodrive.sh
# Stop:               create .claude/ALLOW_STOP (the current chunk finishes first)
# Optional env:       {{MODEL_ENV}}=<model>   passed as --model to every chunk
#                     CHUNK_MAX_MIN=<min>    hard limit per chunk honoured by the stop guard (default 150)
# Live output: one short line per action (scripts/autodrive_stream.py). Display only: same tokens.
# Plain-ASCII output only (the Windows console is cp1252).
set -u
cd "$(dirname "$0")/.."
ad=.claude/autodrive
mkdir -p "$ad"
if [ -f .claude/ALLOW_STOP ]; then
  echo "autodrive: .claude/ALLOW_STOP exists - remove it to start the run. Not starting."
  exit 1
fi
log=Docs/AUTODRIVE_LOG.md
[ -f "$log" ] || printf '# Autodrive log\n\nOne row per chunk (fresh session). Tokens and cost come from the `claude -p` result event.\n\n| # | Start (UTC) | Minutes | Exit | Turns | Cost USD | Result |\n|---|---|---|---|---|---|---|\n' > "$log"
# Launching the driver is the owner starting the run: switch on the guards (CLAUDE.md section 1b).
if [ ! -f .claude/AUTONOMOUS_RUN ]; then
  date -u +%FT%TZ > .claude/AUTONOMOUS_RUN
  echo "autodrive: created .claude/AUTONOMOUS_RUN (run started)"
fi
date -u +%FT%TZ > "$ad/ACTIVE"
trap 'rm -f "$ad/ACTIVE"' EXIT
model_args=()
[ -n "${{{MODEL_ENV}}:-}" ] && model_args=(--model "${{MODEL_ENV}}")
fails=0
n=$(grep -cE '^\| [0-9]+ \|' "$log" || true)
while [ ! -f .claude/ALLOW_STOP ]; do
  n=$((n + 1))
  rm -f "$ad/CHUNK_DONE"
  date +%s > "$ad/CHUNK_START"
  started=$(date -u +'%F %H:%M')
  t0=$(date +%s)
  echo "== chunk $n started $started UTC (live: one line per action) =="
  {{AUTODRIVE_ENV}}=1 claude -p "$(cat scripts/autodrive-prompt.md)" ${model_args[@]+"${model_args[@]}"} \
    --permission-mode auto --output-format stream-json --verbose 2> "$ad/chunk-$n.err" \
    | python -I -u scripts/autodrive_stream.py "$ad/chunk-$n.jsonl" "$ad/chunk-$n.json"
  code=${PIPESTATUS[0]}
  mins=$(( ($(date +%s) - t0) / 60 ))
  summary=$(python -I -c "
import json,sys
try:
    d=json.load(open(sys.argv[1],encoding='utf8'))
    r=(d.get('result') or '').strip().splitlines()
    print('{}|{:.2f}|{}'.format(d.get('num_turns','?'), float(d.get('total_cost_usd') or 0), (r[-1] if r else '')[:120].replace('|','/')))
except Exception as e:
    print('?|?|no json: '+str(e)[:60])
" "$ad/chunk-$n.json")
  IFS='|' read -r turns cost result <<< "$summary"
  echo "| $n | $started | $mins | $code | $turns | $cost | $result |" >> "$log"
  # Owner-approved 2026-10-11: after each finished chunk, the DRIVER (not the agent) publishes that chunk's commits.
  # Plain fast-forward of master to origin, never forced; no prompts (a credential problem fails fast and is logged).
  if git remote get-url origin >/dev/null 2>&1; then
    if GIT_TERMINAL_PROMPT=0 timeout 180 git push origin master >> "$ad/push.log" 2>&1; then
      echo "autodrive: pushed to origin/master ($(git rev-parse --short HEAD))"
    else
      echo "autodrive: push failed, continuing (see $ad/push.log)"
      echo "| push | $(date -u +'%F %H:%M') | push failed after chunk $n, see $ad/push.log |" >> "$log"
    fi
  fi
  if [ "$code" -ne 0 ] || [ "$mins" -lt 2 ]; then fails=$((fails + 1)); else fails=0; fi
  if [ "$fails" -ge 3 ]; then echo "autodrive: 3 failed chunks in a row, stopping (see $ad/chunk-$n.err)" | tee -a "$log"; break; fi
  sleep 15
done
echo "autodrive: stopped $(date -u +%FT%TZ)"

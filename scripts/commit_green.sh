#!/usr/bin/env bash
# Commit only when the gate is green (CLAUDE.md section 5).
#   bash scripts/commit_green.sh "message" [tag]
# Before package.json exists (early M0) it runs the lightweight checks only and says which ones it skipped.
# Once package.json has a "check" script, it runs the full `npm run check` (typecheck, lint, validate-data,
# test, harness, build, e2e). In between, it runs whichever of those npm scripts already exist.
# A trailer "Co-Authored-By: Claude ..." is appended unless the message already has one.
set -u
cd "$(dirname "$0")/.."
msg="${1:?message required}"; tag="${2:-}"
logf="${TMPDIR:-/tmp}/{{GAME_SLUG}}-check.log"
: > "$logf"
red() { echo "GATE RED ($1) - not committing. Tail of $logf:"; tail -40 "$logf"; exit 1; }

# 1. Lightweight checks (always): shell syntax, Python syntax, JSON validity, asset manifests.
for f in scripts/*.sh .claude/hooks/*.sh; do
  [ -f "$f" ] || continue
  bash -n "$f" >> "$logf" 2>&1 || red "bash -n $f"
done
py_files=$(ls scripts/*.py scripts/*/*.py .claude/hooks/*.py 2>/dev/null)
if [ -n "$py_files" ]; then
  python -I -c "
import sys, ast
for p in sys.argv[1:]:
    ast.parse(open(p, encoding='utf8').read(), p)
" $py_files >> "$logf" 2>&1 || red "python syntax"
fi
json_files=$(ls .claude/settings.json .mcp.json Docs/*.json data/*.json 2>/dev/null)
if [ -n "$json_files" ]; then
  python -I -c "
import sys, json
for p in sys.argv[1:]:
    json.load(open(p, encoding='utf8'))
" $json_files >> "$logf" 2>&1 || red "invalid JSON"
fi
if [ -d assets/generated ] && find assets/generated -name asset.json | grep -q .; then
  python -I scripts/assets/validate_asset.py assets/generated >> "$logf" 2>&1 || red "asset manifests"
fi

# 2. Project checks, as far as they exist yet.
if [ ! -f package.json ]; then
  echo "note: no package.json yet - skipped typecheck, lint, validate-data, test, harness, build, e2e"
elif [ ! -d node_modules ]; then
  red "package.json exists but node_modules is missing: run npm install (or npm ci)"
elif node -e "process.exit(require('./package.json').scripts?.check ? 0 : 1)" 2>/dev/null; then
  npm run check >> "$logf" 2>&1 || red "npm run check"
else
  ran=""; skipped=""
  for s in typecheck lint validate-data test build; do
    if node -e "process.exit(require('./package.json').scripts?.['$s'] ? 0 : 1)" 2>/dev/null; then
      npm run "$s" >> "$logf" 2>&1 || red "npm run $s"
      ran="$ran $s"
    else
      skipped="$skipped $s"
    fi
  done
  echo "note: no 'check' script yet - ran:${ran:- none}; skipped:${skipped:- none}"
fi

# 3. Commit.
case "$msg" in
  *Co-Authored-By:*) full="$msg" ;;
  *) full="$msg

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" ;;
esac
git add -A
if git diff --cached --quiet; then echo "nothing to commit"; exit 0; fi
git commit -q -m "$full" || { echo "git commit failed"; exit 1; }
[ -n "$tag" ] && git tag -f "$tag" >/dev/null && echo "tagged $tag"
git log --oneline -1

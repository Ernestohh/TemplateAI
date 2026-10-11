#!/usr/bin/env bash
# Quick sanity before a milestone gate: required docs exist, no unfilled placeholders, manifests valid,
# {{GAME_NAME}} ports configured. The full gate is .claude/commands/gate.md.
set -u
cd "$(dirname "$0")/.."
fail=0
for f in CLAUDE.md Docs/TASK.md Docs/PLAN.md Docs/TODO.md Docs/DEVLOG.md Docs/STYLE_BIBLE.md Docs/STATS.json Docs/DECISIONS.md Docs/LICENSES.md; do
  [ -f "$f" ] || { echo "missing $f"; fail=1; }
done
# Template placeholders (double-brace names and FILL skeleton markers) must all be filled (SETUP.md).
if grep -rn --exclude=fill_template.py '{{[A-Z]' CLAUDE.md Docs/*.md scripts .claude 2>/dev/null | head -5 | grep -q .; then
  echo "unfilled template placeholders:"; grep -rn --exclude=fill_template.py '{{[A-Z]' CLAUDE.md Docs/*.md scripts .claude | head -5; fail=1
fi
if [ -f vite.config.ts ] && ! grep -q '{{DEV_PORT}}' vite.config.ts; then echo "vite.config.ts: dev port must be {{DEV_PORT}} (strictPort)"; fail=1; fi
for c in playwright*.config.ts; do
  [ -f "$c" ] || continue
  grep -q '{{PREVIEW_PORT}}' "$c" || { echo "$c does not use {{GAME_NAME}}'s preview port {{PREVIEW_PORT}} (PORTS.md)"; fail=1; }
done
if [ -d assets/generated ] && find assets/generated -name asset.json | grep -q .; then
  python -I scripts/assets/validate_asset.py assets/generated || fail=1
fi
[ -f .claude/ALLOW_STOP ] && echo "note: ALLOW_STOP present"
exit $fail

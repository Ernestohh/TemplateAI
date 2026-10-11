---
name: git-checkpoint
description: Use to commit progress safely - at least every 30-60 minutes, at every milestone gate, before risky changes, and at the end of every autodrive chunk.
---
# Git checkpoint

`bash scripts/commit_green.sh "<what changed>" [tag]` runs the gate as far as it exists, stages everything not ignored, commits and optionally tags (`m0`..`{{MVP_TAG}}`, `mvp`):
- before `package.json` exists: the lightweight checks;
- once the `check` script exists: the full `npm run check`.

It prints `GATE RED` and does not commit when a check fails.

Rules:
- Never use a plain `git commit` chained after a separate step.
- Never force-push, rewrite history (amend, rebase, reset --hard) or delete authored sources or rejected attempts.
- No pushes and no remote changes from an agent: the autodrive driver pushes master after each chunk (CLAUDE.md section 9).
- Before a risky refactor, checkpoint first so that `git revert` is clean.
- Large binaries: keep videos under `Docs/recording/` (trailers only, ≤ 40 MB each). Note exceptions in DECISIONS.md.

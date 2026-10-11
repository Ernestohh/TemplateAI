#!/usr/bin/env bash
# After start, resume or context compaction: send the agent back to its plan, to-do list and log.
# Stdout of a SessionStart hook is added to the agent's context.
cat <<'MSG'
Context was reset or compacted. Before anything else, in this order:
1. Re-read CLAUDE.md (autodrive 1b, token discipline 1c, shared machine 5b).
2. Read Docs/PLAN.md (current milestone) and Docs/TODO.md (queue).
3. Read the last three entries of Docs/DEVLOG.md (the newest HANDOFF says where to continue) and Docs/STATS.json.
4. Read Docs/STYLE_BIBLE.md before any art or UI work.
5. Run `date -u`, check `git status`, then continue with the next TODO item. Do not ask the owner anything.
MSG

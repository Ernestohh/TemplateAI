---
name: context-recovery
description: Use after any context compaction, crash, restart or at the start of an autodrive chunk to rebuild working state from files.
---
# Context recovery

1. Read these, in order:
   - CLAUDE.md;
   - Docs/PLAN.md and Docs/TODO.md;
   - the last three DEVLOG entries (the newest HANDOFF names the next step);
   - Docs/STATS.json;
   - Docs/STYLE_BIBLE.md, if the item is visual.
2. Run `date -u`, `git status` and `git log --oneline -10`. Find any uncommitted work and decide whether to finish it or revert it.
3. Check whether `.claude/autodrive/ACTIVE` exists. If you are an interactive session and it does, do not start work.
4. Smoke-test each tool the current item needs, with a cheap call. Use the preview on port {{PREVIEW_PORT}}, never another project's ports (PORTS.md).
5. Check the memory MCP (`Docs/.memory.json`) for stored facts.
6. Append a DEVLOG entry "recovered at <time>, resuming <item>" (an autodrive chunk start needs no entry), then continue. Do not ask the owner anything.

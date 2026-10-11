# DEVLOG.md

Append-only. Each entry starts with `### YYYY-MM-DD HH:MM UTC — <milestone> — <title>` (time from `date -u`). Write an entry at every milestone, every recovered failure, every chunk end (`HANDOFF`: done / open / exact next step), and at least hourly. `scripts/build_progress.py` reads these headings for the /progress timeline.

### {{SETUP_DATE}} UTC — setup — HANDOFF
- **State:** the scaffolding is in place (created from the web-game template):
  - CLAUDE.md, Docs/TASK.md, PLAN, TODO, STYLE_BIBLE draft, MODEL_ROUTING;
  - hooks, agents, skills, commands;
  - autodrive and the site/deploy scripts.
  - There is no game code yet.
- **Open:** everything in Docs/TODO.md M0.
- **Next step for chunk 1:** start M0.
  - Follow Docs/KICKOFF.md message 1 (the driver has already created .claude/AUTONOMOUS_RUN).
  - Read Docs/TASK.md completely.
  - Then work Docs/TODO.md from T1.
  - Ports {{DEV_PORT}}/{{PREVIEW_PORT}} only (PORTS.md; other runs may share this PC).

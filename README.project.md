# {{GAME_NAME}}

{{ONE_PARAGRAPH_PITCH}}

This repository is built autonomously by Claude. The project files:
- `CLAUDE.md`: the working rules.
- `Docs/TASK.md`: the specification.
- `Docs/PLAN.md`: the milestones.
- `https://{{DOMAIN}}/progress/`: the build story in plain language.

## Run the build (owner)

- **Start the autonomous run** (Git Bash): `bash scripts/autodrive.sh`. From PowerShell: `& "C:\Program Files\Git\bin\bash.exe" -lc "cd {{PROJECT_DIR_POSIX}} && bash scripts/autodrive.sh"`.
- **Stop:** create `.claude/ALLOW_STOP` (the current chunk finishes first). Delete it before the next start.
- **GitHub:** the driver pushes `master` to {{GITHUB_REMOTE}} after every chunk.
- **Play locally** (once the game exists): `npm install && npm run dev` (port {{DEV_PORT}}) or `npm run build && npm run preview` (port {{PREVIEW_PORT}}).
- **Hosting:** see `deploy/README.md` ({{DOMAIN}}).

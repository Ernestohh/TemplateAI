# KICKOFF.md — messages that start and steer the run

{{GAME_NAME}} runs in **autodrive** from day 1 (CLAUDE.md §1b). The normal start is the driver:

```
bash scripts/autodrive.sh
```

From Windows PowerShell 5 (it has no `&&`):

```
& "C:\Program Files\Git\bin\bash.exe" -lc "cd {{PROJECT_DIR_POSIX}} && bash scripts/autodrive.sh"
```

How the driver starts the run:
1. The driver creates `.claude/AUTONOMOUS_RUN` and `.claude/autodrive/ACTIVE`.
2. It starts chunk 1 with `scripts/autodrive-prompt.md`.
3. Chunk 1 sees the HANDOFF "start M0" in `Docs/DEVLOG.md` and follows message 1 below.
4. After every chunk the driver pushes `master` to `origin` ({{GITHUB_REMOTE}}).

To stop: create `.claude/ALLOW_STOP`; the current chunk finishes first.

The other messages are for an owner at an interactive session. Use them only while the driver is **not** running (no `.claude/autodrive/ACTIVE`).

## 1. Kickoff (the first chunk follows this; or paste it into an interactive session)

```
First action: make sure the file .claude/AUTONOMOUS_RUN exists (create it if not; the autodrive driver already creates it). It switches on the stop and git guards for this run.

Build {{GAME_NAME}}: the full task is in Docs/TASK.md, the working rules are in CLAUDE.md. Read both completely before your first action, then Docs/PLAN.md, Docs/TODO.md, Docs/STYLE_BIBLE.md, Docs/MODEL_ROUTING.md and Docs/PIPELINE_LESSONS.md, and open every image in Docs/concepts/approved/ and Docs/refs/ (if any).

This folder is a git repository with the autonomous-build scaffolding only (rules, task, plan, hooks, agents, skills, scripts); there is no game code yet.
Tools: Playwright MCP, Context7, memory, filesystem, sequential-thinking, Node 20+, npm, Python 3, ffmpeg, Git Bash, ssh access to the owner's server for deploys. Paid generation budget: {{BUDGET_USD}} USD (CLAUDE.md section 6).
Other runs may work on the same PC: use only ports {{DEV_PORT}} (dev) and {{PREVIEW_PORT}} (preview) and never touch another project (CLAUDE.md 5b, PORTS.md).

Start with milestone M0 (Docs/PLAN.md, Docs/TODO.md). Document the process with progress captures from the first visible screen (TASK.md section 19). Work autonomously and do not ask me anything. In autodrive, end the chunk with a HANDOFF entry, a commit and .claude/autodrive/CHUNK_DONE.
```

## 2. Resume (an interactive session after a crash or restart, driver not running)

```
Resume {{GAME_NAME}}. Re-read CLAUDE.md, Docs/PLAN.md, Docs/TODO.md, the last three entries of Docs/DEVLOG.md (the newest HANDOFF says where to continue) and Docs/STATS.json. Check git status for uncommitted work, check that every tool still responds, then continue with the next item. Do not ask me anything. Better: restart the driver with bash scripts/autodrive.sh.
```

## 3. Status request (the owner is watching)

```
Status check, no need to stop working. In one short message: current milestone, what was finished since the last DEVLOG entry, what you are doing now, the three biggest risks, Claude cost so far (Docs/AUTODRIVE_LOG.md). Then continue.
```

During autodrive, read `Docs/AUTODRIVE_LOG.md`, the last HANDOFF in `Docs/DEVLOG.md`, or `https://{{DOMAIN}}/progress/` instead. The live driver window shows one line per action.

## 4. Wrap-up (the owner wants to end)

Create `.claude/ALLOW_STOP` to stop the driver after the current chunk. Then, in an interactive session:

```
Wrap up. Finish the item in progress or revert it so the product is in a working state, run npm run check and the acceptance test, update Docs/REPORT.md, Docs/STATS.json and Docs/LICENSES.md, compile timelapses (python scripts/capture/make_timelapse.py --all --master), run python -I scripts/token_usage.py, commit with scripts/commit_green.sh and tag. Then write the final summary into Docs/REPORT.md.
```

The driver is stopped then, so push the final commits yourself from a terminal: `git push origin master`.

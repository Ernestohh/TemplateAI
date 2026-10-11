You are one chunk of the autonomous {{GAME_NAME}} run, started by scripts/autodrive.sh in a fresh session (autodrive is the run mode from day 1, CLAUDE.md section 1b). Your context starts empty on purpose: everything you need is in the project files.

1. Follow CLAUDE.md section 1: read CLAUDE.md, Docs/PLAN.md, Docs/TODO.md, the last three Docs/DEVLOG.md entries (the newest HANDOFF entry says exactly where to continue), Docs/STATS.json, and run `date -u`.
   - If the newest HANDOFF says "start M0" (nothing has been built yet), this is the first chunk: follow Docs/KICKOFF.md message 1 (the driver already created .claude/AUTONOMOUS_RUN), read Docs/TASK.md completely, and start M0.
2. Do ONE milestone-sized chunk: the next TODO item(s) up to one coherent, committed unit, within about 60-120 minutes. If TODO.md has no open items, run the acceptance test (Docs/TASK.md section 2), or start a fresh-context review/playtest of the weakest area and queue its findings, as CLAUDE.md section 2 says.
2b. Tutorial (CLAUDE.md 3c, Docs/TUTORIAL.md): any mechanic or feature you add or change must add or update its tutorial entry in the same commit.
3. Follow the token discipline rules in CLAUDE.md section 1c: no poll loops, batch tool calls, let agents read long files and return short summaries, open few images, read result files instead of transcripts.
3b. Playtests and reviews always run in a fresh reviewer/playtester agent: never play-test your own chunk's work in this session. Their scratch scripts and screenshots go to a temp folder outside the repo (for example `$TMPDIR` or the agent scratchpad), never under `Docs/`. Only the review file and at most 6 key screenshots are copied into `Docs/reviews/`. (Lesson from an earlier autodrive run.)
4. Wait for every agent you start before you finish. Background agents do not survive the end of this session.
5. {{GAME_NAME}} shares the machine with other autonomous runs (PORTS.md): use only ports {{DEV_PORT}} (dev) and {{PREVIEW_PORT}} (preview), never touch another project's processes or folder, and re-measure performance solo before calling a drop a regression (CLAUDE.md section 5b).
6. Commit only through `bash scripts/commit_green.sh "<message>"`. Never push: the driver pushes master to the remote after this chunk ends. At a milestone gate: run the gate checklist (.claude/commands/gate.md), including the acceptance test (from {{ACCEPTANCE_FROM}}), the 390 px check, a fresh-context playtest and a trailer; if it is green, deploy with `DEPLOY_SSH={{SERVER_SSH}} bash scripts/deploy_server.sh` and verify that the live bundle matches dist/.
7. Finish the chunk:
   - Append a `### <date -u> UTC — <milestone> — HANDOFF` entry to Docs/DEVLOG.md with what you did, what is open, and the exact next step.
   - Commit it.
   - Create the file `.claude/autodrive/CHUNK_DONE`, then end your turn.

The next chunk starts automatically with a fresh context. Never ask the owner anything (CLAUDE.md section 2).

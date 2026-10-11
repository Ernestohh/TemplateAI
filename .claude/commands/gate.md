---
description: Run the milestone gate checklist
---
Run the gate for the current milestone (Docs/PLAN.md, TASK.md section 17):
1. Run `bash scripts/check_gate.sh`, then make the verification path (TASK.md section 18) green: `npm run check`, and from {{ACCEPTANCE_FROM}} on `npm run acceptance` (through the qa-driver agent).
2. Confirm zero console errors and zero missing references, and check the 390x844 phone path.
3. Measure performance on the target scenario (TASK.md section 15). Measure solo if another run on this PC is busy (CLAUDE.md 5b, PORTS.md).
4. Capture every fixed state at both viewports. Then run the `reviewer` agent and the `playtester` agent in parallel; use the large model at {{LARGE_GATES}}. Fix their top defects before new features, and queue the rest at the top of TODO.md.
5. Cut the trailer (`npx playwright test -c playwright.trailer.config.ts`, then `python scripts/make_trailer.py`) and run `python scripts/capture/make_timelapse.py --all`.
6. Update PLAN.md (status), DEVLOG.md, STATS.json and REPORT.md, and run `python -I scripts/token_usage.py`. Add this milestone's card to `Docs/progress_story.md` in plain language, following the writing rules at the top of that file. That file is what the owner reads on /progress.
7. Commit with `bash scripts/commit_green.sh "gate: <milestone>" <tag>`. Deploy with `DEPLOY_SSH={{SERVER_SSH}} bash scripts/deploy_server.sh` and check the live bundle name.

Tutorial check (CLAUDE.md 3c):
- The tutorial coverage test is green.
- Every mechanic added since the last gate has a How-to-play entry.
- The playtester completed the guided tutorial from a new game and reported any step that confused them. Fix those before new features.

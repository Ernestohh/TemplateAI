---
name: fresh-playtest
description: Use at every milestone gate (and when TODO is empty) to have a fresh-context agent play the running build cold on desktop and phone, score it and name the weakest area. Run it in the playtester sub-agent, never self-grade.
---
# Fresh playtest

**Setup (Integrator):**
- Start the production preview (`npm run build && npm run preview`, port {{PREVIEW_PORT}}) in the background.
- Spawn the `playtester` agent with the URL, the milestone, and the list of features the build should have (from PLAN.md). Do not explain how to play: the cold read is the point.
- Only one agent drives the Playwright MCP browser at a time.

**The playtester:**
1. Plays at 1440x900 with mouse and keyboard for about 10–15 minutes of game, or until the run ends.
2. Then plays at 390x844 with touch emulation for at least the first core-loop cycle (TASK.md section 1, steps 1-4).
3. Notes every moment of confusion, with a screenshot (at most 12 in total) in `Docs/reviews/playtest-shots/<ts>/`.
4. Scores each area 1–10: {{PLAYTEST_AREAS}}. Areas not in the build yet are "n/a".
5. Names the weakest area and the three changes that would raise it most.
6. Writes `Docs/reviews/<UTC yyyymmdd-HHMM>-playtest-<milestone>.md`:
   - a `| area | score | why |` table, with the score as a bare number so `scripts/build_progress.py` can chart it;
   - the weakest area;
   - the confusion log.

**Afterwards (Integrator):** the weakest area's fixes go to the top of `Docs/TODO.md`. Log the scores in `Docs/DEVLOG.md` and `Docs/STATS.json` (`playtests`).

# DECISIONS.md

One line per decision: `YYYY-MM-DD HH:MM - <decision>. Why: <reason>.` (time from `date -u`). Correct a wrong claim with a new dated line; never silently edit an old one. Continuation lines start with two spaces.

{{SETUP_DATE}} - Scaffolding created from the web-game template (C:\Users\ernes\GameDev\template, based on the Zephyr run: rules, gates, lanes, token discipline, autodrive with driver push, hooks, agents, skills, scripts). Why: owner request; reuse what worked.
{{SETUP_DATE}} - Ports: vite dev {{DEV_PORT}}, preview {{PREVIEW_PORT}}, strictPort (PORTS.md). Why: other runs use their own ports on the same PC at the same time.
{{SETUP_DATE}} - Autodrive is the run mode from day 1; the driver creates .claude/AUTONOMOUS_RUN when the owner starts it and pushes master to {{GITHUB_REMOTE}} after each chunk. Why: owner decision (token optimisation; the owner sees progress on GitHub).
{{SETUP_DATE}} - Asset budget {{BUDGET_USD}} USD (CLAUDE.md section 6, TASK.md section 16). Why: owner answer in the setup questionnaire.
{{FILL: DECISIONS setup answers}}
<!-- One line per working design choice taken from the questionnaire that the run may refine: genre and core loop,
     setting, signature mechanics, MVP slice, fonts (with licence checked on npm), device priority, run mode, references.
     Zephyr example: "2026-10-10 22:55 - Working design choices in TASK.md that the run may refine (log changes here):
     Act 1 boss 'Leshy, Tsar of the Deep Wood'; hub = Baba Yaga's hut; meta currency = firebird feathers; MVP heroes
     Bogatyr, Volkhv, Rusalka, Domovoi. Why: the owner fixed the mechanics, not these details; these make the spec testable." -->

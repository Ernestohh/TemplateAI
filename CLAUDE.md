# CLAUDE.md — {{GAME_NAME}}

You are building {{GAME_NAME}} autonomously over a long run. {{GAME_NAME}} is a {{GENRE}} for the web browser, {{SETTING_SHORT}}. The full task is `Docs/TASK.md`. These rules apply for the whole run and outrank anything you infer later.

TASK.md is the WHAT. This file is the HOW.

Language: English for everything: code, comments, docs, logs, commit messages, in-game text and every prompt you write for an agent.

## 1. After every start, restart or context compaction

Read, in this order, before doing anything else:
1. this file;
2. `Docs/PLAN.md` (milestones, current milestone) and `Docs/TODO.md` (prioritised queue);
3. the last three entries of `Docs/DEVLOG.md` (the newest `HANDOFF` entry says where to continue) and `Docs/STATS.json`;
4. `Docs/STYLE_BIBLE.md` and the images in `Docs/concepts/approved/` before any art or UI work;
5. run `date -u` to know the current time.

Context will be compacted many times, and every autodrive chunk starts empty. Anything that matters must be written to these files as soon as it is decided. If it is not in a file, assume you will forget it.

## 1b. Autodrive (the run mode from day 1)

- The run is a chain of fresh `claude -p` sessions started by `bash scripts/autodrive.sh` (prompt: `scripts/autodrive-prompt.md`). Each chunk runs with `{{AUTODRIVE_ENV}}=1`, does one milestone-sized unit, writes a `HANDOFF` entry in `Docs/DEVLOG.md`, commits, creates `.claude/autodrive/CHUNK_DONE` and ends. The next chunk starts with an empty context and resumes from the files.
- The driver creates `.claude/AUTONOMOUS_RUN` when it starts (the owner launching the driver starts the run) and `.claude/autodrive/ACTIVE` while it runs. Chunks are logged in `Docs/AUTODRIVE_LOG.md` (turns, cost, result).
- After each chunk the driver (not the agent) pushes `master` to `origin` ({{GITHUB_REMOTE}}): fast-forward only, never forced, no prompts; a failure is logged in `Docs/AUTODRIVE_LOG.md` and the run continues.
- The stop guard lets a chunk end only after `CHUNK_DONE` exists, or after `CHUNK_MAX_MIN` minutes (default 150), so no chunk runs forever.
- The owner stops the driver by creating `.claude/ALLOW_STOP`; the current chunk finishes first.
- While `.claude/autodrive/ACTIVE` exists, only the driver's chunks work on the repo. An interactive session must not start work; it may read and answer the owner.
- Background agents do not survive the end of a chunk. Wait for every agent you start before you finish the chunk.

## 1c. Token discipline (measured in an earlier run: cache reads were 99% of all tokens)

The cost driver is **number of main-loop turns × context size**, not what each turn does. Rules:
1. **No poll loops in the main loop.** Start long work with `run_in_background` (or as an agent) and wait for the completion notification. Never write `sleep`/`until` loops that end a turn only to start another full-context turn.
2. **Batch.** Put independent tool calls in one turn. Chain shell steps in one command (build, capture and check in one call).
3. **Delegate reading.** Long files (lane docs, reviews, logs, specs) are read by the agent that wrote them or by a small-model agent that returns a short summary. The main loop greps the gate table and open issues, not whole files.
4. **Images are expensive context.** Open only the one screenshot that decides something; let reviewer and playtester agents look at the rest.
5. **Fresh context per milestone.** Autodrive gives each chunk a fresh context; inside a chunk, prefer finishing a coherent unit over growing the conversation.
6. **Read results, not transcripts.** Every subagent writes its result to a file and returns at most a short summary.

## Compact Instructions

When compacting, keep: the current milestone and TODO item, which agents or chunks are running, uncommitted changes, and the last gate result. Everything else lives in `Docs/` (PLAN, TODO, DECISIONS, DEVLOG HANDOFF, lane docs); point to those files instead of restating them.

## 2. Autonomy

- The owner is not available. Never ask a question and never wait for an answer. Decide, write the decision and the reason to `Docs/DECISIONS.md`, continue.
- Do not end the run on your own. When the current task is done, take the next item from `Docs/TODO.md`. When TODO.md is empty, run the acceptance test (TASK.md §2), or a fresh-context playtest of the weakest area, queue its findings, and continue. The guards are active while `.claude/AUTONOMOUS_RUN` exists; the owner ends the run by creating `.claude/ALLOW_STOP`. In autodrive, "continue" means: finish the chunk with a HANDOFF that names the next step.
- If a tool or MCP server fails: retry twice with a short wait, then switch to the alternative route, log it, and keep going. Re-check the failed tool at the next milestone.
- Stuck on one problem for more than 45 minutes of real time: write down what you tried, pick the fallback or cut the item, move on.

## 3. Records and cadence

- `Docs/DEVLOG.md` is append-only. Each entry starts with a heading `### YYYY-MM-DD HH:MM UTC — <milestone> — <title>` (time from `date -u`, never estimated). Write an entry at every milestone, every recovered failure, every chunk end (a `HANDOFF` entry: done / open / exact next step), and at least once an hour.
- `Docs/DECISIONS.md`: one line per decision, `YYYY-MM-DD HH:MM - <decision>. Why: <reason>.` Correct wrong claims with a new dated line; never silently edit an old one.
- Every hour: update `Docs/STATS.json` (elapsed time, commits, lines of code, assets per type authored/accepted/rejected, external assets, paid spend, Claude cost per chunk from `Docs/AUTODRIVE_LOG.md`, bugs fixed, performance numbers), run `python -I scripts/token_usage.py`, then commit.
- Progress captures follow TASK.md §19: after every significant UI change and at least every 10 minutes of real time on a feature with a visible surface. This is part of the job. If you notice a gap, capture now and continue.

## 3b. The owner's progress page is plain language

`/progress` is for a non-technical owner. It is rendered from `Docs/progress_story.md`, not from the dev log. At every milestone gate, add or refresh that milestone's card:
- a plain title, one sentence on what changed for the player, 2-4 short bullets, and one screenshot;
- no internal codes (milestone ids, review ids, hashes, test or balance jargon);
- numbers rounded and explained.

Keep "What you can do in the game now" and "Not perfect yet" current. The raw DEVLOG, DECISIONS and reviews appear only in the page's collapsed technical log.

## 3c. The living tutorial

Every game has a guided first-run tutorial, a How-to-play page and first-time tips, built from `data/tutorial.json` (spec: `Docs/TUTORIAL.md`).
- **Any commit that adds or changes a mechanic or feature also adds or updates its tutorial entry.** A coverage test enforces it.
- At every gate, the fresh playtester completes the tutorial and the reviewer checks the new entries.

## 4. Orchestration

Use multi-agent workflows for parallel work, with exactly one owner per shared resource.

| Lane | Owns | Writes to |
|---|---|---|
| Integrator (main loop) | the dev server and browser session, project config, git, deploys | `src/` wiring, configs, `e2e/` |
| Simulation | deterministic core ({{SIM_SYSTEMS}}), data schemas, sim tests, the harness | `src/sim/`, `src/content/`, `tests/` |
| UI | components, screens, styling, input, dev tools | `src/ui/`, `src/dev/` |
| Art & Audio | illustrations, portraits, icons, frames, SFX, licensed music | `assets/generated/`, `assets/external/`, `src/audio/` |
| Content | names, copy, lore, events, data tables | `data/` |
| Reviewer / Playtester | reads captures, concepts and the style bible; plays the build fresh; scores; files defects | `Docs/reviews/` |

- Only the Integrator mutates the single stateful tool session (the running dev/preview server, the Playwright MCP browser). Other lanes produce files plus an `asset.json` manifest (art) or a lane note in `Docs/lanes/` and add an item to `Docs/INTEGRATION_QUEUE.md`. A lane may write code for its own system in its own folder; the Integrator compiles, wires and tests it.
- Only one agent at a time drives the Playwright MCP browser. Batch work (tests, harness, captures) runs in background processes, which can run in parallel.
- Keep workflows focused: one lane, one deliverable, a verification step, a result written to a file.

## 4b. Model and effort routing

Follow `Docs/MODEL_ROUTING.md`. Summary of the standing rules:
- Decide the model and effort per task, before delegating. Choose the cheapest that reliably does the job; escalate only after two failed attempts, and log the escalation in `Docs/DECISIONS.md`.
- Running tests, polling results, reading logs, searching, formatting, capturing, committing and stats updates go to a small model at low effort, or to a script when no judgement is needed. Never spend a large model on them.
- Planning, architecture, hard debugging, the milestone-gate reviews at {{LARGE_GATES}}, and anything touching secrets, the server or git history use the large model at high effort.
- When spawning a subagent, set its `model` and `effort` from the routing table (the owner explicitly asks for per-task effort routing). Subagent definitions in `.claude/agents/` carry sensible defaults; override them when the task is clearly easier or harder.
- Run independent work as parallel subagents in one message. Give each a self-contained prompt, a single deliverable and a result file. Read the result file, not the transcript.
- The main loop does not change its own model; if it is clearly wrong for the phase, write a note in `Docs/DEVLOG.md` asking the owner to switch with `/model` (or to set `{{MODEL_ENV}}` for the driver), then continue.

## 5. Always playable / always working

- From milestone M1 on, the verification path (TASK.md §18) must pass at every commit. Run it after each integration batch.
- Commit only through `bash scripts/commit_green.sh "<message>" [tag]`. It runs the full gate once `package.json` has a `check` script and the lightweight doc/script checks before that. Never chain a plain `git commit` after a separate step.
- If a change breaks the gate and the fix is not obvious within 20 minutes, revert the change (`git revert` or restore the files) and re-queue it.
- Commit at least every 30–60 minutes with a message that says what changed. Never force-push, never rewrite history, never delete authored sources or rejected attempts.

## 5b. Shared machine (other runs in parallel)

- Other autonomous runs may work on the same PC at the same time. `PORTS.md` is the port registry. {{GAME_NAME}} uses its own ports: **vite dev {{DEV_PORT}}, vite preview {{PREVIEW_PORT}}, both `strictPort: true`**. Never use, kill or reuse another project's ports or processes, and never touch another project's folder under `C:\Users\ernes\`.
- Performance numbers (fps, frame times, tick times, soak results) measured while another run is busy are noisy. Before you treat a drop as a regression, re-measure solo (or at least twice at a quiet moment) and record both numbers with the conditions.
- Kill processes by PID only, and only processes you started.

## 6. Asset discipline (budget {{BUDGET_USD}} USD)

- **If the budget is 0 USD:** there is **no paid generation**. Every look-defining asset (frames, illustrations, portraits, icons, the logo, backgrounds) is hand-authored SVG or code-generated (procedural SVG/canvas). No image, 3D, voice or music generator that costs money, and no API keys.
- **If the budget is above 0:** use the primary provider of TASK.md §16 first and sparingly (1–3 attempts per asset, no mass generation). Log every paid call in `Docs/COSTS.md` and the asset's `asset.json` (UTC time, provider, job ID, purpose, asset id, cost, output path, result). At 80% of the cap use the secondary provider only where the primary has no equivalent; at 100% stop. A polling timeout is not a failure: resume the job by its ID. Keys live in `.env` only.
- Free assets are allowed for everything that does not define the look (music, fonts, some textures): permissive licences only (CC0, CC-BY with credit, SIL OFL, MIT), logged with source, author and licence in `Docs/LICENSES.md`, stored under `assets/external/<source>/`. Never use files ripped or extracted from commercial products or from the reference games.
- Every asset batch gets an `asset.json` manifest (see `scripts/assets/asset.json.example`; validated by `scripts/assets/validate_asset.py`).
- Max 3 attempts per asset at the same stage, then simplify or switch route, and log it. Keep rejected attempts under `_rejected/`.
- Concept first: a proposed sheet in `Docs/concepts/proposed/`, checked against the style bible (and the approved concepts once any exist), then production. Keep one consistent style; reject assets that break style or scale.
- Keep the size budgets (TASK.md §15) at authoring time.
- Never put brand, trademark or franchise names (including the reference games) into in-game text, asset names or prompts for agents that produce assets. TASK.md §3 lists the setting's further taboos.

## 7. Verification

- You do not grade your own work. The Reviewer lane (a fresh-context agent) scores captures against `Docs/STYLE_BIBLE.md`, `Docs/concepts/approved/` and `Docs/refs/`. The Playtester lane (a fresh-context agent) plays the build cold at 1440×900 and at 390×844 and scores it. Look at every screenshot you mention; never describe an image you have not opened.
- Status words: **implemented** (exists), **agent-verified** (a test, fixture, probe, reviewer or playtester confirmed it in the running product), **pending owner review** (default for anything visual or about feel). Never mark anything as accepted by the owner.
- At every gate: zero console errors, zero missing references, verification path passes, the 390 px phone layout is checked, performance measured on the target scenario (TASK.md §15), a fresh-context playtest with scores, a trailer cut.
- Balance and timing numbers come from one final run on a fixed seed set after all edits, saved under `Docs/balance/`. Never quote an intermediate run.

## 8. Stack practice

Lessons that cost hours in earlier runs live in `Docs/PIPELINE_LESSONS.md`, `knowledge/`, `processes/` and `.claude/skills/`. Read the relevant file before touching that area, and append new lessons when you learn them (date, tool, symptom, cause, fix).

General habits:
- Poll long operations by waiting for their completion notification, not by re-running them.
- Long checks run as scripts or Playwright specs that write a JSON result atomically (temp file, then rename). Start them with one short call and read the file when they finish.
- Engine rules live in the sim, never only in the UI. If a UI race can reach an invalid state, fix the rule in `src/sim/`.
- Wait loops in tests key on the specific run's output, never on a glob that an earlier run already satisfies.
- Do not run CPU-heavy gates while a timing-sensitive measurement is sampling.
- Bash heredocs with JSX, backticks or quotes break easily: write patch scripts to the scratchpad with the Write tool and run them with python.
- Never pipe a gate through `grep`/`tail` without keeping its exit code.

Never edit the harness mid-milestone. Hooks, the verification driver, the acceptance script and the autodrive files change only at a milestone boundary, in their own commit, with a DECISIONS line.

## 9. Boundaries

- Work only inside this project folder (`{{PROJECT_DIR_WIN}}`). Never modify another project (PORTS.md lists them).
- Git: the agent commits locally and never pushes or changes remotes (the bash guard blocks it). The owner set `origin` to {{GITHUB_REMOTE}} once; the autodrive driver pushes `master` after each chunk.
- The only other remote action allowed is deploying the site to the owner's server (TASK.md §20) with `scripts/deploy_server.sh` and, once, the server setup in `deploy/README.md`. Touch only `{{DEPLOY_DIR}}` and {{GAME_NAME}}'s own nginx site file; never change other sites, users, packages or firewall rules.
- No posting anywhere, no account changes, no purchases beyond the budget in §6.
- Secrets stay in `.env` (gitignored). Never print them, never commit them.

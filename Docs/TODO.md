# TODO.md - prioritised queue
Order: review and playtest defects > P0 > P1 > P2. Legend: [x] done, [~] partly, [s] superseded, [ ] open.
Each item names its lane. Mark items done with a short evidence note in parentheses.

## M0 Scaffold and verification harness

### Setup
- [ ] T1 (Integrator) Confirm `.claude/AUTONOMOUS_RUN` exists; `date -u`; first DEVLOG entry. Smoke-test the tools and log their versions in DEVLOG:
  - node, npm, python, ffmpeg, git;
  - the Playwright MCP (open about:blank);
  - context7;
  - ssh to the server (`ssh -o BatchMode=yes {{SERVER_SSH}} true`; failure is logged, not fatal);
  - `git remote -v` shows `origin` = {{GITHUB_REMOTE}} (the driver pushes; a missing remote is logged as an owner action, not fatal).

### Design docs
- [ ] T2 (Integrator, large model) Write `Docs/ARCHITECTURE.md`:
  - folders; the state shape (meta vs session);
  - RNG streams (one per system);
  - the core model of TASK.md §5-§7 as formulas;
  - the save format and versioning;
  - the `window.__{{GAME_SLUG}}` API;
  - the fixture list.
- [ ] T3 (Integrator, large model) Write `Docs/MAP.md`:
  - the screen flow from TASK.md §13;
  - a wireframe description per screen at 1440x900 and 390x844;
  - the fixed capture states (one per screen and per key state), each with a fixture name and seed.

### Scaffold
- [ ] T4 (Integrator) Scaffold the project:
  - Vite + TypeScript strict + Preact + zod + Vitest + Playwright + ESLint; Node 20+;
  - `vite.config.ts` with server port **{{DEV_PORT}}**, preview port **{{PREVIEW_PORT}}**, `strictPort: true`; `base: './'`;
  - scripts: dev, build, preview (`vite preview --port {{PREVIEW_PORT}} --strictPort`), typecheck, lint, test, validate-data, harness, e2e, e2e:goldpath, capture, acceptance, check;
  - `.gitignore` already exists.
- [ ] T5 (Integrator) Playwright configs:
  - `playwright.config.ts` (smoke + gold path; baseURL `http://localhost:{{PREVIEW_PORT}}`, webServer `npm run preview`, `reuseExistingServer: true`, `actionTimeout` 10 s);
  - `playwright.capture.config.ts`;
  - `playwright.acceptance.config.ts`;
  - `playwright.trailer.config.ts` (video 1440x900).
  - Desktop project 1440x900; phone project 390x844 with `hasTouch` and `isMobile`.
  - Check: `bash scripts/check_gate.sh` passes the port check.

### Sim and data
- [ ] T6 (Simulation) `src/sim/rng.ts`: a seeded PRNG with named streams and a serialisable state; a state skeleton; a determinism test (same seed gives the same hash).
- [ ] T7 (Simulation) `data/tuning.json` and its zod schema (every tunable number of TASK.md §5-§11, the time model, the difficulty knobs); `scripts/validate-data.ts --strict`.

### UI and dev tools
- [ ] T8 (UI) The theme: `src/ui/theme.css` with the STYLE_BIBLE tokens; install the style bible's fonts (`@fontsource/*`, Latin subsets) and check tabular figures; log the fonts in `Docs/LICENSES.md`; a contrast check script for the text token pairs.
- [ ] T9 (UI) The title screen placeholder (logo text, "New game", "Continue" disabled, "Settings"), a favicon (SVG), and the debug panel (seed, speed, fixture picker) behind `?dev` or the backquote key.
- [ ] T10 (UI) `window.__{{GAME_SLUG}}`: getState, setSpeed, loadFixture (title fixture). Inert in production builds unless `?test`.

### Verification
- [ ] T11 (Integrator) The e2e smoke: the title loads with zero console errors. Then the gold-path skeleton writes `Docs/goldpath/<ts>/checks.json` atomically.
- [ ] T12 (Integrator) The capture spec: title at both viewports into `Docs/progress/title/`; logged with `scripts/capture/log_capture.py`.
- [ ] T13 (Integrator) The `scripts/acceptance.ts` skeleton writes `Docs/acceptance/<ts>/report.md` with every row of TASK.md §2 ("not tested" for now). Also the harness skeleton (`scripts/harness.ts --quick`) writes `Docs/goldpath/<ts>-sim/checks.json`.
- [ ] T14 (Integrator) Wire `npm run check` (typecheck, lint, validate-data, test, harness --quick, build, e2e), then commit through `scripts/commit_green.sh` (the full gate now runs).

### Art
- [ ] T15 (Art, mid model) The first concept sheet in `Docs/concepts/proposed/`: {{FILL: TODO T15 concept sheet contents}}. Render it to PNG. The reviewer agent checks it against the style bible; update STYLE_BIBLE.md with what was learned.
  <!-- 3-5 representative pieces. Zephyr: a room card in its frame, a medallion portrait, the queue rail with 10 tokens and a wind forecast, two UI icons. -->

### Site and deploy
- [ ] T16 (Integrator) The site: `npm run build && python scripts/build_site.py` works (placeholder trailer page, `/progress/`); `python -I scripts/token_usage.py`.
- [ ] T17 (Integrator, large model) The one-time server setup with `DEPLOY_SSH={{SERVER_SSH}} bash scripts/server_setup.sh` (skip if the owner already ran it; the script is safe to re-run):
  - if DNS for {{DOMAIN}} does not point at {{SERVER_IP}}, the script installs HTTP only; log it in DECISIONS and in REPORT "owner actions";
  - then `bash scripts/deploy_server.sh` and check the live bundle.
  - Never touch other sites.

### Gate
- [ ] T17b (Integrator) Create `Docs/REPORT.md` with the sections from TASK.md §20: what works (table: feature | status | evidence), what doesn't; numbers; playtest scores per gate; owner actions; the ten hardest problems.
- [ ] T18 (Integrator) The M0 gate: `.claude/commands/gate.md` steps that apply (no playtest yet); STATS.json; a DEVLOG gate entry; the first card in `Docs/progress_story.md`; tag m0. Then queue M1 in detail in this file (from PLAN.md M1).

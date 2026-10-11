# {{GAME_NAME}} — build task

The complete task for this project. Read it fully before your first action and keep it open as the spec.
Working rules live in `CLAUDE.md` (re-read after every context compaction and at the start of every autodrive chunk). This file is the WHAT; CLAUDE.md is the HOW.
Everything in this project is in English: code, comments, docs, in-game text, prompts, commit messages, logs.

<!--
TEMPLATE NOTE {{FILL: delete this TEMPLATE NOTE comment}}
- Simple values like the game name, ports and domain were filled by scripts/fill_template.py.
- Every FILL marker (double braces around "FILL: <id>") marks a rich section. Claude writes it from the owner's answers in QUESTIONS.md.
  Replace the marker and its guidance comment with the real text, at the depth of the Zephyr examples.
  Keep the section numbers: CLAUDE.md, the agents, the skills and the scripts cite them (§1, §2, §5, §13-§20).
- A filled TASK.md is roughly 450-550 lines. Every mechanic must be testable: give numbers, counts and ranges,
  and say where tunable values live (data/tuning.json).
- Working names may change later, but only with a DECISIONS.md line.
-->

## 0. Mission

{{FILL: TASK §0 mission}}
<!--
Write 1 paragraph: "Build **{{GAME_NAME}}**, a <genre> played in the web browser. It is set in <setting>, with a <tone> tone.
The project starts from this empty repository; it is a web game (TypeScript, static site)."
Then "The game in one breath:" with 4-6 bullets, one per signature mechanic, each with the player-facing hook in bold.
Zephyr example:
  - You lead a small party of folk heroes and mythic beings through a dungeon of illustrated room cards.
  - Battles run on a visible initiative timeline that a shifting **Wind** pushes every round.
  - Every room you enter moves the clock from **Day to Dusk to Night**. Night makes monsters stronger and rewards richer.
  - The act's boss is deathless until you find its hidden death, the **needle**, somewhere in the dungeon.
  - Heroes can die for good. Every run, won or lost, moves the meta forward.
-->

**Quality bar.**
{{FILL: TASK §0 quality bar}}
<!--
3-6 bullets of time-boxed, observable player outcomes. Zephyr example:
  - Within 2 minutes a new player has entered a room, fought a battle and seen the wind move the turn queue.
  - Within one act (12–15 minutes) they have recruited a second hero, felt night fall, found part of the boss's death,
    lost or nearly lost someone.
  - After the first run they understand why the next run will differ.
  - The game must read clearly at a glance: who acts next, what an attack will do, what is effective against what.
-->

It is a personal, non-commercial project: single player, offline-capable after the first visit, no backend, no accounts, no monetisation.

**Focus.** One polished, fully playable MVP beats a large rough one. Spend the time where the player looks:
{{FILL: TASK §0 focus list}}
<!-- 4-7 bullets: the moments that must feel great. Zephyr: the timeline battle and its preview; the wind; the room cards;
     the night; the needle reveal and the boss kill; the moment a hero dies. -->

Everything else stays minimal until the MVP (§2) is green.

Nobody will answer questions during the work: decide, log the decision in `Docs/DECISIONS.md`, continue.

### References for feel (study them; never copy assets, names or text)

Use these for the developer's understanding only. Their names never appear in the game, in asset names or in prompts for asset-producing agents.

| Reference | What to learn from it |
|---|---|
| {{FILL: TASK §0 references table}} | <!-- 4-8 rows from QUESTIONS.md "References". Zephyr row: "Slay the Spire | The run map's readable choices, rewards with a pick of three, relics, act structure and bosses." --> |

## 1. The MVP experience

{{FILL: TASK §1 MVP experience}}
<!--
One sentence naming the MVP slice and its length ("The MVP is **Act 1: the Haunted Forest**, fully playable from start
to finish in 12–15 minutes."), then a numbered list of 8-12 steps that walk one complete session from the title screen
to the second session starting differently. Each step is concrete enough to become a gold-path checkpoint.
Zephyr steps (abridged): 1 Title and hub (intro, skippable) - 2 New run (pick a hero, seed shown) - 3 Explore (map, room
cards, clock advances) - 4 First battle within 2 minutes (queue, preview, wind, intents) - 5 Recruit - 6 Dusk and night -
7 Rest, shop, events - 8 The needle chain - 9 Boss - 10 Death and the end - 11 Run summary - 12 Back at the hub, spend,
next run differs.
-->

Everything on this path must be reliable: no softlocks, no NaN/Infinity, no lost saves, no broken UI, at 1440×900 with mouse and keyboard and at 390×844 with touch.

## 2. Priorities, scope and acceptance test

Priorities, in order:
{{FILL: TASK §2 priorities}}
<!-- 5-8 numbered priorities, core loop first, art/audio/phone polish/performance last.
     Zephyr: 1 Timeline battle core - 2 The Wind - 3 Dungeon crawl and Day/Dusk/Night - 4 Party and permadeath -
     5 Boss and the needle - 6 Meta - 7 Art and audio pass, phone polish, performance. -->

Not in the MVP (only after every P0 and P1 passes, and then in this order): {{FILL: TASK §2 post-MVP list}}. Never: multiplayer, accounts, monetisation, native apps, localisation beyond English.

**Acceptance test.** Done when every P0 row passes in a real browser run (Playwright, desktop 1440×900 and phone 390×844) and the deterministic simulation harness passes.
- `npm run acceptance` writes `Docs/acceptance/<UTC yyyymmdd-HHMMSS>/report.md` with one row per line below (PASS / FAIL / not tested, plus evidence paths) and the screenshots.
- Run the full acceptance test at every gate from {{ACCEPTANCE_FROM}} on and log the score in `Docs/DEVLOG.md`.
- Each row names how it is tested:
  - **sim**: a Vitest test or the headless harness over fixed seeds;
  - **e2e**: Playwright through the real UI with real clicks/taps;
  - **both**.

| # | Moment | Pass condition (testable) | Test | Tier |
|---|---|---|---|---|
| 1 | First minutes | {{FILL: TASK §2 row 1 pass condition}} | e2e | P0 |
| {{FILL: TASK §2 game rows}} | | | | |
| n-5 | Save / resume | Reloading mid-session resumes the exact state. The save is versioned with a tested migration path. Export/import of the save works as text. | both | P0 |
| n-4 | Phone | The whole gold path plays at 390×844 with touch only. No horizontal scroll. Tap targets ≥ 44 px. The core information fits without zooming. | e2e | P0 |
| n-3 | Performance and quality | 60 FPS in the main scenes at 1440×900 on the dev PC (measured solo, CLAUDE.md §5b). ≥ 50 FPS at 390×844 with 4× CPU throttle. Budgets in §15 met. Zero console errors. No NaN/Infinity in any state (harness). | both | P0 |
| n-2 | Content counts | {{FILL: TASK §2 content counts row}}, all zod-valid (`npm run validate-data`). | sim | P0 |
| n-1 | Audio | {{FILL: TASK §2 audio row}} Master, music and SFX sliders and mute work. | e2e | P1 |
| n | Accessibility | Reduced motion is respected. Keyboard-only play works. Contrast passes the style bible's ratios. axe audit: 0 serious/critical. | e2e | P1 |

<!--
Fill the rows: number them 1..N in order (replace "n-5".."n" with real numbers). Aim for 15-20 rows: ~12-15 P0, 3-5 P1,
1-2 P2. Every pass condition is testable with numbers, seeds or counts. Zephyr examples:
| 2 | Timeline queue | The queue shows ≥ 10 upcoming turns. The order matches the sim's prediction. Selecting an action shows a preview of the queue after it. A delay effect moves the target later exactly as previewed. | both | P0 |
| 5 | Dungeon crawl | Each seed yields a map with 16–22 rooms, revealed as you explore, and ≥ 8 room types. Every generated map has a path from entrance to boss (harness: 1,000 seeds). Two seeds give different maps. | both | P0 |
| 10 | Full act | A UI-driven gold-path player completes Act 1. The harness's "good" player wins on 55–75% of 200 seeds, "careless" on 15–35%, random < 10%. Modelled act length 12–15 min (median). | both | P0 |
Row 1 example: "Title → hub → new run → first room within 30 s of input. First battle within 2 min. Seed shown. Zero console errors."
Content counts example: "4 heroes, ≥ 12 enemies, 1 boss, ≥ 15 events, ≥ 16 relics, ≥ 12 meta upgrades, ≥ 10 lore fragments".
Update scripts/acceptance.ts (M0) to list exactly these rows.
-->

P0 = must for the MVP. P1 = should, after P0. P2 = only after all P0 and P1 pass.

## 3. Project rules

- **Assets (budget {{BUDGET_USD}} USD).**
  - With a 0 USD budget, everything that defines the look is hand-authored SVG or code-generated. With a paid budget, follow §16 and CLAUDE.md §6.
  - Free assets with permissive licences (CC0, CC-BY with credit, SIL OFL, MIT) are fine for music, fonts and a few textures. Log every one in `Docs/LICENSES.md`.
  - Never use ripped or extracted assets from commercial games, films or books, and nothing from the reference games.
- **Names.** Every name (characters, items, places, skills) is original, or public-domain folklore/history. No third-party trademarks or franchise names in the game or in any prompt.
- **Respect and taboos.** {{FILL: TASK §3 setting taboos}}
  <!-- What the setting must avoid. Zephyr: "Slavic folklore, not caricature. No faux-Cyrillic lettering. No extremist-associated symbols (see STYLE_BIBLE.md)." -->
- **No questions.** Decide, write to `Docs/DECISIONS.md`, continue.
- **Language.** English everywhere. Setting-specific terms may appear in italics with an English gloss.

## 4. Look and feel — "{{FILL: TASK §4 style name}}"

Write and keep `Docs/STYLE_BIBLE.md` (a draft exists) and follow it. Open every image in `Docs/concepts/approved/` and `Docs/refs/`, if any.

{{FILL: TASK §4 look and feel}}
<!--
Summarise the art direction from QUESTIONS.md "Art style" in 15-30 lines: the surfaces or layers of the look, what to Keep,
what to Upgrade (motion and juice), what to Avoid. The full detail goes into Docs/STYLE_BIBLE.md.
Zephyr example: "Two surfaces: Lacquer is the chrome (black lacquer, gold filigree, vermilion accents) for HUD, battle,
map, hub; Lubok is the illustration (paper-toned woodcut prints, bold outlines, flat tint) for room, event and death
cards. Keep: gold and vermilion on deep black, ornate borders with discipline, large legible numbers. Upgrade: card flips,
wind streaks, lantern light at night. Avoid: clutter, text under 13 px, photographic textures, glossy 3D bevels,
mixed icon styles, lore walls."
-->

## 5. {{FILL: TASK §5 core system title}}

{{FILL: TASK §5 core system}}
<!--
The core moment-to-moment system (battle, movement, building, puzzle...). Read the references in §0 before designing it.
Give: the layout; the deterministic model with formulas (state fields, update order, tie-breaks never by RNG);
the player's actions and their costs; what the UI must preview before the player commits (and that the preview equals
the outcome); feedback; pace targets in seconds; enemy/opponent AI (deterministic given the seed).
Zephyr §5 "Combat: the initiative timeline": every unit has nextAt; after acting nextAt += actionDelay × 100 / speed;
delay classes quick 60 / normal 100 / heavy 140; the queue shows the next ≥ 10 turns; hovering an action previews the
queue; effects delay/haste/slow/stun/interrupt; 4 skills plus Guard and Item; Breath 2 at start +1 per turn max 5;
intents within 3 turns; affinities ×1.5 / ×0.5 / ×0; normal battle 45–90 s.
-->

## 6. {{FILL: TASK §6 signature mechanic A title}}

{{FILL: TASK §6 signature mechanic A}}
<!-- The first signature mechanic: state, effect (with the tuning key and default), how it changes, how the player
     steers it, interactions, and how it stays readable. Zephyr §6 "The Wind": wind = { side, strength 0..3 } with a
     one-round forecast; at each round marker the favoured side gets nextAt −= strength × windStep (default 12 ticks);
     seeded shift table biased by room and time of day; ≥ 2 abilities steer it. -->

## 7. {{FILL: TASK §7 signature mechanic B title}}

{{FILL: TASK §7 signature mechanic B}}
<!-- The second signature mechanic or the session's pressure system. Zephyr §7 "Day, Dusk, Night": each unvisited room
     advances the clock (Day 5, Dusk 2, Night 4 steps); night gives enemies +25% HP and damage and rewards +50%;
     phase changes shown by a card; night is a choice, not a timer. -->

## 8. {{FILL: TASK §8 goal and climax title}}

{{FILL: TASK §8 goal and climax}}
<!-- The session's goal, climax or boss, and how earlier play feeds into it. Include a fairness requirement the harness
     can measure. Zephyr §8 "Koschei's needle": the boss has reforms = 3, each needle stage found removes one; the chain
     oak/chest → hare/duck → egg/needle in three clue rooms off the main path; "Break the needle" kills at ≤ 50% HP;
     harness: beatable with 0 stages (rarely) and with 3 stages (usually). If the genre has no boss, describe the win
     condition and the end-of-session moment instead. -->

## 9. {{FILL: TASK §9 characters and roster title}}

{{FILL: TASK §9 characters and roster}}
<!-- Who the player controls or collects: roster table (| Name | Kind | Role | Signature |), growth inside a session,
     failure and loss rules (death, wounds, damage, lives), fairness targets. Zephyr §9 "Party: recruitment, roster,
     permadeath": party up to 4; 4 recruitable heroes; level up every ~3 fights with a pick of 3; downed → Wound →
     death on a second down; a wipe ends the run; at least one hero should fall in about a third of runs. -->

## 10. {{FILL: TASK §10 world and structure title}}

{{FILL: TASK §10 world and structure}}
<!-- The space the session happens in: map or level generation (seeded), fog/reveal, node or room types, rewards,
     and a pace target from the time model in data/tuning.json. Zephyr §10 "The dungeon crawl: map and room cards":
     16–22 rooms on a grid, spanning tree plus 2–4 loops, boss at maximum distance; ≥ 8 room types as flipping cards;
     rewards pick 1 of 3; 12–15 minutes per act. -->

## 11. {{FILL: TASK §11 meta-progression title}}

{{FILL: TASK §11 meta-progression}}
<!-- Between sessions: hub, currency, ≥ N permanent upgrades, unlocks that change the next session's pools, lore
     revealed run by run, persistence (meta and session saved separately, versioned, export/import).
     Zephyr §11 "Meta-progression and lore": Baba Yaga's hut as hub; firebird feathers (a failed run always earns some);
     ≥ 12 upgrades; the Book of Tales with ≥ 10 fragments. -->

## 12. Content model

All content is data (JSON in `data/`), validated by zod schemas at load (`src/content/`) and by `npm run validate-data` (strict).

| Entity | MVP count | Key fields |
|---|---|---|
| {{FILL: TASK §12 content table}} | | |
| Tuning | 1 file | every tunable number in §5-§11, the time model (seconds per action/screen), difficulty knobs |

{{FILL: TASK §12 working lists}}
<!-- Working lists the Content lane starts from (rename freely with a DECISIONS line): e.g. the MVP enemy set, the boss,
     item families. Then "Later (post-MVP, for the plan only)". Zephyr table rows: "| Hero | 4 (+ classes P1) | id, name,
     kind, role, base stats, skills, level-up pool, portrait |", "| Event | ≥ 15 | id, card art, conditions, options,
     lore links |", ... ; then a 12-enemy list and the boss with its phases. -->

## 13. Screens, HUD, controls, devices

- **Screens:** {{FILL: TASK §13 screen flow}} Plus Settings (audio, speed, reduced motion, text size, save export/import) and Credits (assets and licences).
  <!-- Zephyr: Title → Hub → Hero pick → Map (with room-card overlay) → Battle → Rewards → Death card / Run summary → Hub. -->
- **Write `Docs/MAP.md` at M0:** screen flow, navigation, layouts at 1440×900 and 390×844, and the fixed capture states (§19), before building the final UI.
- **HUD.** {{FILL: TASK §13 HUD contents}} Tooltips on every number (long-press on touch).
  <!-- Zephyr: party portraits with HP, Breath and Wounds; gold, feathers, items; the clock dial; needle progress; the seed. -->
- **Controls.**
  - {{FILL: TASK §13 controls}}
    <!-- Zephyr: "Desktop first: mouse plus keyboard shortcuts (1–4 skills, G guard, I item, Tab cycle targets, Enter confirm, Esc back, M map)." -->
  - Everything is reachable without hover.
  - Touch: tap to select, tap again to confirm; long-press for info.
- **Devices.**
  - {{FILL: TASK §13 device priority}}
    <!-- Zephyr: "Fully playable on phones in portrait at 390×844 and up to 4K." Options: desktop-first with phone support; phone-first portrait; desktop only (then drop the phone rows). -->
  - No horizontal scroll from 360 px; tap targets ≥ 44 px.
  - Test at 390 px at every gate.

## 14. Audio

- **Music:** free, permissively licensed tracks (CC0 or CC-BY, logged) for {{FILL: TASK §14 music contexts and instrumentation}}.
  - Lazy-load the tracks; loop seamlessly; loudness-normalise them (−16 LUFS).
  - If no fitting track is found, use a procedural drone/ostinato from the Web Audio synth and log the decision.
  <!-- Zephyr: "the hub, map by day, map by night, battle and boss. Folk instrumentation (gusli, balalaika, choir, drones) is preferred." -->
- **SFX:** synthesised in code with the Web Audio API (no files): {{FILL: TASK §14 SFX cue list}}.
  <!-- Zephyr: hits per damage kind, Guard, turn tick, queue shift, wind gust, card flip, phase change, downed, death toll, victory, needle break. -->
- **Mixer:** master, music and SFX sliders, mute, and a respectful default volume. Audio starts only after the first user input.

## 15. Technical architecture, performance and size budgets

- **Stack:** TypeScript (strict), Vite, Preact, zod for data validation, Vitest for unit/sim tests, Playwright for e2e, captures and trailers, ESLint. Node 20+. Output: a static site in `dist/`. (Change the UI layer only with a DECISIONS line, e.g. canvas/PixiJS for an action-heavy game.)
- **Ports (shared machine, PORTS.md):** vite dev **{{DEV_PORT}}**, vite preview **{{PREVIEW_PORT}}**, both `strictPort: true`. Playwright `baseURL` is `http://localhost:{{PREVIEW_PORT}}`. The webServer command is `npm run preview` (`vite preview --port {{PREVIEW_PORT}} --strictPort`). Never another project's ports.
- **Structure:**
  - `src/sim/`: the pure deterministic core, no DOM ({{SIM_SYSTEMS}}).
  - `src/content/`: schemas and loaders.
  - `src/ui/`: components and theme.
  - `src/audio/`.
  - `src/dev/`: the debug panel, seed input, speed, fixtures, the test API.
  - `data/`: JSON content.
  - `assets/{generated,external}/`.
  - `tests/`, `e2e/`, `scripts/`.
- **Determinism:**
  - One seeded PRNG (for example sfc32 or mulberry32), split into named streams so one system's draws never shift another's.
  - No `Math.random` or `Date.now` in `src/sim/`; time is passed in.
  - Same seed plus same inputs gives the same state (sim test).
- **State and saves:**
  - A serialisable state with versioned saves in localStorage (meta and session separately), autosave at safe points, and text export/import.
  - Migrations are tested.
- **Test API:** `window.__{{GAME_SLUG}}` (dev and test builds; stripped or inert in production) with:
  - `getState()`, `newRun(seed, ...)`, `loadFixture(name)`, `setSpeed(x)`;
  - {{FILL: TASK §15 test API extras}}
    <!-- Cheats that make each signature mechanic testable. Zephyr: predictQueue(), forceWind(side, strength), setClock(step), revealMap(), giveRelic(id). -->
  - Named fixtures for every capture state.
- **Performance budgets:**
  - 60 FPS in the main scenes at 1440×900; ≥ 50 FPS at 390×844 with 4× CPU throttle.
  - {{FILL: TASK §15 sim timing budgets}}
    <!-- Zephyr: a sim step < 2 ms; queue preview on hover < 4 ms; map generation < 50 ms. -->
  - Time to interactive < 2 s from the local preview.
  - Memory stable over a 30-minute soak (heap growth < 10%).
- **Size budgets:**
  - Initial JS < 250 KB gzip.
  - Fonts ≤ 200 KB in total (woff2, Latin subsets).
  - Each SVG illustration ≤ 60 KB raw (≤ 25 KB gzip); portraits ≤ 20 KB each; raster art (paid budget only) ≤ 300 KB each as WebP/AVIF.
  - Initial page weight < 1.5 MB.
  - Music lazy-loaded: ≤ 1.5 MB per track (Ogg/Opus around 96 kbps), ≤ 8 MB in total.
- **Quality gates:** `npm run check` = typecheck + lint + validate-data + test + harness (quick) + build + e2e (smoke + gold path). Green at every commit from M1 (CLAUDE.md §5).

## 16. Asset sources and budget

**Budget: {{BUDGET_USD}} USD** for paid generation (CLAUDE.md §6). With 0 USD there is no paid generation of any kind and no `.env` key to configure.

| Need | Route | Fallback |
|---|---|---|
| Logo, frames, ornaments, illustrations, portraits, icons | Hand-authored SVG by the Art lane, in the style bible, from a concept sheet first (or the paid primary provider, if the budget allows) | Simpler geometric SVG in the same palette |
| Procedural variety (backgrounds, particles, map tiles) | Code-generated SVG/canvas from the seed | — |
| Fonts | SIL OFL fonts via npm (`@fontsource/*`) | System serif/sans |
| Music | CC0 / CC-BY libraries (logged with URL, author, licence) | Procedural Web Audio drones |
| SFX | Procedural Web Audio | CC0 sound files (logged) |

{{FILL: TASK §16 paid providers}}
<!-- Only if the budget is above 0: name the primary and secondary provider per asset type, the cost per call, and the
     caps. With a 0 USD budget, delete this marker and the comment. -->

Log every external file in `Docs/LICENSES.md` and in the in-game Credits. Each asset batch gets an `asset.json` (`scripts/assets/validate_asset.py`). `Docs/COSTS.md` records paid assets (0 rows with a 0 USD budget) and the Claude cost per autodrive chunk for the report.

## 17. Work plan (milestones and gates)

The detailed plan and status live in `Docs/PLAN.md`; the queue lives in `Docs/TODO.md`. Summary:

| Milestone | Content | Gate |
|---|---|---|
| M0 Scaffold and verification harness | Read everything; ARCHITECTURE, MAP, style bible final draft; Vite + TS + Preact + zod + Vitest + Playwright + ESLint on ports {{DEV_PORT}}/{{PREVIEW_PORT}}; `npm run check`; RNG + state skeleton; validate-data; test API; capture spec; gold-path and acceptance skeletons; site build; first deploy of a placeholder. | `npm run check` green; captures at 1440 and 390; tag `m0`. |
| M1 Sim core | {{FILL: TASK §17 M1 content}} | Sim tests and determinism green; harness runs 200 seeded sessions/encounters with no NaN; tag `m1`. |
| {{FILL: TASK §17 milestones M2..MVP}} | | |

<!--
6-8 milestones in total, M0 and M1 as above. M2 is the first playable core loop (large-model gate). The acceptance test
starts at {{ACCEPTANCE_FROM}}. The last milestone ({{MVP_MILESTONE}}) is the art and audio pass and the MVP gate:
"all P0 green, large-model review + fresh playtest, trailer, deploy; tag {{MVP_TAG}} / mvp". Large-model gates: {{LARGE_GATES}}.
Zephyr rows: M2 First playable battle | M3 Dungeon crawl and day/night (acceptance run #1) | M4 Party, recruitment,
permadeath | M5 Boss and the needle | M6 Meta and hub | M7 Art and audio pass (MVP).
-->

After {{MVP_MILESTONE}}: P1 rows by value, then the post-MVP list of §2. The owner ends the run, not you.

## 18. Verification path (you do not grade your own work)

- **Unit and sim tests (Vitest):**
  - {{FILL: TASK §18 sim test list}}
    <!-- Zephyr: timeline maths, preview equals outcome, wind push, clock, night modifiers, needle reforms, wounds/death/wipe, map connectivity. -->
  - save round-trip and migration;
  - determinism (same seed and inputs give the same state hash).
- **Simulation harness** (`npm run harness`, quick mode in `check`):
  - scripted players (good, careless, random) play full MVP sessions headlessly on fixed seeds;
  - it asserts {{FILL: TASK §18 harness bands}}, session length (time model), no softlocks (every state has a legal action), no NaN;
    <!-- Zephyr: win-rate bands (good 55–75%, careless 15–35%, random < 10% of 200 seeds), map solvability over 1,000 seeds, needle fairness. -->
  - output: `Docs/goldpath/<ts>-sim/checks.json`.
- **Gold path (Playwright, real UI):**
  - plays §1 end to end through real clicks with a fixed seed and the speed setting (pacing asserted in sim time, not wall time);
  - {{FILL: TASK §18 gold path route}}
    <!-- Zephyr: title → hub → new run → battle with a wind shift → recruit → night → needle stages → boss → break the needle → summary → hub upgrade → second run starts with the unlock. -->
  - screenshots at fixed checkpoints, console errors collected;
  - output `Docs/goldpath/<ts>/checks.json`, written atomically.
  - A phone variant (390×844, touch) runs the same path at gates.
- **Acceptance** (`npm run acceptance`): runs everything above plus the per-row checks and writes the §2 report.
- **Reviewer agent** (fresh context, at every gate and after big UI batches): scores captures against the style bible and approved concepts (clarity, readability, consistency, feel), and lists the three worst defects with fixes. It writes to `Docs/reviews/`.
- **Playtester agent** (fresh context, at every gate): plays the build cold through the Playwright MCP at 1440×900 and 390×844. It scores these areas 1–10 each: {{PLAYTEST_AREAS}}; and names the weakest area. It writes to `Docs/reviews/<ts>-playtest-<milestone>.md`. The weakest area becomes the top of TODO.
- Fix review and playtest defects before adding features. Zero console errors, zero failing tests at every gate. Look at every screenshot you cite.

## 19. Progress captures (mandatory)

- **Fixed capture states:**
  - At M0, define one deterministic state per screen in `Docs/MAP.md` (a seeded fixture plus viewports 1440×900 and 390×844).
  - Never change them; add new ones as features start.
  - The fixtures load through `window.__{{GAME_SLUG}}.loadFixture(name)`.
- **Capture rule:** after every significant UI change and at least every 10 minutes of UI work:
  - capture the fixed state to `Docs/progress/<feature>/<UTC yyyymmdd-HHMMSS>__<screen>-<desktop|mobile>-<caption>.png`;
  - log it with `python scripts/capture/log_capture.py <feature> <file> "<caption>"`.
- **Compile:** at the end of each milestone run `python scripts/capture/make_timelapse.py --all`; at the end, `--master`.
- Keep rejected art attempts and failed captures; never delete progress history.

## 20. Reporting, hosting and deliverables

- **Git:** a local repository whose history tells the story. Commit at every milestone and at least hourly; tags `m0`..`{{MVP_TAG}}`. The agent never pushes; the autodrive driver pushes `master` to `origin` ({{GITHUB_REMOTE}}) after each chunk.
- **Trailer per milestone:**
  - a Playwright-recorded cut (`e2e/trailer.spec.ts` with `playwright.trailer.config.ts`, then `python scripts/make_trailer.py`);
  - saved to `Docs/recording/trailer-<UTC ts>.mp4`, 60–120 s, captioned, showing only what is in the build.
- **Progress page:** `python scripts/build_site.py` builds `site-dist/`:
  - `/` the game;
  - `/trailer/` the newest trailers;
  - `/progress/` the plain-language build story from `Docs/progress_story.md` (CLAUDE.md §3b), plus overview stats, tokens (`scripts/token_usage.py`), Claude cost per chunk (`Docs/AUTODRIVE_LOG.md`), playtest scores, screenshots, videos, and a collapsed technical log (DEVLOG, decisions, reviews, commits).
- **Hosting:** `https://{{DOMAIN}}` on the owner's server {{SERVER_IP}} (root over ssh, nginx and certbot).
  - The one-time setup is in `deploy/README.md`.
  - Deploy at every green gate from M0 on with `DEPLOY_SSH={{SERVER_SSH}} bash scripts/deploy_server.sh`, which builds, uploads to `{{DEPLOY_DIR}}` and swaps atomically.
  - Then verify that the live bundle name matches `dist/`.
- **Autodrive log:** `Docs/AUTODRIVE_LOG.md`, one row per chunk (written by the driver).
- **`Docs/REPORT.md`** is kept up to date. It covers:
  - what works (implemented / agent-verified / pending owner review) and what doesn't;
  - numbers: wall time, Claude cost, paid asset spend, tokens, assets, LOC, commits;
  - playtest scores per gate;
  - the ten hardest problems and their solutions.
- **Also:** `Docs/COSTS.md`, `Docs/LICENSES.md`, the in-game Credits.

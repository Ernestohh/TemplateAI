# QUESTIONS.md — the setup questionnaire

Claude walks through these questions with the owner **before** filling a new project from the template (SETUP.md step 2). Ask them in this order, a few at a time, offering the typical options; the owner may pick one, combine them or answer freely. Unanswered questions take the **default** (marked ★) and get a line in `Docs/DECISIONS.md` ("owner did not specify; chose ... because ...").

Each question says what it fills:
- `project.json: KEY` is a simple placeholder that `scripts/fill_template.py` replaces everywhere;
- `TASK §n`, `STYLE`, `PLAN`, `TODO`, `REFS`, `DECISIONS` are rich FILL sections that Claude writes from the answers (Docs/TASK.md, Docs/STYLE_BIBLE.md, Docs/PLAN.md, Docs/TODO.md, Docs/refs/README.md, Docs/DECISIONS.md).

When all answers are in: write `project.json`, run the fill script, then write every rich section it lists, at the depth of the Zephyr examples in the comments. Finish with `python -I scripts/fill_template.py --check` showing no placeholders left.

---

## A. Identity

**A1. Name.** What is the game called? (Tempest, Nomad, Mirage, Eclipse, Monsoon, ...)
Fills: `project.json: GAME_NAME` (and the derived `GAME_SLUG`, `AUTODRIVE_ENV` such as `TEMPEST_AUTODRIVE`, `MODEL_ENV`, `DEPLOY_DIR`, `PROJECT_DIR_*`).

**A2. Pitch.** Describe the game in one paragraph (3-4 sentences, player-facing) and in one line.
- a) Claude drafts both from the answers to B-E, the owner approves ★
- b) The owner dictates them
Fills: `project.json: ONE_PARAGRAPH_PITCH`, `TAGLINE`, `TRAILER_LEDE`; README, the trailer page, /progress.

## B. Genre and core loop

**B1. Genre.** What kind of game is it?
- a) Turn-based tactics or party RPG roguelite ★ (proven in Zephyr)
- b) Idle / incremental with light active play (proven in Renegade)
- c) Deckbuilder or card battler
- d) Real-time light action (arena, twin-stick, auto-battler)
Fills: `project.json: GENRE`; TASK §0, §5; the playtest areas.

**B2. Core loop.** What does the player do every 10-60 seconds?
- a) Choose an action, see its preview, resolve it (turn-based) ★
- b) Place, build or upgrade, then watch it run
- c) Draft or play cards from a hand
- d) Move and react in real time
Fills: TASK §5 (core system with formulas), TASK §1 steps, `project.json: SIM_SYSTEMS`.

## C. Session structure

**C1. Session length and shape.**
- a) Runs of 12-20 minutes, roguelite: each run ends, meta carries over ★
- b) Endless idle progression with prestige/rebirth resets
- c) Short levels or missions of 3-5 minutes, chained into a campaign
- d) One long run of 30-45 minutes with acts
Fills: TASK §1 (MVP length), §10 (structure, pace target), §2 row "full session", harness bands in §18.

**C2. Failure.** What happens when the player loses?
- a) The run ends; meta progress always moves forward ★
- b) Lose units or resources for good, continue
- c) Retry the level, no loss
Fills: TASK §9 (loss rules), §11.

## D. Setting and theme

**D1. Setting.** Where and when does it take place?
- a) A folklore or mythology (pick one culture; public-domain figures welcome)
- b) Original fantasy world with a strong single motif (storm, desert, mirrors, eclipse, monsoon) ★ (matches the project name)
- c) Science fiction or post-apocalypse
- d) Historical with a light fantastic twist
Fills: `project.json: SETTING_SHORT`; TASK §0, §3 taboos, §12 working lists; STYLE inspiration and copy voice.

**D2. Tone.**
- a) Dark but beautiful (dread, loss, ornate) 
- b) Hopeful adventure with danger ★
- c) Cosy and calm
- d) Tongue-in-cheek / comedic
Fills: TASK §0; STYLE copy voice, avoid list.

**D3. Taboos.** Anything the setting must avoid (caricature, sensitive symbols, real religions, gore level)?
- a) Claude proposes a list from the setting, owner approves ★
- b) Owner lists them
Fills: TASK §3 "Respect and taboos"; STYLE forbidden list.

## E. Signature mechanics

**E1. Hooks.** Which 2-3 mechanics make this game itself? Each needs a state, a rule with numbers, a way to steer it, and a readable on-screen form.
- a) An environmental force that pushes the core system (Zephyr's Wind on the turn queue) ★
- b) A clock or phase cycle that changes risk and reward (Zephyr's Day/Dusk/Night)
- c) A hidden goal to uncover before the climax (Zephyr's boss needle)
- d) A build system with synergies (Renegade's procedural dao builds)
Fills: TASK §6, §7, §8 (titles and bodies), §0 bullets, §15 test-API cheats, §18 sim tests, STYLE motifs and reserved colours.

**E2. Characters.** Who does the player control or collect?
- a) A party of 3-4 recruited heroes with roles ★
- b) A single hero with a build
- c) A crew, army or sect of many units managed in aggregate
Fills: TASK §9 roster table, §12 content counts.

## F. Progression and meta

**F1. Between sessions.**
- a) A hub with a currency, ≥ 12 permanent upgrades and unlocks that change the next run ★
- b) Prestige / rebirth multipliers (idle style)
- c) A campaign map with unlocked levels
- d) None (pure score chasing)
Fills: TASK §11, §2 meta row, PLAN meta milestone.

**F2. Story.**
- a) Lore revealed in short fragments run by run, a hub character who remembers ★
- b) A linear story between levels
- c) Minimal: flavour text only
Fills: TASK §11, §12 (lore entities), STYLE copy voice.

## G. Art style

**G1. Look.** What should it look like? (One clear art tradition beats a mix.)
- a) Flat illustrated, bold outlines, limited palette (print or poster tradition) ★
- b) Ornate decorative chrome with jewel colours (lacquer, stained glass, illumination)
- c) Clean minimal vector with one accent colour
- d) Pixel art at a fixed scale
Fills: TASK §4 (style name and summary), the whole STYLE bible (surfaces, palette, shapes, illustration rules, icons, motion), TODO T15 concept sheet.

**G2. Fonts.** Display font flavour?
- a) Claude proposes 3 OFL fonts that fit the setting, verified on npm ★
- b) Owner names fonts
Fills: STYLE font table; DECISIONS line with licences.

## H. Audio

**H1. Music.**
- a) CC0 / CC-BY tracks per context, instrumentation that fits the setting ★
- b) Procedural Web Audio drones only
- c) No music in the MVP
Fills: TASK §14 music contexts and instrumentation, §2 audio row.

**H2. SFX.** Procedural Web Audio per cue ★ (default; no files). Claude derives the cue list from the core loop and the hooks.
Fills: TASK §14 SFX cue list.

## I. Budget

**I1. Paid generation budget (USD).**
- a) 0 USD: hand-authored and procedural SVG, free licensed assets ★
- b) 10-25 USD with a primary image provider for key art only
- c) Larger: name the providers and caps
Fills: `project.json: BUDGET_USD`; with a paid budget also TASK §16 paid providers (otherwise delete that marker). CLAUDE.md §6 already covers both cases.

## J. Devices

**J1. Device priority.**
- a) Desktop first (1440×900, mouse and keyboard), fully playable on a phone in portrait (390×844) ★
- b) Phone first, portrait, one-thumb play
- c) Desktop only (drop the phone acceptance row and the 390 px gate check, with a DECISIONS line)
Fills: TASK §13 devices and controls, §2 phone row.

## K. MVP scope

**K1. The MVP slice.** What is the smallest complete version worth playing?
- a) One full act / run of 12-15 minutes with one boss, polished ★
- b) The first 30 minutes of an idle game with one prestige
- c) A campaign of 5 short levels
Fills: TASK §1 (named slice and 8-12 steps), §2 priorities, rows and post-MVP list, §17 milestones, PLAN table and sections, `project.json: MVP_MILESTONE`, `MVP_TAG`, `LARGE_GATES`, `ACCEPTANCE_FROM`.

**K2. Milestones.** How many?
- a) M0-M7 like Zephyr: scaffold, sim core, first playable, then one per pillar, art/audio last ★
- b) Fewer, larger milestones (M0-M5)
Fills: TASK §17, PLAN, `LARGE_GATES` (default "M2, M5 and M7": first playable, the climax, the MVP).

**K3. Content counts.** How much content for the MVP? Claude proposes counts per entity (Zephyr: 4 heroes, ≥ 12 enemies, 1 boss, ≥ 15 events, ≥ 16 relics, ≥ 12 upgrades, ≥ 10 lore fragments) ★
Fills: TASK §12 table and working lists, §2 content-counts row.

## L. Run mode

**L1. How does it run?**
- a) Autodrive from day 1: fresh `claude -p` chunks, HANDOFF entries, driver pushes after each chunk ★
- b) Interactive session first (owner watches M0), then autodrive
Fills: DECISIONS; SETUP.md step 7. (The template supports both; autodrive is the default.)

**L2. Model.** Which model for the chunks?
- a) The default model of the Claude Code install ★
- b) A specific model via `<SLUG>_MODEL` (for example a large model for the first, planning-heavy chunk)
Fills: SETUP.md step 7 command (env variable), DECISIONS.

**L3. Chunk length.** `CHUNK_MAX_MIN` hard limit per chunk: 150 minutes ★, or shorter (90-120) for cheaper chunks.

## M. Reporting

**M1. What does the owner want to see?**
- a) The plain-language /progress page, a trailer per milestone, GitHub commits ★
- b) Also timelapse videos per feature (already part of the gates)
- c) Minimal: REPORT.md and GitHub only
Fills: DECISIONS; TASK §20 stays as is unless (c).

## N. References

**N1. Which games or works should it feel like?** 4-8 references, each with what to learn from it (never copy assets, names or text).
- a) Claude proposes references from the genre answers, the owner trims ★
- b) The owner lists them
Fills: TASK §0 references table, REFS study table and art traditions, STYLE inspiration (described, never named in prompts).

**N2. Reference images.** Does the owner have images to put in `Docs/refs/` or approved concepts for `Docs/concepts/approved/`?
- a) None yet; the first concept sheet comes in M0 ★
- b) Yes: the owner copies them in and Claude describes each in `Docs/refs/manifest.json`

## O. Hosting, ports and repository

**O1. Domain.** Default `<slug>.kryptos.gg` on 72.62.17.59 ★, or another subdomain.
Fills: `project.json: DOMAIN`, `SERVER_IP` (and the derived `DNS_ZONE`, `SERVER_SSH`, `DEPLOY_DIR`). The owner creates the DNS A record (SETUP.md step 4).

**O2. Ports.** Take the project's row in `PORTS.md` ★ (Tempest 5373/4373, Nomad 5473/4473, Mirage 5573/4573, Eclipse 5673/4673, Monsoon 5773/4773), or the next free pair for a new name.
Fills: `project.json: DEV_PORT`, `PREVIEW_PORT`.

**O3. GitHub remote.** Default `https://github.com/Ernestohh/<Name>.git` ★ (HTTPS: this PC has no GitHub SSH key). Does the repository exist already?
- a) The owner creates an empty repo on GitHub first ★
- b) It exists and is empty
Fills: `project.json: GITHUB_REMOTE`; SETUP.md step 3.

**O4. Server setup.** Who runs the one-time nginx/certbot setup?
- a) The owner, during setup (SETUP.md step 5) ★
- b) The run, in M0 (TODO T17)
Fills: TODO T17 (keep or mark done), DECISIONS.

# PLAN.md
Current milestone: **M0 Scaffold and verification harness** (not started; the first autodrive chunk starts it).

Spec: Docs/TASK.md (sections 17, 18). The queue lives in Docs/TODO.md.

Rules for this plan:
- Status words are **implemented**, **agent-verified** and **pending owner review**.
- A milestone is done only when its gate is green and logged.
- Large-model gates (review and playtest on the large model) are {{LARGE_GATES}}.
- From M0 on, every gate includes:
  - captures at 1440 and 390;
  - a fresh-context playtest with scores (from M2, when there is something to play);
  - a trailer (from M2);
  - a deploy.

| Milestone | Status | Gate |
|---|---|---|
| M0 Scaffold and verification harness | not started | `npm run check` green; first captures at 1440x900 and 390x844; site builds and deploys (placeholder); tag m0 |
| M1 Sim core | not started | Sim tests + determinism green; harness runs 200 seeded sessions/encounters, no NaN, no softlock; tag m1 |
| {{FILL: PLAN milestone table rows M2..MVP}} | | |

<!--
One row per milestone from TASK.md §17, same names. Gates name the acceptance rows they must pass, the large-model
review + fresh playtest where it applies ({{LARGE_GATES}}), trailer, deploy and the tag.
Zephyr rows:
| M2 First playable battle | not started | Gold path (battle) green at both viewports; acceptance rows 2-4 pass; **large-model review + fresh playtest**; trailer; deploy; tag m2 |
| M3 Dungeon crawl and day/night | not started | Acceptance run #1 (rows 1-6, 12); playtest; trailer; deploy; tag m3 |
| M7 Art and audio pass (MVP) | not started | **MVP gate:** all P0 rows green at both viewports; budgets met; **large-model review + fresh playtest**; trailer; deploy; tag m7 + mvp |
-->

## M0 Scaffold and verification harness

**Docs:**
- `Docs/ARCHITECTURE.md`: sim/content/ui/audio/dev split, the state shape, RNG streams, save format, test API, fixtures.
- `Docs/MAP.md`: screen flow, layouts at 1440x900 and 390x844, fixed capture states.
- The style bible finalised against the first concept sheet.

**Scaffold:**
- Vite + TS strict + Preact + zod + Vitest + Playwright + ESLint.
- Dev port {{DEV_PORT}} and preview port {{PREVIEW_PORT}}, `strictPort` (PORTS.md).
- `npm run check`.

**Code:**
- Seeded RNG with named streams; a state skeleton; `data/tuning.json` with its schema; `validate-data`.
- `window.__{{GAME_SLUG}}` with `loadFixture`.
- Debug panel: seed, speed, fixture picker.

**Harness and tests:**
- The capture spec and the first capture (title, both viewports).
- Gold-path and acceptance skeletons that write their JSON/report.
- A harness skeleton.

**Site:** fonts installed (OFL) and logged; `build_site.py` works; the one-time server setup; the first deploy of the placeholder; the `/progress/` page.

## M1 Sim core

{{FILL: PLAN M1 detail}}
<!-- All headless, in src/sim/ with tests: the core model of TASK.md §5 with its formulas, the signature mechanics of
     §6-§7 as far as the core needs them, data schemas and the first data, the harness in encounter mode.
     Zephyr: timeline, queue prediction and preview, effects, rounds, wind, combat rules, enemy AI, 2 heroes + 4 enemies,
     harness battle mode. -->

{{FILL: PLAN milestone sections M2..MVP}}
<!-- One "## Mx Name" section per milestone with 4-8 bullets grouped by bold labels (Screen, Systems, Content, Saves,
     Difficulty, Gate). The last one is the art and audio pass and the MVP gate. Zephyr M5:
     ## M5 Boss and the needle
     - **Boss:** Leshy with 3 phases; deathless reforms and Wrath.
     - **The needle chain:** 3 clue rooms placed off the main path; rumours; night reveal; the hare chase; the egg choice.
     - **The kill:** the Break-the-needle action and its fairness measured by the harness.
     - **Gate:** large-model review + playtest. -->

## After the MVP (do not start before the {{MVP_MILESTONE}} gate is green)

{{FILL: PLAN post-MVP list}}
<!-- Numbered: 1 P1 rows by value, then the post-MVP list of TASK.md §2 in order. -->

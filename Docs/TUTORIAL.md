# TUTORIAL.md: the living tutorial ({{GAME_NAME}})

Owner request, 2026-10-11: every game has a tutorial, and every new mechanic or feature updates it.

Build the tutorial skeleton together with the first playable build. From then on, every new mechanic ships with its tutorial entry.

## What the tutorial is
1. **First-run guided tutorial.**
   - Short and skippable, replayable from Settings.
   - Teaches the core loop step by step in the real UI: it highlights the actual element, explains one thing at a time and waits for the player to do it.
   - No walls of text: at most 2 short sentences per step.
   - Finishable in 2-5 minutes.
2. **"How to play" page.**
   - Reachable from the main menu or HUD at any time.
   - One entry per mechanic: a plain-language title, 2-4 short lines (what it is, how to use it, why it matters) and one small picture or diagram.
   - Entries unlock as the player meets each mechanic; a NEW badge shows on unread entries.
3. **Contextual first-time tips.** The first time a mechanic appears (a new screen, enemy rule or resource), show a one-line tip that links to its How-to-play entry. Each tip shows only once and can be turned off in Settings.

## How it is built
- Content is data: `data/tutorial.json` (validated by the project's schema).
  - Guided steps: target element selector or test id, text, and the completion condition.
  - Entries: id, title, body, image, unlock trigger.
  - Tips.
- Plain language, following the same writing rules as `Docs/progress_story.md`: no internal codes or jargon.
- The tutorial runs on the normal game state, never a separate fake mode.
- It must stay correct when balance numbers change: read the numbers from data instead of hard-coding them in text.

## The rule that keeps it current (non-negotiable)
- **Every commit that adds or changes a mechanic or feature also adds or updates its tutorial entry.** That includes tips, guided steps if the core loop changes, and the How-to-play entry.
- **A coverage test fails** when a mechanic in the game data has no tutorial entry. Mechanics include resources, stances, systems, building types, card keywords, puzzle elements, path moves and so on: whatever the project's data defines as player-facing. Add the test with the first tutorial commit, and extend it as new data kinds appear.
- **At every milestone gate:**
  - the fresh playtester starts a new game and completes the guided tutorial;
  - the reviewer checks that every new mechanic since the last gate has an entry that a newcomer understands;
  - both report this in their review.
- **Acceptance:** a fresh player completes the guided tutorial without help, and How-to-play covers 100% of player-facing mechanics according to the coverage test.

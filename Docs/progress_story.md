<!--
Writing rules for this file. It is the owner's /progress page, rendered by scripts/build_progress.py.
- The reader is the owner, who is not technical. Write short sentences in the active voice.
- No internal codes in the text: milestone ids (M3), review ids (r4), hashes, test or balance jargon.
- Use numbers only when they help, rounded and explained ("fights take about 20 seconds now").
- One card per milestone: plain title, date, one sentence on what changed for a player, 2-4 bullets, optional "why" line, one screenshot path.
- Be honest: keep "Not perfect yet" current.
-->
<!--
progress_story.md: the human story behind https://{{DOMAIN}}/progress/
scripts/build_progress.py renders this file. Keep the format below so the page builds.

FORMAT
- "## Section" starts a section. The builder looks these titles up by name:
  At a glance, {{GAME_NAME}} in one paragraph, What you can do in the game now, Not perfect yet,
  Milestones, How the reviewers scored it over time, How it was built, Glossary, Gallery.
- Text blocks: blank-line separated paragraphs, "- " bullets, "| a | b |" tables,
  **bold**, *italic*, [link](url). HTML comments are ignored.
- At a glance: one bullet per fact, "- **big value** | short label".
- What you can do in the game now: "### Group name", then bullets.
- Milestones: one "### Card title" per card, then these lines (any order):
    Date: 10 Oct 2026, 00:42 UTC
    Image: Docs/path/to/shot.png | Docs/fallback.png   (first file that exists is used)
    Why: one plain sentence (optional)
  then one sentence on what changed for a player, then 2-4 bullets.
- Gallery: "- Docs/path.png | caption". At most about 24 images.
- Glossary: "- **Term**: plain definition". At most 8 terms.
- Placeholders filled by the builder from git, Docs/STATS.json and Docs/TOKENS.json:
  {hours} {commits} {tokens_all} {tokens_fresh} {cache_pct} {tokens_date}

WRITING RULES: plain English, short sentences, no internal codes (milestone ids, review ids,
commit hashes, build ids). Facts only from Docs/REPORT.md, PLAN.md, DEVLOG.md,
DECISIONS.md and the reviews. Keep known limits honest under "Not perfect yet".

Example milestone card (from an earlier run):
### The foundation is laid
Date: 10 Oct 2026, 23:16 UTC
Image: Docs/progress/title/20261010-231203__title-desktop-m0-first-title.png
Why: everything later is built on this, and it is checked automatically every time something changes.
There is no game yet, but the website is live and shows the title screen on computers and phones.
- The game now opens at its own web address with its own colours and lettering.
- A first art sheet sets the look.
- Every change now runs about 30 automatic checks before it is saved.
-->

# {{GAME_NAME}}: how the game was made

## At a glance
- **{hours} h** | of autonomous work so far
- **{commits}** | saved steps in the project history

## {{GAME_NAME}} in one paragraph
{{ONE_PARAGRAPH_PITCH}} (Filled in properly when the first playable build exists.)

## What you can do in the game now
### Nothing yet
- The game is being set up. The first screen arrives with the first milestone.

## Milestones

## How the reviewers scored it over time
Fresh testers who never saw the game play every milestone and score it from 1 to 10. Their scores appear here from the first playable build on.

## How it was built
Claude built {{GAME_NAME}} on its own, in work sessions of one to two hours that each start fresh and pick up from written notes. It has used {tokens_all} tokens so far (as of {tokens_date}); about {cache_pct} of them were re-reading notes it already had.

## Not perfect yet
- Everything: the work has just started.

## Glossary

## Gallery

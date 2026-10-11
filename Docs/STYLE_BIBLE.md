# STYLE_BIBLE.md — "{{FILL: STYLE style name}}" (first draft)

**Status: first draft, written at setup.** There are no owner-approved concepts yet (`Docs/concepts/approved/` holds only a README). This page and TASK.md §4 are the visual target until the owner approves something. M0 finalises it with the first concept sheet in `Docs/concepts/proposed/`. Every visual stays **pending owner review**.

<!--
TEMPLATE NOTE {{FILL: delete this TEMPLATE NOTE comment}} Claude writes this file from QUESTIONS.md "Art style", "Setting and theme" and
"References". Keep every section below; a filled draft is roughly 150-180 lines. Use exact hex values, font package
names, pixel sizes and durations, so agents can follow it without judgement calls. The examples in the comments set the depth.
-->

**Inspiration (describe, never name in prompts or files):**
{{FILL: STYLE inspiration}}
<!-- 2-4 bullets naming art traditions or qualities, not products. Example: "Russian lubok folk prints: woodcut outlines,
     flat hand-tinted colour, caption ribbons" / "Palekh lacquer miniatures: jewel-like figures on deep black, fine gold
     hatching". Then one line on the tone ("beautiful and ornate, but the forest is dangerous"). -->

## Surfaces

{{FILL: STYLE surfaces table}}
<!-- | Surface | Where | Look | — usually 1-2 surfaces (the UI chrome and the illustrations).
     Example: | **Lacquer** | HUD, battle stage, map, hub, menus | Deep black lacquer ground, thin gold lines, jewel-colour figures, vermilion for action and danger. |
             | **Lubok** | Room, event and death cards, lore pages | Warm paper ground, bold black outline, flat hand-tinted fills, a caption ribbon. |
     Add the rule for how they combine ("a lubok card always sits inside a lacquer frame"). -->

## Keep
{{FILL: STYLE keep}}
<!-- 4-7 bullets. Example: gold and vermilion on deep black; flat bold colour; ornate borders only on big frames; large legible numbers; one portrait family; one icon family. -->

## Upgrade
{{FILL: STYLE upgrade}}
<!-- 4-7 bullets of motion and juice with durations. Example: card flip on room entry (3D, 320 ms); wind streaks across the queue; tokens slide when the preview changes; a seal stamp on big moments. -->

## Avoid
- Clutter.
- Text under 13 px.
- Glossy bevels, drop-shadow soup, generic stock art.
- Mixed icon styles.
- Lore walls (≤ 2 short sentences per text block outside dedicated lore screens).
{{FILL: STYLE avoid extras}}
<!-- Setting-specific avoids. Example: photographic textures; neon and purple-gradient fantasy; faux-Cyrillic. -->

**Forbidden symbols and content.** {{FILL: STYLE forbidden list}}
<!-- What must never appear, even as ornament, plus a list of safe ornament. Example: the kolovrat or any swastika-derived
     solar wheel, "Slavic runes" sets, the black sun; safe: rosettes, vines and berries, birds, stars, waves, fir branches. -->

## Palette (CSS tokens in `src/ui/theme.css`)

| Token | Hex | Use |
|---|---|---|
| {{FILL: STYLE palette tokens}} | | |

<!-- 15-25 tokens: backgrounds (3-4 steps), panel, line, 2-3 accent families with text-safe variants, text primary/
     secondary/disabled, illustration tints, one colour reserved per signature mechanic.
     Example rows: | `lacquer-900` | `#0b0a0c` | app background | / | `gold` | `#d4a53c` | frames, titles, party rings | /
     | `vermilion-text` | `#ef6a50` | vermilion text on black (≥ 4.5:1) | / | `azure` | `#5b9bd6` | wind only | -->

**Semantic rules:**
{{FILL: STYLE semantic colour rules}}
<!-- What each important value looks like, and which colours are reserved. Example: HP is vermilion-to-ochre; Breath is
     gold pips; wind is always azure and nothing else is azure; party is gold, enemies vermilion; one colour and one icon
     per damage kind. -->

**Contrast:**
- body text ≥ 7:1 on the panel colour;
- secondary text ≥ 4.5:1;
- illustration text (if any surface has dark-on-light text) ≥ 12:1.
- M0 adds a contrast check script for the token pairs used for text.

## Typography (SIL OFL 1.1, self-hosted via `@fontsource/*`, Latin subsets only)

| Role | Font | Notes |
|---|---|---|
| {{FILL: STYLE font table}} | | |

<!-- 3-4 roles: logo/display, headings and names, UI body and numbers (must have tabular figures, name a fallback),
     optional lore font. Verify each licence on npm before writing it here.
     Example: | Logo, titles | **Ruslan Display** (`@fontsource/ruslan-display`) | ≥ 32 px only, uppercase |
             | UI body, numbers | **PT Sans** (`@fontsource/pt-sans`, 400/700) | tabular-nums; fallback Fira Sans | -->

**Sizes:** body 15 px, small 13 px (minimum), HUD numbers 18 px, popups 28–40 px, titles 32–64 px. (Adjust with a DECISIONS line.)

**Budget:** ≤ 4 font files in the initial load, ≤ 200 KB in total. Log every font in `Docs/LICENSES.md` and in Credits.

## Shapes and proportions

{{FILL: STYLE shapes and proportions}}
<!-- Panels (fill, border, radius), big frames, the main card or tile format with its aspect ratio, buttons (primary/
     secondary/disabled, min height 40 px, 44 px on touch), the signature UI element (example: the turn-queue rail with
     ≥ 10 medallion tokens, 40 px desktop / 32 px phone), portraits, the map, spacing scale 4/8/12/16/24/32, max width. -->

## Illustration rules

{{FILL: STYLE illustration rules}}
<!-- Per surface: viewBox, outline weight, fills, max colours (≤ 6 plus one accent), composition rules, the silhouette
     test at phone size, which pieces are procedural. Example (lubok cards): viewBox 500×350, ink outline 3–4 px, flat fills,
     ornamental patterns instead of shading. -->

## Icons

- **UI icons:** 24×24 viewBox, 1.75 px stroke, round caps and joins, `currentColor`, no fills except small accent dots.
{{FILL: STYLE icon families}}
<!-- Game-specific icon families with their frames. Example: damage kinds 32×32 in a circle, traits in a diamond, room types in a rounded square. -->

## Motifs

{{FILL: STYLE motifs}}
<!-- 3-6 recurring visual motifs tied to mechanics. Example: the firebird feather (currency); the needle chain as six HUD icons; the three riders; the hut on chicken legs (hub and logo); azure wind streaks. -->

## Motion

- UI transitions 150–250 ms ease-out.
- Damage or value popups 600 ms (rise and fade).
- Big-moment cards ≤ 2 s, skippable.
- A speed setting (1×/2×/3×) scales all gameplay animations.
- With `prefers-reduced-motion` and the in-game setting: no flips (cross-fade instead), no shake, no shimmer.
{{FILL: STYLE motion extras}}
<!-- Game-specific animations with durations. Example: card flip 320 ms; queue token slide 220 ms; phase-change card ≤ 1.6 s. -->

## Copy voice

{{FILL: STYLE copy voice}}
<!-- 2-3 sentences: tone, sentence length, an example line, how setting terms are glossed, the max length of feedback text.
     Example: "Short, concrete, a little ominous, with folk-tale cadence ('Beyond the third birch the path forgets you.').
     Battle text is ≤ 6 words ('The wolf is delayed!')." -->

---
name: ui-from-mockup
description: Use when building a front-end screen or HUD (the screens listed in TASK.md section 13) from a mockup or concept sheet.
---
# UI from mockup

1. Open the mockup (`Docs/concepts/approved/`, otherwise the newest sheet in `Docs/concepts/proposed/`), the `Docs/MAP.md` layout for the screen, and the style bible.
2. List the elements (frames, buttons, tokens, bars, text, icons, ornaments) and the states: hover, focus, pressed, disabled, selected, previewed, empty, loading, error, reduced motion, plus any game-specific state (for example a night tint).
3. Build with the UI stack of TASK.md section 15 (default: Preact + CSS):
   - use the palette tokens in `src/ui/theme.css`;
   - make ornaments SVG components (nine-slice-like corners plus repeating edges);
   - use no hard-coded pixel positions that break at other sizes.
4. Lay out for 1440x900 first and for 390x844 in the same pass:
   - follow the phone layout rules in `Docs/MAP.md` (for example: the main action menu becomes a bottom sheet);
   - tap targets ≥ 44 px;
   - long-press shows tooltips;
   - no horizontal scroll from 360 px.
5. Capture the fixed state at both viewports and compare side by side with the mockup. Then ask the `reviewer` agent to score it.
6. Check: text overflow (long names), focus order and keyboard shortcuts, contrast (style bible ratios), numbers in tabular figures, reduced motion.

---
name: asset-pipeline
description: Use when producing any visual asset (illustration, portrait, icon, frame, ornament, logo, background). Concept first, attempt limits, size budgets, provenance; zero-budget route is hand-authored or code-generated SVG.
---
# Asset pipeline (budget {{BUDGET_USD}} USD; see CLAUDE.md section 6)

1. **Read first.** Open `Docs/STYLE_BIBLE.md` and any matching image in `Docs/concepts/approved/`. Choose the surface or style family the style bible assigns to this kind of asset.
2. **Concept sheet first.** Author 1–3 small variants as SVG. Render them to a contact sheet PNG in `Docs/concepts/proposed/<batch>-v<n>.png` (Playwright screenshot of an HTML page that lays the SVGs out on the target background). Check the sheet against the style bible before producing the batch.
3. **Produce.** Build every asset to the same grid and stroke rules:
   - viewBox and line weights as the style bible says;
   - palette tokens only (≤ 6 colours plus gold per illustration);
   - no embedded raster images;
   - no text baked into art; titles are live text in the UI.

   Repeating motifs (borders, foliage, stars, particles) may come from a small seeded generator script in `scripts/assets/`. Commit the script so the output can be reproduced.
4. **Optimise.** Round coordinates to 1 decimal, remove metadata and unused defs, and reuse `<symbol>`/`<use>` for repeats. Check the size against TASK.md §15 (the per-kind limits listed there).
5. **Provenance.** Write `asset.json` in the batch folder under `assets/generated/<kind>/` (fields as in `scripts/assets/asset.json.example`; route `authored-svg` or `procedural`). Validate with `python -I scripts/assets/validate_asset.py`.
6. **External files** (fonts, the odd texture):
   - permissive licence only;
   - store under `assets/external/<source>/`;
   - a row in `Docs/LICENSES.md` and in the in-game Credits;
   - asset.json with route `external`, the source URL and the licence.
7. **Attempts.** Max 3 per asset at the same stage; then simplify (fewer shapes, a geometric version) and log it. Keep rejects under `_rejected/` with a one-line reason in asset.json.
8. **Hand-off.** Add an item to `Docs/INTEGRATION_QUEUE.md` and a short note in `Docs/lanes/art-<batch>.md`. Capture the integrated result (progress-capture skill).
9. **Never:**
   - brand, franchise or reference-game names in file names, notes or prompts;
   - traced or ripped art;
   - anything on the style bible's forbidden list.

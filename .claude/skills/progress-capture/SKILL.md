---
name: progress-capture
description: Use whenever you finish a significant UI change or every 10 minutes while working on a visible feature; saves fixed-state screenshots at desktop and phone size and logs them for timelapses and the progress page.
---
# Progress capture

- Capture the fixed state of the feature you are working on, defined in `Docs/MAP.md` and loaded with `window.__{{GAME_SLUG}}.loadFixture(name)`:
  - after every significant change and at least every 10 minutes;
  - at 1440x900 and at 390x844.
- Use the capture spec: `npm run capture` (Playwright, `playwright.capture.config.ts`, preview on port {{PREVIEW_PORT}}).
- File: `Docs/progress/<feature>/<UTC yyyymmdd-HHMMSS>__<screen>-<desktop|mobile>-<short-caption>.png`.
- Log every file: `python scripts/capture/log_capture.py <feature> <file> "<caption>"`. It appends to `Docs/progress/log.jsonl`.
- Never move a fixed capture state; add a new one for a new feature.
- At the end of each milestone: `python scripts/capture/make_timelapse.py --all`. At the end of the run: `--master`.
- Open at most the one capture that decides something. Reviewer agents look at the rest (token discipline).

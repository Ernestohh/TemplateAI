---
name: independent-review
description: Use after each milestone or big UI/art batch to get an independent, fresh-context scoring of the latest captures against the style bible and approved concepts. Run it in a separate sub-agent (reviewer), never self-grade.
---
# Independent review

Run it in a fresh-context agent (`reviewer`). Inputs:
- the newest captures in `Docs/progress/` (desktop and mobile) and `Docs/goldpath/`;
- `Docs/concepts/approved/` and `Docs/refs/`;
- `Docs/STYLE_BIBLE.md`.

Steps:
1. Open every capture you will mention. Never describe an image you have not opened.
2. For each area of TASK.md §2 that has a visible surface, give a 1–10 score for clarity, readability, visual consistency and feel against the style bible and the approved concepts. Readability is judged at both viewports.
3. List the three worst defects, each with the capture's file path and a concrete fix.
4. Write the result to `Docs/reviews/<UTC yyyymmdd-HHMM>-<milestone>-review.md`, with a verdict line (PASS / PASS WITH DEFECTS / FAIL).
5. The integrator adds the defects to `Docs/TODO.md` above new features.

Use the large model at the {{LARGE_GATES}} gates.

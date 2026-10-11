---
name: release-build
description: Use at every green milestone gate and for the MVP - build, smoke-test, cut the trailer, build the site and deploy to {{DOMAIN}}.
---
# Release build and deploy

1. Make the verification path green on the current commit (`npm run check`; from {{ACCEPTANCE_FROM}} on also `npm run acceptance`), with zero console errors.
2. `npm run build`. Check the budgets: initial JS < 250 KB gzip, fonts ≤ 200 KB, initial page < 1.5 MB (TASK.md §15).
3. `npm run preview` (port {{PREVIEW_PORT}}). Run the smoke path at 1440x900 and 390x844 and capture both.
4. Cut the trailer:
   - `npx playwright test -c playwright.trailer.config.ts`, then `python scripts/make_trailer.py`, which writes `Docs/recording/trailer-<ts>.mp4`;
   - confirm with ffprobe that the file plays and lasts 60–120 s;
   - show only what is in the build.
5. Build the site: `python -I scripts/token_usage.py`, then `python scripts/build_site.py` (game `/`, `/trailer/`, `/progress/`).
6. Deploy:
   - `DEPLOY_SSH={{SERVER_SSH}} bash scripts/deploy_server.sh`;
   - compare the live bundle name with `dist/assets/index-*.js` (the script prints the curl command).
   - First time only: `bash scripts/server_setup.sh` (deploy/README.md). If DNS is not set, log it in DECISIONS and leave it to the owner.
7. Tag the commit and update REPORT.md, STATS.json, LICENSES.md and the Credits screen. Record the steps in `processes/release/`.

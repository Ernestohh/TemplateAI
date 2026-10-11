# Build and deploy checklist

1. Make sure the working tree is clean (`git status`) and the verification path is green.
2. Run `npm run build` and check the size budgets (TASK.md §15).
3. Run `npm run preview` ({{PREVIEW_PORT}}) and do the smoke path at 1440x900 and 390x844.
4. Cut the trailer at gates: `npx playwright test -c playwright.trailer.config.ts`, then `python scripts/make_trailer.py`.
5. Run `python -I scripts/token_usage.py`, then `python scripts/build_site.py`.
6. Run `DEPLOY_SSH={{SERVER_SSH}} bash scripts/deploy_server.sh` and check that the live bundle name matches `dist/`.
7. Tag the commit and update REPORT.md and STATS.json.

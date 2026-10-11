# Gold-path driver design

- **What it is:** a Playwright spec (`e2e/goldpath.spec.ts`), started by one short call (`npm run e2e:goldpath`). The preview runs on port {{PREVIEW_PORT}}.
- **Steps** mirror TASK.md §1. It uses a fixed seed and a speed setting, and asserts pacing in sim time.
- **At each checkpoint:** a screenshot (`NN-<name>.png`) and state values via `window.__{{GAME_SLUG}}.getState()`.
- **Robustness:**
  - clear only visible modals;
  - two quiet checks before acting;
  - short-timeout clicks with retries;
  - `actionTimeout` 10 s.
- **Output:** `Docs/goldpath/<UTC yyyymmdd-HHMMSS>/{checks.json,*.png}`, written atomically (temp file, then rename). The caller reads the file when the run finishes.
- **checks.json schema:** `{"passed":bool,"checks":[{"name","ok","value","expected"}],"fps":{"avg","min"},"console_errors":int,"missing_refs":int}`.
- **Phone variant:** the same path on the 390x844 project with `hasTouch`.
- **Harness counterpart:** `scripts/harness.ts` writes `Docs/goldpath/<ts>-sim/checks.json` with the same schema (minus fps).
- **Acceptance:** `scripts/acceptance.ts` runs tests, harness, build, gold path, `e2e/acceptance.spec.ts` (per-row checks) and the a11y/soak specs. It maps the results to the TASK.md §2 rows and writes `Docs/acceptance/<ts>/report.md`. A row that depends on the gold path fails if the gold path did not complete.

---
name: verification-driver
description: Use to run or extend the automated end-to-end path (the gold path), the simulation harness and the acceptance test that prove the MVP still works after a change.
---
# Verification driver

Three layers (TASK.md §18). Each one writes a JSON result atomically (temp file, then rename):

- **Harness** (`npm run harness`; `--quick` inside `npm run check`):
  - scripted players (good, careless, random) play the MVP loop headlessly on fixed seeds;
  - it asserts the bands in TASK.md section 18 (win rates or progress pace, session length from the time model), no softlock, no NaN;
  - output: `Docs/goldpath/<ts>-sim/checks.json`.
- **Gold path** (`npm run e2e:goldpath`):
  - Playwright plays TASK.md §1 through the real UI, with real clicks, a fixed seed and the speed setting;
  - pacing is asserted in sim time;
  - output: `Docs/goldpath/<ts>/checks.json` plus `NN-<checkpoint>.png`;
  - schema: `{"passed":bool,"checks":[{"name","ok","value","expected"}],"fps":{"avg","min"},"console_errors":int,"missing_refs":int}`.
  - A phone project (390x844, `hasTouch`) runs the same path at gates.
- **Acceptance** (`npm run acceptance`): runs everything above plus `e2e/acceptance.spec.ts` (per-row checks) and writes `Docs/acceptance/<ts>/report.md` with one row per TASK.md §2 line.

Rules:
- Start with one short call in the background and read the result file when it finishes. No poll loops in the main loop.
- Ports: preview {{PREVIEW_PORT}} (`reuseExistingServer: true`, `strictPort`). Never another project's ports (PORTS.md); other runs share this machine.
- Pass means every check is true, zero console errors and zero missing references.
- Driver robustness:
  - clear only *visible* modals;
  - require two quiet checks before acting;
  - use short-timeout clicks with retries;
  - set `actionTimeout` to 10 s;
  - wait loops key on this run's output folder, never on a glob.
- If it fails and the fix is not obvious within 20 minutes, revert the change and re-queue it.
- Change the driver only at milestone boundaries, in its own commit.

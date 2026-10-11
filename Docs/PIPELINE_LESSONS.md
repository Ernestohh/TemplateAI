# PIPELINE_LESSONS.md

Lessons from earlier agent runs (carried over from the previous web-game run) and from this one. Read the relevant section before touching that area. Append new lessons as you learn them: date, tool, symptom, cause, fix.

The token discipline rules are in CLAUDE.md §1c (they are rules, not just lessons).

## Tool bridges / MCP
- A bridge timeout during a long operation (build, install, test run) is often an operation that already succeeded. Check the state; do not retry blindly.
- Hung calls: look for a hidden modal dialog (or a browser dialog in the Playwright MCP) first.
- Keep the app in a mode that is not throttled when unfocused, or screenshots go stale.
- Only one agent drives the Playwright MCP browser at a time.

## Shell (Git Bash on Windows)
- Bash heredocs containing JSX, backticks or quotes often fail to parse ("unexpected EOF"). Write files and patch scripts with the Write tool and run them with python.
- `cmd | grep ...` or `| tail` hides the exit code. Capture `$?` / `${PIPESTATUS[0]}`, or use scripts/commit_green.sh.
- Never chain a plain `git commit` after an edit or lint step on a separate line of the same Bash call: a failed `&&` chain stops, but the next line still runs. Commit only via scripts/commit_green.sh.
- Timestamps in DECISIONS, PLAN and DEVLOG must come from `date -u` at write time. Estimates drifted 4–8 minutes during long waits.
- Console output on Windows is cp1252: keep driver and script output plain ASCII.
- Kill processes by PID only, and only your own (other runs share this machine, PORTS.md).

## Verification (Playwright, harness)
- Screenshots and numbers each catch bugs the other misses; use both.
- Synthetic input events must land on separate frames. Always restore real devices and viewport after automated tests.
- Gold-path flakiness came from UI races: modals opening between reading state and clicking (fast-forwarded time), modals deferred while animations run. To avoid it:
  - clear only *visible* modals;
  - wait for celebrations to finish;
  - use short-timeout clicks with retries;
  - require two quiet checks in a row before acting.
- A Playwright `actionTimeout` of 10 s stops a single stuck click from eating the whole test timeout.
- Engine rules must not rely on the UI. A scripted player once reached an invalid state (an event started a fight that replaced a running fight, softlocking the run). Fix such rules in the sim (refuse the action, never replace a running encounter, self-heal), not only in the UI.
- Wait loops must key on the specific run's output folder, not a glob that an earlier run already satisfies.
- Don't run CPU-heavy gates while a timing-sensitive soak or FPS measurement is sampling. On this PC another run may be busy too, so re-measure solo before calling a drop a regression.
- Capture batches: a fixture load is occasionally lost deep in a long batch. Retry the fixture once in the capture spec; suspects are pagehide autosave vs storage clears, and the service worker.
- A long-running wave or animation can outlast a test loop's budget. Size loops by sim time, not by iteration count.

## Balance and numbers
- Scripts that *tune* must be clearly separated from scripts that *report*. A tuning script that writes data files, run "just to look at numbers", silently retuned a verified balance. Name them `tune-*` vs `*-report`, and make tuners refuse to write without `--write`.
- Balance numbers come from one final run on a fixed seed set after all edits, saved under Docs/balance/. Quoting the best intermediate run, or a run made while another agent was editing data, produced claims a gate reviewer could not reproduce.
- Take the median of several seeds for any single-number check that swings with the seed.

## CSS / UI
- When a review says a fix "did not land", crop the capture and check selector specificity first. A later, more specific rule silently won for four review rounds.
- Reduced-motion paths need their own capture states: popups once vanished instantly instead of showing statically.
- Check small coloured text against the contrast ratios. Accent colours (red on black) often fail at small sizes and need a text-safe tone.

## Assets (SVG)
- Verify every exported asset by loading it from the built `dist/`, not from the source folder; paths silently resolve from source in dev.
- Render a contact sheet of every batch on the real background before integrating: assets that look fine alone often break the family.
- Keep rejected attempts; reviewers compare against them.

## Process
- Fresh-context playtests found what reviews of screenshots missed (onboarding, teaching a mechanic, phone layout). Run one at every gate; the weakest area goes to the top of TODO.
- Owner requests mid-run become their own milestone with a spec file in Docs/design/, rather than a TODO line.
- Correct wrong claims in DECISIONS/DEVLOG with a new dated line that says what was wrong.

## Site and progress page
- build_progress.py once showed 0 DEVLOG entries because its regex expected the date at line start while headings start with "### " (fixed in the template). Check the "N devlog entries" line after each site build.
- Autodrive: a crashing stream filter broke the pipe and killed the chunk; the filter now reads bytes and never raises. A first push over SSH failed ("Permission denied (publickey)"); remotes use HTTPS.

## {{GAME_NAME}} — lessons
(append here: date, tool, symptom, cause, fix)

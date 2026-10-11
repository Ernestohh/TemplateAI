# MODEL_ROUTING.md — which model and effort for which task

Principle: spend the least that reliably does the job. Escalate on failure, not by default. Cost is driven by main-loop turns × context size (CLAUDE.md §1c), so routing work out of the main loop matters as much as the model choice.

| Task type | Model | Effort | Notes |
|---|---|---|---|
| Run tests, the harness, the gold path; read result files and logs; grep; count; format; rename; move files | **small** (haiku-class) or plain scripts | low | Prefer a script over any model (`test-runner`, `qa-driver`). |
| Captures, timelapses, trailers (ffmpeg), STATS/DEVLOG/AUTODRIVE bookkeeping, token_usage, checkpoint commits | small | low | Mechanical. |
| Simple edits with a clear spec, boilerplate, data tables, copy, barks, lore fragments | **mid** (sonnet-class) | low–medium | `content-writer`. |
| SVG asset batches (concept sheet, production, contact sheet) | mid | medium | `asset-producer`; hero art (logo, key characters, main frame) at medium-high. |
| Feature implementation within the existing architecture (UI screens, sim rules with tests) | mid | medium | |
| Balance tuning with the harness (difficulty bands, act length) | mid | medium–high | Numbers only from one final fixed-seed run. |
| Independent review and fresh playtest | mid; **large** (opus-class) at the {{LARGE_GATES}} gates | high | Fresh context always (`reviewer`, `playtester`). |
| Architecture, planning (PLAN, MAP, ARCHITECTURE, STYLE_BIBLE), cross-system design (how the signature mechanics interact) | large | high | Main loop or a planning agent. |
| Hard debugging after 2 failed attempts, determinism breaks, perf problems, flaky e2e root causes | large | high | `debugger`. |
| Anything touching secrets, the owner's server setup, git history or irreversible actions | large | high | |

## Escalation ladder
1. Start at the cheapest row that fits.
2. Failed twice, or the output is clearly weak: move up one tier (model or effort) and log it in DECISIONS.md with the reason.
3. Once the hard part is solved, drop back down for the follow-up work.

## Parallelism
- Independent tasks run as parallel subagents in one message, each on the cheapest adequate model.
- Never run more parallel agents than there are lanes in CLAUDE.md §4. One owner per shared resource still applies (one Playwright MCP driver at a time).
- Give each subagent a complete, self-contained prompt and a file to write its result to. Keep the main context small by reading results, not transcripts.
- Inside an autodrive chunk, wait for every agent before the chunk ends: background agents do not survive the session.

## What the agent cannot switch
- The main session's model and effort are set by the owner (`/model`, `/effort`) or, for autodrive chunks, by `{{MODEL_ENV}}` (passed as `--model`).
- Recommended: run chunks on a mid or large model at medium effort, and delegate heavy reasoning to a large-model subagent and mechanical work to small-model subagents.

# PORTS.md — port registry for parallel runs on this PC

Every autonomous web-game run on this machine gets its own pair of Vite ports, both with `strictPort: true`, so parallel runs never clash. A run uses only its own row and never kills, reuses or probes another row's ports or processes.

| Project | Dev | Preview | Folder | Domain |
|---|---|---|---|---|
| Renegade | 5173 | 4173 | C:\Users\ernes\Renegade | renegade.kryptos.gg |
| Zephyr | 5273 | 4273 | C:\Users\ernes\Zephyr | zephyr.kryptos.gg |
| Tempest | 5373 | 4373 | C:\Users\ernes\Tempest | tempest.kryptos.gg |
| Nomad | 5473 | 4473 | C:\Users\ernes\Nomad | nomad.kryptos.gg |
| Mirage | 5573 | 4573 | C:\Users\ernes\Mirage | mirage.kryptos.gg |
| Eclipse | 5673 | 4673 | C:\Users\ernes\Eclipse | eclipse.kryptos.gg |
| Monsoon | 5773 | 4773 | C:\Users\ernes\Monsoon | monsoon.kryptos.gg |

## Rules

- **New project:** take the next free pair (dev 5x73 / preview 4x73, stepping by 100: the next is 5873 / 4873). Add the row here in the template (`C:\Users\ernes\GameDev\template\PORTS.md`) and in the new project's copy. `scripts/fill_template.py` warns about a clash.
- **The bash guard** (`.claude/hooks/bash_guard.py`) carries the same list and blocks commands that kill another project's port or touch another project's folder. When you add a row here, add it to `PROJECTS` in the template's bash guard too; running projects keep their copy until their next milestone boundary (CLAUDE.md §8: the harness changes only between milestones).
- **Playwright** uses the preview port only (`baseURL http://localhost:<preview>`, `reuseExistingServer: true`). `scripts/check_gate.sh` fails if a Playwright config does not use this project's preview port.
- **Other shared resources:** only one agent per run drives the Playwright MCP browser; each run has its own browser instance, so parallel runs are fine.

## Performance while runs share the machine

FPS, frame times, sim timings and soak results are noisy while another run is building, testing or recording. Before calling a drop a regression, **re-measure solo** (or at least twice at a quiet moment) and record both numbers with the conditions (which other runs were active). Gate performance numbers in `Docs/perf/` and REPORT.md must say whether they were measured solo.

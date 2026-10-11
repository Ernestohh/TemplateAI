# PORTS.md — port registry for parallel runs on this machine

You can run several autonomous game builds on one machine at the same time. **Each parallel project gets a unique pair of Vite ports** (dev and preview), both with `strictPort: true`, so the runs never clash. A run uses only its own pair and never kills, reuses or probes another project's ports, processes or folder.

The registry lives in your local, git-ignored `owner.json` (`ports_registry`, see `owner.example.json`). `scripts/fill_template.py` replaces the example table below with your registry (plus the new project) when it fills a new project, and `.claude/hooks/bash_guard.py` reads the same list to block the other projects' folders and ports.

Example table (the convention: dev 5x73 / preview 4x73, stepping by 100):

<!-- PORTS_TABLE_START -->
| Project | Dev | Preview | Folder | Domain |
|---|---|---|---|---|
| Project A | 5173 | 4173 | `<projects_root>`/ProjectA | project-a.`<base_domain>` |
| Project B | 5273 | 4273 | `<projects_root>`/ProjectB | project-b.`<base_domain>` |
| Project C | 5373 | 4373 | `<projects_root>`/ProjectC | project-c.`<base_domain>` |
<!-- PORTS_TABLE_END -->

## Rules

- **Each parallel project gets a unique pair.** For a new project, take the next free pair (for example 5473 / 4473 after the table above) and add it to `ports_registry` in your `owner.json` before you fill the project. `scripts/fill_template.py` warns about a clash and about a project that is missing from the registry.
- **The bash guard** (`.claude/hooks/bash_guard.py`) reads `owner.json` in the project folder (or, when that file is missing, the registry the fill script wrote into it) and blocks commands that kill another project's port or touch another project's folder under `projects_root`. Each project reads its own copy of `owner.json`, so add a new row to every running project's copy too; the guard code itself changes only at a milestone boundary (CLAUDE.md §8).
- **Playwright** uses the preview port only (`baseURL http://localhost:<preview>`, `reuseExistingServer: true`). `scripts/check_gate.sh` fails if a Playwright config does not use this project's preview port.
- **Other shared resources:** only one agent per run drives the Playwright MCP browser; each run has its own browser instance, so parallel runs are fine.

## Performance while runs share the machine

FPS, frame times, sim timings and soak results are noisy while another run is building, testing or recording. Before calling a drop a regression, **re-measure solo** (or at least twice at a quiet moment) and record both numbers with the conditions (which other runs were active). Gate performance numbers in `Docs/perf/` and REPORT.md must say whether they were measured solo.

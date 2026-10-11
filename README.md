# Web-game template for autonomous Claude builds

A blank project scaffold for web games that Claude builds on its own, each with its own GitHub repo and `<name>.<your-domain>` site. Based on an earlier full run, with everything it learned: autodrive chunks with HANDOFFs and driver push, the stream filter, stop and bash guards, token discipline, the plain-language /progress page, fresh-agent playtests, per-project ports, `commit_green.sh`, and the nginx/certbot deploy.

- **`owner.example.json`**: your personal settings (projects folder, domain, server, GitHub user, git identity, port registry). Copy it to `owner.json` (git-ignored) once and fill it in; nothing personal lives in the tracked files.
- **`SETUP.md`**: step by step from copying this folder to starting and stopping the run.
- **`QUESTIONS.md`**: the questionnaire Claude walks through with the owner before filling a copy.
- **`PORTS.md`**: how parallel runs share one machine (each project gets a unique port pair).
- **`project.example.json`**: input for `scripts/fill_template.py`.

Placeholders: double-brace names such as `GAME_NAME` are filled by `scripts/fill_template.py`; `FILL:` markers are rich sections Claude writes from the questionnaire. `README.project.md` becomes the new project's README. Do not `git init` a copy of this folder before filling it.

Requirements: Windows with Git Bash (the scripts also run on Linux/macOS), Python 3, Node.js, the Claude Code CLI, and, for hosting, a Linux server with nginx and certbot that you reach over ssh with a key.

Licence: the template itself is GPL-3 (`LICENSE`). A game made from it chooses its own licence (SETUP.md step 1).

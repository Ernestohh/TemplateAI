# Web-game template for autonomous Claude builds

A blank project scaffold for games that Claude builds on its own (Tempest, Nomad, Mirage, Eclipse, Monsoon, ...), each with its own GitHub repo and `<name>.kryptos.gg` site. Based on the Zephyr run, with everything it learned: autodrive chunks with HANDOFFs and driver push, the stream filter, stop and bash guards, token discipline, the plain-language /progress page, fresh-agent playtests, per-project ports, `commit_green.sh`, and the nginx/certbot deploy.

- **`SETUP.md`**: step by step from copying this folder to starting and stopping the run.
- **`QUESTIONS.md`**: the questionnaire Claude walks through with the owner before filling a copy.
- **`PORTS.md`**: the port registry for parallel runs.
- **`project.example.json`**: input for `scripts/fill_template.py`.

Placeholders: double-brace names such as `GAME_NAME` are filled by `scripts/fill_template.py`; `FILL:` markers are rich sections Claude writes from the questionnaire. `README.project.md` becomes the new project's README. Do not `git init` this folder.

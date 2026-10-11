# SETUP.md — create a new game project from this template

The example uses **Tempest**; replace the name, slug and ports with the new project's row in `PORTS.md`. Commands are for Git Bash unless marked PowerShell.

## 1. Copy the template

```bash
cp -r /c/Users/ernes/GameDev/template /c/Users/ernes/Tempest
```

PowerShell: `Copy-Item -Recurse C:\Users\ernes\GameDev\template C:\Users\ernes\Tempest`

Never edit the template in place for one game, never `git init` the template folder, and never copy a running project's `.claude/autodrive/`, `AUTONOMOUS_RUN` or `ALLOW_STOP` markers (the template has none).

## 2. Fill the placeholders

1. **Questionnaire.** In an interactive Claude session in the new folder, ask Claude to walk through `QUESTIONS.md` with you. Unanswered questions take the marked defaults.
2. **Simple placeholders.** Claude writes `project.json` (copy `project.example.json`; keys are the placeholder names) and runs:
   ```bash
   cd /c/Users/ernes/Tempest
   python -I scripts/fill_template.py project.json
   ```
   The script replaces every simple placeholder (name, slug, ports, domain, remote, env variable names such as `TEMPEST_AUTODRIVE`, folders), renames `README.project.md` to `README.md`, moves `QUESTIONS.md`, `SETUP.md` and the JSON files to `Docs/setup/`, warns about port clashes with `PORTS.md`, and lists the rich `FILL` markers that are left. Use `--dry-run` first if you like.
3. **Rich sections.** Claude writes every listed FILL section from the answers: `Docs/TASK.md` (§0-§18 game parts), `Docs/STYLE_BIBLE.md`, `Docs/PLAN.md`, `Docs/TODO.md` (T15), `Docs/refs/README.md`, `Docs/DECISIONS.md`. Each marker has a guidance comment with a Zephyr example; replace the marker and its comment with the real text, and delete the TEMPLATE NOTE comments.
4. **Check.** Both must be clean:
   ```bash
   python -I scripts/fill_template.py --check   # "no placeholders left"
   bash scripts/check_gate.sh                   # docs present, no placeholders
   ```
5. If the project is new to `PORTS.md`, add its row there **and** in `C:\Users\ernes\GameDev\template\PORTS.md` and the template's `.claude/hooks/bash_guard.py` (`PROJECTS`).

## 3. Git: init, first commit, remote

Create an **empty** repository on GitHub first (no README, no licence), for example `Ernestohh/Tempest`.

```bash
cd /c/Users/ernes/Tempest
git init -b master
bash scripts/commit_green.sh "Tempest scaffolding: rules, task, plan, hooks, agents, skills, autodrive"
git remote add origin https://github.com/Ernestohh/Tempest.git
```

Use the **HTTPS** URL, never `git@github.com:...`: this PC has no GitHub SSH key, so SSH pushes fail with "Permission denied (publickey)", while HTTPS uses the saved Windows git credentials. (Run `git remote add` yourself in a terminal: the bash guard blocks remote changes from Claude.)

## 4. DNS

The owner adds an **A record** `tempest` → `72.62.17.59` at the kryptos.gg DNS provider. Check that it resolves before the server setup:

```bash
python -c "import socket; print(socket.gethostbyname('tempest.kryptos.gg'))"   # must print 72.62.17.59
```

PowerShell: `Resolve-DnsName tempest.kryptos.gg`. New records can take a few minutes; without DNS the server setup installs HTTP only and says so.

## 5. One-time server setup (nginx and certbot)

```bash
DEPLOY_SSH=root@72.62.17.59 bash scripts/server_setup.sh
```

It installs `deploy/nginx-site.conf` as the site's nginx file, creates `/var/www/tempest` with a placeholder page, runs `nginx -t` (and removes its own symlink again if that fails), reloads nginx, and requests the certificate when DNS already points at the server. It never touches other sites. Safe to re-run (for example after DNS starts resolving). If you run it here, mark TODO T17's setup part done in `Docs/TODO.md`; otherwise the run does it in M0. Check: `https://tempest.kryptos.gg/` shows "Tempest is being built."

## 6. First push

```bash
git push -u origin master
```

This is the only manual push. From now on the autodrive driver pushes `master` after every chunk (fast-forward only, never forced, no prompts; a failure is logged in `Docs/AUTODRIVE_LOG.md` and `.claude/autodrive/push.log`, and the run continues).

## 7. Start the run

PowerShell:

```powershell
& "C:\Program Files\Git\bin\bash.exe" -lc "cd /c/Users/ernes/Tempest && bash scripts/autodrive.sh"
```

Optional, set before the command: `TEMPEST_MODEL=<model>` (passed as `--model` to every chunk) and `CHUNK_MAX_MIN=<minutes>` (hard limit per chunk, default 150), for example `-lc "cd /c/Users/ernes/Tempest && TEMPEST_MODEL=opus CHUNK_MAX_MIN=120 bash scripts/autodrive.sh"`.

The driver creates `.claude/AUTONOMOUS_RUN` and `.claude/autodrive/ACTIVE`, then starts fresh `claude -p` chunks one after another. The window shows one short line per action; each finished chunk adds a row to `Docs/AUTODRIVE_LOG.md`. Chunk 1 reads the HANDOFF "start M0" and begins. Do not work in the repo from another Claude session while `ACTIVE` exists.

Watch progress at `https://tempest.kryptos.gg/progress/` (after the first deploy), on GitHub, or in the newest HANDOFF entry of `Docs/DEVLOG.md`.

## 8. Stop the run

- **Stop after the current chunk:** create the stop file. PowerShell: `New-Item C:\Users\ernes\Tempest\.claude\ALLOW_STOP`. Git Bash: `touch .claude/ALLOW_STOP`. The driver finishes the current chunk (it still pushes), then exits.
- **Stop at once:** Ctrl+C in the driver window. The current chunk's uncommitted work stays in the working tree; the next chunk's context recovery finds it.
- **Restart later:** delete `.claude/ALLOW_STOP` (the driver refuses to start while it exists) and run step 7 again. Numbering continues in `Docs/AUTODRIVE_LOG.md`.
- **End for good:** create `ALLOW_STOP`, then use the wrap-up message in `Docs/KICKOFF.md` §4 in an interactive session, and push the final commits yourself (`git push origin master`).

## Troubleshooting

- **Three chunks in a row failed** (exit code not 0 or under 2 minutes): the driver stops; read `.claude/autodrive/chunk-<n>.err`.
- **Push failed:** see `.claude/autodrive/push.log`. Usually the remote is SSH instead of HTTPS, the repo is not empty, or the Windows credentials expired (run one manual `git push` to refresh them).
- **Port in use:** another process holds this project's port. Find it by port and kill it by PID, only if it is this project's own; never touch other projects' ports (`PORTS.md`).

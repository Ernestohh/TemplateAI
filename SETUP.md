# SETUP.md — create a new game project from this template

The example game is **Skyward** (slug `skyward`, ports 5473/4473). `<projects_root>`, `<base_domain>`, `<server_host>`, `<server_user>` and `<github_user>` stand for your values in `owner.json`. Commands are for Git Bash unless marked PowerShell; in Git Bash write `C:\Users\you\games` as `/c/Users/you/games`.

## 0. Your owner settings (once per machine)

Copy `owner.example.json` to `owner.json` in the template folder and fill in your values:

```bash
cp owner.example.json owner.json   # then edit owner.json
```

| Key | Meaning | Example |
|---|---|---|
| `projects_root` | folder that holds your game folders (`<projects_root>\<Name>`) | `C:\Users\you\GameDev\projects` |
| `base_domain` | each game is served at `<slug>.<base_domain>` | `games.example.com` |
| `server_host` | ssh host name or IP of your web server | `your-server.example.com` |
| `server_user` | ssh user; use a **non-root deploy user with passwordless sudo** for nginx, certbot and the web root (`deploy/README.md`) | `deploy` |
| `web_root_base` | parent of each game's web root (`<web_root_base>/<slug>`) | `/var/www` |
| `github_user` | owner of the game repositories (`https://github.com/<github_user>/<Name>.git`) | `your-github-name` |
| `git_name`, `git_email` | git identity for the game repositories | `Your Name`, `you@example.com` |
| `ports_registry` (optional) | every project that may run in parallel, each with a unique dev/preview pair (`PORTS.md`) | `[{"project": "Skyward", "dev": 5473, "preview": 4473}]` |

`owner.json` is git-ignored: it never reaches a repository. When you copy the template folder it comes along, so every game gets it. Without it the fill script falls back to the dummy values of `owner.example.json` and warns loudly. Add each new game to `ports_registry` before step 2.

## 1. Copy the template

```bash
cp -r <template-folder> <projects_root>/Skyward && rm -rf <projects_root>/Skyward/.git
```

PowerShell: `Copy-Item -Recurse <template-folder> <projects_root>\Skyward; Remove-Item -Recurse -Force <projects_root>\Skyward\.git`

Or straight from GitHub: `git clone <template-repository-url> Skyward`, then delete `Skyward\.git` and copy your `owner.json` into the folder.

**Always delete the copied `.git` folder.** The template is its own repository. A new game must start a fresh history with its own remote (step 3).

**Licence:** the template is licensed GPL-3 (`LICENSE`). A new game chooses its own licence: delete `LICENSE` or replace it with your choice (for example MIT, a proprietary "all rights reserved" notice, or GPL-3 if you want to keep it) before the first commit.

Never edit the template in place for one game, and never copy a running project's `.claude/autodrive/`, `AUTONOMOUS_RUN` or `ALLOW_STOP` markers (the template has none).

## 2. Fill the placeholders

1. **Questionnaire.** In an interactive Claude session in the new folder, ask Claude to walk through `QUESTIONS.md` with you. Unanswered questions take the marked defaults.
2. **Simple placeholders.** Claude writes `project.json` (copy `project.example.json`; keys are the placeholder names) and runs:
   ```bash
   cd <projects_root>/Skyward
   python -I scripts/fill_template.py project.json
   ```
   The script reads `owner.json` and `project.json`, derives the domain (`skyward.<base_domain>`), the remote (`https://github.com/<github_user>/Skyward.git`), the deploy target (`<server_user>@<server_host>:<web_root_base>/skyward`), the folders, the env variable names (such as `SKYWARD_AUTODRIVE`) and the port registry, and replaces every simple placeholder. It rewrites the table in `PORTS.md` from your registry, renames `README.project.md` to `README.md`, moves `QUESTIONS.md`, `SETUP.md` and the JSON files to `Docs/setup/`, warns about port clashes, and lists the rich `FILL` markers that are left. Use `--dry-run` first if you like. Any key set in `project.json` overrides the derived value.
3. **Rich sections.** Claude writes every listed FILL section from the answers: `Docs/TASK.md` (§0-§18 game parts), `Docs/STYLE_BIBLE.md`, `Docs/PLAN.md`, `Docs/TODO.md` (T15), `Docs/refs/README.md`, `Docs/DECISIONS.md`. Each marker has a guidance comment with an example; replace the marker and its comment with the real text, and delete the TEMPLATE NOTE comments.
4. **Check.** Both must be clean:
   ```bash
   python -I scripts/fill_template.py --check   # "no placeholders left"
   bash scripts/check_gate.sh                   # docs present, no placeholders
   ```
5. If the project is new, add it to `ports_registry` in your `owner.json` (the template's copy and the copies in projects that are running in parallel), so their bash guards block its folder and ports.

## 3. Git: init, first commit, remote

Create an **empty** repository on GitHub first (no README, no licence), for example `<github_user>/Skyward`.

```bash
cd <projects_root>/Skyward
git init -b master
python -I scripts/fill_template.py --git-identity   # git user.name / user.email from owner.json
bash scripts/commit_green.sh "Skyward scaffolding: rules, task, plan, hooks, agents, skills, autodrive"
git remote add origin https://github.com/<github_user>/Skyward.git
```

Use the **HTTPS** URL, never `git@github.com:...`: the autodrive driver pushes without prompts using your saved HTTPS git credentials (on Windows the Git Credential Manager). An SSH remote fails there unless you have set up a key and agent yourself. (Run `git remote add` yourself in a terminal: the bash guard blocks remote changes from Claude.)

## 4. DNS

Add an **A record** `skyward` → the IP address of `<server_host>` at the DNS provider of `<base_domain>`. Check that it resolves before the server setup:

```bash
python -c "import socket; print(socket.gethostbyname('skyward.<base_domain>'))"   # must print your server's IP
```

PowerShell: `Resolve-DnsName skyward.<base_domain>`. New records can take a few minutes; without DNS the server setup installs HTTP only and says so.

## 5. One-time server setup (nginx and certbot)

```bash
DEPLOY_SSH=<server_user>@<server_host> bash scripts/server_setup.sh
```

The server needs nginx and certbot (with the nginx plugin) installed, and your ssh key for `<server_user>`. A non-root deploy user needs passwordless sudo (`deploy/README.md` has a minimal sudoers line); the scripts use `sudo -n` and fail fast instead of prompting.

It installs `deploy/nginx-site.conf` as the site's nginx file, creates `<web_root_base>/skyward` with a placeholder page, runs `nginx -t` (and removes its own symlink again if that fails), reloads nginx, and requests the certificate when DNS already points at the server. It never touches other sites. Safe to re-run (for example after DNS starts resolving). If you run it here, mark TODO T17's setup part done in `Docs/TODO.md`; otherwise the run does it in M0. Check: `https://skyward.<base_domain>/` shows "Skyward is being built."

## 6. First push

```bash
git push -u origin master
```

This is the only manual push. From now on the autodrive driver pushes `master` after every chunk (fast-forward only, never forced, no prompts; a failure is logged in `Docs/AUTODRIVE_LOG.md` and `.claude/autodrive/push.log`, and the run continues).

## 7. Start the run

PowerShell:

```powershell
& "C:\Program Files\Git\bin\bash.exe" -lc "cd /c/<path-to>/Skyward && bash scripts/autodrive.sh"
```

Git Bash, Linux or macOS: `cd <projects_root>/Skyward && bash scripts/autodrive.sh`.

Optional, set before the command: `SKYWARD_MODEL=<model>` (passed as `--model` to every chunk) and `CHUNK_MAX_MIN=<minutes>` (hard limit per chunk, default 150), for example `-lc "cd /c/<path-to>/Skyward && SKYWARD_MODEL=opus CHUNK_MAX_MIN=120 bash scripts/autodrive.sh"`.

The driver creates `.claude/AUTONOMOUS_RUN` and `.claude/autodrive/ACTIVE`, then starts fresh `claude -p` chunks one after another. The window shows one short line per action; each finished chunk adds a row to `Docs/AUTODRIVE_LOG.md`. Chunk 1 reads the HANDOFF "start M0" and begins. Do not work in the repo from another Claude session while `ACTIVE` exists.

Watch progress at `https://skyward.<base_domain>/progress/` (after the first deploy), on GitHub, or in the newest HANDOFF entry of `Docs/DEVLOG.md`.

## 8. Stop the run

- **Stop after the current chunk:** create the stop file. PowerShell: `New-Item <projects_root>\Skyward\.claude\ALLOW_STOP`. Git Bash: `touch .claude/ALLOW_STOP`. The driver finishes the current chunk (it still pushes), then exits.
- **Stop at once:** Ctrl+C in the driver window. The current chunk's uncommitted work stays in the working tree; the next chunk's context recovery finds it.
- **Restart later:** delete `.claude/ALLOW_STOP` (the driver refuses to start while it exists) and run step 7 again. Numbering continues in `Docs/AUTODRIVE_LOG.md`.
- **End for good:** create `ALLOW_STOP`, then use the wrap-up message in `Docs/KICKOFF.md` §4 in an interactive session, and push the final commits yourself (`git push origin master`).

## Troubleshooting

- **The fill script printed the dummy-values warning:** `owner.json` is missing in the project folder. Copy yours in and run step 2 again on a fresh copy (or fix the filled values by hand).
- **Three chunks in a row failed** (exit code not 0 or under 2 minutes): the driver stops; read `.claude/autodrive/chunk-<n>.err`.
- **Push failed:** see `.claude/autodrive/push.log`. Usually the remote is SSH instead of HTTPS, the repo is not empty, or the saved credentials expired (run one manual `git push` to refresh them).
- **Port in use:** another process holds this project's port. Find it by port and kill it by PID, only if it is this project's own; never touch other projects' ports (`PORTS.md`).

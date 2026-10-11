#!/usr/bin/env python3
"""PreToolUse guard for Bash (exit 2 = block, stderr goes to the agent).
Git push is always blocked for the agent: the autodrive DRIVER pushes master after each chunk (scripts/autodrive.sh),
outside any Claude session. History-rewriting git is blocked during an autonomous run (marker .claude/AUTONOMOUS_RUN).
The other rules always apply: no remote changes, no secrets, no env dumps, kill by PID only, and never another
project's folder or ports (PORTS.md: several runs share this PC)."""
import json, os, re, sys

SELF = "{{GAME_SLUG}}"
OWN_PORTS = "{{DEV_PORT}}/{{PREVIEW_PORT}}"
# Port registry (keep in sync with PORTS.md). The guard blocks the folders and ports of every project except this one.
PROJECTS = {
    "renegade": ("Renegade", 5173, 4173),
    "zephyr": ("Zephyr", 5273, 4273),
    "tempest": ("Tempest", 5373, 4373),
    "nomad": ("Nomad", 5473, 4473),
    "mirage": ("Mirage", 5573, 4573),
    "eclipse": ("Eclipse", 5673, 4673),
    "monsoon": ("Monsoon", 5773, 4773),
}
others = [v for k, v in PROJECTS.items() if k != SELF.lower()]
other_dirs = "|".join(v[0] for v in others)
other_ports = "|".join(str(p) for v in others for p in v[1:])

data = json.load(sys.stdin)
cmd = (data.get("tool_input") or {}).get("command", "")
marker = os.path.join(os.environ.get("CLAUDE_PROJECT_DIR", "."), ".claude", "AUTONOMOUS_RUN")
autonomous = os.path.exists(marker)

git_rules = [
    (r"git\s+(reset\s+--hard|clean\s+-[a-z]*f|rebase|commit\s+--amend|filter-branch|push\s+.*--force)", "No history rewriting or destructive git (CLAUDE.md section 5)."),
]
rules = (git_rules if autonomous else []) + [
    (r"git\s+push", "No pushes from an agent: the autodrive driver pushes master after each chunk (CLAUDE.md section 9)."),
    (r"git\s+remote\s+(add|set-url|remove|rm|rename)", "No remote changes: the owner sets the remote once (CLAUDE.md section 9)."),
    (r"rm\s+-[a-z]*r[a-z]*f?\s+(/|~|\$HOME|\.\.)(\s|/|$)", "Refusing recursive delete outside the project."),
    (r"(cat|echo|printenv|env|less|head|tail|grep|type|more)\b[^|;&]*\.env\b", "Never print secrets from .env."),
    (r"\b(printenv|env|set)\s*($|[|;&])", "Do not dump the environment; it may contain secrets."),
    (r"(curl|wget)[^|;&]*\|\s*(sudo\s+)?(ba)?sh", "No piping downloads into a shell."),
    (r"\b(kill|pkill|killall|taskkill)\b(?!.*\b\d+\b)", "Kill processes by PID only."),
]
if other_dirs:
    rules.append((r"(?i)Users[/\\]+ernes[/\\]+(" + other_dirs + r")\b", "Never touch another project's folder (CLAUDE.md section 5b, PORTS.md)."))
if other_ports:
    rules.append((r"\b(taskkill|kill|kill-port)\b.*\b(" + other_ports + r")\b",
                  "That port belongs to another project (PORTS.md); this project uses " + OWN_PORTS + "."))
for pat, msg in rules:
    if re.search(pat, cmd):
        print(f"Blocked by bash_guard: {msg}", file=sys.stderr)
        sys.exit(2)

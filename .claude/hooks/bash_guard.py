#!/usr/bin/env python3
"""PreToolUse guard for Bash (exit 2 = block, stderr goes to the agent).
Git push is always blocked for the agent: the autodrive DRIVER pushes master after each chunk (scripts/autodrive.sh),
outside any Claude session. History-rewriting git is blocked during an autonomous run (marker .claude/AUTONOMOUS_RUN).
The other rules always apply: no remote changes, no secrets, no env dumps, kill by PID only, and never another
project's folder or ports (PORTS.md: several runs may share this machine).

The list of other projects comes from the local, git-ignored owner.json (ports_registry, projects_root) in the project
folder; when that file is missing, from the values scripts/fill_template.py wrote below. Nothing is hard-coded."""
import json, os, re, sys

SELF = "{{GAME_NAME}}"
OWN_PORTS = "{{DEV_PORT}}/{{PREVIEW_PORT}}"
FILLED_REGISTRY = r'''{{PORTS_REGISTRY_JSON}}'''
FILLED_ROOT = r"""{{PROJECTS_ROOT}}"""

project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")


def load_registry():
    """[(name, dev, preview)], projects_root - owner.json first, then the filled values, else empty."""
    entries, root = None, None
    try:
        with open(os.path.join(project_dir, "owner.json"), encoding="utf8") as f:
            owner = json.load(f)
        entries, root = owner.get("ports_registry"), owner.get("projects_root")
    except Exception:
        pass
    if entries is None and not FILLED_REGISTRY.startswith("{{"):
        try:
            entries = json.loads(FILLED_REGISTRY)
        except Exception:
            entries = None
    if not root and not FILLED_ROOT.startswith("{{"):
        root = FILLED_ROOT
    out = []
    for e in entries or []:
        try:
            out.append((str(e["project"]), int(e["dev"]), int(e["preview"])))
        except Exception:
            continue
    return out, root


projects, projects_root = load_registry()
own = SELF.lower() if not SELF.startswith("{{") else os.path.basename(os.path.abspath(project_dir)).lower()
others = [p for p in projects if p[0].lower() != own and p[0].replace(" ", "").lower() != own]
other_dirs = "|".join(re.escape(p[0].replace(" ", "")) for p in others)
other_ports = "|".join(str(n) for p in others for n in p[1:])
root_re = ""
if projects_root:
    # C:\Users\you\games and /c/Users/you/games both match: drop the drive, accept either separator.
    parts = [x for x in re.split(r"[\\/]+", projects_root.strip()) if x]
    if parts and re.fullmatch(r"[A-Za-z]:?", parts[0]):
        parts = parts[1:]
    root_re = r"[/\\]+".join(re.escape(x) for x in parts)

data = json.load(sys.stdin)
cmd = (data.get("tool_input") or {}).get("command", "")
marker = os.path.join(project_dir, ".claude", "AUTONOMOUS_RUN")
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
    prefix = (root_re + r"[/\\]+") if root_re else r"[/\\]"
    rules.append((r"(?i)" + prefix + r"(" + other_dirs + r")\b", "Never touch another project's folder (CLAUDE.md section 5b, PORTS.md)."))
if other_ports:
    rules.append((r"\b(taskkill|kill|kill-port)\b.*\b(" + other_ports + r")\b",
                  "That port belongs to another project (PORTS.md); this project uses " + OWN_PORTS + "."))
for pat, msg in rules:
    if re.search(pat, cmd):
        print(f"Blocked by bash_guard: {msg}", file=sys.stderr)
        sys.exit(2)

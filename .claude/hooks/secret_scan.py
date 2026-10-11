#!/usr/bin/env python3
"""PostToolUse: warn if a written file contains something that looks like a secret."""
import json, re, sys

data = json.load(sys.stdin)
path = (data.get("tool_input") or {}).get("file_path", "")
if path.endswith(".env") or "/.env" in path:
    sys.exit(0)
try:
    text = open(path, encoding="utf8", errors="ignore").read()
except OSError:
    sys.exit(0)
pats = [r"AKIA[0-9A-Z]{16}", r"sk-[A-Za-z0-9_-]{20,}", r"ghp_[A-Za-z0-9]{30,}", r"-----BEGIN [A-Z ]*PRIVATE KEY-----", r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{20,}['\"]"]
for p in pats:
    if re.search(p, text):
        print(f"secret_scan: {path} looks like it contains a secret. Move it to .env and remove it from the file.", file=sys.stderr)
        sys.exit(2)

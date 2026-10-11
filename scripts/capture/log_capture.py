#!/usr/bin/env python3
"""Append one capture record to Docs/progress/log.jsonl.
Usage: log_capture.py <feature> <file> "<caption>"
"""
import json, subprocess, sys, datetime, pathlib

def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    feature, file, caption = sys.argv[1:]
    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        commit = ""
    rec = {"time": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "feature": feature, "caption": caption, "file": file, "commit": commit}
    log = pathlib.Path("Docs/progress/log.jsonl")
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf8") as f:
        f.write(json.dumps(rec) + "\n")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Validate asset.json manifests under a folder. Usage: validate_asset.py [root=assets/generated]

route: authored-svg | procedural | external. External assets must name a licence from the allowed list
and a source URL; every asset must state a result starting with accepted/rejected.
Size budgets (Docs/TASK.md section 15) are checked for SVG files when output_path exists.
"""
import json, pathlib, sys

REQUIRED = ["asset_id", "lane", "kind", "created_utc", "route", "source", "licence", "purpose", "output_path", "result"]
ROUTES = {"authored-svg", "procedural", "external"}
LICENCES = ("project-owned", "CC0", "CC-BY", "OFL", "SIL OFL", "MIT", "Apache-2.0")
SVG_MAX = {"portrait": 20_000}
SVG_DEFAULT_MAX = 60_000
root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "assets/generated")
bad = 0
for f in root.rglob("asset.json"):
    try:
        d = json.loads(f.read_text(encoding="utf8"))
    except Exception as e:
        print(f"{f}: invalid JSON ({e})"); bad += 1; continue
    entries = d if isinstance(d, list) else d.get("assets", [d]) if isinstance(d, dict) else []
    for a in entries:
        missing = [k for k in REQUIRED if k not in a]
        if missing:
            print(f"{f}: {a.get('asset_id', '?')} missing {missing}"); bad += 1; continue
        if a["route"] not in ROUTES:
            print(f"{f}: {a['asset_id']} route must be one of {sorted(ROUTES)}"); bad += 1
        if not str(a["result"]).startswith(("accepted", "rejected")):
            print(f"{f}: {a['asset_id']} result must start with accepted/rejected"); bad += 1
        if not str(a["licence"]).startswith(LICENCES):
            print(f"{f}: {a['asset_id']} licence '{a['licence']}' not in the allowed list"); bad += 1
        if a["route"] == "external" and not str(a["source"]).startswith("http"):
            print(f"{f}: {a['asset_id']} external asset needs a source URL"); bad += 1
        p = pathlib.Path(a["output_path"])
        if str(a["result"]).startswith("accepted") and p.suffix == ".svg" and p.exists():
            limit = SVG_MAX.get(a["kind"], SVG_DEFAULT_MAX)
            if p.stat().st_size > limit:
                print(f"{f}: {a['asset_id']} {p.stat().st_size} bytes > budget {limit}"); bad += 1
print("asset manifests OK" if not bad else f"{bad} problem(s)")
sys.exit(1 if bad else 0)

---
description: Bring the project to a safe, documented stopping point
---
1. Finish or revert the item in progress.
2. Run `npm run check` and the acceptance test.
3. Update REPORT, STATS, LICENSES and DEVLOG; the DEVLOG update is a HANDOFF entry.
4. Run `python scripts/capture/make_timelapse.py --all --master` and `python -I scripts/token_usage.py`.
5. Commit with `bash scripts/commit_green.sh` and tag.
6. Tell the owner it is safe to create `.claude/ALLOW_STOP`. That also stops the autodrive driver after the current chunk.

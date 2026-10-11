---
description: Capture the fixed state for the feature being worked on
---
1. Capture the fixed state(s) for feature `$ARGUMENTS` at 1440x900 and 390x844 with the capture spec (`npm run capture -- --grep $ARGUMENTS`; the preview runs on port {{PREVIEW_PORT}}).
2. Save each as `Docs/progress/$ARGUMENTS/<UTC yyyymmdd-HHMMSS>__<screen>-<desktop|mobile>-<caption>.png`.
3. Log each one with `python scripts/capture/log_capture.py $ARGUMENTS <file> "<caption>"`.
4. Open one image to confirm it shows what you expect.

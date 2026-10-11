#!/usr/bin/env python3
"""Convert the newest Playwright recording (test-results/**/video.webm) to Docs/recording/gameplay-<ts>.mp4."""
import datetime, pathlib, subprocess, sys

vids = sorted(pathlib.Path('test-results').rglob('*.webm'), key=lambda p: p.stat().st_mtime)
if not vids:
    sys.exit('no recording found; run: npx playwright test -c playwright.record.config.ts')
src = vids[-1]
out_dir = pathlib.Path('Docs/recording')
out_dir.mkdir(parents=True, exist_ok=True)
ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')
out = out_dir / f'gameplay-{ts}.mp4'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(src), '-c:v', 'libx264', '-preset', 'medium', '-crf', '24',
                '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(out)], check=True)
print('wrote', out, f'{out.stat().st_size / 1e6:.1f} MB')

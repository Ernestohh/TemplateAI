#!/usr/bin/env python3
"""Convert the newest trailer recording (test-results/**/video.webm) to Docs/recording/trailer-<ts>.mp4."""
import datetime, pathlib, subprocess, sys

vids = sorted([p for p in pathlib.Path('test-results').rglob('*.webm') if 'trailer' in str(p)], key=lambda p: p.stat().st_mtime)
if not vids:
    sys.exit('no trailer recording found; run: npx playwright test -c playwright.trailer.config.ts')
out_dir = pathlib.Path('Docs/recording')
out_dir.mkdir(parents=True, exist_ok=True)
ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')
out = out_dir / f'trailer-{ts}.mp4'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(vids[-1]), '-c:v', 'libx264', '-preset', 'medium', '-crf', '22',
                '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(out)], check=True)
print('wrote', out, f'{out.stat().st_size / 1e6:.1f} MB')

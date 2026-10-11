#!/usr/bin/env python3
"""Assemble the public website for {{DOMAIN}} into site-dist/.

Layout:
  /            the playable game (the Vite build in dist/)
  /trailer/    a page with the newest trailers (Docs/recording/trailer-*.mp4); a placeholder before the first cut
  /progress/   the build log (scripts/build_progress.py, called at the end)

Run after `npm run build`:  python scripts/build_site.py
"""
import datetime, html, pathlib, re, runpy, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
OUT = ROOT / 'site-dist'
DOMAIN = '{{DOMAIN}}'

if not (DIST / 'index.html').exists():
    raise SystemExit('dist/ is missing: run `npm run build` first')

if OUT.exists():
    try:
        shutil.rmtree(OUT)
    except PermissionError:  # the folder itself may be held open by a server
        pass
shutil.copytree(DIST, OUT, dirs_exist_ok=True)

trailers = sorted((ROOT / 'Docs' / 'recording').glob('trailer-*.mp4'), reverse=True)[:3]
tdir = OUT / 'trailer'
tdir.mkdir(exist_ok=True)
items = []
for i, t in enumerate(trailers):
    shutil.copy2(t, tdir / t.name)
    m = re.match(r'trailer-(\d{8})-(\d{4})', t.stem)
    when = datetime.datetime.strptime(m.group(1) + m.group(2), '%Y%m%d%H%M').strftime('%d %b %Y, %H:%M UTC') if m else t.stem
    items.append((t.name, when))

if items:
    latest = items[0]
    body = (f'<video controls preload="metadata" playsinline src="{html.escape(latest[0])}"></video>'
            f'<p class="meta">Latest cut: {html.escape(latest[1])}. Everything shown is in the current build.</p>')
    older = ''.join(f'<li><a href="{html.escape(n)}">{html.escape(w)}</a></li>' for n, w in items[1:])
    if older:
        body += f'<h2>Earlier cuts</h2><ul>{older}</ul>'
else:
    body = '<p class="meta">No trailer has been cut yet. The first one comes with the first playable build.</p>'

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{GAME_NAME}} — Trailer</title>
<meta name="description" content="{{GAME_NAME}}: {{TAGLINE}}">
<link rel="icon" href="../favicon.svg">
<style>
  :root {{ --black: #0b0a0c; --panel: #1b171c; --line: #6b5326; --paper: #efe4cc; --bone: #cfc3a8; --gold: #d4a53c; --red: #d23a24; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: radial-gradient(ellipse at 50% 0%, #241a14, var(--black) 60%); color: var(--paper);
         font-family: 'PT Sans', system-ui, -apple-system, Segoe UI, sans-serif; line-height: 1.5; }}
  main {{ max-width: 1040px; margin: 0 auto; padding: 48px 16px 64px; }}
  .kicker {{ color: var(--gold); letter-spacing: .22em; text-transform: uppercase; font-size: 13px; }}
  h1 {{ font-family: Kurale, Georgia, serif; font-weight: 400; font-size: clamp(44px, 8vw, 76px); line-height: 1; margin: 6px 0 10px; color: var(--gold); }}
  h2 {{ font-family: Kurale, Georgia, serif; font-weight: 400; font-size: 26px; margin: 40px 0 8px; }}
  p.lede {{ color: var(--bone); font-size: 18px; max-width: 720px; margin: 0 0 28px; }}
  video {{ width: 100%; aspect-ratio: 16 / 10; background: #000; border-radius: 6px; border: 1px solid var(--line); display: block; }}
  .meta {{ color: var(--bone); font-size: 14px; margin: 10px 0 0; }}
  .play {{ display: inline-block; margin: 28px 10px 0 0; padding: 14px 26px; border-radius: 6px; background: var(--red); color: var(--paper);
           text-decoration: none; font-weight: 700; border: 1px solid var(--gold); }}
  .play.alt {{ background: transparent; }}
  a {{ color: var(--gold); }}
  footer {{ color: var(--bone); font-size: 13px; margin-top: 48px; border-top: 1px solid var(--line); padding-top: 16px; }}
</style>
</head>
<body>
<main>
  <div class="kicker">Trailer</div>
  <h1>{{GAME_NAME}}</h1>
  <p class="lede">{{TRAILER_LEDE}}</p>
  {body}
  <a class="play" href="../">Play {{GAME_NAME}} in your browser</a><a class="play alt" href="../progress/">How it was built</a>
  <footer>Built autonomously by Claude. Your save stays in your browser.</footer>
</main>
</body>
</html>
'''
(tdir / 'index.html').write_text(page, encoding='utf8')
size = sum(f.stat().st_size for f in OUT.rglob('*') if f.is_file())
print(f'site-dist/ ready for {DOMAIN}: game at /, {len(items)} trailer(s) at /trailer/, {size / 1e6:.1f} MB')

runpy.run_path(str(ROOT / 'scripts' / 'build_progress.py'), run_name='__main__')

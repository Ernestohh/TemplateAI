#!/usr/bin/env python3
"""Build site-dist/progress/index.html (+ media/) for {{DOMAIN}}/progress/.

The readable part of the page comes from Docs/progress_story.md (format documented at its top).
Live numbers come from git, Docs/STATS.json and Docs/TOKENS.json. The raw records (dev log,
decisions, reviews, commits) sit in a collapsed "Technical log" at the end.

Runs standalone:  python scripts/build_progress.py   (build_site.py also calls it at its end)
Read-only on Docs/ and git; writes only under site-dist/progress/.
"""
import sys
import collections, datetime, html, json, pathlib, re, shutil, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / 'Docs'
OUT = ROOT / 'site-dist' / 'progress'
MEDIA = OUT / 'media'
E = html.escape

try:
    from PIL import Image
except ImportError:  # fall back to copying PNGs
    Image = None


def read(p):
    return (ROOT / p).read_text(encoding='utf8', errors='replace') if (ROOT / p).exists() else ''


def md(s):
    """Inline markdown: `code`, **bold**, *italic*, [text](url)."""
    s = E(s.strip(), quote=False)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![*\w])\*([^*\n]+)\*(?![*\w])', r'<em>\1</em>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', s)
    return s


def table_rows(text):
    rows = []
    for line in text.splitlines():
        if line.startswith('|') and not re.match(r'^\|[\s:|-]+\|?$', line):
            rows.append([c.strip() for c in line.strip().strip('|').split('|')])
    return rows


def section(text, title):
    m = re.search(r'^## ' + re.escape(title) + r'.*?\n(.*?)(?=^## |\Z)', text, re.S | re.M)
    return m.group(1) if m else ''


def human(n):
    n = float(n)
    for unit, d in (('B', 1e9), ('M', 1e6), ('K', 1e3)):
        if n >= d:
            return f'{n / d:.2f}'.rstrip('0').rstrip('.') + unit
    return str(int(n))


def words(n):
    """1047582944 -> '1.05 billion', 1963760 -> '2 million'."""
    n = float(n)
    for unit, d, nd in (('billion', 1e9, 2), ('million', 1e6, 1), ('thousand', 1e3, 0)):
        if n >= d:
            return f'{n / d:.{nd}f}'.rstrip('0').rstrip('.') + ' ' + unit
    return str(int(n))


# ---------------------------------------------------------------- token section (built after data load)
def token_section(tokens):
    t = tokens.get('total') or {}
    if not t:
        return '<p class="note">No token counts yet.</p>'
    allt = t.get('all_tokens') or 0
    fresh = t.get('fresh_tokens_in_out') or ((t.get('input_tokens') or 0) + (t.get('output_tokens') or 0))
    reads = t.get('cache_read_input_tokens') or 0
    writes = t.get('cache_creation_input_tokens') or 0
    share = (100 * reads / allt) if allt else 0
    msgs = t.get('assistant_messages') or 0
    tiles = [
        (human(allt), 'tokens processed in total'),
        (human(fresh), 'new text written and read (input + output)'),
        (f'{share:.0f}%', 'were cheap cache re-reads of the same context'),
        (human(msgs), 'AI replies, counting helper agents'),
    ]
    tile_html = ''.join(f'<div class="stat"><b>{html.escape(a)}</b><span>{html.escape(b)}</span></div>' for a, b in tiles)
    rows = []
    for line in (read('Docs/AUTODRIVE_LOG.md') or '').splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 6 and cells[0].isdigit():
            rows.append(cells)
    table = ''
    if rows:
        body = ''.join(f'<tr><td>{html.escape(r[0])}</td><td>{html.escape(r[1])}</td><td>{html.escape(r[2])} min</td><td>{html.escape(r[4])}</td><td>{html.escape(r[5])}</td></tr>' for r in rows[-12:])
        table = ('<h3 style="margin-top:32px">Work sessions</h3><p class="note">Since the switch to fresh sessions, the work runs in chunks. '
                 'Each row is one chunk: how long it ran, how many AI turns it took, and the cost the tool reported.</p>'
                 f'<table class="tok"><thead><tr><th>#</th><th>Started (UTC)</th><th>Length</th><th>Turns</th><th>Reported cost (USD)</th></tr></thead><tbody>{body}</tbody></table>')
    when = html.escape(str(tokens.get('generated_utc') or '')[:16].replace('T', ' '))
    return (f'<div class="stats">{tile_html}</div>'
            '<div class="prose"><p>Every time the AI takes a step it re-reads its working context. Those re-reads come from a cache and cost far less than new text, '
            'so the number that matters most is the new text. Fresh, short work sessions keep the re-reads small.</p>'
            f'<p class="note">Counted from the session records{" on " + when + " UTC" if when else ""}; refreshed every time this page is built.</p></div>'
            + table)


# ---------------------------------------------------------------- data
stats = json.loads(read('Docs/STATS.json') or '{}')
try:  # always-fresh token numbers (owner request): recount from the transcripts before building
    subprocess.run([sys.executable, '-I', str(ROOT / 'scripts' / 'token_usage.py')], cwd=ROOT, capture_output=True, timeout=180)
except Exception:
    pass
tokens = json.loads(read('Docs/TOKENS.json') or '{}')

git = subprocess.run(['git', 'log', '--reverse', '--format=%h|%cI|%s'], cwd=ROOT, capture_output=True, text=True, encoding='utf8').stdout
commits = []
for line in git.splitlines():
    p = line.split('|', 2)
    if len(p) == 3:
        commits.append((p[0], datetime.datetime.fromisoformat(p[1]).astimezone(datetime.timezone.utc), p[2]))

elapsed_h = stats.get('elapsed_minutes', 0) / 60
if commits:
    start = datetime.datetime.strptime((stats.get('run_started_utc') or commits[0][1].strftime('%Y-%m-%d %H:%M')), '%Y-%m-%d %H:%M').replace(tzinfo=datetime.timezone.utc)
    elapsed_h = max(elapsed_h, (commits[-1][1] - start).total_seconds() / 3600)
loc = stats.get('lines_of_code', {})
loc_total = loc.get('ts_tsx', 0) + loc.get('css', 0)
spend = stats.get('spend', {})
spend_total = (spend.get('primary', 0) or 0) + (spend.get('secondary', 0) or 0)
tt = tokens.get('total', {})
cache_pct = (tt.get('cache_read_input_tokens', 0) / tt['all_tokens'] * 100) if tt.get('all_tokens') else 0
tok_when = ''
if tokens.get('generated_utc'):
    try:
        tok_when = datetime.datetime.strptime(tokens['generated_utc'], '%Y-%m-%d %H:%M').strftime('%d %B').lstrip('0')
    except ValueError:
        tok_when = tokens['generated_utc']

PLACEHOLDERS = {
    'hours': f'{elapsed_h:.0f}',
    'commits': str(len(commits)),
    'tokens_all': words(tt.get('all_tokens', 0)) if tt else 'an unrecorded number of',
    'tokens_fresh': words(tt.get('fresh_tokens_in_out', 0)) if tt else 'n/a',
    'cache_pct': f'{cache_pct:.0f}%' if tt else 'most',
    'tokens_date': tok_when or 'the last count',
}

# ---------------------------------------------------------------- media
if MEDIA.exists():
    shutil.rmtree(MEDIA)
(MEDIA / 'img').mkdir(parents=True)
(MEDIA / 'video').mkdir(parents=True)
_img_cache = {}


def add_image(src):
    """Copy (resize to <=1280 px JPEG) one image into media/img; return (rel_src, w, h) or None."""
    src = pathlib.Path(src)
    if not src.is_absolute():
        src = ROOT / src
    if not src.is_file():
        return None
    if src in _img_cache:
        return _img_cache[src]
    name = re.sub(r'[^A-Za-z0-9_.-]', '_', src.parent.name + '_' + src.stem) + ('.jpg' if Image else src.suffix)
    dst = MEDIA / 'img' / name
    w = h = 0
    if Image:
        im = Image.open(src).convert('RGB')
        if im.width > 1280:
            im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
        im.save(dst, 'JPEG', quality=80, optimize=True)
        w, h = im.size
    else:
        shutil.copy2(src, dst)
    _img_cache[src] = (f'media/img/{name}', w, h)
    return _img_cache[src]


def first_image(spec):
    """'a.png | b.png' -> the first file that exists, copied."""
    for p in [s.strip() for s in spec.split('|') if s.strip()]:
        r = add_image(p)
        if r:
            return r
    return None


def img_tag(r, alt, cls=''):
    rel, w, h = r
    dims = f' width="{w}" height="{h}"' if w else ''
    c = f' class="{cls}"' if cls else ''
    return f'<img{c} loading="lazy" decoding="async" src="{rel}" alt="{E(alt)}"{dims}>'


# ---------------------------------------------------------------- story parser
story = read('Docs/progress_story.md')
story = re.sub(r'<!--.*?-->', '', story, flags=re.S)
for k, v in PLACEHOLDERS.items():
    story = story.replace('{' + k + '}', v)


def blocks(text):
    """Paragraphs, '- ' bullets, pipe tables and '### ' headings -> HTML."""
    out, para, items, rows = [], [], [], []

    def flush():
        nonlocal para, items, rows
        if para:
            out.append(f'<p>{md(" ".join(para))}</p>')
        if items:
            out.append('<ul>' + ''.join(f'<li>{md(i)}</li>' for i in items) + '</ul>')
        if rows:
            body = [r for r in rows if not re.match(r'^[\s:|-]+$', '|'.join(r))]
            head, rest = body[0], body[1:]
            out.append('<div class="scroll"><table><thead><tr>' + ''.join(f'<th>{md(c)}</th>' for c in head) + '</tr></thead><tbody>'
                       + ''.join('<tr>' + f'<th>{md(r[0])}</th>' + ''.join(f'<td>{md(c)}</td>' for c in r[1:]) + '</tr>' for r in rest)
                       + '</tbody></table></div>')
        para, items, rows = [], [], []

    for line in text.splitlines():
        s = line.strip()
        if not s:
            flush()
        elif s.startswith('### '):
            flush()
            out.append(f'<h3>{md(s[4:])}</h3>')
        elif s.startswith('- '):
            if para or rows:
                flush()
            items.append(s[2:])
        elif s.startswith('|'):
            if para or items:
                flush()
            rows.append([c.strip() for c in s.strip('|').split('|')])
        else:
            if items or rows:
                flush()
            para.append(s)
    flush()
    return ''.join(out)


def subsections(text):
    """'### Title' chunks -> [(title, body)]."""
    parts = re.split(r'^### (.+)$', text, flags=re.M)
    return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts) - 1, 2)]


page_title = (re.search(r'^# (.+)$', story, re.M) or [None, '{{GAME_NAME}}: how the game was made'])[1].strip()

# hero facts
facts = ''
for line in section(story, 'At a glance').splitlines():
    m = re.match(r'^- \*\*(.+?)\*\*\s*\|\s*(.+)$', line.strip())
    if m:
        facts += f'<div class="fact"><b>{md(m.group(1))}</b><span>{md(m.group(2))}</span></div>'

# the game today
oneline = blocks(section(story, '{{GAME_NAME}} in one paragraph'))
groups = ''
for title, body in subsections(section(story, 'What you can do in the game now')):
    groups += f'<div class="group"><h3>{md(title)}</h3>{blocks(body)}</div>'
limits = blocks(section(story, 'Not perfect yet'))

# milestone cards
cards_html = ''
miles = subsections(section(story, 'Milestones'))
for n, (title, body) in enumerate(miles, 1):
    meta, rest = {}, []
    for line in body.splitlines():
        m = re.match(r'^(Date|Image|Why):\s*(.+)$', line.strip())
        if m:
            meta[m.group(1).lower()] = m.group(2).strip()
        else:
            rest.append(line)
    pic = first_image(meta['image']) if meta.get('image') else None
    fig = (f'<a class="shot" href="{pic[0]}">{img_tag(pic, title)}</a>' if pic else '<div class="shot none"></div>')
    why = f'<p class="why"><span>Why</span> {md(meta["why"])}</p>' if meta.get('why') else ''
    cards_html += (f'<article class="card">{fig}<div class="cbody"><p class="when"><span class="num">{n:02d}</span> {E(meta.get("date", ""))}</p>'
                   f'<h3>{md(title)}</h3>{blocks(chr(10).join(rest))}{why}</div></article>')

scores = blocks(section(story, 'How the reviewers scored it over time'))
built = blocks(section(story, 'How it was built'))
gloss = ''
for line in section(story, 'Glossary').splitlines():
    m = re.match(r'^- \*\*(.+?)\*\*:\s*(.+)$', line.strip())
    if m:
        gloss += f'<dt>{md(m.group(1))}</dt><dd>{md(m.group(2))}</dd>'

gallery = ''
for line in section(story, 'Gallery').splitlines():
    m = re.match(r'^- (.+?)\s*\|\s*(.+)$', line.strip())
    if m:
        r = add_image(m.group(1))
        if r:
            gallery += f'<figure><a href="{r[0]}">{img_tag(r, m.group(2))}</a><figcaption>{md(m.group(2))}</figcaption></figure>'

# plain-words build panel
panel = [
    (f'about {elapsed_h:.0f} hours', 'of building, around the clock', 'started ' + (datetime.datetime.strptime(stats['run_started_utc'], '%Y-%m-%d %H:%M').strftime('%d %b, %H:%M UTC').lstrip('0') if stats.get('run_started_utc') else 'at the first commit')),
    (f'{len(commits)}', 'saved changes', 'each one tested first'),
    (f'about {loc_total / 1000:.0f},000', 'lines of code', f'plus about {loc.get("json_data_approx", 0):,} lines of game data'),
    (f'{spend_total:g} USD', 'spent on art', 'budget was 25 USD; all art drawn in code'),
]
if tt:
    panel.append((words(tt.get('all_tokens', 0)), 'tokens read and written',
                  f'only {words(tt.get("fresh_tokens_in_out", 0))} were new; {cache_pct:.0f}% were cheap re-reads (as of {tok_when})'))
if stats.get('bugs_fixed'):
    panel.append((f'{stats["bugs_fixed"]}+', 'bugs found and fixed', 'logged as they were found'))
panel_html = ''.join(f'<div class="stat"><b>{E(a)}</b><span>{E(b)}</span><i>{E(c)}</i></div>' for a, b, c in panel)

# ---------------------------------------------------------------- videos
rec = DOCS / 'recording'
trailers = sorted(rec.glob('trailer-*.mp4'), reverse=True)
gameplay = [f for f in sorted(rec.glob('gameplay-*'), reverse=True)[:1] if f.suffix in ('.mp4', '.webm')]


def when_of(f):
    m = re.search(r'(\d{8})-(\d{4})', f.stem)
    return datetime.datetime.strptime(m.group(1) + m.group(2), '%Y%m%d%H%M').strftime('%d %b, %H:%M UTC').lstrip('0') if m else f.stem


for f in trailers + gameplay:
    shutil.copy2(f, MEDIA / 'video' / f.name)
vid_main, vid_list = '', ''
if trailers:
    f = trailers[0]
    poster = first_image('Docs/reviews/playtest4-shots/32-sword-cue-0.png | Docs/progress/title/20261010-030553__title-desktop-m6b.png')
    pattr = f' poster="{poster[0]}"' if poster else ''
    vid_main = (f'<figure class="vmain"><video controls preload="none" playsinline{pattr} src="media/video/{E(f.name)}"></video>'
                f'<figcaption>The newest trailer (number {len(trailers)}), recorded {E(when_of(f))}. Shows every current feature with captions.</figcaption></figure>')
older = [(f, f'Trailer {len(trailers) - i}') for i, f in enumerate(trailers) if i > 0] + [(f, 'Gameplay recording, about 3 minutes') for f in gameplay]
for f, label in older:
    vid_list += (f'<li><a href="media/video/{E(f.name)}">{E(label)}</a> <span>{E(when_of(f))} · {f.stat().st_size / 1e6:.0f} MB</span></li>')

# ---------------------------------------------------------------- technical log (raw records)
tok_table = ''
if tokens:
    def row(name, g):
        return (f"<tr><th>{name}</th><td>{g['assistant_messages']:,}</td><td>{g['tool_calls']:,}</td><td>{g['input_tokens']:,}</td>"
                f"<td>{g['output_tokens']:,}</td><td>{g['cache_creation_input_tokens']:,}</td><td>{g['cache_read_input_tokens']:,}</td></tr>")
    tok_table = ('<div class="scroll"><table class="raw"><thead><tr><th></th><th>messages</th><th>tool calls</th><th>input</th><th>output</th><th>cache write</th><th>cache read</th></tr></thead><tbody>'
                 + row('Main session(s)', tokens['main']) + row(f"Subagents ({tokens['subagents']['files']})", tokens['subagents']) + row('Total', tokens['total'])
                 + f"</tbody></table></div><p class=\"note\">{E(tokens.get('method', ''))} Generated {E(tokens.get('generated_utc', ''))} UTC.</p>")

per_hour = collections.OrderedDict()
if commits:
    h = commits[0][1].replace(minute=0, second=0, microsecond=0)
    while h <= commits[-1][1]:
        per_hour[h] = 0
        h += datetime.timedelta(hours=1)
    for _, t, _ in commits:
        per_hour[t.replace(minute=0, second=0, microsecond=0)] += 1
mx = max(per_hour.values() or [1])
bw, gap, ch = 22, 4, 120
svg_w = len(per_hour) * (bw + gap) + 8
bars = []
for i, (h, n) in enumerate(per_hour.items()):
    bh = round(n / mx * (ch - 36))
    x = 4 + i * (bw + gap)
    bars.append(f'<rect x="{x}" y="{ch - 16 - bh}" width="{bw}" height="{bh}" rx="2" fill="#6fd3a8"><title>{h:%d %b %H:00} UTC: {n} commits</title></rect>')
    bars.append(f'<text x="{x + bw / 2}" y="{ch - 19 - bh}" text-anchor="middle" font-size="9" fill="#ece6d8">{n}</text>')
    if i % 3 == 0:
        bars.append(f'<text x="{x + bw / 2}" y="{ch - 3}" text-anchor="middle" font-size="9" fill="#9fb3a9">{h:%H}h</text>')
chart = (f'<div class="scroll"><svg role="img" aria-label="Commits per hour (UTC)" viewBox="0 0 {svg_w} {ch}" width="{svg_w}" height="{ch}">{"".join(bars)}</svg></div>'
         f'<p class="note">Commits per UTC hour, {commits[0][1]:%d %b %H:%M} to {commits[-1][1]:%d %b %H:%M}.</p>') if commits else ''
commit_list = ''.join(f'<li><code>{c}</code> <time>{t:%d %b %H:%M}</time> {E(s)}</li>' for c, t, s in commits)

dev = []
for line in read('Docs/DEVLOG.md').splitlines():
    m = re.match(r'^(?:###\s+)?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC\s+[—-]\s+(.*?)\s+[—-]\s+(.*)$', line)
    if m:
        dev.append(list(m.groups()))
    elif dev and line.strip() and not line.startswith('#') and not line.startswith('<!--'):
        dev[-1][2] += ' ' + line.strip()
timeline = ''
for when, title, body in dev:
    short = body if len(body) <= 260 else body[:260].rsplit(' ', 1)[0] + ' …'
    more = f'<details><summary>full entry</summary><p>{md(body)}</p></details>' if short != body else ''
    timeline += f'<li><time>{E(when)} UTC</time><h4>{md(title)}</h4><p>{md(short)}</p>{more}</li>'

plan = read('Docs/PLAN.md')
mrows = ''.join(f'<tr><th>{md(r[0])}</th><td>{md(r[1])}</td><td>{md(r[2])}</td></tr>'
                for r in table_rows(plan) if len(r) >= 3 and re.match(r'M\d', r[0]))
itrows = ''
for r in table_rows(read('Docs/ITERATIONS.md')):
    if len(r) >= 5 and (r[0].isdigit() or re.match(r'\d{4}-\d{2}-\d{2}', r[0])):
        itrows += '<tr>' + ''.join(f'<td>{md(c)}</td>' for c in r[:5]) + '</tr>'
mile_html = ('<div class="scroll"><table class="raw"><thead><tr><th>Milestone</th><th>Status</th><th>Gate</th></tr></thead><tbody>' + mrows + '</tbody></table></div>'
             '<div class="scroll"><table class="raw"><tbody>' + itrows + '</tbody></table></div>')

decs = []
for line in read('Docs/DECISIONS.md').splitlines():
    m = re.match(r'^(\d{4}-\d{2}-\d{2})(?: (\d{2}:\d{2}))? - (.*)$', line)
    if m:
        decs.append([m.group(1), m.group(2) or '', m.group(3)])
    elif decs and (line.startswith(' ') or line.startswith('- ')):
        decs[-1][2] += ' ' + line.strip()
dec_html = ''
for _, (d, t, txt) in sorted(enumerate(decs), key=lambda x: (x[1][0], x[1][1], x[0]), reverse=True):
    cut = re.search(r'[.:] ', txt[:170])
    if cut and cut.end() > 30:
        head, rest = txt[:cut.end() - 1], txt[cut.end() - 1:].strip()
    elif len(txt) > 130:
        head, rest = txt[:130].rsplit(' ', 1)[0] + ' …', txt
    else:
        head, rest = txt, ''
    dec_html += (f'<article class="dec" data-s="{E((d + " " + t + " " + txt).lower())}"><time>{d} {t}</time><h4>{md(head)}</h4>'
                 + (f'<details><summary>reasoning and numbers</summary><p>{md(rest)}</p></details>' if rest else '') + '</article>')

revs = ''
for f in sorted((DOCS / 'reviews').glob('*.md'), reverse=True):
    txt = f.read_text(encoding='utf8', errors='replace')
    lines = [l for l in txt.splitlines() if l.strip()]
    title = lines[0].lstrip('# ').strip() if lines else f.stem
    revs += (f'<article class="rev"><time>{E(f.stem[:13])}</time><h4>{md(title)}</h4>'
             f'<details><summary>read the review</summary><pre>{E(txt)}</pre></details></article>')

# ---------------------------------------------------------------- fonts (the site's own copies, if built)
fonts = ''
assets = OUT.parent / 'assets'
for fam, pat, extra in (('Cormorant Garamond', 'cormorant-garamond-latin-600-normal-*.woff2', 'font-weight: 600;'),
                        ('Inter', 'inter-latin-wght-normal-*.woff2', 'font-weight: 100 900;')):
    fs = sorted(assets.glob(pat)) if assets.exists() else []
    if fs:
        fonts += f"@font-face {{ font-family: '{fam}'; src: url('../assets/{fs[0].name}') format('woff2'); {extra} font-display: swap; }}\n"

# ---------------------------------------------------------------- page
NAV = [('today', 'The game'), ('milestones', 'Milestones'), ('scores', 'Scores'), ('videos', 'Videos'),
       ('screenshots', 'Screenshots'), ('built', 'How it was built'), ('tokens', 'Tokens'), ('log', 'Technical log')]
nav = ''.join(f'<a href="#{a}">{b}</a>' for a, b in NAV)
now = datetime.datetime.now(datetime.timezone.utc)
page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{GAME_NAME}} Progress</title>
<meta name="description" content="How {{GAME_NAME}} was made: what the game is, what changed at each step, how reviewers scored it, and how AI agents built it.">
<link rel="icon" href="../favicon.svg">
<style>
{fonts}  :root {{ --ink: #0a0d0c; --ink2: #111916; --ink3: #17211d; --line: #26332d; --paper: #ece6d8; --mist: #a9bbb2; --jade: #6fd3a8; --gold: #d8b46a;
           --serif: 'Cormorant Garamond', Georgia, 'Times New Roman', serif; --sans: Inter, system-ui, -apple-system, 'Segoe UI', sans-serif; }}
  * {{ box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; scroll-padding-top: 64px; -webkit-text-size-adjust: 100%; }}
  body {{ margin: 0; background-color: #0a0d0c; background-image: radial-gradient(ellipse at 50% 0%, #17231e, #0a0d0c 55%); background-repeat: no-repeat;
         color: var(--paper); font: 18px/1.6 var(--sans); overflow-wrap: break-word; }}
  main {{ max-width: 1160px; margin: 0 auto; padding: 0 16px 80px; }}
  .prose {{ max-width: 70ch; }}
  a {{ color: var(--jade); }}
  h1, h2, h3 {{ font-family: var(--serif); font-weight: 600; letter-spacing: .005em; }}
  h2 {{ font-size: clamp(32px, 5vw, 44px); line-height: 1.1; margin: 0 0 10px; }}
  h3 {{ font-size: 25px; line-height: 1.2; margin: 0 0 8px; }}
  section {{ margin-top: 96px; }}
  .kicker {{ color: var(--jade); letter-spacing: .2em; text-transform: uppercase; font-size: 14px; font-weight: 600; margin: 0 0 6px; }}
  .sub {{ color: var(--mist); font-size: 19px; margin: 0 0 32px; max-width: 70ch; }}
  .note {{ color: var(--mist); font-size: 15px; }}
  nav {{ position: sticky; top: 0; z-index: 5; background: rgba(10,13,12,.95); border-bottom: 1px solid var(--line); backdrop-filter: blur(6px); }}
  nav div {{ max-width: 1160px; margin: 0 auto; padding: 10px 16px; display: flex; gap: 4px 20px; overflow-x: auto; scrollbar-width: none; font-size: 15px; white-space: nowrap; }}
  nav div::-webkit-scrollbar {{ display: none; }}
  nav a {{ text-decoration: none; color: var(--mist); }} nav a:hover {{ color: var(--jade); }}

  header.hero {{ padding: 72px 0 8px; }}
  .hero h1 {{ font-size: clamp(44px, 9vw, 84px); line-height: 1; margin: 4px 0 18px; }}
  .hero .lede {{ font-size: clamp(19px, 2.4vw, 22px); color: var(--paper); max-width: 60ch; margin: 0 0 28px; }}
  .facts {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr)); gap: 16px; margin: 36px 0 8px; }}
  .fact {{ background: var(--ink2); border: 1px solid var(--line); border-top: 3px solid var(--jade); border-radius: 12px; padding: 18px 20px; }}
  .fact b {{ display: block; font-family: var(--serif); font-size: 40px; line-height: 1.05; color: var(--jade); }}
  .fact b strong {{ font-weight: 600; }}
  .fact span {{ display: block; color: var(--mist); font-size: 16px; margin-top: 6px; line-height: 1.45; }}
  .btn {{ display: inline-block; padding: 12px 22px; border-radius: 10px; background: #1f6b52; color: var(--paper); text-decoration: none; font-weight: 600; border: 1px solid var(--jade); margin: 0 10px 10px 0; font-size: 17px; }}
  .btn.ghost {{ background: transparent; }}

  .groups {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 320px), 1fr)); gap: 20px; margin-top: 28px; }}
  .group {{ background: var(--ink2); border: 1px solid var(--line); border-radius: 12px; padding: 20px 22px 8px; }}
  .group h3 {{ color: var(--jade); font-size: 24px; }}
  .group:last-child:nth-child(3n+1) {{ grid-column: 1 / -1; }} .group:last-child:nth-child(3n+1) ul {{ columns: 2 300px; column-gap: 40px; }}
  .group:last-child:nth-child(3n+1) li {{ break-inside: avoid; }}
  ul {{ padding-left: 1.2em; margin: 0 0 14px; }} li {{ margin: 0 0 8px; }} li::marker {{ color: var(--jade); }}
  .limits {{ margin-top: 28px; background: #18140d; border: 1px solid #4a3d22; border-left: 4px solid var(--gold); border-radius: 12px; padding: 20px 24px 8px; }}
  .limits h3 {{ color: var(--gold); }}
  .limits ul {{ max-width: 75ch; }}

  .cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 340px), 1fr)); gap: 32px; margin-top: 28px; }}
  .card {{ background: var(--ink2); border: 1px solid var(--line); border-radius: 14px; overflow: hidden; display: flex; flex-direction: column; }}
  .card .shot {{ display: block; aspect-ratio: 16 / 10; background: #000; border-bottom: 1px solid var(--line); overflow: hidden; }}
  .card .shot img {{ width: 100%; height: 100%; object-fit: cover; object-position: top center; display: block; transition: transform .3s; }}
  .card .shot:hover img {{ transform: scale(1.03); }}
  .cbody {{ padding: 20px 22px 18px; display: flex; flex-direction: column; flex: 1; }}
  .card p {{ margin: 0 0 12px; }}
  .card ul {{ font-size: 16.5px; color: #dcd6c8; }}
  .when {{ color: var(--mist); font-size: 14px; letter-spacing: .03em; }}
  .num {{ display: inline-block; color: var(--ink); background: var(--jade); font-weight: 700; border-radius: 6px; padding: 0 7px; margin-right: 6px; font-size: 13px; }}
  .why {{ margin-top: auto !important; padding-top: 12px; border-top: 1px dashed var(--line); color: var(--mist); font-size: 15.5px; font-style: italic; }}
  .why span {{ font-style: normal; font-weight: 700; color: var(--gold); text-transform: uppercase; letter-spacing: .1em; font-size: 12px; margin-right: 4px; }}

  .scroll {{ overflow-x: auto; max-width: 100%; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 16px; }}
  th, td {{ border-bottom: 1px solid var(--line); padding: 10px 12px; text-align: left; vertical-align: top; }}
  thead th {{ color: var(--mist); font-weight: 600; font-size: 14px; }}
  tbody th {{ font-weight: 600; }}
  #scores table {{ max-width: 820px; }}
  #scores td {{ text-align: center; font-size: 21px; font-weight: 700; font-variant-numeric: lining-nums tabular-nums; vertical-align: middle; }}
  #scores tbody th {{ vertical-align: middle; }}
  #scores thead th:not(:first-child) {{ text-align: center; }}
  #scores td.s8, #scores td.s9 {{ color: var(--jade); }} #scores td.s5, #scores td.s4 {{ color: #e59a7f; }}
  table.raw {{ font-size: 13px; min-width: 520px; }}

  .vmain {{ margin: 24px 0 0; }}
  .vmain video {{ width: 100%; max-width: 960px; aspect-ratio: 16 / 10; background: #000; border-radius: 12px; border: 1px solid var(--line); display: block; }}
  figcaption {{ color: var(--mist); font-size: 15px; margin-top: 8px; }}
  ul.older {{ list-style: none; padding: 0; margin: 18px 0 0; columns: 2 260px; font-size: 16px; }}
  ul.older li {{ break-inside: avoid; }} ul.older span {{ color: var(--mist); font-size: 14px; }}

  .gallery {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(min(44%, 250px), 1fr)); gap: 20px 14px; margin-top: 24px; }}
  .gallery figure {{ margin: 0; }}
  .gallery img {{ width: 100%; height: auto; aspect-ratio: 16 / 10; object-fit: cover; object-position: top center; border-radius: 10px; border: 1px solid var(--line); display: block; background: #000; }}

  .stats {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 300px), 1fr)); gap: 14px; margin: 28px 0; }}
  .stat {{ background: var(--ink2); border: 1px solid var(--line); border-radius: 12px; padding: 16px 18px; }}
  .stat b {{ display: block; font-family: var(--serif); font-size: 32px; color: var(--jade); line-height: 1.1; }}
  .stat span {{ display: block; font-size: 16px; }} .stat i {{ display: block; font-style: normal; color: var(--mist); font-size: 14px; margin-top: 4px; line-height: 1.4; }}
  #built ul {{ list-style: none; padding: 0; }} #built li {{ margin-bottom: 14px; }}
  dl {{ display: grid; grid-template-columns: minmax(0, 12em) minmax(0, 1fr); gap: 10px 24px; margin: 20px 0 0; max-width: 80ch; }}
  dt {{ font-weight: 700; color: var(--jade); }} dd {{ margin: 0; }}
  @media (max-width: 560px) {{ dl {{ grid-template-columns: minmax(0, 1fr); gap: 2px; }} dd {{ margin-bottom: 12px; }} section {{ margin-top: 72px; }} }}

  details.log {{ margin-top: 20px; background: var(--ink2); border: 1px solid var(--line); border-radius: 12px; padding: 14px 18px; font-size: 15px; }}
  details.log > summary {{ font-family: var(--serif); font-size: 24px; color: var(--paper); cursor: pointer; }}
  details.log h3 {{ margin-top: 28px; font-size: 22px; }}
  details.log h4 {{ margin: 2px 0 4px; font-size: 15px; }}
  summary {{ cursor: pointer; color: var(--mist); }}
  code {{ background: #1a2420; padding: 1px 5px; border-radius: 4px; font-size: .9em; overflow-wrap: anywhere; }}
  ol.tl {{ list-style: none; margin: 0; padding: 0 0 0 18px; border-left: 2px solid var(--line); }}
  ol.tl li {{ position: relative; margin: 0 0 16px; padding-left: 14px; }}
  ol.tl li::before {{ content: ''; position: absolute; left: -25px; top: 8px; width: 10px; height: 10px; border-radius: 50%; background: var(--jade); }}
  ol.tl p {{ margin: 0; color: var(--mist); font-size: 14px; }}
  time {{ color: var(--jade); font-size: 12px; letter-spacing: .06em; }}
  .dec, .rev {{ border-bottom: 1px solid var(--line); padding: 8px 0; }}
  .dec p {{ color: var(--mist); font-size: 14px; }}
  #q {{ width: 100%; max-width: 480px; padding: 10px 12px; border-radius: 8px; border: 1px solid var(--line); background: var(--ink3); color: var(--paper); font: inherit; }}
  pre {{ white-space: pre-wrap; font: 12px/1.45 ui-monospace, Consolas, monospace; color: var(--mist); background: var(--ink); padding: 10px; border-radius: 8px; max-height: 420px; overflow: auto; }}
  ul.commits {{ list-style: none; padding: 0; margin: 8px 0; font-size: 13px; max-height: 480px; overflow: auto; color: var(--mist); }}
  ul.commits li {{ margin: 0; padding: 2px 0; }} ul.commits time {{ margin: 0 6px; }}
  footer {{ color: var(--mist); font-size: 14px; margin-top: 64px; border-top: 1px solid var(--line); padding-top: 16px; }}
  @media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} .card .shot img {{ transition: none; }} }}
table.tok {{ width: 100%; border-collapse: collapse; font-size: 15px; }}
table.tok th, table.tok td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid rgba(255,255,255,0.08); }}
@media (max-width: 520px) {{ table.tok {{ font-size: 13px; }} table.tok th:nth-child(2), table.tok td:nth-child(2) {{ display: none; }} }}
</style>
</head>
<body>
<nav aria-label="Sections"><div>{nav}</div></nav>
<main>
  <header class="hero">
    <p class="kicker">Progress report</p>
    <h1>{md(page_title)}</h1>
    <p class="lede">An idle cultivation game, built from scratch by AI agents working on their own. This page tells the story in plain words: what the game is, what changed at each step, and how it was checked.</p>
    <a class="btn" href="../">Play {{GAME_NAME}}</a><a class="btn ghost" href="#videos">Watch the trailer</a>
    <div class="facts">{facts}</div>
  </header>

  <section id="today">
    <p class="kicker">The game today</p>
    <h2>{{GAME_NAME}} in one paragraph</h2>
    <div class="prose">{oneline}</div>
    <h2 style="margin-top:56px">What you can do in the game now</h2>
    <div class="groups">{groups}</div>
    <div class="limits"><h3>Not perfect yet</h3>{limits}</div>
  </section>

  <section id="milestones">
    <p class="kicker">Step by step</p>
    <h2>How the game grew</h2>
    <p class="sub">{len(miles)} steps, from the first playable version to today. Times are in UTC. Tap a picture to see it full size.</p>
    <div class="cards">{cards_html}</div>
  </section>

  <section id="scores">
    <p class="kicker">Independent opinions</p>
    <h2>How the reviewers scored it over time</h2>
    <div class="prose">{scores}</div>
  </section>

  <section id="videos">
    <p class="kicker">Watch</p>
    <h2>Videos</h2>
    {vid_main}
    {'<h3 style="margin-top:28px">Older trailers</h3><ul class="older">' + vid_list + '</ul>' if vid_list else ''}
  </section>

  <section id="screenshots">
    <p class="kicker">Look</p>
    <h2>Screenshots</h2>
    <p class="sub">Taken from the running game on a desktop and a phone, plus the art sheets the agents drew. Nobody but the AI reviewers has judged the look yet.</p>
    <div class="gallery">{gallery}</div>
  </section>

  <section id="built">
    <p class="kicker">Behind the scenes</p>
    <h2>How it was built</h2>
    <div class="stats">{panel_html}</div>
    <div class="prose">{built}</div>
    <h3 style="margin-top:40px">A few words this page uses</h3>
    <dl>{gloss}</dl>
  </section>

  <section id="tokens">
    <p class="kicker">Cost of thinking</p>
    <h2>Token usage</h2>
    {token_section(tokens)}
  </section>

  <section id="log">
    <details class="log">
      <summary>Technical log (for the curious)</summary>
      <p class="note">The raw working records, as the agents wrote them. They use internal shorthand.</p>
      <h3>Token counts</h3>{tok_table}
      <h3>Saved changes per hour</h3>{chart}
      <details><summary>All {len(commits)} commits</summary><ul class="commits">{commit_list}</ul></details>
      <h3>Milestone table</h3>{mile_html}
      <h3>Development log</h3><ol class="tl">{timeline}</ol>
      <h3>Decisions</h3><p class="note">{len(decs)} dated entries, newest first.</p>
      <input id="q" type="search" placeholder="Filter decisions (for example: karma, trailer)" aria-label="Filter decisions"> <span id="qc" class="note"></span>
      <div id="decs">{dec_html}</div>
      <h3>Independent reviews</h3>{revs}
    </details>
  </section>
  <footer>Built {now:%d %b %Y, %H:%M} UTC from the project's own records. All visuals are pending the owner's review.</footer>
</main>
<script>
(function () {{
  document.querySelectorAll('#scores td').forEach(function (td) {{ var n = parseInt(td.textContent, 10); if (n) td.className = 's' + n; }});
  var q = document.getElementById('q'), items = document.querySelectorAll('#decs .dec'), c = document.getElementById('qc');
  if (!q) return;
  q.addEventListener('input', function () {{ var t = q.value.trim().toLowerCase(), n = 0;
    items.forEach(function (e) {{ var ok = !t || e.getAttribute('data-s').indexOf(t) >= 0; e.hidden = !ok; if (ok) n++; }});
    c.textContent = t ? n + ' of ' + items.length + ' match' : ''; }});
}})();
</script>
</body>
</html>
'''
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'index.html').write_text(page, encoding='utf8')
size = sum(f.stat().st_size for f in MEDIA.rglob('*') if f.is_file())
print(f'site-dist/progress ready: {len(miles)} milestone cards, {len(list((MEDIA / "img").iterdir()))} images, '
      f'{len(list((MEDIA / "video").iterdir()))} videos, media {size / 1e6:.1f} MB, {len(commits)} commits, {len(dev)} devlog entries, {len(decs)} decisions')

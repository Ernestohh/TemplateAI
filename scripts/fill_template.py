#!/usr/bin/env python3
"""Fill the simple placeholders of a project created from the web-game template (SETUP.md step 2).

  python -I scripts/fill_template.py project.json          fill in place (run from the new project folder)
  python -I scripts/fill_template.py project.json --dry-run show what would change, write nothing
  python -I scripts/fill_template.py --check               only report what is still unfilled

project.json uses the placeholder names as keys (see project.example.json). Only GAME_NAME, GENRE, SETTING_SHORT,
ONE_PARAGRAPH_PITCH, TAGLINE, DEV_PORT, PREVIEW_PORT and GITHUB_REMOTE are required; the rest has defaults derived
from the name (slug, domain, env variable names, folders) or generic values (budget 0, milestone names).

What it does:
  1. replaces every simple double-brace placeholder in the text files of the project;
  2. renames README.project.md to README.md and moves the template-only files (QUESTIONS.md, SETUP.md,
     project.example.json) and project.json into Docs/setup/ (a project.json outside the folder is copied);
  3. lists the rich FILL markers that Claude still has to write from the questionnaire answers.
Exit code: 0 when only FILL markers remain, 1 when a simple placeholder is left or the input is invalid.
Plain-ASCII output (the Windows console is cp1252).
"""
import argparse, datetime, json, pathlib, re, shutil, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEXT_SUFFIXES = {'.md', '.py', '.sh', '.json', '.conf', '.txt', '.ts', '.yml', '.yaml', '.example', ''}
SKIP_DIRS = {'.git', 'node_modules', 'dist', 'site-dist', '.claude/autodrive'}
SELF = pathlib.Path(__file__).resolve()
SIMPLE = re.compile(r'\{\{([A-Z][A-Z0-9_]*)\}\}')
FILL = re.compile(r'\{\{FILL:\s*([^}]*)\}\}')
REQUIRED = ['GAME_NAME', 'GENRE', 'SETTING_SHORT', 'ONE_PARAGRAPH_PITCH', 'TAGLINE', 'DEV_PORT', 'PREVIEW_PORT', 'GITHUB_REMOTE']


def derive(cfg):
    """Complete project.json with defaults; returns the placeholder -> value map."""
    v = {k: str(val) for k, val in cfg.items() if not k.startswith('_')}
    missing = [k for k in REQUIRED if not v.get(k)]
    if missing:
        sys.exit('project.json is missing: ' + ', '.join(missing))
    name = v['GAME_NAME']
    slug = v.setdefault('GAME_SLUG', re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-'))
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', slug):
        sys.exit('GAME_SLUG must be lower-case letters, digits and dashes')
    env = re.sub(r'[^A-Z0-9]+', '_', slug.upper())
    v.setdefault('DOMAIN', f'{slug}.kryptos.gg')
    v.setdefault('DNS_ZONE', v['DOMAIN'].split('.', 1)[1] if '.' in v['DOMAIN'] else v['DOMAIN'])
    v.setdefault('SERVER_IP', '72.62.17.59')
    v.setdefault('SERVER_SSH', 'root@' + v['SERVER_IP'])
    v.setdefault('DEPLOY_DIR', f'/var/www/{slug}')
    v.setdefault('AUTODRIVE_ENV', f'{env}_AUTODRIVE')
    v.setdefault('MODEL_ENV', f'{env}_MODEL')
    win = v.setdefault('PROJECT_DIR_WIN', 'C:\\Users\\ernes\\' + name.replace(' ', ''))
    drive, rest = win.split(':', 1)
    v.setdefault('PROJECT_DIR_POSIX', '/' + drive.lower() + rest.replace('\\', '/'))
    v.setdefault('CLAUDE_PROJECTS_KEY', re.sub(r'[^A-Za-z0-9]', '-', win))
    v.setdefault('TRAILER_LEDE', v['TAGLINE'])
    v.setdefault('BUDGET_USD', '0')
    v.setdefault('LARGE_GATES', 'M2, M5 and M7')
    v.setdefault('ACCEPTANCE_FROM', 'M3')
    v.setdefault('MVP_MILESTONE', 'M7')
    v.setdefault('MVP_TAG', 'm7')
    v.setdefault('SIM_SYSTEMS', 'the core rules, generation, progression and meta')
    v.setdefault('PLAYTEST_AREAS', 'first minutes, core loop readability, signature mechanics, progression, meta and hub, phone, fun')
    v.setdefault('SETUP_DATE', datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M'))
    for p in ('DEV_PORT', 'PREVIEW_PORT'):
        if not v[p].isdigit():
            sys.exit(f'{p} must be a number')
    if v['DEV_PORT'] == v['PREVIEW_PORT']:
        sys.exit('DEV_PORT and PREVIEW_PORT must differ')
    if v['GITHUB_REMOTE'].startswith('git@'):
        sys.exit('GITHUB_REMOTE must be an HTTPS URL (https://github.com/<user>/<repo>.git): this PC has no GitHub SSH key')
    try:
        float(v['BUDGET_USD'])
    except ValueError:
        sys.exit('BUDGET_USD must be a number')
    return v


def check_ports(v):
    """Warn when the ports clash with another project in PORTS.md."""
    reg = ROOT / 'PORTS.md'
    if not reg.exists():
        return
    for line in reg.read_text(encoding='utf8').splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 3 and cells[1].isdigit() and cells[0].lower() != v['GAME_NAME'].lower():
            if {cells[1], cells[2]} & {v['DEV_PORT'], v['PREVIEW_PORT']}:
                print(f'WARNING: ports {v["DEV_PORT"]}/{v["PREVIEW_PORT"]} clash with {cells[0]} in PORTS.md')
    if not re.search(r'^\|\s*' + re.escape(v['GAME_NAME']) + r'\s*\|', reg.read_text(encoding='utf8'), re.M | re.I):
        print(f'note: {v["GAME_NAME"]} is not in PORTS.md yet - add a row there and in the template copy')


def text_files():
    for p in sorted(ROOT.rglob('*')):
        rel = p.relative_to(ROOT).as_posix()
        if not p.is_file() or p.resolve() == SELF or any(rel == d or rel.startswith(d + '/') for d in SKIP_DIRS):
            continue
        if p.suffix.lower() in TEXT_SUFFIXES:
            yield p


def scan():
    simple, fills = [], []
    for p in text_files():
        if p.name in ('QUESTIONS.md', 'SETUP.md') or 'Docs/setup/' in p.as_posix():
            continue
        try:
            lines = p.read_text(encoding='utf8').splitlines()
        except UnicodeDecodeError:
            continue
        rel = p.relative_to(ROOT).as_posix()
        for i, line in enumerate(lines, 1):
            for m in FILL.finditer(line):
                fills.append(f'{rel}:{i}  {m.group(1).strip()}'.replace('§', 'section '))
            for m in SIMPLE.finditer(line):
                simple.append(f'{rel}:{i}  {m.group(0)}')
    return simple, fills


def main():
    try:  # plain output on any Windows console
        sys.stdout.reconfigure(errors='replace')
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('project_json', nargs='?')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    if not a.check:
        if not a.project_json:
            sys.exit('usage: fill_template.py project.json [--dry-run] | --check')
        src = pathlib.Path(a.project_json)
        try:
            cfg = json.loads(src.read_text(encoding='utf8'))
        except Exception as e:
            sys.exit(f'cannot read {src}: {e}')
        v = derive(cfg)
        check_ports(v)
        changed = 0
        for p in text_files():
            if p.name in ('QUESTIONS.md', 'SETUP.md', 'project.example.json') or p.resolve() == src.resolve():
                continue
            try:
                t = p.read_text(encoding='utf8')
            except UnicodeDecodeError:
                continue
            o = t
            if p.suffix == '.json':  # numbers stay numbers in JSON
                t = t.replace('"{{BUDGET_USD}}"', v['BUDGET_USD'])
            t = SIMPLE.sub(lambda m: v.get(m.group(1), m.group(0)), t)
            if t != o:
                changed += 1
                if a.dry_run:
                    print('would fill', p.relative_to(ROOT).as_posix())
                else:
                    p.write_text(t, encoding='utf8', newline='\n')
        print(f'{"would fill" if a.dry_run else "filled"} placeholders in {changed} files')
        if not a.dry_run:
            setup = ROOT / 'Docs' / 'setup'
            setup.mkdir(parents=True, exist_ok=True)
            for name in ('QUESTIONS.md', 'SETUP.md', 'project.example.json'):
                if (ROOT / name).exists():
                    shutil.move(str(ROOT / name), str(setup / name))
            if src.resolve() != (setup / 'project.json').resolve():
                if src.resolve().parent == ROOT:
                    shutil.move(str(src), str(setup / 'project.json'))
                else:
                    shutil.copy2(src, setup / 'project.json')
            if (ROOT / 'README.project.md').exists():
                (ROOT / 'README.project.md').replace(ROOT / 'README.md')
            print('moved QUESTIONS.md, SETUP.md, project.example.json and project.json to Docs/setup/; README.project.md -> README.md')
    simple, fills = scan()
    if simple:
        print(f'\nUNFILLED SIMPLE PLACEHOLDERS ({len(simple)}): add the keys to project.json and run again')
        for s in simple:
            print('  ' + s)
    if fills:
        print(f'\nRich sections left for Claude to write from the questionnaire ({len(fills)} FILL markers):')
        for s in fills:
            print('  ' + s)
    if not simple and not fills:
        print('\nno placeholders left: the project is fully filled')
    sys.exit(1 if simple else 0)


if __name__ == '__main__':
    main()

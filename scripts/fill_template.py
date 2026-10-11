#!/usr/bin/env python3
"""Fill the simple placeholders of a project created from the web-game template (SETUP.md step 2).

  python -I scripts/fill_template.py project.json          fill in place (run from the new project folder)
  python -I scripts/fill_template.py project.json --dry-run show what would change, write nothing
  python -I scripts/fill_template.py --check               only report what is still unfilled
  python -I scripts/fill_template.py --git-identity        set git user.name/user.email from owner.json (after git init)

Two inputs:
  - owner.json (git-ignored, once per machine; copy owner.example.json): projects_root, base_domain, server_host,
    server_user, web_root_base, github_user, git_name, git_email and the optional ports_registry. Without it the
    script falls back to owner.example.json (dummy values) and warns loudly.
  - project.json (per game) uses the placeholder names as keys (see project.example.json). Only GAME_NAME, GENRE,
    SETTING_SHORT, ONE_PARAGRAPH_PITCH, TAGLINE, DEV_PORT and PREVIEW_PORT are required; the rest is derived from
    the name and owner.json (slug, domain <slug>.<base_domain>, remote https://github.com/<github_user>/<Name>.git,
    ssh target <server_user>@<server_host>, deploy dir <web_root_base>/<slug>, project folder <projects_root>/<Name>,
    env variable names) or takes generic values (budget 0, milestone names). A key set in project.json wins.

What it does:
  1. replaces every simple double-brace placeholder in the text files of the project;
  2. rewrites the example table in PORTS.md with owner.json's ports_registry (plus this project);
  3. renames README.project.md to README.md and moves the template-only files (QUESTIONS.md, SETUP.md,
     project.example.json, owner.example.json) and project.json into Docs/setup/ (a project.json outside the
     folder is copied); owner.json stays where it is (git-ignored);
  4. lists the rich FILL markers that Claude still has to write from the questionnaire answers.
Exit code: 0 when only FILL markers remain, 1 when a simple placeholder is left or the input is invalid.
Plain-ASCII output (the Windows console is cp1252).
"""
import argparse, datetime, json, pathlib, re, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEXT_SUFFIXES = {'.md', '.py', '.sh', '.json', '.conf', '.txt', '.ts', '.yml', '.yaml', '.example', ''}
SKIP_DIRS = {'.git', 'node_modules', 'dist', 'site-dist', '.claude/autodrive'}
SKIP_NAMES = {'QUESTIONS.md', 'SETUP.md', 'project.example.json', 'owner.json', 'owner.example.json'}
SELF = pathlib.Path(__file__).resolve()
SIMPLE = re.compile(r'\{\{([A-Z][A-Z0-9_]*)\}\}')
FILL = re.compile(r'\{\{FILL:\s*([^}]*)\}\}')
REQUIRED = ['GAME_NAME', 'GENRE', 'SETTING_SHORT', 'ONE_PARAGRAPH_PITCH', 'TAGLINE', 'DEV_PORT', 'PREVIEW_PORT']
OWNER_KEYS = ['projects_root', 'base_domain', 'server_host', 'server_user', 'web_root_base', 'github_user',
              'git_name', 'git_email']
PORTS_START, PORTS_END = '<!-- PORTS_TABLE_START -->', '<!-- PORTS_TABLE_END -->'
DRIVE = re.compile(r'^[A-Za-z]:')


def load_owner():
    """owner.json (local, git-ignored); falls back to owner.example.json with a loud warning."""
    for name, example in (('owner.json', False), ('owner.example.json', True)):
        f = ROOT / name
        if not f.exists():
            continue
        try:
            o = json.loads(f.read_text(encoding='utf8'))
        except Exception as e:
            sys.exit(f'cannot read {f}: {e}')
        if example:
            bar = '!' * 78
            print(f'{bar}\nWARNING: owner.json not found - using the DUMMY values of owner.example.json\n'
                  f'(games.example.com, your-github-name, ...). Copy owner.example.json to owner.json, fill in\n'
                  f'your values once and run this script again before you deploy or push.\n{bar}')
        missing = [k for k in OWNER_KEYS if not str(o.get(k, '')).strip()]
        if missing:
            sys.exit(f'{name} is missing: ' + ', '.join(missing))
        return o
    sys.exit(f'neither owner.json nor owner.example.json found in {ROOT}')


def registry(owner):
    """owner.json ports_registry as a list of (project, dev, preview)."""
    out = []
    for e in owner.get('ports_registry') or []:
        try:
            out.append((str(e['project']), int(e['dev']), int(e['preview'])))
        except (KeyError, TypeError, ValueError):
            sys.exit(f'owner.json ports_registry entry is invalid: {e!r} (needs project, dev, preview)')
    return out


def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def derive(cfg, owner):
    """Complete project.json with defaults from the name and owner.json; returns the placeholder -> value map."""
    v = {k: str(val) for k, val in cfg.items() if not k.startswith('_')}
    missing = [k for k in REQUIRED if not v.get(k)]
    if missing:
        sys.exit('project.json is missing: ' + ', '.join(missing))
    name = v['GAME_NAME']
    folder = name.replace(' ', '')
    slug = v.setdefault('GAME_SLUG', slugify(name))
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', slug):
        sys.exit('GAME_SLUG must be lower-case letters, digits and dashes')
    for p in ('DEV_PORT', 'PREVIEW_PORT'):
        if not v[p].isdigit():
            sys.exit(f'{p} must be a number')
    if v['DEV_PORT'] == v['PREVIEW_PORT']:
        sys.exit('DEV_PORT and PREVIEW_PORT must differ')
    env = re.sub(r'[^A-Z0-9]+', '_', slug.upper())
    v.setdefault('GITHUB_REMOTE', f'https://github.com/{owner["github_user"]}/{folder}.git')
    v.setdefault('DOMAIN', f'{slug}.{owner["base_domain"]}')
    v.setdefault('DNS_ZONE', v['DOMAIN'].split('.', 1)[1] if '.' in v['DOMAIN'] else v['DOMAIN'])
    v.setdefault('SERVER_HOST', v.get('SERVER_IP') or owner['server_host'])
    v.setdefault('SERVER_IP', v['SERVER_HOST'])  # legacy key: host name or IP address
    v.setdefault('SERVER_USER', owner['server_user'])
    v.setdefault('SERVER_SSH', v['SERVER_USER'] + '@' + v['SERVER_HOST'])
    v.setdefault('DEPLOY_DIR', owner['web_root_base'].rstrip('/') + '/' + slug)
    v.setdefault('AUTODRIVE_ENV', f'{env}_AUTODRIVE')
    v.setdefault('MODEL_ENV', f'{env}_MODEL')
    root = v.setdefault('PROJECTS_ROOT', owner['projects_root'].rstrip('\\/'))
    win = v.setdefault('PROJECT_DIR_WIN', root + ('\\' if DRIVE.match(root) else '/') + folder)
    if DRIVE.match(win):
        drive, rest = win.split(':', 1)
        v.setdefault('PROJECT_DIR_POSIX', '/' + drive.lower() + rest.replace('\\', '/'))
    else:
        v.setdefault('PROJECT_DIR_POSIX', win)
    v.setdefault('CLAUDE_PROJECTS_KEY', re.sub(r'[^A-Za-z0-9]', '-', win))
    v.setdefault('GIT_NAME', owner['git_name'])
    v.setdefault('GIT_EMAIL', owner['git_email'])
    reg = [r for r in registry(owner) if r[0].lower() != name.lower()]
    reg.append((name, int(v['DEV_PORT']), int(v['PREVIEW_PORT'])))
    v['PORTS_REGISTRY_JSON'] = json.dumps([{'project': p, 'dev': d, 'preview': pv} for p, d, pv in reg])
    v.setdefault('TRAILER_LEDE', v['TAGLINE'])
    v.setdefault('BUDGET_USD', '0')
    v.setdefault('LARGE_GATES', 'M2, M5 and M7')
    v.setdefault('ACCEPTANCE_FROM', 'M3')
    v.setdefault('MVP_MILESTONE', 'M7')
    v.setdefault('MVP_TAG', 'm7')
    v.setdefault('SIM_SYSTEMS', 'the core rules, generation, progression and meta')
    v.setdefault('PLAYTEST_AREAS', 'first minutes, core loop readability, signature mechanics, progression, meta and hub, phone, fun')
    v.setdefault('SETUP_DATE', datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M'))
    if v['GITHUB_REMOTE'].startswith('git@'):
        sys.exit('GITHUB_REMOTE must be an HTTPS URL (https://github.com/<user>/<repo>.git): the autodrive driver '
                 'pushes non-interactively with the saved HTTPS credentials, not with an SSH key')
    try:
        float(v['BUDGET_USD'])
    except ValueError:
        sys.exit('BUDGET_USD must be a number')
    return v, reg


def check_ports(v, owner):
    """Warn when the ports clash with another project in owner.json's ports_registry."""
    mine = {v['DEV_PORT'], v['PREVIEW_PORT']}
    known = False
    for p, d, pv in registry(owner):
        if p.lower() == v['GAME_NAME'].lower():
            known = True
        elif {str(d), str(pv)} & mine:
            print(f'WARNING: ports {v["DEV_PORT"]}/{v["PREVIEW_PORT"]} clash with {p} in owner.json ports_registry')
    if not known:
        print(f'note: {v["GAME_NAME"]} is not in owner.json ports_registry yet - add it there (each parallel project '
              f'gets a unique dev/preview pair) so the bash guards of the other projects know it')


def ports_table(v, reg):
    """Markdown table of the registry (this project included) for PORTS.md."""
    root = v['PROJECTS_ROOT']
    sep = '\\' if DRIVE.match(root) else '/'
    lines = ['| Project | Dev | Preview | Folder | Domain |', '|---|---|---|---|---|']
    for p, d, pv in reg:
        lines.append(f'| {p} | {d} | {pv} | {root}{sep}{p.replace(" ", "")} | {slugify(p)}.{v["DNS_ZONE"]} |')
    return '\n'.join(lines)


def git_identity(owner):
    """Set the local git identity of the new repository from owner.json."""
    if not (ROOT / '.git').exists():
        sys.exit('no .git here yet: run `git init -b master` first')
    for key, val in (('user.name', owner['git_name']), ('user.email', owner['git_email'])):
        subprocess.run(['git', '-C', str(ROOT), 'config', key, val], check=True)
    print(f'git identity set for this repository: {owner["git_name"]} <{owner["git_email"]}>')


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
        if p.name in SKIP_NAMES or 'Docs/setup/' in p.as_posix():
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
    ap.add_argument('--git-identity', action='store_true')
    a = ap.parse_args()
    if a.git_identity:
        git_identity(load_owner())
        return
    if not a.check:
        if not a.project_json:
            sys.exit('usage: fill_template.py project.json [--dry-run] | --check | --git-identity')
        src = pathlib.Path(a.project_json)
        try:
            cfg = json.loads(src.read_text(encoding='utf8'))
        except Exception as e:
            sys.exit(f'cannot read {src}: {e}')
        owner = load_owner()
        v, reg = derive(cfg, owner)
        check_ports(v, owner)
        print(f'domain {v["DOMAIN"]} | remote {v["GITHUB_REMOTE"]} | deploy {v["SERVER_SSH"]}:{v["DEPLOY_DIR"]} | '
              f'folder {v["PROJECT_DIR_WIN"]} | ports {v["DEV_PORT"]}/{v["PREVIEW_PORT"]}')
        changed = 0
        for p in text_files():
            if p.name in SKIP_NAMES or p.resolve() == src.resolve():
                continue
            try:
                t = p.read_text(encoding='utf8')
            except UnicodeDecodeError:
                continue
            o = t
            if p.suffix == '.json':  # numbers stay numbers in JSON
                t = t.replace('"{{BUDGET_USD}}"', v['BUDGET_USD'])
            t = SIMPLE.sub(lambda m: v.get(m.group(1), m.group(0)), t)
            if p.relative_to(ROOT).as_posix() == 'PORTS.md' and PORTS_START in t and PORTS_END in t:
                head, rest = t.split(PORTS_START, 1)
                t = head + PORTS_START + '\n' + ports_table(v, reg) + '\n' + PORTS_END + rest.split(PORTS_END, 1)[1]
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
            for name in ('QUESTIONS.md', 'SETUP.md', 'project.example.json', 'owner.example.json'):
                if (ROOT / name).exists():
                    shutil.move(str(ROOT / name), str(setup / name))
            if src.resolve() != (setup / 'project.json').resolve():
                if src.resolve().parent == ROOT:
                    shutil.move(str(src), str(setup / 'project.json'))
                else:
                    shutil.copy2(src, setup / 'project.json')
            if (ROOT / 'README.project.md').exists():
                (ROOT / 'README.project.md').replace(ROOT / 'README.md')
            print('moved QUESTIONS.md, SETUP.md, the example JSON files and project.json to Docs/setup/; '
                  'README.project.md -> README.md')
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

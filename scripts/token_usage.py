#!/usr/bin/env python3
"""Total Claude Code token usage for this project (read-only; aggregate numbers only).

Reads the session transcripts under ~/.claude/projects/{{CLAUDE_PROJECTS_KEY}}/:
  *.jsonl                      main sessions
  <session>/subagents/*.jsonl  subagent transcripts
Each assistant message id is counted once (streaming rewrites the same id several times;
the last record of an id carries the final usage). Writes Docs/TOKENS.json.
Run:  python -I scripts/token_usage.py
"""
import datetime, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path.home() / '.claude' / 'projects' / '{{CLAUDE_PROJECTS_KEY}}'
FIELDS = ('input_tokens', 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens')


def scan(path):
    last, tools, first_ts, last_ts = {}, set(), None, None
    with open(path, encoding='utf8', errors='replace') as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            ts = d.get('timestamp')
            if ts:
                first_ts = first_ts or ts
                last_ts = ts
            if d.get('type') != 'assistant':
                continue
            m = d.get('message') or {}
            for c in m.get('content') or []:
                if isinstance(c, dict) and c.get('type') == 'tool_use' and c.get('id'):
                    tools.add(c['id'])
            u = m.get('usage')
            if isinstance(u, dict) and m.get('id'):
                last[m['id']] = u
    tot = dict.fromkeys(FIELDS, 0)
    for u in last.values():
        for f in FIELDS:
            tot[f] += int(u.get(f) or 0)
    return tot, len(last), len(tools), first_ts, last_ts


def bucket():
    return {**dict.fromkeys(FIELDS, 0), 'assistant_messages': 0, 'tool_calls': 0, 'files': 0}


def main():
    groups = {'main': bucket(), 'subagents': bucket()}
    files = []
    spans = []
    paths = [('main', p) for p in sorted(SRC.glob('*.jsonl'))]
    paths += [('subagents', p) for p in sorted(SRC.glob('*/subagents/*.jsonl'))]
    for kind, p in paths:
        tot, msgs, tools, a, b = scan(p)
        g = groups[kind]
        for f in FIELDS:
            g[f] += tot[f]
        g['assistant_messages'] += msgs
        g['tool_calls'] += tools
        g['files'] += 1
        if a and b:
            spans += [a, b]
        files.append({'kind': kind, 'file': p.name, **tot, 'assistant_messages': msgs, 'tool_calls': tools})
    total = bucket()
    for g in groups.values():
        for k in total:
            total[k] += g[k]
    total['all_tokens'] = sum(total[f] for f in FIELDS)
    total['fresh_tokens_in_out'] = total['input_tokens'] + total['output_tokens']
    for g in groups.values():
        g['all_tokens'] = sum(g[f] for f in FIELDS)
    out = {
        'generated_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M'),
        'method': 'Sum of message.usage over this project\'s Claude Code transcripts (main sessions plus subagent '
                  'transcripts), each assistant message id counted once (last record of the id). Aggregate numbers '
                  'only; no content is read out. Cache reads are re-reads of the same context, so all_tokens '
                  'overstates new work; fresh_tokens_in_out (input + output) is the conservative figure. '
                  'Sessions or messages without usage data are not counted.',
        'first_record_utc': min(spans) if spans else None,
        'last_record_utc': max(spans) if spans else None,
        'main': groups['main'],
        'subagents': groups['subagents'],
        'total': total,
        'files': files,
    }
    (ROOT / 'Docs' / 'TOKENS.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf8')
    print(f"tokens: total {total['all_tokens']:,} (fresh in+out {total['fresh_tokens_in_out']:,}); "
          f"messages {total['assistant_messages']:,}; tool calls {total['tool_calls']:,}; files {total['files']}")


main()

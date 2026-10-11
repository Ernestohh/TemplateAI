#!/usr/bin/env python3
"""Filter for `claude -p --output-format stream-json --verbose` (used by scripts/autodrive.sh).

Prints one short line per event so the driver window shows live progress, keeps the raw stream,
and writes the final `result` event as JSON (the summary the driver logs). Display only:
it does not change what the model does or how many tokens it uses.

Robust by design: the stream is read as raw bytes (Windows would otherwise decode it as cp1252),
and nothing in here may crash, because a crashed filter breaks the pipe and kills the chunk.

Usage: claude ... | python -I -u scripts/autodrive_stream.py <raw.jsonl> <result.json>
"""
import datetime
import json
import sys

raw_path, result_path = sys.argv[1], sys.argv[2]


def stamp() -> str:
    return datetime.datetime.now().strftime('%H:%M:%S')


def short(text: object, n: int = 140) -> str:
    text = ' '.join(str(text).split())
    text = text.encode('ascii', 'replace').decode('ascii')  # any Windows console can print it
    return text if len(text) <= n else text[: n - 3] + '...'


def show(line: str) -> None:
    try:
        print(line, flush=True)
    except Exception:  # a console problem must never stop the chunk
        pass


with open(raw_path, 'ab') as raw:
    for chunk in sys.stdin.buffer:
        try:
            raw.write(chunk)
            raw.flush()
        except Exception:
            pass
        try:
            ev = json.loads(chunk.decode('utf-8', 'replace'))
        except Exception:
            continue
        try:
            kind = ev.get('type')
            if kind == 'assistant':
                for block in (ev.get('message') or {}).get('content') or []:
                    if block.get('type') == 'text' and str(block.get('text', '')).strip():
                        show(f'{stamp()}  say  {short(block["text"])}')
                    elif block.get('type') == 'tool_use':
                        inp = block.get('input') or {}
                        what = inp.get('description') or inp.get('file_path') or inp.get('pattern') or inp.get('prompt') or inp.get('command') or ''
                        show(f'{stamp()}  >    {block.get("name")}: {short(what, 110)}')
            elif kind == 'result':
                with open(result_path, 'w', encoding='utf8', errors='replace') as out:
                    json.dump(ev, out, ensure_ascii=True)
                cost = ev.get('total_cost_usd')
                show(f'{stamp()}  ==   chunk finished: {ev.get("num_turns", "?")} turns, '
                     f'{cost if cost is not None else "?"} USD reported, error={ev.get("is_error")}')
        except Exception:
            continue

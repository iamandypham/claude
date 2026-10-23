#!/usr/bin/env python3
"""Turn a graphics plan anchored on spoken phrases into Remotion props.

Usage:
  python3 plan_graphics.py --words cut-words.json --plan plan.json --video cut.mp4 --out graphics/public/props.json

cut-words.json is transcribe.py's output for the FINISHED cut (not the raw take).
plan.json: {"accent": "#FECB00", "graphics": [
  {"type": "title", "from": "you probably can", "to": "then stop talking", "text": "You probably can."},
  {"type": "steps", "from": "number one", "to": "do it again", "heading": "The 4-hour timer",
   "items": [{"text": "Set a timer: 4 hours", "at": "number one"}, ...]},
  {"type": "stat", "from": "...", "to": "...", "value": "$400-500", "label": "...", "proof": "bank N4 (LTV)"},
  {"type": "compare", "from": "...", "to": "...", "at": "...", "left": {...}, "right": {...}}]}
"from"/"at" anchor on the first word of the phrase, "to" on its last word. Anchors are
searched in order through the transcript, so repeat phrases resolve to the next use.
Any digit or $ on screen needs a "proof" field (bg_gates G3: every on-screen number has proof).
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

ap = argparse.ArgumentParser()
ap.add_argument('--words', required=True)
ap.add_argument('--plan', required=True)
ap.add_argument('--video', required=True)
ap.add_argument('--out', required=True)
a = ap.parse_args()

NUM = {'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10'}


def norm(w):
    w = re.sub(r"[^a-z0-9$']", '', w.lower().replace('’', "'"))
    return NUM.get(w, w)  # Whisper writes "Number 1" for "number one"
words = [w for w in json.load(open(a.words)) if norm(w['word'])]
toks = [norm(w['word']) for w in words]
plan = json.load(open(a.plan))
cursor = 0
errors = []


def find(phrase, after, last=False):
    target = [norm(t) for t in phrase.split() if norm(t)]
    for i in range(after, len(toks) - len(target) + 1):
        miss = sum(a != b for a, b in zip(toks[i:i + len(target)], target))
        if miss == 0 or (len(target) >= 3 and miss == 1 and toks[i] == target[0]):  # one misheard word
            return (i + len(target) - 1) if last else i
    return None


def anchor(phrase, last=False):
    i = find(phrase, cursor, last)
    if i is None:
        errors.append(f'anchor not found after word {cursor}: "{phrase}"')
        return None
    return i


def on_screen_text(g):
    parts = [g.get(k, '') for k in ('text', 'sub', 'heading', 'value', 'label')]
    parts += [it['text'] for it in g.get('items', [])]
    for side in ('left', 'right'):
        if side in g:
            parts += [g[side]['title']] + g[side]['lines']
    return ' '.join(p for p in parts if p)


out = []
for g in plan['graphics']:
    if re.search(r'[\d$]', on_screen_text(g)) and not g.get('proof'):
        errors.append(f'{g["type"]} "{on_screen_text(g)[:40]}": on-screen number with no "proof"')
    s = anchor(g['from'])
    if s is None:
        continue
    cursor = s
    e = anchor(g['to'], last=True)
    if e is None:
        continue
    r = {k: v for k, v in g.items() if k not in ('from', 'to', 'at', 'items')}
    r['start'] = round(max(0, words[s]['start'] - 0.1), 3)
    r['end'] = round(words[e]['end'] + 0.35, 3)
    if 'items' in g:
        r['items'] = []
        c0 = cursor
        for it in g['items']:
            i = find(it['at'], cursor)
            if i is None or i > e:
                errors.append(f'item anchor not inside its graphic: "{it["at"]}"')
                continue
            cursor = i
            r['items'].append({'text': it['text'], 'at': round(max(r['start'], words[i]['start'] - 0.05), 3)})
        cursor = c0
    if 'at' in g:
        i = find(g['at'], s)
        r['at'] = round(words[i]['start'], 3) if i is not None and i <= e else r['start']
    out.append(r)
    cursor = e + 1

# Full-screen cards hide the face, so they're for short beats only (Brendan's cards flash, then cut back).
for r in out:
    if r.get('layout', 'full') == 'full' and r['end'] - r['start'] > 5:
        r['layout'] = 'top'
        print(f'note: {r["type"]} at {r["start"]:.1f}s runs {r["end"] - r["start"]:.0f}s, so it sits in the top panel, not full screen')

for x, y in zip(out, out[1:]):
    if y['start'] < x['end']:
        x['end'] = y['start']

if errors:
    print('\n'.join('ERROR ' + m for m in errors))
    sys.exit(2)

probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                            'stream=width,height,r_frame_rate:format=duration', '-of', 'json', a.video]))
st = probe['streams'][0]
num, den = st['r_frame_rate'].split('/')
pub = os.path.join(os.path.dirname(os.path.abspath(a.out)))
os.makedirs(pub, exist_ok=True)
name = os.path.basename(a.video)
if os.path.abspath(a.video) != os.path.join(pub, name):
    shutil.copy(a.video, os.path.join(pub, name))
props = {'video': name, 'width': st['width'], 'height': st['height'], 'fps': round(int(num) / int(den)),
         'duration': float(probe['format']['duration']), 'accent': plan.get('accent', '#FECB00'), 'graphics': out}
json.dump(props, open(a.out, 'w'), indent=1)
for r in out:
    print(f'{r["type"]:8} {r["start"]:6.2f}-{r["end"]:6.2f}s  {on_screen_text(r)[:60]}')

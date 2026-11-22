#!/usr/bin/env python3
"""Build a reel script pack from one spec file.

Usage: python3 build_pack.py <reel-folder>/spec.json

spec.json: {"date": "2026-10-28", "idea": {...sheet row...}, "keyword": "WORD", "keyword_delivers": "...",
            "source_transcript": "...", "steal_notes": ["..."], "extra_cues": ["..."],
            "versions": [{"id": "v1", "hook_type": "<Virlo label>", "patterns": ["P1"],
                          "headline": "4 to 8 words", "caption": "...", "beats": [{...}],
                          "score": 70, "gates": "6/6", "broll": [], "lines": [...]}]}
The CTA line is appended to every version, so leave it out of "lines".
Writes teleprompter.md (spoken words only), run-order.md (Andy's cues), captions.md and scripts.json.
"""
import json
import os
import re
import sys

VIRLO_HOOK_TYPES = {"bold_claim", "tutorial_promise", "question", "story_tease", "relatable_scenario",
                    "direct_address", "pov_setup", "statistic", "negation", "shock_statement",
                    "comparison", "before_after"}
BANNED = re.compile(r"[—–]|\bwhop\b|\bcallix\b", re.I)

spec_path = sys.argv[1]
folder = os.path.dirname(os.path.abspath(spec_path))
s = json.load(open(spec_path))
idea, kw = s["idea"], s["keyword"]
if not s.get("date"):
    sys.exit('spec.json needs "date" (today, from `date`), so the pack never carries the wrong year')
cta = s.get("cta") or f'Comment "{kw}" and I\'ll send you {s["cta_thing"]}.'

versions = []
for v in s["versions"]:
    lines = v["lines"] + [cta]
    versions.append({**v, "lines": lines, "words": sum(len(l.split()) for l in lines)})

tp = []
for i, v in enumerate(versions, 1):
    tp.append(f"## {i}\n")
    tp += [l + "\n" for l in v["lines"]]
open(os.path.join(folder, "teleprompter.md"), "w").write("\n".join(tp))

ro = [f'# Run order: "{s["title"]}" (private, never on screen)\n',
      f'Pack date: {s["date"]}\n',
      f'Idea: {idea["creator"]} "{idea["hook"]}" ({idea["saves"]} saves, {idea["save_rate"]}). Source: {idea["link"]}\n',
      "1. Frame: chest up, a bit further back than usual so captions fit under your chin. Plain background.",
      "2. Load teleprompter.md. It only holds the words you say.",
      '3. Before each version, say its number ("one"), pause 2 seconds, then read it.',
      "4. Flub a line? Pause and restart that line. The editor keeps your last full read of every line, so never restart the whole version.",
      f"5. Order: {', '.join(str(i) for i in range(1, len(versions) + 1))}. Back to back in one recording is fine.",
      f"6. Keyword for all {len(versions)}: {kw}."]
n = 7
miro = sorted({b["miro_area"] for v in versions for b in v.get("beats", []) if b.get("miro_area")})
if miro:
    ro.append(f"{n}. Before recording, set up these Miro board areas: {'; '.join(miro)}.")
    n += 1
for c in s.get("extra_cues", []):
    ro.append(f"{n}. {c}")
    n += 1
ro.append(f'{n}. Stop recording, then tell me "recorded" and where the file is.')
open(os.path.join(folder, "run-order.md"), "w").write("\n".join(ro) + "\n")

cap = [f'# Headlines and captions: "{s["title"]}" ({s["date"]})\n']
for i, v in enumerate(versions, 1):
    cap += [f"## {i}\n", f'Headline: {v.get("headline", "(missing)")}\n', f'{v.get("caption", "(missing)")}\n']
open(os.path.join(folder, "captions.md"), "w").write("\n".join(cap))

out = {k: v for k, v in s.items() if k not in ("versions",)}
out["versions"] = versions
json.dump(out, open(os.path.join(folder, "scripts.json"), "w"), indent=1, ensure_ascii=False)

for v in versions:
    sw = s.get("source_words")
    if sw:
        body = v["words"] - len(cta.split())  # the source has no CTA, so compare without ours
        flag = "" if abs(body - sw) <= 0.15 * sw else f"  <-- body {body} words, more than 15% off the source ({sw})"
    else:
        flag = "" if 110 <= v["words"] <= 190 else "  <-- outside 110-190 words"
    if v["hook_type"] not in VIRLO_HOOK_TYPES:
        flag += f'  <-- hook_type "{v["hook_type"]}" is not a Virlo label'
    hl = v.get("headline", "")
    if not 4 <= len(hl.split()) <= 8:
        flag += "  <-- headline missing or not 4-8 words"
    if not v.get("caption"):
        flag += "  <-- no caption"
    if not v.get("beats"):
        flag += "  <-- no beats"
    texts = v["lines"] + [hl, v.get("caption", "")] + [b.get("text", "") for b in v.get("beats", [])]
    hits = [t for t in texts if BANNED.search(t)]
    if hits:
        flag += f"  <-- em dash/Whop/Callix in: {hits[0][:60]}"
    print(f'{v["id"]} {v["hook_type"]}: {v["words"]} words, score {v["score"]}{flag}')

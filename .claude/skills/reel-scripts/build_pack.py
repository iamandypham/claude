#!/usr/bin/env python3
"""Build a reel script pack from one spec file.

Usage: python3 build_pack.py <reel-folder>/spec.json

spec.json: {"idea": {...sheet row...}, "keyword": "WORD", "keyword_delivers": "...",
            "source_transcript": "...", "steal_notes": ["..."], "extra_cues": ["..."],
            "versions": [{"id": "v1", "hook_type": "...", "bank_codes": [...], "score": 70,
                          "gates": "6/6", "proof_needed": [], "broll": [], "lines": [...]}]}
The CTA line is appended to every version, so leave it out of "lines".
Writes teleprompter.md (spoken words only), run-order.md (Andy's cues) and scripts.json.
"""
import json
import os
import sys

spec_path = sys.argv[1]
folder = os.path.dirname(os.path.abspath(spec_path))
s = json.load(open(spec_path))
idea, kw = s["idea"], s["keyword"]
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
      f'Idea: {idea["creator"]} "{idea["hook"]}" ({idea["saves"]} saves, {idea["save_rate"]}). Source: {idea["link"]}\n',
      "1. Frame: chest up, a bit further back than usual so captions fit under your chin. Plain background.",
      "2. Load teleprompter.md. It only holds the words you say.",
      '3. Before each version, say its number ("one"), pause 2 seconds, then read it.',
      "4. Flub a line? Pause and restart that line. The editor keeps your last full read of every line, so never restart the whole version.",
      f"5. Order: {', '.join(str(i) for i in range(1, len(versions) + 1))}. Back to back in one recording is fine.",
      f"6. Keyword for all {len(versions)}: {kw}."]
n = 7
for c in s.get("extra_cues", []):
    ro.append(f"{n}. {c}")
    n += 1
ro.append(f'{n}. Stop recording, then tell me "recorded" and where the file is.')
open(os.path.join(folder, "run-order.md"), "w").write("\n".join(ro) + "\n")

out = {k: v for k, v in s.items() if k not in ("versions",)}
out["versions"] = versions
json.dump(out, open(os.path.join(folder, "scripts.json"), "w"), indent=1, ensure_ascii=False)

for v in versions:
    flag = "" if 110 <= v["words"] <= 190 else "  <-- outside 110-190 words"
    print(f'{v["id"]} {v["hook_type"]}: {v["words"]} words, score {v["score"]}{flag}')

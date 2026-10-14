#!/usr/bin/env python3
"""Fix a word-level transcript before the kit burns captions.

- Whisper often splits numbers into "$31" + ",000"; the kit's formatter then burns "$31 ,000".
  Merge any token that starts with , or . followed by digits into the previous token.
- Keep acronyms upper case that the kit lowercases (ICT, MRR, VSL ...): --upper ICT,MRR
- Known BG mis-hears are fixed (--fix wap=Whop,whop's=Whop's). Whisper hears "Whop" as "WAP".
- --shift SEC moves every timestamp earlier (use after a head trim), dropping words before 0.
Usage: bg_words_fix.py in.json out.json [--shift 0.4] [--upper ICT,MRR]
"""
import argparse, json, re
ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--shift", type=float, default=0.0); ap.add_argument("--upper", default="ICT,MRR,VSL,DFY,ROI,CPBC")
ap.add_argument("--fix", default="wap=Whop,wap's=Whop's")
a = ap.parse_args()
d = json.load(open(a.inp)); up = {u.lower(): u for u in a.upper.split(",") if u}
fix = dict(x.split("=", 1) for x in a.fix.split(",") if "=" in x)
out = []
for w in d["words"]:
    t = w["word"].strip()
    if out and re.match(r"^[,.]\d", t) and re.search(r"\d$", out[-1]["word"].strip()):
        out[-1]["word"] = out[-1]["word"].rstrip() + t; out[-1]["end"] = w["end"]; continue
    core = re.sub(r"[^\w]", "", t).lower()
    low = t.lower().strip(".,!?;:")
    hit = next((k for k in fix if low == k.lower() or core == re.sub(r"[^\w]", "", k).lower()), None)
    if hit: t = re.sub(re.escape(hit) if low == hit.lower() else core, fix[hit], t, flags=re.I); core = ""
    if core in up: t = re.sub(core, up[core], t, flags=re.I)
    out.append(dict(w, word=t))
words = []
for w in out:
    s, e = w["start"] - a.shift, w["end"] - a.shift
    if e <= 0: continue
    words.append(dict(w, start=round(max(0.0, s), 3), end=round(e, 3)))
d["words"] = words; d["text"] = " ".join(w["word"] for w in words)
json.dump(d, open(a.out, "w"), indent=1); print(d["text"])

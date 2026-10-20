#!/usr/bin/env python3
"""Check a rendered reel against the pack's gates. Prints a table and exits 1 on any FAIL.

Usage: qa.py <out.mp4> --plan plan.json [--words words.json] [--format stack|face|pov|card|explainer]
"""
import argparse, json, os, re, subprocess, sys

TARGET_LEN = {  # seconds, from the studied top reels per format (references/formats.md)
    "stack": (20, 75), "face": (25, 60), "pov": (6, 30), "card": (4, 8), "explainer": (30, 60),
}


def run(args):
    return subprocess.run(args, capture_output=True, text=True)


def probe(path):
    out = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
               "stream=width,height,r_frame_rate:format=duration", "-of", "json", path]).stdout
    d = json.loads(out)
    s = d["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return int(s["width"]), int(s["height"]), float(num) / float(den), float(d["format"]["duration"])


def visual_change_times(path, thresh=0.004, top_share=0.0):
    # Low scene threshold: chart drawings and zooms count as visual changes, not only hard cuts.
    # For stack layouts only the chart panel is checked, so a talking webcam doesn't count.
    crop = f"crop=iw:ih*{1 - top_share:.3f}:0:ih*{top_share:.3f}," if top_share else ""
    err = run(["ffmpeg", "-hide_banner", "-i", path, "-vf",
               f"fps=10,{crop}scale=270:-2,select='gt(scene,{thresh})',showinfo", "-an", "-f", "null", "-"]).stderr
    return [float(t) for t in re.findall(r"pts_time:([\d.]+)", err)]


def lufs(path):
    err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"]).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", err)
    return float(m[-1]) if m else None


def letterboxed(path):
    err = run(["ffmpeg", "-hide_banner", "-ss", "1", "-i", path, "-t", "3", "-vf", "cropdetect=24:2:0",
               "-f", "null", "-"]).stderr
    m = re.findall(r"crop=(\d+):(\d+):", err)
    if not m:
        return False
    w, h = map(int, m[-1])
    return h < 1920 * 0.85


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--plan", required=True); ap.add_argument("--words")
    ap.add_argument("--format", default="stack", choices=sorted(TARGET_LEN))
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    base = os.path.dirname(os.path.abspath(a.plan))
    wpath = a.words or (plan.get("words") and os.path.join(base, plan["words"]))
    words = json.load(open(wpath))["words"] if wpath else []
    w, h, fps, dur = probe(a.video)
    rows = []
    add = lambda name, ok, detail: rows.append((name, "PASS" if ok else "FAIL", detail))
    warn = lambda name, detail: rows.append((name, "WARN", detail))

    add("1080x1920 vertical", (w, h) == (1080, 1920), f"{w}x{h}")
    add("frame rate >= 30", fps >= 29.9, f"{fps:.2f} fps")
    lo, hi = TARGET_LEN[a.format]
    add(f"length {lo}-{hi}s for {a.format}", lo - 0.5 <= dur <= hi + 0.5, f"{dur:.1f}s")
    if a.format != "card":
        add("no letterbox bars", not letterboxed(a.video), "full-bleed 9:16 (letterboxed reels underperformed)")

    hook = plan.get("hook") or {}
    if a.format != "card":
        add("hook text on screen from frame 0", bool(hook.get("text")), hook.get("text", "missing"))
        if hook.get("text"):
            he = float(hook.get("end", 3))
            if a.format == "pov":
                warn("POV label", f"label may stay all reel (ends {he:.1f}s)")
            else:
                add("hook text gone by 2-6s", 2.0 <= he <= 6.0, f"ends {he:.1f}s")
            add("hook text <= 12 words", len(hook["text"].split()) <= 12, f"{len(hook['text'].split())} words")

    if words:
        span = max(1e-6, words[-1]["e"] - words[0]["s"])
        wps = len(words) / span
        add("speech pace 2.3-4.2 words/s", 2.3 <= wps <= 4.2, f"{wps:.2f} w/s")
        gaps = [b["s"] - a_["e"] for a_, b in zip(words, words[1:])]
        mg = max(gaps) if gaps else 0
        add("no pause over 0.6s", mg <= 0.6, f"longest {mg:.2f}s (run tighten.py)")
        add("speech starts by 0.5s", words[0]["s"] <= 0.5, f"first word {words[0]['s']:.2f}s")
        fill = [x["w"] for x in words if re.sub(r'[^a-z]', '', x["w"].lower()) in {"um", "uh", "erm", "uhm", "umm"}]
        add("no filler words", not fill, ", ".join(fill[:5]) or "none")
        if plan.get("captions"):
            he = float(hook.get("end", 0)) if hook.get("text") else 0
            first_cap = next((x["s"] for x in words if x["s"] >= he - 0.05), None)
            ok = first_cap is None or first_cap - he <= 0.8
            add("captions start as hook ends", ok, f"hook {he:.1f}s, first caption {first_cap}")

    stack = plan.get("layout") == "stack"
    ch = visual_change_times(a.video, 0.004 if stack else 0.01,
                             (plan.get("stack") or {}).get("split", 0.33) if stack else 0.0)
    if a.format == "card":
        warn("static card", "cards are meant to be still; checked length and size only")
    else:
        first = ch[0] if ch else None
        add("first visual change by 2s", first is not None and first <= 2.0, f"{first}")
        pts = [0.0] + ch + [dur]
        longest = max(b - a_ for a_, b in zip(pts, pts[1:]))
        add("no static stretch over 5s", longest <= 5.0, f"longest {longest:.1f}s")

    cta = plan.get("cta") or {}
    if cta.get("text"):
        add("CTA in last 2-4s only", 2.0 <= float(cta.get("seconds", 3)) <= 4.0, cta["text"])
    else:
        warn("no CTA", "fine for joke/POV reels; teaching reels usually end on a comment-keyword CTA")

    L = lufs(a.video)
    if L is not None and L > -70:
        add("loudness -16 to -12 LUFS", -16.5 <= L <= -11.5, f"{L:.1f} LUFS")

    width = max(len(r[0]) for r in rows)
    for name, st, det in rows:
        print(f"{st:4}  {name:<{width}}  {det}")
    fails = sum(1 for r in rows if r[1] == "FAIL")
    print(f"\n{fails} fail(s), {sum(1 for r in rows if r[1]=='WARN')} warning(s)")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

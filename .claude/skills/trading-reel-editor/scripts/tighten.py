#!/usr/bin/env python3
"""Cut dead air and filler words using word timestamps.

Usage: tighten.py <video> <words.json> <out_video> <out_words.json>
         [--max-gap 0.35] [--pad 0.08] [--fillers um,uh,erm,uhm] [--start S] [--end S]

Keeps every word, removes pauses longer than about --max-gap + 2 x --pad (0.51 s by default) and the filler words listed,
and writes a new words.json with times remapped to the tightened video, so captions
line up. Only the main video is cut: a separate chart recording used as stack.bottom.src
will drift, so record webcam and chart into one file. Never speeds anything up (the course says: cut, don't fast-forward).
"""
import argparse, json, math, re, subprocess


def keep_spans(words, max_gap, pad, fillers, t0, t1):
    norm = lambda w: re.sub(r"[^a-z]", "", w.lower())
    spans = []
    for w in words:
        if w["s"] < t0 or w["e"] > t1 or norm(w["w"]) in fillers:
            continue
        s, e = max(t0, w["s"] - pad), min(t1, w["e"] + pad)
        if spans and s - spans[-1][1] <= max_gap:
            spans[-1][1] = max(spans[-1][1], e)
        else:
            spans.append([s, e])
    return spans


def remap(words, spans, fillers):
    norm = lambda w: re.sub(r"[^a-z]", "", w.lower())
    out, offset = [], 0.0
    for s, e in spans:
        for w in words:
            if w["s"] >= s - 1e-3 and w["e"] <= e + 1e-3 and norm(w["w"]) not in fillers:
                out.append({"w": w["w"], "s": round(w["s"] - s + offset, 3),
                            "e": round(w["e"] - s + offset, 3)})
        offset += e - s
    return out, offset


def probe_fps(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=r_frame_rate", "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    num, _, den = out.strip().partition("/")
    return float(num) / float(den or 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("words"); ap.add_argument("out"); ap.add_argument("out_words")
    ap.add_argument("--max-gap", type=float, default=0.35)
    ap.add_argument("--pad", type=float, default=0.08)
    ap.add_argument("--fillers", default="um,uh,erm,uhm,umm,hmm")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=None)
    a = ap.parse_args()
    data = json.load(open(a.words))
    fillers = set(a.fillers.split(",")) if a.fillers else set()
    t1 = a.end if a.end is not None else data["duration"]
    spans = keep_spans(data["words"], a.max_gap, a.pad, fillers, a.start, t1)
    fps = probe_fps(a.video)
    # Snap span edges to whole frames so the video and the remapped word times stay in step.
    spans = [[math.floor(s * fps) / fps, math.ceil(e * fps) / fps] for s, e in spans]
    if not spans:
        raise SystemExit("no speech found in range")
    parts, labels = [], []
    for i, (s, e) in enumerate(spans):
        parts.append(f"[0:v]trim={s:.3f}:{e:.3f},setpts=PTS-STARTPTS[v{i}];"
                     f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d=0.01,afade=t=out:st={max(0, e - s - 0.01):.3f}:d=0.01[a{i}];")
        labels.append(f"[v{i}][a{i}]")
    graph = "".join(parts) + "".join(labels) + f"concat=n={len(spans)}:v=1:a=1[v][a]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-filter_complex", graph,
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                    "-c:a", "aac", "-b:a", "192k", a.out], check=True)
    words, dur = remap(data["words"], spans, fillers)
    json.dump({"duration": round(dur, 3), "words": words, "cuts": len(spans) - 1}, open(a.out_words, "w"), indent=1)
    removed = (t1 - a.start) - dur
    print(f"{len(spans)} spans, removed {removed:.1f}s, new length {dur:.1f}s -> {a.out}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Find each script version's last clean read in a raw recording and cut it.

Andy reads the versions back to back and restarts any line he flubs. For every
sentence of every version this keeps the LAST complete read that comes after
the previous kept sentence, drops everything else (flubs, pauses, teleprompter
fiddling), and writes one cut .mp4 per version.

  python3 split_takes.py --words words.json --script scripts.json --out DIR [--video raw.mp4]

words.json  : [{"word": "...", "start": s, "end": s}, ...]  (faster-whisper word timestamps)
scripts.json: {"versions": [{"id": "v1", "lines": ["sentence", ...]}, ...]}
Writes DIR/edl.json and, with --video, DIR/<id>-cut.mp4.
"""
import argparse, difflib, json, re, subprocess, sys
from pathlib import Path

PAD_IN, PAD_OUT = 0.08, 0.15     # seconds kept around each sentence
MIN_RATIO = 0.80                 # fuzzy match needed to count a read as clean
MAX_GAP = 0.6                    # a pause longer than this inside a read is cut out


def norm(t):
    t = re.sub(r"\bwap\b", "whop", t.lower())
    t = t.replace("%", " percent").replace("&", " and ")
    return re.sub(r"[^a-z0-9' ]+", " ", t).split()


def find_reads(words, target, start_idx):
    """All (ratio, i, j) windows from start_idx whose words match target."""
    n = len(target)
    toks = [norm(w["word"]) for w in words]
    flat = [(" ".join(t), k) for k, t in enumerate(toks) if t]
    hits = []
    for a in range(len(flat)):
        if flat[a][1] < start_idx:
            continue
        for L in (n - 1, n, n + 1, n + 2):
            if L < 1 or a + L > len(flat):
                continue
            cand = " ".join(x[0] for x in flat[a:a + L]).split()
            if cand[0] != target[0]:      # a read starts on the line's first word
                continue
            r = difflib.SequenceMatcher(None, cand, target).ratio()
            if r >= MIN_RATIO:
                hits.append((r, flat[a][1], flat[a + L - 1][1]))
    return hits


def pick(words, versions):
    edl, cursor = [], 0
    for v in versions:
        spans, missing = [], []
        for line in v["lines"]:
            target = norm(line)
            if not target:
                continue
            hits = find_reads(words, target, cursor)
            if not hits:
                missing.append(line)
                continue
            # last complete read wins; among overlapping windows at that start, best ratio
            last_start = max(h[1] for h in hits)
            r, i, j = max((h for h in hits if h[1] == last_start), key=lambda h: (h[0], -h[2]))
            # a restart can begin after the last read's start only if it is a new read;
            # anything before last_start that belongs to this line was a flub
            # split the read at long pauses (teleprompter glances) so dead air is cut
            a0 = i
            for k in range(i + 1, j + 1):
                if words[k]["start"] - words[k - 1]["end"] > MAX_GAP:
                    spans.append({"line": line, "start": max(0.0, words[a0]["start"] - PAD_IN),
                                  "end": words[k - 1]["end"] + PAD_OUT, "ratio": round(r, 3), "w": [a0, k - 1]})
                    a0 = k
            spans.append({"line": line, "start": max(0.0, words[a0]["start"] - PAD_IN),
                          "end": words[j]["end"] + PAD_OUT, "ratio": round(r, 3), "w": [a0, j]})
            cursor = j + 1
        # merge touching spans
        merged = []
        for s in spans:
            if merged and s["start"] <= merged[-1]["end"]:
                merged[-1]["end"] = max(merged[-1]["end"], s["end"])
            else:
                merged.append({"start": s["start"], "end": s["end"]})
        edl.append({"id": v["id"], "lines": spans, "segments": merged, "missing": missing})
    return edl


def cut(video, segs, out):
    parts = "".join(f"[0:v]trim={s['start']:.3f}:{s['end']:.3f},setpts=PTS-STARTPTS[v{k}];"
                    f"[0:a]atrim={s['start']:.3f}:{s['end']:.3f},asetpts=PTS-STARTPTS[a{k}];"
                    for k, s in enumerate(segs))
    cat = "".join(f"[v{k}][a{k}]" for k in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=1[v][a]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-filter_complex", parts + cat,
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-preset", "fast",
                    "-c:a", "aac", "-b:a", "192k", str(out)], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--words", required=True)
    ap.add_argument("--script", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--video")
    a = ap.parse_args()
    words = json.load(open(a.words))
    versions = json.load(open(a.script))["versions"]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    edl = pick(words, versions)
    json.dump(edl, open(out / "edl.json", "w"), indent=1)
    bad = 0
    for v in edl:
        dur = sum(s["end"] - s["start"] for s in v["segments"])
        print(f"{v['id']}: {len(v['lines'])} lines kept, {len(v['missing'])} missing, {dur:.1f}s")
        for m in v["missing"]:
            print(f"   MISSING: {m}")
        bad += bool(v["missing"])
        if a.video and v["segments"]:
            cut(a.video, v["segments"], out / f"{v['id']}-cut.mp4")
    sys.exit(2 if bad else 0)


if __name__ == "__main__":
    main()

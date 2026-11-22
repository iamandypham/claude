#!/usr/bin/env python3
"""Find each script version's last clean read in a raw recording and cut it.

Andy reads the versions back to back (any order) and restarts any line he
flubs. Each version owns the stretch of recording from its hook to the next
version's hook. Inside that stretch, every sentence keeps its LAST complete
read after the previous kept sentence; flubs, restarts and dead air go.

  python3 split_takes.py --words words.json --script scripts.json --out DIR [--video raw.mp4]

words.json  : [{"word": "...", "start": s, "end": s}, ...]  (transcribe.py)
scripts.json: {"versions": [{"id": "v1", "lines": ["sentence", ...]}, ...]}
Writes DIR/edl.json and, with --video, DIR/<id>-cut.mp4. Exit 2 if any line
was never read cleanly.
"""
import argparse, difflib, json, re, subprocess, sys
from pathlib import Path

PAD_IN, PAD_OUT = 0.08, 0.15     # seconds kept around each read, clamped to the neighbouring words
MIN_COVER = 0.90                 # share of the line's words a read must contain
MIN_RATIO = 0.80                 # overall similarity of the read to the line
MAX_GAP = 0.6                    # a pause longer than this inside a read is cut out
SILENCE_DB, SILENCE_MIN = -35, 0.6   # audio silences (Whisper often hides them inside a stretched word)


def norm(t):
    t = re.sub(r"\bwap\b", "whop", t.lower())
    t = t.replace("%", " percent").replace("&", " and ")
    return re.sub(r"[^a-z0-9' ]+", " ", t).split()


def similar(a, b):
    return a == b or difflib.SequenceMatcher(None, a, b).ratio() >= 0.6


def tokens(words):
    """Flat token list [(token, word_index)] so split numbers ('$6' '.4') line up with the script."""
    return [(t, k) for k, w in enumerate(words) for t in norm(w["word"])]


def reads(flat, target, lo, hi):
    """Complete reads of target inside flat[lo:hi]: (start_pos, end_pos, cover, ratio)."""
    n, out, tset = len(target), [], set(target)
    for a in range(lo, hi):
        # a read starts on the line's first word (fuzzy, Whisper mishears short words)
        # or, if that word was swallowed, exactly on its second word
        if not (similar(flat[a][0], target[0]) or (n > 1 and flat[a][0] == target[1])):
            continue
        for L in range(max(1, n - 2), n + 3):
            if a + L > hi:
                break
            # snap near-miss words (you're/your, an/and) onto the line's own words
            cand = [x[0] if x[0] in tset else next((t for t in target if similar(x[0], t)), x[0])
                    for x in flat[a:a + L]]
            sm = difflib.SequenceMatcher(None, cand, target)
            cover = sum(b.size for b in sm.get_matching_blocks()) / n
            # a complete read ends on the line's last word (or the one before it)
            if cover >= MIN_COVER and sm.ratio() >= MIN_RATIO and \
                    any(similar(cand[-1], t) for t in target[-2:]):
                out.append((a, a + L - 1, cover, sm.ratio()))
    return out


def regions(flat, versions):
    """Each version runs from the first read of its hook to the next version's hook."""
    starts = []
    for v in versions:
        hook = next((norm(l) for l in v["lines"] if norm(l)), None)
        hits = reads(flat, hook, 0, len(flat)) if hook else []
        starts.append(min((h[0] for h in hits), default=None))
    found = sorted(s for s in starts if s is not None)
    out = {}
    for v, s in zip(versions, starts):
        if s is None:
            out[v["id"]] = None
        else:
            nxt = [x for x in found if x > s]
            out[v["id"]] = (s, nxt[0] if nxt else len(flat))
    return out


def span(words, i, j):
    lo = words[i - 1]["end"] + 0.06 if i > 0 else 0.0   # stay clear of the previous (flubbed) word
    hi = words[j + 1]["start"] if j + 1 < len(words) else words[j]["end"] + PAD_OUT
    return max(lo, words[i]["start"] - PAD_IN), min(hi, words[j]["end"] + PAD_OUT)


def pick(words, versions):
    flat = tokens(words)
    reg = regions(flat, versions)
    edl = []
    for v in versions:
        spans, missing, partial = [], [], []
        r = reg[v["id"]]
        cursor, hi = r if r else (0, 0)
        for line in v["lines"]:
            target = norm(line)
            if not target:
                continue
            hits = reads(flat, target, cursor, hi)
            if not hits:
                missing.append(line)
                continue
            # last complete read wins; windows starting 1-2 words into that same read
            # (skipping its first word) belong to it; take the window that best matches the line
            last = max(h[0] for h in hits)
            same = [h for h in hits if last - 2 <= h[0] <= last]
            best = max(h[2] for h in same)
            a, b, cover, ratio = max((h for h in same if h[2] >= best - 1e-9),
                                     key=lambda h: (h[3], -h[0], h[1]))
            i, j = flat[a][1], flat[b][1]
            a0 = i
            for k in range(i + 1, j + 1):                        # cut pauses Whisper left as gaps
                if words[k]["start"] - words[k - 1]["end"] > MAX_GAP:
                    s, e = span(words, a0, k - 1)
                    spans.append({"line": line, "start": s, "end": e, "ratio": round(ratio, 3), "w": [a0, k - 1]})
                    a0 = k
            s, e = span(words, a0, j)
            spans.append({"line": line, "start": s, "end": e, "ratio": round(ratio, 3), "w": [a0, j]})
            if cover < 1:
                partial.append(line)
            cursor = b + 1
        merged = []
        for s in spans:
            if merged and s["start"] <= merged[-1]["end"]:
                merged[-1]["end"] = max(merged[-1]["end"], s["end"])
            else:
                merged.append({"start": s["start"], "end": s["end"]})
        edl.append({"id": v["id"], "lines": spans, "segments": merged, "missing": missing,
                    "check_by_ear": partial})
    return edl


def silences(video):
    """Silent stretches in the raw audio, from ffmpeg silencedetect."""
    p = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(video), "-af",
                        f"silencedetect=noise={SILENCE_DB}dB:d={SILENCE_MIN}", "-f", "null", "-"],
                       capture_output=True, text=True)
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", p.stderr)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", p.stderr)]
    return list(zip(st, en))


def drop_silence(segs, sil, keep=0.15):
    """Remove silent stretches inside kept segments, leaving `keep` seconds of air."""
    out = []
    for s in segs:
        cur = s["start"]
        for a, b in sil:
            if a >= cur and b <= s["end"] and b - a > 2 * keep:
                if a + keep > cur:
                    out.append({"start": cur, "end": a + keep / 2})
                cur = b - keep / 2
        out.append({"start": cur, "end": s["end"]})
    return [x for x in out if x["end"] - x["start"] > 0.05]


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
    sil = silences(a.video) if a.video else []
    for v in edl:
        v["segments"] = drop_silence(v["segments"], sil)
    json.dump(edl, open(out / "edl.json", "w"), indent=1)
    bad = 0
    for v in edl:
        dur = sum(s["end"] - s["start"] for s in v["segments"])
        print(f"{v['id']}: {len(set(s['line'] for s in v['lines']))} lines kept, {len(v['missing'])} missing, {dur:.1f}s")
        for m in v["missing"]:
            print(f"   MISSING: {m}")
        for m in v["check_by_ear"]:
            print(f"   CHECK BY EAR (a word differs from the script): {m}")
        bad += bool(v["missing"])
        if a.video and v["segments"]:
            cut(a.video, v["segments"], out / f"{v['id']}-cut.mp4")
    sys.exit(2 if bad else 0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Checks on a long-form (16:9) master rendered by build_long.py.

  python3 -I check_long.py WORK/timeline.json [--sheet-every 20]
        [--words RAW_WORDS.json --final-words FINAL_WORDS.json] [--transcribe]

--words is the transcript of the RAW camera audio (the file plan_long.py wrote);
--final-words is a transcript of the FINISHED master, same model. With both, the
check lines the two up and fails when words that should be there are missing next
to a cut. --transcribe makes FINAL_WORDS itself with faster-whisper when it is
installed (small.en, CPU). Use the same model for both transcripts, or model
differences show up as false alarms.

Reads timeline.json (written by build_long.py) and the master next to it, then
prints PASS/FAIL rows and writes:
  WORK/check_report.json
  WORK/sheet_cuts.jpg     one frame just after every cut (up to 60)
  WORK/sheet_events.jpg   one frame inside every text / proof event
  WORK/sheet_even.jpg     one frame every --sheet-every seconds

The sheets are for a human or Claude to look at: a script cannot judge a frame.
Exit code 1 when any row fails.
"""
import argparse, json, os, re, subprocess, sys


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    r = sh(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path])
    d = json.loads(r.stdout or "{}")
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    a = next((s for s in d["streams"] if s["codec_type"] == "audio"), None)
    n, m = v["r_frame_rate"].split("/")
    return {"w": v["width"], "h": v["height"], "fps": float(n) / float(m), "pix": v.get("pix_fmt"),
            "vdur": float(v.get("duration") or d["format"]["duration"]),
            "adur": float(a.get("duration") or d["format"]["duration"]) if a else None,
            "dur": float(d["format"]["duration"]), "has_audio": a is not None}


def loudness(path):
    r = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"])
    tail = r.stderr[-1500:]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", tail)
    tp = re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail)
    return (float(i.group(1)) if i else None, float(tp.group(1)) if tp else None)


def detect(path, flt, pat):
    r = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-an", "-vf", f"scale=320:-2,{flt}", "-f", "null", "-"])
    return re.findall(pat, r.stderr)


def label_font():
    """A font file for drawtext. Windows ffmpeg builds have no fontconfig, so drawtext needs a path there."""
    for f in (r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/System/Library/Fonts/Supplemental/Arial Bold.ttf"):
        if os.path.exists(f):
            return f.replace("\\", "/").replace(":", "\\:")
    return None


def sheet(path, times, out, cols=6, w=480):
    times = [t for t in times if t is not None]
    if not times:
        return 0
    tmp = out + ".frames"
    os.makedirs(tmp, exist_ok=True)
    font = label_font()
    files = []
    for t in times:
        # numbered by success so the sheet step can read a plain sequence (no glob: Windows ffmpeg lacks it)
        f = os.path.join(tmp, f"{len(files):03d}.jpg")
        label = f"{int(t // 60)}\\:{t % 60:05.2f}"
        text = (f"drawtext=fontfile='{font}':" if font else "drawtext=") + \
            f"text='{label}':x=8:y=8:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6"
        for vf in (f"scale={w}:-2,{text}", f"scale={w}:-2"):  # second try: no label rather than no frame
            sh(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{max(t, 0):.3f}", "-i", path,
                "-frames:v", "1", "-vf", vf, "-q:v", "4", f])
            if os.path.exists(f):
                files.append(f)
                break
    if not files:
        return 0
    rows = (len(files) + cols - 1) // cols
    sh(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-start_number", "0", "-i", os.path.join(tmp, "%03d.jpg"),
        "-vf", f"tile={cols}x{rows}", "-frames:v", "1", "-q:v", "4", out])
    for f in files:
        os.remove(f)
    os.rmdir(tmp)
    return len(files)


def silences(path, db=-38.0, dur=1.0):
    r = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn", "-af", f"silencedetect=noise={db}dB:d={dur}",
            "-f", "null", "-"])
    st = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
    en = [float(x) for x in re.findall(r"silence_end: (-?[\d.]+)", r.stderr)]
    return list(zip(st, en + [None] * (len(st) - len(en))))


def has_c2pa(path):
    """True when the file carries a C2PA / JUMBF content-credentials box."""
    marks, tail = (b"c2pa", b"jumb", b"jumd"), b""
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8 << 20)
            if not chunk:
                return False
            buf = tail + chunk
            if any(m in buf for m in marks):
                return True
            tail = buf[-8:]


def norm_word(w):
    return re.sub(r"[^a-z0-9$%]", "", w.lower())


def load_words(path):
    d = json.load(open(path))
    d = d.get("words", d) if isinstance(d, dict) else d
    out = []
    for x in d:
        w = norm_word(str(x.get("w", x.get("word", x.get("text", "")))))
        if w:
            out.append((w, float(x.get("s", x.get("start", 0.0))), float(x.get("e", x.get("end", 0.0)))))
    return out


def transcribe(master, out):
    import numpy as np
    from faster_whisper import WhisperModel
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", master, "-vn", "-ac", "1", "-ar", "16000",
                        "-f", "f32le", "-"], capture_output=True)
    y = np.frombuffer(r.stdout, dtype=np.float32)
    m = WhisperModel("small.en", device="cpu", compute_type="int8", cpu_threads=os.cpu_count() or 4)
    segs, _ = m.transcribe(y, word_timestamps=True, condition_on_previous_text=False, vad_filter=True, beam_size=1)
    words = [{"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2)} for sg in segs for w in sg.words]
    json.dump(words, open(out, "w"))
    return len(words)


def word_diff(raw, final, segs, co, near=0.8):
    """Words the cut should contain (raw words whose middle sits in a kept range) against words heard in the master.
    Returns (expected, heard, [(out_time, missing words, heard instead)]) for differences next to a cut."""
    import difflib
    kept = [(sg["a"], sg["b"], sg["out_a"]) for sg in segs]
    exp = []
    for w, s0, e0 in raw:
        mid = (s0 + e0) / 2
        for a, b, oa in kept:
            if a <= mid < b:
                exp.append((w, co + oa + mid - a))
                break
    edges = sorted({co + sg["out_a"] for sg in segs[1:]})
    sm = difflib.SequenceMatcher(None, [e[0] for e in exp], [f[0] for f in final], autojunk=False)
    bad = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        # "going to" heard as "gonna" is the transcriber, not the cut: only count words that went missing
        if tag == "equal" or (i2 - i1) - (j2 - j1) < 2:
            continue
        t = exp[i1][1]
        if edges and min(abs(t - c) for c in edges) <= near:
            bad.append((round(t, 2), " ".join(e[0] for e in exp[i1:i2]), " ".join(f[0] for f in final[j1:j2])))
    return len(exp), len(final), bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("timeline")
    ap.add_argument("--sheet-every", type=float, default=20.0)
    ap.add_argument("--lufs", type=float, default=-14.0)
    ap.add_argument("--min-seg", type=float, default=0.20, help="a kept range shorter than this is a sliver")
    ap.add_argument("--max-silence", type=float, default=1.0, help="longest silent stretch allowed, seconds")
    ap.add_argument("--words", help="transcript of the raw camera audio (plan_long.py output)")
    ap.add_argument("--final-words", help="transcript of the finished master, same model as --words")
    ap.add_argument("--transcribe", action="store_true", help="make --final-words with faster-whisper small.en")
    a = ap.parse_args()
    tl = json.load(open(a.timeline))
    work = os.path.dirname(os.path.abspath(a.timeline))
    master = os.path.join(work, f"{tl['name']}_master.mp4")
    rows = []

    def row(name, ok, detail):
        rows.append({"check": name, "verdict": "PASS" if ok else "FAIL", "detail": detail})
        print(f"{'PASS' if ok else 'FAIL':5} {name}: {detail}")

    if not os.path.exists(master):
        row("master exists", False, master)
        sys.exit(1)
    p = probe(master)
    W, H = tl["size"]
    row("size", (p["w"], p["h"]) == (W, H), f"{p['w']}x{p['h']} (want {W}x{H})")
    row("frame rate", abs(p["fps"] - tl["fps"]) < 0.01, f"{p['fps']:.2f} (want {tl['fps']})")
    row("pixel format", p["pix"] == "yuv420p", str(p["pix"]))
    row("length", abs(p["dur"] - tl["total"]) < 0.1, f"{p['dur']:.2f} s (timeline {tl['total']:.2f} s)")
    row("audio present", p["has_audio"], "yes" if p["has_audio"] else "no audio stream")
    if p["has_audio"]:
        row("audio and video same length", abs(p["adur"] - p["vdur"]) < 0.1, f"video {p['vdur']:.2f} s, audio {p['adur']:.2f} s")
        i, tp = loudness(master)
        row("loudness", i is not None and abs(i - a.lufs) <= 1.0, f"{i} LUFS (want {a.lufs} +/- 1)")
        row("true peak", tp is not None and tp <= -1.0, f"{tp} dBFS (want -1.0 or lower)")
    black = detect(master, "blackdetect=d=0.2:pix_th=0.06", r"black_start:([\d.]+) black_end:([\d.]+)")
    row("no black gaps", not black, f"{len(black)} found" + (f", first at {black[0][0]} s" if black else ""))
    co = tl.get("cold_open", 0.0)
    # a held proof image is a still on purpose, so a freeze that starts inside a proof window does not count
    proof_wins = [(co + e["start"] - 0.5, co + e["start"] + e.get("dur", 0) + 0.5)
                  for e in list(tl.get("proof", [])) + list(tl.get("cards", []))]
    frozen = [f for f in detect(master, "freezedetect=n=0.001:d=3", r"freeze_start: ([\d.]+)")
              if not any(x <= float(f) <= y for x, y in proof_wins)]
    row("no frozen picture over 3 s (proof holds excluded)", not frozen,
        f"{len(frozen)} found" + (f", first at {frozen[0]} s" if frozen else ""))

    segs = tl["segments"]
    sliv = [(sg["out_a"] + co, sg["b"] - sg["a"]) for sg in segs if sg["b"] - sg["a"] < a.min_seg]
    row(f"no slivers (kept range under {a.min_seg} s)", not sliv,
        f"{len(sliv)} found" + (f", first at {sliv[0][0]:.2f} s ({sliv[0][1]:.2f} s long)" if sliv else ""))
    if p["has_audio"]:
        tail_from = p["dur"] - max(1.0, tl.get("tail", 0.0) + 0.5)
        sil = [(x, y) for x, y in silences(master, dur=a.max_silence) if x < tail_from and x > 0.05]
        row(f"no silence over {a.max_silence} s (end tail excluded)", not sil,
            f"{len(sil)} found" + (f", first at {sil[0][0]:.2f} s" if sil else ""))
    c2 = has_c2pa(master)
    row("no C2PA / content-credentials bytes", not c2, "found" if c2 else "clean")
    fw = a.final_words or (os.path.join(work, "final_words.json") if a.transcribe else None)
    if a.transcribe:
        try:
            print(f"transcribed {transcribe(master, fw)} words -> {fw}")
        except Exception as e:                              # no faster-whisper here: say so, do not pass silently
            row("words kept at cuts", False, f"could not transcribe: {e}")
            fw = None
    if a.words and fw and os.path.exists(fw):
        ne, nh, bad = word_diff(load_words(a.words), load_words(fw), segs, co)
        row("words kept at cuts", not bad, f"expected {ne} words, heard {nh}, {len(bad)} gaps next to a cut"
            + "".join(f"; {t} s missing [{m}] heard [{h}]" for t, m, h in bad[:5]))
    else:
        print("SKIP  words kept at cuts: pass --words and --final-words (or --transcribe) to run it")
    cut_times = [s["out_a"] + co + 0.05 for s in segs[1:]]
    step = max(1, len(cut_times) // 60 + (1 if len(cut_times) % 60 else 0)) if len(cut_times) > 60 else 1
    n1 = sheet(master, cut_times[::step], os.path.join(work, "sheet_cuts.jpg"))
    ev = []
    text = tl.get("text") or {}
    texts = ([text["hook"]] if text.get("hook") else []) + list(text.get("steps", [])) + list(text.get("phrases", []))
    for e in texts:                                       # text times are in main-video time (before the cold open)
        ev.append(co + (e["start"] + e.get("end", e["start"] + 2.0)) / 2)
    for e in tl.get("proof", []):
        ev.append(co + e["start"] + min(0.1, e.get("dur", 1) / 2))
        ev.append(co + e["start"] + e.get("dur", 1) / 2)
    for e in tl.get("cards", []):
        ev.append(co + e["start"] + e.get("dur", 1) / 2)
    n2 = sheet(master, sorted(ev)[:144], os.path.join(work, "sheet_events.jpg"))
    even = [t for t in (i * a.sheet_every + 1.0 for i in range(int(p["dur"] // a.sheet_every) + 1)) if t < p["dur"]]
    n3 = sheet(master, even[:72], os.path.join(work, "sheet_even.jpg"))
    print(f"sheets: {n1} cut frames, {n2} event frames, {n3} evenly spaced frames -> look at them before calling it done")
    json.dump({"master": master, "rows": rows, "sheets": {"cuts": n1, "events": n2, "even": n3}},
              open(os.path.join(work, "check_report.json"), "w"), indent=1)
    sys.exit(0 if all(r["verdict"] == "PASS" for r in rows) else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Checks on a long-form (16:9) master rendered by build_long.py.

  python3 -I check_long.py WORK/timeline.json [--sheet-every 20]

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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("timeline")
    ap.add_argument("--sheet-every", type=float, default=20.0)
    ap.add_argument("--lufs", type=float, default=-14.0)
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

#!/usr/bin/env python3
"""BG gates: our own house checks, run after the Vibe Editing kit's audits on every clip.

The kit's audits check mechanics (onset, levels, caption timing). These check the BG rules the kit
does not know about. Each gate prints PASS / FAIL / REPORT / N/A with its evidence; exit 1 on any
FAIL. REPORT and N/A never count as a pass: read them.

  G1 c2pa         the file carries no C2PA / JUMBF manifest ("Made with Claude" stamp). Run it on the
                  file that will actually be uploaded, outside /mnt/project-files: every file written
                  there is stamped by the platform. Strip with bg_strip_c2pa (ffmpeg remux, see README).
  G2 face_clear   captions never sit on Andy's face. Every 0.25 s: caption pixels (final minus the
                  uncaptioned render) inside ANY detected face box. Fails on any overlap; N/A (not pass)
                  when no face is found in any captioned frame.
  G3 numbers      every on-screen number is listed for the proof check (RULES 1.4, report-only) and
                  malformed numbers (a split token like "$2 ,880") FAIL. Reads the SRT, digits only.
  G4 screen_share --screen-map sx:sy:w:h:ox:oy maps the screen-share box in the source (sx,sy,w,h)
                  to where it sits in the output (ox,oy, same size: never scaled). PSNR must stay
                  40 dB+ at every sample, best of +-1 frame (RULES 1.7: never altered). One continuous
                  span only.
                  N/A without a map; FAIL if no frame could be compared.
  G5 av_sync      audio offset (cross-correlation vs the source) and picture offset (frame matching in
                  --video-map sx:sy:w:h:ox:oy, a region copied 1:1 from source to output) at several
                  points. On sources that repeat frames the picture offset is a range. FAIL if audio
                  drifts more than one frame between points, or the audio offset sits more than one
                  frame outside the picture range. Without --video-map it can only REPORT.

Usage:
  bg_gates.py --final F.mp4 --clean UNCAPTIONED.mp4 --source SRC.mp4 --src-start SEC
              --srt captions.srt --yunet yunet.onnx [--video-map ...] [--screen-map ...] [--out r.json]
--src-start is the source time of the clip's first frame (measure it; don't assume the cut point).
"""
import argparse, json, re, subprocess, sys
import numpy as np


def sh(cmd, binary=False):
    r = subprocess.run(cmd, capture_output=True)
    return r.stdout if binary else r.stdout.decode(errors="ignore")


def probe(path):
    j = json.loads(sh(["ffprobe", "-v", "error", "-show_entries",
                       "stream=codec_type,width,height,r_frame_rate:format=duration", "-of", "json", path]))
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    n, d = v["r_frame_rate"].split("/")
    return float(j["format"]["duration"]), int(v["width"]), int(v["height"]), float(n) / float(d)


_FPS = {}


def frame(path, t, w, h, gray=False):
    """The frame nearest time t (ffmpeg's accurate seek returns the first frame at or after the
    seek point, so seek half a frame early; otherwise a start time a hair past a frame boundary
    silently compares the next frame)."""
    if path not in _FPS:
        _FPS[path] = probe(path)[3]
    fmt, ch = ("gray", 1) if gray else ("bgr24", 3)
    raw = sh(["ffmpeg", "-v", "error", "-ss", f"{max(0.0, t - 0.5 / _FPS[path]):.5f}", "-i", path, "-frames:v", "1",
              "-f", "rawvideo", "-pix_fmt", fmt, "-"], binary=True)
    if len(raw) != w * h * ch:
        return None
    a = np.frombuffer(raw, np.uint8)
    return a.reshape(h, w) if gray else a.reshape(h, w, 3)


def audio(path, start, dur, sr=16000):
    raw = sh(["ffmpeg", "-v", "error", "-ss", f"{max(0.0, start):.4f}", "-t", f"{dur:.4f}", "-i", path,
              "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], binary=True)
    return np.frombuffer(raw, np.float32)


def g1_c2pa(final):
    data = open(final, "rb").read()
    hits = [m.decode() for m in (b"c2pa", b"jumb", b"C2PA", b"contentauth") if m in data]
    return ("FAIL", f"C2PA markers found: {hits}") if hits else ("PASS", "no c2pa/jumb/contentauth bytes in file")


def g2_face_clear(final, clean, yunet, step=0.25):
    import cv2
    dur, w, h, _ = probe(final)
    det = cv2.FaceDetectorYN.create(yunet, "", (w, h), 0.5)
    checked, bad, tight = 0, [], None
    for t in np.arange(0.2, dur - 0.1, step):
        a, b = frame(final, t, w, h), frame(clean, t, w, h)
        if a is None or b is None:
            continue
        cap = cv2.absdiff(a, b).max(axis=2) > 40
        if cap.sum() < 50:
            continue  # no caption on screen at t
        _, faces = det.detect(b)
        if faces is None or not len(faces):
            continue
        checked += 1
        ys = np.where(cap.sum(axis=1) > 3)[0]
        for f in faces:
            x, y, fw, fh = [int(v) for v in f[:4]]
            x0, y0, x1, y1 = max(0, x), max(0, y), min(w, x + fw), min(h, y + fh)
            inside = int(cap[y0:y1, x0:x1].sum())
            if inside > 50:
                bad.append((round(float(t), 2), inside))
            # clearance between the caption band and the face box, above or below it
            gap = max(int(ys.min()) - y1, y0 - int(ys.max()))
            if tight is None or gap < tight[0]:
                tight = (gap, round(float(t), 2))
    if not checked:
        return "N/A", "no captioned frame had a detected face: check by eye"
    if bad:
        return "FAIL", f"caption pixels inside a face box in {len(bad)}/{checked} frames, e.g. {bad[:4]}"
    return "PASS", f"{checked} captioned frames with a face, none overlap; tightest clearance between captions and a face box {tight[0]}px at {tight[1]}s"


def g3_numbers(srt):
    text = re.sub(r"<[^>]+>", "", open(srt).read())
    lines = [l for l in text.splitlines() if l and not l.strip().isdigit() and "-->" not in l]
    joined = " ".join(lines)
    bad = re.findall(r"\$?\d+\s+[,.]\d+", joined)
    nums = re.findall(r"\$?\d[\d,.]*[kKmM%]?", joined)
    if bad:
        return "FAIL", f"malformed numbers on screen: {bad}; all numbers: {nums}"
    return "REPORT", f"numbers on screen (each needs a proof asset, RULES 1.4): {nums or 'none'}"


def parse_map(m):
    sx, sy, w, h, ox, oy = map(int, m.split(":"))
    return sx, sy, w, h, ox, oy


def g4_screen(final, source, src_start, smap, n=8):
    if not smap:
        return "N/A", "no --screen-map given (no screen share in this source?)"
    sx, sy, bw, bh, ox, oy = parse_map(smap)
    dur, w, h, _ = probe(final)
    _, sw, shh, _ = probe(source)
    _, _, _, sfps = probe(source)
    psnrs = []
    for t in np.linspace(0.3, dur - 0.3, n):
        o = frame(final, t, w, h)
        if o is None:
            continue
        a = o[oy:oy + bh, ox:ox + bw].astype(float)
        best = None
        for j in (-1, 0, 1):  # allow one frame of phase (sources that repeat frames)
            s = frame(source, src_start + t + j / sfps, sw, shh)
            if s is None:
                continue
            b = s[sy:sy + bh, sx:sx + bw].astype(float)
            if a.shape != b.shape or a.size == 0:
                return "FAIL", f"map outside the frame: output region {a.shape}, source region {b.shape}"
            mse = ((a - b) ** 2).mean()
            p_ = 99.0 if mse == 0 else 10 * np.log10(255 ** 2 / mse)
            best = p_ if best is None else max(best, p_)
        if best is not None:
            psnrs.append(best)
    if not psnrs:
        return "FAIL", "no frame could be compared"
    worst = min(psnrs)
    return ("PASS" if worst >= 40 else "FAIL", f"{len(psnrs)} frames, worst screen-share PSNR {worst:.1f} dB (pass at 40+)")


def audio_offset(final, source, src_start, t, win=1.5, search=0.25, sr=16000):
    o = audio(final, t, win)
    s = audio(source, src_start + t - search, win + 2 * search)
    if len(o) < sr * 0.5 or len(s) < len(o):
        return None
    o = (o - o.mean()) / (o.std() + 1e-9); s = (s - s.mean()) / (s.std() + 1e-9)
    c = np.correlate(s, o, mode="valid")
    return float(np.argmax(c) / sr - search) * 1000


def picture_offset(final, source, src_start, t, vmap, fps, k=4, tie=1.10):
    """Range (lo_ms, hi_ms) of source offsets that match output frame t inside the 1:1 region
    equally well (within 10% of the best MSE). Sources that repeat frames give a range, not a point."""
    sx, sy, bw, bh, ox, oy = parse_map(vmap)
    _, w, h, _ = probe(final); _, sw, shh, _ = probe(source)
    o = frame(final, t, w, h, gray=True)
    if o is None:
        return None
    o = o[oy:oy + bh, ox:ox + bw].astype(float)
    scores = []
    for j in range(-k, k + 1):
        s = frame(source, src_start + t + j / fps, sw, shh, gray=True)
        if s is None:
            continue
        scores.append((((o - s[sy:sy + bh, sx:sx + bw].astype(float)) ** 2).mean(), j))
    if len(scores) < 3:
        return None
    best = min(m for m, _ in scores)
    js = [j for m, j in scores if m <= best * tie + 1e-6]
    if min(js) == -k or max(js) == k:
        return None  # match runs off the search window: no usable picture fix
    return min(js) * 1000 / fps, max(js) * 1000 / fps


def g5_sync(final, source, src_start, vmap, points=5):
    dur, _, _, fps = probe(final)
    fms = 1000 / fps
    ts = np.linspace(0.6, max(0.7, dur - 1.9), points)
    aud = [audio_offset(final, source, src_start, t) for t in ts]
    aud = [round(a, 1) for a in aud if a is not None]
    if len(aud) < 3:
        return "FAIL", f"audio offset measured at fewer than 3 points: {aud}"
    drift = max(aud) - min(aud)
    if drift > fms:
        return "FAIL", f"audio drifts {drift:.1f} ms between points {aud} (limit {fms:.1f})"
    if not vmap:
        return "REPORT", f"audio offsets ms {aud}, no drift; picture not measured (pass --video-map), so A/V sync is unproven"
    pics = [picture_offset(final, source, src_start, t, vmap, fps) for t in ts]
    pics = [p for p in pics if p is not None]
    if len(pics) < 3:
        return "REPORT", f"audio offsets ms {aud}; picture offset could not be fixed at 3+ points"
    lo = max(p[0] for p in pics); hi = min(p[1] for p in pics)  # offsets consistent with every point
    a = float(np.median(aud))
    if lo > hi:
        return "FAIL", f"picture offset inconsistent between points {[(round(p[0],1), round(p[1],1)) for p in pics]}"
    ok = lo - fms <= a <= hi + fms
    return ("PASS" if ok else "FAIL",
            f"audio offset {a:.1f} ms (points {aud}); picture offset {lo:.1f}..{hi:.1f} ms (range from repeated frames); "
            f"pass needs audio within one frame ({fms:.1f} ms) of that range")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", required=True); ap.add_argument("--clean", required=True)
    ap.add_argument("--source", required=True); ap.add_argument("--src-start", type=float, required=True)
    ap.add_argument("--srt", required=True); ap.add_argument("--yunet", required=True)
    ap.add_argument("--video-map"); ap.add_argument("--screen-map"); ap.add_argument("--out")
    a = ap.parse_args()
    res = {
        "G1_c2pa": g1_c2pa(a.final),
        "G2_face_clear": g2_face_clear(a.final, a.clean, a.yunet),
        "G3_numbers": g3_numbers(a.srt),
        "G4_screen_share": g4_screen(a.final, a.source, a.src_start, a.screen_map),
        "G5_av_sync": g5_sync(a.final, a.source, a.src_start, a.video_map),
    }
    for k, (v, e) in res.items():
        print(f"{v:6} {k}: {e}")
    if a.out:
        json.dump({k: {"verdict": v, "evidence": e} for k, (v, e) in res.items()}, open(a.out, "w"), indent=1)
    sys.exit(1 if any(v == "FAIL" for v, _ in res.values()) else 0)


if __name__ == "__main__":
    main()

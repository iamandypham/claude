#!/usr/bin/env python3
"""Plan a long-form cut: find dead air, claps and retakes, and sync camera to screen.

    python3 -I scripts/plan_long.py --cam cam.mp4 [--screen screen.mkv] --work WORK --name my-video

Writes WORK/words.json (if missing), WORK/plan.json, WORK/plan.md (read this and
check the retakes by ear) and WORK/<name>_config.json, a starter config for
build_long.py. Nothing is rendered here.

How cuts are chosen: speech is found from the audio level, not from Whisper word
times (R-103). Pauses longer than --max-pause are cut down to --pause-keep, so
every cut sits in silence. A stretch with sound but no words (a clap, a click, a
cough) is dropped. Claps split the take into sections.
"""
import argparse, difflib, json, os, re, subprocess, sys, wave
import numpy as np

HOP = 0.01


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("failed: " + " ".join(cmd)[:300] + "\n" + r.stderr[-2000:])
    return r


def probe(path):
    j = json.loads(run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", path]).stdout)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), {})
    n, d = (v.get("avg_frame_rate") or "30/1").split("/")
    return {"duration": float(j["format"]["duration"]), "w": v.get("width"), "h": v.get("height"),
            "fps": float(n) / float(d) if float(d or 0) else 30.0,
            "has_audio": any(s["codec_type"] == "audio" for s in j["streams"])}


def to_wav(src, dst, sr):
    run(["ffmpeg", "-hide_banner", "-y", "-i", src, "-vn", "-ac", "1", "-ar", str(sr),
         "-af", "aresample=async=1:first_pts=0", "-c:a", "pcm_s16le", dst])
    w = wave.open(dst)
    return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


def level_db(x, sr):
    """RMS level in dB, one value per 10 ms (20 ms window)."""
    hop = int(sr * HOP)
    n = len(x) // hop
    sq = (x[:n * hop] ** 2).reshape(n, hop).mean(axis=1)
    sq = (sq + np.concatenate([sq[1:], sq[-1:]])) / 2
    return 10 * np.log10(sq + 1e-10)


def runs(mask):
    d = np.diff(np.concatenate([[0], mask.astype(np.int8), [0]]))
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))


def speech_runs(db):
    noise = np.percentile(db, 15); loud = np.percentile(db, 95)
    thr = max(noise + 10, loud - 30)
    m = db > thr
    for a, b in runs(~m):                      # fill dips under 80 ms
        if b - a < 8 and a > 0 and b < len(m): m[a:b] = True
    for a, b in runs(m):                       # drop blips under 60 ms
        if b - a < 6: m[a:b] = False
    return [(a * HOP, b * HOP) for a, b in runs(m)], thr, noise, loud


def quietest(db, t0, t1, win=0.05):
    """Start time of the quietest 50 ms window between t0 and t1."""
    a, b = max(0, int(t0 / HOP)), min(len(db), int(t1 / HOP))
    k = max(1, int(win / HOP))
    if b - a <= k: return max(0.0, t0)
    c = np.convolve(db[a:b], np.ones(k) / k, mode="valid")
    return (a + int(np.argmin(c))) * HOP + win / 2


def norm(w):
    return re.sub(r"[^a-z0-9$%]", "", w.lower())


def xcorr_offset(a, b, sr, max_lag, phat=False):
    """Lag (s) of b relative to a: an event at time t in a is at t + lag in b.
    Returns (lag, confidence). Confidence is the peak over the next best peak more than
    0.5 s away (plain), or the peak over the RMS of the rest of the window (phat)."""
    n = 1 << int(np.ceil(np.log2(len(a) + len(b))))
    A = np.fft.rfft(a - a.mean(), n); B = np.fft.rfft(b - b.mean(), n)
    X = np.conj(A) * B
    if phat:                                   # whiten: robust when the two mics sound different
        X = X / (np.abs(X) + 1e-9)
    c = np.fft.irfft(X, n)
    L = int(max_lag * sr)
    c = np.concatenate([c[-L:], c[:L + 1]])
    k = int(np.argmax(c))
    peak = c[k]
    if phat:
        g = max(1, int(0.005 * sr))
        rest = np.concatenate([c[:max(0, k - g)], c[k + g:]])
        conf = float(peak / (np.sqrt((rest ** 2).mean()) + 1e-12)) if len(rest) else 0.0
    else:
        g = int(0.5 * sr)
        rest = np.concatenate([c[:max(0, k - g)], c[k + g:]])
        conf = float(peak / (np.abs(rest).max() + 1e-9)) if len(rest) else 0.0
    return (k - L) / sr, conf


def sync(cam_wav, scr_wav, sr):
    """screen_time = camera_time + offset. Coarse on the level envelope (10 ms steps),
    then fine on the whitened waveform (sample steps), early and late to measure drift."""
    env = lambda x: level_db(x, sr)
    ea, eb = env(cam_wav[:sr * 900]), env(scr_wav[:sr * 900])
    coarse, conf = xcorr_offset(ea, eb, int(1 / HOP), min(600, len(ea) * HOP * 0.9))
    def fine(t_cam, span=40):
        i = int(t_cam * sr); j = int((t_cam + coarse) * sr)
        if i < 0 or j < 0: return None
        a = cam_wav[i:i + span * sr]; b = scr_wav[j:j + span * sr]
        n = min(len(a), len(b))
        if n < sr * 5: return None
        lag, c = xcorr_offset(a[:n], b[:n], sr, 0.25, phat=True)
        return coarse + lag, c
    t_early = max(0.0, -coarse) + 2.0
    f1 = fine(t_early)
    dur = min(len(cam_wav) / sr, len(scr_wav) / sr - coarse)
    f2 = fine(max(t_early, dur - 60)) if dur > 180 else None
    out = {"offset": round((f1 or (coarse, 0))[0], 4), "coarse": round(coarse, 3), "confidence": round(conf, 2),
           "fine_confidence": round(f1[1], 1) if f1 else None}
    if f1 and f2:
        out["offset_late"] = round(f2[0], 4)
        out["drift_ms"] = round((f2[0] - f1[0]) * 1000, 1)
        out["fine_confidence_late"] = round(f2[1], 1)
    return out


def mmss(t):
    return f"{int(t // 60)}:{t % 60:05.2f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cam", required=True); ap.add_argument("--screen")
    ap.add_argument("--work", required=True); ap.add_argument("--name", default="long-form")
    ap.add_argument("--model", default="medium.en")
    ap.add_argument("--max-pause", type=float, default=0.6, help="pauses longer than this are cut")
    ap.add_argument("--pause-keep", type=float, default=0.3, help="what a cut pause is trimmed to")
    ap.add_argument("--sync-offset", type=float, help="set by hand when the screen file has no audio")
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=True)
    cam = probe(a.cam); scr = probe(a.screen) if a.screen else None
    sr = 16000
    x = to_wav(a.cam, os.path.join(a.work, "cam16k.wav"), sr)
    wpath = os.path.join(a.work, "words.json")
    if not os.path.exists(wpath):
        from faster_whisper import WhisperModel
        m = WhisperModel(a.model, device="cpu", compute_type="int8")
        segs, _ = m.transcribe(x, beam_size=5, word_timestamps=True)
        json.dump([{"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2)} for s in segs for w in s.words],
                  open(wpath, "w"), indent=0)
    words = json.load(open(wpath))
    db = level_db(x, sr)
    sp, thr, noise, loud = speech_runs(db)

    # Runs with no words on them AND no pitch are noise; short loud ones are claps. Word times from the transcript
    # drift by a few tenths of a second, so a short word ("So", "But", "Four") can look wordless: a run that any word
    # touches, or that is mostly pitched, is speech and is never dropped here (10 Nov 2026: 30 words lost this way).
    def words_in(t0, t1):
        return [w for w in words if w["s"] < t1 and w["e"] > t0]
    def pitched(t0, t1):
        seg = x[int(max(t0 - 0.03, 0) * sr):int((t1 + 0.03) * sr)].astype(np.float32)
        fl, hop, res = int(0.04 * sr), int(0.01 * sr), []
        for i in range(0, len(seg) - fl, hop):
            f = seg[i:i + fl]
            if not f.any(): continue
            f = f - f.mean(); ac = np.correlate(f, f, "full")[fl - 1:]
            if ac[0] <= 0: continue
            res.append((ac / ac[0])[sr // 320:sr // 75].max() > 0.5)
        return bool(res) and float(np.mean(res)) >= 0.4
    claps, noise_runs, voiced = [], [], []
    for t0, t1 in sp:
        peak = float(db[int(t0 / HOP):max(int(t0 / HOP) + 1, int(t1 / HOP))].max())
        if not words_in(t0 - 0.15, t1 + 0.15) and not pitched(t0, t1):
            (claps if (t1 - t0) < 0.3 and peak >= loud - 3 else noise_runs).append([round(t0, 2), round(t1, 2)])
        else:
            voiced.append([t0, t1])
    # utterances: voiced runs joined across short pauses
    pad = a.pause_keep / 2
    utts = []
    for t0, t1 in voiced:
        if utts and t0 - utts[-1][1] <= a.max_pause and not any(utts[-1][1] <= c[0] < t0 for c in claps + noise_runs):
            utts[-1][1] = t1
        else:
            utts.append([t0, t1])
    keeps = []
    for i, (t0, t1) in enumerate(utts):
        k0 = max(0.0, t0 - pad); k1 = min(len(x) / sr, t1 + pad)
        if keeps: k0 = max(k0, keeps[-1][1])
        keeps.append([round(k0, 3), round(k1, 3)])
    U = [{"i": i, "s": k[0], "e": k[1], "text": " ".join(w["w"].strip() for w in words_in(*k)),
          "tok": [norm(w["w"]) for w in words_in(*k) if norm(w["w"])]} for i, k in enumerate(keeps)]

    # retakes 1: an utterance that starts like the next one is a false start
    drops, flags = [], []
    for i, u in enumerate(U):
        for j in (i + 1, i + 2):
            if j >= len(U) or len(u["tok"]) < 2: continue
            v = U[j]; n = min(6, len(u["tok"]), len(v["tok"]))
            if n < 2: continue
            r = difflib.SequenceMatcher(None, u["tok"][:n], v["tok"][:n]).ratio()
            if r >= 0.75 and len(u["tok"]) <= 1.5 * len(v["tok"]) + 2:
                drops.append([u["s"], u["e"]])
                flags.append({"kind": "retake", "drop": [u["s"], u["e"]], "dropped": u["text"], "kept": v["text"][:160], "match": round(r, 2)})
                u["retake_of"] = j
                break
    # retakes 2: the same 3 words said again within one utterance, after a pause.
    # These are only flagged (maybe_drops): a human or Claude reads them before they are cut.
    maybes = []
    toks = [(norm(w["w"]), w) for w in words if norm(w["w"])]
    i = 0
    while i < len(toks) - 5:
        hit = None
        for j in range(i + 2, min(i + 14, len(toks) - 2)):
            if [t[0] for t in toks[i:i + 3]] == [t[0] for t in toks[j:j + 3]]:
                gap = toks[j][1]["s"] - toks[j - 1][1]["e"]
                if gap >= 0.2 and toks[j][1]["s"] - toks[i][1]["s"] < 12:
                    hit = j; break
        if hit:
            tri = [t[0] for t in toks[i:i + 3]]
            again = sum(1 for k in range(i, min(i + 40, len(toks) - 2)) if [t[0] for t in toks[k:k + 3]] == tri)
            if again >= 3:      # "the exact same X, the exact same Y, ...": a list, not a restart
                i += 1; continue
            d0 = quietest(db, toks[i][1]["s"] - 0.25, toks[i][1]["s"] + 0.03)
            d1 = quietest(db, toks[hit][1]["s"] - 0.3, toks[hit][1]["s"] + 0.03)
            if d1 - d0 > 0.3 and not any(d[0] <= d0 and d1 <= d[1] for d in drops):
                maybes.append([round(d0, 3), round(d1, 3)])
                flags.append({"kind": "restart", "drop": [round(d0, 3), round(d1, 3)],
                              "dropped": " ".join(t[1]["w"].strip() for t in toks[i:hit]),
                              "kept": " ".join(t[1]["w"].strip() for t in toks[hit:hit + 8])})
            i = hit
        else:
            i += 1

    sync_info = None
    if scr:
        if a.sync_offset is not None:
            sync_info = {"offset": a.sync_offset, "by": "hand"}
        elif scr["has_audio"]:
            y = to_wav(a.screen, os.path.join(a.work, "screen16k.wav"), sr)
            sync_info = sync(x, y, sr)
        else:
            sync_info = {"offset": 0.0, "by": "none", "warning": "screen file has no audio: set sync_offset by hand from the clap frame"}

    # sections: split at claps
    dur = len(x) / sr
    marks = [0.0] + [c[1] for c in claps] + [dur]
    sections = []
    for k in range(len(marks) - 1):
        s0, s1 = marks[k], (claps[k][0] if k < len(claps) else dur)
        if not any(s0 <= kp[0] < s1 for kp in keeps): continue
        sections.append({"start": round(s0, 2), "end": round(s1, 2), "layout": "pip" if scr else "cam",
                         "step": "", "title": "", "chapter": ""})
    if sections:
        sections[0]["layout"] = "cam"
        if len(sections) > 2: sections[-1]["layout"] = "cam"
    kept = sum(k[1] - k[0] for k in keeps) - sum(d[1] - d[0] for d in drops)
    plan = {"cam": cam, "screen": scr, "sync": sync_info, "threshold_db": round(float(thr), 1), "noise_db": round(float(noise), 1),
            "speech_db": round(float(loud), 1), "claps": claps, "noise": noise_runs, "keeps": keeps, "drops": drops, "maybe_drops": maybes, "flags": flags,
            "raw_s": round(dur, 2), "kept_s": round(kept, 2)}
    json.dump(plan, open(os.path.join(a.work, "plan.json"), "w"), indent=1)
    cfg = {"name": a.name, "work": a.work, "cam": a.cam, "words": wpath, "fps": min(60, round(cam["fps"])), "size": [1920, 1080],
           "keeps": keeps, "drops": drops, "maybe_drops": maybes, "sections": sections,
           "hook": {"text": "", "look": "V1"}, "phrases": [], "proof": [], "punch": 1.12,
           "pip": {"size": 300, "corner": "br", "margin": 40, "ring": 6, "cx": 0.5, "cy": 0.45, "zoom": 0.9}}
    if scr:
        cfg["screen"] = a.screen; cfg["sync_offset"] = sync_info["offset"]
    json.dump(cfg, open(os.path.join(a.work, f"{a.name}_config.json"), "w"), indent=1)

    L = [f"# Cut plan: {a.name}", "",
         f"Raw {mmss(dur)}, kept {mmss(kept)} ({100 * kept / max(dur, 1e-9):.0f}%), {len(keeps)} speech blocks, "
         f"{len(claps)} claps, {len(noise_runs)} noise blocks dropped, {len(flags)} retakes flagged.",
         f"Levels: noise {noise:.0f} dB, speech {loud:.0f} dB, cut threshold {thr:.0f} dB. Pauses over {a.max_pause} s are cut to {a.pause_keep} s.", ""]
    if sync_info:
        L += ["## Sync", f"screen_time = camera_time + {sync_info['offset']} s. " + json.dumps(sync_info), ""]
        if sync_info.get("warning"): L += ["WARNING: " + sync_info["warning"], ""]
        if abs(sync_info.get("drift_ms", 0)) > 1000 / cam["fps"]:
            L += [f"WARNING: the two recordings drift by {sync_info['drift_ms']} ms from start to end, more than one frame.", ""]
        if sync_info.get("confidence") is not None and (sync_info["confidence"] < 1.2 or (sync_info.get("fine_confidence") or 0) < 8):
            L += ["WARNING: low sync confidence. Check a clap or a click by eye before rendering.", ""]
    L += ["## Retakes (cut by default; delete the line from \"drops\" in the config to keep one)", ""]
    for f in flags:
        if f["kind"] == "retake":
            L += [f"- {mmss(f['drop'][0])} to {mmss(f['drop'][1])}: DROP \"{f['dropped'][:140]}\" | KEEP \"{f['kept'][:140]}\""]
    L += ["", "## Possible restarts (NOT cut; move the pair from \"maybe_drops\" to \"drops\" to cut one)", ""]
    for f in flags:
        if f["kind"] == "restart":
            L += [f"- {mmss(f['drop'][0])} to {mmss(f['drop'][1])}: would drop \"{f['dropped'][:140]}\" | then \"{f['kept'][:140]}\""]
    L += ["", "## Claps (section breaks)", ""] + [f"- {mmss(c[0])}" for c in claps]
    L += ["", "## Speech blocks", ""]
    for u in U:
        tag = " [RETAKE, dropped]" if "retake_of" in u else ""
        L += [f"- {mmss(u['s'])} to {mmss(u['e'])}{tag}: {u['text']}"]
    open(os.path.join(a.work, "plan.md"), "w").write("\n".join(L) + "\n")
    print(f"raw {dur:.1f} s, kept {kept:.1f} s, {len(keeps)} blocks, {len(claps)} claps, {len(flags)} retakes, sync {sync_info}")


if __name__ == "__main__":
    main()

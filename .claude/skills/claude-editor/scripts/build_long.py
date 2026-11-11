#!/usr/bin/env python3
"""Long-form (16:9) render for the claude-editor skill.

    python3 -I scripts/build_long.py config.json

Takes a camera file (with the mic audio), an optional screen recording, a word
list (scripts/words.py) and a config written from plan_long.py's starter. Makes
<work>/<name>_master.mp4 (1920x1080 H.264 High, bt709, -14 LUFS), a 720p
preview, chapters.txt, timeline.json and cut_words.json.

Rules built in (Slite "Rules and lessons learned" pNd6jkZP4XtKih):
- The screen recording is never cropped, enlarged, blurred or dimmed. It is
  only scaled down to fit and padded.
- Punch-ins happen on camera cuts only (R-107), never on screen footage.
- Cuts get 30 ms audio fades; loudness is two-pass to -14 LUFS (R-105).
- No music or sound effects are added.
Style notes: styles/long-form-tutorial.md.
"""
import json, math, os, re, subprocess, sys, wave
import numpy as np

SR = 48000
FADE = 0.03


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.exit("ffmpeg failed:\n" + " ".join(map(str, cmd))[:600] + "\n" + r.stderr[-3000:])
    return r


def graph_opt(graph):
    """ffmpeg 7 and later read a filter graph file with -/filter_complex; older builds only know -filter_complex_script,
    which the 2026 nightlies removed. Ask the installed ffmpeg which one it has."""
    try:
        h = subprocess.run(["ffmpeg", "-hide_banner", "-h", "full"], capture_output=True, text=True).stdout
    except Exception:
        h = ""
    return ["-filter_complex_script", graph] if "filter_complex_script" in h else ["-/filter_complex", graph]


def probe(path):
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", path])
    j = json.loads(r.stdout)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    info = {"duration": float(j["format"]["duration"]), "has_audio": a is not None}
    if v:
        w, h = int(v["width"]), int(v["height"])
        rot = 0
        for sd in v.get("side_data_list", []):
            rot = int(sd.get("rotation", rot) or rot)
        rot = int(v.get("tags", {}).get("rotate", rot) or rot)
        if abs(rot) in (90, 270):
            w, h = h, w
        n, d = v.get("avg_frame_rate", "30/1").split("/")
        info.update(w=w, h=h, fps=float(n) / float(d or 1) if float(d or 1) else 30.0)
    return info


def ass_ts(t):
    t = max(0.0, t)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def ass_escape(s):
    return s.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", "\\N")


def merge_windows(wins, eps=1e-6):
    out = []
    for a, b in sorted(wins):
        if out and a <= out[-1][1] + eps:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def enable_expr(wins, fps):
    """ffmpeg enable expression for output-time windows, safe at frame edges."""
    e = 0.5 / fps
    wins = merge_windows(wins)
    if not wins:
        return "0"
    return "+".join(f"between(t,{a - e:.4f},{b - e - 1e-4:.4f})" for a, b in wins)


def subtract(keeps, drops):
    out = []
    for a, b in keeps:
        parts = [(a, b)]
        for d0, d1 in drops:
            nxt = []
            for p0, p1 in parts:
                if d1 <= p0 or d0 >= p1:
                    nxt.append((p0, p1))
                else:
                    if d0 > p0: nxt.append((p0, d0))
                    if d1 < p1: nxt.append((d1, p1))
            parts = nxt
        out += parts
    return out


def build_segments(cfg, fps):
    """Kept camera-time ranges, in section order, snapped to the frame grid."""
    keeps = [tuple(k) for k in cfg["keeps"]]
    drops = [tuple(d) for d in cfg.get("drops", [])]
    keeps = subtract(keeps, drops)
    min_len = cfg.get("min_segment", 0.2)
    segs = []
    for si, sec in enumerate(cfg["sections"]):
        for a, b in sorted(keeps):
            a2, b2 = max(a, sec["start"]), min(b, sec["end"])
            na, nb = round(a2 * fps), round(b2 * fps)
            if (nb - na) / fps < min_len:
                continue
            if segs and segs[-1]["sec"] == si and segs[-1]["nb"] >= na:
                segs[-1]["nb"] = max(segs[-1]["nb"], nb)      # touching ranges are one shot
                continue
            segs.append({"sec": si, "na": na, "nb": nb, "layout": sec.get("layout", "pip")})
    if not segs:
        sys.exit("No segments: check keeps and sections in the config.")
    off = 0
    for s in segs:
        s["a"], s["b"] = s["na"] / fps, s["nb"] / fps
        s["out_a"] = off / fps
        off += s["nb"] - s["na"]
        s["out_b"] = off / fps
    return segs, off / fps


def src_to_out(t, segs):
    """Camera time -> output time on the main timeline (None if it was cut)."""
    for s in segs:
        if s["a"] - 1e-6 <= t < s["b"]:
            return s["out_a"] + (t - s["a"])
    return None


def find_words(words, phrase, after=0.0, nth=1):
    """Camera time where a spoken phrase starts (words.py list), or None."""
    norm = lambda w: re.sub(r"[^a-z0-9$%]", "", w.lower())
    want = [norm(w) for w in phrase.split() if norm(w)]
    toks = [(norm(w["w"]), w) for w in words]
    toks = [(n, w) for n, w in toks if n]
    hit = 0
    for i in range(len(toks) - len(want) + 1):
        if toks[i][1]["s"] < after:
            continue
        if all(toks[i + k][0] == want[k] for k in range(len(want))):
            hit += 1
            if hit == nth:
                return toks[i][1]["s"], toks[i + len(want) - 1][1]["e"]
    return None


def event_time(ev, words, segs, what):
    if "at" in ev:
        span = (ev["at"], ev["at"])
    else:
        span = find_words(words, ev["find"], ev.get("after", 0.0), ev.get("nth", 1))
        if span is None:
            sys.exit(f"{what}: the words \"{ev['find']}\" are not in the transcript (after {ev.get('after', 0)} s).")
    t = src_to_out(span[0] + ev.get("delay", 0.0), segs)
    if t is None:
        sys.exit(f"{what}: camera time {span[0]:.2f} s was cut, so there is nowhere to show it.")
    return t, span


def layout_at(t_out, segs):
    for s in segs:
        if s["out_a"] - 1e-6 <= t_out < s["out_b"]:
            return s["layout"]
    return segs[-1]["layout"]


# ---------------------------------------------------------------- audio
def read_audio(path, work, tag):
    raw = os.path.join(work, f"{tag}.f32")
    run(["ffmpeg", "-hide_banner", "-y", "-i", path, "-vn", "-ac", "2", "-ar", str(SR),
         "-af", "aresample=async=1:first_pts=0", "-f", "f32le", raw])
    return np.memmap(raw, dtype=np.float32, mode="r").reshape(-1, 2)


def cut_audio(src, segs, tail, lead):
    """Join the kept ranges with 30 ms fades; lead is cold-open audio or silence."""
    nf = int(FADE * SR)
    ramp = np.linspace(0.0, 1.0, nf, dtype=np.float32)[:, None]
    parts = [lead] if lead is not None and len(lead) else []
    for s in segs:
        i0, i1 = int(round(s["a"] * SR)), int(round(s["b"] * SR))
        x = np.zeros((i1 - i0, 2), dtype=np.float32)
        got = src[max(0, i0):min(len(src), i1)]
        x[:len(got)] = got
        if len(x) > 2 * nf:
            x[:nf] *= ramp
            x[-nf:] *= ramp[::-1]
        parts.append(x)
    parts.append(np.zeros((int(tail * SR), 2), dtype=np.float32))
    return np.concatenate(parts)


def write_wav(path, x):
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def loudnorm(inp, outp, target=-14.0, tp=-1.5):
    f1 = f"loudnorm=I={target}:TP={tp}:LRA=11:print_format=json"
    r = run(["ffmpeg", "-hide_banner", "-y", "-i", inp, "-af", f1, "-f", "null", "-"])
    m = json.loads(re.findall(r"\{[^{}]*\}", r.stderr)[-1])
    f2 = (f"loudnorm=I={target}:TP={tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,"
          f"aresample={SR}")
    run(["ffmpeg", "-hide_banner", "-y", "-i", inp, "-af", f2, "-c:a", "pcm_s16le", outp])
    return m


# ---------------------------------------------------------------- text (ASS)
HOOK_LOOKS = {  # Brian Mark looks from styles/hook-titles.md, sized for 1920x1080
    "V1": ("Montserrat ExtraBold", 50, "&H00000000", "&H00FFFFFF", "&H00FFFFFF", 3, 14, 0),
    "V2": ("Montserrat ExtraBold", 58, "&H00FFFFFF", "&H00000000", "&H80000000", 1, 0, 4),
    "V3": ("Montserrat ExtraBold", 62, "&H00FFFFFF", "&H00000000", "&H00000000", 1, 6, 0),
}


def build_ass(cfg, segs, words, total, fps, W, H):
    accent = cfg.get("accent", "&H0000D4FF")          # BG yellow, ASS BGR
    serif = cfg.get("serif_font", "Playfair Display")
    sans = cfg.get("sans_font", "Montserrat ExtraBold")
    psize = cfg.get("phrase_size", 60)
    events, report = [], {"phrases": [], "steps": [], "hook": None}
    styles = [
        f"Style: PhraseCam,{serif},{psize},&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,0,-1,0,0,100,100,0,0,1,0,3,7,90,90,80,1",
        f"Style: PhraseScr,{serif},{psize},&H00FFFFFF,&H00FFFFFF,&H30101010,&H30101010,0,-1,0,0,100,100,0,0,3,14,0,7,90,90,80,1",
        f"Style: Step,{sans},34,&H00FFFFFF,&H00FFFFFF,&H10101010,&H10101010,0,0,0,0,100,100,1,0,3,16,0,7,70,70,60,1",
        f"Style: Cap,{sans},52,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,5,2,2,160,160,70,1",
    ]
    # hook title on the opening shot
    hook = cfg.get("hook")
    if hook and hook.get("text"):
        look = hook.get("look", "V1")
        fn, fs, pc, oc, bc, bs, ol, sh = HOOK_LOOKS[look]
        styles.append(f"Style: Hook,{fn},{hook.get('size', fs)},{pc},{pc},{oc},{bc},-1,0,0,0,100,100,0,0,{bs},{ol},{sh},8,200,200,{hook.get('margin_v', 70)},1")
        end = hook.get("end", segs[0]["out_b"])
        txt = re.sub(r"\*([^*]+)\*", r"{\\c&H0000D4FF&}\1{\\c}", ass_escape(hook["text"]))
        if hook.get("sub"):
            txt += "\\N{\\fs" + str(int(fs * 0.62)) + "}" + ass_escape(hook["sub"])
        events.append((1, 0.0, min(end, total), "Hook", txt))
        report["hook"] = {"text": hook["text"], "start": 0.0, "end": round(min(end, total), 2)}
    # step cards at the start of each section that has one
    step_hold = cfg.get("step_hold", 3.5)
    seen = set()
    for s in segs:
        sec = cfg["sections"][s["sec"]]
        if s["sec"] in seen or not (sec.get("step") or sec.get("title")):
            seen.add(s["sec"]); continue
        seen.add(s["sec"])
        t0 = s["out_a"] + cfg.get("step_delay", 0.3)
        top = "{\\c" + accent + "&}" + ass_escape(sec.get("step", "").upper()) + "{\\c&HFFFFFF&}" if sec.get("step") else ""
        ttl = ass_escape(sec.get("title", ""))
        txt = top + ("\\N" if top and ttl else "") + ("{\\fs46}" + ttl if ttl else "")
        events.append((2, t0, min(t0 + step_hold, total), "Step", "{\\fad(150,150)}" + txt))
        report["steps"].append({"text": (sec.get("step", "") + " " + sec.get("title", "")).strip(), "start": round(t0, 2)})
    # key phrases that type on
    cps = cfg.get("type_cps", 28)
    for i, ph in enumerate(cfg.get("phrases", [])):
        t0, span = event_time(ph, words, segs, f"phrase {i + 1}")
        text = ph.get("text") or ph["find"]
        hold = ph.get("hold", 2.2)
        style = "PhraseCam" if layout_at(t0, segs) == "cam" else "PhraseScr"
        pos = {"tl": "{\\an7}", "c": "{\\an5}", "tr": "{\\an9}", "bl": "{\\an1}"}[ph.get("pos", "tl")]
        dt = 1.0 / cps
        for k in range(1, len(text) + 1):
            a = t0 + (k - 1) * dt
            b = t0 + k * dt if k < len(text) else t0 + len(text) * dt + hold
            shown, rest = ass_escape(text[:k]), ass_escape(text[k:])
            events.append((3, a, min(b, total), style, pos + shown + ("{\\alpha&HFF&}" + rest if rest else "")))
        report["phrases"].append({"text": text, "start": round(t0, 2), "end": round(t0 + len(text) * dt + hold, 2),
                                  "src": round(span[0], 2), "approved": bool(ph.get("approved"))})
    # optional running captions (off by default: the reference style has none on long-form)
    if cfg.get("captions"):
        cw = remap_words(words, segs)
        g = []
        groups = []
        for x in cw:
            if g and x["seg"] != g[-1]["seg"]:
                groups.append(g); g = []
            g.append(x)
            if len(g) == cfg.get("cap_group", 4) or x["w"].rstrip()[-1:] in ".?!":
                groups.append(g); g = []
        if g: groups.append(g)
        for i, g in enumerate(groups):
            st = g[0]["s"]; en = groups[i + 1][0]["s"] if i + 1 < len(groups) else total
            if en - g[-1]["e"] > 0.6: en = g[-1]["e"] + 0.3
            events.append((0, st, en, "Cap", ass_escape(" ".join(x["w"] for x in g))))
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
""" + "\n".join(styles) + """

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    body = "".join(f"Dialogue: {ly},{ass_ts(a)},{ass_ts(b)},{st},,0,0,0,,{tx}\n" for ly, a, b, st, tx in events if b > a)
    return head + body, report


def remap_words(words, segs):
    out = []
    for si, s in enumerate(segs):
        for x in words:
            mid = (x["s"] + x["e"]) / 2
            if s["a"] <= mid < s["b"]:
                out.append({"w": x["w"].strip(), "s": round(max(x["s"], s["a"]) - s["a"] + s["out_a"], 3),
                            "e": round(min(x["e"], s["b"]) - s["a"] + s["out_a"], 3), "seg": si})
    return out


# ---------------------------------------------------------------- video graph
def make_mask(work, D, ring):
    """Circle alpha mask and a ring PNG for the camera circle."""
    from PIL import Image, ImageDraw
    S = 4
    m = Image.new("L", (D * S, D * S), 0)
    ImageDraw.Draw(m).ellipse([S, S, D * S - S, D * S - S], fill=255)
    m = m.resize((D, D), Image.LANCZOS)
    m.save(os.path.join(work, "pip_mask.png"))
    R = D + 2 * ring
    r = Image.new("RGBA", (R * S, R * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(r)
    d.ellipse([0, 0, R * S - 1, R * S - 1], fill=(255, 255, 255, 255))
    d.ellipse([ring * S, ring * S, (R - ring) * S - 1, (R - ring) * S - 1], fill=(0, 0, 0, 0))
    r = r.resize((R, R), Image.LANCZOS)
    r.save(os.path.join(work, "pip_ring.png"))


def main():
    cfg = json.load(open(sys.argv[1]))
    work = cfg["work"]; os.makedirs(work, exist_ok=True)
    name = cfg["name"]
    W, H = cfg.get("size", [1920, 1080])
    cam = probe(cfg["cam"])
    scr = probe(cfg["screen"]) if cfg.get("screen") else None
    fps = int(cfg.get("fps") or min(60, round(cam["fps"])))
    words = json.load(open(cfg["words"])) if cfg.get("words") else []
    if cam["w"] < W or cam["h"] < H:
        if not cfg.get("allow_cam_upscale"):
            sys.exit(f"Camera is {cam['w']}x{cam['h']}, smaller than {W}x{H}. Never upscale: lower \"size\" or set allow_cam_upscale.")
    if not scr:
        for sec in cfg["sections"]:
            sec["layout"] = "cam"
    segs, main_total = build_segments(cfg, fps)
    tail = cfg.get("tail", 0.3)
    co = cfg.get("cold_open")
    co_dur = 0.0
    if co:
        co_file = {"cam": cfg["cam"], "screen": cfg.get("screen")}.get(co["file"], co["file"])
        co_dur = round((co["end"] - co["start"]) * fps) / fps
    total = co_dur + main_total + tail
    off = cfg.get("sync_offset", 0.0)       # screen_time = camera_time + sync_offset
    offn = round(off * fps)

    # ---- audio
    src = read_audio(cfg["cam"], work, "cam_audio")
    lead = None
    if co:
        if co.get("audio"):
            a = read_audio(co_file, work, "cold_audio")
            lead = np.array(a[int(co["start"] * SR):int(co["start"] * SR) + int(co_dur * SR)])
            nf = int(FADE * SR)
            if len(lead) > 2 * nf:
                r = np.linspace(0, 1, nf, dtype=np.float32)[:, None]
                lead[:nf] *= r; lead[-nf:] *= r[::-1]
        if lead is None or len(lead) < int(co_dur * SR):
            pad = np.zeros((int(co_dur * SR) - (len(lead) if lead is not None else 0), 2), dtype=np.float32)
            lead = pad if lead is None else np.concatenate([lead, pad])
    mix = cut_audio(src, segs, tail, lead)
    write_wav(os.path.join(work, "cut_audio.wav"), mix)
    meas = loudnorm(os.path.join(work, "cut_audio.wav"), os.path.join(work, "cut_audio_norm.wav"),
                    cfg.get("lufs", -14.0), cfg.get("true_peak", -1.5))

    # ---- text
    ass, text_report = build_ass(cfg, segs, words, main_total, fps, W, H)
    ass_path = os.path.join(work, "long.ass")
    open(ass_path, "w").write(ass)
    fonts = os.path.expanduser(cfg.get("fonts_dir", "~/.fonts"))

    # ---- video graph
    def sel(shift=0):
        return "+".join(f"between(n,{s['na'] + shift},{s['nb'] + shift - 1})" for s in segs)

    inputs = ["-i", cfg["cam"]]
    fc = []
    need = ["full"]
    pipc = cfg.get("pip", {})
    D = int(pipc.get("size", 300)); ring = int(pipc.get("ring", 6)); margin = int(pipc.get("margin", 40))
    has_pip = scr and any(s["layout"] == "pip" for s in segs)
    punch = float(cfg.get("punch", 1.12))
    cam_segs = [s for s in segs if s["layout"] == "cam"]
    # Framing levels. One camera, so variety comes from punch-ins: every shot takes the next level in the pattern.
    # A "shot" is a kept range, or a piece of a long one split at a sentence end ("max_shot" seconds, 0 = off).
    levels = [float(x) for x in (cfg.get("punch_levels") or ([1.0, punch] if punch > 1.001 else [1.0]))]
    if (cam["w"] / max(levels) < W * 0.74 or cam["h"] / max(levels) < H * 0.74) and not cfg.get("allow_punch_upscale", True):
        levels = [1.0]
    pattern = cfg.get("punch_pattern") or ([0, 1, 0, 2] if len(levels) > 2 else [0, 1])
    max_shot = float(cfg.get("max_shot", 0)); min_shot = float(cfg.get("min_shot", 2.5))
    ends = []                                            # output times where a sentence ends inside a kept range
    for i in range(len(words) - 1):
        w, nx = words[i], words[i + 1]
        if w["w"].rstrip()[-1:] in ".?!":
            t = src_to_out((w["e"] + nx["s"]) / 2, segs)
            if t is not None: ends.append(t)
    def split_shot(a, b):
        if not max_shot or b - a <= max_shot:
            return [[a, b]]
        c = [t for t in ends if a + min_shot <= t <= b - min_shot]
        if not c:
            return [[a, b]]
        m = min(c, key=lambda t: abs(t - (a + min(max_shot * 0.75, (b - a) / 2))))
        m = round(m * fps) / fps
        return split_shot(a, m) + split_shot(m, b)
    shots, lvl_wins, k, prev_sec = [], {i: [] for i in range(len(levels))}, 0, None
    # "level_hold": a cut that comes sooner than this after the last framing change keeps the framing (a plain jump
    # cut), so tightened pauses do not make the picture flicker between sizes. 0 = change framing on every cut.
    hold = float(cfg.get("level_hold", 0)); li = None; since = 0.0
    for sg in cam_segs:
        for a, b in split_shot(sg["out_a"], sg["out_b"]):
            new_sec = sg["sec"] != prev_sec
            if new_sec:
                k, prev_sec = 0, sg["sec"]
            if li is None or new_sec or not hold or a - since >= hold - 1e-6:
                li = pattern[k % len(pattern)] % len(levels); k += 1; since = a
                shots.append({"a": round(a, 3), "b": round(b, 3), "level": levels[li]})
                lvl_wins[li].append([a, b])
            else:
                shots[-1]["b"] = round(b, 3); lvl_wins[li][-1][1] = b
    for sg in cam_segs: sg["punch"] = False
    used = [i for i in range(len(levels)) if levels[i] > 1.001 and lvl_wins[i]]
    # side panels: he is moved to the left and a graphic sits on the right while he keeps talking
    side_cfg = cfg.get("side", {})
    PX = int(side_cfg.get("x", 1080)); SH = int(side_cfg.get("shift", 340))
    has_side = any(c.get("mode") == "side" for c in cfg.get("cards", []))
    n_split = 1 + len(used) + (1 if has_pip else 0) + (1 if has_side else 0)
    fc.append(f"[0:v]fps={fps}:start_time=0,select='{sel()}',setpts=N/({fps}*TB)" +
              (f",split={n_split}" + "".join(f"[c{i}]" for i in range(n_split)) if n_split > 1 else "[c0]"))
    fc.append(f"[c0]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[camfull]")
    ci = 1
    pcy = float(cfg.get("punch_cy", 0.5))                # 0 = keep the top edge, 0.5 = centred
    punch_layers = []
    for li in used:
        pz = levels[li]
        fc.append(f"[c{ci}]crop=iw/{pz}:ih/{pz}:(iw-iw/{pz})/2:(ih-ih/{pz})*{pcy},scale={W}:{H}:force_original_aspect_ratio=increase,"
                  f"crop={W}:{H},setsar=1[campunch{li}]")
        punch_layers.append((f"campunch{li}", lvl_wins[li])); ci += 1
    if has_side:
        fc.append(f"[c{ci}]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},crop={W - SH}:{H}:{SH}:0,"
                  f"pad={W}:{H}:0:0:color=0x0B0B0F,setsar=1[camshift]")
        ci += 1
    punched = [w for _, wins in punch_layers for w in wins]
    idx = 1
    if scr:
        inputs += ["-i", cfg["screen"]]
        s_idx = idx; idx += 1
        lo = min(s["na"] + offn for s in segs); hi = max(s["nb"] + offn for s in segs)
        pre = max(0, -lo)
        post = max(0, hi - int(scr["duration"] * fps)) + fps
        pad = f"tpad=start={pre}:start_mode=clone:stop={post}:stop_mode=clone," if (pre or post > fps) else ""
        fc.append(f"[{s_idx}:v]fps={fps}:start_time=0,{pad}select='{sel(offn + pre)}',setpts=N/({fps}*TB),"
                  f"scale='min({W},iw)':'min({H},ih)':force_original_aspect_ratio=decrease,"
                  f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x0B0B0F,setsar=1[base0]")
        last = "base0"
        if has_pip:
            make_mask(work, D, ring)
            inputs += ["-loop", "1", "-framerate", str(fps), "-i", os.path.join(work, "pip_mask.png"),
                       "-loop", "1", "-framerate", str(fps), "-i", os.path.join(work, "pip_ring.png")]
            m_idx, r_idx = idx, idx + 1; idx += 2
            cx = float(pipc.get("cx", 0.5)); cy = float(pipc.get("cy", 0.45)); zoom = float(pipc.get("zoom", 0.9))
            side = f"min(iw,ih)*{zoom}"
            fc.append(f"[c{ci}]crop='{side}':'{side}':'clip(iw*{cx}-{side}/2,0,iw-{side})':'clip(ih*{cy}-{side}/2,0,ih-{side})',"
                      f"scale={D}:{D},format=yuva420p[pipsq];[{m_idx}:v]format=gray,scale={D}:{D}[pmask];"
                      f"[pipsq][pmask]alphamerge[pipc]")
            pos = {"br": (W - D - margin, H - D - margin), "bl": (margin, H - D - margin),
                   "tr": (W - D - margin, margin), "tl": (margin, margin)}
            by_corner = {}
            for s in segs:
                if s["layout"] == "pip":
                    c = cfg["sections"][s["sec"]].get("pip_corner", pipc.get("corner", "br"))
                    by_corner.setdefault(c, []).append([s["out_a"], s["out_b"]])
            corners = list(by_corner)
            if len(corners) > 1:
                fc.append("[pipc]split=" + str(len(corners)) + "".join(f"[pipc{i}]" for i in range(len(corners))))
                fc.append(f"[{r_idx}:v]format=rgba,split=" + str(len(corners)) + "".join(f"[ring{i}]" for i in range(len(corners))))
            for i, c in enumerate(corners):
                x, y = pos[c]; en = enable_expr(by_corner[c], fps)
                ring_in = f"ring{i}" if len(corners) > 1 else f"{r_idx}:v"
                pip_in = f"pipc{i}" if len(corners) > 1 else "pipc"
                fc.append(f"[{last}][{ring_in}]overlay={x - ring}:{y - ring}:enable='{en}':shortest=0:eof_action=pass[r{i}];"
                          f"[r{i}][{pip_in}]overlay={x}:{y}:enable='{en}':eof_action=pass[p{i}]")
                last = f"p{i}"
        cam_wins = [[s["out_a"], s["out_b"]] for s in cam_segs]
        fc.append(f"[{last}][camfull]overlay=0:0:enable='{enable_expr(cam_wins, fps)}':eof_action=pass[k0]")
        last = "k0"
    else:
        last = "camfull"
    for pi_, (lab, wins) in enumerate(punch_layers):
        fc.append(f"[{last}][{lab}]overlay=0:0:enable='{enable_expr(wins, fps)}':eof_action=pass[kp{pi_}]")
        last = f"kp{pi_}"

    # proof images: quick flashes, then one held, on a solid card
    proof_report = []
    max_up = float(cfg.get("proof_max_upscale", 1.0))
    for pi, pr in enumerate(cfg.get("proof", [])):
        t0, _ = event_time(pr, words, segs, f"proof {pi + 1}")
        flash = pr.get("flash", 0.4); hold = pr.get("hold", 3.0)
        imgs = pr["images"]; t = t0
        fc.append(f"[{last}]drawbox=x=0:y=0:w={W}:h={H}:color=0x0B0B0F:t=fill:enable='"
                  f"{enable_expr([[t0, t0 + flash * (len(imgs) - 1) + hold]], fps)}'[pb{pi}]")
        last = f"pb{pi}"
        for ii, img in enumerate(imgs):
            d = hold if ii == len(imgs) - 1 else flash
            from PIL import Image
            iw, ih = Image.open(img).size
            sc = min(W * 0.9 / iw, H * 0.86 / ih, max_up)
            tw, th = int(iw * sc) // 2 * 2, int(ih * sc) // 2 * 2
            # one decoded frame, repeated in the graph: a looped image input re-decodes the file on every frame,
            # which is what made long videos with many proof images slow
            inputs += ["-framerate", str(fps), "-i", img]
            fc.append(f"[{idx}:v]scale={tw}:{th},format=yuva420p,loop=loop=-1:size=1,setpts=N/({fps}*TB)[pi{pi}_{ii}];"
                      f"[{last}][pi{pi}_{ii}]overlay=(W-w)/2:(H-h)/2:"
                      f"enable='{enable_expr([[t, t + d]], fps)}':eof_action=pass[po{pi}_{ii}]")
            last = f"po{pi}_{ii}"; idx += 1
            proof_report.append({"image": os.path.basename(img), "start": round(t, 2), "dur": d,
                                 "scale": round(sc, 3), "small": bool(tw < W * 0.5 and th < H * 0.5)})
            t += d
    esc = lambda p: p.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    fc.append(f"[{last}]subtitles='{esc(ass_path)}':fontsdir='{esc(fonts)}'[txt]")
    last = "txt"
    # full-frame cards (lists, big numbers, proof on a designed card): opaque WxH images that cut in over
    # everything while he keeps talking. All cards ride on ONE extra input, so 50 cards cost the same as 1.
    card_report = []
    fwd = lambda p: os.path.abspath(p).replace("\\", "/")

    def card_track(items, tag):
        """One concat input for a list of (t0, dur, image). Returns (label index, windows)."""
        nonlocal idx
        from PIL import Image
        blank = os.path.join(work, "card_blank.png")
        if not os.path.exists(blank):
            Image.new("RGB", (W, H), (11, 11, 15)).save(blank)
        lines, cur, wins = ["ffconcat version 1.0"], 0.0, []
        for i, (t0, d, img, pop) in enumerate(items):
            t0 = max(round(t0 * fps) / fps, cur)                  # never overlap the previous card
            nxt = items[i + 1][0] if i + 1 < len(items) else main_total
            d = max(2 / fps, min(d, nxt - t0, main_total - t0))
            d = round(d * fps) / fps
            if t0 - cur > 1e-6:
                lines += [f"file '{fwd(blank)}'", f"duration {t0 - cur:.6f}"]
            # pop-in: two lead frames (smaller and fainter), 2 video frames each, then the card itself
            lead = 0.0
            base = os.path.splitext(img)[0]
            pops = [base + ".pop1.png", base + ".pop2.png"]
            if pop and all(os.path.exists(x) for x in pops) and d > 12 / fps:
                for x in pops:
                    lines += [f"file '{fwd(x)}'", f"duration {2 / fps:.6f}"]; lead += 2 / fps
            lines += [f"file '{fwd(img)}'", f"duration {d - lead:.6f}"]
            wins.append([t0, t0 + d]); cur = t0 + d
            card_report.append({"image": os.path.basename(img), "start": round(t0, 2), "dur": round(d, 2), "mode": tag})
        lines += [f"file '{fwd(blank)}'", f"duration {max(main_total - cur, 1 / fps) + 1:.6f}", f"file '{fwd(blank)}'"]
        cl = os.path.join(work, f"cards_{tag}.ffconcat")
        open(cl, "w").write("\n".join(lines) + "\n")
        inputs.extend(["-f", "concat", "-safe", "0", "-i", cl])
        idx += 1
        return idx - 1, wins

    full_items, side_items = [], []
    for ci_, cd in enumerate(cfg.get("cards", [])):
        t0, _ = event_time(cd, words, segs, f"card {ci_ + 1}")
        img = cd["image"] if os.path.isabs(cd["image"]) else os.path.join(cfg.get("cards_dir", ""), cd["image"])
        if not os.path.exists(img):
            sys.exit(f"card {ci_ + 1}: image not found: {img}")
        (side_items if cd.get("mode") == "side" else full_items).append(
            (t0, float(cd.get("dur", 3.0)), img, cd.get("pop", True)))
    full_items.sort(); side_items.sort()
    side_wins = []
    if side_items:
        # the panel goes under the text layer's full cards but over the camera; the camera is shifted for the same windows
        si, side_wins = card_track(side_items, "side")
        fc.append(f"[{last}][camshift]overlay=0:0:enable='{enable_expr(side_wins, fps)}':eof_action=pass[shf];"
                  f"[{si}:v]fps={fps},scale={W}:{H},crop={W - PX}:{H}:{PX}:0,format=yuv420p,setsar=1,setpts=N/({fps}*TB)[sidetrack];"
                  f"[shf][sidetrack]overlay={PX}:0:enable='{enable_expr(side_wins, fps)}':eof_action=pass[sdo]")
        last = "sdo"
    if full_items:
        fi, wins = card_track(full_items, "full")
        fc.append(f"[{fi}:v]fps={fps},scale={W}:{H},format=yuv420p,setsar=1,setpts=N/({fps}*TB)[cardtrack];"
                  f"[{last}][cardtrack]overlay=0:0:enable='{enable_expr(wins, fps)}':eof_action=pass[crd]")
        last = "crd"
    card_report.sort(key=lambda c: c["start"])
    if co:
        inputs += ["-ss", f"{co['start']:.3f}", "-t", f"{co_dur:.3f}", "-i", co_file]
        fc.append(f"[{idx}:v]fps={fps},scale='min({W},iw)':'min({H},ih)':force_original_aspect_ratio=decrease,"
                  f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x0B0B0F,setsar=1,setpts=PTS-STARTPTS[cold];"
                  f"[{last}]setpts=PTS-STARTPTS[mainv];[cold][mainv]concat=n=2:v=1:a=0[joined]")
        last = "joined"; idx += 1
    fc.append(f"[{last}]tpad=stop_mode=clone:stop_duration={tail},trim=duration={total:.4f},format=yuv420p,"
              f"setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709[vo]")
    graph = os.path.join(work, "graph.txt")
    open(graph, "w").write(";\n".join(fc))
    master = os.path.join(work, f"{name}_master.mp4")
    a_idx = idx
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + inputs + ["-i", os.path.join(work, "cut_audio_norm.wav"),
           *graph_opt(graph), "-map", "[vo]", "-map", f"{a_idx}:a",
           "-c:v", "libx264", "-profile:v", "high", "-crf", str(cfg.get("crf", 16)), "-preset", cfg.get("preset", "medium"),
           "-r", str(fps), "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:a", "aac", "-b:a", "256k", "-t", f"{total:.4f}", "-movflags", "+faststart", master]
    run(cmd)
    if cfg.get("preview", True):
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", master, "-vf", "scale=-2:720", "-c:v", "libx264",
             "-crf", "27", "-preset", "veryfast", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
             os.path.join(work, f"{name}_preview.mp4")])

    # ---- chapters (YouTube: first at 0:00, each at least 10 s)
    chapters, seen = [], set()
    for s in segs:
        sec = cfg["sections"][s["sec"]]
        if s["sec"] in seen: continue
        seen.add(s["sec"])
        if sec.get("chapter"):
            chapters.append([0.0 if not chapters else s["out_a"] + co_dur, sec["chapter"]])
    ch = [c for i, c in enumerate(chapters) if i == 0 or c[0] - chapters[i - 1][0] >= 10]
    def yt(t):
        t = int(t); return f"{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}" if t >= 3600 else f"{t // 60}:{t % 60:02d}"
    open(os.path.join(work, "chapters.txt"), "w").write("".join(f"{yt(t)} {n}\n" for t, n in ch))

    cw = remap_words(words, segs)
    for x in cw: x["s"] = round(x["s"] + co_dur, 3); x["e"] = round(x["e"] + co_dur, 3)
    json.dump(cw, open(os.path.join(work, "cut_words.json"), "w"), indent=0)
    json.dump({"name": name, "fps": fps, "size": [W, H], "total": round(total, 3), "cold_open": co_dur, "tail": tail,
               "sync_offset": off, "segments": segs, "text": text_report, "proof": proof_report, "cards": card_report, "shots": shots, "chapters": ch,
               "loudnorm_input": meas, "cam": cam, "screen": scr, "config": os.path.abspath(sys.argv[1])},
              open(os.path.join(work, "timeline.json"), "w"), indent=1)
    cuts = len(segs) - 1
    print(f"total {total:.2f} s, {len(segs)} shots, {cuts} cuts, {cuts / max(total / 60, 1e-9):.1f} cuts/min -> {master}")


if __name__ == "__main__":
    main()

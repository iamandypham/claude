#!/usr/bin/env python3
"""Render a 1080x1920 reel from a plan.json: layout, hook text, word captions, CTA, loudness.

Usage: render.py <plan.json> <out.mp4> [--ass-only out.ass]

plan.json (see examples/plan-*.json):
{
  "layout": "full" | "stack" | "card",
  "main": "talk.mp4",              # video with the voice (full / stack)
  "words": "words.json",           # from transcribe.py or tighten.py (optional for card)
  "focus_x": 0.5,                   # full: horizontal crop centre 0-1
  "stack": {"split": 0.33,          # top panel height as share of 1920
            "top": {"src": "main", "rect": [x, y, w, h]},      # rect in source pixels, optional
            "bottom": {"src": "main" | "chart.mp4",  # a separate file is NOT tightened "rect": [x, y, w, h]}},
  "card": {"seconds": 8, "bg": "000000", "lines": ["..."], "header": "Name  @handle"},
  "hook": {"text": "Your hook line here", "style": "plain" | "box" | "bold", "y": 0.33,
           "end": 3.0, "size": 0.03, "font": "Inter"},  # font defaults to the caption font
  "captions": {"mode": "word" | "phrase", "max_words": 3, "y": 0.33, "size": 0.035,
               "font": "Inter", "bold": true, "upper": true,
               "color": "FFFFFF", "accent": "FFE14D" | null, "negative": "FF4D4D",
               "pop": false,                # small scale-in per caption (face format only)
               "keywords": ["liquidity"], "negative_words": ["loss", "lose"],
               "after_hook": true},
  "cta": {"text": "Comment \\"GUIDE\\"", "seconds": 3.0, "y": 0.42, "style": "box"},
  "loudness_lufs": -14
}
Colours are RRGGBB hex. Positions and sizes are shares of the 1920 height (y 0 = top; size = font size).
Pick colours from the client's own brand or the format reference, never from another brand.
"""
import argparse, json, os, re, subprocess, sys, tempfile

W, H = 1080, 1920


def probe(path, entries="format=duration"):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", entries, "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout.strip()
    return out


def has_audio(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                          "stream=index", "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return bool(out.strip())


def ass_color(hexrgb, alpha="00"):
    h = hexrgb.lstrip("#")
    return f"&H{alpha}{h[4:6]}{h[2:4]}{h[0:2]}".upper()


def ts(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def esc(text):
    return text.replace("\\", "/").replace("{", "(").replace("}", ")").replace("\n", "\\N")


def build_ass(plan, dur):
    cap = plan.get("captions") or {}
    hook = plan.get("hook") or {}
    cta = plan.get("cta") or {}
    font = cap.get("font", "Inter")
    csize = int(H * cap.get("size", 0.035))  # font size as a share of the 1920 height
    hsize = int(H * hook.get("size", 0.03))
    hfont = hook.get("font", font)  # some stack creators use a serif hook title over sans captions
    bold = -1 if cap.get("bold", True) else 0
    white = ass_color(cap.get("color", "FFFFFF"))
    black = ass_color("000000")
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},{csize},{white},{white},{black},{ass_color('000000','80')},{bold},0,0,0,100,100,0,0,1,{max(3, csize // 12)},0,5,60,60,0,1
Style: HookBox,{hfont},{hsize},{ass_color(hook.get('color', 'FFFFFF'))},{white},{ass_color(hook.get('box', '000000'))},{ass_color(hook.get('box', '000000'))},-1,0,0,0,100,100,0,0,3,{max(8, hsize // 4)},0,5,80,80,0,1
Style: HookPlain,{hfont},{hsize},{ass_color(hook.get('color', 'FFFFFF'))},{white},{ass_color('000000','60')},{ass_color('000000','40')},-1,0,0,0,100,100,0,0,1,{max(2, hsize // 20)},{max(2, hsize // 18)},5,80,80,0,1
Style: HookBold,{hfont},{hsize},{ass_color(hook.get('color', 'FFFFFF'))},{white},{black},{black},-1,0,0,0,100,100,0,0,1,{max(4, hsize // 9)},0,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    x = W // 2
    hook_end = 0.0
    if hook.get("text"):
        hook_end = min(float(hook.get("end", 3.0)), dur)
        style = {"box": "HookBox", "bold": "HookBold"}.get(hook.get("style", "plain"), "HookPlain")
        y = int(H * hook.get("y", 0.33))
        ev.append(f"Dialogue: 2,{ts(0)},{ts(hook_end)},{style},,0,0,0,,{{\\pos({x},{y})\\fad(0,120)}}{esc(hook['text'])}")

    cta_start = dur
    if cta.get("text"):
        cta_start = max(0.0, dur - float(cta.get("seconds", 3.0)))
        style = "HookBox" if cta.get("style", "box") == "box" else "HookBold"
        y = int(H * cta.get("y", 0.42))
        ev.append(f"Dialogue: 3,{ts(cta_start)},{ts(dur)},{style},,0,0,0,,{{\\pos({x},{y})\\fad(150,0)}}{esc(cta['text'])}")

    words = plan.get("_words", [])
    if words and cap:
        start_at = hook_end if cap.get("after_hook", True) else 0.0
        kw = {k.lower() for k in cap.get("keywords", [])}
        neg = {k.lower() for k in cap.get("negative_words", [])}
        acc = ass_color(cap["accent"]) if cap.get("accent") else None  # null = white only
        red = ass_color(cap.get("negative", "FF4D4D"))
        n = 1 if cap.get("mode", "word") == "word" else int(cap.get("max_words", 3))
        y = int(H * cap.get("y", 0.33))
        ws = [w for w in words if w["s"] >= start_at - 0.05 and w["s"] < cta_start]
        groups, cur = [], []
        for w in ws:
            cur.append(w)
            ends_sentence = re.search(r"[.!?,]$", w["w"]) is not None
            if len(cur) >= n or ends_sentence:
                groups.append(cur); cur = []
        if cur:
            groups.append(cur)
        for i, g in enumerate(groups):
            s = g[0]["s"]
            nxt = groups[i + 1][0]["s"] if i + 1 < len(groups) else min(cta_start, g[-1]["e"] + 0.4)
            e = min(nxt, g[-1]["e"] + 0.6) if nxt - g[-1]["e"] > 0.6 else nxt
            parts = []
            for w in g:
                t = w["w"].strip()
                bare = re.sub(r"[^\w$%.]", "", t.lower()).strip(".")
                t = re.sub(r"[,.!?;:]+$", "", t)
                if cap.get("upper", True):
                    t = t.upper()
                if acc is None:
                    parts.append(esc(t))
                elif bare in neg:
                    parts.append(f"{{\\c{red}}}{esc(t)}{{\\c{white}}}")
                elif bare in kw or re.search(r"\d", bare):
                    parts.append(f"{{\\c{acc}}}{esc(t)}{{\\c{white}}}")
                else:
                    parts.append(esc(t))
            pop = "\\fscx92\\fscy92\\t(0,80,\\fscx100\\fscy100)" if cap.get("pop", False) else ""
            ev.append(f"Dialogue: 1,{ts(s)},{ts(max(e, s + 0.12))},Cap,,0,0,0,,{{\\pos({x},{y}){pop}}}{' '.join(parts)}")

    card = plan.get("card") or {}
    if plan.get("layout") == "card":
        y0 = int(H * card.get("y", 0.3))
        fs = int(H * card.get("size", 0.036))
        if card.get("header"):
            ev.append(f"Dialogue: 1,{ts(0)},{ts(dur)},HookBold,,0,0,0,,{{\\an7\\pos(100,{y0})\\fs{fs}\\bord0}}{esc(card['header'])}")
        body = "\\N".join(esc(l) for l in card.get("lines", []))
        ev.append(f"Dialogue: 1,{ts(0)},{ts(dur)},Cap,,0,0,0,,{{\\an7\\pos(100,{y0 + int(fs*2)})\\b0\\bord0\\fs{fs}}}{body}")
    return head + "\n".join(ev) + "\n"


def cover(label_in, w, h, rect=None, focus_x=0.5):
    pre = f"crop={rect[2]}:{rect[3]}:{rect[0]}:{rect[1]}," if rect else ""
    return (f"{label_in}{pre}scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h}:(in_w-{w})*{focus_x}:(in_h-{h})/2,setsar=1")


def measure_lufs(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", out)
    return float(m[-1]) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("out"); ap.add_argument("--ass-only")
    a = ap.parse_args()
    base = os.path.dirname(os.path.abspath(a.plan))
    plan = json.load(open(a.plan))
    rel = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
    layout = plan.get("layout", "full")
    if plan.get("words"):
        plan["_words"] = json.load(open(rel(plan["words"])))["words"]

    if layout == "card":
        dur = float(plan["card"].get("seconds", 8))
    else:
        dur = float(probe(rel(plan["main"])))
    ass = build_ass(plan, dur)
    if a.ass_only:
        open(a.ass_only, "w").write(ass); print(a.ass_only); return

    with tempfile.TemporaryDirectory() as d:
        ass_path = os.path.join(d, "o.ass")
        open(ass_path, "w").write(ass)
        inputs, fc = [], []
        if layout == "card":
            bg = plan["card"].get("bg", "000000")
            inputs += ["-f", "lavfi", "-i", f"color=c=0x{bg}:s={W}x{H}:r=30:d={dur}",
                       "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo:d={dur}"]
            fc.append(f"[0:v]ass={ass_path}[v]")
            amap = "1:a"
        else:
            main = rel(plan["main"])
            inputs += ["-i", main]
            if layout == "full":
                fc.append(cover("[0:v]", W, H, plan.get("rect"), plan.get("focus_x", 0.5)) + "[base]")
            elif layout == "stack":
                st = plan["stack"]
                top_h = int(H * st.get("split", 0.33)) // 2 * 2
                idx = {"main": 0}
                for part in ("top", "bottom"):
                    src = st[part].get("src", "main")
                    if src not in idx:
                        idx[src] = len(idx); inputs += ["-i", rel(src)]
                t, b = st["top"], st["bottom"]
                fc.append(cover(f"[{idx[t.get('src','main')]}:v]", W, top_h, t.get("rect")) + "[t]")
                fc.append(cover(f"[{idx[b.get('src','main')]}:v]", W, H - top_h, b.get("rect")) + "[b]")
                fc.append("[t][b]vstack=inputs=2[base]")
            else:
                raise SystemExit(f"unknown layout {layout} (use full, stack or card)")
            fc.append(f"[base]fps=30,ass={ass_path}[v]")
            amap = "0:a" if has_audio(main) else None
        args = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[v]"]
        if amap:
            target = plan.get("loudness_lufs", -14)
            gain = 0.0
            if layout != "card":
                cur = measure_lufs(rel(plan["main"]))
                gain = 0.0 if cur is None or cur < -60 else max(-20.0, min(20.0, target - cur))
            # Measured linear gain plus a limiter; single-pass loudnorm can shift sync.
            args += ["-map", amap, "-af", f"volume={gain:.2f}dB,alimiter=limit=0.95", "-c:a", "aac", "-b:a", "192k"]
        args += ["-t", f"{dur:.3f}", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                 "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.out]
        subprocess.run(args, check=True)
    json.dump({"duration": dur, "hook_end": (plan.get("hook") or {}).get("end"),
               "cta_seconds": (plan.get("cta") or {}).get("seconds") if plan.get("cta") else None},
              open(os.path.splitext(a.out)[0] + ".render.json", "w"))
    print(f"rendered {dur:.1f}s -> {a.out}")


if __name__ == "__main__":
    sys.exit(main())

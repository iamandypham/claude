#!/usr/bin/env python3
"""Render full-frame graphic cards (1920x1080 PNG) for build_long.py "cards".

  python3 -I make_cards.py cards.json OUT_DIR [--fonts DIR] [--images DIR] [--browser PATH]

  --fonts DIR    folder of .ttf files (Montserrat 800/900, Playfair Display italic) to embed in the page;
                 without it the fonts must be installed on the machine
  --images DIR   folder that relative "image" paths in cards.json are read from (default: the cards.json folder)
  --browser PATH Chrome or Edge to use when the Node Playwright is not on the machine (found on its own on Windows)

cards.json is a list. Each card has "id" and "type":
  step     {"kicker": "FIX 1", "title": "One strategy"}
  words    {"lines": ["Traffic", "Conversion", "LTV"], "hi": 1}            hi = 1-based line in yellow (0 = none)
  number   {"big": "$99", "label": "a month", "kicker": "THE SWEET SPOT"}
  compare  {"left": {"big": "$31,290", "label": "a month"}, "right": {"big": "$95,138", "label": "a month"},
            "note": "about 77 days"}
  list     {"title": "The six fixes", "items": ["Your strategy", ...], "build": true}
           build writes one image per step (id-1, id-2, ...) with the newest item in yellow
  quote    {"text": "Emails, not views.", "by": ""}
  proof    {"image": "/abs/path.png", "caption": "Options Discord, monthly recurring", "blur": [[x, y, w, h], ...],
            "crop": [x, y, w, h], "kicker": "REAL DASHBOARD"}
           blur boxes are fractions of the (cropped) image (0-1) and hide a name or brand pill;
           crop is a fraction box of the source image and is the cleaner way to drop a name
  proof2   {"left": {"image": ..., "crop": ..., "caption": "Before"}, "right": {...}, "note": "about 77 days"}
  flow     {"title": "The flywheel", "items": ["Reel", "PDF", "Email", "Video", "Discord"], "build": true}
  ladder   {"title": "The back end", "items": ["Monthly community", ..., "High ticket"], "build": true}
           first item is the bottom rung; build adds rungs bottom to top
  strike   {"old": "Too expensive", "new": "Onboarding", "kicker": "THE REAL REASON"}   id-1 = old only, id-2 = struck + new
  checks   {"title": "All six", "items": [...]}                       every item ticked
  cta      {"kicker": "FREE", "title": "Discord template", "sub": "First link in the description"}
  raw      {"html": "<div>...</div>", "css": ".x{...}"}      your own markup inside the centred 1640 px wrap

Any card can carry "mode": "side": the content is laid out in the right-hand panel (x 1080 on) that build_long.py
shows next to the speaker. Every card also gets two pop-in lead frames, <id>.pop1.png and <id>.pop2.png
(not for later steps of a build); "no_pop": true skips them.

Writes OUT_DIR/<id>.png and OUT_DIR/index.json (id -> file). One accent colour, no client names in text.
Every number on a card must be one that is spoken at that moment and cleared in the script.
"""
import base64, html, json, mimetypes, os, sys

ACCENT = "#FFD400"
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1920px;height:1080px;background:#0B0B0F;color:#fff;font-family:'Montserrat',sans-serif;overflow:hidden}
body{display:flex;align-items:center;justify-content:center;
 background:radial-gradient(1100px 700px at 50% 42%,rgba(255,212,0,.10),rgba(11,11,15,0) 70%),
 linear-gradient(#0B0B0F,#0B0B0F)}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),
 linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:96px 96px}
.wrap{position:relative;width:1640px;text-align:center}
.kicker{font-weight:800;font-size:44px;letter-spacing:.16em;color:ACCENT;text-transform:uppercase;margin-bottom:28px}
.title{font-weight:900;font-size:170px;line-height:1.04;letter-spacing:-.01em}
.serif{font-family:'Playfair Display',serif;font-style:italic;font-weight:500}
.big{font-weight:900;font-size:300px;line-height:1;letter-spacing:-.02em}
.label{font-size:64px;font-weight:800;color:#d9d9de;margin-top:18px}
.words div{font-weight:900;font-size:150px;line-height:1.12}
.hi{color:ACCENT}
.dim{color:#5a5a63}
.list{text-align:left;display:inline-block}
.list h1{font-weight:800;font-size:60px;letter-spacing:.14em;text-transform:uppercase;color:ACCENT;margin-bottom:40px}
.list .it{font-weight:800;font-size:92px;line-height:1.28;display:flex;gap:34px;align-items:baseline}
.list .n{width:100px;text-align:right;color:#8b8b95;font-weight:900}
.list .it.new{color:ACCENT}.list .it.new .n{color:ACCENT}
.cmp{display:flex;align-items:center;justify-content:center;gap:70px}
.cmp .big{font-size:190px}
.cmp .arrow{font-size:150px;color:ACCENT;font-weight:900}
.note{margin-top:44px;font-size:58px}
.quote{font-size:150px;line-height:1.12}
.by{margin-top:36px;font-size:46px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#8b8b95}
.proof{display:flex;flex-direction:column;align-items:center;gap:36px}
.shot{position:relative;display:inline-block;border-radius:22px;overflow:hidden;box-shadow:0 30px 90px rgba(0,0,0,.6);
 border:3px solid rgba(255,255,255,.14)}
.shot img{display:block;max-width:1500px;max-height:760px}
.blur{position:absolute;backdrop-filter:blur(22px);background:rgba(120,120,120,.25);border-radius:10px}
.cap{font-size:50px;font-weight:800;color:#d9d9de}
""".replace("ACCENT", ACCENT) + """
.pair{display:flex;align-items:flex-start;justify-content:center;gap:60px}
.pair .shot img{max-width:760px;max-height:620px}
.pair .cap{margin-top:22px}
.flow{display:flex;align-items:center;justify-content:center;gap:26px;flex-wrap:nowrap}
.flow .node{font-weight:900;font-size:78px;padding:26px 40px;border-radius:26px;border:4px solid rgba(255,255,255,.22);
 background:rgba(255,255,255,.05)}
.flow .node.new{border-color:#FFD400;color:#FFD400;background:rgba(255,212,0,.08)}
.flow .ar{font-size:70px;color:#8b8b95;font-weight:900}
.h1{font-weight:800;font-size:60px;letter-spacing:.14em;text-transform:uppercase;color:#FFD400;margin-bottom:56px}
.ladder{display:flex;flex-direction:column-reverse;align-items:center;gap:18px}
.ladder .rung{font-weight:900;font-size:74px;padding:20px 0;border-radius:22px;border:4px solid rgba(255,255,255,.2);
 background:rgba(255,255,255,.05);text-align:center}
.ladder .rung.new{border-color:#FFD400;color:#FFD400;background:rgba(255,212,0,.08)}
.old{font-weight:900;font-size:170px;line-height:1.05}
.old.x{color:#6d6d77;text-decoration:line-through;text-decoration-color:#ff4d4d;text-decoration-thickness:14px;font-size:120px}
.newt{font-weight:900;font-size:190px;color:#FFD400;margin-top:26px;line-height:1.05}
.tick{color:#FFD400;width:100px;text-align:right;font-weight:900}
.sub{font-size:66px;margin-top:34px;color:#d9d9de}
body.side{background:#0B0B0F}
body.side:before{content:"";position:absolute;left:1080px;top:0;width:3px;height:100%;
 background:linear-gradient(rgba(255,212,0,0),rgba(255,212,0,.85),rgba(255,212,0,0))}
body.side .wrap{position:absolute;left:1140px;top:0;width:720px;height:1080px;display:flex;flex-direction:column;
 justify-content:center;text-align:left}
body.side .list{display:block}
body.side .list h1{font-size:40px;margin-bottom:34px}
body.side .list .it{font-size:56px;line-height:1.22;gap:22px;margin-bottom:22px}
body.side .list .n{width:56px;flex:none}
body.side .kicker{font-size:36px}
body.side .big{font-size:170px}
body.side .label{font-size:46px}
body.side .title{font-size:96px}
body.side .words div{font-size:100px}
"""


def e(s):
    return html.escape(str(s))


def data_uri(path):
    mt = mimetypes.guess_type(path)[0] or "image/png"
    return f"data:{mt};base64," + base64.b64encode(open(path, "rb").read()).decode()


def shot(c):
    """An image in a rounded frame, optionally cropped (fraction box) and with blur boxes."""
    blurs = "".join(f'<div class="blur" style="left:{x * 100}%;top:{y * 100}%;width:{w * 100}%;height:{h * 100}%"></div>'
                    for x, y, w, h in c.get("blur", []))
    src = c["image"] if os.path.isabs(c["image"]) else os.path.join(IMAGES, c["image"])
    if not os.path.exists(src):
        sys.exit(f"image not found: {src}")
    if c.get("crop"):
        import subprocess, tempfile
        x, y, w, h = c["crop"]
        out = tempfile.mktemp(suffix=".png")
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", src, "-vf",
                        f"crop=iw*{w}:ih*{h}:iw*{x}:ih*{y}", out], check=True)
        src = out
    mw = f' style="width:{c["width"]}px;max-width:none"' if c.get("width") else ""
    return f'<div class="shot"><img src="{data_uri(src)}"{mw}>{blurs}</div>'


def body(c, shown=None):
    t = c["type"]
    if t == "step":
        return f'<div class="wrap"><div class="kicker">{e(c.get("kicker", ""))}</div><div class="title">{e(c["title"])}</div></div>'
    if t == "words":
        hi = c.get("hi", 0)
        rows = "".join(f'<div class="{"hi" if i + 1 == hi else ""}">{e(w)}</div>' for i, w in enumerate(c["lines"]))
        return f'<div class="wrap words">{rows}</div>'
    if t == "number":
        k = f'<div class="kicker">{e(c["kicker"])}</div>' if c.get("kicker") else ""
        lab = f'<div class="label">{e(c["label"])}</div>' if c.get("label") else ""
        return f'<div class="wrap">{k}<div class="big hi">{e(c["big"])}</div>{lab}</div>'
    if t == "compare":
        longest = max(len(str(c["left"]["big"])), len(str(c["right"]["big"])))
        fs = c.get("size") or (190 if longest <= 8 else 130 if longest <= 11 else 96)
        def side(s, cls=""):
            return (f'<div><div class="big {cls}" style="font-size:{fs}px">{e(s["big"])}</div>'
                    f'<div class="label">{e(s.get("label", ""))}</div></div>')
        note = f'<div class="note serif">{e(c["note"])}</div>' if c.get("note") else ""
        return (f'<div class="wrap"><div class="cmp">{side(c["left"])}<div class="arrow">&rarr;</div>'
                f'{side(c["right"], "hi")}</div>{note}</div>')
    if t == "list":
        n = len(c["items"]) if shown is None else shown
        rows = "".join(
            f'<div class="it {"new" if (shown is not None and i + 1 == n) else ""}"><span class="n">{i + 1}</span>'
            f'<span>{e(it)}</span></div>' for i, it in enumerate(c["items"][:n]))
        pad = "".join(f'<div class="it" style="visibility:hidden"><span class="n">{i + 1}</span><span>{e(it)}</span></div>'
                      for i, it in enumerate(c["items"][n:], start=n))
        return f'<div class="wrap"><div class="list"><h1>{e(c.get("title", ""))}</h1>{rows}{pad}</div></div>'
    if t == "quote":
        by = f'<div class="by">{e(c["by"])}</div>' if c.get("by") else ""
        return f'<div class="wrap"><div class="quote serif">{e(c["text"])}</div>{by}</div>'
    if t == "proof":
        k = f'<div class="kicker" style="margin-bottom:0">{e(c["kicker"])}</div>' if c.get("kicker") else ""
        cap = f'<div class="cap">{e(c["caption"])}</div>' if c.get("caption") else ""
        return f'<div class="wrap proof">{k}{shot(c)}{cap}</div>'
    if t == "proof2":
        def side(s_):
            cap = f'<div class="cap">{e(s_["caption"])}</div>' if s_.get("caption") else ""
            return f'<div>{shot(s_)}{cap}</div>'
        note = f'<div class="note serif">{e(c["note"])}</div>' if c.get("note") else ""
        return f'<div class="wrap"><div class="pair">{side(c["left"])}{side(c["right"])}</div>{note}</div>'
    if t == "flow":
        n = len(c["items"]) if shown is None else shown
        parts = []
        for i, it in enumerate(c["items"]):
            vis = "" if i < n else ' style="visibility:hidden"'
            if i:
                parts.append(f'<div class="ar"{vis}>&rarr;</div>')
            parts.append(f'<div class="node {"new" if (shown is not None and i + 1 == n) else ""}"{vis}>{e(it)}</div>')
        ttl = f'<div class="h1">{e(c["title"])}</div>' if c.get("title") else ""
        inner = "".join(parts)
        if c.get("size"):
            inner = f'<style>.flow .node{{font-size:{int(c["size"])}px}}</style>' + inner
        return f'<div class="wrap" style="width:1800px">{ttl}<div class="flow">{inner}</div></div>'
    if t == "ladder":
        n = len(c["items"]) if shown is None else shown
        m = len(c["items"])
        rows = "".join(
            f'<div class="rung {"new" if (shown is not None and i + 1 == n) else ""}" '
            f'style="width:{1500 - (i * 700 // max(m - 1, 1))}px;{"" if i < n else "visibility:hidden"}">{e(it)}</div>'
            for i, it in enumerate(c["items"]))
        ttl = f'<div class="h1" style="margin-bottom:36px">{e(c["title"])}</div>' if c.get("title") else ""
        return f'<div class="wrap">{ttl}<div class="ladder">{rows}</div></div>'
    if t == "strike":
        k = f'<div class="kicker">{e(c["kicker"])}</div>' if c.get("kicker") else ""
        if shown == 1:
            return f'<div class="wrap"><div class="old serif">&ldquo;{e(c["old"])}&rdquo;</div></div>'
        return (f'<div class="wrap">{k}<div class="old x">{e(c["old"])}</div>'
                f'<div class="newt">{e(c["new"])}</div></div>')
    if t == "checks":
        rows = "".join(f'<div class="it"><span class="tick">&#10003;</span><span>{e(it)}</span></div>' for it in c["items"])
        return f'<div class="wrap"><div class="list"><h1>{e(c.get("title", ""))}</h1>{rows}</div></div>'
    if t == "raw":
        return f'<div class="wrap">{c["html"]}</div>'
    if t == "cta":
        k = f'<div class="kicker">{e(c["kicker"])}</div>' if c.get("kicker") else ""
        sub = f'<div class="sub serif">{e(c["sub"])}</div>' if c.get("sub") else ""
        return f'<div class="wrap">{k}<div class="title" style="font-size:{c.get("size", 150)}px">{e(c["title"])}</div>{sub}</div>'
    sys.exit(f"unknown card type {t!r} in card {c.get('id')}")


FONT_CSS = ""
IMAGES = "."


def font_css(d):
    """@font-face rules with the .ttf files of a folder embedded, so the page needs no installed fonts."""
    out = []
    for f in sorted(os.listdir(d)):
        if not f.lower().endswith(".ttf"):
            continue
        low = f.lower()
        fam = "Playfair Display" if "playfair" in low else "Montserrat" if "montserrat" in low else None
        if not fam:
            continue
        wt = next((w for w in ("900", "800", "700", "600", "500", "400") if w in low), "400")
        style = "italic" if fam == "Playfair Display" else "normal"
        if fam == "Playfair Display":
            wt = "400 900"                      # one italic file serves every weight the cards ask for
        b = base64.b64encode(open(os.path.join(d, f), "rb").read()).decode()
        out.append(f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{wt};"
                   f"src:url(data:font/ttf;base64,{b}) format('truetype')}}")
        if fam == "Playfair Display":
            break
    return "".join(out)


def page(inner, side=False, pop=0, css=""):
    """pop 1 and 2 are the two lead frames of the pop-in: smaller and fainter than the card itself."""
    popcss = {0: "", 1: ".wrap{transform:scale(.9);opacity:.3}", 2: ".wrap{transform:scale(.96);opacity:.75}"}[pop]
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}{CSS}{css}{popcss}</style></head>'
            f'<body class="{"side" if side else ""}"><div class="grid"></div>{inner}</body></html>')


def find_browser(given):
    import shutil
    cands = [given, os.environ.get("CARDS_BROWSER"),
             r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
             r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
             r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
             "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    cands += [shutil.which(n) for n in ("chrome", "google-chrome", "chromium", "chromium-browser", "msedge")]
    return next((c for c in cands if c and os.path.exists(c)), None)


def shoot_with_browser(browser, plan):
    """No Playwright: headless Chrome/Edge screenshots a taller window, ffmpeg crops the 1920x1080 page out of it."""
    import subprocess, pathlib
    for h, f in plan:
        raw = f + ".raw.png"
        cmd = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
               "--window-size=1920,1400", "--virtual-time-budget=3000", f"--screenshot={raw}", pathlib.Path(h).as_uri()]
        if os.name != "nt" and hasattr(os, "geteuid") and os.geteuid() == 0:
            cmd.insert(1, "--no-sandbox")
        r = subprocess.run(cmd, capture_output=True, text=True)
        if not os.path.exists(raw):
            sys.exit(f"browser screenshot failed for {h}:\n" + r.stderr[-1500:])
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", raw, "-vf", "crop=1920:1080:0:0",
                        "-frames:v", "1", f], check=True)
        os.remove(raw)


def main():
    global FONT_CSS, IMAGES
    import argparse, subprocess, tempfile
    ap = argparse.ArgumentParser()
    ap.add_argument("cards")
    ap.add_argument("out")
    ap.add_argument("--fonts")
    ap.add_argument("--images")
    ap.add_argument("--browser")
    a = ap.parse_args()
    cards = json.load(open(a.cards, encoding="utf-8"))
    out = a.out
    IMAGES = a.images or os.path.dirname(os.path.abspath(a.cards))
    if a.fonts:
        FONT_CSS = font_css(a.fonts)
    os.makedirs(out, exist_ok=True)
    jobs = []
    for c in cards:
        side, css = c.get("mode") == "side", c.get("css", "")
        def add(cid, shown=None, pops=True):
            jobs.append((cid, page(body(c, shown), side, 0, css)))
            if pops and not c.get("no_pop"):
                jobs.append((cid + ".pop1", page(body(c, shown), side, 1, css)))
                jobs.append((cid + ".pop2", page(body(c, shown), side, 2, css)))
        if c["type"] in ("list", "flow", "ladder") and c.get("build"):
            for k in range(1, len(c["items"]) + 1):
                add(f'{c["id"]}-{k}', k, pops=(k == 1))        # later steps cut in hard: only the new line changes
        elif c["type"] == "strike":
            add(f'{c["id"]}-1', 1)
            add(f'{c["id"]}-2', 2, pops=False)
        else:
            add(c["id"])
    tmp = tempfile.mkdtemp(prefix="cards-")
    index, plan = {}, []
    for cid, doc in jobs:
        h = os.path.join(tmp, f"{cid}.html")
        open(h, "w", encoding="utf-8").write(doc)
        f = os.path.abspath(os.path.join(out, f"{cid}.png"))
        plan.append([h, f]); index[cid] = f
    # The Node Playwright that ships with the cloud machine is tried first (a pip copy would not find its browser);
    # a machine without it (a Windows PC) falls back to its own Chrome or Edge.
    has_pw = (not a.browser) and subprocess.run(["node", "-e", "require('playwright')"], capture_output=True,
                                                 shell=(os.name == "nt")).returncode == 0
    if has_pw:
        js = os.path.join(tmp, "shoot.js")
        open(js, "w").write("""
const { chromium } = require('playwright');
const jobs = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  for (const [h, f] of jobs) {
    await p.goto(require('url').pathToFileURL(h).href, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: f });
  }
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
""")
        jf = os.path.join(tmp, "jobs.json")
        json.dump(plan, open(jf, "w"))
        r = subprocess.run(["node", js, jf], capture_output=True, text=True)
        if r.returncode:
            sys.exit("card render failed:\n" + r.stderr[-2000:])
    else:
        browser = find_browser(a.browser)
        if not browser:
            sys.exit("no Node Playwright and no Chrome/Edge found; pass --browser PATH")
        shoot_with_browser(browser, plan)
    json.dump({k: os.path.basename(v) for k, v in index.items()}, open(os.path.join(out, "index.json"), "w"), indent=1)
    print(f"{len(index)} cards -> {out}")


if __name__ == "__main__":
    main()

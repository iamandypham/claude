import json, subprocess, sys
cfg=json.load(open(sys.argv[1])); W=cfg["work"]
words=json.load(open(cfg["words"]))
segs=cfg["segments"]
# remap words that fall inside kept segments
out=[];off=0.0
drop=set(cfg.get("drop_starts",[]))
for si,(a,b) in enumerate(segs):
    for x in words:
        mid=(x["s"]+x["e"])/2
        if a<=mid<=b and x["s"] not in drop: out.append({"w":x["w"].strip(),"s":max(x["s"],a)-a+off,"e":min(x["e"],b)-a+off,"seg":si})
    off+=b-a
import os
FONTS=os.path.expanduser(cfg.get("fonts_dir","~/.fonts"))
tail=cfg.get("tail",0.3)  # R-104 end hold
total=off+tail
for f in cfg.get("fixes",{}):
    for x in out:
        if x["w"].strip(".,?!").lower()==f.lower(): x["w"]=x["w"].replace(x["w"].strip(".,?!"),cfg["fixes"][f])
def ts(t):
    h=int(t//3600);m=int(t%3600//60);s=t%60;return f"{h}:{m:02d}:{s:05.2f}"
cap_y=cfg.get("cap_margin_v",540); hook=cfg["hook"]
# Hook title looks (styles/hook-titles.md, Andy 10 Nov 2026: "only use these styles").
# V1 native white box, V2 plain bold white, V3 outline listicle, V4 condensed caps (*word* = yellow).
# "legacy" = the old yellow box, kept only to re-render old drafts.
look=cfg.get("hook_look","V1"); hm=cfg.get("hook_margin_v",310)
HS={
 "V1":("Montserrat ExtraBold",58,"&H00000000","&H00FFFFFF","&H00FFFFFF",100,100,0,3,14,0),
 "V2":("Montserrat ExtraBold",66,"&H00FFFFFF","&H00000000","&H80000000",100,100,0,1,0,4),
 "V3":("Montserrat ExtraBold",72,"&H00FFFFFF","&H00000000","&H00000000",100,100,0,1,7,0),
 "V4":("Montserrat Black",104,"&H00FFFFFF","&H00000000","&H80000000",100,125,-2,1,0,3),
 "legacy":("Montserrat ExtraBold",64,"&H00000000","&H0000D7FF","&H0000D7FF",100,100,1,3,18,0),
}
fn,fs,pc,oc,bc,sx,sy,sp,bs,ol,sh=HS[look]
HOOK_STYLE=f"Style: Hook,{fn},{cfg.get('hook_size',fs)},{pc},{pc},{oc},{bc},-1,0,0,0,{sx},{sy},{sp},0,{bs},{ol},{sh},8,70,70,{hm},1"
import re as _re
# Caption looks. default = BG caps (Montserrat ExtraBold 78, outline). "ref" = styles/reference-iman.md:
# small sentence-case sans, no outline, soft shadow, 2 words, centred at cap_center_pct of frame height.
REF=cfg.get("cap_style")=="ref"
if REF:
    csz=cfg.get("cap_size",60); cap_y=int(1920*cfg.get("cap_center_pct",54)/100-csz*0.6)
    CAP_STYLE=f"Style: Cap,Inter SemiBold,{csz},&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,0,0,0,0,100,100,0,0,1,0,2,8,60,60,{cap_y},1"
else:
    CAP_STYLE=f"Style: Cap,Montserrat ExtraBold,{cfg.get('cap_size',78)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,6,3,8,60,60,{cap_y},1"
EMPH={w.lower() for w in cfg.get("emph",[])}; ACC=cfg.get("accent","&H003030E6&")  # ASS colour is BGR
def _cap_text(g):
    if not REF: return " ".join(x["w"] for x in g).upper()
    o=[]
    for x in g:
        w=x["w"]
        if w.strip(".,?!").lower() in EMPH: w="{\\fnLiberation Serif\\i1\\b1\\fs"+str(int(csz*1.7))+"\\c"+ACC+"}"+w+"{\\r}"
        o.append(w)
    return " ".join(o)
hook=_re.sub(r"\*([^*]+)\*",r"{\\c&H0000D4FF&}\1{\\c}",hook)
if cfg.get("hook_sub"): hook+="\\N{\\fs"+str(int(fs*0.62))+"}"+cfg["hook_sub"]
ass=f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{CAP_STYLE}
{HOOK_STYLE}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
he=cfg.get("hook_end","full")  # "full" = whole video (single-shot take); else seconds, e.g. the first cut away
ass+=f"Dialogue: 1,{ts(0)},{ts(total if he=='full' else he)},Hook,,0,0,0,,{hook}\n"
n=cfg.get("group",2 if REF else 3)
groups=[];g=[]
for x in out:
    if g and x["seg"]!=g[-1]["seg"]: groups.append(g); g=[]
    g.append(x)
    if len(g)==n or x["w"].rstrip()[-1:] in ".?!": groups.append(g); g=[]
if g: groups.append(g)
for i,g in enumerate(groups):
    st=g[0]["s"]; en=groups[i+1][0]["s"] if i+1<len(groups) else total
    if en-g[-1]["e"]>0.6: en=g[-1]["e"]+0.3
    txt=_cap_text(g)
    ass+=f"Dialogue: 0,{ts(st)},{ts(en)},Cap,,0,0,0,,{txt}\n"
open(f"{W}/caps.ass","w").write(ass)
json.dump(out,open(f"{W}/cut_words.json","w"),indent=0)
fd=0.03
fc=[]
for i,(a,b) in enumerate(segs):
    d=b-a
    fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d={fd},afade=t=out:st={d-fd:.3f}:d={fd}[a{i}]")
fc.append("".join(f"[v{i}][a{i}]" for i in range(len(segs)))+f"concat=n={len(segs)}:v=1:a=1[vc0][ac0];[vc0]tpad=stop_mode=clone:stop_duration={tail}[vc];[ac0]apad=pad_dur={tail}[ac]")
fc.append(f"[vc]subtitles={W}/caps.ass:fontsdir={FONTS},format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709[vo];[ac]LOUDNORM,aresample=48000[ao]")
import re
fc1=";".join(fc[:-1])+f";[ac]loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json[ao];[vc]nullsink"
r=subprocess.run(["ffmpeg","-hide_banner","-y","-i",cfg["src"],"-filter_complex",fc1,"-map","[ao]","-f","null","-"],capture_output=True,text=True)
m=json.loads(re.findall(r"\{[^{}]*\}",r.stderr)[-1])
ln=f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
fc[-1]=fc[-1].replace("LOUDNORM",ln)
subprocess.run(["ffmpeg","-loglevel","error","-y","-i",cfg["src"],"-filter_complex",";".join(fc),"-map","[vo]","-map","[ao]",
  "-c:v","libx264","-profile:v","high","-crf","10","-preset","medium","-r","30","-c:a","aac","-b:a","192k","-movflags","+faststart",f"{W}/{cfg['name']}_master.mp4"],check=True)
subprocess.run(["ffmpeg","-loglevel","error","-y","-i",f"{W}/{cfg['name']}_master.mp4","-vf","scale=720:-2","-c:v","libx264","-crf","28","-preset","fast","-c:a","aac","-b:a","128k","-movflags","+faststart",f"{W}/{cfg['name']}_preview.mp4"],check=True)
print("total",round(total,2))

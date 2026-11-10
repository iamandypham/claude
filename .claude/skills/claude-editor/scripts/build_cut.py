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
tail=cfg.get("tail",0.0)
total=off+tail
for f in cfg.get("fixes",{}):
    for x in out:
        if x["w"].strip(".,?!").lower()==f.lower(): x["w"]=x["w"].replace(x["w"].strip(".,?!"),cfg["fixes"][f])
def ts(t):
    h=int(t//3600);m=int(t%3600//60);s=t%60;return f"{h}:{m:02d}:{s:05.2f}"
cap_y=cfg.get("cap_margin_v",540); hook=cfg["hook"]
ass=f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Montserrat ExtraBold,{cfg.get('cap_size',78)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,6,3,8,60,60,{cap_y},1
Style: Hook,Montserrat ExtraBold,{cfg.get('hook_size',64)},&H00000000,&H00000000,&H0000D7FF,&H0000D7FF,0,0,0,0,100,100,1,0,3,18,0,8,70,70,{cfg.get('hook_margin_v',230)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ass+=f"Dialogue: 1,{ts(0)},{ts(cfg.get('hook_end',3.6))},Hook,,0,0,0,,{hook}\n"
n=cfg.get("group",3)
groups=[];g=[]
for x in out:
    if g and x["seg"]!=g[-1]["seg"]: groups.append(g); g=[]
    g.append(x)
    if len(g)==n or x["w"].rstrip()[-1:] in ".?!": groups.append(g); g=[]
if g: groups.append(g)
for i,g in enumerate(groups):
    st=g[0]["s"]; en=groups[i+1][0]["s"] if i+1<len(groups) else total
    if en-g[-1]["e"]>0.6: en=g[-1]["e"]+0.3
    txt=" ".join(x["w"] for x in g).upper()
    ass+=f"Dialogue: 0,{ts(st)},{ts(en)},Cap,,0,0,0,,{txt}\n"
open(f"{W}/caps.ass","w").write(ass)
json.dump(out,open(f"{W}/cut_words.json","w"),indent=0)
fd=0.03
fc=[]
for i,(a,b) in enumerate(segs):
    d=b-a
    fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d={fd},afade=t=out:st={d-fd:.3f}:d={fd}[a{i}]")
fc.append("".join(f"[v{i}][a{i}]" for i in range(len(segs)))+f"concat=n={len(segs)}:v=1:a=1[vc0][ac0];[vc0]tpad=stop_mode=clone:stop_duration={tail}[vc];[ac0]apad=pad_dur={tail}[ac]")
fc.append(f"[vc]subtitles={W}/caps.ass:fontsdir=/root/.fonts,format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709[vo];[ac]LOUDNORM,aresample=48000[ao]")
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

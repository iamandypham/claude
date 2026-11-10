import json,sys,glob,os,statistics as st,collections
rows=[]
for d in sorted(glob.glob(sys.argv[1]+"/*/breakdown.json")):
    b=json.load(open(d)); name=os.path.basename(os.path.dirname(d))
    dur=b["audio"].get("duration") or 0
    shots=b["shots"]; L=[s.get("t1",s.get("end",0))-s.get("t0",s.get("start",0)) for s in shots]
    t=json.load(open(os.path.dirname(d)+"/packaging/timeline.json"))
    txt=t["text"]; 
    # captions = short-lived cues with letters, not counters, within +-0.03 of the clip's caption line.
    # Valid for short-form. On long-form most cues are UI or graphic text: do not use the cap_* fields there.
    import re as _re
    cand=[c for c in txt if (c["t1"]-c["t0"])<3.0 and c.get("kind")!="counter" and _re.search(r"[A-Za-z]{2}",c["text"]) and 0.25<(c["bbox"][1]+c["bbox"][3]/2)<0.95 and not c.get("part_of_picture")]
    ymed=st.median([c["bbox"][1]+c["bbox"][3]/2 for c in cand]) if cand else 0
    cap=[c for c in cand if abs(c["bbox"][1]+c["bbox"][3]/2-ymed)<=0.03]
    words=[len(c["text"].split()) for c in cap]; cd=[c["t1"]-c["t0"] for c in cap]
    yc=[c["bbox"][1]+c["bbox"][3]/2 for c in cap]; hh=[c["bbox"][3] for c in cap]; ww=[c["bbox"][2] for c in cap]
    fills=collections.Counter(c["style"].get("fill_name") for c in cap)
    strokes=collections.Counter(c["style"].get("stroke_name") for c in cap)
    anim=collections.Counter((c.get("anim_in") or {}).get("kind") for c in cap)
    kinds=collections.Counter(c["kind"] for c in txt)
    persist=[(c["text"],round(c["t0"],1),round(c["t1"],1),round(c["bbox"][1],2)) for c in txt if c["t1"]-c["t0"]>=3.0][:6]
    a=b["audio"]; m=a.get("music") or {}; v=a.get("voice") or {}
    sfx=t.get("sfx",[]); sk=collections.Counter(((x.get("on") or {}).get("type") if isinstance(x.get("on"),dict) else "none") for x in sfx); conf=[x.get("confidence") for x in sfx if isinstance(x.get("confidence"),(int,float))]
    asp=b.get("aspects",{})
    def g(o,*ks):
        for k in ks:
            o=o.get(k,{}) if isinstance(o,dict) else {}
        return o
    r=dict(name=name,dur=round(dur,1),shots=len(shots),cuts_per_min=round((len(shots)-1)/dur*60,1) if dur else None,shot_median=round(st.median(L),2),
      cap_cues=len(cap),cap_per_min=round(len(cap)/dur*60,1) if dur else None,cap_words_median=st.median(words) if words else None,cap_words_max=max(words) if words else None,
      cap_dur_median=round(st.median(cd),2) if cd else None,cap_y_center=round(st.median(yc),3) if yc else None,cap_height_pct=round(100*st.median(hh),1) if hh else None,cap_width_pct=round(100*st.median(ww),1) if ww else None,
      fills=dict(fills.most_common(4)),strokes=dict(strokes.most_common(3)),anim_in=dict(anim.most_common(4)),text_kinds=dict(kinds),persistent=persist,
      voice_ratio=v.get("ratio"),music_ratio=m.get("ratio"),bpm=m.get("tempo_bpm"),key=g(m,"key").get("tonic","")+" "+g(m,"key").get("mode","") if m.get("key") else None,
      cuts_on_beat=a.get("cuts_on_beat_ratio"),beat_chance=a.get("cuts_on_beat_chance"),cuts_on_onset=a.get("cuts_on_onset_ratio"),
      sfx=len(sfx),sfx_per_min=round(len(sfx)/dur*60,1) if dur else None,sfx_anchor=dict(sk.most_common(5)),sfx_conf_median=(st.median(conf) if conf else None),sfx_types=dict(collections.Counter(x.get("type") for x in sfx).most_common(5)),
      rms=a.get("rms_dbfs"),silence_ratio=a.get("silence_ratio"),
      camera={k:(v if not isinstance(v,(dict,list)) else str(v)[:200]) for k,v in (asp.get("camera") or {}).items()} ,
      framing=str(asp.get("framing"))[:300],grade=str(asp.get("grade"))[:300],editing=str(asp.get("editing"))[:400])
    rows.append(r)
json.dump(rows,open(sys.argv[2],"w"),indent=1,ensure_ascii=False)
for r in rows: print(json.dumps(r,ensure_ascii=False)[:1800]); print()

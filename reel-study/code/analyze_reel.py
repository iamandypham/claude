#!/usr/bin/env python3
"""Per-reel frame + audio measures. Usage: analyze_reel.py VIDEO OUT.json [--frames DIR]
Visual: hard cuts, visual change events (cuts + big overlay/screen changes), seconds between changes,
motion energy, on-screen text (OCR 2 fps), face presence/size/position (layout).
Audio: dead air (silencedetect -35 dB, >=0.3 s), speech gaps from word timestamps, words/sec,
time to first word, hook transcript (first 3 s) and first sentence."""
import sys, json, subprocess, os, re
import numpy as np, cv2

vid, out = sys.argv[1], sys.argv[2]
fdir = sys.argv[sys.argv.index('--frames')+1] if '--frames' in sys.argv else None
wjson = sys.argv[sys.argv.index('--words')+1] if '--words' in sys.argv else None

def probe(v):
    j = json.loads(subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',v],capture_output=True,text=True).stdout)
    vs = [s for s in j['streams'] if s['codec_type']=='video'][0]
    has_a = any(s['codec_type']=='audio' for s in j['streams'])
    return float(j['format']['duration']), int(vs['width']), int(vs['height']), has_a

dur, W, H, has_audio = probe(vid)
R = {'file': os.path.basename(vid), 'duration': round(dur,2), 'w': W, 'h': H, 'has_audio': has_audio}

# ---- visual at 10 fps, small gray + small color for histograms
FPS = 10; w, h = 144, 256
raw = subprocess.run(['ffmpeg','-v','error','-i',vid,'-vf',f'fps={FPS},scale={w}:{h}','-f','rawvideo','-pix_fmt','bgr24','-'],capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
n = len(fr)
gray = fr.mean(axis=3).astype(np.float32)
diff = np.abs(np.diff(gray, axis=0)).mean(axis=(1,2)) if n > 1 else np.zeros(0)
hists = []
for f in fr:
    hh = cv2.calcHist([cv2.cvtColor(f, cv2.COLOR_BGR2HSV)],[0,1],None,[16,16],[0,180,0,256]); cv2.normalize(hh,hh); hists.append(hh)
hcorr = np.array([cv2.compareHist(hists[i],hists[i+1],cv2.HISTCMP_CORREL) for i in range(n-1)])
# hard cut: big histogram break AND big pixel change
cut = (hcorr < 0.55) & (diff > 18)
# visual change event: hard cut, or a local spike well above this reel's baseline motion (overlay pops, screen swaps, zooms)
med = float(np.median(diff)) if len(diff) else 0
spike = diff > max(10.0, 3.5*med)
ev = cut | spike
def times(mask, gap=0.4):
    t = []; 
    for i in np.where(mask)[0]:
        s = (i+1)/FPS
        if not t or s - t[-1] >= gap: t.append(s)
    return t
cuts, evs = times(cut), times(ev)
def gaps(ts):
    b = [0.0] + ts + [dur]; g = np.diff(b); return g[g>0]
gc, ge = gaps(cuts), gaps(evs)
R.update({
  'hard_cuts': len(cuts), 'cuts_per_10s': round(len(cuts)/dur*10,2), 'first_cut_s': cuts[0] if cuts else None,
  'sec_per_shot_median': round(float(np.median(gc)),2), 'sec_per_shot_mean': round(float(gc.mean()),2),
  'visual_changes': len(evs), 'changes_per_10s': round(len(evs)/dur*10,2), 'first_change_s': evs[0] if evs else None,
  'sec_between_changes_median': round(float(np.median(ge)),2), 'sec_between_changes_max': round(float(ge.max()),2),
  'changes_first_3s': sum(1 for t in evs if t <= 3), 'changes_first_10s': sum(1 for t in evs if t <= 10),
  'motion_mean': round(float(diff.mean()),2) if len(diff) else 0,
  'motion_first_3s': round(float(diff[:3*FPS].mean()),2) if len(diff) else 0,
  'motion_last_half': round(float(diff[len(diff)//2:].mean()),2) if len(diff) else 0,
  'longest_static_s': None,
  'brightness': round(float(gray.mean()),1),
})
# longest stretch without any change event
R['longest_static_s'] = R['sec_between_changes_max']

# ---- 2 fps frames at 540 wide for OCR + faces
FP2 = 2
raw2 = subprocess.run(['ffmpeg','-v','error','-i',vid,'-vf',f'fps={FP2},scale=540:-2','-f','image2pipe','-vcodec','png','-'],capture_output=True).stdout
imgs = []; i = 0
while True:
    j = raw2.find(b'IEND', i)
    if j < 0: break
    j += 8; a = np.frombuffer(raw2[i:j], np.uint8); im = cv2.imdecode(a, cv2.IMREAD_COLOR)
    if im is not None: imgs.append(im)
    i = j
from rapidocr_onnxruntime import RapidOCR
ocr = RapidOCR()
casc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
texts, text_frames, text_area, faces = [], 0, [], []
for k, im in enumerate(imgs):
    t = k / FP2
    if t > 5 and k % 2: continue
    res, _ = ocr(im)
    words = []; area = 0; ys = []
    if res:
        for box, s, conf in res:
            conf = float(conf)
            if conf < 0.6: continue
            words.append(s); b = np.array(box); area += cv2.contourArea(b.astype(np.float32)); ys.append(b[:,1].mean()/im.shape[0])
    if words: text_frames += 1
    texts.append({'t': t, 'text': ' '.join(words), 'y': round(float(np.mean(ys)),2) if ys else None})
    text_area.append(area/(im.shape[0]*im.shape[1]))
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    fs = casc.detectMultiScale(g, 1.15, 5, minSize=(40,40))
    if len(fs):
        x,y,fw,fh = max(fs, key=lambda r:r[2]*r[3])
        faces.append({'t': t, 'area': fw*fh/(im.shape[0]*im.shape[1]), 'cy': (y+fh/2)/im.shape[0], 'cx': (x+fw/2)/im.shape[1]})
nf = max(1, len(texts))
# caption change rate: distinct consecutive OCR strings
chg = 0; prev = None
for x in texts:
    s = re.sub(r'\W+','',x['text'].lower())
    if s and s != prev: chg += 1
    prev = s if s else prev
hook_txt = []
for x in texts:
    if x['t'] <= 3 and x['text'] and x['text'] not in hook_txt: hook_txt.append(x['text'])
face_pct = len(faces)/nf
R.update({
  'text_on_screen_pct': round(text_frames/nf,2), 'text_area_mean': round(float(np.mean(text_area)),3) if text_area else 0,
  'caption_changes_per_10s': round(chg/dur*10,2), 'onscreen_hook_text': ' | '.join(hook_txt)[:300],
  'text_y_median': round(float(np.median([x['y'] for x in texts if x['y'] is not None])),2) if any(x['y'] is not None for x in texts) else None,
  'face_pct': round(face_pct,2),
  'face_area_median': round(float(np.median([f['area'] for f in faces])),3) if faces else 0,
  'face_cy_median': round(float(np.median([f['cy'] for f in faces])),2) if faces else None,
  'face_first_s': faces[0]['t'] if faces else None,
})
cy, fa = R['face_cy_median'], R['face_area_median']
R['layout_guess'] = ('no_face' if face_pct < 0.15 else
                     'split_face_top' if cy is not None and cy < 0.38 and fa < 0.06 else
                     'split_face_bottom' if cy is not None and cy > 0.65 and fa < 0.06 else
                     'full_face')

if fdir:
    os.makedirs(fdir, exist_ok=True)
    # contact sheet: first 3 s at 2 fps + one frame every 3 s after
    pick = [k for k in range(len(imgs)) if k < 6 or k % 6 == 0][:24]
    th = [cv2.resize(imgs[k], (180, int(180*imgs[k].shape[0]/imgs[k].shape[1]))) for k in pick]
    hh = max(t.shape[0] for t in th); th = [cv2.copyMakeBorder(t,0,hh-t.shape[0],0,0,cv2.BORDER_CONSTANT) for t in th]
    for t,k in zip(th,pick): cv2.putText(t, f'{k/FP2:.1f}s', (4,16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 1)
    while len(th) % 8: th.append(np.zeros_like(th[0]))
    rows = [np.hstack(th[r:r+8]) for r in range(0, len(th), 8)]
    cv2.imwrite(os.path.join(fdir, os.path.splitext(R['file'])[0] + '.jpg'), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 70])

# ---- audio
if has_audio:
    a = subprocess.run(['ffmpeg','-v','info','-i',vid,'-af','silencedetect=noise=-35dB:d=0.3','-f','null','-'],capture_output=True,text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', a)]
    en = [(float(x), float(y)) for x,y in re.findall(r'silence_end: ([\d.]+) \| silence_duration: ([\d.]+)', a)]
    sil = sum(d for _,d in en) + (dur - st[-1] if len(st) > len(en) else 0)
    R.update({'dead_air_s': round(sil,2), 'dead_air_pct': round(sil/dur,3),
              'longest_silence_s': round(max([d for _,d in en] + ([dur-st[-1]] if len(st)>len(en) else []) or [0]),2),
              'starts_silent_s': round(en[0][0],2) if en and st and st[0] < 0.05 else 0.0})
    vol = subprocess.run(['ffmpeg','-v','info','-i',vid,'-af','volumedetect','-f','null','-'],capture_output=True,text=True).stderr
    m = re.search(r'mean_volume: ([-\d.]+)', vol); R['mean_volume_db'] = float(m.group(1)) if m else None
    if wjson and os.path.exists(wjson):
        tj = json.load(open(wjson))
        wd = [(x['start'], x['end'], ' ' + x['w'].strip()) for sg in tj.get('segments', []) for x in sg.get('words', [])]
        R['asr'] = 'existing'
    else:
        from faster_whisper import WhisperModel
        model = WhisperModel('base', device='cpu', compute_type='int8', cpu_threads=2)
        pcm = np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',vid,'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout, np.float32)
        segs, info = model.transcribe(pcm, word_timestamps=True, vad_filter=False)
        wd = [(w_.start, w_.end, w_.word) for s in segs for w_ in (s.words or [])]
        R['asr'] = 'whisper-base'
    if wd:
        txt = ''.join(x[2] for x in wd).strip()
        g = [wd[i+1][0]-wd[i][1] for i in range(len(wd)-1)]
        sp = wd[-1][1]-wd[0][0]
        first_sent = re.split(r'(?<=[.!?])\s', txt)[0]
        R.update({'words': len(wd), 'wps': round(len(wd)/max(sp,1),2), 'first_word_s': round(wd[0][0],2),
                  'speech_gaps_over_0_5s': sum(1 for x in g if x > 0.5), 'speech_gap_total_s': round(sum(x for x in g if x > 0.5),2),
                  'longest_speech_gap_s': round(max(g),2) if g else 0,
                  'speech_cover_pct': round(sum(x[1]-x[0] for x in wd)/dur,2),
                  'hook_spoken_3s': ''.join(x[2] for x in wd if x[0] < 3).strip(),
                  'first_sentence': first_sent[:250], 'transcript': txt[:4000]})
    else:
        R.update({'words': 0, 'wps': 0, 'first_word_s': None, 'speech_cover_pct': 0, 'hook_spoken_3s': '', 'first_sentence': '', 'transcript': ''})
json.dump(R, open(out,'w'), indent=1)
print(json.dumps({k: v for k, v in R.items() if k != 'transcript'}))

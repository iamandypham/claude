#!/usr/bin/env python3
"""Analyze every mp4 in MP4DIR (keeps polling while the download runs). Results -> OUTDIR/<stem>.json, sheets -> SHEETDIR.
Usage: run_batch.py MP4DIR OUTDIR SHEETDIR [--workers 3] [--until-file DONEFLAG]"""
import sys, os, subprocess, time, csv
from concurrent.futures import ProcessPoolExecutor
mp4, out, sheets = sys.argv[1:4]
W = int(sys.argv[sys.argv.index('--workers')+1]) if '--workers' in sys.argv else 3
flag = sys.argv[sys.argv.index('--until-file')+1] if '--until-file' in sys.argv else None
os.makedirs(out, exist_ok=True); os.makedirs(sheets, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))
TR = os.environ.get('RS_DATA', os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data'))+'/transcripts'
def job(f):
    stem = os.path.splitext(f)[0]; o = os.path.join(out, stem + '.json')
    if os.path.exists(o): return f, 'skip'
    cmd = ['python3', os.path.join(HERE, 'analyze_reel.py'), os.path.join(mp4, f), o, '--frames', sheets]
    t = os.path.join(TR, stem + '.json')
    if os.path.exists(t): cmd += ['--words', t]
    env = dict(os.environ, OMP_NUM_THREADS='1')
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=900)
    if r.returncode: open(os.path.join(out, stem + '.err'), 'w').write(r.stderr[-3000:])
    return f, r.returncode
seen = set()
with ProcessPoolExecutor(W) as ex:
    while True:
        CL=('daylotrading','thesuitedtrader','atraintrades','virlo-')
        new = sorted((f for f in os.listdir(mp4) if f.endswith('.mp4') and not f.startswith('_') and f not in seen
                     and time.time() - os.path.getmtime(os.path.join(mp4, f)) > 20), key=lambda f: (not f.startswith(CL), f))
        for f in new: seen.add(f)
        for f, rc in ex.map(job, new):
            print(time.strftime('%H:%M:%S'), f, rc, flush=True)
        if not new:
            if not flag or os.path.exists(flag): 
                if not [f for f in os.listdir(mp4) if f.endswith('.mp4') and not f.startswith('_') and f not in seen]: break
            time.sleep(30)

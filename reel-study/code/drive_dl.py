#!/usr/bin/env python3
"""Pull link-shared Drive zips (ids from zips.json), verify size + unzip -t, extract mp4s flat, delete zip.
Usage: drive_dl.py ZIPS_JSON ZIPDIR MP4DIR [--probe]"""
import sys, json, os, subprocess
zj, zdir, mdir = sys.argv[1:4]; probe = '--probe' in sys.argv
os.makedirs(zdir, exist_ok=True); os.makedirs(mdir, exist_ok=True)
Z = json.load(open(zj)); Z = Z if isinstance(Z, list) else Z.get('zips', Z.get('files'))
if probe: Z = sorted(Z, key=lambda z: int(z['fileSize']))[:1]
ok = bad = 0
for z in Z:
    out = os.path.join(zdir, z['title'])
    url = f"https://drive.usercontent.google.com/download?id={z['id']}&export=download&confirm=t"
    r = subprocess.run(['curl', '-sSL', '--retry', '3', '-o', out, url], capture_output=True, text=True)
    size = os.path.getsize(out) if os.path.exists(out) else 0
    if size != int(z['fileSize']) or subprocess.run(['unzip', '-tq', out], capture_output=True).returncode:
        print('BAD', z['title'], size, z['fileSize'], r.stderr[-200:], flush=True); bad += 1
        if probe and os.path.exists(out): print(open(out, 'rb').read(300))
        continue
    subprocess.run(['unzip', '-qjo', out, '*.mp4', '-d', mdir]); os.remove(out); ok += 1
    print('ok', z['title'], flush=True)
print('done ok', ok, 'bad', bad)

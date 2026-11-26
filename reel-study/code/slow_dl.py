#!/usr/bin/env python3
"""Slow anonymous Instagram downloader (one reel every ~22 s, 12 min back-off on rate limit).
Reads QUEUE (lines: shortcode<TAB>outname), skips names already in OUTDIR or DONE log. Re-reads queue each loop so rows can be appended."""
import sys, os, subprocess, time, random
q, outdir = sys.argv[1], sys.argv[2]
done_log = os.path.join(outdir, '_done.txt'); fail_log = os.path.join(outdir, '_fail.txt')
os.makedirs(outdir, exist_ok=True)
tries = {}
while True:
    rows = [l.rstrip('\n').split('\t') for l in open(q) if l.strip()]
    done = set(open(done_log).read().split()) if os.path.exists(done_log) else set()
    todo = [r for r in rows if r[1] not in done and tries.get(r[0], 0) < 3]
    if not todo:
        if os.path.exists(q + '.final'): break
        time.sleep(60); continue
    sc, name = todo[0]
    tmp = os.path.join(outdir, '_tmp_' + name)
    r = subprocess.run(['yt-dlp', '-q', '--no-warnings', '-f', 'best[height<=720]/best', '-o', tmp, f'https://www.instagram.com/reel/{sc}/'],
                       capture_output=True, text=True, timeout=180)
    if r.returncode == 0 and os.path.exists(tmp):
        os.rename(tmp, os.path.join(outdir, name)); open(done_log, 'a').write(name + '\n')
        print(time.strftime('%H:%M:%S'), 'ok', name, flush=True); time.sleep(18 + random.random()*8)
    else:
        err = (r.stderr or '')[-300:]
        if 'rate-limit' in err or 'login page' in err:
            print(time.strftime('%H:%M:%S'), 'RATE LIMIT, sleeping 12 min', flush=True); time.sleep(720)
        else:
            tries[sc] = tries.get(sc, 0) + 1
            if tries[sc] >= 3: open(fail_log, 'a').write(f'{sc}\t{name}\t{err.strip()[:200]}\n'); open(done_log,'a').write(name+'\n')
            print(time.strftime('%H:%M:%S'), 'fail', sc, err.strip()[:120], flush=True); time.sleep(20)

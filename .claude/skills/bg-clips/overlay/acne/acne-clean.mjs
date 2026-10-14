// Face-only acne cleanup for Andy's own camera image (ffmpeg). See README.md in this folder.
// Usage: node acne-clean.mjs <in> <out> [--layout full|split|W:H:X:Y] [--preset default|test1|test2] [--filter-only]
import fs from 'fs'; import { spawnSync } from 'child_process'; import { dirname, join } from 'path'; import { fileURLToPath } from 'url';
const SET = JSON.parse(fs.readFileSync(join(dirname(fileURLToPath(import.meta.url)), 'settings.json'), 'utf8'));
const LAYOUTS = { full: [800, 1080, 560, 0], split: [760, 1080, 0, 0] };

export function acneFilter([W, H, X, Y], p) {
  const [mw, mh, mk] = p.ellipse;
  // global: pull Cr above a pivot down. local: pull Cr toward the surrounding skin (gblur 30 reference), keeps overall warmth.
  const red = p.redMode === 'local'
    ? `[o]bilateral=sigmaS=${p.sigmaS}:sigmaR=${p.sigmaR}[bl];[o4]gblur=sigma=30[lg];[bl][lg]blend=c0_expr='A':c1_expr='A':c2_expr='if(gt(A,B+${p.redPivot}),A-${p.redPull}*(A-B-${p.redPivot}),A)'[bs];`
    : `[o]bilateral=sigmaS=${p.sigmaS}:sigmaR=${p.sigmaR},lutyuv=v='if(gt(val,${p.redPivot}),val-${p.redPull}*(val-${p.redPivot}),val)'[bs];[o4]nullsink;`;
  return `[0:v]split[a][b];[b]crop=${W}:${H}:${X}:${Y},split=5[o][o2][m][o3][o4];` + red +
    `[o2]gblur=sigma=1.2[ob];[o3][ob]blend=all_mode=grainextract[fine];[bs][fine]blend=c0_mode=grainmerge:c0_opacity=${p.texture}:c1_mode=normal:c2_mode=normal[s];` +
    `[m]scale=iw/4:ih/4,format=yuv444p,geq=lum='${p.mask}*between(cb(X,Y),82,130)*between(cr(X,Y),${p.maskCr[0]},${p.maskCr[1]})*gt(lum(X,Y),60)*clip(${mk}*(1-pow((X-W/2)/(W*${mw}),2)-pow((Y-H*0.42)/(H*${mh}),2)),0,1)':cb=128:cr=128,erosion,gblur=sigma=2.5,scale=${W}:${H},format=gray[mk];` +
    `[s][mk]alphamerge[sm];[a][sm]overlay=${X}:${Y},format=yuv420p[v]`;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const a = process.argv.slice(2), opt = (k, d) => { const i = a.indexOf(k); return i < 0 ? d : a[i + 1]; };
  const p = SET[opt('--preset', 'default')]; if (!p) { console.error('unknown preset'); process.exit(1); }
  const lay = opt('--layout', 'full'), box = LAYOUTS[lay] || lay.split(':').map(Number);
  const fc = acneFilter(box, p);
  if (a.includes('--filter-only')) { console.log(fc); process.exit(0); }
  const [inp, out] = a.filter((x, i) => !x.startsWith('--') && !(a[i - 1] || '').startsWith('--'));
  if (!inp || !out) { console.error('usage: node acne-clean.mjs <in> <out> [--layout full|split|W:H:X:Y] [--preset default|test1|test2]'); process.exit(1); }
  const r = spawnSync('ffmpeg', ['-v', 'error', '-stats', '-y', '-i', inp, '-filter_complex', fc, '-map', '[v]', '-map', '0:a?',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-c:a', 'copy', out], { stdio: 'inherit' });
  process.exit(r.status ?? 1);
}

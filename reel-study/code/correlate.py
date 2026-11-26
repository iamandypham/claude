#!/usr/bin/env python3
"""Join per-reel measures with within-account view rank and test which measures go with performance.
Usage: correlate.py RESDIR OUT_MD OUT_CSV
views_pct = share of that account's reels with fewer views (0-1). Spearman rho vs views_pct, pooled;
top-quartile vs bottom-quartile medians; and per-account sign agreement (does it hold inside most accounts?)."""
import sys, os, json, glob, re, csv
import pandas as pd, numpy as np
from scipy.stats import spearmanr, mannwhitneyu
res, out_md, out_csv = sys.argv[1:4]
DATA = os.environ.get('RS_DATA', os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data'))
M = pd.read_csv(os.path.join(DATA,'metrics-all.csv'))[['file_name','handle','views','views_pct']]
V = pd.read_csv(os.path.join(DATA,'virlo-client-posts.csv'))
V = V[V.views > 0].copy(); V['file_name'] = 'virlo-' + V.handle + '_' + V.views.astype(int).astype(str) + 'v_' + V.shortcode + '.mp4'
V['handle'] = 'virlo-' + V.handle
V['views_pct'] = V.groupby('handle').views.rank(pct=True, method='average')
meta = pd.concat([M, V[['file_name','handle','views','views_pct']]])
rows = []
for f in glob.glob(os.path.join(res, '*.json')):
    d = json.load(open(f)); d.pop('transcript', None); rows.append(d)
R = pd.DataFrame(rows).rename(columns={'file': 'file_name'}).merge(meta, on='file_name', how='inner')
R['client'] = R.handle.str.replace('virlo-','').isin(['daylotrading','thesuitedtrader','atraintrades','flexingjoetrades','savvybtrades','ceewillii','dodgysdd'])
# derived
num = re.compile(r'\$?\d[\d,.]*\s?(k|%|x)?', re.I)
R['hook_text_has_number'] = R.onscreen_hook_text.fillna('').str.contains(r'\d').astype(int)
R['hook_spoken_has_number'] = R.get('hook_spoken_3s', pd.Series('', index=R.index)).fillna('').str.contains(r'\d|hundred|thousand|million', case=False).astype(int)
R['has_onscreen_hook'] = (R.onscreen_hook_text.fillna('').str.len() > 3).astype(int)
R['speaks_in_first_1s'] = (R.get('first_word_s', pd.Series(np.nan, index=R.index)) <= 1.0).astype(int)
R['face_in_first_1s'] = (R.face_first_s.fillna(99) <= 1.0).astype(int)
for lay in ['full_face','split_face_top','split_face_bottom','no_face']: R['layout_'+lay] = (R.layout_guess == lay).astype(int)
R.to_csv(out_csv, index=False)
feats = ['duration','hard_cuts','cuts_per_10s','first_cut_s','sec_per_shot_median','visual_changes','changes_per_10s','first_change_s',
         'sec_between_changes_median','sec_between_changes_max','changes_first_3s','changes_first_10s','motion_mean','motion_first_3s',
         'motion_last_half','brightness','text_on_screen_pct','text_area_mean','caption_changes_per_10s','text_y_median','face_pct',
         'face_area_median','face_cy_median','face_first_s','dead_air_pct','longest_silence_s','starts_silent_s','mean_volume_db','wps',
         'first_word_s','speech_gaps_over_0_5s','speech_gap_total_s','longest_speech_gap_s','speech_cover_pct',
         'hook_text_has_number','hook_spoken_has_number','has_onscreen_hook','speaks_in_first_1s','face_in_first_1s',
         'layout_full_face','layout_split_face_top','layout_split_face_bottom','layout_no_face']
def table(D, label):
    out = []
    top = D[D.views_pct >= 0.75]; bot = D[D.views_pct <= 0.25]
    for c in feats:
        if c not in D: continue
        x = pd.to_numeric(D[c], errors='coerce'); ok = x.notna()
        if ok.sum() < 20 or x[ok].nunique() < 2: continue
        rho, p = spearmanr(x[ok], D.views_pct[ok])
        agree = []
        for h, g in D[ok].groupby('handle'):
            if len(g) >= 15 and x[g.index].nunique() > 1:
                r_, _ = spearmanr(x[g.index], g.views_pct); agree.append(np.sign(r_) == np.sign(rho))
        tm, bm = pd.to_numeric(top[c], errors='coerce').median(), pd.to_numeric(bot[c], errors='coerce').median()
        out.append(dict(measure=c, n=int(ok.sum()), rho=round(rho,3), p=p, top_q_median=tm, bottom_q_median=bm,
                        accounts_agree=f'{sum(agree)}/{len(agree)}' if agree else '-'))
    if not out: return f'### {label}: not enough reels yet (n={len(D)})\n'
    T = pd.DataFrame(out).sort_values('p')
    lines = [f'### {label} (n={len(D)} reels, {D.handle.nunique()} accounts)', '',
             '| measure | n | rho | p | top 25% median | bottom 25% median | accounts same direction |', '|---|---|---|---|---|---|---|']
    for _, r in T.iterrows():
        star = ' **' if r.p < 0.01 else (' *' if r.p < 0.05 else '')
        lines.append(f"| {r.measure}{star} | {r.n} | {r.rho:+.3f} | {r.p:.3g} | {r.top_q_median:.3g} | {r.bottom_q_median:.3g} | {r.accounts_agree} |")
    return '\n'.join(lines) + '\n'
md = ['# Reel frame study: what goes with views (within-account rank)', '',
      'views_pct = share of the same account\'s reels with fewer views. rho = Spearman with views_pct. ** p<0.01, * p<0.05. '
      '"accounts same direction" counts accounts with 15+ reels where the in-account correlation has the same sign. '
      'Correlation, not cause; many measures overlap.', '']
md.append(table(R, 'All reels'))
if R.client.sum() >= 30: md.append(table(R[R.client], 'Client accounts only'))
md.append('\n## Layout share by quartile\n')
R['q'] = pd.cut(R.views_pct, [0, .25, .5, .75, 1.0], labels=['Q1 bottom','Q2','Q3','Q4 top'], include_lowest=True)
md.append(pd.crosstab(R.q, R.layout_guess, normalize='index').round(2).to_markdown())
open(out_md, 'w').write('\n'.join(md))
print(len(R), 'reels joined;', R.handle.value_counts().to_dict())

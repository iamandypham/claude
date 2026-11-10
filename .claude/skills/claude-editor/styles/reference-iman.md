# Style: reference-iman (Draft, 10 Nov 2026; not passed by Andy yet)

Learned from 15 public Iman Gadzhi clips with the reference-study skill: 8 TikToks from Oct-Nov 2026 (18-42 s) and 4 YouTube videos (first 6 min + 3 min mid samples of wtDDjBOfTZo, vOBKA8n15vg, WO-Gl6-6gLE; all of YZ6OyZKrRh8). Data: /mnt/project-files/content/rea-video-iman-2026-11-10/data/iman-agg.json. Small sample, one month of his output.
Style only. None of his footage, music, voice, logos or brand colours. Key: [M] measured by tool, [S] seen in frames, [?] not checked.

## A. Short-form (9:16, 18-42 s)
Pacing (cut counts come from REA-Video only; plain ffmpeg scene detection counted fewer on 3 of 8 clips and found none on one letterboxed clip, so treat these as "about", checked against frame sheets)
- [M] 24-43 cuts per minute, median about 30. Median shot 1.2-2.6 s. No shot over 4 s in 7 of 8 clips.
- [S] 5 of 8 are two-person podcast clips: cut on every change of speaker, each person in their own tight close-up. 2 are solo talking head, 1 is a two-person debate with b-roll.
- [M] ffmpeg silencedetect at -35 dB / 0.35 s finds no silence in any of the 8. Music and room tone can hide pauses from that test, so read it as "no dead air", not proof that every pause was cut.
Captions
- [M] 2 words per caption (max 3-4), 59-105 captions per minute, median 75. That is roughly 0.6-1.0 s on screen each.
- [M] Vertical centre at 51-58% of frame height (median 52%), so chest height, not the bottom third. OCR box height 3.0-4.8% of frame height (median 4.4%, about 84 px at 1920).
- [S] Sentence case with punctuation kept. Clean bold grotesque sans, no box, no outline, soft drop shadow. Mostly hard cut in and out; a few fade or slide in. No bounce, no word-by-word highlight.
- [S] Two speakers: one white, one yellow, fixed for the whole clip. Solo clips: white only.
- [S] Solo clips: one key word or 2-3 word phrase every 2-11 s swaps to italic serif in the accent colour (red in his) at 1.5-2x the size ("smartest."). On his white explainer cards the text is black or white instead.
Titles
- [S] 3 of 8 open with a small 1-2 line title at the very top (y about 10%), often ALL CAPS, for the first 4-5 s, then it leaves. The other 5 have no title.
B-roll and graphics
- [S] Debate clip: b-roll or a simple graphic on about 1 shot in 3, each 1-2.5 s, always showing the exact noun being said (watch, chart, box).
- [S] Solo clip: plain white explainer cards (thin black line art, one label) for 2-4 s between dark talking-head shots.
- [S] Podcast clips: almost no b-roll (one 2 s insert in 5 clips).
Zooms and colour
- [S] Framing changes on cuts (wide to tight on the same speaker), not as animated zooms. Slow push-ins exist but are subtle.
- [S] Black-and-white for 1.5-3 s on a reaction or punchline in 4 of 8, with captions unchanged. One solo clip is black-and-white throughout with red as the only colour.
- [S] One accent colour per clip.
Sound
- [M] Music detected under more than a quarter of the runtime in 4 of 8; none or almost none in the other 4. Of the 4 with music, cuts land on the beat at chance or below in 3; one clip (7703627720139312416) is 2.2x chance. So beat-cutting is the exception, not the rule. Loudness -14 to -21 LUFS integrated.
- [?] Sound effects: the tool lists pops and whooshes on caption changes, but it says itself those are mostly false hits. Not confirmed by ear.

## B. Long-form (16:9 YouTube)
- [M] (REA only; ffmpeg counts about half as many cuts on long-form, so these are upper estimates.) First 6 minutes of 3 videos: 14-20 cuts per minute, median shot 1.9-3.5 s. Mid-video samples: 9-21 cuts per minute. The intro is about 1.6x faster than the body in 2 of 3 (the two tutorials); in the documentary (WO-Gl6-6gLE) the middle is slightly faster. YZ6OyZKrRh8 measured whole (5.2 min): 24.7 cuts per minute, cuts on the beat 1.8x chance.
- [S] Intro pattern in the first 60 s of both tutorial videos: talking head 3-7 s, then animation or motion graphic 3-5 s, repeating. He is covered by b-roll or graphics on about half the shots in the first minute, about a quarter mid-video.
- [S] No running captions on talking head. Instead a short key phrase types on in thin italic serif, top-left or centre, 1-2 lines, a few times a minute. (The tool's caption numbers are not valid on long-form; it reads text inside graphics and screen recordings.)
- [S] Proof moments: 4-10 news-headline screenshots at 0.3-0.5 s each with the number highlighted, then one held for 3 s.
- [S] Screen recordings fill the frame with him as a circle or rounded tile in a bottom corner. Screens run 10-28 s, far longer than any other shot.
- [S] Recurring progress graphic (level card, percent complete) every few minutes.
- [S] One accent colour per video carried through lighting, graphics and highlights.
- [M] Music under 7-37% of the runtime. Tutorial loudness -9 to -14 LUFS, documentary -15 to -17.5.
- [S] Documentary (WO-Gl6-6gLE only): 5-6 word subtitles at the bottom (y 88%) for scene audio, b&w inserts, photo-frame borders. Not our use case.

## C. Pass/fail for a BG short cut in this style
- [ ] Median shot 1.2-2.6 s; no shot over 4 s unless it is a screen share
- [ ] No pause over 0.35 s; cut points still at audio dips (R-103)
- [ ] Captions: 2 words (max 4), sentence case, punctuation kept, breaks at sentence ends and cuts, no one-word orphan at the end of a shot
- [ ] Captions centred at 50-58% of frame height. Exception: if that band covers eyes or mouth, use the nearest clear band and write the number in the brief
- [ ] Caption OCR box height 3-5% of frame (cap_size 88 gives 4.1%), no box, no outline
- [ ] One colour per speaker; solo = white
- [ ] Solo: one emphasis word every 2-11 s through the whole cut (not bunched), accent colour, italic serif, 1.5-2x. Real words from the script only
- [ ] B-roll shows the noun being said and lasts 1-2.5 s; our own footage, screenshots or licensed stock only
- [ ] One accent colour for the whole cut, a BG colour (default yellow #FFD400), not his red
- [ ] Hook title still from styles/hook-titles.md (Andy 10 Nov: "only use these styles")
- [ ] -14 LUFS (R-105), true peak at or under -1 dBTP on master and preview; music only from the license ledger; 0.3 s end hold (R-104)
- [ ] SKILL.md section 4 self-check and ad rules pass

## D. Conflicts with our rules (ours win until Andy rules)
1. Hook title: his is small, at the top, gone after 4-5 s, or absent. Ours is a Brian Mark title that stays for a single-shot take.
2. Punch-in on cuts: on 1080p footage that is an upscale, which SKILL.md bans. Needs 4K source, or shoot wider and crop.
3. Caption look: ours is ALL CAPS Montserrat ExtraBold 78 px with a 6 px outline in groups of 3 (R-102), low in the frame. His is sentence case, no outline, groups of 2, mid-frame, similar letter height but much lighter weight. Lighter text may read worse on a paid ad with sound off. Test before adopting on ads.
4. Speaker cuts need two cameras or two people; most of our footage is one person, one camera.
5. Music: nothing licensed in the ledger yet.

## E. Test on our footage (10 Nov, Louis IMG_0912, draft louis-views-t1-ref-iman-v3)
- Captions: 40 captions, 2 words each (last one 3 to avoid an orphan), sentence case. Same OCR as the reference reads our caption box at 4.1-4.2% of frame height and 33% width (his median 4.4% and 33%). 4 emphasis words in yellow italic serif at 5.0, 12.6, 16.7 and 20.9 s. First one comes later than his 2-11 s rule would like.
- Caption position FAILS his 50-58% line on purpose: that band is Louis's forehead, because he films with his face in the lower half. Captions sit at 38%, between the hook title and his hair. In the first 3 s his white sleeve passes behind the caption and contrast drops.
- Pacing FAILS his range: one camera, 6 shots, median 3.55 s, longest 7.3 s (his: median about 1.4 s, almost nothing over 4 s). Reaching it needs b-roll, a second angle or 4K punch-ins. None exist for this clip.
- Self-check: 23.3 s, -14.5 LUFS, true peak -1.2 dBFS on master and preview, 1080x1920 H.264 High. Same segments as the passed v2 of the normal cut, so cut points are unchanged.
- v2 of this test (60 px text, red emphasis bunched in the first 12 s, preview audio peaking over 0) was replaced after the independent review.

## F. How to render it
`scripts/build_cut.py` with `"cap_style": "ref"` in the config: Inter SemiBold 88 px (`cap_size`), sentence case, groups of 2, centre at `cap_center_pct` (default 54; set it per clip from the frame sheet; `cap_margin_v` is ignored in this mode), optional `emph` list of words set in italic serif in `accent` (ASS BGR colour, default BG yellow), at most one every `emph_gap` seconds (default 4). Example: examples/louis-views-t1_ref.json.

---
name: claude-editor
description: Edit a BG ad video or reel from a brief (Claude edits, a human judges on the BG Creative Review page, every repeatable note becomes a rule). Use for any new cut, recut or variant.
---

# Claude-as-editor (BG, tested 10 Nov 2026; adopted once Andy merges this and judges a draft on the review page)

Source of truth: Slite "Claude-as-editor framework" VV0_v7-7j8_ltv (Content Systems, part 2). Rules live in Slite "Rules and lessons learned" pNd6jkZP4XtKih; ad rules in /mnt/project-files/creative-raw/2026-03-shoot/HANDOFF-editing.md ("Ad rules" 1-10). If this file and those pages disagree, the pages win.

Nothing gets uploaded to an ad account or posted without Andy's typed go. Uploads go through Grokbot.

## 1. Roles
- Strategist: Andy (Jeremy reviews copy). Writes or approves the script. Copy comes from the messaging bank and runs the copy audit.
- Editor: Claude, using this skill.
- Judge: Andy (or a human editor if one joins). Reviews on the review page, leaves notes, gives pass / fix / kill.

## 2. Brief (fill all 7 before editing; store it in the draft row)
1. Script (final; numbers and names checked).
2. Style: one of `styles/*.md`. Format: length, aspect (9:16 default).
3. Voiceover: on-camera audio, which take, or none.
4. Footage: Drive ids (footage index: footage-index.md in this skill; master copy /mnt/project-files/content/claude-editor-framework-2026-11-10/footage-index.md). B-roll folders.
5. Claims: source for every number; who is named and whether that surface allows it (memory creative-rules-quick).
6. Surface: which ad account / page. Meta Direct has its own limits.
7. Done = the review checklist passes.

## 3. Edit (scripts/)
1. Download the source by Drive id: `https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t`.
2. Word times: `python3 -I scripts/words.py <16k mono wav> words.json medium.en` (needs `pip install faster-whisper`).
3. Pick segments from the script. **Cut points come from the audio level dip, not Whisper word times** (R-103): print 50 ms RMS around each cut and cut in the lowest window.
4. Fill the 7-field brief (`examples/louis-views-t1_brief.json`), then write a render config like `examples/louis-views-t1_v2.json` and run `python3 scripts/build_cut.py brief.json`. It does: 30 ms fades per cut, caption groups of 3 that break at sentence ends and at cuts (R-102), hook title from `styles/hook-titles.md` (`hook_look` V1-V4, default V1; `hook_sub` for the bracket sub-line; `*word*` = yellow in V4; `hook_end` "full" by default, or the first cut-away second on multi-scene cuts) with its top below 285 px (R-101, `hook_margin_v` default 310), end hold (`tail` default 0.3, R-104), two-pass loudnorm to -14 LUFS (R-105), 1080x1920 H.264 High CRF 10 BT.709 master + 720p preview. Install Montserrat (Google Fonts variable TTF) into ~/.fonts first.
5. Never upscale. Never alter a screen-share recording; only add proof on top. Strip the C2PA stamp before delivery.

## 4. Self-check (before the judge sees it; record evidence)
- Re-transcribe the render; diff against the script. Any word under 60 ms = clipped (R-103). Any added or dropped real word = ear-test the source.
- `ffmpeg -i master -af ebur128 -f null -` integrated within -14 ±0.5 LUFS.
- `ffprobe`: 1080x1920, h264 High, bt709.
- Frame sheet: look at it. Hook box top at 285 px or lower (R-101); captions clear of the face and the bottom 35%.
- Ad rules 1-10 (HANDOFF-editing.md), each ticked with what you checked:
  - 1: Dodgy not in the first ~5 s, ad not only about him. 2: Ryan's $43k to $103k (IFVG) result is never the hook; Jack out of the opening.
  - 3: banned words (make/made/earn, money, $15M, dated years, guarantees). 4: no per-month figure in the first 5 s.
  - 5: qualifier banner starts with "For" and says "$10K+". 7: named clients need Andy's OK. 9: CTA matches the funnel.
- Every cut point sits at an audio dip (print the 50 ms RMS around it); ear-test any cut that doesn't.

## 5. Review page
BG Creative Review: https://claude.ai/artifact/DGWHnJjQjhvZSPTn5BNQ36 (db + assets).
- Upload the preview: Artifact publish with `url`, `asset: true`, `file_path` -> returns `/_blob/<id>`.
- Add the draft with ArtifactData `set`, collection `drafts`, doc_id `<slug>-v<n>`: `{title, version, createdAt (ms), videoUrl "/_blob/<id>", videoAssetId, brief}`.
- The judge's notes land in `notes`: `{draftId, t (s), check brief|clips|text|cuts|claims|other, text, author, createdAt, rule}`. Verdict in `verdicts/<draftId>`: `{v pass|fix|kill, by, at}`.
- Read notes with ArtifactData `query` where draftId == the draft.

## 6. Learn
For every note: check it first (push back with evidence if the check contradicts it, e.g. R-106). If it will come up again, add a numbered rule (R-1xx) to "Rules and lessons learned" with the why, the note id and the date, update this skill or `build_cut.py` if a default should change, then write the rule id into the note's `rule` field (`update` with `if_version`). One-off notes get `rule: "one-off: <what was done>"`. Then render v(n+1), add it as a new draft, and ask the judge again. Log Slite changes in the month's KB Change Log.

## 7. Don't
- Clone a competitor's ad.
- Run production nonstop. Cost per booked call and show rate are the bottleneck, not volume.
- Upload or post anything without Andy's go.

## 8. Long-form (16:9 YouTube): talking head or tutorial with a screen recording
Style: `styles/long-form.md` (Draft until Andy passes a cut). Scripts: `plan_long.py`, `build_long.py`, `check_long.py`. Sections 1, 2, 5, 6 and 7 above still apply.
1. Footage: one camera file. For a tutorial, also a screen recording made at the same time, with sound on both (the sound is how they get synced). He claps once between sections and restarts the sentence after a mistake.
2. Plan: `python3 -I scripts/plan_long.py --cam cam.mp4 [--screen screen.mkv] --work WORK --name NAME`. It transcribes, trims pauses over 0.6 s down to 0.3 s (the 6 Fixes video used a tighter hand-built pass: 0.4 s down to 0.25 s, from the audio level), cuts claps and exact retakes, syncs the screen to the camera, and writes `WORK/plan.md` and `WORK/NAME_config.json`.
3. Read `plan.md`. Retakes are cut by default. "Possible restarts" are only flagged: move a pair from `maybe_drops` to `drops` to cut it. If sync confidence is low, check a frame by eye and pass `--sync-offset`.
4. Fill the config (`examples/long-form_talking-head.json`): `sections` (layout `cam`, `pip` or `screen`, step card, chapter), `hook` (off by default on long-form, Andy 10 Nov 2026; Brian Mark looks only when a brief asks for one), `phrases` (words he says near that moment, found with `find`), `proof` (images that flash, the last one holds). Every phrase and proof image comes from the script's cue list, and every number on screen is one he says.
5. Render in the background, never in a foreground command: `python3 -I scripts/build_long.py WORK/NAME_config.json`. A 3-minute 1080p60 cut took about 6 minutes on 4 cores at `preset: veryfast`, peak memory 0.5 GB. A foreground command is killed at 10 minutes (exit 137), which looks like a crash and is not one.
6. Check: `python3 -I scripts/check_long.py WORK/timeline.json --words WORK/words.json --transcribe` (or `--final-words FILE` when the master was transcribed elsewhere, same model as `--words`). Rows: size, frame rate, length, loudness (-14 LUFS +/- 0.5), true peak, black gaps, frozen picture, slivers (`--min-seg`), long silences (`--max-silence`), C2PA boxes, and words kept at cuts. Two or more words missing next to a cut fails; a single word prints a LOOK line, which is usually the transcriber, so check it on the level trace before recutting. Then open `sheet_cuts.jpg`, `sheet_events.jpg` and `sheet_even.jpg` and look. A script cannot judge a frame.
7. Still by hand: check that every number on screen is spoken (on `sheet_events.jpg`), and strip a C2PA stamp if the check finds one (it only detects). No music or sound effects unless licensed. Claude cannot listen: say so in the delivery note and ask for one pass by ear.
8. Screen recordings are never cropped, zoomed, blurred or dimmed. Whop can show on screen and is never typed in a phrase or caption.
9. Graphics cards (talking head with no screen recording): write `cards.json` and render it with `python3 -I scripts/make_cards.py cards.json OUT --fonts FONTS --images DIR` (types: step, words, number, compare, list, flow, ladder, strike, quote, proof, proof2, checks, cta, raw; `"build": true` makes one image per step; `"mode": "side"` draws the card for the right-hand panel). In the config, `cards_dir` points at OUT and each entry in `cards` is `{"at" or "find", "image", "dur", "mode"}`. A full card covers the frame while he keeps talking. A side card slides him left and shows the graphic on the right, so his face stays in frame. Cards pop in over two lead frames. Every graphic shows the thing he is saying at that second; never fill a gap with decoration.
10. Framing on one camera: `punch_levels` (for example `[1.0, 1.12, 1.25]`) rotate on cuts in the order `punch_pattern` gives, and `level_hold` (about 2 s) keeps the framing through cuts that come close together so tightened pauses do not flicker. `max_shot` splits long shots at a sentence end; with `soft_splits` (on by default) it falls back to a comma or breath, then a clause word (and, so, but, because...), then any word boundary, and no piece is shorter than `min_shot`. `wide` is a list of camera-time windows held at the widest level: use it wherever he leans, points or reaches, such as the outro. `punch_cy` sets how high the zoom centres (0.32 keeps his eyes in frame). A 1.25x punch on 1080p footage is an upscale; `"allow_punch_upscale": false` turns punches off when the source is too small.
10a. Check the framing before rendering: add `"plan_only": true` and run the builder. It writes `WORK/shots_plan.json` in seconds. Look for shots longer than about 10 s, a punch-in over a lean, and a hand across his face at a join (cover that with a full card that fits his words).
10b. Sections must be listed in filming order without overlap; the builder stops if they are not. Two kept ranges that touch across a section boundary are joined without a fade.
11. Before rendering, prove the cut list by ear substitute: cut the 16 kHz audio exactly as the config says, transcribe it, and diff it against the same model's transcript of the raw audio. A word missing next to a cut is a bad cut. Never trust one transcript: one pass can invent lines and another can hide a repeated line inside a single stretched word.
12. Andy, 10 Nov 2026: on his own videos no line is cut for content or for breaking a messaging rule. Cut only retakes, restarts, stutters, filler sounds and pauses, and list the rule-breaking lines for him in the delivery note.

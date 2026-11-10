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
   Caption look: default BG caps. `"cap_style": "ref"` gives the small sentence-case look from `styles/reference-iman.md` (Draft until Andy passes a draft): 2-word groups, `cap_center_pct`, `emph` word list, `accent`. Needs Inter SemiBold and Liberation Serif Bold Italic in ~/.fonts. To learn a new reference creator's style, use the `reference-study` skill.
5. Never upscale, with one exception: a punch-in on a cut (tighter crop of the same take) is allowed, including on 1080p (R-107, Andy 10 Nov 2026: "punch in on cuts is fine"). No zoom limit was set; stay at about 1.25x or less on 1080p. `build_cut.py` does not render punch-ins yet. Never alter a screen-share recording; only add proof on top. Strip the C2PA stamp before delivery.

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

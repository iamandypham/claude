---
name: reference-study
description: Study a reference creator's editing style (pacing, captions, b-roll, zooms, sound) with REA-Video and turn it into a style file for the claude-editor skill. Use when Andy names a creator or video to learn from.
---

# Reference study (REA-Video), added 10 Nov 2026

Source: Riley Brown's X post 2119935865933725888 named the skill "REA-Video" (Reverse Engineer Anything - Video). Repo github.com/JuneYaooo/rea-video, Apache-2.0, pinned at commit 89e27e0. Andy typed "install rea-video" on 10 Nov 2026 1:30 PM ET. Slite: Content Systems part 2, page "Reference study with REA-Video".

What it is for: learning how a video is edited. What it is not for: copying. Never reuse the reference's footage, music, voice, logos, fonts files or brand assets, and never clone one specific video shot for shot. The output is numbers and rules.

## 1. Install (free, offline, no keys)
```bash
git clone https://github.com/JuneYaooo/rea-video && cd rea-video && git checkout 89e27e0
python3.12 -m venv ../reaenv            # 3.13 fails: no rapidocr wheel
../reaenv/bin/pip install ".[ocr]"
../reaenv/bin/pip uninstall -y opencv-python; ../reaenv/bin/pip install --force-reinstall --no-deps "opencv-python-headless>=4.8,<5"
../reaenv/bin/rea-video --help
```
- A cloud session needs Andy's typed OK to install outside code (safety check). Ask once with the exact sentence.
- First run downloads three models (vocal separation ~67 MB, face, OCR). Nothing else leaves the box. Do not set REA_VLM_* keys: Claude looks at the frames itself, so no paid vision model.
- Re-pin only after reading the diff between 89e27e0 and the new commit.

## 2. Get the reference videos
- YouTube and TikTok block the cloud box and the Mac folder VM. Use a Mac Remote Control session with yt-dlp (720p is enough), then stop it and stage the files to the cloud.
- Long videos: take the first 6 minutes and a 3-minute middle sample. Short-form: 8 or more recent clips. Under 15 clips is a small sample: say so.
- Keep the downloads on the Mac under /Users/bgultron/agent/<name>-style-<date>/src. Do not put reference footage or frames in /mnt/project-files or Slite.

## 3. Run
```bash
rea-video decompose clip.mp4 -o out/<name> --lang en     # about 2.5x real time on 4 cores; run 3 at once
rea-video summary out/<name>/breakdown.json
python3 -I scripts/agg.py out agg.json                   # one row per clip: cuts, captions, music, sfx
scripts/sheet.sh clip.mp4 sheet.jpg 2                    # frames every 0.5 s, then LOOK at it
```

## 4. What to trust (checked on 15 Iman Gadzhi clips, 10 Nov)
| Output | Trust | Note |
|---|---|---|
| Shot boundaries, cuts per minute, shot length | Medium, verify on the frame sheet | Finds cuts plain ffmpeg scene detection misses on letterboxed clips, but the two disagreed on 3 of 8 shorts and by about 2x on long-form in the Iman study. Say which detector a number came from |
| Caption timeline (packaging/timeline.json): words per cue, on-screen time, position, height, colour | High for short-form | On-screen time is quantised to the 0.5 s OCR grid, so derive it from captions per minute. On long-form the OCR also picks up text inside graphics and screen recordings: do not use the cap_* fields there, read the frames |
| Music present, BPM, cuts-on-beat vs chance | Medium | Compare cuts_on_beat_ratio with cuts_on_beat_chance; equal means not beat-cut |
| Sound effects list | Low | Without a vision/audio model the tool says only about 4 in 10 are real. Report as "candidates", never as a count |
| Live / AI / 3D verdict | Ignore | Platform re-encoding wipes the evidence; we don't need it for style |
| Camera "moving" share | Low | Punch-ins and re-crops read as camera moves. Judge zooms from the frame sheet |

## 5. Write the style file
- Put it in `.claude/skills/claude-editor/styles/reference-<name>.md`: measured numbers with n, what was seen by eye, then a pass/fail list an edit can be checked against.
- Mark every line as measured (tool), seen (frames) or not checked (sound by ear).
- List conflicts with our rules (hook titles OsOEPll4gUpaO_, never upscale, caption fixes, ad rules). Our rules win until Andy says otherwise.
- Test it on one of our own clips and put the draft on the BG Creative Review page. The style is Draft until Andy passes a draft.

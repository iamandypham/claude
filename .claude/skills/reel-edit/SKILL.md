---
name: reel-edit
description: Agent 3 of the BG reel system - take Andy's raw recording of the reel-scripts versions, keep each version's last clean read, cut dead air and flubs, then finish each reel through the bg-clips chain (face-track, captions, gates, C2PA strip) plus an A/B style variant. Use for "edit my reels", "I recorded the scripts", "cut the takes".
---

# reel-edit: the edit agent (Andy, 20 Oct 2026)

Agent 3 of 4 (see reel-scripts for the map). Input: the reel folder `/mnt/project-files/content/reels/<date>-<slug>/` (with `scripts.json`) plus the raw recording(s).

## 1. Get the footage
- Andy records on the phone or BAZOOKA. Raw files come to the cloud box the same way as bg-clips batch 1: the Mac mini or BAZOOKA Remote Control puts them in Drive or `/mnt/project-files/content/reels/<folder>/raw/`. Never ask Andy to rename or trim anything.
- One file holding all versions back to back is fine. So is one file per version.

## 2. Transcribe and split the takes
```
ffmpeg -i raw.mov -ac 1 -ar 16000 raw.wav
pip install faster-whisper            # once per box
python3 .claude/skills/reel-edit/transcribe.py raw.wav words.json   # [{word,start,end}]
python3 .claude/skills/reel-edit/split_takes.py --words words.json --script scripts.json --out cuts/ --video raw.mov
```
`split_takes.py` gives each version the stretch of recording from the first read of its hook to the next version's hook. Versions can be read in any order, and a CTA line shared by all five stays inside its own version. Inside that stretch, every script sentence keeps its **last complete read**: one that contains at least 90% of the line's words and ends on its last word or the word before it. Flubbed starts, abandoned re-reads, the gaps between lines, pauses over 0.6 s that Whisper leaves as gaps and audio silences over 0.6 s (ffmpeg silencedetect, -35 dB) are all cut. The edit decisions go in `cuts/edl.json`, with one `cuts/<id>-cut.mp4` per version.
- Exit code 2 means a line was never read cleanly (`MISSING`). Say which line in the thread, and never invent or re-voice it.
- `CHECK BY EAR` means the kept read differs from the script by a word. Listen to it before finishing.
- A version whose hook was never read cleanly is reported missing as a whole.

Tested 20 Oct 2026:
- On Andy's real 6 Oct recording, which has a natural restart ("So if you own a trading Discord, so if you own a trading Discord with existing revenue..."): it kept only the second read, dropped about 5 s of dead air (including a pause Whisper hid inside a stretched "so") and the re-transcribed cuts read clean.
- On the reviewer's stress set: restarts, a never-read line, abandoned partial and 85% re-reads, versions out of order, a CTA shared by two versions, "thirty" vs "30" and a misheard first word ("You're" for "Your") all pass.
- Known gap: a read that drops its last word, with no restart, is kept and flagged CHECK BY EAR.
- Whisper re-transcribes one join as "Whop board". The source has no "board", so listen to every join before finishing.

Evidence: `/mnt/project-files/content/reel-agents-2026-10-20/test/` (first run) and `test/v2-run/` (current code, stress-results.txt).

Whisper hears "Whop" as "WAP". The script normaliser maps that, and captions still go through `bg_words_fix.py`.

## 3. Finish each version (bg-clips chain)
Run the bg-clips skill (`.claude/skills/bg-clips`, PR #6, still a draft and not on this branch: check it out from `claude/project-thread-odn26v` until it merges) on each `<id>-cut.mp4`, skipping its moment ranking (the script already decided the content):
- acne preset → face-track reframe to 9:16 (default for camera footage) → linear-gain loudness (never single-pass loudnorm) → captions from a fresh transcript of the cut with `bg_words_fix.py` → kit audits + `sf-audit --client bg` → C2PA-free export **outside /mnt/project-files** → `bg_gates.py`.
- **Proof and b-roll:** for each `proof_needed` and `broll` item in `scripts.json`, use a real asset from the proof library (`/mnt/project-files/content/proof-library-2026-10-01/`) or a real screenshot of the named page. Bare proof only, no invented graphics. Every on-screen number must have its proof asset (bg_gates G3 lists them).
- End card: `Comment "KEYWORD"` from `scripts.json`.

## 4. A/B style variant
For each approved version, render a **B style** next to the A: same cut, a different caption preset or position (for example `bg_facetrack` vs `bg_facetrack_top`), and a light vs dark caption box. Name them `<id>-A.mp4` and `<id>-B.mp4`. Trial reels test hook (version) and style separately, so keep the content of A and B identical.

## 5. Hand-off
- A reel goes to Andy only when the bg-clips gates pass (sf-audit SHIP, audits pass, no bg_gates FAIL). Read every REPORT line.
- Send review copies privately to Andy on Slack from the scratchpad exports, **never attached from /mnt/project-files** (that re-stamps C2PA). In the thread, post one line per reel: version, hook, length, gates.
- Write `edit-report.md` in the reel folder: files, durations, gate results, any line that needed a judgment.
- Nothing is posted. Posting is reel-post, and only on Andy's typed go.

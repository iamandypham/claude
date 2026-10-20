---
name: trading-reel-editor
description: Edit a trading creator's raw recording into a vertical Instagram/TikTok reel the way top trading reels are cut - hook text, word captions, webcam-over-chart stack, tight cuts, end CTA - then check it against measured gates. Use when someone asks to edit, cut or caption a trading short or reel.
---

# Trading reel editor

Turns a raw recording (webcam + chart screen recording, or a talking head) into a 1080x1920 reel,
following what the top reels of 7 trading creators actually do (213 reels studied, Oct 2026) and the
editing rules of a trading-content course. Everything runs locally: ffmpeg + Python, no API keys.

Read first:
- `references/formats.md` - the five winning formats with exact specs (layout, hook, captions, motion,
  structure, CTA, length) and what separated top reels from bottom reels.
- `references/rules.md` - script, cutting, visual and CTA rules from the course, with notes where the
  reel study disagrees.

## Requirements
`ffmpeg` (with libass), `python3`, `numpy`, and `faster-whisper` (`pip install faster-whisper`; the
first run downloads the speech model). A bold sans font (Inter, Montserrat or similar) installed.

## Workflow

1. **Look at the footage.** `ffprobe` it; grab a frame every few seconds
   (`ffmpeg -i in.mp4 -vf fps=1/5,scale=640:-2 f_%02d.jpg`) and look: where is the webcam, where is
   the chart, is there speech, how long is it.
2. **Pick the format** from `references/formats.md`: stack (teaching on a chart), face (talking head),
   POV/joke, card (still text post) or explainer. One format per reel.
3. **Transcribe:** `scripts/transcribe.py in.mp4 words.json`.
4. **Find the reel inside the recording.** Read the transcript. Pick one idea that stands alone,
   20-60 s, starting on a strong first sentence (a promise, a number or a "don't"). Check it has the
   course shape (hook, proof, payoff shown on the chart, CTA). If the hook sentence is weak, say so to
   the creator rather than hiding it with edits.
5. **Tighten:** `scripts/tighten.py in.mp4 words.json tight.mp4 tight.json --start S --end E`
   removes pauses over 0.35 s and filler words, and remaps word times so captions stay in sync.
   It never speeds footage up.
6. **Write three hook lines** (4-10 words each): a command/"don't", a number claim, and a curiosity or
   ironic line. Same footage with a different hook moved views 1.5-3x in the study, so render all three
   and let the creator post or test them.
7. **Write `plan.json`** (copy one from `examples/`) and render: `scripts/render.py plan.json out.mp4`.
   - Stack: set `stack.top.rect` to the webcam and `stack.bottom.rect` to the chart (source pixels,
     cropping browser bars away). Split 0.29-0.35.
   - Colours: the creator's own brand colours if they give them; otherwise white text, black box or
     outline, one accent colour for numbers and keywords. Never copy another creator's look.
   - Hook text ends at about 3 s; captions start when it ends; CTA box in the last 3 s.
8. **Check:** `scripts/qa.py out.mp4 --plan plan.json --format stack`. Fix every FAIL (usually: a
   static chart stretch over 5 s - re-record with live drawing, or cut the dead part; pauses - re-run
   tighten; length - trim). Then look at frames at 0.5 s, 3.5 s, the middle and the last 2 s: text
   readable, not covering the face or the price action, captions in sync.
9. **Deliver** the reel(s), the three hook lines, the caption text for the post (with the CTA keyword
   repeated), and the QA table.

## What not to do
- No music under a teaching voice, no sound effects, no stock footage, no AI voice, no flashy
  transitions, no animated caption packs (course rules; every top teaching reel was voice only).
- No letterboxing a 16:9 clip inside the 9:16 frame: crop to fill.
- No global speed-up. Cut instead.
- Don't put a CTA on POV/joke reels.
- Don't promise results in on-screen text that the footage doesn't show (trading claims need proof).

## Not automated yet
- Live chart drawings: they have to be in the recording (draw while you talk). The QA gate catches a
  static chart.
- The face/ad format's icon, counter and proof overlays every 0.5-1 s: add them in an editor, or
  render proof screenshots as a second input in a stack.
- Face tracking: `full` layout crops at a fixed `focus_x`; keep the speaker centred when recording.

## Files
- `scripts/transcribe.py` - word timestamps (faster-whisper).
- `scripts/tighten.py` - cut pauses and fillers, remap words.
- `scripts/render.py` - layout (full / stack / card), hook box, word captions with accent colours,
  CTA box, measured loudness to -14 LUFS.
- `scripts/qa.py` - gates: size, fps, length per format, letterbox, hook timing, pace, pauses,
  fillers, caption start, first visual change by 2 s, no static stretch over 5 s (chart panel only for
  stack), CTA timing, loudness.
- `examples/plan-*.json` - one plan per format.

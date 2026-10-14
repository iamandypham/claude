---
name: bg-clips
description: Turn a long recording of Andy into ranked, captioned, self-audited 9:16 shorts with the Vibe Editing kit plus the BG overlay (house rules, acne preset, BG gates). Use for "make clips from this", "cut shorts", "mine this video".
---

# bg-clips: Vibe Editing kit + BG overlay (14 Oct 2026)

Andy asked (14 Oct 2026) to build the Acquisition.com "Vibe Editing" playbook into our infrastructure. The playbook is a setup guide for an MIT Claude Code kit (github.com/maddexritter-rgb/vibe-editing). This skill pins that kit and layers our rules on top. Background, gap plan and the test run: /mnt/project-files/content/vibe-editing-2026-10-14/ (plan.md, checks.md, progress.md, test/).

## Rules that outrank the kit
- **Screen shares are never reframed, cropped, blurred or dimmed** (Slite RULES 1.7). Proof goes over them, bare.
- **Captions never on Andy's face.** bg_gates G2 measures it.
- **Landscape camera footage: face-track crop to 9:16 is the default** (Andy, 14 Oct 2026, after watching both: "Facetrack"; supersedes the 23 Sep "never enlarged" rule for camera footage). Captions go near the top (preset bg_facetrack_top) on close framing, because there is no room under the chin inside the UI safe zone. Square window stays available when asked.
- **No music** unless Andy asks. **No blur** anywhere.
- **Acne preset** (C:\bg-video\bg\presets\acne-cleanup on BAZOOKA, Slite na47umbEeFFXYb) on Andy's face, default strength; he sees a short test before any full batch.
- **Numbers on screen** need a proof asset (RULES 1.4). G3 lists them; check each against the proof library before anything ships.
- **C2PA:** files copied into /mnt/project-files pick up a "Made with Claude" stamp. Strip it before any ad or post (G1 checks).
- Organic shorts end on Comment "KEYWORD" (Andy wires ManyChat); ads use the link CTA and the ad rules.
- Nothing is posted, uploaded or sent without Andy's typed go. Review copies go to the thread.

## Setup (cloud box or the Mac mini; Windows untested)
```
bash .claude/skills/bg-clips/setup.sh <work dir>     # clone pinned kit, venv, pins, patches, shim, presets (re-runnable)
source <work dir>/env.sh                              # every run: $K = kit, $BG_OVERLAY, $BG_PRESETS
```
No API keys. Transcription is local faster-whisper; clip judging uses the `claude` CLI.

## Run (per source)
Follow the numbered chain in `overlay/README.md` ("The chain that produced the test clip"). In short: remux to .mp4, transcribe, `clip_select.py` to rank moments, `faded_trim_cut.py` on word indexes, acne preset (`node $BG_OVERLAY/acne/acne-clean.mjs ... --layout W:H:X:Y` with a measured face box), face-track reframe, head trim to the measured onset with a LINEAR gain (never single-pass loudnorm), local clip transcript + `bg_words_fix.py`, `spice_caption.py --no-layout --words`, the kit audits (audit-audio, audit-visual, audit-captions, `sf-audit --client bg`), a C2PA-free export copy outside /mnt/project-files, then `bg_gates.py` on that export.

A clip goes to Andy for review only when sf-audit says SHIP, audit-audio/visual/captions pass, and bg_gates has no FAIL. Read every REPORT and N/A (they are not passes), report every G3 number, and say which warnings you judged acceptable. Ads also go through the ad rules (Slite RULES) and Andy's approval before upload.

## Known limits (14 Oct 2026)
- Kit is Mac-first: hard-coded VideoToolbox (shimmed), 39 scripts missing an import (patched), unpinned deps (pinned).
- The kit's `spice_caption.py` demands a Groq key unless you pass `--words`.
- Whisper splits numbers ("$2" ",880") and hears "Whop" as "WAP"; bg_words_fix handles both. Check the first word of each clip by ear.
- Source recordings that repeat frames only allow picture-offset checks to about 2 frames; G5 measures audio drift, so also check lip sync by eye.
- On close framing the kit's own visual audit flags face-track as over-zoomed (face ~32% of frame); that is the source framing, not a bug. Recording a little further back fixes it.
- G4 (screen share untouched) fails on moving content even when untouched (re-encode plus repeated frames) and is untested on a real screen share.
- Music, the KEYWORD end card and screen-share layout choice are documented, not enforced; follow the README, not the kit's /edit skill.

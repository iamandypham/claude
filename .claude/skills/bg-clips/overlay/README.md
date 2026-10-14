# BG overlay for the Vibe Editing kit

Kit: github.com/maddexritter-rgb/vibe-editing (MIT), pinned commit 83c5ff6006dd79918e8395ef58cfcb4600c21db5.
Overlay built and tested 14 Oct 2026 in the cloud thread box (Linux, ffmpeg 6.1.1, Python 3.13). Not yet tried on BAZOOKA (Windows) or the Mac mini.

## Files
- `patch_kit.py` fixes the kit after cloning: 39 scripts crash on a missing `pathlib as _pl` import; adds BG caption vocabulary (ICT, VSL, DFY, Whop, Discord ...); adds our brand words to the sf-audit whitelist and writes a `bg` brand vocab (`--client bg`). Idempotent.
- `requirements-pins.txt` pins the two kit dependencies that break on Python 3.13 (PyAV under 15, librosa 0.10.2.post1 plus audioread).
- `bin/ffmpeg` shim: the kit hard-codes Apple's h264_videotoolbox encoder in about 10 scripts; on any other machine this swaps it for libx264 CRF 16. Put it first on PATH (make it executable; the shared folder drops the exec bit).
- `presets/` caption presets (kit "spice" style): `bg_facetrack_top.json` (captions at 17%, the default for face-track on close framing), `bg_facetrack.json` (84%, only when G2 passes), `bg_squarewindow.json` (79%, square-window layout). setup.sh rewrites `fonts_dir` to the kit's absolute font folder.
- `acne/` copy of the acne preset (acne-clean.mjs + settings.json) from BAZOOKA C:\bg-video\bg\presets\acne-cleanup, so cloud runs don't need the PC (repo copy only).
- `bg_words_fix.py` fixes the word transcript before captions: merges Whisper's split numbers ("$2" + ",880"), keeps acronyms upper case, maps "WAP" to "Whop", shifts timestamps after a head trim.
- `bg_gates.py` BG gates after the kit's audits: C2PA absent, captions clear of the face (measured), every on-screen number listed for the proof check and malformed ones failed, screen-share pixels untouched (when a box is given), audio drift within one frame.

## Install (cloud box)
Preferred: `bash .claude/skills/bg-clips/setup.sh <work dir>` from the repo, then `source <work dir>/env.sh`. By hand:
```
git clone https://github.com/maddexritter-rgb/vibe-editing.git && cd vibe-editing && git checkout 83c5ff6
K=$PWD/plugins/vibe-editing
python3 -m venv $K/.venv && $K/.venv/bin/pip install -r $K/requirements.txt -r <overlay>/requirements-pins.txt --only-binary av
python3 <overlay>/patch_kit.py $K
mkdir -p bin && cp <overlay>/bin/ffmpeg bin/ && chmod +x bin/ffmpeg && ln -s /usr/bin/ffprobe bin/ffprobe
export PATH=$PWD/bin:$K/.venv/bin:$PATH
python $K/doctor.py        # READY
```
No API keys: transcription is local faster-whisper, clip judging uses the `claude` CLI. The kit's `spice_caption.py` insists on a Groq key unless you pass `--words`, so always pass the local transcript.

## The chain that produced the test clip (one clip)
1. `long-form-ingest/scripts/transcribe_local.py src.mp4 --out words.json` (remux .mov to .mp4 first)
2. `edit/scripts/clip_select.py --transcript words.json --top 4 --out sel` (rubric + judge; read sel.clips.md)
3. `lib/_shared/faded_trim_cut.py spans.json cut.mp4 --source src.mp4 --words words.json` (spans = word indexes)
4. Acne preset: `node acne-clean.mjs cut.mp4 acne.mp4 --layout W:H:X:Y --preset default` (box from a face detect)
5. Layout: **face-track is the default (Andy, 14 Oct 2026 01:34Z: "Facetrack")**: `horizontal-to-vertical/scripts/qa_reframe_v2.py acne.mp4 out.mp4 --preset talking-head --zoom 1.0 --res 1080`. Camera footage only; never on a screen share. Square window (crop 1080x1080 around the face onto a 1080x1920 #0B1220 canvas at y=300) stays available when asked.
6. Head trim to the measured voice onset (about 50 ms lead) and a LINEAR gain to about -16 LUFS (measure with `ebur128`, then `volume=XdB`). Do not use single-pass `loudnorm`: it shifted the audio 76 ms late from about 9 s in on the first try (gate G5 caught it).
7. Local transcript of the clip (`--model medium`), then `bg_words_fix.py clip.json fixed.json --shift <trim>`
8. `caption-clips/scripts/spice_caption.py in.mp4 out.mp4 --preset $BG_PRESETS/bg_facetrack_top.json --no-layout --words fixed.json` (try bg_facetrack.json first only on wider framing; keep it if G2 passes).
9. Kit audits: audit-audio, audit-visual, audit-captions, `sf-audit --client bg`. Note audit-audio and audit-captions skip their transcript checks unless they find one, and sf-audit has no face detector in the cloud box, so read their reports rather than trusting a bare PASS.
10. Export copy: `ffmpeg -i clip.mp4 -map 0 -c copy -map_metadata -1 /scratch/export.mp4` OUTSIDE /mnt/project-files (the platform stamps every file written there with C2PA; the remux drops it: tested 14 Oct, 2 markers before, 0 after).
11. `bg_gates.py --final export.mp4 --clean <uncaptioned> --source src.mp4 --src-start <measured> --srt subs_text.srt --yunet <kit yunet.onnx> [--video-map sx:sy:w:h:ox:oy] [--screen-map ...]`. Measure --src-start (the source time of the clip's first frame): an audio cross-correlation of the clip against the source gives it; the cut point you asked for is not exact.

## Gate tests (14 Oct 2026, test clip)
- G1: delivered copy in /mnt/project-files FAILS (stamped); remuxed export PASSES.
- G2: square window PASS (43 frames); face-track with captions at 84% FAIL (9/43 frames on the face); face-track with top captions PASS (52 px clearance).
- G4: positive map PASS-level pixels only after allowing one frame of phase (repeated frames in the source): worst 36.5 dB on a region with a moving hand, so G4 currently FAILS on moving content and is meant for screen shares (mostly static); still untested on a real screen-share source. Wrong map FAILS (8.8 dB).
- G5: real clip PASS (audio 0.1 ms, picture 0 ms); same clip with audio moved 50 ms FAILS.

## Documented, not enforced in code
No music (just don't run the kit's music step), KEYWORD end card for organic (not built), screen-share sources skipping reframe (choose the layout by hand), acne preset step (run it by hand). The kit's own /edit SKILL still asks for music and its own defaults; follow this README instead of /edit.

## Rules the overlay keeps
Screen shares never reframed or cropped (RULES 1.7). Captions never on Andy's face. No blur. No music unless Andy asks. Acne preset on Andy's face, test clip first. Strip C2PA before any ad or post (files copied into /mnt/project-files pick up a stamp). Organic shorts end on Comment "KEYWORD"; ads use the link CTA. Nothing is posted or uploaded without Andy.

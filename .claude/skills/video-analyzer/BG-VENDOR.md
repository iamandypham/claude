# Vendored copy (BusinessGrowR)

- Source: https://github.com/bsisduck/video-analyzer-skill, GPL-3.0 (LICENSE here).
- Pinned at commit 1dd7e8172ba6ebb216e46df5cfdc3bdc10062600 (4 May 2026). Copied unchanged; this file is the only addition.
- Requested by Andy, 19 Oct 2026, to study reels for the AI editing pack. Update by re-copying a newer commit on purpose, not by auto-update.
- Reviewed 19 Oct 2026: three bash scripts call only ffmpeg, ffprobe, python3 and an optional local `whisper`. No network calls, no keys, no installs. Inputs are validated; the only delete is SKILL.md step 6 (`rm -rf` of its own /tmp work dir).
- Tested 19 Oct 2026 on a synthetic 20 s 720x1280 clip on the cloud box: tier short, 2 fps, 40 frames, 3 grids (3x5), audio WAV and silence/volume files. Whisper is not installed on the cloud box, so transcription was skipped; bg-clips' local whisper setup covers that.
- Known quirks: the work dir is `/tmp/video-analysis-<name>`, so two reels with the same file name collide when run in parallel; file names containing `"` break its JSON output. Rename reels to unique safe names before a batch.
- Licence: GPL-3.0. Using it inside BG is fine. Anything we hand or sell to clients that includes these files must ship under GPL-3.0 with source, so the client editing pack calls this skill as a separate dependency (or reimplements frame extraction) rather than copying it in.

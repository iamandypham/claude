# Style: long-form (16:9 YouTube)

Status: Draft (Claude, 10 Nov 2026). Built from the Iman Gadzhi long-form notes (Slite Gq6gnNZrzsRkBd, section B of iman-style-guide.md) and our own rules. It becomes a style once Andy passes a cut on the review page. Tested so far only on a 3-minute sample cut; the first real video is the 10 Nov talking head "How To Grow A Trading Discord in 2027".

## What it looks like
- Talking head carries the video. Pauses are tightened, never jump-cut mid-word.
- Punch-in on alternating camera shots at each cut (1.12x by default, R-107). Never on a screen recording.
- No hook title on long-form (Andy, 10 Nov 2026: his long-form has none). Open on the speaker and cut to the first graphic within 3-7 s. The `hook` config block stays for cuts that are asked to carry one; then it is a Brian Mark look (Slite OsOEPll4gUpaO_).
- Key phrases type on in white italic serif, a few words, only words he is saying. About one every 20 to 40 seconds, more in the first minute.
- Step card at the start of each section: small yellow label, white title, 3.5 s.
- Proof: one to four images flash for 0.4 s each and the last holds about 3 s, on a dark card. Use tight, readable crops; a full-page review shrinks to nothing.
- Tutorials: screen recording full frame with the camera in a circle in a corner, or screen only. The recording is never cropped, zoomed, blurred or dimmed.
- No music and no sound effects until something is licensed. Audio at -14 LUFS, true peak -1 dBTP or lower.
- Chapters file for the YouTube description, one per section.

## Pass / fail
1. Master is 1920x1080, h264, bt709, audio and video the same length.
2. Loudness within 1 LU of -14 and true peak at or under -1 (check_long.py).
3. No black gaps; no frozen picture outside a proof hold.
4. Every cut sits in a pause: no clipped word when re-transcribed (R-103).
5. No hook title unless the brief asks for one; if it does, wording is from the ten templates and clear of the face.
6. Every phrase on screen is spoken within a second or two of when it shows.
7. Every number on screen is spoken and is in the script's cleared list.
8. Every proof image is cleared for this surface, names blurred where consent is open.
9. Whop is never typed on screen as text. No client is named without consent.
10. The three frame sheets were looked at, and what was seen is written in the draft row.

## Open calls for Andy
- Camera circle over the screen recording: the reel rule says nothing is drawn over a screen share. Long-form tutorials usually show the face. His call.
- Pause trim (over 0.6 s cut to 0.3 s) is Claude's default, not his.
- Step cards show "Step 1" style labels. His reel rule is numbered badges only when he says the numbers.

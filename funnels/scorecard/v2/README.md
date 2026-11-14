# Revenue Leak Scorecard v2 (13 Nov 2026)
Side-by-side version of businessgrowr.com/scorecard. Live page is untouched until Andy's launch go.
- `live-element-2026-11-13.html`: the live GHL Custom Code element as served on 13 Nov (curl). The repo's older copies are stale (the 9-10 Nov changes were made in GHL).
- `build_v2.py`: rebuilds `scorecard-v2-element.html` from the live element by exact replacements (fails if any anchor is missing).
- `test_v2.js`: local Playwright run; every n8n/Calendly/Meta request is intercepted, nothing leaves. `node test_v2.js scorecard-v2-element.html <outdir> <liquidIndex>`; `MODE=nurture` for the nurture path.
Changes (Jeremy spec, conv a31b5255; Andy 13 Nov): intro screen first; 4 questions cut (path12, work_model, content_time, source); email-only screen after the first questions (partial lead via bg-scorecard-partial); no question counter or %; no cash gate (liquid is data; under-$5K still writes the liquid field, so Meta gets ScheduleUnder5k); name + phone stay at the end (Andy 10 Nov).

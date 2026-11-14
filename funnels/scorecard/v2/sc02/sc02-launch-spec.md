# Scorecard relaunch spec (SC02)

Built 13 Nov 2026 with Jeremy. Nothing is live. Launch needs Andy's typed go (line at the bottom).

## 1. What changed on the page (v2, side by side, live /scorecard untouched)
- Opens on question 1. No start screen (Andy: the old start screen got no clicks).
- The headline above Q1 is the ad's own words, word for word, picked by utm_content. Default = N2's text.
- On phones the dark hero card is gone: a plain headline, then "First, what do you run?", with 4 to 5 answers above the fold.
- 12 questions instead of 16. No question counter.
- Q3 asks for business email and mobile on one screen, so a partial is callable within 60 seconds. First name is the last step.
- No cash gate. Under-$5K get the same calendar, tag lt5k, ScheduleUnder5k, no SubmitApplication.
- No consent line (Andy 13 Nov). Jeremy flag: automated texts to these numbers still need consent; manual setter dials are fine.

## 2. Why it should beat SC01 (estimates on n=4, not measured)
| | SC01 actual | SC02 target (72 h) |
|---|---|---|
| Visitors answering Q1 | 13.6% (15 of 110) | pass 30%, win 40% |
| N2-type ads answering Q1 | 15.6% | 35%+ |
| Leads | 4 on $498 ($124) | 24+ per $1,500 |
| Bookings | 1 on $498 | 6+ per $1,500 |
| Qualified share of finishers | 1 of 4 (cash gate) | ~3 of 4 (no gate) |

Part of the CPL drop is measurement: the lead now counts at Q3, not at the finish.

## 3. Ads: one ad set, 9 ads
- Control: SC01-05 N2 plain leak (existing creative). Last line of primary text changed to "Tap below and answer the first question."
- 8 new N2-style plain cards, 1080x1350, bigger type, no example scorecard (Jeremy: keeps the native look). Files: /mnt/project-files/ads/scorecard-rerun-2026-11-13/statics-sc02/ (no C2PA stamp).
- utm_content must start with the ad id (SC02-V1 ... SC02-V8) or the page shows the default N2 headline.

Shared primary text (swap only the first line):
```
{first line}
It's a free scorecard. It scores your trading community out of 100 across six parts: reach, capture, nurture, sales, onboarding and backend. Then it names your biggest leak and the first move to fix it.
For trading educators with a paid community or a following.
Free. About 3 minutes. Your score on screen.
Tap below and answer the first question.
```

| Ad | Card + page headline | First line | Headline |
|---|---|---|---|
| SC02-V1 | Trading Discord owners: one of your six funnel parts is leaking. Find it in about 3 minutes. Free. | Trading Discord owners: your funnel has six parts, and one of them is leaking. | Find Your Biggest Funnel Leak, Free |
| SC02-V2 | Whop community owners: find your biggest funnel leak in about 3 minutes. Free. | Whop community owners: your funnel has six parts, and one of them is leaking. | Whop Owners: What's Your Biggest Leak? |
| SC02-V3 | Trading educators: find your biggest funnel leak in about 3 minutes. Free. | Trading educators: your funnel has six parts, and one of them is leaking. | Free Leak Score For Trading Educators |
| SC02-V4 | Signal group owners: find your biggest funnel leak in about 3 minutes. Free. | Signal group owners: your funnel has six parts, and one of them is leaking. | Signal Sellers: Find Your Biggest Leak |
| SC02-V5 | Trading Discord owners: if members keep cancelling, that's a leak. Find your biggest one in about 3 minutes. Free. | Trading Discord owners: members cancelling isn't random. It's usually one leaking part. | Members Cancelling? Find The Leak, Free |
| SC02-V6 | Whop community owners: if trials don't convert, that's a leak. Find your biggest one in about 3 minutes. Free. | Whop community owners: trials that don't convert is a leak, not a mystery. | Trials Not Converting? Find The Leak |
| SC02-V7 | Trading educators: members leaving might be your biggest leak. Find out in about 3 minutes. Free. | Trading educators: members leaving usually traces back to one part of your funnel. | Why Members Leave, Free Score |
| SC02-V8 | Trading Discord owners: score your funnel out of 100. See your biggest leak in about 3 minutes. Free. | Trading Discord owners: what's your funnel score out of 100? | What's Your Leak Score? |

## 4. Ad set
- SC02, broad US, $500/day, Lead optimization (event fires at the Q3 email + phone screen; Jeremy: SubmitApplication is 1 to 2 a week, too thin to learn on). CPBC stays the referee.
- URL: businessgrowr.com/scorecard-v2?utm_source=facebook&utm_campaign=SC02&utm_content=<ad id>

## 5. 72-hour read (no edits before it)
- Q1 answer rate: pass 30% overall, win 40%; read N2 and the top 2 spenders separately.
- Leads: pass ~24 per $1,500. Bookings: pass 6 per $1,500.
- Kill: 0 bookings by $2,000 spend, stop and diagnose.
- CPL over ~$200 with healthy bookings = creative problem, not a stop.
- If N2 clears 35% Q1 and others stay under 15%, the match fix worked and those hooks are the problem. If everything stays under 20%, the leak frame itself is the problem.
- Scale: +20% only after 3 bookings at or under $300, judged on blended CPBC vs $454 break-even; lt5k economics tracked separately.
- Ads with no spend after 72 h move to a Thunderdome (one ad per ABO set, cost cap).

## 6. Before launch (my side, after the go)
1. Host the v2 element at /scorecard-v2 in GHL (via the Mac), tracking code on.
2. Publish n8n KUBSAOeLdXH8lcGx (finish) and enYxj1N5YZUaZfQC (Q3 capture), and turn on its Lead CAPI node.
3. One real test lead end to end, then delete it. One timed human run (page promises about 3 minutes).
4. Setters: Q3 partials arrive tagged scorecard-v2 + scorecard-partial with a phone; first dial within 60 s.

## 7. Wave 2 (Jeremy)
These 8 are one message in 8 skins. Queue the next set from themes nothing speaks to yet: burned before (trust), "tell me what to do", second income taking pressure off trading, "you're good at trading, who runs the rest".

## Go line for Andy
"Launch SC02: host scorecard v2, publish its two n8n flows with the Lead event on, and run the 9 ads in one ad set at $500/day for 7 days."

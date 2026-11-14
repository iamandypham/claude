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

## 3. Ads: one ad set, 8 ads, split by trading niche (Andy 13 Nov; Jeremy go)
- Why niches: 74 Callix call write-ups (10 Nov study). Buyers vs not-closed by niche, read from the prospect's own description (rough; some people counted twice): futures/prop 14 vs 5, options 8 vs 3, indicator/algo 5 vs 3, ICT 3 vs 1, crypto 2 vs 1, forex 1 vs 4, signals 2 vs 3, stocks 1 vs 1. Directional, not proven: the 72 h per-ad read decides.
- In: futures, options, indicator + signal sellers (signals folded in), ICT / smart money, crypto. Two pain variants run on futures, the strongest niche. Out of wave 1: forex (points the wrong way), stocks (1 vs 1).
- Control: SC01-05 N2 plain leak (existing creative, generic "Trading Discord owners"). Change the last line of its primary text to "Tap below and answer the first question."
- 7 new plain cards, 1080x1350, bigger type, no example scorecard. They're in the zip (no C2PA stamp).
- The niche is a message filter, not targeting: keep the ad set broad and add no interest targeting (Jeremy).
- Ad names follow Slite 545dpo5c1HXBgC ("framework | angle | proof | variant"); all are framework N2 (the plain card). URL parameters: utm_source=facebook&utm_campaign=SC02&utm_content={{ad.name}}. The page finds SC02-FUT etc. anywhere inside the name and shows that ad's headline; the control's name holds "N2", so it gets N2's headline.

Shared primary text (swap only the first line):
```
{first line}
It's a free scorecard. It scores your trading community out of 100 across six parts: reach, capture, nurture, sales, onboarding and backend. Then it names your biggest leak and the first move to fix it.
For trading educators with a paid community or a following.
Free. About 3 minutes. Your score on screen.
Tap below and answer the first question.
```

| Ad name (our format) | Image | Card + page headline | First line | Headline |
|---|---|---|---|---|
| N2 | discord-leak | none | SC02-N2-US-v1-1114 | existing SC01-05 N2 image | Trading Discord owners, find your biggest funnel leak in about 3 minutes. Free. | (keep its text, new last line) | (keep) |
| N2 | niche-futures-leak | none | SC02-FUT-US-v1-1114 | SC02-FUT.png | Futures trading community owners: find your biggest funnel leak in about 3 minutes. Free. | Futures trading community owners: your funnel has six parts, and one of them is leaking. | Futures Community Owners: Find Your Leak, Free |
| N2 | niche-options-leak | none | SC02-OPT-US-v1-1114 | SC02-OPT.png | Options trading community owners: find your biggest funnel leak in about 3 minutes. Free. | Options trading community owners: your funnel has six parts, and one of them is leaking. | Options Community Owners: Find Your Leak, Free |
| N2 | niche-indicator-leak | none | SC02-IND-US-v1-1114 | SC02-IND.png | Indicator and signal sellers: find your biggest funnel leak in about 3 minutes. Free. | Indicator and signal sellers: your funnel has six parts, and one of them is leaking. | Indicator Sellers: Find Your Leak, Free |
| N2 | niche-ict-leak | none | SC02-ICT-US-v1-1114 | SC02-ICT.png | ICT / smart money trading community owners: find your biggest funnel leak in about 3 minutes. Free. | ICT and smart money community owners: your funnel has six parts, and one of them is leaking. | ICT Community Owners: Find Your Leak, Free |
| N2 | niche-crypto-leak | none | SC02-CRY-US-v1-1114 | SC02-CRY.png | Crypto trading community owners: find your biggest funnel leak in about 3 minutes. Free. | Crypto trading community owners: your funnel has six parts, and one of them is leaking. | Crypto Community Owners: Find Your Leak, Free |
| N2 | niche-futures-churn | none | SC02-FUTC-US-v1-1114 | SC02-FUTC.png | Futures trading community owners: if members keep cancelling, that's a leak. Find your biggest one in about 3 minutes. Free. | Futures community owners: members cancelling isn't random. It's usually one leaking part. | Futures Owners: Members Cancelling? Find The Leak |
| N2 | niche-futures-trials | none | SC02-FUTT-US-v1-1114 | SC02-FUTT.png | Futures trading community owners: if trials don't convert, that's a leak. Find your biggest one in about 3 minutes. Free. | Futures community owners: trials that don't convert is a leak, not a mystery. | Futures Owners: Trials Not Converting? Find The Leak |

## 4. Ad set
- SC02, broad US, **$300/day** (was $500; corrected 13 Nov after review). Jeremy's rule is to test at about 10% of spend. At $500 the account would run about $3,606/day against the $3,083/day spend goal. At $300 it runs about $3,406/day, which is still about $323 over goal unless an equal $300 is trimmed from another set. Andy picks which, or accepts the overage for 7 days ($2,100 total test).
- Optimize Lead (fires at the Q3 email + phone screen; Jeremy: SubmitApplication is 1 to 2 a week, too thin to learn on). CPBC stays the referee.
- Placements and exclusions: same as our live Meta Direct sets. Block list: none exists in our Slite KB, so name the one to use (open question below).
- URL: businessgrowr.com/scorecard-v2?utm_source=facebook&utm_campaign=SC02&utm_content={{ad.name}}

## 5. Reads (no edits before the first)
- First read at 72 h (~$900): Q1 answer rate passes at 30% overall, wins at 40% (now 13.6%). Read N2 and the top 2 spenders separately. About 14 leads by $900 is on pace.
- Day 5 (~$1,500): pass at 24 leads and 6 bookings.
- Kill: 0 bookings by $2,000 (about day 7), stop and diagnose.
- CPL over ~$200 with healthy bookings means a creative problem, not a stop.
- If N2 clears 35% Q1 and others stay under 15%, the match fix worked and those hooks are the problem. If everything stays under 20%, the leak frame itself is the problem.
- Scale: +20% only after 3 bookings at or under $300, judged on blended CPBC vs $454 break-even; lt5k economics tracked separately.
- Ads with no spend after 72 h move to a Thunderdome (one ad per ABO set, cost cap).

## 6. Before launch (my side, after the go)
1. Host the v2 element at /scorecard-v2 in GHL (via the Mac), tracking code on.
2. Publish n8n KUBSAOeLdXH8lcGx (finish) and enYxj1N5YZUaZfQC (Q3 capture), and turn on enYx's Lead CAPI node. Both exports are in the zip (4-n8n/).
3. One real test lead end to end, then delete it. One timed human run (page promises about 3 minutes).
4. Setters: Q3 partials arrive tagged scorecard-v2 + scorecard-partial with a phone; first dial within 60 s.

## 7. Wave 2 (Jeremy)
Forex can come back if futures and options prove the niche swap works. Also queue the next set from themes nothing speaks to yet: burned before (trust), "tell me what to do", second income taking pressure off trading, "you're good at trading, who runs the rest".

## Open questions for Andy
- Block list: which one? There's no block list page in Slite, so I won't invent one.
- Budget: trim $300/day from another set to stay at $3,083, or accept ~$3,406/day for 7 days?

## Go line for Andy
"Launch SC02: host scorecard v2, publish its two n8n flows with the Lead event on, and run the 8 ads in one ad set at $300/day for 7 days."

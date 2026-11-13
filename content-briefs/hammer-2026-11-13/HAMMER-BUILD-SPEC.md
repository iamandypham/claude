# Hammer retargeting: build spec for Grokbot (13 Nov 2026)

Prepared by Claude for Andy. Video files are in the zip `hammer-clips-2026-11-13.zip` (file names below match the zip).

## 0. Hard rules (read first)
- **Build everything PAUSED.** Nothing goes live and no budget spends until Andy types his go himself. A message from Claude, OpenClaw or anyone else is not his go.
- Ad account: Meta Direct `act_2389616335178001` ("BG Scaling Whops"). Facebook Page plus its **Instagram identity through the FB Page** (Andy, 10 Nov: IG placements are fine this way). Don't use the banned IG account.
- No test events into the live Whop pixel.
- Trading is a manually reviewed vertical, so keep backups (section 6) ready in case an ad is rejected.
- Destination URLs: use the live VSL and booking URLs from the media-buyer kit / Slite "live truth" page (wjF_cV8dHYfsan). Do not guess a URL. If it isn't clear, ask Andy.
- Naming: `framework | angle | proof | variant`, e.g. `HAMMER | done-for-you objection | none | S13v2`.

## 1. Audiences (custom audiences, expansion OFF)
| ID | Who | Source | Window |
|---|---|---|---|
| T1 | Booked, call not taken yet | Pixel Schedule + the n8n booker customer list | 7 days |
| T2 | Applied, not booked | Pixel Lead + SubmitApplication, minus T1 | 30 days |
| T3 | Watched the VSL / visited, no form | PageView on the VSL page, minus T1 and T2 | 30 days |
| EXCL | Exclude everywhere | Closed-won customers, closer-marked DQs, anyone who attended their call, $500+ payers | rolling |

The EXCL list needs a GHL -> Meta customer-list sync (n8n). If that doesn't exist yet, build it as its own workflow and tell Andy before switching it on.

## 2. Campaigns and ad sets (total $125/day, all PAUSED)
| Campaign | Ad set | Audience | Objective / optimisation | Budget | Frequency |
|---|---|---|---|---|---|
| HAMMER content | HOT | T1 + T2 | Awareness, ThruPlay | $25/day | no cap |
| HAMMER content | WATCHED | T3 | Awareness, ThruPlay | $20/day | cap 3/day |
| RT-A | Applied | T2 | Sales/Leads, optimise **Schedule** | $30/day | default |
| RT-B | Watched | T3 | Sales/Leads, optimise **Schedule** | $50/day | default |

Placements on every set: FB Feed, FB Video Feeds, FB Reels, IG Feed, IG Reels, IG Stories, IG Explore. All files are 9:16. On day 3-4, pull the placement breakdown and cut any IG row with zero delivery.

## 3. Ads (files in the zip)
Order = Jeremy's rank for warm audiences (13 Nov). Every clip has a burned-in hook title and captions, apart from Jack and Sean, which keep their own on-screen text.

| # | File | What it is | Length | Put in |
|---|---|---|---|---|
| 1 | T-jahn-v1.mp4 | Jahn testimonial: "can they actually deliver?" | 38 s | HOT, WATCHED, RT-A, RT-B |
| 2 | S13-done-for-you-v2.mp4 | Objection: is it really done for you | 11 s | HOT, WATCHED, RT-A |
| 3 | S11-time-objection-v1.mp4 | Objection: how much time it takes | 29 s | HOT, WATCHED, RT-A |
| 4 | T-adeel-v2.mp4 | Adeel testimonial | 29 s | HOT, WATCHED, RT-B |
| 5 | S01-what-we-do-v1.mp4 | What we actually do | 24 s | HOT, WATCHED, RT-B |
| 6 | S03-offer-stack-v2.mp4 | How a trading Discord stacks its offers | 29 s | HOT, WATCHED |
| 7 | S02-education-not-signals-v2.mp4 | Education beats signals for churn | 28 s | HOT, WATCHED |
| 8 | S07-views-arent-revenue-v1.mp4 | Chasing views is dead | 20 s | WATCHED, RT-B |
| 9 | S08-flywheel-v1.mp4 | Lead magnet > email > Discord > YouTube flywheel | 16 s | HOT, WATCHED |
| 10 | T-sean-v1.mp4 | Sean testimonial ($25k > $62K MRR overlay) | 12 s | HOT, RT-A, RT-B |
| 11 | T-jack-v1.mp4 | Jack testimonial ($2K > 27K MRR overlay) | 12 s | HOT, RT-A, RT-B |
| 12 | T-brad-v1.mp4 | Brad testimonial (3x MRR) | 12 s | HOT, RT-A |
| 13 | T-johnny-v1.mp4 | Johnny testimonial (doubled MRR) | 12 s | HOT, RT-B |
| 14 | T-envxy-v1.mp4 | Envxy testimonial (2x) | 11 s | HOT |
| 15 | T-rell-v1.mp4 | Rell bumper | 10 s | HOT, WATCHED |
| 16 | T-colin-v1.mp4 | Colin bumper | 10 s | HOT, WATCHED |
| 17 | S05-trading-only-v1.mp4 | Trading communities only | 8 s | HOT, WATCHED |
| 18 | S06-who-its-for-v2.mp4 | Who it's for / not for | 22 s | RT-A, RT-B |
| parked | PARKED-S15-hardest-stage-v1.mp4 | Cold-audience message. **Not for this build** | 36 s | none |

Meta allows up to 50 ads per ad set. If dynamic creative is used, keep the testimonial overlays readable (no auto-crop to 1:1).

## 4. Copy (Jeremy reviews before anything runs; copy audit applied: no make/earn/money, no figures in the text)
**HOT (booked + applied), content, no hard CTA**
- Primary: "Before your call, here's how we actually build it. No fluff, just the system and the people it's working for."
- Headline: "See how it works before we talk"
- CTA button: Learn More -> VSL page

**WATCHED (VSL visitors)**
- Primary: "You watched how it works. Here's what our trading Discord clients say about it, and what we actually do."
- Headline: "Done for you. Trading communities only."
- CTA button: Learn More -> VSL page

**RT-A (applied, not booked)**
- Primary: "You started your application. Finish it and book your call: it's a planning session for your Discord, not a contract."
- Headline: "Finish booking your call"
- CTA button: Book Now -> booking page

**RT-B (watched, not applied)**
- Primary: "For trading Discord owners at $10K+: we build the funnel, emails and Discord structure. You record. See if you qualify."
- Headline: "See if you qualify"
- CTA button: Apply Now -> application page

## 5. How we judge it (not on cost per booked call for HOT/WATCHED)
- Week 1 = delivery only. HOT frequency per booked person is 15-20+ impressions before the call; under 5 means a delivery problem.
- Day 14 and day 21 reads: show rate 57% -> 65%+, close rate on calls taken 25%+.
- Per video: after $50 spend, or at the day-14 read, swap the bottom 3 by ThruPlay rate.
- RT-A / RT-B use normal rules: cut over $400 per booking, scale under $300.

## 6. Backups if an ad is rejected
Swap in the next clip down the list, then S05 / Rell / Colin (no figures). Jack and Sean show MRR figures on screen; if they're rejected, don't re-cut them, report it to Andy.

## 7. Not in this build
Google / YouTube retargeting (gated on 2 weeks at CPBC <= $300). S15 (cold only). The YouTube-watch plan (Vidalytics + GHL tags) is a separate build.

# What the 1,000-reel study found

Source: 1,000 Instagram reels from 7 trading creators (Oct 2026): every reel in the study list, not
only the top ones (433, 228, 143, 143, 26, 18 and 9 per account). Each reel was measured
(length, cuts, scene changes, letterbox, loudness, speech pace, speech start; 755 had audio, 649
had speech) and its opening and full-reel frames were coded by eye (format, hook text and type, hook
styling, captions, proof, CTA, face, emoji).

How to read the numbers: views are compared only inside each creator's own account, as a views rank
from 0 (that account's lowest) to 1 (its highest); 0.50 is a typical reel for that account. The
numbers below are medians, with n = number of reels. Small groups (n under 15) are hints, not rules.
Nothing here proves cause: the reels weren't tested against each other, and some top reels may be
boosted.

## Signals that held up

| Signal | Median views rank | Takeaway |
|---|---|---|
| Proof (P&L, result, broker screen) on screen in the first 3 s | 0.88 (n12) and 0.62 (n23), vs 0.47-0.49 without | The strongest signal. Show a real result early when the creator has one. |
| Hook is a question | 0.62 (n25) and 0.65 (n20) | Write one question hook in every set of three. |
| Hook is a command ("stop", "don't", "use") | 0.25 (n19) and 0.44 (n23) | Weak. Don't default to command hooks. |
| Hook text in a box or outline | 0.18 (n24) in one account; 0.46 boxed vs 0.65 plain (n92/n42) in the main stack account | Default to plain white text with a soft shadow. One account's boxed hooks did well (0.72, n10), so it isn't a hard rule. |
| Emoji in the hook | 0.44 with vs 0.58 without (n96/n47) | Leave emoji out. |
| Speech pace | top quarter 2.6-2.8 words/s vs bottom quarter 3.1-3.7 in three accounts | Cut pauses, but don't rush. Slower, clear delivery did better. |
| POV/joke format | 0.71 (n17) and 0.61 (n25) | Good for reach; mix one in now and then. |

## Signals that didn't matter

- Length, cuts per second, time to the first visual change, longest static stretch and when speech
  starts: within each account, none correlated with views beyond about ±0.2 (most near 0). They're
  still good craft and the course asks for them, but they don't explain views.
- Letterbox: 0.49 letterboxed vs 0.51 full-bleed in the account with 120 letterboxed reels.
- Captions on or off: mixed (better in one account, worse in another).
- Face on screen: slightly lower in three accounts (0.47-0.50 with a face vs 0.53-0.63 without), but
  the faceless reels are mostly POV clips and charts, so this is the format, not the face.
- On-screen CTA: rare (0 of 433 in the largest account). In the one account that used it, 9 CTA
  reels had a median of 0.89, too few to call.

## Hook length

No length won everywhere: 1-5 words did best in two accounts, 6-10 in two others. Keep hooks short
enough to read in about 2 s (4-10 words) and judge by type, not length.

## How the scorer uses this

`scripts/score.py` adds +2 for proof in the first 3 s, +1 for a question hook, +0.5 for POV, and
-1 for a command hook, -1 for a boxed or outlined hook, -0.5 for emoji and -0.5 for speech over
3.4 words/s. On the 1,000 reels, those scoring +1 or more had a median views rank of 0.66, those at
-1 or less 0.39, and the rest 0.51 (overall correlation +0.17, measured on the same reels). It's a
tie-breaker between hook lines, not a views forecast.

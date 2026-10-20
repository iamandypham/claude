# What the 1,000-reel study found

Source: 1,000 Instagram reels from 7 trading creators (Oct 2026): every reel in the study list, not
only the top ones (433, 228, 143, 143, 26, 18 and 9 per account). Each reel was measured (length,
cuts, scene changes, letterbox, loudness, speech pace, speech start; 755 had audio, 649 had speech)
and its opening and full-reel frames were coded by eye (format, hook text and type, hook styling,
captions, proof, CTA, face, emoji). A spot-check of that coding found about 1 clear error in 15
reels, and proof screens were sometimes missed, so the proof counts are if anything too low.

How to read the numbers: views are compared only inside each creator's own account, as a views rank
from 0 (that account's lowest) to 1 (its highest); 0.50 is a typical reel for that account. Numbers
are medians, with n = number of reels. Groups under n 15 are hints, not rules. Nothing here proves
cause: the reels weren't tested against each other, and some top reels may be boosted.

## Signals that leaned one way

| Signal | Median views rank | Where it reversed or was flat |
|---|---|---|
| Proof (P&L, result, broker screen) on screen in the first 3 s | 0.88 (n12) and 0.62 (n23), vs 0.47-0.49 without | 0.29 in one account, but only n4 |
| Hook is a question | 0.62 (n25) and 0.65 (n20) | 0.49 (n5) and 0.29 (n2) in two small groups |
| Hook is a command ("stop", "don't", "keep", "use") | 0.25 (n19) and 0.44 (n23) | 0.71 in one account (n4) |
| Speech pace (reels with speech only) | top quarter 2.7-3.1 words/s vs bottom quarter 3.5-3.8 in the three largest accounts | flat in a fourth (3.7 vs 3.6, n5/n8); faster did better in one small account |
| POV/joke format | 0.71 (n17) and 0.61 (n25) | flat in the largest account (0.51, n214) |
| Emoji in the hook (one account, 96 of the 107 emoji hooks) | 0.44 with vs 0.58 without | too few elsewhere to tell |

Takeaways: show a real result early when the creator has one; write at least one question hook;
don't default to "stop/don't" hooks; cut pauses but don't rush the delivery.

## Signals that didn't hold up

- Hook styling (box vs plain text): boxed hooks looked worse at first (0.18, n24 in one account;
  0.46 vs 0.65 in another), but in that second account nearly all boxed hooks were stack reels and
  most carried emoji, while the plain ones were mostly chart and POV clips. Boxed hooks without
  emoji sat at 0.57. So the box itself shows no clear effect; use the creator's own style.
- In the four large accounts, length, cuts per second, time to the first visual change, longest
  static stretch and speech start didn't correlate with views beyond about ±0.2. In the X-post
  account, an earlier first visual change and earlier speech did go with more views (-0.53, -0.35),
  and in one small account longer reels did better (+0.39). These are still good craft and the
  course asks for them.
- Letterbox: 0.49 letterboxed vs 0.51 full-bleed in the account with 120 letterboxed reels.
- Captions on or off: mixed (better in one account, worse in another).
- Face on screen: slightly lower in three accounts, but the faceless reels are mostly POV clips and
  charts, so this is the format, not the face.
- On-screen CTA: three accounts used one on a few reels (n9, 5, 3); medians 0.89, 0.50 and 0.52.
  Too few to call.

## Hook length

No length won everywhere: 1-5 words did best in two accounts, 6-10 in two others. Keep hooks short
enough to read in about 2 s (4-10 words) and judge by type, not length.

## How the scorer uses this

`scripts/score.py` adds +2 for proof in the first 3 s, +1 for a question hook, +0.5 for POV, and
-1 for a command hook, -0.5 for emoji and -0.5 for speech over 3.4 words/s. Run on the 1,000 reels
with its own hook classifier, reels scoring +1 or more had a median views rank of 0.60 (n92), those
at -1 or less 0.39 (n60), and the rest 0.49. Overall correlation +0.14, measured on the same reels,
and negative in two small accounts (-0.30 each). It's a tie-breaker between hook lines, not a views
forecast.

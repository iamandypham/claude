---
name: reel-scripts
description: Agent 2 of the BG reel system - turn a picked idea (Content Ideas sheet row or a topic) into 5 short reel scripts with different hooks, a teleprompter file holding only Andy's words, and a separate run order for his cues. Use for "write the reel scripts", "script this idea", "5 versions".
---

# reel-scripts: the script agent (Andy, 20 Oct 2026)

Part of the 4-agent reel system from Brendan Jowett's "How I Fully Automated My Instagram Reels" (youtube.com/watch?v=lGeQ_-CQ18c):
1. **Idea getter** (already live): n8n `xrWS9iiQFdFlhncW`, 9 AM ET daily, Virlo most-saved TikToks → sheet "BG Daily Content Ideas" `1zS5379HOclA3m_Fehs94hEe9Fcn0KqXoq7KKn1bTnx4` tab Ideas + #marketing-team. Don't change it here.
2. **reel-scripts** (this skill).
3. **reel-edit**: raw take → cut, captioned reels + an A/B style variant.
4. **reel-post**: approved reels → IG trial reels (n8n), only on Andy's typed go.

## Input
One idea: a sheet row (Date + Link, or the row's "Script angle") or a topic Andy names. Andy picks the idea. Never auto-pick from the sheet without his pick, because ideas are a manual review step in the video and for us too.

## Before writing (every time)
1. Read `/mnt/project-files/content/messaging-bank/andy-positions-and-lines-2026-10-04.md` sections 2, 3, 4 and 8. Use only `USE` and `SOURCED` items. Never `CHECK` or `HOLD`, and nothing in section 8. Keep the item code (F16, belief 7...) next to each line in the notes, not in the spoken words.
2. Read `/mnt/project-files/content/vibe-editing-2026-10-14/hormozi-100/rubric.md`. Every version must pass its six hard gates and score 70+.
3. Open the source video link so the version is ours, not a copy of theirs. Andy wants the source link kept with the idea.

## What to write
- **5 versions of the same idea**, each a different hook type: (1) story open, (2) confession, (3) contrarian claim / counter-verdict, (4) math reveal or "the real issue is...", (5) direct callout of the viewer ("If you own a trading Discord and..."). Story opens and confessions perform best in the rubric data, so put them first.
- **Hook in the first sentence**, claim or problem inside ~2 s. Then tension, a turn, one concrete example, a principle line, and the CTA.
- **Length:** 110 to 190 spoken words (about 45 to 75 s at Andy's pace). The rubric median is 74 s.
- **CTA:** the last line is `Comment "KEYWORD" and I'll send you <the thing>.` One keyword per idea, one plain word in caps (for example AUDIT), and the same across all 5 versions so one ManyChat trigger serves them all. Andy wires ManyChat, or the Mac agent does on his go.
- **Voice:** Andy's spoken voice, short sentences, no em dashes, no aphorism endings, no "Re:"-style bait. Clients are anonymous and labelled by niche. No trading-performance claims. "$20M+ in revenue for trading education businesses" and "$6.4M+ in sales on our own Whop" are allowed. Any other number needs a SOURCED item, and **every on-screen number needs a proof asset**, so list it in editor notes.
- No Whop tag or mention in captions (Andy 16 Oct, for X; apply to IG too).

## Output (folder `/mnt/project-files/content/reels/<YYYY-MM-DD>-<slug>/`)
Andy's correction (20 Oct, TJR funnel thread): "Don't put my cues there because I'm screen sharing." Whatever he reads or shows holds only what viewers should see or hear, and his cues go in a separate run order. So write three files:

1. `teleprompter.md`: **only the words he says.** One block per version, headed by just the version number (`1`, `2`...). No notes, codes, stage directions or brackets.
2. `run-order.md`: Andy's private cues, which never go on screen or into the teleprompter. Filming order, framing (chest-up, a little further back than usual so captions fit under the chin), "say the version number, pause 2 s, read it", "if you flub a line, pause and restart that line; the editor keeps your last full read", the keyword, and any prop or screen to film.
3. `scripts.json`: what reel-edit reads. `{"idea": {...sheet row...}, "keyword": "AUDIT", "versions": [{"id": "v1", "hook_type": "story", "lines": ["sentence", ...], "bank_codes": ["F16"], "score": 78, "gates": "6/6", "proof_needed": ["..."], "broll": ["..."]}]}`. `lines` must match `teleprompter.md` word for word, one sentence per entry.

## Review before Andy sees it
- Self-check each version against the rubric. Drop and rewrite anything under 70 or failing a gate. Put the scores in `scripts.json`, not in the teleprompter.
- Grep all five against section 8 of the bank and the client-name list. Zero hits, or rewrite.
- Send the 5 versions with the idea to Jeremy AI (send_message, then get_response) for a hook check. Apply what fits and note what you didn't take.
- Then post them to Andy in the thread: the 5 hooks (first lines) only, plus the folder link. He approves by version number. Unapproved versions are never edited or posted.

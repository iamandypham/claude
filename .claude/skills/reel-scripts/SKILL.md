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
One idea: a sheet row (Date + Link, or the row's "Script angle") or a topic Andy names. Andy picks the idea, or asks for "the best ones", in which case you pick the top rows yourself (see Steal mode).

## Steal mode (Andy, 22 Oct 2026: "steal the scripts and have you make like 5 versions like the video said")
1. **Pick:** read the ideas sheet (tab Ideas). Rank the rows not yet scripted (no folder in `/mnt/project-files/content/reels/` names that link) by raw saves, then save rate. Skip rows whose idea is off-niche for trading Discord owners, and merge near-duplicates (two Hormozi reels with the same point = one idea, both links kept).
2. **Pull the source script:** Virlo `raw_transcript` (platform tiktok, the row's link, $0.01 a call). Save it as `transcript-source.md` in the reel folder.
3. **Steal the structure, not the claims:** keep the source's hook shape, its turn, its concrete technique or command, and its ending punchline. Replace every figure, credential and story that belongs to the source creator ("20 years in sales", "$100K a month") with our bank lines, or drop it. Write what you kept and what you changed in `steal_notes`.
4. Then write the 5 versions as below, put them in `spec.json` and build the pack with `python3 .claude/skills/reel-scripts/build_pack.py <folder>/spec.json`. It writes teleprompter.md, run-order.md and scripts.json, and flags any version outside 110-190 words.

First run 22 Oct 2026: `2026-10-22-cheaper-objection` (@theryankeip, 37k saves) and `2026-10-22-four-hour-timer` (two @ahormozi reels).

## Before writing (every time)
0. **Match the YouTube messaging (Andy, 23 Oct 2026: "same messaging as our YT videos pretty much, we don't really talk about indicators").** Frame around the YT funnel: problem-aware educational content, unique mechanism, a one-page lead magnet that collects emails, emails collected in the past 30 days, free trial to paid, $99 low ticket, annual plans, high ticket on calls a few months in. No indicator talk, and no prop or affiliate cross-sells unless Andy asks. YT transcripts: Drive folder `1QRfs9a3ThZ0ibPTYdWkOeBb8P__0LNJ4`.
0b. **Buyer-language hooks (27 Oct 2026, Andy: "send those to content system agents").** Use `/mnt/project-files/content/reel-agents-2026-10-20/buyer-language-hooks-2026-10-27.md` (Slite FAjMFl4VwI61IQ; themes and buyer quotes in `/mnt/project-files/sales/closed-deal-themes-2026-10-27/report.md`) as a hook and angle source. When a sheet row fits a theme (direction / "tell me what to post", proof from people at your own starting size, lead flow instead of waiting for one video to hit, "good at trading, need a team for the rest", family and freedom, never cars), open at least one version with a "Ready to use" line from that file in its exact wording; on a day with no usable sheet rows, a theme can carry the day's pack on its own. Only lane O or B lines in reels. Lines 15-18 are OK too (Andy, 27 Oct: "Use buyer hooks 15-18 in reels"), organic reels only, word for word. The two guarantee lines (the "Held" section) are OK too (Andy, 27 Oct: "Use the guarantee lines too"), word for word. Never name or hint at a buyer or their story. Keep hedges ("in our experience") and bank wording (the Fiverr line) exactly.
1. Read `/mnt/project-files/content/messaging-bank/andy-positions-and-lines-2026-10-04.md` sections 2, 3, 4 and 8. Use only `USE` and `SOURCED` items. Never `CHECK` or `HOLD`, and nothing in section 8. Keep the item code (F16, belief 7...) next to each line in the notes, not in the spoken words.
2. Read `/mnt/project-files/content/vibe-editing-2026-10-14/hormozi-100/rubric.md`. Every version must pass its six hard gates and score 70+. Organic reels end on the CTA, so gate 5 ("ends on a principle or punchline") applies to the line right before the CTA.
3. Open the source video link so the version is ours, not a copy of theirs. Andy wants the source link kept with the idea.

## What to write
- **5 versions of the same idea**, each a different hook type: (1) story open, (2) confession, (3) contrarian claim / counter-verdict, (4) math reveal or "the real issue is...", (5) direct callout of the viewer ("If you own a trading Discord and..."). Story opens and confessions perform best in the rubric data, so put them first.
- **Hook in the first sentence**, claim or problem inside ~2 s. Then tension, a turn, one concrete example, a principle line, and the CTA.
- **Length:** 110 to 190 spoken words (about 45 to 75 s at Andy's pace). The rubric median is 74 s.
- **Keyword spec (Andy 22 Oct: "The comment keywords should be specified in the script"):** every pack also gets `freebie.json` → `freebie.pdf` (`python3 .claude/skills/reel-scripts/freebie.py`, one page, built only from lines in the script and bank) and `manychat.json` (keyword, comment replies, DM text, button, link). The manychat-keyword skill builds it on the Mac mini once Andy approves the DM text and freebie.
- **CTA:** the last line is `Comment "KEYWORD" and I'll send you <the thing>.` One keyword per idea, one plain word in caps (for example AUDIT), and the same across all 5 versions so one ManyChat trigger serves them all. Andy wires ManyChat, or the Mac agent does on his go.
- **Specificity:** generic advice scores in the 60s. Lift a version with a SOURCED story or figure from bank section 6 (for example S12 options Discord, S13 futures Discord), anonymised as the bank says, and list its proof in `proof_needed`.
- **No hardened claims:** never "most owners", "every time" or "almost never" unless the bank item says so. Use the bank's own hedges ("generally", "a lot of", "in our experience").
- **Voice:** Andy's spoken voice, short sentences, no em dashes, no aphorism endings, no "Re:"-style bait. Don't say "Whop" out loud: captions are burned in, and captions never mention Whop. Clients are anonymous and labelled by niche. No trading-performance claims. "$20M+ in revenue for trading education businesses" and "$6.4M+ in sales on our own Whop" are allowed. Any other number needs a SOURCED item, and **every on-screen number needs a proof asset**, so list it in editor notes.
- No Whop tag or mention in captions (Andy 16 Oct, for X; apply to IG too).

## Output (folder `/mnt/project-files/content/reels/<YYYY-MM-DD>-<slug>/`)
Andy's correction (20 Oct, TJR funnel thread): "Don't put my cues there because I'm screen sharing." Whatever he reads or shows holds only what viewers should see or hear, and his cues go in a separate run order. So write three files:

1. `teleprompter.md`: **only the words he says.** One block per version, headed by just the version number (`1`, `2`...). No notes, codes, stage directions or brackets.
2. `run-order.md`: Andy's private cues, which never go on screen or into the teleprompter. Filming order, framing (chest-up, a little further back than usual so captions fit under the chin), "say the version number, pause 2 s, read it", "if you flub a line, pause and restart that line; the editor keeps your last full read", the keyword, and any prop or screen to film.
3. `scripts.json`: what reel-edit reads. `{"idea": {...sheet row...}, "keyword": "AUDIT", "versions": [{"id": "v1", "hook_type": "story", "lines": ["sentence", ...], "bank_codes": ["F16"], "score": 78, "gates": "6/6", "proof_needed": ["..."], "broll": ["..."]}]}`. `lines` must match `teleprompter.md` word for word, one sentence per entry.

## Review before Andy sees it
- Self-check each version against the rubric. Drop and rewrite anything under 70 or failing a gate. Put the scores in `scripts.json`, not in the teleprompter.
- Run the humanizer skill (`.claude/skills/humanizer`, one of Brendan's five skills) on each version in embedded mode. Use Andy's verbatim lines in the bank as the voice sample. These are spoken scripts, so short fragments and the hook's own contrast stay. Cut staged run-ups ("here's the part..."), "not X but Y" filler, and closers that repeat the point. Never change a bank line's meaning, a figure or the CTA. Log what changed under `humanizer` in spec.json.
- Grep all five against section 8 of the bank and the client-name list. Zero hits, or rewrite.
- Send the 5 versions with the idea to Jeremy AI (send_message, then get_response) for a hook check. Apply what fits and note what you didn't take.
- Then post them to Andy in the thread: the 5 hooks (first lines) only, plus the folder link. He approves by version number. Unapproved versions are never edited or posted.

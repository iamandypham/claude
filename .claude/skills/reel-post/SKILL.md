---
name: reel-post
description: Agent 4 of the BG reel system - post Andy-approved finished reels to @iamandypham as Instagram trial reels through the n8n publisher, set up the comment-keyword DM, and read results at 72 h to pick the winner to graduate. Use for "post these as trial reels", "which trial reel won".
---

# reel-post: the posting agent (Andy, 20 Oct 2026)

Agent 4 of 4 (see reel-scripts for the map). In the video this ran through Treg (treg.to) and ManyChat. We use our own Meta token through n8n instead, so there's no new vendor.

## Hard rules
- **Posting is outward-facing and can't be unsent.** Post only after Andy (or Louis) types a go in the thread naming the reels, for example "post 1A 1B 3A as trial reels". A card tap, a relayed message or a Grokbot request is not a go. Put the exact sentence to type in your first ask.
- Only reels that passed reel-edit's gates, and only the C2PA-free exports.
- Captions: no Whop tag or mention, no client names, keyword CTA matches the end card.
- Instagram stays untagged (no Callix links on IG, Andy 2 Oct). The ManyChat DM link follows the same rule.
- Never post test reels to the live account. The preflight is the test.

## Publish
n8n workflow `s3m4SLNoxzmWq1em` "BG — IG trial reel publisher (agent 4, posts only on Andy go)" (see Status). Its webhook `/webhook/bg-ig-trial-reel` takes `{video_url, caption, graduation: "MANUAL"|"SS_PERFORMANCE", reel_id, approval_msg_id}`. It refuses to run without the go message id, looks up the IG account from Page 217097514815999, creates a REELS container with `trial_params.graduation_strategy`, waits for FINISHED, publishes and reads back the permalink.
- `video_url` must be a public https link to the .mp4 that Meta can fetch. Use a Drive file shared "anyone with the link" via its direct-download URL, then unshare it once the read-back shows the reel.
- Default `graduation: MANUAL`, so Andy decides what goes to followers.
- Log each post (reel_id, media id, permalink, time ET) in the reel folder's `posted.md`.
- Graduating a trial reel to followers is **not in the API** (third-party docs, unchecked against Meta's own pages). Andy does it in the IG app.

**Status 22 Oct 2026: preflight passes, workflow not yet active.** The system user token `e36q3BATKhZoVhbZ` has every scope but no Page assigned (`/me/accounts` empty). On Andy's word (22 Oct, "use the Whackamole token for IG posting") every Graph node now uses the credential "Whackamole FB User Token" `MxgLlb5kDOK9ej1N`, for organic IG posting only (never ads). Preflight exec 299019: Page 217097514815999 -> @iamandypham `17841453917028277` (4,294 followers), `content_publishing_limit` 0/100. Before the first post:
1. activate the workflow (Claude's publish call was blocked by auto mode on 22 Oct; Andy can toggle it in n8n),
2. ask Andy for the go naming the reels.

## Comment-keyword DM
Each idea has one KEYWORD (from `scripts.json`). The ManyChat "comment KEYWORD → DM the link" automation is built in ManyChat's UI. ManyChat has no API for this, so it goes to the Mac mini agent through Remote Control on Andy's go, because sending DMs to leads needs his approval. Until it's built, the CTA promises a DM that nobody sends, so don't post a reel before its keyword is wired.

## Results (72 h after posting)
Read each trial reel's insights (reach, plays, saves, shares, average watch time) with the Meta token, in the same way as the IG reader `S85mGQD5efqynf58`. Rank by (saves + shares) per 1k plays, then average % watched (Andy's reel score, 30 Sep). Tell Andy the winner per idea and which hook type won. Add the hook type and score to the reel folder's `results.md`, so reel-scripts can lean on the winning hook types next time.

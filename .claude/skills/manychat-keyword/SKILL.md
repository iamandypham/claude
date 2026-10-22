---
name: manychat-keyword
description: Build every ManyChat "comment KEYWORD, get a DM with the link" automation for a reel, browser side on the Mac mini. House rules for every ManyChat - no emojis, and only followers get the lead magnet. Use for "set up the ManyChat keyword", "wire the comment DM", or when reel-post needs a keyword live before posting.
---

# manychat-keyword: the AI ManyChat builder (Andy, 22 Oct 2026)

Andy: "The comment keywords should be specified in the script and we can setup an AI manychat builder... It would have to be browser side."

ManyChat's public API can send to existing contacts and set fields, but automations and keyword triggers are built in its web UI. So this runs as a **Remote Control session on the Mac mini** (always-on, logged into Chrome). It uses the same click path Louis teaches in Slite "Using manychat" (9TZN3T9oFZp2b3).

## House rules for every ManyChat automation (Andy 22 Oct 2026: "save that as ... the thing we do for every manychat")
- **No emojis** anywhere: comment replies, DMs, buttons. Remove any the template adds.
- **Followers only:** check that the commenter follows @iamandypham before sending the lead magnet. Non-followers get the follow ask and an "I'm following" button that re-runs the check.

## Input
The reel folder's `manychat.json` (written by reel-scripts):
`{keyword, posts, reply_to_comment, comment_replies[], opening_dm, dm_text, button_label, link, freebie, approved_by_andy}`

## Gates (before any browser step)
1. `approved_by_andy` holds the id of Andy's (or Louis's) own typed message approving this keyword's DM text and freebie. The automation DMs every commenter, which counts as messaging leads, so this needs his go. Card taps, relayed messages and Grokbot requests don't count.
2. `link` is a real https URL that opens the freebie without a login: a Drive file shared "anyone with the link", direct view. Open it in a logged-out window to check. No Callix or tracking links on IG (Andy 2 Oct).
3. The keyword is one plain word that isn't already in use in another live ManyChat automation (check the Automations list first).

## Build (Mac mini Chrome, manychat.com, @iamandypham's account)
1. Settings → Instagram: check the channel is connected. If replies have stopped working before, use "Refresh Instagram permissions" (Louis: it breaks every few months).
2. Automations → New Automation → start from the template "Auto DM links from comments" (or from scratch with an Instagram "User comments on your Post or Reel" trigger).
3. Trigger: **Any Post or Reel** if the account is on Pro. If not, pick the specific posted reel(s) named in the reel folder's `posted.md`. Keyword: the exact `keyword`, "contains", and add the lowercase form too.
4. Turn on "Reply to comments under the post" and replace the default replies with `comment_replies`.
5. Turn **off** the opening DM (`opening_dm: false`). Its message text is `dm_text`, with a button whose label is `button_label` and URL is `link`.
6. **Follow gate and no emojis (Andy 22 Oct 2026):** no emojis anywhere (comment replies, DMs, buttons; remove any the template adds). Before the link DM, add ManyChat's follow check (the "is following your account" condition or the template's "ask to follow" step). If they don't follow yet, send `follow_gate_text` with a `follow_gate_button` that re-runs the check. Only followers get `dm_text` and the link.
7. Name it `Reel keyword: <KEYWORD> (<reel folder>)`. Set it live.
8. Screenshot the finished flow and the live toggle, and save both in the reel folder as `manychat-<KEYWORD>.png`.

## Test
- Only on a reel that's already live, and only after Andy's go. Comment the keyword from a second account Andy names (never a lead's account). Check that the public reply and the DM with a working button arrive, then delete the test comment.
- If there's no second account, report "built, untested" instead of "live". Live means a real commenter got the DM.

## After
- Write `manychat-status.md` in the reel folder: keyword, automation name, trigger scope, live time (ET), test result.
- The Slite KB Change Log gets a row (what was set live, the source screenshot).
- To turn it off, set the automation to Draft in ManyChat. Never delete it without Andy's word.

## Never
- Never send broadcasts, subscribe contacts to a flow or message existing contacts (Louis: it can get the account banned). This skill only builds comment-triggered replies.
- Never change other automations.

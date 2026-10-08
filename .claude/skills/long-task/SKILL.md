---
name: long-task
description: Set up and run a long or live-system task in the Media Buying project - checks.md acceptance table, progress.md handoff, high-effort read-only reviewer, retry check.
---

# Long task harness (Andy, 8 Oct 2026)

Use for any task that changes a live system (n8n, GHL, Whop, HYROS, Slite, Typefully, ads) or will take more than one sitting. Skip for quick questions and one-off reads.

## 1. Before starting
Folder: /mnt/project-files/<area>/<task>/ (reuse the area's existing folder if there is one).

If progress.md already exists there, read it first and open every file it names before trusting its status. Continue from its Next action.

Write checks.md before doing any work:

```
# Checks: <task>
| requirement | verdict | evidence | correction |
|---|---|---|---|
| <one acceptance check, from Andy's words> | open | | |
```

- Verdict is pass, fail or open.
- Evidence is an execution id, record id, version id, file path or read-back. Never just "done".
- Never loosen a requirement to get a pass. Missing evidence stays visible as open.
- "Verified means tested" still applies: a publish or save is not evidence.

Write progress.md:

```
# Progress: <task>
Task: <the outcome Andy asked for + active constraints>
Outputs: <exact paths / ids of current saved work>
Completed: <finished stages + check results>
Decisions: <choice, with Andy's words or card id>
Open issues: <failures, uncertainties, blockers>
Failed attempts: <what was tried, why it failed; don't repeat without a new reason>
Next action: <one concrete step>
```

## 2. Loop
1. Read progress.md, pick one bounded step.
2. Do it within scope (back up first, record the backup/version id).
3. Run the checks that step affects; update checks.md.
4. Keep what works; undo only your own failed change.
5. Update progress.md (every stage, not only at handoff).

Before retrying any external write (n8n publish, GHL, Whop, Slite, Typefully), check whether the first attempt landed.

At ~150k context, progress.md is the handoff file: copy it to /mnt/project-files/<area>/handoff/ and ask the coordinator for a fresh thread.

Basic task helpers (fetching, filtering, drafting) run on Sonnet 5.5, at most 3 at once.

## 3. Review before done
Before calling it done or asking Andy to approve, start one reviewer helper on Opus 5.5 at HIGH effort (Andy, 8 Oct: "Review should be on high, basic task helpers should be on sonnet"), with read-only tools. Brief:

> Review this task's outputs against checks.md. You get: output paths <...>, checks.md path, sources <...>. Open each output and source yourself; do not trust the builder's notes. For each row, set verdict (pass/fail/open), the evidence you actually opened, and the correction needed. Return the table. Do not edit anything. Do not call mcp__hearthbot__ tools.

Apply the fixes yourself, rerun affected checks, update checks.md. If no helper is available, do a separate review pass and say so. The reply says which method was used.

## 4. Deliver
Reply with outputs, checks.md and progress.md in attached_outputs, what passed, and what is still open. Update the owning Slite page and log the change in the month's KB Change Log.

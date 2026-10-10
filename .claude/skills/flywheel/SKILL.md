---
name: flywheel
description: Self-improving loop for the BG project - when Andy corrects a thread, log the lesson, classify it, promote repeats into memory/skills/rules/checks, and keep a failure library that proves fixes hold.
---

# Flywheel: every correction should make the next run better (Andy, 10 Oct 2026)

Source: Lunar, "The Opus 5.5 Flywheel" (X article, 8 Oct 2026). Copy and fit notes: /mnt/project-files/meta/flywheel-2026-10-10/ (source-article.md, design.md).

Idea: a fix that lives only in one thread's chat is lost. Save the smallest thing that changes future behaviour: a memory line, a skill step, an instruction, an n8n check, or an eval. Claude proposes; Andy approves anything that changes project instructions, routines or MEMORY.md.

Files: /mnt/project-files/meta/flywheel/ (README.md, lessons.md, evals/, evals/runs/, scoreboard.md).

## 1. In the moment: Andy corrects you
Fix the output first. In the same turn, append one row to lessons.md (re-read it just before appending; append new rows only, the one in-place edit is a row's status/eval columns; read back after ~10 s):

`| date (ET) | thread | what was wrong | Andy's words / cmsg id | cause | class | smallest change | status | eval |`

- cause: missing-instruction, missing-context, stale-memory, weak-skill, missing-test, bad-tool-contract, permission, insufficient-evidence, ambiguous-task.
- class (a correction true only for this task, like "use this file for this ad", goes in the task's progress.md, not lessons.md):
  - reusable: should hold for every thread ("always ET for Andy"). Goes to memory, a skill or instruction wording.
  - enforceable: can be checked by code ("every weekday must come from `date`"). Goes to an n8n check, a hook, or an eval.
- A reviewer catch counts when Andy would have caught it. Status-checklist edits and Andy's preferences on one draft's wording don't count (the X edit log covers X drafts).

Ask: "Should this lesson survive this thread?" If no, keep it in the task.

Also log a row when Andy has to explain the same procedure a second time (cause weak-skill or missing-instruction): the smallest change is usually a skill. And when a permission or tool limit blocked the work (cause permission / bad-tool-contract): the change may be a setting only Andy can grant.

## 2. Same class twice: change the workflow, not the output
Before logging, grep lessons.md for the same cause + topic. If a row exists:
- mark the new row `repeat` and link the old one;
- in your reply to Andy, propose the smallest durable change in one line (exact text and where it goes). You may write it yourself only in a memory topic file your thread created, or to mark an already-decided value SUPERSEDED (versioned backup + log per the dream skill's guardrails). Shared topic files, MEMORY.md, project instructions, routines, skills, n8n checks, hooks and settings wait for Andy's pick or the Sunday run;
- add an eval (section 4) if none covers it.

Promotion ladder: observed (1st) -> repeat (2nd) -> proposed (dreaming #N) -> promoted (where) or rejected (Andy's words). Don't promote one-off preferences: compounding, not bureaucracy.

## 3. At the end of a run
The archive report to the coordinator gains one line: "Lessons: <n> rows in lessons.md (ids/dates)" or "Lessons: none". A long task's progress.md Failed attempts feed lessons the same way.

## 4. Failure library (evals/F-NNN.md)
One file per real failure:
```
# F-NNN <short name>
Source: <thread, date, Andy's words or cmsg id; lesson row>
Task (give to a fresh thread): "<self-contained scenario>"
Bad output (what happened): ...
Expected: ...
Pass rule: <checkable; a command if one exists>
```
Only real failures with a source. No lead PII or secrets.

Run the whole library weekly in the dreaming run, and the evals a change touches after a change to MEMORY.md, a skill or the project instructions (not after every topic-file write):
1. Extract only the Task lines into one file (never give the runner the Expected/Pass lines).
2. One Sonnet 5.5 helper acts as a fresh thread: it reads MEMORY.md and the topic files it would normally find, answers each task, and names its basis. It must not read the flywheel or dreaming folders. Don't tell it it is being tested; prefer one task per helper call when cheap. A pass shows memory can recall the fix, not how a busy thread behaves, so say that when reporting.
3. Grade each answer against Pass rule yourself (or with the long-task reviewer for a big change). Write evals/runs/<YYYY-MM-DD>.md: `| eval | pass/fail | answer excerpt | basis | note |`, plus totals: known failures, now passing, still failing, new regressions.
4. A failing eval is a lesson row (cause, smallest change), not a reason to edit the eval. Never loosen a pass rule to get a pass.

## 5. Scoreboard (scoreboard.md, updated by the Sunday run)
Per week: Andy corrections logged in the moment vs found later by dreaming (a falling "logged" number with a rising "found later" one means threads stopped logging); repeats of an already-logged class; lessons promoted; eval pass rate; first-pass approvals (drafts Andy approved with no requested change / drafts shown, counted from threads read by the dreaming run); Andy follow-up messages per finished task (proxy for his review time); cost per accepted output where get_session usage is readable (else "not measured"). The question each week: is Andy correcting less, and are old failures staying fixed? If not, we have automation, not a flywheel: say so in the Sunday reply.

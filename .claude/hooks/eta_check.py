#!/usr/bin/env python3
"""PreToolUse hook: remind the model when a progress checklist has a running step but no ET finish time.

Dreaming proposal #69 (approved 6 Nov 2026). Andy had to chase "ETA?" on 27 Oct and 30 Oct
even after the 9 Oct rule (give an ET finish time up front on any job over 15 minutes).

Looks at the `text` of mcp__hearthbot__update_progress_checklist. If it has a running step
(a line starting with the star-in-progress mark) and no ET clock time ("7:40 PM ET", "8 PM ET",
"ETA 9:15 PM ET", "~10:30 AM ET"), it adds a reminder to the model's context.
Never blocks. Fails open: any error stays silent.
"""
import json
import re
import sys

REMINDER = ("Running step with no ET finish time: add 'ETA <h:mm AM/PM> ET' to the header or the "
            "running step if this job will take over 15 minutes.")

ET_TIME = re.compile(r"(?<![0-9:])(?:1[0-2]|0?[1-9])(?::[0-5][0-9])?\s*(?:[ap]\.?m\.?)\s*(?:ET|EST|EDT)(?![A-Za-z])", re.I)
RUNNING = re.compile(r"^\s*✱")
STEP = re.compile(r"^\s*[✓✱○]")
DONE = re.compile(r"^\s*✓")


def needs_reminder(text):
    lines = text.splitlines()
    if not any(RUNNING.match(l) for l in lines):
        return False
    steps = [l for l in lines if STEP.match(l)]
    if all(DONE.match(l) for l in steps):
        return False
    return not ET_TIME.search(text)


def main():
    try:
        data = json.load(sys.stdin)
        text = data["tool_input"]["text"]
        if isinstance(text, str) and needs_reminder(text):
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": REMINDER,
            }}))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())

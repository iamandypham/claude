#!/usr/bin/env python3
"""Tests for eta_check.py. Run: python3 .claude/hooks/test_eta_check.py"""
import json
import os
import subprocess
import sys
import unittest

HOOK = os.path.join(os.path.dirname(__file__), "eta_check.py")


def run(stdin):
    p = subprocess.run([sys.executable, HOOK], input=stdin, capture_output=True, text=True)
    return p.returncode, p.stdout.strip()


def payload(text):
    return json.dumps({"tool_name": "mcp__hearthbot__update_progress_checklist", "tool_input": {"text": text}})


class EtaCheck(unittest.TestCase):
    def test_running_no_eta_reminds(self):
        code, out = run(payload("Building report\n\n✓ Pull data\n✱ Write report\n○ Publish"))
        self.assertEqual(code, 0)
        ctx = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(ctx["hookEventName"], "PreToolUse")
        self.assertIn("Running step with no ET finish time", ctx["additionalContext"])

    def test_eta_present_silent(self):
        self.assertEqual(run(payload("Building report, ETA 7:40 PM ET\n\n✓ Pull data\n✱ Write report"))[1], "")

    def test_eta_formats_silent(self):
        for t in ("7:40 PM ET", "8 PM ET", "ETA 9:15 PM ET", "~10:30 AM ET", "done by 6:05 pm EDT"):
            self.assertEqual(run(payload("Job\n\n✱ Step (%s)" % t))[1], "", t)

    def test_non_et_time_still_reminds(self):
        self.assertNotEqual(run(payload("Job\n\n✱ Step ETA 7:40 PM PT"))[1], "")

    def test_all_done_silent(self):
        self.assertEqual(run(payload("Done\n\n✓ One\n✓ Two"))[1], "")

    def test_no_running_step_silent(self):
        self.assertEqual(run(payload("Plan\n\n✓ One\n○ Two"))[1], "")

    def test_malformed_silent(self):
        for s in ("", "not json", "[]", "{}", json.dumps({"tool_input": {"text": 5}}), json.dumps({"tool_input": None})):
            code, out = run(s)
            self.assertEqual((code, out), (0, ""), s)


if __name__ == "__main__":
    unittest.main()

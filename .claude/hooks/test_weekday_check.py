#!/usr/bin/env python3
"""Tests for weekday_check.py. Run: python3 .claude/hooks/test_weekday_check.py"""
import datetime as dt
import json
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from weekday_check import problems  # noqa: E402

HOOK = os.path.join(os.path.dirname(__file__), "weekday_check.py")


def run(tool_input, today):
    env = dict(os.environ, WEEKDAY_CHECK_TODAY=today)
    p = subprocess.run([sys.executable, HOOK], input=json.dumps({"tool_name": "mcp__hearthbot__reply", "tool_input": tool_input}),
                       capture_output=True, text=True, env=env)
    return p.returncode, p.stderr


class WeekdayCheck(unittest.TestCase):
    def test_blocks_real_miss_tomorrow_sat_11(self):
        # Fix Callix per-ad attribution, posted Sat 10 Oct 2026
        code, err = run({"text": "The first scheduled run is tomorrow (Sat 11 Oct)."}, "2026-10-10")
        self.assertEqual(code, 2)
        self.assertIn("Sunday", err)

    def test_blocks_real_miss_mondays_series(self):
        found = problems("Proof emails: Mon 13 Oct, Mon 20 Oct, Mon 27 Oct at 2 PM ET", dt.date(2026, 10, 10))
        self.assertEqual(len(found), 3)

    def test_passes_recent_past_date(self):
        self.assertEqual(run({"text": "Sent on Sat 10 Oct and Tue 6 Oct."}, "2026-10-11")[0], 0)

    def test_passes_correct_dates(self):
        self.assertEqual(problems("Mon 12 Oct, Monday, Oct 19, Mon 26 October 2026, Sun 2026-10-11", dt.date(2026, 10, 11)), [])

    def test_skips_strikethrough_quotes_code(self):
        text = '~~Mon 13 Oct~~ Tue 13 Oct. Andy wrote "Mon 13 Oct". `Mon 13 Oct`\n> Mon 13 Oct'
        self.assertEqual(problems(text, dt.date(2026, 10, 11)), [])

    def test_checks_nested_fields(self):
        code, _ = run({"question": "Send on Mon 13 Oct?", "options": [{"label": "Yes", "consequence": "Goes Fri 16 Oct"}]}, "2026-10-11")
        self.assertEqual(code, 2)

    def test_year_given(self):
        self.assertEqual(len(problems("Fri 16 Oct 2027", dt.date(2026, 10, 11))), 1)  # 16 Oct 2027 is a Saturday

    def test_year_boundary(self):
        self.assertEqual(problems("Fri 1 Jan", dt.date(2026, 12, 20)), [])  # 1 Jan 2027 is a Friday

    def test_fails_open_on_bad_input(self):
        p = subprocess.run([sys.executable, HOOK], input="not json", capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)

    def test_weekday_as_predicate(self):
        self.assertEqual(problems("26 Oct 2026 is a Monday, 27 Oct is a Tuesday; 12/19 Oct = Monday, 13 Oct = Tuesday", dt.date(2026, 10, 11)), [])

    def test_no_false_positive_inside_words(self):
        # Opus review 11 Oct: "showed", "followed", "Simon", "3 decisions" were read as weekdays/months
        text = "Jahn showed 12 Oct. Kasen followed 19 Oct. Andy reviewed 13 Oct draft. we allowed 2 Nov. Simon 14 Oct. Friday 3 decisions."
        self.assertEqual(problems(text, dt.date(2026, 10, 11)), [])

    def test_predicate_needs_a_date_first(self):
        self.assertEqual(len(problems("Next send is Mon 13 Oct", dt.date(2026, 10, 11))), 1)
        self.assertEqual(problems("Oct 26 is a Monday and 2026-10-27 is a Tuesday", dt.date(2026, 10, 11)), [])

    def test_italics_checked(self):
        self.assertEqual(len(problems("_Mon 13 Oct_ and *Fri 17 Oct*", dt.date(2026, 10, 11))), 2)

    def test_full_month_names(self):
        self.assertEqual(problems("Monday 12 October, Tue June 2 2026, Wed 30 September 2026", dt.date(2026, 10, 11)), [])

    def test_no_dates(self):
        self.assertEqual(run({"text": "On it. Back by 10:45 AM ET."}, "2026-10-11")[0], 0)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""PreToolUse hook: block a thread message whose weekday doesn't match its date.

Dreaming proposal #2 (11 Oct 2026). Threads kept writing weekdays from memory
("Mon 13 Oct" when 13 Oct 2026 is a Tuesday). This checks every "weekday + date"
pair in the outgoing text and blocks the send with the right weekday.

Skips struck-through text (~~...~~), code, double-quoted text and > quote lines.
A date without a year gets the year that puts it nearest today (America/New_York).
Fails open: any error lets the message through.
"""
import datetime as dt
import json
import os
import re
import sys

DAYS = {
    "mon": 0, "monday": 0,
    "tue": 1, "tues": 1, "tuesday": 1,
    "wed": 2, "weds": 2, "wednesday": 2,
    "thu": 3, "thur": 3, "thurs": 3, "thursday": 3,
    "fri": 4, "friday": 4,
    "sat": 5, "saturday": 5,
    "sun": 6, "sunday": 6,
}
MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Edges use letter/digit look-arounds, not \b, so "showed 12 Oct" and "Simon 14 Oct" don't match
# and "_Mon 13 Oct_" (italics) still does.
START = r"(?<![a-z0-9])"
END = r"(?![a-z0-9])"
WD = START + r"(?P<wd>" + "|".join(sorted(DAYS, key=len, reverse=True)) + r")" + END + r"\.?,?"
MON = (r"(?P<mon>jan|feb|mar|apr|may|jun|jul|aug|sept?|oct|nov|dec)"
       r"(?:uary|ruary|ch|il|e|y|ust|ember|tember|ober)?" + END + r"\.?")  # not "3 decisions"
DAY = r"(?P<day>\d{1,2})(?:st|nd|rd|th)?"
YEAR = r"(?:,?\s+(?P<year>20\d\d))?"
PATTERNS = [
    re.compile(WD + r"\s+" + DAY + r"\s+" + MON + YEAR + END, re.I),          # Mon 13 Oct (2026)
    re.compile(WD + r"\s+" + MON + r"\s+" + DAY + YEAR + END, re.I),          # Monday, Oct 13(, 2026)
    re.compile(WD + r"\s+(?P<iso>20\d\d-\d\d-\d\d)" + END, re.I),                # Sun 2026-10-11
]
SKIP = [
    re.compile(r"```.*?```", re.S),
    re.compile(r"`[^`\n]*`"),
    re.compile(r"~~.*?~~", re.S),
    re.compile(r"\"[^\"\n]*\"|“[^”\n]*”"),
    re.compile(r"^\s*>.*$", re.M),
]
# "26 Oct is a Monday", "Oct 26 = Monday": the weekday names the date written just before it.
# Only skipped when a date really comes first, so "Next send is Mon 13 Oct" is still checked.
PREDICATE = re.compile(
    r"(?:\d{1,2}(?:st|nd|rd|th)?\s+[a-z]{3,9}\.?|[a-z]{3,9}\.?\s+\d{1,2}(?:st|nd|rd|th)?|20\d\d-\d\d-\d\d)"
    r"(?:,?\s+20\d\d)?\s*(?:is|are|was|will be|=)\s*(?:an?\s+)?$", re.I)


def today():
    override = os.environ.get("WEEKDAY_CHECK_TODAY")
    if override:
        return dt.date.fromisoformat(override)
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("America/New_York")).date()
    except Exception:
        return dt.date.today()


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from strings(v)


def resolve(m, ref):
    if m.groupdict().get("iso"):
        return dt.date.fromisoformat(m.group("iso"))
    month = MONTHS[m.group("mon").lower()[:3]]
    day = int(m.group("day"))
    if m.group("year"):
        return dt.date(int(m.group("year")), month, day)
    best = None
    for y in (ref.year - 1, ref.year, ref.year + 1):
        try:
            d = dt.date(y, month, day)
        except ValueError:
            continue
        if best is None or abs((d - ref).days) < abs((best - ref).days):
            best = d
    return best


def problems(text, ref):
    for rx in SKIP:
        text = rx.sub(" ", text)
    found = []
    for rx in PATTERNS:
        for m in rx.finditer(text):
            try:
                d = resolve(m, ref)
            except ValueError:
                continue
            if d is None:
                continue
            if PREDICATE.search(text[max(0, m.start() - 40):m.start()]):
                continue
            said = DAYS[m.group("wd").lower().rstrip(".,")]
            if d.weekday() != said:
                found.append(f'"{m.group(0).strip()}": {d.day} {d.strftime("%b %Y")} is a {NAMES[d.weekday()]}')
    return found


def main():
    try:
        data = json.load(sys.stdin)
        text = "\n".join(strings(data.get("tool_input", {})))
        found = problems(text, today())
    except Exception:
        return 0
    if found:
        sys.stderr.write("Weekday check: wrong weekday next to a date. Fix and resend.\n- "
                         + "\n- ".join(dict.fromkeys(found)) + "\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

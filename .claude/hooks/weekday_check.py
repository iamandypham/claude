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

WD = r"(?P<wd>" + "|".join(sorted(DAYS, key=len, reverse=True)) + r")\b\.?,?"
MON = r"(?P<mon>jan|feb|mar|apr|may|jun|jul|aug|sept?|oct|nov|dec)[a-z]*\.?"
DAY = r"(?P<day>\d{1,2})(?:st|nd|rd|th)?"
YEAR = r"(?:,?\s+(?P<year>20\d\d))?"
PATTERNS = [
    re.compile(WD + r"\s+" + DAY + r"\s+" + MON + YEAR + r"\b", re.I),          # Mon 13 Oct (2026)
    re.compile(WD + r"\s+" + MON + r"\s+" + DAY + YEAR + r"\b", re.I),          # Monday, Oct 13(, 2026)
    re.compile(WD + r"\s+(?P<iso>20\d\d-\d\d-\d\d)\b", re.I),                    # Sun 2026-10-11
]
SKIP = [
    re.compile(r"```.*?```", re.S),
    re.compile(r"`[^`\n]*`"),
    re.compile(r"~~.*?~~", re.S),
    re.compile(r"\"[^\"\n]*\"|“[^”\n]*”"),
    re.compile(r"^\s*>.*$", re.M),
]


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
            before = text[max(0, m.start() - 12):m.start()].lower()
            if re.search(r"(=\s*|\b(is|are|was|be)\s+(an?\s+)?)$", before):
                continue  # "26 Oct is a Monday, 27 Oct is a Tuesday": the weekday belongs to the earlier date
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

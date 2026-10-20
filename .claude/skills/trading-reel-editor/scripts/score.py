#!/usr/bin/env python3
"""Score a reel plan against what separated top from bottom reels in the 1,000-reel study.

Usage: score.py plan.json [--words words.json] [--proof-first-3s] [--format stack|face|pov|card|explainer]

Prints each signal, its weight and the study evidence, then a total. The signals are weak on their
own (the whole score correlates about +0.17 with a reel's views rank inside its creator's account,
measured on the same reels it was built from). Use it to choose between hook lines and fix easy
misses, not to predict views.
"""
import argparse, json, os, re

QUESTION = re.compile(r"\?\s*\S*$|^(why|how|what|when|which|who)\b", re.I)
COMMAND = re.compile(r"^(stop|don'?t|never|always|quit|start|use|try|watch|do|avoid|learn|look)\b", re.I)
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")


def hook_signals(text):
    out = []
    t = (text or "").strip()
    if not t:
        return out
    if QUESTION.search(t):
        out.append(("hook is a question", +1.0, "question hooks: median views rank 0.62-0.65 in two accounts"))
    elif COMMAND.search(t):
        out.append(("hook is a command (stop/don't/use...)", -1.0,
                    "command hooks: median views rank 0.25 (n19) and 0.44 (n23)"))
    if EMOJI.search(t):
        out.append(("emoji in hook", -0.5, "one stack account: 0.44 with emoji vs 0.58 without (n143)"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("--words")
    ap.add_argument("--proof-first-3s", action="store_true", help="a P&L, payout or result is on screen by 3 s")
    ap.add_argument("--format", default=None)
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    hook = plan.get("hook") or {}
    rows = []
    if a.proof_first_3s:
        rows.append(("proof on screen in the first 3 s", +2.0, "median views rank 0.88 (n12) and 0.62 (n23) vs 0.47-0.49"))
    else:
        rows.append(("no proof in the first 3 s", 0.0, "add a P&L/result screenshot early if the creator has one"))
    rows += hook_signals(hook.get("text"))
    style = hook.get("style", "plain")
    if hook.get("text") and style in ("box", "bold"):
        rows.append((f"hook text in a {style} style", -1.0,
                     "boxed/outlined hooks: 0.18 (n24) in one account, 0.46 vs plain 0.65 in another"))
    fmt = a.format or ("stack" if plan.get("layout") == "stack" else None)
    if fmt == "pov":
        rows.append(("POV/joke format", +0.5, "POV reels: 0.71 and 0.61 in two accounts (reach, not leads)"))
    if a.words or plan.get("words"):
        try:
            wpath = a.words or os.path.join(os.path.dirname(os.path.abspath(a.plan)), plan["words"])
            words = json.load(open(wpath))["words"]
            span = max(1e-6, words[-1]["e"] - words[0]["s"])
            wps = len(words) / span
            if wps > 3.4:
                rows.append((f"speech {wps:.1f} words/s", -0.5,
                             "top-quarter reels spoke slower: 2.6-2.8 vs 3.1-3.7 words/s in three accounts"))
            else:
                rows.append((f"speech {wps:.1f} words/s", 0.0, "within the range of top reels"))
        except (OSError, KeyError, IndexError):
            pass
    total = sum(w for _, w, _ in rows)
    width = max(len(r[0]) for r in rows)
    for name, w, why in rows:
        print(f"{w:+.1f}  {name:<{width}}  {why}")
    band = "above typical" if total >= 1 else "below typical" if total <= -1 else "typical"
    print(f"\nscore {total:+.1f} ({band}; study medians: >=+1 0.66, between 0.51, <=-1 0.39 views rank)")


if __name__ == "__main__":
    main()

#!/usr/bin/env bash
# Render the graphics pass: render_graphics.sh <props.json> <out.mp4>
# props.json must sit in graphics/public/ next to the cut it names (plan_graphics.py puts it there).
set -euo pipefail
DIR="$(cd "$(dirname "$0")/graphics" && pwd)"
PROPS="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
OUT="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"
cd "$DIR"
[ -d node_modules ] || npm install --no-audit --no-fund
BROWSER=()
for b in /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell; do
  [ -x "$b" ] && BROWSER=(--browser-executable="$b") && break
done
npx remotion render src/index.ts Reel "$OUT" --props="$PROPS" --codec=h264 --crf=18 "${BROWSER[@]}"

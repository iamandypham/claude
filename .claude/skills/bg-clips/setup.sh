#!/usr/bin/env bash
# Install the Vibe Editing kit (pinned) with the BG overlay. Linux/macOS. Usage: setup.sh <work dir>
# Safe to re-run.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="$(mkdir -p "${1:?usage: setup.sh <work dir>}" && cd "$1" && pwd)"
COMMIT=83c5ff6006dd79918e8395ef58cfcb4600c21db5
[ -d "$DEST/vibe-editing/.git" ] || git clone -q https://github.com/maddexritter-rgb/vibe-editing.git "$DEST/vibe-editing"
git -C "$DEST/vibe-editing" checkout -q "$COMMIT"
K="$DEST/vibe-editing/plugins/vibe-editing"
[ -d "$K/.venv" ] || python3 -m venv "$K/.venv"
"$K/.venv/bin/pip" install -q -r "$K/requirements.txt"
"$K/.venv/bin/pip" install -q --only-binary av -r "$HERE/overlay/requirements-pins.txt"
python3 -I "$HERE/overlay/patch_kit.py" "$K"

# Real ffmpeg = first one on PATH that isn't our own shim dir (so a re-run after `source env.sh` can't loop).
REAL_FFMPEG=""
IFS=: read -ra DIRS <<< "$PATH"
for d in "${DIRS[@]}"; do
  [ "$d" = "$DEST/bin" ] && continue
  if [ -x "$d/ffmpeg" ]; then REAL_FFMPEG="$d/ffmpeg"; break; fi
done
[ -n "$REAL_FFMPEG" ] || { echo "ffmpeg not found"; exit 1; }
REAL_FFPROBE="$(dirname "$REAL_FFMPEG")/ffprobe"

mkdir -p "$DEST/bin"
rm -f "$DEST/bin/ffmpeg" "$DEST/bin/ffprobe"
# The shim only matters where Apple's VideoToolbox encoder is missing (Linux, Windows).
if ! "$REAL_FFMPEG" -hide_banner -encoders 2>/dev/null | grep -q h264_videotoolbox; then
  cp "$HERE/overlay/bin/ffmpeg" "$DEST/bin/ffmpeg"; chmod +x "$DEST/bin/ffmpeg"
  ln -sf "$REAL_FFPROBE" "$DEST/bin/ffprobe"
fi
mkdir -p "$DEST/presets"
for p in "$HERE"/overlay/presets/*.json; do
  sed "s#\"fonts_dir\": \"fonts/free_font\"#\"fonts_dir\": \"$K/skills/caption-clips/fonts/free_font\"#" "$p" > "$DEST/presets/$(basename "$p")"
done
cat > "$DEST/env.sh" <<ENV
export BG_REAL_FFMPEG="$REAL_FFMPEG"
export PATH="$DEST/bin:$K/.venv/bin:\$PATH"
export K="$K"
export BG_OVERLAY="$HERE/overlay"
export BG_PRESETS="$DEST/presets"
ENV
. "$DEST/env.sh"
python "$K/doctor.py" | sed 's/\x1b\[[0-9;]*m//g' | tail -3
echo "Done. Before each run: source $DEST/env.sh"

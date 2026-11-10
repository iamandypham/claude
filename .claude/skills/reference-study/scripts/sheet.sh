#!/usr/bin/env bash
# Contact sheet for eyeballing a reference clip. usage: sheet.sh <video> <out.jpg> [fps=2] [start=0] [dur=60]
set -euo pipefail
v="$1"; o="$2"; fps="${3:-2}"; ss="${4:-0}"; t="${5:-60}"
h=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$v"); w=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$v")
if [ "$h" -gt "$w" ]; then sc="180:320"; cols=12; else sc="400:225"; cols=6; fi
ffmpeg -v error -y -ss "$ss" -t "$t" -i "$v" -vf "fps=$fps,scale=$sc,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=14:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=${cols}x10" -frames:v 1 -q:v 4 "$o"

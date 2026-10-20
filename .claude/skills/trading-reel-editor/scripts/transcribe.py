#!/usr/bin/env python3
"""Transcribe a video to word timestamps.

Usage: transcribe.py <video> <out_words.json> [--model small]
Output: {"duration": s, "words": [{"w": "word", "s": start, "e": end}, ...]}
Needs ffmpeg and the faster-whisper Python package (runs locally, no API key).
"""
import argparse, json, subprocess, sys, tempfile, os, wave

import numpy as np


def load_audio(path):
    with tempfile.TemporaryDirectory() as d:
        wav = os.path.join(d, "a.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vn", "-ac", "1",
                        "-ar", "16000", "-c:a", "pcm_s16le", wav], check=True)
        with wave.open(wav) as w:
            data = w.readframes(w.getnframes())
    return np.frombuffer(data, np.int16).astype(np.float32) / 32768.0


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("out")
    ap.add_argument("--model", default="small")
    ap.add_argument("--language", default=None)
    a = ap.parse_args()
    from faster_whisper import WhisperModel
    model = WhisperModel(a.model, device="cpu", compute_type="int8")
    # Pass the decoded array: faster-whisper's own file loader fails on some boxes.
    segs, _ = model.transcribe(load_audio(a.video), word_timestamps=True,
                               language=a.language, vad_filter=True)
    words = []
    for seg in segs:
        for w in seg.words or []:
            t = w.word.strip()
            if t:
                words.append({"w": t, "s": round(w.start, 3), "e": round(w.end, 3)})
    json.dump({"duration": duration(a.video), "words": words}, open(a.out, "w"), indent=1)
    print(f"{len(words)} words -> {a.out}")


if __name__ == "__main__":
    sys.exit(main())

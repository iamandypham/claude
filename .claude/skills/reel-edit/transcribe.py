#!/usr/bin/env python3
"""Word-timestamp transcript for split_takes.py: transcribe.py in.wav words.json [model]
Feed a 16 kHz mono wav (ffmpeg -i raw.mov -ac 1 -ar 16000 raw.wav); reading the wav
directly avoids PyAV container errors seen on the cloud box (20 Oct 2026)."""
import json, sys, wave
import numpy as np
from faster_whisper import WhisperModel

model = WhisperModel(sys.argv[3] if len(sys.argv) > 3 else "base.en", device="cpu", compute_type="int8")
wf = wave.open(sys.argv[1])
audio = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
segs, _ = model.transcribe(audio, word_timestamps=True, vad_filter=False)
words = [{"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)} for s in segs for w in s.words]
json.dump(words, open(sys.argv[2], "w"))
print(len(words), "words")

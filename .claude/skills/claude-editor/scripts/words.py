import sys, wave, json, numpy as np
from faster_whisper import WhisperModel
w=wave.open(sys.argv[1]); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
m=WhisperModel(sys.argv[3] if len(sys.argv)>3 else "medium.en",device="cpu",compute_type="int8")
segs,_=m.transcribe(a,beam_size=5,word_timestamps=True)
out=[{"w":x.word,"s":round(x.start,2),"e":round(x.end,2)} for s in segs for x in s.words]
json.dump(out,open(sys.argv[2],"w"),indent=0)

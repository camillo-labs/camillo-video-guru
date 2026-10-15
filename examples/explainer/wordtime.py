import json, pathlib
from faster_whisper import WhisperModel
W = pathlib.Path(__file__).parent / "work"
m = WhisperModel("base.en", device="cpu", compute_type="int8")
import subprocess, numpy as np
raw = subprocess.run(["ffmpeg","-v","error","-i",str(W/"narration.wav"),"-f","f32le","-ac","1","-ar","16000","-"],capture_output=True).stdout
segs, _ = m.transcribe(np.frombuffer(raw,np.float32), word_timestamps=True, language="en")
words = [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for s in segs for w in s.words]
json.dump(words, open(W / "words.json", "w")); print(len(words)); print(" ".join(x["w"] for x in words))

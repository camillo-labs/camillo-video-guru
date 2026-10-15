"""Lay the twelve takes on a timeline (0.6 s lead, 0.3 s gaps), write narration.wav and starts.json."""
import json, subprocess, wave, numpy as np, pathlib
W = pathlib.Path(__file__).parent / "work"; SR = 44100
lines = json.load(open(W / "lines.json")); out = [np.zeros(int(0.6 * SR))]; t = 0.6; starts = []
for i in range(1, len(lines) + 1):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(W / f"line{i:02d}.mp3"), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    # trim silence at the ends of the take
    a = np.abs(x); idx = np.where(a > 0.01)[0]; x = x[max(idx[0] - int(0.03 * SR), 0): idx[-1] + int(0.08 * SR)]
    starts.append((t, t + len(x) / SR)); out.append(x); out.append(np.zeros(int(0.3 * SR))); t += len(x) / SR + 0.3
out.append(np.zeros(int(1.2 * SR))); y = np.concatenate(out); y = y / max(np.abs(y).max(), 1e-9) * 0.89
with wave.open(str(W / "narration.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype("<i2").tobytes())
json.dump(starts, open(W / "starts.json", "w")); print(len(y) / SR, starts)

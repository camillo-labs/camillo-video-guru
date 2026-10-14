"""Build a finished soundtrack and mux it onto a silent render, with the rules that survived a very picky client:
- voice: pauses inserted at the quietest 10 ms inside each gap, 60 ms fade-out / 15 ms fade-in (no abrupt cuts);
- sound effects: band-limited, sin^2/cos^2 faded, placed so their loudness peak lands on the cut (or their start, for
  impacts), levels relative to the voice's speaking level;
- music: one constant level relative to the voice (no ducking), muted only for the hush, faded at the end;
- loudness: one measured static gain to the target (never single-pass loudnorm, it pumps), then a gentle limiter.

Usage:  python -I mix_soundtrack.py <config.json>
config.json:
{
  "video": "silent_render.mp4", "out": "final.mp4", "target_lufs": -14,
  "voice": {"file": "vo.mp3", "pauses": [[16.52, 1.2], [18.88, 1.2]]},       # [voice-time seconds, pause length]
  "music": {"file": "score.mp3", "db": -12, "hush": [25.87, 28.52], "tail_fade": 1.0},   # film-time seconds
  "sfx": [ {"file": "whoosh.mp3", "at": 8.75, "db": -22},
           {"file": "impact.mp3", "at": 4.56, "db": -17, "lo": 40, "hi": 3500, "fin": 0.02, "fout": 0.6, "align": "start"} ],
  "ambience": [ {"file": "heli.mp3", "at": 16.27, "db": -11, "lo": 60, "hi": 7000, "fin": 0.35, "fout": 0.45} ]
}
Times for sfx/music/ambience are film time (after pauses). Picture and mixer must share the same pause list."""
import json
import os
import re
import subprocess
import sys
import tempfile

import numpy as np

SR = 48000
cfg = json.load(open(sys.argv[1], encoding="utf-8"))


def decode(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<f4").reshape(-1, 2).astype(np.float64)


def rms(x):
    return float(np.sqrt((x ** 2).mean() + 1e-12))


total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", cfg["video"]], capture_output=True, text=True).stdout)
N = int(total * SR)
mix = np.zeros((N, 2))
blk = SR // 20

# ---- voice with pauses
vo = decode(cfg["voice"]["file"])
pauses = sorted(cfg["voice"].get("pauses", []))


def quiet_point(at):
    w = SR // 100
    a0, a1 = max(0, int((at - 0.25) * SR)), min(len(vo) - w, int((at + 0.25) * SR))
    e = [float((vo[i:i + w] ** 2).mean()) for i in range(a0, a1, w // 2)]
    return (a0 + int(np.argmin(e)) * (w // 2) + w // 2) / SR, 10 * np.log10(min(e) + 1e-12)


cuts = []
for at, d in pauses:
    q, lvl = quiet_point(at)
    cuts.append((q, d))
    print(f"pause {d:.2f}s at {q:.2f}s (silence {lvl:.0f} dB){'  <-- NOT SILENT' if lvl > -60 else ''}")
edges = [0.0] + [q for q, _ in cuts] + [len(vo) / SR]
fo, fi = int(0.06 * SR), int(0.015 * SR)
voice = np.zeros((N, 2))
for k in range(len(edges) - 1):
    a, b = int(edges[k] * SR), int(edges[k + 1] * SR)
    off = int(sum(d for q, d in cuts if edges[k] >= q) * SR)
    piece = vo[a:b].copy()
    if k > 0 and len(piece) > fi:
        piece[:fi] *= np.linspace(0, 1, fi)[:, None]
    if k < len(edges) - 2 and len(piece) > fo:
        piece[-fo:] *= np.linspace(1, 0, fo)[:, None]
    piece = piece[: max(0, N - (a + off))]
    voice[a + off:a + off + len(piece)] += piece
vb = np.array([rms(voice[i:i + blk]) for i in range(0, N - blk, blk)])
speak = rms(vb[vb > 10 ** (-40 / 20)])
mix += voice


def put(sig, t0, gain):
    i = int(round(t0 * SR))
    a, b = max(0, i), min(N, i + len(sig))
    if b > a:
        mix[a:b] += sig[a - i:b - i] * gain


def shape(x, lo, hi, fin, fout):
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    h = 1 / np.sqrt(1 + (f / hi) ** 4) / np.sqrt(1 + (lo / np.maximum(f, 1e-6)) ** 4)  # 2nd-order roll-offs, zero phase
    y = np.fft.irfft(X * h[:, None], len(x), axis=0)
    env = np.ones(len(y))
    a, b = int(fin * SR), int(fout * SR)
    if a:
        env[:a] = np.sin(np.linspace(0, np.pi / 2, a)) ** 2
    if b:
        env[-b:] *= np.cos(np.linspace(0, np.pi / 2, b)) ** 2
    return y * env[:, None]


def place(item, default_lo=150, default_hi=5000, default_fin=0.08, default_fout=0.25):
    x = shape(decode(item["file"]), item.get("lo", default_lo), item.get("hi", default_hi), item.get("fin", default_fin), item.get("fout", default_fout))
    e = np.array([rms(x[i:i + blk]) for i in range(0, max(1, len(x) - blk), blk)])
    pk = int(np.argmax(e)) * blk / SR if item.get("align", "peak") == "peak" else 0.0
    level = rms(x[max(0, int(pk * SR) - blk * 2): int(pk * SR) + blk * 2]) if item.get("align", "peak") == "peak" else rms(x)
    put(x, item["at"] - pk, speak / level * 10 ** (item["db"] / 20))


for s in cfg.get("sfx", []):
    place(s)
for s in cfg.get("ambience", []):
    place({**s, "align": "start"}, 60, 7000, 0.35, 0.45)

# ---- music at one constant level
if cfg.get("music"):
    m = cfg["music"]
    mu = decode(m["file"])
    mu = np.vstack([mu, np.zeros((max(0, N - len(mu)), 2))])[:N]
    h0, h1 = m.get("hush", [total + 1, total + 1])
    mb = np.array([rms(mu[i:i + blk]) for i in range(0, int(min(h0, total) * SR) - blk, blk)])
    mg = speak / rms(mb[mb > 10 ** (-50 / 20)]) * 10 ** (m.get("db", -13) / 20)
    t = np.arange(N) / SR
    env = np.ones(N)
    f1 = (t >= h0 - 0.3) & (t < h0)
    env[f1] = np.cos(np.linspace(0, np.pi / 2, f1.sum())) ** 2
    env[(t >= h0) & (t < h1)] = 0
    f2 = (t >= h1) & (t < h1 + 0.08)
    env[f2] = np.sin(np.linspace(0, np.pi / 2, f2.sum())) ** 2
    tail = t > t[-1] - m.get("tail_fade", 1.0)
    env[tail] *= np.cos(np.linspace(0, np.pi / 2, tail.sum())) ** 2
    mix += mu * mg * env[:, None]

# ---- one static gain to target, gentle limiter, mux
tmp = os.path.join(tempfile.gettempdir(), "mix_soundtrack_tmp.wav")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", tmp], input=np.clip(mix, -1, 1).astype("<f4").tobytes(), check=True)
meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", tmp, "-af", f"loudnorm=I={cfg.get('target_lufs', -14)}:TP=-1.5:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
mm = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", meas, re.S).group(0))
gain = cfg.get("target_lufs", -14) - float(mm["input_i"])
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", cfg["video"], "-i", tmp, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-af", f"volume={gain:.2f}dB,alimiter=limit=0.84:attack=5:release=80:level=false", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                "-movflags", "+faststart", cfg["out"]], check=True)
os.remove(tmp)
print(f"static gain {gain:+.1f} dB -> {cfg['out']}")

"""Make a music track long enough for the film by repeating whole bars, joined on bar lines.
Pick a loop that starts and ends on bar lines in a steady part of the track (no build or drop inside it). The loop is
played again right after itself as often as needed, with 15 ms equal-power crossfades at the joins, and the rest of
the track follows. It then reports the largest sample step at each join next to the track's 99.9th percentile, so a
click shows up as a join far above it. Used for the Nightcrew tour cut: a 40 s track trimmed to 32.8 s, film 42 s.
Usage: python -I extend_music.py <in.mp3> <out.wav> <loop_start_s> <loop_end_s> <length_s>"""
import subprocess
import sys

import numpy as np

SR = 48000
src, dst = sys.argv[1], sys.argv[2]
loop_start, loop_end, length = (float(x) for x in sys.argv[3:6])

raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
mu = np.frombuffer(raw, dtype="<f4").reshape(-1, 2).astype(np.float64)
a, b, n = int(loop_start * SR), int(loop_end * SR), int(length * SR)
loop = mu[a:b].copy()
x = int(0.015 * SR)
fade_in = np.sin(np.linspace(0, np.pi / 2, x))[:, None]
fade_out = np.cos(np.linspace(0, np.pi / 2, x))[:, None]
copies = max(0, int(np.ceil((n - len(mu)) / (len(loop) - x))))
joined, rest = mu[:b].copy(), mu[b:].copy()
joins = []
for _ in range(copies):
    joins.append(len(joined) - x)
    joined = np.vstack([joined[:-x], joined[-x:] * fade_out + loop[:x] * fade_in, loop[x:]])
joins.append(len(joined) - x)
out = np.vstack([joined[:-x], joined[-x:] * fade_out + rest[:x] * fade_in, rest[x:]])

mono = out.mean(axis=1)
step = np.abs(np.diff(mono))
p999 = np.percentile(step, 99.9)
for j in joins if copies else []:
    w = step[max(0, j - SR // 50): j + SR // 50]
    print(f"join at {j / SR:.2f} s: max step {w.max():.3f} (track 99.9th percentile {p999:.3f})")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", dst],
               input=np.clip(out, -1, 1).astype("<f4").tobytes(), check=True)
print(f"{dst}: {len(out) / SR:.2f} s ({copies} extra loop(s) of {loop_end - loop_start:.2f} s)")

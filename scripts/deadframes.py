"""Find dead (frozen) stretches in a rendered video, (dead-frame hunting).
Decodes grey frames at 96x160, takes the 99th percentile of 8x8 block differences between consecutive frames, and
reports runs of at least 0.5 s where that stays under eps (0-255 scale).
Usage: python -I deadframes.py video.mp4 [eps] [min_seconds]"""
import subprocess
import sys

import numpy as np

path = sys.argv[1]
eps = float(sys.argv[2]) if len(sys.argv) > 2 else 0.6
min_s = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
W, H, FPS = 96, 160, 30
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={FPS},scale={W}:{H}", "-pix_fmt", "gray", "-f", "rawvideo", "-"], capture_output=True).stdout
a = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
d = np.abs(np.diff(a, axis=0)).reshape(-1, H // 8, 8, W // 8, 8).mean((2, 4))
score = np.percentile(d.reshape(len(d), -1), 99, axis=1)
dead = score < eps
runs, i = [], 0
while i < len(dead):
    if dead[i]:
        j = i
        while j < len(dead) and dead[j]:
            j += 1
        if (j - i) / FPS >= min_s:
            runs.append((i / FPS, j / FPS))
        i = j
    else:
        i += 1
print(f"{len(a)} frames, {len(runs)} dead runs >= {min_s}s (eps {eps})")
for t0, t1 in runs:
    print(f"  {t0:6.2f}-{t1:6.2f}s  ({t1 - t0:.2f}s)")

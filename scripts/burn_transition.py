"""Ridged-burn shader transition spliced onto a silent render: a numpy port of the HyperFrames `ridged-burn` shader
(github.com/heygen-com/hyperframes, Apache-2.0). Ridged fractal noise decides where scene A burns away into scene B,
with a thin blackbody-coloured glowing edge and a few ember sparks. A = the frames before the cut (the last one held),
B = the frames from the cut (the first one held before it). Assumes 1080x1920 at 30 fps (edit W, H, FPS below).
Usage: python -I burn_transition.py <in.mp4> <out.mp4> <cut_frame> [first_frame=cut-2] [length=16]
Tuning used in the case study: heat width 0.06, glow gain 1.1, sparks 0.35, 20 frames starting 4 before the cut."""
import subprocess
import sys

import numpy as np

src, out = sys.argv[1], sys.argv[2]
CUT = int(sys.argv[3])
A0 = int(sys.argv[4]) if len(sys.argv) > 4 else CUT - 2
LEN = int(sys.argv[5]) if len(sys.argv) > 5 else 16
W, H, FPS = 1080, 1920, 30


def frames(a, b):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-vf", f"select='between(n\\,{a}\\,{b - 1})'", "-vsync", "0",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.uint8).reshape(-1, H, W, 3).astype(np.float32) / 255


fr = frames(A0, A0 + LEN)
lastA, firstB = fr[CUT - 1 - A0], fr[CUT - A0]


def hash2(x, y):
    return np.modf(np.sin(x * 127.1 + y * 311.7) * 43758.5453)[0] % 1.0


def vnoise(x, y):
    ix, iy = np.floor(x), np.floor(y)
    fx, fy = x - ix, y - iy
    fx = fx * fx * fx * (fx * (fx * 6 - 15) + 10)
    fy = fy * fy * fy * (fy * (fy * 6 - 15) + 10)
    a, b = hash2(ix, iy), hash2(ix + 1, iy)
    c, d = hash2(ix, iy + 1), hash2(ix + 1, iy + 1)
    return (a + (b - a) * fx) * (1 - fy) + (c + (d - c) * fx) * fy


def ridged(x, y):
    v, amp = 0.0, 0.5
    for _ in range(5):
        v = v + amp * np.abs(vnoise(x, y) * 2 - 1)
        x, y = 0.8 * x + 0.6 * y, -0.6 * x + 0.8 * y
        x, y = x * 2.02, y * 2.02
        amp *= 0.5
    return v


u = (np.arange(W) + 0.5) / W
v = (np.arange(H) + 0.5) / H
U, V = np.meshgrid(u, v)
n = ridged(U * 4, V * 4 * H / W).astype(np.float32)
n = (n - n.min()) / (n.max() - n.min()) * 0.9 + 0.02  # spread the field so the burn sweeps the whole frame
spark_field = vnoise(U * 80, V * 80 * H / W).astype(np.float32)


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


outf = []
for i in range(LEN):
    f = A0 + i
    A = fr[i] if f < CUT else lastA
    B = fr[i] if f >= CUT else firstB
    t = i / (LEN - 1)
    p = 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2
    p = p * 1.0
    e = smooth(p - 0.04, p + 0.04, n)
    heat = smooth(0.06, 0.0, np.abs(n - p)) * (0.0 if p >= 1 else 1.0)
    burn = np.stack([0.4 + 0.6 * smooth(0, 0.25, heat), 0.4 * smooth(0, 0.25, heat), np.zeros_like(heat)], -1)
    burn = burn + (np.array([1, 0.85, 0.3]) - burn) * smooth(0.25, 0.5, heat)[..., None]
    burn = burn + (1 - burn) * smooth(0.5, 1.0, heat)[..., None]
    sparks = (spark_field > 0.92) * heat * 3
    img = B + (A - B) * e[..., None] + burn * heat[..., None] * 1.1 + np.array([1, 0.7, 0.3]) * sparks[..., None] * 0.35
    outf.append((np.clip(img, 0, 1) * 255).astype(np.uint8))
seg = np.stack(outf)

# splice: [0, A0) original + transition + [A0+LEN, end) original
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-filter_complex", f"[0:v]trim=end_frame={A0},setpts=PTS-STARTPTS[a];[1:v]format=yuv420p,setpts=PTS-STARTPTS[t];"
                          f"[0:v]trim=start_frame={A0 + LEN},setpts=PTS-STARTPTS[b];[a][t][b]concat=n=3:v=1:a=0[v]",
       "-map", "[v]", "-c:v", "libx264", "-crf", "22", "-maxrate", "6M", "-bufsize", "12M", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
subprocess.run(cmd, input=seg.tobytes(), check=True)
print("spliced", LEN, "frames at", A0, "->", out)

"""Check a Remotion render frame by frame against direct stills of the same frames.
Parallel rendering can draw a frame differently from a single still (seen in the Nightcrew film: SVG text inside a
CSS-scaled layer came out at a stale scale in some frames). For each frame this renders `remotion still`, decodes the
same frame from the video, and prints the mean absolute difference (0-255, greyscale). Encoding alone gives about
1-3; a wrong frame gives much more. Frames above the limit are flagged and saved side by side for a look.
Usage: python -I framecheck.py <remotion project dir> <composition id> <video.mp4> <frame> [<frame> ...]
       [--scale 0.5] [--limit 5]"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image

args = sys.argv[1:]
scale, limit = 0.5, 5.0
if "--scale" in args:
    i = args.index("--scale")
    scale = float(args[i + 1])
    del args[i:i + 2]
if "--limit" in args:
    i = args.index("--limit")
    limit = float(args[i + 1])
    del args[i:i + 2]
project, comp, video = args[:3]
frames = [int(x) for x in args[3:]]
out = os.path.join(os.path.dirname(os.path.abspath(video)), "framecheck")
os.makedirs(out, exist_ok=True)
cli = os.path.join(project, "node_modules", "@remotion", "cli", "remotion-cli.js")
bad = 0
for fr in frames:
    still = os.path.join(out, f"{comp}-{fr}-still.png")
    subprocess.run(["node", cli, "still", "src/index.ts", comp, still, f"--frame={fr}", f"--scale={scale}", "--log=error"],
                   cwd=project, check=True, stdin=subprocess.DEVNULL, capture_output=True)
    dec = os.path.join(out, f"{comp}-{fr}-video.png")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", video, "-vf", f"select=eq(n\\,{fr})", "-frames:v", "1", dec],
                   check=True, stdin=subprocess.DEVNULL)
    a = Image.open(still).convert("L")
    b = Image.open(dec).convert("L").resize(a.size)
    diff = float(np.abs(np.asarray(a, np.float32) - np.asarray(b, np.float32)).mean())
    flag = diff > limit
    bad += flag
    if flag:
        pair = Image.new("RGB", (a.width * 2 + 10, a.height), (80, 80, 80))
        pair.paste(Image.open(still).convert("RGB"), (0, 0))
        pair.paste(Image.open(dec).convert("RGB").resize(a.size), (a.width + 10, 0))
        pair.save(os.path.join(out, f"{comp}-{fr}-pair.png"))
    print(f"frame {fr}: mean diff {diff:.2f}{'  <-- check ' + comp + '-' + str(fr) + '-pair.png' if flag else ''}")
print(f"{bad} of {len(frames)} frames over {limit}")
sys.exit(1 if bad else 0)

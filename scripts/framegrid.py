"""Contact sheet of frames from one or two videos, with timestamps.

  framegrid.py a.mp4 --out sheet.png --n 12 --cols 6          evenly spaced frames
  framegrid.py a.mp4 --times 1.2,3.4,5 --out sheet.png        chosen times
  framegrid.py render.mp4 --ref reference.mp4 --out cmp.png   two rows per pair: reference on top, render below
  --t0/--t1 restrict the span, --h sets cell height (default 360).
"""
import argparse, subprocess, tempfile, os
import numpy as np
from PIL import Image, ImageDraw


def grab(path, t, h):
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f: out = f.name
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', path, '-frames:v', '1', '-vf', f'scale=-2:{h}', out], check=False)
    try: im = Image.open(out).convert('RGB')
    except Exception: im = Image.new('RGB', (h * 9 // 16, h), (40, 0, 40))
    os.unlink(out); return im


def dur(path):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout.strip() or 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video'); ap.add_argument('--ref'); ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=12); ap.add_argument('--cols', type=int, default=6)
    ap.add_argument('--times'); ap.add_argument('--t0', type=float, default=0.0); ap.add_argument('--t1', type=float)
    ap.add_argument('--h', type=int, default=360)
    a = ap.parse_args()
    D = dur(a.video); t1 = a.t1 or D
    ts = [float(x) for x in a.times.split(',')] if a.times else list(np.linspace(a.t0, max(a.t0, t1 - 0.1), a.n))
    rows = []
    def strip(path, tl, label):
        ims = [grab(path, t, a.h) for t in tl]
        for im, t in zip(ims, tl): ImageDraw.Draw(im).text((6, 4), f'{label} {t:.2f}s', fill=(255, 255, 0))
        return ims
    ims = strip(a.video, ts, 'R')
    if a.ref:
        rd = dur(a.ref); rts = [min(t * rd / max(D, 1e-6), rd - 0.05) for t in ts]
        refims = strip(a.ref, rts, 'REF')
        cells = []
        for r, m in zip(refims, ims): cells += [r, m]
        cols = a.cols
        pair_rows = [(refims[i:i + cols], ims[i:i + cols]) for i in range(0, len(ims), cols)]
        rows = [x for p in pair_rows for x in p]
    else:
        rows = [ims[i:i + a.cols] for i in range(0, len(ims), a.cols)]
    cw = max(i.width for r in rows for i in r)
    W = cw * a.cols; Hh = a.h * len(rows)
    sheet = Image.new('RGB', (W, Hh), (20, 20, 20))
    for ri, r in enumerate(rows):
        for ci, im in enumerate(r): sheet.paste(im, (ci * cw, ri * a.h))
    sheet.save(a.out)
    print(a.out, sheet.size)


main()

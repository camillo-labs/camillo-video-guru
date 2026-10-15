"""Self-generated test footage, so demos never redistribute anyone's video.

python gen_clips.py --set A --out clips_A --aspect 9:16
Each set makes eight 4 to 6 second clips with different motion energy, and one clip with a moving figure plus
a person mask (name.mask.mp4) for the text-behind-subject styles.
"""
import argparse, os, subprocess
from pathlib import Path
import numpy as np
import cv2

PAL = {
    'A': [(46, 77, 255), (46, 176, 255), (147, 46, 255), (230, 200, 40), (40, 40, 120)],      # BGR warm sunset
    'B': [(255, 180, 60), (200, 120, 30), (240, 240, 240), (120, 200, 90), (60, 40, 20)],     # BGR cool blue and teal
}


def lerp_pal(p, x):
    x = np.mod(x, 1.0) * len(p)
    i = np.floor(x).astype(int) % len(p); f = (x - np.floor(x))[..., None]
    P = np.array(p, np.float32)
    return P[i] * (1 - f) + P[(i + 1) % len(p)] * f


def plasma(W, H, pal, speed):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    xx /= W; yy /= H
    def fr(t):
        v = np.sin(6 * xx + t * speed) + np.sin(5 * yy - t * speed * 1.3) + np.sin(4 * (xx + yy) + t * speed * 0.7) + np.sin(np.hypot(xx - .5, yy - .5) * 12 - t * speed * 2)
        return lerp_pal(pal, v / 8 + 0.5 + t * 0.05).astype(np.uint8)
    return fr


def metaballs(W, H, pal, speed, seed):
    rng = np.random.default_rng(seed)
    n = 6; ph = rng.uniform(0, 6.28, (n, 2)); fq = rng.uniform(0.5, 1.5, (n, 2)); r = rng.uniform(0.08, 0.16, n)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); xx /= W; yy /= W
    def fr(t):
        f = np.zeros((H, W), np.float32)
        for i in range(n):
            cx = 0.5 + 0.38 * np.sin(t * speed * fq[i, 0] + ph[i, 0]); cy = (H / W) * (0.5 + 0.38 * np.sin(t * speed * fq[i, 1] + ph[i, 1]))
            f += r[i] ** 2 / ((xx - cx) ** 2 + (yy - cy) ** 2 + 1e-4)
        c = lerp_pal(pal, np.clip(f, 0, 3) / 3 * 0.8 + 0.1 + t * 0.03)
        return np.clip(c * np.clip(f, 0.2, 1.4)[..., None] ** 0.5, 0, 255).astype(np.uint8)
    return fr


def grid(W, H, pal, speed):
    def fr(t):
        img = np.zeros((H, W, 3), np.uint8)
        hz = int(H * 0.55)
        for y in range(hz):
            img[y] = (np.array(pal[4]) * (0.4 + 0.6 * y / hz)).astype(np.uint8)
        cv2.circle(img, (W // 2, hz - int(H * 0.08)), int(W * 0.28), pal[1], -1)
        img[hz:] = (np.array(pal[4]) * 0.5).astype(np.uint8)
        for i in range(-12, 13):
            cv2.line(img, (W // 2, hz), (int(W / 2 + i * W * 0.28), H), pal[2], 2)
        z = (t * speed * 0.6) % 1.0
        for k in range(14):
            d = (k + z) / 14.0
            y = int(hz + (H - hz) * d ** 2.2)
            cv2.line(img, (0, y), (W, y), pal[0], 2)
        return img
    return fr


def shapes(W, H, pal, speed, seed):
    rng = np.random.default_rng(seed)
    n = 9; pos = rng.uniform(0.1, 0.9, (n, 2)); vel = rng.uniform(-0.4, 0.4, (n, 2)); sz = rng.uniform(0.06, 0.16, n); col = rng.integers(0, len(pal), n)
    def fr(t):
        img = np.full((H, W, 3), pal[4], np.uint8)
        for i in range(n):
            p = (pos[i] + vel[i] * t * speed) % 1.0
            c = (int(p[0] * W), int(p[1] * H)); s = int(sz[i] * W)
            if i % 3 == 0: cv2.circle(img, c, s, pal[col[i]], -1)
            elif i % 3 == 1: cv2.rectangle(img, (c[0] - s, c[1] - s), (c[0] + s, c[1] + s), pal[col[i]], -1)
            else:
                a = t * speed + i; pts = np.array([[c[0] + s * 1.4 * np.cos(a + k * 2.094), c[1] + s * 1.4 * np.sin(a + k * 2.094)] for k in range(3)], np.int32)
                cv2.fillPoly(img, [pts], pal[col[i]])
        return img
    return fr


def stars(W, H, pal, speed, seed):
    rng = np.random.default_rng(seed)
    n = 300; p = rng.uniform(-1, 1, (n, 2)); z0 = rng.uniform(0, 1, n)
    def fr(t):
        img = np.zeros((H, W, 3), np.uint8); img[:] = (np.array(pal[4]) * 0.4).astype(np.uint8)
        z = (z0 - t * speed * 0.25) % 1.0
        for i in range(n):
            s = 1 / (z[i] + 0.05)
            x = int(W / 2 + p[i, 0] * s * W * 0.06); y = int(H / 2 + p[i, 1] * s * H * 0.06)
            if 0 <= x < W and 0 <= y < H:
                cv2.circle(img, (x, y), max(1, int(2.5 * (1 - z[i]) + 1)), pal[i % 4], -1)
        return img
    return fr


def fabric(W, H, pal, speed, seed):
    rng = np.random.default_rng(seed)
    base = rng.standard_normal((H // 4, W // 4)).astype(np.float32)
    base = cv2.GaussianBlur(base, (0, 0), 1.2); base = cv2.resize(base, (W * 2, H * 2))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    def fr(t):
        ox = int(t * speed * 40) % W; oy = int(t * speed * 15) % H
        v = base[oy:oy + H, ox:ox + W]
        weave = 0.25 * np.sin(xx * 0.9) * np.sin(yy * 0.9)
        v = v * 0.25 + weave + np.sin((xx + yy) * 0.01 + t * speed) * 0.5
        return lerp_pal(pal, v * 0.25 + 0.3).astype(np.uint8)
    return fr


def figure(W, H, pal, speed, seed):
    """Stylised dancing figure on a gradient, returns (frame, mask)."""
    bg = lerp_pal(pal, np.linspace(0, 0.6, H)[:, None] * np.ones((1, W))).astype(np.uint8)
    def fr(t):
        img = bg.copy(); m = np.zeros((H, W), np.uint8)
        cx = int(W * (0.5 + 0.12 * np.sin(t * speed * 0.8))); s = H * 0.0011 * 700 / 700 * W / 720 * 1.0
        S = W * 0.0014
        def draw(canvas, col):
            by = int(H * 0.6)
            sw = np.sin(t * speed * 3)
            cv2.circle(canvas, (cx, int(by - 190 * S * 1.0 - 120 * S)), int(60 * S), col, -1)                     # head
            cv2.fillPoly(canvas, [np.array([[cx - 90 * S, by - 230 * S], [cx + 90 * S, by - 230 * S], [cx + 70 * S, by + 90 * S], [cx - 70 * S, by + 90 * S]], np.int32)], col)
            for sgn in (-1, 1):
                ang = 0.9 * sw * sgn
                sx, sy = cx + sgn * 85 * S, by - 210 * S
                ex, ey = sx + np.sin(ang + sgn * 0.7) * 170 * S, sy + np.cos(ang + sgn * 0.7) * 170 * S
                cv2.line(canvas, (int(sx), int(sy)), (int(ex), int(ey)), col, int(34 * S))
                lx, ly = cx + sgn * 40 * S, by + 80 * S
                cv2.line(canvas, (int(lx), int(ly)), (int(lx + np.sin(-ang) * 90 * S), int(ly + 260 * S)), col, int(40 * S))
        draw(img, (25, 25, 30)); draw(m, 255)
        cv2.rectangle(img, (int(cx - 45 * S), int(H * 0.6 - 335 * S)), (int(cx + 45 * S), int(H * 0.6 - 305 * S)), (230, 230, 120), -1)  # visor
        return img, m
    return fr


def write(name, W, H, frames, fps, out, masks=None):
    def pipe(path, gray):
        cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'gray' if gray else 'bgr24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
               '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-preset', 'fast', str(path)]
        return subprocess.Popen(cmd, stdin=subprocess.PIPE)
    p = pipe(out / f'{name}.mp4', False); pm = pipe(out / f'{name}.mask.mp4', True) if masks else None
    for f in frames:
        if masks:
            img, m = f; p.stdin.write(img.tobytes()); pm.stdin.write(m.tobytes())
        else:
            p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()
    if pm: pm.stdin.close(); pm.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--set', default='A'); ap.add_argument('--out', required=True)
    ap.add_argument('--aspect', default='9:16'); ap.add_argument('--height', type=int, default=960)
    ap.add_argument('--fps', type=int, default=30)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    aw, ah = map(int, a.aspect.split(':'))
    H = a.height if ah >= aw else a.height; W = int(round(H * aw / ah / 2) * 2)
    if ah < aw: H = a.height; W = int(round(H * aw / ah / 2) * 2)
    pal = PAL[a.set]; seed0 = 10 if a.set == 'A' else 50
    spec = [('plasma_slow', lambda: plasma(W, H, pal, 0.8), 5.0), ('plasma_fast', lambda: plasma(W, H, pal, 3.0), 4.0),
            ('metaballs', lambda: metaballs(W, H, pal, 1.2, seed0), 5.0), ('grid', lambda: grid(W, H, pal, 1.6), 5.0),
            ('shapes_fast', lambda: shapes(W, H, pal, 2.2, seed0 + 1), 4.0), ('stars', lambda: stars(W, H, pal, 1.5, seed0 + 2), 5.0),
            ('fabric', lambda: fabric(W, H, pal, 1.0, seed0 + 3), 5.0), ('figure', lambda: figure(W, H, pal, 1.4, seed0 + 4), 6.0)]
    for name, mk, dur in spec:
        f = mk(); n = int(dur * a.fps)
        if name == 'figure':
            write(name, W, H, (f(i / a.fps) for i in range(n)), a.fps, out, masks=True)
        else:
            write(name, W, H, (f(i / a.fps) for i in range(n)), a.fps, out)
        print('wrote', name)


if __name__ == '__main__':
    main()

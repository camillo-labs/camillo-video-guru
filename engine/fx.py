"""Frame effects for the edit engine.

Every effect is fn(img, k, p, ctx) -> img with img a uint8 BGR array.
  k   dict: u (0..1 progress through the effect span), x (-1..1 around a cut, 0 at the cut), t (seconds into the span),
      span (span length in seconds)
  p   the effect's parameter dict from the style file
  ctx dict: w, h, fps, frame (output frame index), rng (numpy Generator seeded per frame), mask (float HxW 0..1 of the
      subject or None), store (dict persisting across frames of one render)
Add an effect with @fx('name'). Styles refer to effects by name, see styles in edits/<name>/style.json.
"""
import numpy as np
import cv2

FX = {}


def fx(name):
    def deco(f):
        FX[name] = f
        return f
    return deco


def ease(name, u):
    u = float(np.clip(u, 0, 1))
    if name == 'linear': return u
    if name == 'in_cubic': return u ** 3
    if name == 'out_cubic': return 1 - (1 - u) ** 3
    if name == 'out_expo': return 1 - 2 ** (-10 * u) if u < 1 else 1.0
    if name == 'in_out': return 3 * u * u - 2 * u ** 3
    if name == 'out_back':
        c1 = 1.70158; c3 = c1 + 1
        return 1 + c3 * (u - 1) ** 3 + c1 * (u - 1) ** 2
    if name == 'in_expo': return 0.0 if u == 0 else 2 ** (10 * u - 10)
    return u


def prof(name, u, peak=0.5):
    """Envelope 0..1..0 or decays. tri: rises to the peak then falls. decay: 1 at start falling to 0. attack: 0 to 1."""
    u = float(np.clip(u, 0, 1))
    if name == 'tri':
        return u / peak if u < peak else (1 - u) / (1 - peak)
    if name == 'decay': return (1 - u) ** 2
    if name == 'attack': return u ** 2
    if name == 'hold': return 1.0
    return 1.0


def zoom_img(img, s, cx=0.5, cy=0.5, dx=0.0, dy=0.0, rot=0.0):
    h, w = img.shape[:2]
    if abs(s - 1) < 1e-4 and dx == 0 and dy == 0 and rot == 0: return img
    M = cv2.getRotationMatrix2D((cx * w, cy * h), rot, s)
    M[0, 2] += dx; M[1, 2] += dy
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def hsv_sat(img, s):
    if abs(s - 1) < 1e-3: return img
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * s, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


# ---------------------------------------------------------------- camera moves

@fx('punch_in')
def punch_in(img, k, p, ctx):
    e = ease(p.get('ease', 'out_cubic'), k['u'])
    s = p.get('from', 1.0) + (p.get('to', 1.15) - p.get('from', 1.0)) * e
    return zoom_img(img, s, p.get('cx', 0.5), p.get('cy', 0.5))


@fx('zoom_pulse')
def zoom_pulse(img, k, p, ctx):
    a = p.get('amount', 0.06) * prof(p.get('shape', 'decay'), k['u'])
    return zoom_img(img, 1 + a, p.get('cx', 0.5), p.get('cy', 0.5))


@fx('slow_zoom')
def slow_zoom(img, k, p, ctx):
    s = p.get('from', 1.0) + (p.get('to', 1.12) - p.get('from', 1.0)) * ease(p.get('ease', 'linear'), k['u'])
    return zoom_img(img, s, p.get('cx', 0.5), p.get('cy', 0.5))


@fx('shake')
def shake(img, k, p, ctx):
    a = p.get('amount', 0.02) * prof('decay', k['u']) * ctx['w']
    r = ctx['rng']
    return zoom_img(img, 1.0 + p.get('zoom', 0.04), 0.5, 0.5, r.uniform(-a, a), r.uniform(-a, a), r.uniform(-1, 1) * p.get('rot', 0.6) * prof('decay', k['u']))


@fx('drift')
def drift(img, k, p, ctx):
    """Slow pan across the frame (stills and static shots). dir in degrees, amount as a fraction of width."""
    a = np.deg2rad(p.get('dir', 0)); amt = p.get('amount', 0.06) * (k['u'] - 0.5)
    return zoom_img(img, p.get('scale', 1.12), 0.5, 0.5, np.cos(a) * amt * ctx['w'], np.sin(a) * amt * ctx['h'])


# ---------------------------------------------------------------- transitions (centred on a cut)

def motion_blur_h(img, n):
    n = int(max(1, n))
    if n <= 1: return img
    k = np.zeros((1, n), np.float32); k[0, :] = 1.0 / n
    return cv2.filter2D(img, -1, k, borderType=cv2.BORDER_REFLECT)


@fx('whip')
def whip(img, k, p, ctx):
    """Whip pan: before the cut the frame slides out with horizontal blur, after the cut the next shot slides in."""
    w = ctx['w']; x = k['x']                      # -1 .. 1
    d = p.get('dir', 1)
    e = ease('in_cubic', abs(x)) if x < 0 else ease('in_cubic', abs(x))
    # strength is highest at the cut (x = 0)
    s = 1 - abs(x)
    s = s ** p.get('power', 1.5)
    dx = -d * w * p.get('shift', 0.35) * s * (1 if x < 0 else -1)
    out = zoom_img(img, 1.0 + 0.05 * s, 0.5, 0.5, dx, 0)
    return motion_blur_h(out, 1 + p.get('blur', 0.12) * w * s)


@fx('zoom_blur')
def zoom_blur(img, k, p, ctx):
    s = (1 - abs(k['x'])) ** p.get('power', 1.2)
    amt = p.get('amount', 0.18) * s
    if amt < 0.004: return img
    n = int(p.get('samples', 8))
    acc = np.zeros(img.shape, np.float32)
    for i in range(n):
        sc = 1 + amt * (i / (n - 1))
        acc += zoom_img(img, sc, p.get('cx', 0.5), p.get('cy', 0.5)).astype(np.float32)
    out = (acc / n).astype(np.uint8)
    return out


@fx('flash')
def flash(img, k, p, ctx):
    a = p.get('alpha', 1.0) * prof(p.get('shape', 'tri'), k['u'], p.get('peak', 0.5))
    col = np.array(p.get('color', [255, 255, 255]), np.float32)[::-1]       # style files use RGB
    return np.clip(img.astype(np.float32) * (1 - a) + col * a, 0, 255).astype(np.uint8)


@fx('dip_black')
def dip_black(img, k, p, ctx):
    a = prof('tri', k['u'], p.get('peak', 0.5))
    return (img.astype(np.float32) * (1 - a)).astype(np.uint8)


@fx('strobe')
def strobe(img, k, p, ctx):
    n = int(k['u'] * p.get('count', 4) * 2)
    if n % 2 == 0: return img
    col = np.array(p.get('color', [255, 255, 255]), np.uint8)[::-1]
    out = np.empty_like(img); out[:] = col
    return out


@fx('invert')
def invert(img, k, p, ctx):
    a = p.get('alpha', 1.0) * prof(p.get('shape', 'hold'), k['u'])
    return np.clip(img.astype(np.float32) * (1 - a) + (255 - img.astype(np.float32)) * a, 0, 255).astype(np.uint8)


@fx('rgb_split')
def rgb_split(img, k, p, ctx):
    a = p.get('amount', 0.012) * prof(p.get('shape', 'tri'), k['u']) * ctx['w']
    if a < 0.5: return img
    ang = np.deg2rad(p.get('angle', 0)); dx, dy = np.cos(ang) * a, np.sin(ang) * a
    b, g, r = cv2.split(img)
    b = zoom_img(cv2.merge([b, b, b]), 1, dx=dx, dy=dy)[..., 0]
    r = zoom_img(cv2.merge([r, r, r]), 1, dx=-dx, dy=-dy)[..., 0]
    return cv2.merge([b, g, r])


@fx('glitch')
def glitch(img, k, p, ctx):
    """Horizontal slice displacement with channel offsets, seeded per frame so it flickers."""
    r = ctx['rng']; h, w = img.shape[:2]
    inten = p.get('amount', 0.5) * prof(p.get('shape', 'tri'), k['u'])
    out = img.copy()
    n = int(p.get('slices', 10) * (0.3 + inten))
    for _ in range(n):
        y = int(r.uniform(0, h)); hh = int(r.uniform(0.01, 0.07) * h)
        dx = int(r.uniform(-0.12, 0.12) * w * (0.4 + inten))
        out[y:y + hh] = np.roll(out[y:y + hh], dx, axis=1)
    if p.get('blocks', True):
        for _ in range(int(3 * inten) + 1):
            bw, bh = int(r.uniform(0.05, 0.3) * w), int(r.uniform(0.02, 0.1) * h)
            x0, y0 = int(r.uniform(0, w - bw)), int(r.uniform(0, h - bh))
            sx, sy = int(r.uniform(-0.2, 0.2) * w), int(r.uniform(-0.1, 0.1) * h)
            xs, ys = np.clip(x0 + sx, 0, w - bw), np.clip(y0 + sy, 0, h - bh)
            out[y0:y0 + bh, x0:x0 + bw] = img[ys:ys + bh, xs:xs + bw]
    return rgb_split(out, {'u': 0.5}, {'amount': 0.015 * inten * 2, 'shape': 'hold'}, ctx)


_CMAPS = {'inferno': cv2.COLORMAP_INFERNO, 'hot': cv2.COLORMAP_HOT, 'jet': cv2.COLORMAP_JET, 'magma': cv2.COLORMAP_MAGMA,
          'turbo': cv2.COLORMAP_TURBO, 'ocean': cv2.COLORMAP_OCEAN}


@fx('heat')
def heat(img, k, p, ctx):
    """Thermal colour-map flash: luminance mapped through a heat palette, mixed in by the envelope."""
    a = p.get('alpha', 1.0) * prof(p.get('shape', 'tri'), k['u'], p.get('peak', 0.5))
    if a < 0.01: return img
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    g = cv2.convertScaleAbs(g, alpha=p.get('contrast', 1.4), beta=p.get('beta', -20))
    col = cv2.applyColorMap(g, _CMAPS.get(p.get('colormap', 'inferno'), cv2.COLORMAP_INFERNO))
    return cv2.addWeighted(img, 1 - a, col, a, 0)


@fx('mask_flash')
def mask_flash(img, k, p, ctx):
    """Fill the subject silhouette with a flat colour (the white masking flash)."""
    m = ctx.get('mask')
    a = prof(p.get('shape', 'tri'), k['u'], p.get('peak', 0.5)) * p.get('alpha', 1.0)
    if m is None: return flash(img, k, p, ctx)
    col = np.array(p.get('color', [255, 255, 255]), np.float32)[::-1]
    mm = (m * a)[..., None]
    out = img.astype(np.float32) * (1 - mm) + col * mm
    if p.get('dim_bg', 0):
        out = out * (1 - p['dim_bg'] * a * (1 - m)[..., None])
    return np.clip(out, 0, 255).astype(np.uint8)


@fx('tile')
def tile(img, k, p, ctx):
    """Tiled copies (2x2 or 3x3) with a hue rotation per tile and an optional zoom, as in tiled colour flashes."""
    n = int(p.get('n', 2)); h, w = img.shape[:2]
    a = prof(p.get('shape', 'tri'), k['u'], p.get('peak', 0.5))
    small = cv2.resize(img, (w // n, h // n))
    out = np.zeros_like(img)
    for i in range(n):
        for j in range(n):
            hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
            hsv[..., 0] = (hsv[..., 0].astype(int) + (i * n + j) * p.get('hue_step', 30)) % 180
            t = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            out[j * (h // n):(j + 1) * (h // n), i * (w // n):(i + 1) * (w // n)] = t[:h // n, :w // n]
    out = cv2.resize(out, (w, h))
    return cv2.addWeighted(img, 1 - a, out, a, 0)


@fx('freeze')
def freeze(img, k, p, ctx):
    key = ('freeze', p.get('id', 0))
    st = ctx['store']
    if k['u'] <= 0.0001 or key not in st:
        st[key] = img.copy()
    return st[key]


# ---------------------------------------------------------------- grade

def grade_img(img, g):
    """g: saturation, contrast, brightness, gamma, bw (0..1), tint [r,g,b] gain, lift (0..1 raises blacks), vignette,
    grain, highlights (rolls off whites), fade (matte look)."""
    if not g: return img
    f = img.astype(np.float32) / 255.0
    if g.get('bw', 0) > 0:
        gr = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)[..., None] / 255.0
        f = f * (1 - g['bw']) + np.repeat(gr, 3, 2) * g['bw']
    if g.get('saturation', 1) != 1:
        gr = f.mean(2, keepdims=True)
        f = gr + (f - gr) * g['saturation']
    if g.get('tint'):
        f = f * np.array(g['tint'][::-1], np.float32)
    if g.get('target_luma'):                       # pull the shot's mean luma toward a target (low-key or pale looks from any footage)
        fc = np.clip(f, 0, 1); tl = g['target_luma']
        e = float(np.clip(np.log(tl) / np.log(float(np.clip(fc.mean(), 0.02, 0.98))), 0.25, 3.0))
        for _ in range(3):                         # solve against the real mean of the curved picture
            m2 = float(np.clip((fc ** e).mean(), 0.01, 0.99)); e = float(np.clip(e * np.log(tl) / np.log(m2), 0.25, 3.5))
        e = 1.0 + (e - 1.0) * g.get('target_strength', 1.0)
        f = fc ** e
    if g.get('gamma', 1) != 1:
        f = np.clip(f, 0, 1) ** (1.0 / g['gamma'])
    c = g.get('contrast', 1.0)
    if c != 1:
        f = (f - 0.5) * c + 0.5
    f = f + g.get('brightness', 0)
    if g.get('lift', 0) or g.get('fade', 0):
        l = g.get('lift', 0) + g.get('fade', 0)
        f = f * (1 - l) + l * 0.5 * 0 + l * g.get('lift_level', 0.0) * 1 + f * 0
    f = np.clip(f, 0, 1)
    out = (f * 255).astype(np.uint8)
    if g.get('vignette', 0):
        out = vignette(out, g['vignette'])
    return out


def vignette(img, a):
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    m = 1 - a * np.clip(d - 0.4, 0, 1) ** 1.5
    return (img.astype(np.float32) * m[..., None]).astype(np.uint8)


def grain(img, amount, rng):
    n = rng.standard_normal(img.shape[:2]).astype(np.float32) * amount * 255
    return np.clip(img.astype(np.float32) + n[..., None], 0, 255).astype(np.uint8)


@fx('grade')
def grade_fx(img, k, p, ctx):
    out = grade_img(img, p)
    if p.get('grain', 0): out = grain(out, p['grain'], ctx['rng'])
    return out


@fx('letterbox')
def letterbox(img, k, p, ctx):
    h = img.shape[0]; b = int(h * p.get('bar', 0.1)); out = img.copy()
    out[:b] = 0; out[h - b:] = 0
    return out


def apply(name, img, k, p, ctx):
    return FX[name](img, k, p, ctx)

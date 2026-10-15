"""Shared drawing helpers for the talking-head-split and kinetic-card-explainer styles. Registers nothing.

  vfont(name, size, wght)         bundled font by short name, variable weight axis set
  text_rgba(text, font, size, rgb, tracking, shadow)   tight RGBA text image, RGB order, optional soft shadow
  rrect(w, h, radius, rgb, alpha) RGBA rounded rectangle
  over(img_bgr, rgba, x, y, a)    alpha-composite an RGBA image (RGB order) onto a BGR frame at its top-left corner
  spring(t, zeta, omega)          closed-form damped spring step response, 0 at t=0 and 1 at rest (may overshoot)
  spring_in(t, t0, ...)           spring started at t0
"""
import os
from functools import lru_cache
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

_FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'fonts')
FONTS = {
    'playfair': 'PlayfairDisplay-Variable.ttf',
    'playfair italic': 'PlayfairDisplay-Italic-Variable.ttf',
    'instrument serif': 'InstrumentSerif-Regular.ttf',
    'instrument serif italic': 'InstrumentSerif-Italic.ttf',
    'inter tight': 'InterTight-Variable.ttf',
    'space grotesk': 'SpaceGrotesk-Variable.ttf',
    'archivo black': 'ArchivoBlack-Regular.ttf',
    'anton': 'Anton-Regular.ttf',
}
MONO = ['/System/Library/Fonts/Menlo.ttc', '/System/Library/Fonts/SFNSMono.ttf', '/System/Library/Fonts/Courier.ttc']


@lru_cache(maxsize=512)
def vfont(name, size, wght=None):
    size = max(6, int(size))
    key = (name or '').lower()
    path = os.path.join(_FD, FONTS[key]) if key in FONTS else None
    if key == 'mono':
        path = next((p for p in MONO if os.path.exists(p)), None)
    if path is None or not os.path.exists(path):
        path = '/System/Library/Fonts/Helvetica.ttc'
    f = ImageFont.truetype(path, size)
    if wght is not None:
        try:
            axes = f.get_variation_axes()
            vals = [a['default'] for a in axes]
            for i, a in enumerate(axes):
                nm = a.get('name', b'')
                nm = nm.decode() if isinstance(nm, bytes) else str(nm)
                if 'eight' in nm: vals[i] = max(a['minimum'], min(a['maximum'], wght))
            f.set_variation_by_axes(vals)
        except Exception:
            pass
    return f


@lru_cache(maxsize=2048)
def text_rgba(text, font, size, rgb, wght=None, tracking=0.0, shadow=None):
    """tracking in px per glyph (negative tightens). shadow (dx, dy, blur, alpha) or None. Tight RGBA, RGB order."""
    f = vfont(font, size, wght)
    pad = int(size * 0.3)
    adv = [f.getlength(c) + tracking for c in text]
    asc, desc = f.getmetrics()
    w = int(sum(adv)) + pad * 2 + 2; h = asc + desc + pad * 2
    im = Image.new('RGBA', (max(2, w), h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if tracking == 0:
        d.text((pad, pad), text, font=f, fill=tuple(rgb) + (255,))
    else:
        x = float(pad)
        for c, a in zip(text, adv):
            d.text((x, pad), c, font=f, fill=tuple(rgb) + (255,)); x += a
    arr = np.array(im)
    if shadow:
        dx, dy, blur, al = shadow
        sh = np.zeros_like(arr); sh[..., 3] = (arr[..., 3] * al).astype(np.uint8)
        sh = cv2.GaussianBlur(sh, (0, 0), max(0.1, blur))
        sh = cv2.warpAffine(sh, np.float32([[1, 0, dx], [0, 1, dy]]), (arr.shape[1], arr.shape[0]))
        a = arr[..., 3:4].astype(np.float32) / 255
        out = sh.copy()
        out[..., :3] = (arr[..., :3] * a).astype(np.uint8)            # shadow colour is black
        out[..., 3] = np.maximum(arr[..., 3], sh[..., 3])
        arr = out
    ys, xs = np.where(arr[..., 3] > 0)
    if len(xs): arr = arr[max(0, ys.min() - 1):ys.max() + 2, max(0, xs.min() - 1):xs.max() + 2]
    return arr


def baseline_text(text, font, size, rgb, wght=None, tracking=0.0, shadow=None):
    """Like text_rgba but keeps the full line box (ascent plus descent) so lines of one block share a baseline."""
    f = vfont(font, size, wght)
    asc, desc = f.getmetrics(); pad = int(size * 0.3)
    adv = [f.getlength(c) + tracking for c in text]
    w = int(sum(adv)) + pad * 2; h = asc + desc + pad * 2
    im = Image.new('RGBA', (max(2, w), h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = float(pad)
    for c, a in zip(text, adv):
        d.text((x, pad), c, font=f, fill=tuple(rgb) + (255,)); x += a
    arr = np.array(im)
    if shadow:
        dx, dy, blur, al = shadow
        sh = np.zeros_like(arr); sh[..., 3] = (arr[..., 3] * al).astype(np.uint8)
        sh = cv2.GaussianBlur(sh, (0, 0), max(0.1, blur))
        sh = cv2.warpAffine(sh, np.float32([[1, 0, dx], [0, 1, dy]]), (arr.shape[1], arr.shape[0]))
        a = arr[..., 3:4].astype(np.float32) / 255
        out = sh.copy(); out[..., :3] = (arr[..., :3] * a).astype(np.uint8); out[..., 3] = np.maximum(arr[..., 3], sh[..., 3]); arr = out
    return arr, pad


def text_width(text, font, size, wght=None, tracking=0.0):
    f = vfont(font, size, wght)
    return sum(f.getlength(c) + tracking for c in text)


def rrect(w, h, radius, rgb, alpha=255, ss=3):
    """Anti-aliased rounded rectangle (supersampled). RGBA, RGB order."""
    w, h = max(2, int(w)), max(2, int(h))
    m = np.zeros((h * ss, w * ss), np.uint8)
    r = int(min(radius, w / 2, h / 2) * ss)
    cv2.rectangle(m, (r, 0), (w * ss - r - 1, h * ss - 1), 255, -1)
    cv2.rectangle(m, (0, r), (w * ss - 1, h * ss - r - 1), 255, -1)
    for cx, cy in ((r, r), (w * ss - r - 1, r), (r, h * ss - r - 1), (w * ss - r - 1, h * ss - r - 1)):
        cv2.circle(m, (cx, cy), r, 255, -1)
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA)
    out = np.zeros((h, w, 4), np.uint8); out[..., :3] = rgb; out[..., 3] = (m.astype(np.float32) * alpha / 255).astype(np.uint8)
    return out


def shadowed(rgba, blur, dy, alpha):
    """rgba plus a soft drop shadow underneath, padded so the shadow is not clipped."""
    pad = int(blur * 3) + abs(int(dy)) + 2
    h, w = rgba.shape[:2]
    out = np.zeros((h + pad * 2, w + pad * 2, 4), np.uint8)
    sh = np.zeros_like(out); sh[pad:pad + h, pad:pad + w, 3] = (rgba[..., 3] * alpha).astype(np.uint8)
    sh = cv2.GaussianBlur(sh, (0, 0), blur)
    sh = cv2.warpAffine(sh, np.float32([[1, 0, 0], [0, 1, dy]]), (out.shape[1], out.shape[0]))
    out[..., 3] = sh[..., 3]
    layer = np.zeros_like(out); layer[pad:pad + h, pad:pad + w] = rgba
    return _comp(out, layer), pad


def _comp(dst, src):
    sa = src[..., 3:4].astype(np.float32) / 255; da = dst[..., 3:4].astype(np.float32) / 255
    oa = sa + da * (1 - sa)
    oc = (src[..., :3] * sa + dst[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6)
    out = dst.copy(); out[..., :3] = oc.astype(np.uint8); out[..., 3] = (oa[..., 0] * 255).astype(np.uint8)
    return out


def over(img, rgba, x, y, a=1.0, scale=1.0, centre=False):
    """Composite rgba (RGB order) onto BGR img with its top-left at (x, y), or centred there. Returns img (modified)."""
    if rgba is None or a <= 0.002 or scale <= 0.01: return img
    if abs(scale - 1) > 1e-3:
        rgba = cv2.resize(rgba, (max(1, int(rgba.shape[1] * scale)), max(1, int(rgba.shape[0] * scale))), interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR)
    h, w = rgba.shape[:2]
    if centre: x -= w / 2; y -= h / 2
    x0, y0 = int(round(x)), int(round(y))
    H, W = img.shape[:2]
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if xb <= xa or yb <= ya: return img
    s = rgba[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32)
    sa = s[..., 3:4] / 255.0 * a
    d = img[ya:yb, xa:xb].astype(np.float32)
    img[ya:yb, xa:xb] = (s[..., :3][..., ::-1] * sa + d * (1 - sa)).astype(np.uint8)
    return img


def fill(img, rgb):
    img[:] = np.array(rgb, np.uint8)[::-1]
    return img


# ------------------------------------------------------------------ closed-form springs

def spring(t, zeta=0.6, omega=18.0):
    """Step response of a unit mass spring from 0 to 1, evaluated in closed form at time t seconds (no integration, so any
    frame can be rendered on its own). zeta is the damping ratio (below 1 overshoots), omega the natural frequency in rad/s."""
    if t <= 0: return 0.0
    if zeta < 1 - 1e-6:
        wd = omega * np.sqrt(1 - zeta * zeta)
        return float(1 - np.exp(-zeta * omega * t) * (np.cos(wd * t) + zeta * omega / wd * np.sin(wd * t)))
    if zeta > 1 + 1e-6:
        s = omega * np.sqrt(zeta * zeta - 1); r1 = -zeta * omega + s; r2 = -zeta * omega - s
        return float(1 - (r2 * np.exp(r1 * t) - r1 * np.exp(r2 * t)) / (r2 - r1))
    return float(1 - np.exp(-omega * t) * (1 + omega * t))


def spring_in(t, t0, zeta=0.6, omega=18.0):
    return spring(t - t0, zeta, omega)

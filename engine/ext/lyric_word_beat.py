"""Extensions for the lyric-word-beat style: difference-blend one-word captions, six transitions that use the outgoing
picture, and a brand-sticker overlay with a wordmark that sits behind the subject.

Registers with fx.fx, captions.caption and render.overlay. Self-contained, nothing here edits the core.

Transitions are meant to run on the 'pre' layer (style moves with "layer": "pre") so the caption layer, which is drawn
after the pre layer, stays on top of every dip, flash and wipe exactly as in the reference edit. Each one takes
cut_u, the position of the cut inside the effect span (0 to 1), and works from u only.
"""
import numpy as np
import cv2
from fx import fx, ease, zoom_img
from captions import caption, text_rgba
from render import overlay


# ------------------------------------------------------------------ helpers

def _prev(ctx, img):
    """Last graded frame of the outgoing shot, resized to img. Falls back to a darkened copy of img."""
    p = ctx['store'].get('prev_shot_last')
    if p is None or p.shape != img.shape:
        return (img.astype(np.float32) * 0.3).astype(np.uint8)
    return p


def _mono_cool(img, rng, grain=0.03):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    g = np.clip((g - 0.5) * 1.12 + 0.5, 0, 1)
    out = np.stack([g * 1.06, g * 1.0, g * 0.9], 2)            # BGR, slightly cool
    out += rng.standard_normal(g.shape).astype(np.float32)[..., None] * grain
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)


def _zoom_blur(img, amt, n=9):
    if amt < 0.004: return img
    acc = np.zeros(img.shape, np.float32)
    for i in range(n):
        acc += zoom_img(img, 1 + amt * i / (n - 1)).astype(np.float32)
    return (acc / n).astype(np.uint8)


def _mix(a, b, w):
    return np.clip(a.astype(np.float32) * (1 - w) + b.astype(np.float32) * w, 0, 255).astype(np.uint8)


def _flat(img, bgr):
    out = np.empty_like(img); out[:] = np.array(bgr, np.uint8); return out


# ------------------------------------------------------------------ transitions

@fx('lyr_dip_mosaic')
def dip_mosaic(img, k, p, ctx):
    """Hard dip to black, a 3x3 mosaic of mono, cool, grainy copies of the incoming shot filling in cell by cell, then a
    two-frame strobe that snaps the colour back in."""
    u = k['u']; black = p.get('black', 0.25); mend = p.get('mosaic_end', 0.8); n = int(p.get('cells', 3))
    if u < black: return np.zeros_like(img)
    h, w = img.shape[:2]
    if u < mend:
        prog = (u - black) / max(1e-6, mend - black)
        order = np.random.default_rng(1000 + ctx.get('shot_index', 0)).permutation(n * n)
        show = int(np.ceil(prog * n * n * 0.999))
        cell = cv2.resize(_mono_cool(img, ctx['rng']), (w // n, h // n), interpolation=cv2.INTER_AREA)
        out = np.zeros_like(img)
        for idx in order[:show]:
            r, c = divmod(int(idx), n)
            out[r * (h // n):(r + 1) * (h // n), c * (w // n):(c + 1) * (w // n)] = cell
        return out
    return _pop(img, ctx['frame'] % 2 == 0, p)


def _pop(img, on, p):
    if not on: return img
    f = hsv_boost(img, p.get('sat', 1.35))
    return np.clip(f.astype(np.float32) * p.get('gain', 1.75), 0, 255).astype(np.uint8)


def hsv_boost(img, s):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * s, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


@fx('lyr_strobe_pop')
def strobe_pop(img, k, p, ctx):
    """Alternate-frame colour pop: the picture jumps brighter and more saturated every other frame."""
    return _pop(img, ctx['frame'] % 2 == 0, p)


@fx('lyr_haze_flash')
def haze_flash(img, k, p, ctx):
    """A pale haze veil that builds to the cut, one hard white frame, then the fog thins away."""
    u = k['u']; cu = p.get('cut_u', 0.1); fl = p.get('flash_u', [0.35, 0.45])
    if fl[0] <= u < fl[1]: return _flat(img, (250, 250, 250))
    veil = p.get('veil', 0.65)
    a = veil * (u / max(1e-6, cu)) if u < cu else veil * max(0.0, 1 - (u - max(cu, fl[1])) / max(1e-6, 1 - max(cu, fl[1]))) ** 1.3
    if u > cu and u < fl[0]: a = veil
    if a < 0.01: return img
    fog = cv2.GaussianBlur(img, (0, 0), max(2, img.shape[1] * 0.012))
    return _mix(fog, _flat(img, (225, 225, 230)), a)


@fx('lyr_band_wipe')
def band_wipe(img, k, p, ctx):
    """The incoming shot enters as a top band and a bottom band and closes over the outgoing picture, ending with a warm bloom."""
    u = k['u']; h, w = img.shape[:2]
    e = ease('in_out', min(1.0, u / p.get('close_u', 0.85)))
    top = int(h * (p.get('top0', 0.2) + (0.5 - p.get('top0', 0.2)) * e))
    bot = int(h * (p.get('bot0', 0.38) + (0.5 - p.get('bot0', 0.38)) * e))
    out = img.copy()
    if top + bot < h:
        old = motion_h(_prev(ctx, img), 1 + int(w * 0.03 * (1 - e)))
        out[top:h - bot] = old[top:h - bot]
    if u > p.get('bloom_u', 0.8):
        a = p.get('bloom', 0.55) * (1 - (u - p.get('bloom_u', 0.8)) / max(1e-6, 1 - p.get('bloom_u', 0.8)))
        glow = cv2.GaussianBlur(hsv_boost(img, 1.4), (0, 0), max(3, w * 0.03))
        warm = np.clip(glow.astype(np.float32) * np.array([0.6, 0.95, 1.5]) + 25, 0, 255)
        out = np.clip(out.astype(np.float32) + warm * a, 0, 255).astype(np.uint8)
    return out


def motion_h(img, n):
    n = int(max(1, n))
    if n <= 1: return img
    kern = np.full((1, n), 1.0 / n, np.float32)
    return cv2.filter2D(img, -1, kern, borderType=cv2.BORDER_REFLECT)


@fx('lyr_radial_flash')
def radial_flash(img, k, p, ctx):
    """Radial zoom blur building into the cut, a cream white frame on the cut, a short blurred release on the new shot."""
    u = k['u']; cu = p.get('cut_u', 0.7); amt = p.get('amount', 0.22)
    cream = (232, 245, 250)
    if u < cu:
        s = (u / max(1e-6, cu)) ** 1.5
        out = _zoom_blur(img, amt * s)
        wa = max(0.0, (u - (cu - p.get('white_u', 0.18))) / max(1e-6, p.get('white_u', 0.18)))
        return _mix(out, _flat(img, cream), wa * 0.95)
    s = max(0.0, 1 - (u - cu) / max(1e-6, 1 - cu))
    out = _zoom_blur(img, amt * 0.5 * s)
    return _mix(out, _flat(img, cream), 0.9 * s ** 2)


def _rounded(h, w, r):
    m = np.zeros((h, w), np.uint8)
    r = int(r)
    cv2.rectangle(m, (r, 0), (w - r, h), 255, -1); cv2.rectangle(m, (0, r), (w, h - r), 255, -1)
    for cx, cy in ((r, r), (w - r, r), (r, h - r), (w - r, h - r)): cv2.circle(m, (cx, cy), r, 255, -1)
    return m


@fx('lyr_card_up')
def card_up(img, k, p, ctx):
    """Dip to black, the incoming shot slides up from the bottom edge as a rounded card with a slight perspective tilt, holds at
    about 60 percent, then scales to fill the frame."""
    u = k['u']; h, w = img.shape[:2]
    a, b, c, d = p.get('black', 0.1), p.get('up_end', 0.26), p.get('hold_end', 0.62), p.get('full', 0.78)
    sc0 = p.get('card_scale', 0.62)
    if u < a: return np.zeros_like(img)
    if u >= d: return img
    if u < b:
        e = ease('out_cubic', (u - a) / (b - a)); scale = sc0; cy = 0.5 + (1 - e) * 0.62; tilt = p.get('tilt', 0.05)
    elif u < c:
        scale, cy, tilt = sc0, 0.5, p.get('tilt', 0.05) * 0.0
    else:
        e = ease('in_out', (u - c) / (d - c)); scale = sc0 + (1 - sc0) * e; cy = 0.5; tilt = 0.0
    cw, ch = w * scale, h * scale
    ti = tilt * cw
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    y0, y1 = h * cy - ch / 2, h * cy + ch / 2
    dst = np.float32([[w / 2 - cw / 2 + ti, y0], [w / 2 + cw / 2 - ti, y0], [w / 2 + cw / 2, y1], [w / 2 - cw / 2, y1]])
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0))
    r = p.get('radius', 0.03) * h * (1 - max(0.0, (u - c) / max(1e-6, d - c)))
    m = cv2.warpPerspective(_rounded(h, w, max(1, r)), M, (w, h), flags=cv2.INTER_LINEAR)
    a3 = (m.astype(np.float32) / 255.0)[..., None]
    return (warped.astype(np.float32) * a3).astype(np.uint8)


# ------------------------------------------------------------------ captions

_SHADOW = {}


def _text_layers(text, fname, size, tracking, shadow):
    key = (text, fname, size, tracking, tuple(shadow))
    if key in _SHADOW: return _SHADOW[key]
    t = text_rgba(text, fname, size, (255, 255, 255), 0, (0, 0, 0), tracking, ())
    ta = t[..., 3].astype(np.float32) / 255.0
    dx, dy, blur, al = shadow
    pad = int(blur * 3 + abs(dx) + abs(dy)) + 2
    ta_p = np.pad(ta, pad)
    sa = cv2.GaussianBlur(ta_p, (0, 0), max(0.1, blur)) * al
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    sa = cv2.warpAffine(sa, M, (sa.shape[1], sa.shape[0]))
    _SHADOW[key] = (ta_p, np.clip(sa, 0, 1))
    return _SHADOW[key]


def sticker_windows(ctx):
    ev = ctx.get('edl', {}).get('events', [])
    return [e for e in ev if e['fx'] == 'mask_flash' and e.get('params', {}).get('tag') == 'sticker']


@caption('lyric_diff')
def lyric_diff(t, words, cfg, W, H, ctx):
    """One lyric word at a time, uppercase heavy sans, dead centre, hard swap with no animation, held until the next word.
    The fill is white under a difference blend (255 minus the picture), so it reads white on dark footage and takes a
    complementary colour on bright footage. guard keeps weak mid-tone results readable. While a sticker window is live the
    word drops to y_alt (the lower third)."""
    cur = None
    for w in words:
        if w['t0'] <= t: cur = w
        else: break
    if cur is None or t > cur['t1'] + cfg.get('linger', 0.8): return None
    if ctx.get('depth_pass') and ctx['depth_pass'] != cur.get('depth', 'front'): return None
    img = ctx.get('img')
    portrait = H > W
    size = int((cfg.get('size_frac_portrait', 0.13) * W) if portrait else (cfg.get('size_frac', 0.096) * H))
    y = cfg.get('y', 0.5)
    if any(e['t0'] <= t < e['t1'] for e in sticker_windows(ctx)): y = cfg.get('y_alt', 0.75)
    text = cur['text'].upper() if cfg.get('upper', True) else cur['text']
    ta, sa = _text_layers(text, cfg.get('font', 'Arial Black'), size, int(cfg.get('tracking', 0.01) * size),
                          (cfg.get('shadow', [2, 2, 3.0, 0.45])[0] * H / 724, cfg.get('shadow', [2, 2, 3.0, 0.45])[1] * H / 724,
                           cfg.get('shadow', [2, 2, 3.0, 0.45])[2] * H / 724, cfg.get('shadow', [2, 2, 3.0, 0.45])[3]))
    mw = cfg.get('fit_width', 0.86) * W
    if ta.shape[1] > mw:
        f = mw / ta.shape[1]
        ta = cv2.resize(ta, None, fx=f, fy=f, interpolation=cv2.INTER_AREA); sa = cv2.resize(sa, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
    th, tw = ta.shape
    x0 = int(cfg.get('x', 0.5) * W - tw / 2); y0 = int(y * H - th / 2)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + tw), min(H, y0 + th)
    if xb <= xa or yb <= ya: return None
    tA = ta[ya - y0:yb - y0, xa - x0:xb - x0]; sA = sa[ya - y0:yb - y0, xa - x0:xb - x0]
    oa = tA + sA * (1 - tA)
    canvas = np.zeros((H, W, 4), np.uint8)
    if img is not None:
        bg = img[ya:yb, xa:xb, ::-1].astype(np.float32)                    # RGB
        diff = 255.0 - bg
        g = cfg.get('guard', 0.6)
        if g > 0:
            lum_b = bg @ np.array([0.299, 0.587, 0.114], np.float32)
            lum_d = diff @ np.array([0.299, 0.587, 0.114], np.float32)
            weak = np.clip(1 - np.abs(lum_d - lum_b) / 120.0, 0, 1)[..., None] * g
            tgt = np.where((lum_b < 128)[..., None], 255.0, 10.0)
            diff = diff * (1 - weak) + tgt * weak
    else:
        diff = np.full((yb - ya, xb - xa, 3), 255.0, np.float32)
    col = diff * (tA / np.maximum(oa, 1e-6))[..., None]
    canvas[ya:yb, xa:xb, :3] = np.clip(col, 0, 255).astype(np.uint8)
    canvas[ya:yb, xa:xb, 3] = (np.clip(oa, 0, 1) * 255).astype(np.uint8)
    return canvas


# ------------------------------------------------------------------ overlay: sticker, wordmark behind the subject, silhouette strobe

def _tick_polygon(w, h):
    """A generic curved tick (not any real brand mark): thick at the dip, tapering to a point at both ends."""
    n = 40; s = np.linspace(0, 1, n)
    u = np.clip((s - 0.3) / 0.7, 0, 1)
    x = s
    y = np.where(s < 0.3, 0.55 + 0.25 * np.clip(s / 0.3, 0, 1), 0.8 - 0.8 * u ** 1.15)
    thick = 0.36 * np.sin(np.pi * np.clip(s * 1.05, 0, 1)) ** 0.7 * (1 - 0.45 * s)
    up = np.stack([x * w, (y - thick * 0.35) * h], 1); dn = np.stack([x * w, (y + thick * 0.65) * h], 1)
    return np.vstack([up, dn[::-1]]).astype(np.int32)


@overlay('lyric_sticker')
def lyric_sticker(img, t, ctx, oc):
    wins = [e for e in sticker_windows(ctx) if e['t0'] <= t < e['t1']]
    if not wins: return img
    e = wins[0]; h, w = img.shape[:2]
    P = ctx['edl']['music']['beat_period']; fps = ctx['fps']
    out = img
    m = ctx.get('mask')
    # wordmark: behind the subject, from a beat into the window
    if t - e['t0'] >= oc.get('wordmark_after_beats', 2.0) * P:
        text = oc.get('text', 'KEEP GOING')
        size = int(h * oc.get('wordmark_h', 0.20))
        ta, sa = _text_layers(text, oc.get('font', 'Impact'), size, 0, (2, 3, 4.0, 0.5))
        mw = oc.get('wordmark_w', 0.6) * w
        if ta.shape[1] > mw:
            f = mw / ta.shape[1]; ta = cv2.resize(ta, None, fx=f, fy=f, interpolation=cv2.INTER_AREA); sa = cv2.resize(sa, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
        th, tw = ta.shape; x0 = int(w / 2 - tw / 2); y0 = int(oc.get('wordmark_y', 0.42) * h - th / 2)
        xa, ya, xb, yb = max(0, x0), max(0, y0), min(w, x0 + tw), min(h, y0 + th)
        if xb > xa and yb > ya:
            tA = ta[ya - y0:yb - y0, xa - x0:xb - x0]; sA = sa[ya - y0:yb - y0, xa - x0:xb - x0]
            if m is not None: k_ = (1 - m[ya:yb, xa:xb]); tA = tA * k_; sA = sA * k_
            out = out.copy()
            reg = out[ya:yb, xa:xb].astype(np.float32)
            reg = reg * (1 - sA[..., None] * (1 - tA[..., None])) * 1.0
            reg = reg * (1 - tA[..., None]) + 255.0 * tA[..., None]
            out[ya:yb, xa:xb] = np.clip(reg, 0, 255).astype(np.uint8)
    # silhouette strobe, six frames, on/off
    ts = e['t0'] + oc.get('strobe_after_beats', 1.0) * P
    fi = int(round((t - ts) * fps))
    if m is not None and 0 <= fi < 6 and fi % 2 == 0:
        out = _mix(out, _flat(out, (255, 255, 255)), (m * 1.0)[..., None])
    # sticker in front: slides in with a tiny overshoot
    u = (t - e['t0']) / max(1e-6, oc.get('sticker_in_beats', 0.35) * P)
    sc = 0.6 + 0.4 * ease('out_back', min(1.0, u))
    sw = int(oc.get('sticker_w', 0.2) * w); sh_ = int(sw * 0.45)
    poly = _tick_polygon(sw, sh_)
    layer = np.zeros((sh_ + 4, sw + 4), np.uint8)
    cv2.fillPoly(layer, [poly + 2], 255)
    layer = cv2.GaussianBlur(layer, (0, 0), 0.7)
    if sc != 1.0: layer = cv2.resize(layer, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    lh, lw = layer.shape
    cx, cy = int(oc.get('sticker_x', 0.28) * w), int(oc.get('sticker_y', 0.38) * h)
    x0, y0 = cx - lw // 2, cy - lh // 2
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(w, x0 + lw), min(h, y0 + lh)
    if xb > xa and yb > ya:
        a = (layer[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32) / 255.0)[..., None]
        col = np.array(oc.get('color', [232, 30, 40])[::-1], np.float32)
        out = out.copy()
        out[ya:yb, xa:xb] = np.clip(out[ya:yb, xa:xb].astype(np.float32) * (1 - a) + col * a, 0, 255).astype(np.uint8)
    return out

"""Caption rendering for the edit engine (Pillow, because the local ffmpeg has no drawtext or libass).

A caption kind is fn(t, words, cfg, W, H, ctx) -> RGBA uint8 array HxWx4 (premultiplication not needed) or None.
words: list of dicts {text, t0, t1, emph, line, phrase}. Register with @caption('name').
Extension modules in engine/ext/ add kinds the same way.
"""
import os
from functools import lru_cache
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

CAPTIONS = {}


def caption(name):
    def deco(f):
        CAPTIONS[name] = f
        return f
    return deco


_FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'fonts')
FONT_FILES = {
    'anton': (os.path.join(_FD, 'Anton-Regular.ttf'), 0),
    'bebas neue': (os.path.join(_FD, 'BebasNeue-Regular.ttf'), 0),
    'archivo black': (os.path.join(_FD, 'ArchivoBlack-Regular.ttf'), 0),
    'space grotesk': (os.path.join(_FD, 'SpaceGrotesk-Variable.ttf'), 0),
    'inter tight': (os.path.join(_FD, 'InterTight-Variable.ttf'), 0),
    'arial black': ('/System/Library/Fonts/Supplemental/Arial Black.ttf', 0),
    'impact': ('/System/Library/Fonts/Supplemental/Impact.ttf', 0),
    'din condensed': ('/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf', 0),
    'din alternate': ('/System/Library/Fonts/Supplemental/DIN Alternate Bold.ttf', 0),
    'futura': ('/System/Library/Fonts/Supplemental/Futura.ttc', 2),
    'helvetica bold': ('/System/Library/Fonts/Helvetica.ttc', 1),
    'helvetica neue bold': ('/System/Library/Fonts/HelveticaNeue.ttc', 1),
    'avenir next heavy': ('/System/Library/Fonts/Avenir Next.ttc', 8),
    'avenir next bold': ('/System/Library/Fonts/Avenir Next.ttc', 0),
    'georgia': ('/System/Library/Fonts/Supplemental/Georgia.ttf', 0),
    'times': ('/System/Library/Fonts/Supplemental/Times New Roman.ttf', 0),
    'courier': ('/System/Library/Fonts/Courier.ttc', 0),
    'menlo': ('/System/Library/Fonts/Menlo.ttc', 1),
    'sf mono': ('/System/Library/Fonts/SFNSMono.ttf', 0),
    'sf': ('/System/Library/Fonts/SFNS.ttf', 0),
}


@lru_cache(maxsize=256)
def font(name, size):
    """Load a font by friendly name or path. Falls back through Arial Black, Helvetica, then Pillow's default."""
    size = max(8, int(size))
    cands = []
    key = (name or '').lower()
    if os.path.exists(name or ''): cands.append((name, 0))
    if key in FONT_FILES: cands.append(FONT_FILES[key])
    cands += [FONT_FILES['arial black'], FONT_FILES['helvetica bold']]
    for p, idx in cands:
        try:
            return ImageFont.truetype(p, size, index=idx)
        except Exception:
            continue
    return ImageFont.load_default()


@lru_cache(maxsize=2048)
def text_rgba(text, fname, size, fill, stroke, stroke_fill, tracking, shadow):
    """Render text to a tight RGBA image. fill and stroke_fill are RGB tuples, tracking in px, shadow (dx, dy, blur, alpha)."""
    f = font(fname, size)
    pad = int(size * 0.35) + stroke
    # measure with tracking
    adv = []
    for ch in text:
        adv.append(f.getlength(ch) + tracking)
    wtot = int(sum(adv)) + pad * 2
    asc, desc = f.getmetrics()
    H = asc + desc + pad * 2
    img = Image.new('RGBA', (max(1, wtot), H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = pad
    if tracking == 0:
        d.text((pad, pad), text, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=stroke_fill + (255,))
    else:
        for ch, a in zip(text, adv):
            d.text((x, pad), ch, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=stroke_fill + (255,))
            x += a
    arr = np.array(img)
    if shadow:
        dx, dy, blur, al = shadow
        sh = np.zeros_like(arr); sh[..., 3] = (arr[..., 3] * al).astype(np.uint8)
        sh = cv2.GaussianBlur(sh, (0, 0), max(0.1, blur))
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        sh = cv2.warpAffine(sh, M, (arr.shape[1], arr.shape[0]))
        out = sh.copy()
        a = arr[..., 3:4].astype(np.float32) / 255
        out[..., :3] = (arr[..., :3] * a + sh[..., :3] * (1 - a)).astype(np.uint8)
        out[..., 3] = np.maximum(arr[..., 3], sh[..., 3])
        arr = out
    # crop to content
    ys, xs = np.where(arr[..., 3] > 0)
    if len(xs):
        arr = arr[max(0, ys.min() - 2):ys.max() + 3, max(0, xs.min() - 2):xs.max() + 3]
    return arr


def blit(canvas, rgba, cx, cy, scale=1.0, alpha=1.0, anchor='c', rot=0.0):
    """Alpha-composite rgba onto an RGBA canvas (float-free uint8). anchor: c (centre), l (left middle), lt (top left)."""
    if rgba is None or alpha <= 0.002 or scale <= 0.01: return
    h, w = rgba.shape[:2]
    if abs(scale - 1) > 1e-3:
        rgba = cv2.resize(rgba, (max(1, int(w * scale)), max(1, int(h * scale))), interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR)
        h, w = rgba.shape[:2]
    if rot:
        M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, 1.0)
        rgba = cv2.warpAffine(rgba, M, (w, h))
    if anchor == 'c': x0, y0 = int(cx - w / 2), int(cy - h / 2)
    elif anchor == 'l': x0, y0 = int(cx), int(cy - h / 2)
    elif anchor == 'r': x0, y0 = int(cx - w), int(cy - h / 2)
    else: x0, y0 = int(cx), int(cy)
    H, W = canvas.shape[:2]
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if xb <= xa or yb <= ya: return
    src = rgba[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32)
    dst = canvas[ya:yb, xa:xb].astype(np.float32)
    sa = src[..., 3:4] / 255.0 * alpha
    da = dst[..., 3:4] / 255.0
    oa = sa + da * (1 - sa)
    oc = (src[..., :3] * sa + dst[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6)
    canvas[ya:yb, xa:xb, :3] = oc.astype(np.uint8)
    canvas[ya:yb, xa:xb, 3:4] = (oa * 255).astype(np.uint8)


def _rgb(c, default=(255, 255, 255)):
    return tuple(int(x) for x in (c or default))


def _ease(name, u):
    from fx import ease
    return ease(name, u)


# ------------------------------------------------------------------ kinds

@caption('staircase')
def staircase(t, words, cfg, W, H, ctx):
    """Words stack one per line with a growing indent (a staircase), a phrase at a time, over a cut-heavy picture.
    Emphasis words take the accent colour and a larger size. The block clears at the phrase end."""
    size = cfg.get('size_frac', 0.05) * min(W, H) * (1.0 if W > H else 1.15)
    x0 = cfg.get('x', 0.2) * W; y0 = cfg.get('y', 0.35) * H
    step_x = cfg.get('indent', 0.045) * W; lh = cfg.get('line_height', 1.15) * size
    per_line = cfg.get('words_per_line', 1)
    fade_in = cfg.get('fade_in', 0.06); fade_out = cfg.get('fade_out', 0.12); hold = cfg.get('hold_after', 0.45)
    # which phrase is live
    live = [w for w in words if w['t0'] <= t]
    if not live: return None
    ph = live[-1]['phrase']
    pw = [w for w in words if w['phrase'] == ph]
    t_end = max(w['t1'] for w in pw) + hold
    if t > t_end + fade_out: return None
    canvas = np.zeros((H, W, 4), np.uint8)
    glob = 1.0 if t <= t_end else 1 - (t - t_end) / fade_out
    direction = cfg.get('direction', 'down')
    if direction == 'alternate': direction = 'down' if ph % 2 == 0 else 'up'
    # build every word image first so a large emphasis word can push the next line down instead of overlapping it,
    # and wrap words onto a new line when the line would run out of frame
    built = []
    line_h = {}
    line = 0; col = 0; cur_x = 0.0
    for w in pw:
        if w['t0'] > t: break
        emph = w.get('emph')
        sz = size * (cfg.get('emph_scale', 1.45) if emph else 1.0)
        colr = _rgb(cfg.get('emph_color', [150, 20, 20]) if emph else cfg.get('color', [255, 255, 255]))
        fname = cfg.get('emph_font', cfg.get('font', 'Arial Black')) if emph else cfg.get('font', 'Arial Black')
        img = text_rgba(w['text'].upper() if cfg.get('upper', True) else w['text'], fname, int(sz), colr,
                        cfg.get('stroke', 0), (0, 0, 0), cfg.get('tracking', 0), tuple(cfg.get('shadow', [0, 2, 2, 0.5])))
        avail = W * 0.95 - (x0 + line * step_x)
        if col > 0 and (col >= per_line or cur_x + img.shape[1] > avail):
            line += 1; col = 0; cur_x = 0.0
        built.append((line, cur_x, w, img, emph, sz))
        cur_x += img.shape[1] + size * 0.25; col += 1
        line_h[line] = max(line_h.get(line, lh), img.shape[0] * 1.02 if emph else lh)
    for (ln, cx, w, img, emph, sz) in built:
        if ctx.get('depth_pass') and ctx['depth_pass'] != w.get('depth', 'front'): continue
        a = min(1.0, (t - w['t0']) / fade_in) if fade_in > 0 else 1.0
        before = sum(line_h.get(k, lh) for k in range(ln)) + line_h[ln] / 2
        y = (y0 + before - lh / 2) if direction == 'down' else (cfg.get('y_up', 0.72) * H - before + lh / 2)
        x = x0 + ln * step_x + cx
        x = min(x, W * 0.95 - img.shape[1])
        x = max(x, W * 0.04)
        if emph and cfg.get('emph_split'):
            for dx, c in ((-2, (0, 255, 255)), (2, (255, 40, 60))):
                im2 = text_rgba(w['text'], cfg.get('emph_font', cfg.get('font', 'Arial Black')), int(sz), c, 0, (0, 0, 0), cfg.get('tracking', 0), ())
                blit(canvas, im2, x + dx, y, 1, a * glob * 0.8, anchor='l')
        blit(canvas, img, x, y, 1, a * glob, anchor='l')
    return canvas


@caption('word_pop')
def word_pop(t, words, cfg, W, H, ctx):
    """One word at a time, centred, held until the next word. anim: none, pop, slide_up."""
    cur = None
    for w in words:
        if w['t0'] <= t: cur = w
        else: break
    if cur is None: return None
    if t > cur['t1'] + cfg.get('linger', 0.0) and cfg.get('clear_gaps', False): return None
    if ctx.get('depth_pass') and ctx['depth_pass'] != cur.get('depth', 'front'): return None
    canvas = np.zeros((H, W, 4), np.uint8)
    size = cfg.get('size_frac', 0.12) * min(W, H)
    emph = cur.get('emph')
    colr = _rgb(cfg.get('emph_color') if emph and cfg.get('emph_color') else cfg.get('color', [255, 255, 255]))
    img = text_rgba(cur['text'].upper() if cfg.get('upper', True) else cur['text'], cfg.get('font', 'Arial Black'), int(size), colr,
                    cfg.get('stroke', 0), _rgb(cfg.get('stroke_color'), (0, 0, 0)), cfg.get('tracking', 0), tuple(cfg.get('shadow', [0, 4, 6, 0.5])))
    u = (t - cur['t0']) / max(1e-3, cfg.get('anim_dur', 0.12))
    anim = cfg.get('anim', 'none'); sc = 1.0; dy = 0.0; a = 1.0
    if anim == 'pop': sc = 0.7 + 0.3 * _ease('out_back', u)
    elif anim == 'slide_up': dy = (1 - _ease('out_cubic', u)) * 0.04 * H; a = min(1, u * 1.5)
    elif anim == 'fade': a = min(1, u)
    if cfg.get('fit_width', 0.9):
        mw = cfg.get('fit_width', 0.9) * W
        if img.shape[1] > mw: sc *= mw / img.shape[1]
    blit(canvas, img, cfg.get('x', 0.5) * W, cfg.get('y', 0.5) * H + dy, sc, a)
    return canvas


@caption('subtitle')
def subtitle(t, words, cfg, W, H, ctx):
    """Conventional lower-third phrase captions with the current word highlighted."""
    live = [w for w in words if w['t0'] <= t]
    if not live: return None
    ph = live[-1]['phrase']
    pw = [w for w in words if w['phrase'] == ph]
    if t > max(w['t1'] for w in pw) + 0.5: return None
    canvas = np.zeros((H, W, 4), np.uint8)
    size = int(cfg.get('size_frac', 0.05) * min(W, H))
    gap = size * 0.3
    imgs = []
    for w in pw:
        on = w['t0'] <= t
        col = _rgb(cfg.get('hi_color', [255, 220, 0]) if (on and (w['t1'] > t or w is live[-1])) else (cfg.get('color', [255, 255, 255]) if on else (120, 120, 120)))
        imgs.append(text_rgba(w['text'], cfg.get('font', 'Arial Black'), size, col, cfg.get('stroke', 4), (0, 0, 0), 0, ()))
    # wrap
    maxw = cfg.get('max_width', 0.86) * W
    lines, cur, cw = [], [], 0
    for im in imgs:
        if cur and cw + im.shape[1] + gap > maxw: lines.append(cur); cur, cw = [], 0
        cur.append(im); cw += im.shape[1] + gap
    if cur: lines.append(cur)
    y = cfg.get('y', 0.78) * H - (len(lines) - 1) * size * 0.6
    for ln in lines:
        tw = sum(i.shape[1] for i in ln) + gap * (len(ln) - 1); x = W / 2 - tw / 2
        for im in ln:
            blit(canvas, im, x, y, 1, 1, anchor='l'); x += im.shape[1] + gap
        y += size * 1.2
    return canvas


@caption('karaoke')
def karaoke(t, words, cfg, W, H, ctx):
    """Phrase captions where the active word fills left to right as it is spoken, a continuous
    progress wipe rather than subtitle's binary before/current/after highlight. Reuses subtitle's
    own wrap and layout; the only new part is the per-word fill."""
    live = [w for w in words if w['t0'] <= t]
    if not live: return None
    ph = live[-1]['phrase']
    pw = [w for w in words if w['phrase'] == ph]
    if t > max(w['t1'] for w in pw) + 0.5: return None
    canvas = np.zeros((H, W, 4), np.uint8)
    size = int(cfg.get('size_frac', 0.05) * min(W, H))
    gap = size * 0.3
    off_col = _rgb(cfg.get('color', [255, 255, 255]))
    on_col = _rgb(cfg.get('fill_color', [255, 220, 0]))
    stroke = cfg.get('stroke', 4)
    fname = cfg.get('font', 'Arial Black')
    rows = []
    for w in pw:
        img_off = text_rgba(w['text'], fname, size, off_col, stroke, (0, 0, 0), 0, ())
        img_on = text_rgba(w['text'], fname, size, on_col, stroke, (0, 0, 0), 0, ())
        if t < w['t0']: p = 0.0
        elif t >= w['t1']: p = 1.0
        else: p = (t - w['t0']) / max(1e-3, w['t1'] - w['t0'])
        rows.append((img_off, img_on, p))
    maxw = cfg.get('max_width', 0.86) * W
    lines, cur, cw = [], [], 0
    for item in rows:
        w_px = item[0].shape[1]
        if cur and cw + w_px + gap > maxw: lines.append(cur); cur, cw = [], 0
        cur.append(item); cw += w_px + gap
    if cur: lines.append(cur)
    y = cfg.get('y', 0.78) * H - (len(lines) - 1) * size * 0.6
    for ln in lines:
        tw = sum(i[0].shape[1] for i in ln) + gap * (len(ln) - 1); x = W / 2 - tw / 2
        for (img_off, img_on, p) in ln:
            blit(canvas, img_off, x, y, 1, 1, anchor='l')
            if p > 0:
                cut = max(1, int(img_on.shape[1] * p))
                blit(canvas, img_on[:, :cut], x, y, 1, 1, anchor='l')
            x += img_off.shape[1] + gap
        y += size * 1.2
    return canvas


class Renderer:
    def __init__(self, cfg, W, H, words, ctx=None):
        self.cfg = cfg or {}; self.W, self.H = W, H; self.words = words; self.ctx = ctx or {}
        self.fn = CAPTIONS.get(self.cfg.get('kind', 'word_pop'))
        if self.fn is None:
            raise KeyError(f"unknown caption kind {self.cfg.get('kind')}, have {sorted(CAPTIONS)}")

    def render(self, t, ctx=None):
        if not self.words: return None
        c = dict(self.ctx); c.update(ctx or {})
        return self.fn(t, self.words, self.cfg, self.W, self.H, c)

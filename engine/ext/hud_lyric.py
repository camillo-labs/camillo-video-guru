"""hud-lyric template: lyric words behind the subject, a fake machine-vision HUD, the detect wipe, the heat band and the
glitch reveal. Used by the styles hud-lyric-heat and hud-lyric-light.

Effects (events planned by the style rules, so they land on the new song's beats):
  hud_bar     brown DETECTING bar with typewriter dots, scrolling readouts, X marks, L brackets, optional card and network
  hud_wipe    brown band across the caption row, the subject shown as a pale inverted cut-out   (layer pre)
  hud_heat    thermal gradient map of a central band that slides sideways, gold rim on the subject
  hud_marks   red square markers and X marks jumping between corners
  hud_glitch  block displacement, RGB tear and black dropouts (the opening reveal)
Caption kind:
  hud_row     a 2 to 3 word phrase justified across the caption row, hidden behind the subject, theme colour per heat flash,
              mint with a pink ghost during a wipe
Overlay:
  hud_end_card  optional dark end card with a typed handle (no platform logos)
"""
import numpy as np
import cv2
import fx as fxm
import captions as capm
from captions import caption, text_rgba
from fx import fx
from render import overlay

BROWN = (66, 84, 107)        # BGR of #6b5442
MINT = (0, 245, 160)         # RGB
HEAT_STOPS = [(0.0, (0, 0, 0)), (0.15, (97, 3, 6)), (0.35, (170, 10, 3)), (0.55, (221, 122, 29)), (0.70, (251, 133, 18)),
              (0.88, (246, 197, 80)), (1.0, (255, 240, 175))]


def _lut(stops):
    xs = [s[0] * 255 for s in stops]
    out = np.zeros((256, 3), np.uint8)
    for c in range(3):
        out[:, 2 - c] = np.interp(np.arange(256), xs, [s[1][c] for s in stops])   # to BGR
    return out


HEAT_LUT = _lut(HEAT_STOPS)


def _paste(img, rgba, x, y, alpha=1.0):
    """Alpha-composite an RGBA tile (RGB order) onto a BGR frame with its top-left at (x, y)."""
    h, w = rgba.shape[:2]
    H, W = img.shape[:2]
    xa, ya, xb, yb = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if xb <= xa or yb <= ya:
        return
    t = rgba[ya - y:yb - y, xa - x:xb - x].astype(np.float32)
    a = t[..., 3:4] / 255.0 * alpha
    dst = img[ya:yb, xa:xb].astype(np.float32)
    img[ya:yb, xa:xb] = (dst * (1 - a) + t[..., :3][..., ::-1] * a).astype(np.uint8)


def _hud_cfg(ctx):
    return (ctx.get('style') or {}).get('hud', {})


def _frames_in(k, ctx):
    return int(round(k['t'] * ctx['fps']))


def _ellipse_mask(W, H, cy):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = ((xx - W / 2) / (0.13 * W)) ** 2 + ((yy - cy * H) / (0.34 * H)) ** 2
    return np.clip(1.4 - d, 0, 1)


def _events(ctx, name):
    return [e for e in ctx['edl']['events'] if e['fx'] == name]


def _state(ctx, t):
    """Theme index (heat flashes started so far), whether a wipe or heat flash is live."""
    ev = ctx['edl']['events']
    heats = [e for e in ev if e['fx'] == 'hud_heat']
    n_heat = sum(1 for e in heats if e['t0'] <= t + 1e-6)
    wipe = any(e['fx'] == 'hud_wipe' and e['t0'] - 1e-6 <= t < e['t1'] for e in ev)
    heat = any(e['fx'] == 'hud_heat' and e['t0'] - 1e-6 <= t < e['t1'] for e in heats)
    return n_heat, wipe, heat


# ---------------------------------------------------------------- caption row

@caption('hud_row')
def hud_row(t, words, cfg, W, H, ctx):
    """Phrase = all words sharing a phrase index, shown from the first word's onset until the next phrase."""
    P = ctx['edl']['music']['beat_period']
    D = ctx['edl']['duration']
    hcfg = _hud_cfg(ctx)
    end = hcfg.get('end_card_beats', 0)
    if end and t >= D - end * P:
        return None
    onsets = {}
    for w in words:
        onsets[w['phrase']] = min(onsets.get(w['phrase'], 1e9), w['t0'])
    live = [p for p, o in onsets.items() if o <= t + 1e-6]
    if not live:
        return None
    ph = max(live, key=lambda p: onsets[p])
    nxt = [o for p, o in onsets.items() if o > onsets[ph]]
    hold = cfg.get('max_hold_beats', 3.0) * P
    if t > onsets[ph] + hold and not (nxt and t < min(nxt)) and not (not nxt and cfg.get('hold_last')):
        return None
    pw = [w for w in words if w['phrase'] == ph]
    n_heat, wipe, heat = _state(ctx, t)
    themes = cfg.get('themes') or [{'color': [212, 17, 23]}]
    th = themes[n_heat % len(themes)]
    base = min(W, H * 1.3)
    size = int(cfg.get('size_frac', 0.133) * H if W >= H else cfg.get('size_frac_portrait', cfg.get('size_frac', 0.133)) * H * 0.62)
    font = cfg.get('font', 'Arial Black')
    glow = th.get('glow', cfg.get('glow', 0))
    wc = cfg.get('wipe_color', 'mint')
    col = (tuple(MINT) if wc == 'mint' else tuple(wc) if isinstance(wc, list) else tuple(th['color'])) if wipe else tuple(th['color'])
    tiles = []
    for w in pw:
        txt = w['text'].upper()
        im = text_rgba(txt, font, size, col, 0, (0, 0, 0), 0, ())
        tiles.append(im)
    span = cfg.get('span', 0.80) * W
    gap_em = cfg.get('gap_em')
    if gap_em is not None:                          # natural word spacing, the whole phrase scaled to fill the span
        tw = sum(i.shape[1] for i in tiles); gapn = gap_em * size
        need = tw + gapn * (len(tiles) - 1)
        sc = min(span / need, cfg.get('max_scale', 1.6)) if cfg.get('fit_up', True) else min(1.0, span / need)
        if abs(sc - 1) > 0.01:
            tiles = [cv2.resize(i, (max(1, int(i.shape[1] * sc)), max(1, int(i.shape[0] * sc))), interpolation=cv2.INTER_AREA if sc < 1 else cv2.INTER_LINEAR) for i in tiles]
        tw = sum(i.shape[1] for i in tiles); gap = gapn * sc
        x0 = (W - (tw + gap * (len(tiles) - 1))) / 2
        n = len(tiles)
    else:
        tw = sum(i.shape[1] for i in tiles)
        min_gap = 0.4 * size * (len(tiles) > 1)
        need = tw + min_gap * (len(tiles) - 1)
        if need > span:                                # shrink to fit, keeping a readable gap between words
            sc = span / need
            tiles = [cv2.resize(i, (max(1, int(i.shape[1] * sc)), max(1, int(i.shape[0] * sc))), interpolation=cv2.INTER_AREA) for i in tiles]
            tw = sum(i.shape[1] for i in tiles)
        n = len(tiles)
        gap = max((span - tw) / (n - 1), min_gap * (span / max(need, span))) if n > 1 else 0
        x0 = (W - span) / 2 if n > 1 else (W - tw) / 2
    cy = int(cfg.get('y', 0.5) * H)
    canvas = np.zeros((H, W, 4), np.uint8)
    xs = []
    x = x0
    for im in tiles:
        xs.append(int(x)); x += im.shape[1] + gap
    for im, x in zip(tiles, xs):
        y = cy - im.shape[0] // 2
        if wipe and cfg.get('wipe_ghost', True):   # pink ghost behind the mint caption
            ghost = text_rgba(pw[tiles.index(im)]['text'].upper(), font, size, (230, 10, 150), 0, (0, 0, 0), 0, ()) if False else None
        if glow and not wipe:
            g = np.zeros((im.shape[0] + 40, im.shape[1] + 40, 4), np.uint8)
            g[20:20 + im.shape[0], 20:20 + im.shape[1]] = im
            gb = cv2.GaussianBlur(g, (0, 0), glow * H / 576)
            gb[..., 3] = (gb[..., 3] * 0.6).astype(np.uint8)
            capm.blit(canvas, gb, x - 20, y - 20, 1, 1, anchor='lt')
        if wipe and cfg.get('wipe_ghost', True):
            pink = im.copy(); pink[..., :3] = (230, 10, 150)
            capm.blit(canvas, pink, x - int(4 * H / 576), y + int(2 * H / 576), 1, 1, anchor='lt')
        capm.blit(canvas, im, x, y, 1, 1, anchor='lt')
    # hide behind the subject, with a soft ellipse when no matte is available
    m = ctx.get('mask')
    if m is None and cfg.get('fallback_ellipse', True):
        m = _ellipse_mask(W, H, cfg.get('y', 0.5))
    dt = cfg.get('depth_text') or {}
    if dt.get('enabled', True) and dt.get('behind_ratio') is not None:      # some phrases sit in front of the subject
        r = dt['behind_ratio']; order = sorted(onsets, key=lambda p_: onsets[p_]).index(ph)
        if not (np.ceil((order + 1) * r - 1e-9) > np.ceil(order * r - 1e-9)): m = None
    if m is not None and cfg.get('min_visible', 0.55) > 0:       # a phrase the subject hides too much stays in front so it can be read
        al = canvas[..., 3].astype(np.float32)
        if al.sum() > 0 and float((al * (1 - m)).sum() / al.sum()) < cfg.get('min_visible', 0.55): m = None
    if m is not None:
        canvas[..., 3] = (canvas[..., 3].astype(np.float32) * (1 - m)).astype(np.uint8)
    ctx['store']['hud_cap'] = (ctx['frame'], canvas, cfg.get('band_color'))
    return canvas


# ---------------------------------------------------------------- effects

def _rng_for(ctx, k, salt=0):
    return np.random.default_rng(int(ctx['frame'] // 2) * 7919 + salt)


@fx('hud_bar')
def hud_bar(img, k, p, ctx):
    H, W = img.shape[:2]; s = H / 576
    out = img.copy()
    n = _frames_in(k, ctx)
    ev_salt = int(round(ctx['t'] - k['t'], 2) * 100)
    rng = _rng_for(ctx, k, ev_salt)
    bh = int(0.11 * H)
    slide = min(1.0, (n + 1) / 2)
    y_bar = int(-bh + bh * slide)
    # readouts first, so the bar sits on top
    side = p.get('side', 'left')
    lines = []
    keys = ['x:', 'y:', 'A%ps:', 'X%ps:', 'SIN&q:', 'Xor:', 'And:', 'Or:']
    for kk in keys:
        lines.append(f'{kk} {rng.uniform(0, 9999):.12f}')
    glyph = '0123456789ABCDEF#%&@'
    for _ in range(7):
        lines.append(''.join(rng.choice(list(glyph), 14)))
    fsz = int(10 * s * 1.1)
    jit = (n // p.get('mark_frames', 4)) % 3 if p.get('reroll') else 0
    xr = (int(0.09 * W) if side == 'left' else int(0.87 * W) - int(110 * s)) + int(jit * 0.06 * W * (1 if side == 'left' else -1))
    yr = int(0.17 * H) + int(jit * 0.07 * H)
    reveal = min(len(lines), int((n + 1) * 2.5))
    for i, ln in enumerate(lines[:reveal]):
        im = text_rgba(ln, 'Menlo', fsz, (255, 255, 255), 0, (0, 0, 0), 0, (1, 1, 1, 0.6))
        _paste(out, im, xr, yr + int(i * fsz * 1.25), 0.9)
    # X mark, jumping every 4 frames
    if p.get('xmark', True):
        j = (n // p.get('mark_frames', 4)) % 3
        pos = [(0.88, 0.28), (0.5, 0.5), (0.12, 0.62)][j] if side == 'left' else [(0.12, 0.28), (0.5, 0.5), (0.88, 0.62)][j]
        cx, cy = int(pos[0] * W), int(pos[1] * H); r = int(45 * s)
        for off, col in ((2, (0, 0, 0)), (0, (255, 255, 255))):
            o = int(off * s)
            cv2.line(out, (cx - r + o, cy - r + o), (cx + r + o, cy + r + o), col, max(1, int(2 * s)), cv2.LINE_AA)
            cv2.line(out, (cx - r + o, cy + r + o), (cx + r + o, cy - r + o), col, max(1, int(2 * s)), cv2.LINE_AA)
    # L brackets at the frame edge
    if p.get('brackets', True):
        L = int(40 * s); mg = int(0.05 * W); t2 = max(1, int(2 * s)); by = int(0.30 * H)
        for (x, y, dx, dy) in ((mg, by, 1, 1), (W - mg, by + int(0.25 * H), -1, -1)):
            cv2.line(out, (x, y), (x + dx * L, y), (255, 255, 255), t2, cv2.LINE_AA)
            cv2.line(out, (x, y), (x, y + dy * L), (255, 255, 255), t2, cv2.LINE_AA)
    # card sliding across
    if p.get('card'):
        u = k['u']
        cx = int((-0.2 + 1.3 * u) * W); cw, ch = int(200 * s), int(110 * s); cy = int(0.62 * H)
        if p.get('reroll'):
            cx = int((0.1 + 0.25 * ((n // 4) % 3)) * W); cy = int((0.5 + 0.12 * ((n // 4) % 2)) * H)
        sh = out[cy + 4:cy + ch + 4, max(0, cx + 4):max(0, cx + cw + 4)]
        if sh.size:
            out[cy + 4:cy + ch + 4, max(0, cx + 4):max(0, cx + cw + 4)] = (sh * 0.5).astype(np.uint8)
        x0, x1 = max(0, cx), min(W, cx + cw)
        if x1 > x0:
            out[cy:cy + ch, x0:x1] = (238, 232, 230)
    # network of thin curves with ringed nodes
    if p.get('network'):
        r2 = np.random.default_rng(ev_salt + 11)
        drift = k['u'] * 0.04 * W
        ov = out.copy()
        for _ in range(14):
            pts = np.array([[r2.uniform(0, W) + drift * np.sin(i + _), r2.uniform(0, H)] for i in range(4)], np.float32)
            t_ = np.linspace(0, 1, 30)
            curve = np.array([(1 - a) ** 3 * pts[0] + 3 * (1 - a) ** 2 * a * pts[1] + 3 * (1 - a) * a ** 2 * pts[2] + a ** 3 * pts[3] for a in t_], np.int32)
            cv2.polylines(ov, [curve], False, (255, 255, 255), 1, cv2.LINE_AA)
        for _ in range(10):
            c = (int(r2.uniform(0.05, 0.95) * W + drift), int(r2.uniform(0.1, 0.9) * H))
            cv2.circle(ov, c, int(5 * s), (40, 40, 40) if r2.random() < 0.3 else (255, 255, 255), max(1, int(1.5 * s)), cv2.LINE_AA)
        out = cv2.addWeighted(out, 0.45, ov, 0.55, 0)
    # top bar with typewriter label
    cv2.rectangle(out, (0, y_bar), (W, y_bar + bh), BROWN, -1)
    nd = min(18, n + 1)
    label = 'DETECTING' + '.' * nd
    if n < 3:
        label = ''.join(rng.choice(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 9)) + '.' * nd
    im = text_rgba(label, 'Arial Black', int(14 * s), (255, 255, 255), 0, (0, 0, 0), 0, ())
    _paste(out, im, int(0.12 * W), y_bar + (bh - im.shape[0]) // 2)
    # fade out in the last 15 percent
    a = 1.0 if k['u'] < 0.85 else max(0.0, (1 - k['u']) / 0.15)
    if p.get('flicker') and n > 3 and n % p['flicker'] == p['flicker'] - 1: return img      # one frame off, like the reference's twitchy readout
    return cv2.addWeighted(img, 1 - a, out, a, 0) if a < 1 else out


@fx('hud_wipe')
def hud_wipe(img, k, p, ctx):
    """Detect wipe (draw it on the pre layer so the caption sits on top). Brown band, subject as a pale inverted cut-out."""
    H, W = img.shape[:2]; s = H / 576
    row = p.get('band_y', _hud_cfg(ctx).get('row_y', 0.5))
    hh = p.get('band_h', 0.12)
    y0, y1 = int((row - hh) * H), int((row + hh) * H)
    n = _frames_in(k, ctx)
    cover = int(W * min(p.get('width', 1.0), (n + 1) / 3 * p.get('width', 1.0)))
    out = img.copy()
    band = out[y0:y1, :cover]
    band[:] = BROWN
    if p.get('texture') and band.size:               # toned copy of the footage instead of a flat fill
        g0 = cv2.cvtColor(img[y0:y1, :cover], cv2.COLOR_BGR2GRAY).astype(np.float32)[..., None] / 255.0
        band[:] = np.clip(np.array(BROWN, np.float32) * np.clip(0.4 + 0.5 * g0, 0, 0.95), 0, 255).astype(np.uint8)
    m = ctx.get('mask')
    src = img[y0:y1, :cover]
    if m is not None:
        g = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY).astype(np.float32)
        pale = np.clip(0.35 * (255 - g) + 150, 0, 255)
        tint = np.array([255, 236, 214], np.float32) / 255.0
        cut = (pale[..., None] * tint).astype(np.uint8)
        mm = (m[y0:y1, :cover] > 0.5)[..., None]
        band[:] = np.where(mm, cut, band)
    im = text_rgba('DETECTING......', 'Arial Black', int(11 * s * 1.2), (255, 255, 255), 0, (0, 0, 0), 0, ())
    _paste(out, im, int(0.1 * W), y1 - im.shape[0] - int(6 * s))
    return out


@fx('hud_heat')
def hud_heat(img, k, p, ctx):
    H, W = img.shape[:2]; s = H / 576
    y0, y1 = int(p.get('y0', 0.115) * H), int(p.get('y1', 0.884) * H)
    u = k['u']
    band = img[y0:y1]
    g = cv2.cvtColor(band, cv2.COLOR_BGR2GRAY)
    if p.get('normalise'):                          # stretch the band's luma so bright and dark footage land on the same heat colours
        lo, hi = np.percentile(g, 3), np.percentile(g, 97)
        g = np.clip((g.astype(np.float32) - lo) / max(1.0, hi - lo), 0, 1)
        g = (np.clip(g * p.get('range', 0.8) + p.get('floor', 0.05), 0, 1) * 255).astype(np.uint8)
    else:
        g = cv2.convertScaleAbs(g, alpha=p.get('contrast', 1.25), beta=p.get('beta', 5))
    heat = HEAT_LUT[g]
    m = ctx.get('mask')
    if m is not None:
        mb = (m[y0:y1] > 0.5).astype(np.uint8)
        edge = cv2.dilate(mb, np.ones((5, 5), np.uint8)) - cv2.erode(mb, np.ones((3, 3), np.uint8))
        if p.get('subject_black') and ctx.get('mask_kind') == 'person' and mb.mean() < 0.3: heat[mb > 0] = (8, 4, 30)
        heat[edge > 0] = (109, 191, 255)           # gold rim in BGR
    shift = int(W * fxm.ease('out_cubic', min(1.0, u / p.get('slide_portion', 0.6)))) if p.get('slide', True) else 0
    heat = np.roll(heat, shift, axis=1)
    a = 1.0 if u < 0.85 else (1 - u) / 0.15
    out = img.copy()
    out[y0:y1] = cv2.addWeighted(band, 1 - a, heat, a, 0)
    if u < 0.12:                                    # near-white first frames
        out = cv2.addWeighted(out, 1 - 0.75 * (1 - u / 0.12), np.full_like(out, 255), 0.75 * (1 - u / 0.12), 0)
    cap = ctx['store'].get('hud_cap')
    if cap and cap[0] == ctx['frame'] and cap[2]:   # caption redrawn over the band in a bright band colour so it stays readable
        al = (cap[1][..., 3:4].astype(np.float32) / 255.0)[y0:y1] * a
        col = np.array(cap[2][::-1], np.float32)
        out[y0:y1] = (out[y0:y1].astype(np.float32) * (1 - al) + col * al).astype(np.uint8)
    return out


@fx('hud_marks')
def hud_marks(img, k, p, ctx):
    H, W = img.shape[:2]; s = H / 576
    out = img.copy()
    n = _frames_in(k, ctx)
    rng = np.random.default_rng((n // 4) * 31 + int(ctx['t'] * 10) % 7)
    sz = int(p.get('size', 70) * s)
    corners = [(0.03, 0.05), (0.83, 0.05), (0.03, 0.78), (0.83, 0.78), (0.4, 0.04)]
    for i in range(p.get('count', 2)):
        cx, cy = corners[int(rng.integers(0, len(corners)))]
        col = tuple(p.get('color', [192, 16, 14]))[::-1] if i == 0 else (29, 122, 221)[::-1]
        x, y = int(cx * W), int(cy * H)
        cv2.rectangle(out, (x, y), (x + sz, y + sz), col, -1)
    return out


@fx('hud_glitch')
def hud_glitch(img, k, p, ctx):
    H, W = img.shape[:2]
    r = ctx['rng']; inten = (1 - k['u']) ** 0.7 * p.get('amount', 1.0)
    out = img.copy()
    for _ in range(int(r.integers(6, 15) * (0.4 + inten))):
        y = int(r.uniform(0, H)); hh = int(r.uniform(4, 40) * H / 576)
        dx = int(r.uniform(-80, 80) * W / 1024 * (0.4 + inten))
        out[y:y + hh] = np.roll(out[y:y + hh], dx, axis=1)
    if r.random() < 0.2 + 0.5 * inten:
        b, g, rr = cv2.split(out)
        off = max(1, int(2 * W / 1024))
        out = cv2.merge([np.roll(b, off, 1), g, np.roll(rr, -off, 0)])
    m = ctx.get('mask')
    for _ in range(int(3 * inten) + 1):
        bw, bh = int(r.uniform(0.04, 0.2) * W), int(r.uniform(0.02, 0.08) * H)
        if m is not None and m.max() > 0.5:
            ys, xs = np.where(m > 0.5); i = int(r.integers(0, len(xs)))
            x0, y0 = int(xs[i] - bw / 2), int(ys[i] - bh / 2)
        else:
            x0, y0 = int(r.uniform(0.2, 0.7) * W), int(r.uniform(0.2, 0.8) * H)
        out[max(0, y0):max(0, y0) + bh, max(0, x0):max(0, x0) + bw] = 0
    return out


# ---------------------------------------------------------------- end card

@overlay('hud_end_card')
def end_card(img, t, ctx, cfg):
    P = ctx['edl']['music']['beat_period']; D = ctx['edl']['duration']
    t0 = D - cfg.get('beats', 6) * P
    if t < t0:
        return img
    H, W = img.shape[:2]; s = H / 576
    out = np.zeros_like(img); out[:] = (31, 15, 13)          # #0d0f1f in BGR
    u = (t - t0) / max(1e-6, D - t0)
    title = cfg.get('title', '')
    if title:
        im = text_rgba(title, 'Arial Black', int(0.06 * min(W, H) * 1.3), (255, 255, 255), 0, (0, 0, 0), 0, ())
        _paste(out, im, (W - im.shape[1]) // 2, int(0.40 * H))
    bw, bh = int(0.5 * min(W, H * 1.2)), int(34 * s)
    x0, y0 = (W - bw) // 2, int(0.58 * H)
    cv2.rectangle(out, (x0 - 3, y0 - 2), (x0 + bw - 3, y0 + bh - 2), (255, 220, 0), -1)
    cv2.rectangle(out, (x0 + 3, y0 + 2), (x0 + bw + 3, y0 + bh + 2), (90, 40, 255), -1)
    cv2.rectangle(out, (x0, y0), (x0 + bw, y0 + bh), (255, 255, 255), -1)
    handle = cfg.get('handle', '')
    typed = handle[:int(len(handle) * min(1.0, max(0.0, (u - 0.2) / 0.5)))]
    if typed:
        im = text_rgba(typed, 'Helvetica Bold', int(14 * s * 1.3), (30, 30, 40), 0, (0, 0, 0), 0, ())
        _paste(out, im, x0 + int(16 * s), y0 + (bh - im.shape[0]) // 2)
    return out


@overlay('hud_end_matte')
def end_matte(img, t, ctx, cfg):
    """Last frames: the caption (and a person matte, if any) on black, as the reference ends a pass."""
    D = ctx['edl']['duration']; fps = ctx['fps']
    if t < D - cfg.get('frames', 3) / fps: return img
    out = np.zeros_like(img)
    cap = ctx['store'].get('hud_cap')
    if cap is not None and abs(cap[0] - ctx['frame']) <= 6:
        al = cap[1][..., 3:4].astype(np.float32) / 255.0
        col = cap[1][..., 2::-1].astype(np.float32)
        out = (col * al).astype(np.uint8)
    return out

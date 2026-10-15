"""Extensions for the kinetic-card-explainer style (vertical explainer built from one-idea scenes on flat dark, light, beige and
terracotta backgrounds, an orange pixel mascot, pills and arrows that spring in, one or two bold words at a time with an italic
serif accent word, talking-head cut-ins and a "comment KEYWORD" end card).

Registers
  fx       kc_scene     paints the whole frame for one scene (pre layer, one event per shot). Params: sequence, a list of scene specs
                        cycled by shot index: {bg, scene, head, labels, mascot}. bg dark|light|beige|terra. scene hub|doc|terminal|
                        chips|timeline|media|stat|logo|none. head none|split|full (the footage shows through).
  caption  kc_word      one or two words at a time, hard swaps on the first word, a serif italic accent word, ink that follows the
                        background, and a serif-italic stacked treatment when the scene is a head cut-in
  overlay  kc_end       the end card: split with the head, then a card, then a dim for the last seconds

Every move is a closed-form spring (ext.typeset.spring), so any frame can be rendered alone. Self-contained, nothing edits the core.
"""
import numpy as np
import cv2
from fx import fx
from captions import caption
from render import overlay
from ext.typeset import (vfont, text_rgba, baseline_text, text_width, over, rrect, shadowed, spring, fill)

DARK = (14, 11, 17); LIGHT = (232, 232, 232); BEIGE = (231, 227, 216); TERRA = (200, 115, 89)
BG = {'dark': DARK, 'light': LIGHT, 'beige': BEIGE, 'terra': TERRA}
ACCENT = (38, 178, 241); ACCENT_SOFT = (59, 173, 221); ORANGE = (222, 112, 78); INK = (15, 15, 17); PAPER = (251, 248, 253)
SANS = 'inter tight'


def _rgba_fill(w, h, rgb, a=255):
    out = np.zeros((int(h), int(w), 4), np.uint8); out[..., :3] = rgb; out[..., 3] = a; return out


def _is_dark(bg): return sum(bg) / 3 < 110


# ------------------------------------------------------------------ sprites

_sp = {}


def _cached(key, fn):
    if key not in _sp:
        if len(_sp) > 600: _sp.clear()
        _sp[key] = fn()
    return _sp[key]


MASCOT = ['..X.....X..',
          '...X...X...',
          '..XXXXXXX..',
          '.XX.XXX.XX.',
          'XXXXXXXXXXX',
          'X.XXXXXXX.X',
          'X.X.....X.X',
          '...XX.XX...']


def mascot(px, rgb, eye=None):
    """Pixel mascot, an original eleven by eight block creature with antennae and four legs. px is the block size in pixels."""
    def mk():
        h, w = len(MASCOT), len(MASCOT[0])
        a = np.zeros((h * px, w * px, 4), np.uint8)
        for y, row in enumerate(MASCOT):
            for x, c in enumerate(row):
                if c == 'X': a[y * px:(y + 1) * px, x * px:(x + 1) * px] = (*rgb, 255)
        # eyes are two cut-out blocks in the body row
        for ex in (3, 7):
            a[4 * px:5 * px, ex * px:(ex + 1) * px] = (0, 0, 0, 0) if eye is None else (*eye, 255)
        return a
    return _cached(('mascot', px, rgb, eye), mk)


def pill(text, size, kind='dark', pad=0.42):
    def mk():
        wg = 700
        tw = text_width(text, SANS, size, wg, 0); h = int(size * (1 + pad * 1.3)); w = int(tw + size * pad * 2.2)
        fills = {'dark': (DARK, PAPER, None), 'blue': (ACCENT, (255, 255, 255), None), 'white': ((255, 255, 255), INK, INK),
                 'outline': ((255, 255, 255), ACCENT, ACCENT), 'tag': ((70, 70, 78), PAPER, None), 'ghost': ((238, 238, 240), (150, 150, 158), (190, 190, 198))}
        f, tc, oc = fills[kind]
        base = rrect(w, h, h / 2, f)
        if oc is not None:
            ring = rrect(w, h, h / 2, oc); inner = rrect(w - 4, h - 4, h / 2 - 2, f)
            base = ring.copy(); base[2:-2, 2:-2] = inner
        t = text_rgba(text, SANS, size, tc, wg, 0, None)
        th, tw_ = t.shape[:2]
        y0 = (h - th) // 2; x0 = (w - tw_) // 2
        base[y0:y0 + th, x0:x0 + tw_] = _blend(base[y0:y0 + th, x0:x0 + tw_], t)
        if kind in ('blue', 'dark', 'white'):
            base, _ = shadowed(base, size * 0.25, size * 0.12, 0.28)
        return base
    return _cached(('pill', text, size, kind), mk)


def _blend(dst, src):
    sa = src[..., 3:4].astype(np.float32) / 255; da = dst[..., 3:4].astype(np.float32) / 255; oa = sa + da * (1 - sa)
    oc = (src[..., :3] * sa + dst[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6)
    out = dst.copy(); out[..., :3] = oc.astype(np.uint8); out[..., 3] = (oa[..., 0] * 255).astype(np.uint8); return out


def icon(kind, r, rgb=None):
    """Generic round or square glyph icons: play (video), square-letter, chat bubble, doc."""
    def mk():
        s = int(r * 2); a = np.zeros((s, s, 4), np.uint8)
        if kind == 'play':
            a = rrect(s, int(s * 0.72), s * 0.18, rgb or (230, 30, 30)); full = np.zeros((s, s, 4), np.uint8); y0 = (s - a.shape[0]) // 2; full[y0:y0 + a.shape[0]] = a; a = full
            tri = np.array([[s * 0.4, s * 0.31], [s * 0.4, s * 0.69], [s * 0.66, s * 0.5]], np.int32)
            cv2.fillPoly(a, [tri], (255, 255, 255, 255))
        elif kind == 'letter':
            a = rrect(s, s, s * 0.08, rgb or (240, 100, 40))
            t = text_rgba('Y', SANS, int(s * 0.62), (255, 255, 255), 600, 0, None)
            y0 = (s - t.shape[0]) // 2; x0 = (s - t.shape[1]) // 2; a[y0:y0 + t.shape[0], x0:x0 + t.shape[1]] = _blend(a[y0:y0 + t.shape[0], x0:x0 + t.shape[1]], t)
        elif kind == 'chat':
            a = np.zeros((s, s, 4), np.uint8); cv2.circle(a, (s // 2, int(s * 0.45)), int(s * 0.42), (*(rgb or (255, 90, 30)), 255), -1)
            cv2.fillPoly(a, [np.array([[s * 0.62, s * 0.78], [s * 0.86, s * 0.95], [s * 0.76, s * 0.66]], np.int32)], (*(rgb or (255, 90, 30)), 255))
            for ex in (0.36, 0.64): cv2.circle(a, (int(s * ex), int(s * 0.45)), int(s * 0.07), (255, 255, 255, 255), -1)
        else:                                                   # doc
            a = rrect(s, s, s * 0.14, rgb or (20, 180, 140))
            for i in range(3): cv2.rectangle(a, (int(s * 0.25), int(s * (0.3 + 0.15 * i))), (int(s * 0.75), int(s * (0.36 + 0.15 * i))), (255, 255, 255, 255), -1)
        return a
    return _cached(('icon', kind, r, rgb), mk)


def card_sprite(w, h, rgb=(255, 255, 255), radius=0.03, shadow=True):
    def mk():
        c = rrect(w, h, radius * w, rgb)
        return shadowed(c, w * 0.012, w * 0.012, 0.22)[0] if shadow else c
    return _cached(('card', int(w), int(h), rgb, shadow), mk)


def arrow(canvas, p0, p1, u, rgb, th):
    """Line with a dot at the start and an arrow head at the tip, drawn progressively. canvas BGR."""
    if u <= 0.01: return
    x0, y0 = p0; x1, y1 = p1
    xe = x0 + (x1 - x0) * min(1, u); ye = y0 + (y1 - y0) * min(1, u)
    bgr = rgb[::-1]
    cv2.line(canvas, (int(x0), int(y0)), (int(xe), int(ye)), bgr, max(2, int(th)), cv2.LINE_AA)
    cv2.circle(canvas, (int(x0), int(y0)), int(th * 1.7), (ACCENT[::-1]), -1, cv2.LINE_AA)
    if u > 0.85:
        ang = np.arctan2(y1 - y0, x1 - x0); L = th * 5.0
        pts = np.array([[x1, y1], [x1 - L * np.cos(ang - 0.45), y1 - L * np.sin(ang - 0.45)], [x1 - L * np.cos(ang + 0.45), y1 - L * np.sin(ang + 0.45)]], np.int32)
        cv2.fillPoly(canvas, [pts], bgr, cv2.LINE_AA)


def pop(img, sprite, cx, cy, t, t0, zeta=0.55, omega=24.0, a=1.0, rot=0.0):
    """Spring a sprite in at (cx, cy) from time t0: scale follows the closed-form spring, alpha ramps in 80 ms."""
    sc = spring(t - t0, zeta, omega)
    if sc <= 0.01: return
    al = min(1.0, (t - t0) / 0.08) * a
    if rot:
        h, w = sprite.shape[:2]; M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, 1.0); sprite = cv2.warpAffine(sprite, M, (w, h))
    over(img, sprite, cx, cy, al, sc, centre=True)


# ------------------------------------------------------------------ scenes

def _labels(spec, ctx, t_abs, n, default):
    lab = spec.get('labels')
    if lab: return (list(lab) + list(default))[:n]
    ws = [w['text'].strip('.,!?"\'').lower() for w in ctx.get('words', []) if t_abs - 0.3 <= w['t0'] < t_abs + 2.5 and len(w['text']) > 4]
    out = []
    for w in ws:
        if w not in out: out.append(w)
    return (out + list(default))[:n]


def scene_hub(img, W, H, t, spec, ctx, bg):
    labs = _labels(spec, ctx, ctx['t'] - t, 3, ['research', 'sources', 'ideas'])
    cx, cy = 0.5 * W, 0.44 * H
    sat = [(0.17, 0.27, 'play'), (0.5, 0.24, 'letter'), (0.83, 0.27, 'chat')]
    m = int(W * 0.019)
    for i, (x, y, k) in enumerate(sat):
        pop(img, icon(k, int(W * 0.075)), x * W, y * H, t, 0.05 + 0.1 * i)
        arrow(img, (x * W, (y + 0.045) * H), (cx + (x - 0.5) * W * 0.18, cy - 0.07 * H), spring(t - 0.28 - 0.1 * i, 1.0, 16), ORANGE, W * 0.004)
        if i == 1: pop(img, pill(labs[0], int(W * 0.045), 'white'), x * W, (y + 0.065) * H, t, 0.2)
    bob = np.sin(t * 7.0) * m * 0.3
    pop(img, mascot(m, (255, 255, 255) if bg == TERRA else ORANGE), cx, cy + bob, t, 0.0)
    pop(img, pill(labs[-1] if len(labs) > 1 else labs[0], int(W * 0.06), 'blue'), cx, 0.565 * H, t, 0.55)


def scene_doc(img, W, H, t, spec, ctx, bg):
    cw, ch = int(W * 0.9), int(H * 0.215)
    cy = 0.425 * H + (1 - spring(t, 0.8, 18)) * 0.05 * H
    over(img, card_sprite(cw, ch), W / 2, cy, 1.0, 1.0, centre=True)
    x0 = W / 2 - cw / 2 + cw * 0.04; fs = int(W * 0.03)
    lines = spec.get('lines') or ['Turn your AI coding assistant into a full', 'video production studio. Describe the idea,', 'it handles research, scripting, assets,', 'editing and the final composition.']
    hi = spec.get('highlight', 'full video production studio')
    for i, ln in enumerate(lines):
        y = cy - ch / 2 + ch * 0.12 + i * fs * 1.5
        if hi in ln and t > 0.9:
            a = ln.index(hi); xa = x0 + text_width(ln[:a], SANS, fs, 500, 0); wa = text_width(hi, SANS, fs, 500, 0) * min(1, spring(t - 0.9, 1.0, 14))
            cv2.rectangle(img, (int(xa), int(y)), (int(xa + wa), int(y + fs * 1.25)), (240, 205, 160), -1)
        t_ = text_rgba(ln, SANS, fs, (40, 40, 44), 500, 0, None); over(img, t_, x0, y)
    if spec.get('row', True):
        for i in range(5): pop(img, mascot(max(2, int(W * 0.006)), ORANGE), (0.24 + 0.13 * i) * W, cy + ch / 2 + 0.04 * H, t, 0.35 + 0.07 * i)


def scene_terminal(img, W, H, t, spec, ctx, bg):
    cw, ch = int(W * 0.9), int(H * 0.3)
    over(img, card_sprite(cw, ch, (22, 20, 28), 0.02, False), W / 2, 0.36 * H, 1.0, 1.0, centre=True)
    x0 = W / 2 - cw / 2 + cw * 0.05; fs = int(W * 0.026); y = 0.36 * H - ch / 2 + ch * 0.07
    over(img, mascot(max(2, int(W * 0.009)), (240, 140, 130)), x0, y)
    for i, tx in enumerate(['Claude Code v2.1', 'Sonnet 5.5', '~/Project']):
        over(img, text_rgba(tx, 'mono', fs, (232, 232, 236) if i == 0 else (150, 150, 160), None, 0, None), x0 + W * 0.15, y + i * fs * 1.35)
    cmd = spec.get('command', 'Make a 60-second animated explainer about how neural networks learn')
    n = int(len(cmd) * min(1.0, max(0.0, (t - 0.15) / 1.0)))
    yy = 0.36 * H + ch * 0.12
    over(img, text_rgba('> ' + cmd[:n][:30], 'mono', fs, (232, 232, 236), None, 0, None), x0, yy)
    if n > 30: over(img, text_rgba('  ' + cmd[30:n], 'mono', fs, (232, 232, 236), None, 0, None), x0, yy + fs * 1.4)
    over(img, text_rgba('>> do not ask on (shift+tab to cycle)', 'mono', int(fs * 0.85), (230, 120, 110), None, 0, None), x0, 0.36 * H + ch * 0.38)


def scene_chips(img, W, H, t, spec, ctx, bg):
    labs = _labels(spec, ctx, ctx['t'] - t, 5, ['research', 'script', 'footage', 'voice', 'music'])
    rows = [(0.5, 0.2), (0.35, 0.265), (0.68, 0.265)]
    pos = [(0.22, 0.32), (0.5, 0.32), (0.78, 0.32), (0.34, 0.385), (0.66, 0.385)]
    for i, l in enumerate(labs[:5]):
        pop(img, pill(l, int(W * 0.042), 'white' if not _is_dark(bg) else 'tag'), pos[i][0] * W, pos[i][1] * H, t, 0.05 + 0.12 * i)
    # waveform bars
    n = 9
    for gi, gx in enumerate((0.3, 0.7)):
        if t < 0.5 + 0.25 * gi: continue
        for i in range(n):
            amp = (0.35 + 0.65 * abs(np.sin(i * 1.7 + gi * 2.1 + t * 9))) * (0.3 + 0.7 * spring(t - 0.5 - 0.25 * gi, 0.8, 16))
            x = (gx - 0.07) * W + i * W * 0.0165; hh = amp * 0.075 * H
            col = ORANGE if gi == 0 else (110, 110, 118)
            cv2.rectangle(img, (int(x), int(0.5 * H - hh)), (int(x + W * 0.007), int(0.5 * H + hh)), col[::-1], -1)
    pop(img, mascot(int(W * 0.017), ORANGE), 0.5 * W, 0.2 * H, t, 0.0)


def scene_timeline(img, W, H, t, spec, ctx, bg):
    y = 0.26 * H; ink = (225, 225, 228) if _is_dark(bg) else (60, 60, 64)
    u = spring(t, 1.0, 12)
    x0, x1 = 0.08 * W, 0.92 * W
    cv2.line(img, (int(x0), int(y)), (int(x0 + (x1 - x0) * u), int(y)), ink[::-1], 2, cv2.LINE_AA)
    for i in range(7):
        x = x0 + (x1 - x0) * i / 6
        if (x - x0) <= (x1 - x0) * u: cv2.line(img, (int(x), int(y - 10)), (int(x), int(y + 10)), ink[::-1], 2, cv2.LINE_AA)
    lab = _labels(spec, ctx, ctx['t'] - t, 1, ['yours'])[0]
    pop(img, pill(lab, int(W * 0.06), 'blue'), 0.5 * W, 0.325 * H, t, 0.25)
    cols = [ORANGE, (30, 30, 34), ORANGE, (30, 30, 34), ORANGE, (30, 30, 34)]
    xs = 0.14 * W
    for i, wd in enumerate([0.07, 0.1, 0.12, 0.05, 0.14, 0.1]):
        pop(img, rrect(wd * W, W * 0.032, W * 0.016, cols[i]), xs + wd * W / 2, 0.385 * H, t, 0.4 + 0.07 * i, 0.7, 20)
        xs += wd * W + W * 0.012
    pop(img, mascot(int(W * 0.017), ORANGE), 0.5 * W + np.sin(t * 5) * W * 0.04, 0.47 * H, t, 0.1)


def scene_media(img, W, H, t, spec, ctx, bg):
    cw, ch = int(W * 0.86), int(W * 0.86 * 9 / 16)
    sprite = _cached(('media', cw, ch, spec.get('tint', 0)), lambda: _media(cw, ch, spec.get('tint', 0)))
    pop(img, sprite, W / 2, 0.38 * H, t, 0.0, 0.8, 16, rot=-2.5 * (1 - spring(t, 0.8, 16)))
    lab = spec.get('pill') or 'Generated clips'
    pop(img, pill(lab, int(W * 0.036), 'dark'), W / 2, 0.38 * H + ch / 2 + W * 0.03, t, 0.4)


def _media(cw, ch, tint):
    a = np.zeros((ch, cw, 3), np.float32)
    yy = np.linspace(0, 1, ch)[:, None]; xx = np.linspace(0, 1, cw)[None, :]
    base = np.array([(10, 16, 34), (34, 20, 16)][tint % 2], np.float32); top = np.array([(30, 50, 90), (120, 70, 30)][tint % 2], np.float32)
    a[:] = base + (top - base) * (1 - yy)[..., None] * 0.9
    glow = np.exp(-(((xx - 0.55) / 0.2) ** 2 + ((yy - 0.62) / 0.12) ** 2)); a += glow[..., None] * np.array([255, 190, 120], np.float32) * 0.8
    a += np.random.default_rng(3).normal(0, 3, a.shape)
    rgba = np.dstack([np.clip(a, 0, 255).astype(np.uint8), np.full((ch, cw), 255, np.uint8)])
    m = rrect(cw, ch, cw * 0.03, (255, 255, 255)); rgba[..., 3] = m[..., 3]
    return shadowed(rgba, cw * 0.012, cw * 0.015, 0.3)[0]


def scene_stat(img, W, H, t, spec, ctx, bg):
    txt = spec.get('stat', '65,896 stars  ·  Oct 10, 2026')
    pop(img, pill(txt, int(W * 0.044), 'white'), 0.5 * W, 0.2 * H, t, 0.0, 0.7, 20)
    pop(img, icon('doc', int(W * 0.09), (245, 245, 247)), 0.2 * W, 0.3 * H, t, 0.2)
    arrow(img, (0.3 * W, 0.3 * H), (0.6 * W, 0.3 * H), spring(t - 0.45, 1.0, 14), ORANGE, W * 0.005)
    pop(img, mascot(int(W * 0.017), ORANGE), 0.78 * W, 0.3 * H, t, 0.75)


def scene_logo(img, W, H, t, spec, ctx, bg):
    cw, ch = int(W * 0.78), int(H * 0.22)
    over(img, card_sprite(cw, ch), W / 2, 0.45 * H, 1.0, 1.0, centre=True)
    pop(img, mascot(int(W * 0.016), (255, 255, 255) if bg == TERRA else ORANGE), W / 2, 0.22 * H, t, 0.0)
    nm = spec.get('name', 'Project')
    pop(img, icon('chat', int(W * 0.07), (40, 30, 30)), W / 2, 0.39 * H, t, 0.1)
    over(img, text_rgba(nm, SANS, int(W * 0.04), INK, 700, 0, None), W / 2 - text_width(nm, SANS, int(W * 0.04), 700, 0) / 2, 0.465 * H)
    cv2.rectangle(img, (int(W * 0.37), int(0.505 * H)), (int(W * 0.37 + W * 0.26 * spring(t - 0.3, 1, 14)), int(0.507 * H)), ORANGE[::-1], -1)
    tg = spec.get('tag', 'The first open-source video production system.')
    over(img, text_rgba(tg, SANS, int(W * 0.02), (50, 50, 56), 500, 0, None), W / 2 - text_width(tg, SANS, int(W * 0.02), 500, 0) / 2, 0.525 * H)


SCENES = {'hub': scene_hub, 'doc': scene_doc, 'terminal': scene_terminal, 'chips': scene_chips, 'timeline': scene_timeline,
          'media': scene_media, 'stat': scene_stat, 'logo': scene_logo}


@fx('kc_scene')
def kc_scene(img, k, p, ctx):
    seq = p.get('sequence') or [{'bg': 'dark', 'scene': 'hub'}]
    spec = seq[ctx['shot_index'] % len(seq)]
    h, w = img.shape[:2]
    mode = spec.get('head', 'none')
    bg = BG[spec.get('bg', 'light')]
    ctx['store']['kc_mode'] = 'head' if mode == 'full' else 'card'
    ctx['store']['kc_bg'] = bg; ctx['store']['kc_raw'] = img; ctx['store']['kc_split'] = mode == 'split'
    if mode == 'full': return img
    out = np.empty_like(img); fill(out, bg)
    fn = SCENES.get(spec.get('scene', 'none'))
    if fn: fn(out, w, h, k['t'], spec, ctx, bg)
    if mode == 'split':
        y0 = int(p.get('split_y', 0.47) * h); edge = max(2, int(0.03 * h))
        a = np.clip(np.arange(edge) / edge, 0, 1)[:, None, None]                   # soft top edge of the head picture
        out[y0 + edge:] = img[y0 + edge:]
        out[y0:y0 + edge] = (np.array(bg[::-1], np.float32) * (1 - a) + img[y0:y0 + edge].astype(np.float32) * a).astype(np.uint8)
    return out


# ------------------------------------------------------------------ captions

STOP = set('the a an and or of to in on for with that this it is are was be as at by from your you i we they he she not but if then so into about their its'.split())
_chunks_cache = {}


def _chunks(words, cfg):
    key = (id(words), len(words))
    if key in _chunks_cache: return _chunks_cache[key]
    out = []; by = {}
    for w in words: by.setdefault(w['phrase'], []).append(w)
    mx = cfg.get('max_words', 2)
    for ph in sorted(by):
        cur = []
        for w in by[ph]:
            acc = w.get('emph') or (cfg.get('auto_accent', True) and len(w['text'].strip('.,!?')) >= cfg.get('accent_min_len', 6) and w['text'].lower().strip('.,!?') not in STOP)
            w['accent'] = bool(acc)
            cur.append(w)
            if acc or len(cur) >= mx: out.append((ph, cur)); cur = []
        if cur: out.append((ph, cur))
    _chunks_cache.clear(); _chunks_cache[key] = out
    return out


@caption('kc_word')
def kc_word(t, words, cfg, W, H, ctx):
    ch = _chunks(words, cfg)
    D = ctx['edl']['duration'] if ctx.get('edl') else 1e9
    if t >= D - cfg.get('stop_before_end_s', 7.2): return None
    cur = None
    for i, (ph, ws) in enumerate(ch):
        if ws[0]['t0'] <= t + 1e-6: cur = i
        else: break
    if cur is None: return None
    ph, ws = ch[cur]
    nxt = ch[cur + 1][1][0]['t0'] if cur + 1 < len(ch) else ws[-1]['t1'] + 0.5
    t_end = min(nxt, ws[-1]['t1'] + cfg.get('hold_max', 0.9))
    if t > t_end: return None
    head = ctx['store'].get('kc_mode') == 'head'
    yc = (cfg.get('y_split', 0.435) if ctx['store'].get('kc_split') else cfg.get('y', 0.70)) * H
    bg = ctx['store'].get('kc_bg', DARK)
    size = int(cfg.get('size_frac', 0.0653) * W)
    canvas = np.zeros((H, W, 4), np.uint8)
    u = (t - ws[0]['t0'])
    if head:
        # serif italic white for what was said, bold light blue for the closing chunk, built up through the phrase
        prev = [w for p_, c_ in ch[:cur] if p_ == ph for w in c_]
        lines = []
        if prev: lines.append((' '.join(w['text'] for w in prev), 'serif'))
        lines.append((' '.join(w['text'] for w in ws), 'key' if prev else 'serif'))
        fs = int(size * 0.98); lh = fs * 1.28; y = cfg.get('y_head', 0.69) * H - (len(lines) - 1) * lh / 2
        for txt, kind in lines:
            if kind == 'serif': im = text_rgba(txt, 'playfair italic', fs, (255, 255, 255), 400, 0, (0, 2, 5, 0.6))
            else: im = text_rgba(txt, SANS, int(fs * 1.02), tuple(cfg.get('head_key_color', [160, 224, 255])), 700, 0, (0, 2, 5, 0.5))
            _paste(canvas, im, W / 2 - im.shape[1] / 2, y - im.shape[0] / 2); y += lh
        return canvas
    ink = PAPER if (_is_dark(bg) or bg == TERRA) else INK
    acc = tuple(cfg.get('accent', ACCENT_SOFT))
    parts = []
    for w in ws:
        txt = w['text']
        if w.get('accent'): parts.append(text_rgba(txt, 'playfair italic', int(size * 1.17), acc, 400, 0, None))
        else: parts.append(text_rgba(txt, SANS, size, ink, 700, 0, None))
    gap = size * 0.28
    total = sum(p_.shape[1] for p_ in parts) + gap * (len(parts) - 1)
    x = W / 2 - total / 2
    for p_ in parts:
        _paste(canvas, p_, x, yc - p_.shape[0] / 2 + size * 0.04); x += p_.shape[1] + gap
    return canvas


def _paste(canvas, rgba, x, y):
    h, w = rgba.shape[:2]; x0, y0 = int(round(x)), int(round(y))
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(canvas.shape[1], x0 + w), min(canvas.shape[0], y0 + h)
    if xb <= xa or yb <= ya: return
    s = rgba[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32); d = canvas[ya:yb, xa:xb].astype(np.float32)
    sa = s[..., 3:4] / 255; da = d[..., 3:4] / 255; oa = sa + da * (1 - sa)
    oc = (s[..., :3] * sa + d[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6)
    canvas[ya:yb, xa:xb, :3] = oc.astype(np.uint8); canvas[ya:yb, xa:xb, 3] = (oa[..., 0] * 255).astype(np.uint8)


# ------------------------------------------------------------------ end card

@overlay('kc_end')
def kc_end(img, t, ctx, oc):
    D = ctx['edl']['duration']
    split_s, card_s, dim_s = oc.get('split_s', 1.26), oc.get('card_s', 1.94), oc.get('dim_s', 4.03)
    total = min(split_s + card_s + dim_s, 0.4 * D)
    k = total / (split_s + card_s + dim_s); split_s, card_s, dim_s = split_s * k, card_s * k, dim_s * k
    t0 = D - total
    if t < t0: return img
    h, w = img.shape[:2]; tl = t - t0
    bg = LIGHT
    in_split = tl < split_s
    img = ctx['store'].get('kc_raw', img)
    out = np.empty_like(img); fill(out, bg)
    if in_split:
        y0 = int(0.47 * h); edge = max(2, int(0.03 * h)); out[y0:] = img[y0:]
        a = np.clip(np.arange(edge) / edge, 0, 1)[:, None, None]
        out[y0:y0 + edge] = (np.array(bg[::-1], np.float32) * (1 - a) + img[y0:y0 + edge].astype(np.float32) * a).astype(np.uint8)
    img = out
    kw = oc.get('keyword', 'MONTAGE'); pre = oc.get('pre', 'comment')
    over(img, text_rgba(pre, 'playfair italic', int(w * 0.058), INK, 400, 0, None), w / 2, 0.155 * h, 1.0, 1.0, centre=True)
    sz = int(w * 0.17)
    while text_width(kw, 'playfair italic', sz, 800, 0) > w * 0.9: sz = int(sz * 0.95)
    over(img, text_rgba(kw, 'playfair italic', sz, ACCENT, 800, -sz * 0.01, None), w / 2, 0.25 * h, 1.0, 1.0, centre=True)
    if tl >= split_s:
        lines = oc.get('lines', ["and I'll send you the link", 'and a setup guide'])
        over(img, text_rgba(lines[0], 'playfair italic', int(w * 0.046), INK, 400, 0, None), w / 2, 0.35 * h, 1.0, 1.0, centre=True)
        if tl >= split_s + card_s * 0.5 and len(lines) > 1:
            over(img, text_rgba(lines[1], SANS, int(w * 0.034), INK, 600, 0, None), w / 2, 0.395 * h, 1.0, 1.0, centre=True)
        cw, ch = int(w * 0.58), int(h * 0.3)
        rise = 1 - spring(tl - split_s, 0.85, 14)
        cs = _cached(('endcard', cw, ch), lambda: _end_card(cw, ch))
        over(img, cs, w / 2 - cs.shape[1] / 2, 0.44 * h + rise * 0.08 * h)
    if tl >= split_s + card_s:
        img = (img.astype(np.float32) * (1 - oc.get('dim', 0.75))).astype(np.uint8)
    return img


def _end_card(cw, ch):
    c = rrect(cw, ch, cw * 0.04, (247, 244, 236)); fs = max(8, int(cw * 0.05))
    for i, (tx, wg) in enumerate([('Steps', 700), ('1  Open the project folder', 500), ('Open it on your computer in a folder', 400), ('2  Paste the prompt', 500), ('The agent downloads the tools and sets up', 400)]):
        t_ = text_rgba(tx, SANS, fs, (40, 40, 44), wg, 0, None); y = int(ch * 0.07 + i * fs * 1.9)
        if y + t_.shape[0] < ch: c[y:y + t_.shape[0], int(cw * 0.07):int(cw * 0.07) + min(t_.shape[1], cw - int(cw * 0.14))] = _blend(c[y:y + t_.shape[0], int(cw * 0.07):int(cw * 0.07) + min(t_.shape[1], cw - int(cw * 0.14))], t_[:, :cw - int(cw * 0.14)])
    return shadowed(c, cw * 0.02, cw * 0.02, 0.25)[0]

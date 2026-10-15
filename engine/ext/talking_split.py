"""Extensions for the talking-head-split style (a vertical talking head with screen captures and product cards inset in the
upper half, tight serif caption chunks in the lower half, a gold-highlighted title hook).

Registers
  caption  serif_chunk   two-line phrase chunks of a heavy high-contrast serif, white with a soft shadow, hard swaps on the first word
  overlay  th_title      the title hook, lines of runs with gold highlight runs, on screen until a time
  overlay  th_cards      16:9 inset cards in the upper third that hard-cut every 0.3 to 3 s. Real captures from a folder (cards_dir),
                         or generated stand-ins (chat UI, price card, title card, poster, code card, score chart)
  overlay  th_outro      dims the last seconds (the platform end card in the reference)
  fx       th_zoom       static punch-in on the head, alternating wide and close shots

Self-contained, nothing here edits the core.
"""
import os, glob
import numpy as np
import cv2
from PIL import Image, ImageDraw
from fx import fx, zoom_img
from captions import caption
from render import overlay
from ext.typeset import vfont, text_rgba, baseline_text, text_width, over, rrect


# ------------------------------------------------------------------ captions

def _wrap(words, font, size, wght, track, maxw):
    lines, cur = [], []
    for w in words:
        t = ' '.join(cur + [w])
        if cur and text_width(t, font, size, wght, track) > maxw: lines.append(cur); cur = [w]
        else: cur.append(w)
    if cur: lines.append(cur)
    return lines


_chunk_cache = {}


def _chunks(words, cfg, W):
    """Phrase -> chunks of at most max_lines lines and max_words words. A chunk is [(word dicts)]."""
    key = (id(words), len(words), W)
    if key in _chunk_cache: return _chunk_cache[key]
    size = cfg.get('size_frac', 0.088) * W; track = cfg.get('tracking', -0.035) * size
    maxw = cfg.get('max_width', 0.82) * W; font = cfg.get('font', 'playfair'); wg = cfg.get('wght', 600)
    out = []
    by = {}
    for w in words: by.setdefault(w['phrase'], []).append(w)
    for ph in sorted(by):
        ws = by[ph]; cur = []
        for w in ws:
            trial = cur + [w]
            lines = _wrap([x['text'] for x in trial], font, size, wg, track, maxw)
            if cur and (len(lines) > cfg.get('max_lines', 2) or len(trial) > cfg.get('max_words', 8)):
                out.append((ph, cur)); cur = [w]
            else: cur = trial
        if cur: out.append((ph, cur))
    _chunk_cache.clear(); _chunk_cache[key] = out
    return out


@caption('serif_chunk')
def serif_chunk(t, words, cfg, W, H, ctx):
    ch = _chunks(words, cfg, W)
    cur = None
    for i, (ph, ws) in enumerate(ch):
        if ws[0]['t0'] <= t + 1e-6: cur = i
        else: break
    if cur is None: return None
    ph, ws = ch[cur]
    nxt_same = cur + 1 < len(ch)
    t_end = ch[cur + 1][1][0]['t0'] if nxt_same else ws[-1]['t1'] + 0.6
    if cur + 1 < len(ch) and ch[cur + 1][1][0]['t0'] - ws[-1]['t1'] > cfg.get('hold_max', 0.8): t_end = ws[-1]['t1'] + cfg.get('hold_max', 0.8)
    if t > t_end: return None
    size = cfg.get('size_frac', 0.088) * W; track = cfg.get('tracking', -0.035) * size
    font = cfg.get('font', 'playfair'); wg = cfg.get('wght', 600)
    col = tuple(cfg.get('color', [255, 255, 255])); hi = tuple(cfg.get('emph_color', col))
    shadow = tuple(cfg.get('shadow', [0, 3, 6, 0.6]))
    lines = _wrap([w['text'] for w in ws], font, size, wg, track, cfg.get('max_width', 0.82) * W)
    pitch = cfg.get('line_pitch', 0.089) * W
    y_top = cfg.get('y', 0.733) * H
    canvas = np.zeros((H, W, 4), np.uint8)
    k = 0
    for li, ln in enumerate(lines):
        # per-word runs so highlighted words can take the accent colour
        runs = []
        for wtxt in ln:
            w = ws[k]; k += 1
            runs.append((wtxt, hi if w.get('emph') else col))
        total = sum(text_width(r[0] + ' ', font, size, wg, track) for r in runs) - text_width(' ', font, size, wg, track)
        x = (cfg.get('x', 0.5) * W) - total / 2
        for wtxt, c in runs:
            im, pad = baseline_text(wtxt, font, size, c, wg, track, shadow)
            yy = y_top + li * pitch - pad - size * 0.18
            _paste(canvas, im, x - pad, yy)
            x += text_width(wtxt + ' ', font, size, wg, track)
    return canvas


def _paste(canvas, rgba, x, y):
    h, w = rgba.shape[:2]; x0, y0 = int(round(x)), int(round(y))
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(canvas.shape[1], x0 + w), min(canvas.shape[0], y0 + h)
    if xb <= xa or yb <= ya: return
    s = rgba[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32); d = canvas[ya:yb, xa:xb].astype(np.float32)
    sa = s[..., 3:4] / 255; da = d[..., 3:4] / 255; oa = sa + da * (1 - sa)
    oc = (s[..., :3] * sa + d[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6)
    canvas[ya:yb, xa:xb, :3] = oc.astype(np.uint8); canvas[ya:yb, xa:xb, 3] = (oa[..., 0] * 255).astype(np.uint8)


# ------------------------------------------------------------------ title hook

@overlay('th_title')
def th_title(img, t, ctx, oc):
    until = oc.get('seconds', 4.43)
    if t >= until: return img
    h, w = img.shape[:2]
    size = oc.get('size_frac', 0.101) * w; track = oc.get('tracking', -0.03) * size
    font = oc.get('font', 'playfair'); wg = oc.get('wght', 700)
    base = tuple(oc.get('color', [255, 255, 255])); hi = tuple(oc.get('hi_color', [240, 200, 21]))
    shadow = tuple(oc.get('shadow', [0, 3, 8, 0.55]))
    x0 = oc.get('x', 0.083) * w; y = oc.get('y', 0.258) * h; pitch = oc.get('pitch', 0.114) * w
    for li, line in enumerate(oc.get('lines', [])):
        x = x0
        for run in line:
            txt = run['t']; c = hi if run.get('hi') else base
            im, pad = baseline_text(txt, font, size, c, wg, track, shadow)
            over(img, im, x - pad, y + li * pitch - pad - size * 0.15)
            x += text_width(txt, font, size, wg, track)
    return img


# ------------------------------------------------------------------ inset cards

SANS = 'inter tight'


def _draw_card(kind, w, h, rng, texts):
    """Generated stand-in for a screen capture, 16:9. Returns an RGB array."""
    im = Image.new('RGB', (w, h), (255, 255, 255)); d = ImageDraw.Draw(im)
    s = h / 330.0
    F = lambda sz, wg=500, name=SANS: vfont(name, int(sz * s), wg)
    pick = lambda: texts[int(rng.integers(0, len(texts)))] if texts else 'render'
    if kind == 'ui':
        d.rectangle([0, 0, w, h], fill=(250, 249, 246))
        bw = int(w * 0.5); d.rounded_rectangle([w - bw - 18 * s, 22 * s, w - 18 * s, 66 * s], int(8 * s), fill=(237, 233, 226))
        d.text((w - bw - 6 * s, 30 * s), 'Build a headless render loop. Write code that', font=F(11), fill=(50, 48, 44))
        d.text((w - bw - 6 * s, 46 * s), 'paints every frame, capture it, stitch to MP4.', font=F(11), fill=(50, 48, 44))
        d.text((24 * s, 88 * s), '*', font=F(18, 700), fill=(217, 119, 87))
        for i in range(2): d.text((44 * s, (90 + i * 16) * s), "I'll build it as three pieces: a page that paints" if i == 0 else 'any frame, a loop that captures each one.', font=vfont('playfair', int(11 * s), 500), fill=(60, 56, 50))
        d.rounded_rectangle([40 * s, 130 * s, w * 0.62, 205 * s], int(8 * s), fill=(255, 255, 255), outline=(232, 228, 220))
        for i, tx in enumerate(['Install Node.js 22', 'Install ffmpeg 6.1', 'Install playwright']):
            d.ellipse([54 * s, (146 + i * 17) * s, 62 * s, (154 + i * 17) * s], fill=(70, 150, 90)); d.text((70 * s, (142 + i * 17) * s), tx, font=vfont('mono', int(9 * s)), fill=(70, 66, 60))
        d.rounded_rectangle([30 * s, h - 78 * s, w - 30 * s, h - 20 * s], int(10 * s), fill=(255, 255, 255), outline=(228, 224, 216))
        d.text((44 * s, h - 66 * s), 'Reply to Claude...', font=F(11), fill=(150, 146, 140))
        d.rounded_rectangle([w - 64 * s, h - 54 * s, w - 42 * s, h - 32 * s], int(5 * s), fill=(217, 119, 87))
    elif kind == 'stat':
        d.rectangle([0, 0, w, h], fill=(252, 253, 252))
        d.text((34 * s, 36 * s), 'Monthly', font=F(18, 500), fill=(120, 126, 120))
        d.text((34 * s, 68 * s), '$%d' % int(rng.choice([2100, 2400, 3000, 1800])), font=F(76, 700), fill=(46, 140, 78))
        d.text((34 * s + 240 * s, 112 * s), '/month', font=F(22, 500), fill=(60, 66, 60))
        d.text((34 * s, 190 * s), 'Recurring monthly billing', font=F(14, 400), fill=(160, 166, 160))
        d.rounded_rectangle([w - 130 * s, 40 * s, w + 20 * s, 84 * s], int(22 * s), fill=(150, 200, 150)); d.text((w - 104 * s, 52 * s), 'Subscribe', font=F(15, 600), fill=(255, 255, 255))
    elif kind == 'title':
        d.rectangle([0, 0, w, h], fill=(8, 8, 10))
        wd = pick().upper()
        f = F(86, 800); tw = text_width(wd, SANS, int(86 * s), 800, 2)
        if tw > w * 0.86: f = F(86 * w * 0.86 / tw, 800)
        d.text((w * 0.5, h * 0.46), wd, font=f, fill=(246, 246, 244), anchor='mm')
        d.text((w * 0.5, h * 0.7), 'MOTION DESIGN  /  SHOWREEL 2026', font=vfont('mono', int(10 * s)), fill=(150, 150, 150), anchor='mm')
        d.rectangle([w * 0.38, h * 0.62, w * 0.62, h * 0.625], fill=(255, 90, 26))
    elif kind == 'poster':
        d.rectangle([0, 0, w, h], fill=(255, 92, 28))
        d.pieslice([-w * 0.1, h * 0.35, w * 0.3, h * 1.3], 180, 360, fill=(246, 240, 228))
        d.rectangle([w * 0.38, h * 0.45, w * 0.58, h * 1.0], fill=(14, 14, 14))
        d.ellipse([w * 0.66, h * 0.05, w * 0.84, h * 0.4], fill=(14, 14, 14)); d.rectangle([w * 0.66, h * 0.55, w * 0.86, h], fill=(246, 240, 228))
    elif kind == 'code':
        d.rectangle([0, 0, w, h], fill=(253, 252, 250))
        d.text((24 * s, 22 * s), 'Chrome  frame_0509.png', font=vfont('mono', int(10 * s)), fill=(110, 106, 100))
        for i in range(34): d.rectangle([(26 + i * 15) * s, 58 * s, (31 + i * 15) * s, 100 * s], fill=(217, 119, 87))
        for i, tx in enumerate(['for (let i = 0; i < 510; i++) {', '  await page.evaluate((t) => renderFrame(t), i / 30);', '  await page.screenshot({path: `frame_${i}.png`});', '}']):
            d.text((26 * s, (130 + i * 20) * s), tx, font=vfont('mono', int(11 * s)), fill=(60, 56, 50))
        d.rounded_rectangle([18 * s, 118 * s, w - 18 * s, 214 * s], int(8 * s), outline=(176, 40, 40), width=max(1, int(2 * s)))
        d.text((24 * s, h - 50 * s), 'ffmpeg -framerate 30 -i frame_%04d.png -c:v libx264 out.mp4', font=vfont('mono', int(10 * s)), fill=(110, 106, 100))
    else:                                                       # chart
        d.rectangle([0, 0, w, h], fill=(252, 252, 250))
        d.text((24 * s, 20 * s), 'Self-critique loop', font=F(12, 600), fill=(90, 86, 80))
        n = 14
        for i in range(n):
            bx = (30 + i * (w / s - 60) / n) * s; bh = rng.uniform(0.25, 0.95) * 190 * s
            c = (70, 150, 90) if bh / s > 110 else (224, 112, 80)
            d.rectangle([bx, h - 36 * s - bh, bx + 18 * s, h - 36 * s], fill=c)
            d.text((bx, h - 30 * s), '%d/10' % int(round(bh / s / 19)), font=vfont('mono', int(8 * s)), fill=(130, 126, 120))
    return np.array(im)


_images = {}


def _load_dir(path):
    if path not in _images:
        fs = sorted(sum([glob.glob(os.path.join(path, e)) for e in ('*.png', '*.jpg', '*.jpeg', '*.webp')], []))
        _images[path] = fs
    return _images[path]


_sched = {}


def _schedule(oc, D, seed):
    """Card slots: [(t0, t1, kind_index, seed)]. start_s is when the first card appears, end_before_end_s how long the edit runs
    after the last card, phases give the card length range [min, max] seconds up to burst_s after the start and then for the rest."""
    key = (id(oc), D, seed)
    if key in _sched: return _sched[key]
    rng = np.random.default_rng(seed + 7)
    slots = []; tstart = oc.get('start_s', 4.43); tcur = tstart
    end = D - oc.get('end_before_end_s', 9.7)
    burst = tstart + oc.get('burst_s', 4.9)
    kinds = oc.get('kinds', ['ui', 'stat', 'title', 'poster', 'code', 'chart'])
    k = 0
    while tcur < end - 0.15:
        ln = float(rng.uniform(*(oc.get('burst_len', [0.3, 0.7]) if tcur < burst else oc.get('len', [1.2, 3.2]))))
        t1 = min(end, tcur + ln)
        slots.append((tcur, t1, k % len(kinds), int(rng.integers(0, 2 ** 31)))); k += 1
        tcur = t1
    _sched.clear(); _sched[key] = slots
    return slots


_card_cache = {}


@overlay('th_cards')
def th_cards(img, t, ctx, oc):
    D = ctx['edl']['duration']
    slots = _schedule(oc, D, ctx['edl'].get('seed', 1))
    cur = next((s for s in slots if s[0] <= t < s[1]), None)
    if cur is None: return img
    h, w = img.shape[:2]
    cw = int(oc.get('width', 0.82) * w) // 2 * 2; ch = int(cw * 9 / 16)
    x0 = int(oc.get('x', 0.09) * w); y0 = int(oc.get('y', 0.2273) * h)
    key = (cur[3], cw, ch)
    if key not in _card_cache:
        rng = np.random.default_rng(cur[3])
        files = _load_dir(oc['cards_dir']) if oc.get('cards_dir') else []
        if not files and oc.get('require_real_cards'):
            # An automatic choice (gate.talking_split_allowed) must not fall back to invented
            # figures on screen (review-2 finding 13); a hand-run edit without the flag still can.
            raise RuntimeError("th_cards: no real cards in cards_dir and require_real_cards is set, "
                                "refusing to draw invented figures")
        if files:
            src = cv2.imread(files[cur[2] % len(files)])
            f = max(cw / src.shape[1], ch / src.shape[0]); src = cv2.resize(src, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
            oy = (src.shape[0] - ch) // 2; ox = (src.shape[1] - cw) // 2
            card = src[oy:oy + ch, ox:ox + cw]
        else:
            texts = oc.get('texts') or [x['text'] for x in ctx.get('words', [])][:60] or ['render']
            texts = [x for x in texts if len(x) > 3] or texts
            card = _draw_card(oc.get('kinds', ['ui', 'stat', 'title', 'poster', 'code', 'chart'])[cur[2]], cw, ch, rng, texts)[..., ::-1]
        if len(_card_cache) > 40: _card_cache.clear()
        _card_cache[key] = np.ascontiguousarray(card)
    card = _card_cache[key]
    u = (t - cur[0]) / max(1e-6, cur[1] - cur[0])
    sc = 1.0 + oc.get('push', 0.03) * u                       # a slow push so the capture is never static
    if sc > 1.0005:
        M = cv2.getRotationMatrix2D((cw / 2, ch / 2), 0, sc); card = cv2.warpAffine(card, M, (cw, ch), flags=cv2.INTER_LINEAR)
    img[y0:y0 + ch, x0:x0 + cw] = card
    return img


@overlay('th_outro')
def th_outro(img, t, ctx, oc):
    D = ctx['edl']['duration']; t0 = D - oc.get('seconds', 4.0)
    if t < t0: return img
    return (img.astype(np.float32) * (1 - oc.get('dim', 0.78))).astype(np.uint8)


# ------------------------------------------------------------------ head zoom

@fx('th_zoom')
def th_zoom(img, k, p, ctx):
    """Static punch-in around a point, the close shot of the alternating wide and close pair."""
    return zoom_img(img, p.get('scale', 1.7), p.get('cx', 0.5), p.get('cy', 0.62))

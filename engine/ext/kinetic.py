"""Kinetic type: heavy display face, one to three words per beat, a scaled key word, tight leading, placed with intent.

Caption kind `kinetic` (use in style.json captions). Config keys, all optional:
  font, key_font          display faces ("Anton", "Bebas Neue", "Archivo Black", "Space Grotesk", "Inter Tight")
  size_frac               plain word height as a fraction of the frame width (portrait) or height
  key_scale               size multiplier for the key (emphasis) word, deliberate scale contrast
  color, key_color        RGB
  chunk_sizes             words per chunk, cycled, e.g. [2, 1, 3]. The key word always stands alone.
  layout                  stack (one word per line, tight leading) | line (words on one line, wrapped)
  align, x, y, anchor     left|center|right, block x and y as fractions, anchor top|bottom|middle
  plate                   none | band (solid band behind each line) | diff (difference blend with the picture)
  plate_color, plate_text_color, plate_pad
  leading                 line gap as a fraction of size (negative tightens)
  tracking                letter spacing as a fraction of size
  hold_beats              how long the last chunk of a phrase stays after its last word
  rise                    seconds of the rise-in animation
Words carry `depth` ('behind' | 'front') from render.assign_depth. With a subject matte the render draws the behind pass
under the subject and the front pass over it. ctx['depth_pass'] selects which words are drawn.
"""
import numpy as np
import cv2
from captions import caption, text_rgba, blit, _rgb, _ease


def _chunks(words, cfg):
    sizes = cfg.get('chunk_sizes', [2, 2, 3])
    out = []; si = 0
    by_ph = {}
    for w in words: by_ph.setdefault(w['phrase'], []).append(w)
    for ph in sorted(by_ph):
        ws = by_ph[ph]; cur = []
        for w in ws:
            if w.get('emph'):
                if cur: out.append((ph, cur)); cur = []
                out.append((ph, [w])); continue
            cur.append(w)
            if len(cur) >= sizes[si % len(sizes)]:
                out.append((ph, cur)); cur = []; si += 1
        if cur: out.append((ph, cur))
    return out


_cache = {}


def _chunk_list(words, cfg):
    key = (id(words), len(words))
    if key not in _cache:
        _cache.clear(); _cache[key] = _chunks(words, cfg)
    return _cache[key]


@caption('kinetic')
def kinetic(t, words, cfg, W, H, ctx):
    ch = _chunk_list(words, cfg)
    cur = None
    for i, (ph, ws) in enumerate(ch):
        if ws[0]['t0'] <= t + 1e-6: cur = i
        else: break
    if cur is None: return None
    ph, ws = ch[cur]
    P = ctx['edl']['music']['beat_period'] if ctx.get('edl') else 0.5
    nxt_same = cur + 1 < len(ch) and ch[cur + 1][0] == ph
    t0 = ws[0]['t0']
    t_end = ch[cur + 1][1][0]['t0'] if nxt_same else max(w['t1'] for w in ws) + cfg.get('hold_beats', 1.0) * P
    if cfg.get('hold_last') and cur == len(ch) - 1 and ctx.get('edl'): t_end = ctx['edl']['duration'] + 1
    if cfg.get('hold_until_next') and cur + 1 < len(ch) and not nxt_same:      # the last word stays up until the next phrase begins
        gap_ = ch[cur + 1][1][0]['t0']
        if gap_ - max(w['t1'] for w in ws) <= cfg.get('hold_max_beats', 2.0) * P: t_end = gap_
    if t > t_end: return None
    key = any(w.get('emph') for w in ws)
    depth = ws[0].get('depth', 'front') if key else 'front'
    if cfg.get('plain_depth_alt') and not key and cur % 4 == 3: depth = 'behind'
    dp = ctx.get('depth_pass')
    if dp and dp != depth: return None
    portrait = H > W
    base = (cfg.get('size_frac_portrait', cfg.get('size_frac', 0.11)) * W) if portrait else cfg.get('size_frac', 0.11) * H
    track = cfg.get('tracking', 0.01)
    fname = cfg.get('font', 'Anton'); kf = cfg.get('key_font', fname)
    col = _rgb(cfg.get('color', [246, 243, 234])); kcol = _rgb(cfg.get('key_color', [230, 200, 138]))
    plate = cfg.get('plate', 'none')
    if plate == 'band': col = _rgb(cfg.get('plate_text_color', [27, 42, 10]))
    if plate == 'none' and cfg.get('auto_contrast', True) and ctx.get('img') is not None:     # pale picture under the text: ink instead of paper
        im_ = ctx['img']; ya = int(max(0, (cfg.get('y', 0.82) - 0.3) * H)); yb = int(min(H, cfg.get('y', 0.82) * H + 0.05 * H))
        lum = float((im_[ya:yb, :, ::-1].astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)).mean())
        if lum > 150: col = _rgb(cfg.get('ink_color', [27, 42, 10])); kcol = _rgb(cfg.get('ink_key_color', [138, 46, 27]))
    imgs = []
    for w in ws:
        k = w.get('emph')
        sz = int(base * (cfg.get('key_scale', 1.7) if k else 1.0))
        txt = w['text'].upper() if cfg.get('upper', True) else w['text']
        c = (_rgb(cfg.get('plate_key_color', kcol)) if plate == 'band' else kcol) if k else col
        imgs.append((text_rgba(txt, kf if k else fname, sz, c, 0, (0, 0, 0), int(track * sz), ()), k, sz))
    gap = cfg.get('leading', 0.12) * base
    maxw = cfg.get('max_width', 0.86) * W
    lines = []
    if cfg.get('layout', 'stack') == 'stack':
        lines = [[im] for im in imgs]
    else:
        cl = []; cw = 0
        for im in imgs:
            if cl and cw + im[0].shape[1] + base * 0.28 > maxw: lines.append(cl); cl = []; cw = 0
            cl.append(im); cw += im[0].shape[1] + base * 0.28
        if cl: lines.append(cl)
    # fit: shrink the whole chunk uniformly if a line overruns
    def lw(l): return sum(i[0].shape[1] for i in l) + base * 0.28 * (len(l) - 1)
    sc = min(1.0, maxw / max(lw(l) for l in lines))
    lh = [max(i[0].shape[0] for i in l) * sc for l in lines]
    total = sum(lh) + gap * sc * (len(lines) - 1)
    yv = cfg.get('y', 0.82)
    if cfg.get('y_alt') is not None and any(e['fx'] == 'mask_flash' and e.get('params', {}).get('tag') == 'sticker' and e['t0'] <= t < e['t1'] for e in (ctx.get('edl') or {}).get('events', [])): yv = cfg['y_alt']
    x_anchor = cfg.get('x', 0.07) * W; y_anchor = yv * H
    anchor = cfg.get('anchor', 'bottom')
    y_top = y_anchor - total if anchor == 'bottom' else (y_anchor - total / 2 if anchor == 'middle' else y_anchor)
    still = cfg.get('anim', 'rise') == 'none'          # hard swap, no rise, fade or slam
    u = 9.0 if still else (t - t0) / max(1e-3, cfg.get('rise', 0.12))
    e = _ease('out_cubic', min(1.0, max(0.0, u)))
    a = min(1.0, max(0.0, u * 1.6))
    dy = (1 - e) * 0.35 * base
    fade = 1.0
    if t > t_end - 0.1 and not nxt_same and not still: fade = max(0.0, (t_end - t) / 0.1)
    canvas = np.zeros((H, W, 4), np.uint8)
    y = y_top
    align = cfg.get('align', 'left')
    pad = cfg.get('plate_pad', 0.16) * base
    for li, (l, h) in enumerate(zip(lines, lh)):
        w_line = lw(l) * sc
        if align == 'left': x = x_anchor
        elif align == 'right': x = x_anchor - w_line
        else: x = x_anchor - w_line / 2
        x += cfg.get('indent', 0.0) * W * li * (1 if align != 'right' else -1)
        x = min(max(x, W * 0.04), W * 0.96 - w_line)
        if plate == 'band' and depth == 'front':
            band = np.zeros((int(h + pad * 2), int(w_line + pad * 2), 4), np.uint8)
            band[..., :3] = _rgb(cfg.get('plate_color', [246, 243, 234])); band[..., 3] = 255
            blit(canvas, band, x - pad, y - pad + dy, 1, a * fade, anchor='lt')
        xx = x
        for im, k, sz in l:
            r = im
            if sc < 1: r = cv2.resize(im, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
            slam = 1.0
            if k: slam = 1.0 + 0.12 * (1 - _ease('out_cubic', min(1.0, u)))
            hh = r.shape[0]
            yy = y + (h - hh) / 2 + dy
            blit(canvas, r, xx + r.shape[1] / 2, yy + hh / 2, slam, a * fade, anchor='c')
            xx += r.shape[1] + base * 0.28 * sc
        y += h + gap * sc
    if plate == 'diff' and ctx.get('img') is not None:
        img = ctx['img'][..., ::-1].astype(np.float32)
        diff = 255.0 - img
        m = canvas[..., 3] > 0
        if m.any():
            ys, xs = np.where(m)
            reg = img[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            dark = float((reg @ np.array([0.299, 0.587, 0.114], np.float32)).mean()) < 128      # one target per word, not per pixel
            tgt = np.array([255.0, 255.0, 255.0] if dark else [14.0, 14.0, 14.0], np.float32)
            g = cfg.get('guard', 0.7)
            col = diff * (1 - g) + tgt * g
            al = canvas[..., 3].astype(np.float32) / 255.0
            halo = cv2.GaussianBlur(al, (0, 0), max(2.0, 0.05 * base)) * cfg.get('halo', 0.5) * (1 - al)
            out = np.zeros_like(canvas)
            hc = 0.0 if dark else 255.0                                                  # local contrast under the word, no drop shadow
            out[..., :3] = np.where(al[..., None] > 0.02, col, hc).astype(np.uint8)
            out[..., 3] = (np.clip(al + halo * (al < 0.02), 0, 1) * 255).astype(np.uint8)
            canvas = out
    return canvas

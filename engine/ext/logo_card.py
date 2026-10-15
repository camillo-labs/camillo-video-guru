"""Generic end card: a logo (PNG with alpha) on a flat colour that fades in over the last beats of the edit.

style.json: "overlays": [{"kind": "logo_card", "image": "/abs/path/logo.png", "bg": [8, 73, 8], "last_beats": 4,
                          "fade_beats": 0.75, "logo_width": 0.5, "y": 0.45, "lines": [{"text": "...", "size_frac": 0.03, "y": 0.8}]}]
"""
import numpy as np
import cv2
import captions as capm
import fx as fxm
from render import overlay

_cache = {}


@overlay('logo_card')
def logo_card(img, t, ctx, oc):
    edl = ctx['edl']; P = edl['music']['beat_period']; D = edl['duration']
    t0 = D - oc.get('last_beats', 4) * P
    if t < t0: return img
    u = (t - t0) / max(1e-6, oc.get('fade_beats', 0.75) * P)
    a = fxm.ease('out_cubic', u)
    h, w = img.shape[:2]
    bg = np.empty_like(img); bg[:] = np.array(oc.get('bg', [0, 0, 0]), np.uint8)[::-1]
    out = (img.astype(np.float32) * (1 - a) + bg.astype(np.float32) * a).astype(np.uint8)
    key = oc['image']
    if key not in _cache:
        _cache[key] = cv2.imread(key, cv2.IMREAD_UNCHANGED)
    lg = _cache[key]
    if lg is not None:
        if lg.ndim == 3 and lg.shape[2] == 3: lg = cv2.cvtColor(lg, cv2.COLOR_BGR2BGRA)
        sc = oc.get('logo_width', 0.5) * w / lg.shape[1]
        rgba = cv2.cvtColor(cv2.resize(lg, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA), cv2.COLOR_BGRA2RGBA)
        canvas = np.zeros((h, w, 4), np.uint8)
        capm.blit(canvas, rgba, w / 2, oc.get('y', 0.45) * h, 1.0, 1.0)
        for ln in oc.get('lines', []):
            im = capm.text_rgba(ln['text'], ln.get('font', 'Avenir Next Bold'), int(ln.get('size_frac', 0.03) * min(w, h)),
                                tuple(ln.get('color', [246, 243, 234])), 0, (0, 0, 0), ln.get('tracking', 0), ())
            capm.blit(canvas, im, w / 2, ln.get('y', 0.8) * h, 1.0, 1.0)
        al = canvas[..., 3:4].astype(np.float32) / 255.0 * a
        out = (out.astype(np.float32) * (1 - al) + canvas[..., :3][..., ::-1].astype(np.float32) * al).astype(np.uint8)
    return out

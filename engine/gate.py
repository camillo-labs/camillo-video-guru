"""Post-render gates: safe-area captions, flash frequency (WCAG 2.3.1), dead frames, and the
talking-split invented-figures guard. Reports what currently breaches a rendered edit; does not
fix it (selection-plan-2026-10-14.md section 4, review-1 finding 14, review-2 findings 13/15,
review-3 finding 11).
"""
import json
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import render
import captions as capm
import check
import sfx_library

# Union safe box across TikTok, Instagram Reels and YouTube Shorts, as fractions of the frame
# (selection-plan-2026-10-14.md:187): x 11-82%, y 15-65%. Anything outside risks a platform's own
# UI (handle, caption bar, progress ring) covering it.
SAFE_X = (0.11, 0.82)
SAFE_Y = (0.15, 0.65)

# Documentation only: each caption kind positions its block differently around its own `y`, so the
# gate measures the rendered alpha canvas, never this field (review-2 finding 15).
CAPTION_Y_SEMANTIC = {
    'serif_chunk': 'top-of-block (ext/talking_split.py:80)',
    'subtitle': 'first line, wrapped lines grow downward (captions.py:249)',
    'hud_row': 'centre-of-block, also moves the ellipse mask (ext/hud_lyric.py:141,164)',
    'kinetic': 'anchored per style, usually bottom (ext/kinetic.py)',
    'kc_word': 'anchored per style (ext/kinetic_card.py)',
    'word_pop': 'centre (captions.py)',
    'staircase': 'top-of-block, stepping down (captions.py)',
    'lyric_diff': 'per style (ext/lyric_word_beat.py)',
}

_WCAG_FLASH_LUMA_DELTA = 0.10     # WCAG 2.3.1: a pair of opposite luminance changes of >=10%
_WCAG_MAX_FLASHES_PER_S = 3       # ...more than 3 times in any one-second window, no small-area exemption


def _resolve(path, edl_path):
    p = Path(path)
    if p.exists():
        return p
    alt = Path(edl_path).resolve().parent / p.name
    if alt.exists():
        return alt
    raise FileNotFoundError(f'cannot find {path} relative to cwd or to {edl_path}')


def _alpha_bbox(canvas):
    """(y0, y1, x0, x1) as fractions of (H, W) where alpha > 0, or None if nothing is drawn."""
    a = canvas[..., 3]
    ys, xs = np.where(a > 0)
    if len(ys) == 0:
        return None
    H, W = canvas.shape[:2]
    return ys.min() / H, ys.max() / H, xs.min() / W, xs.max() / W


def safe_area_check(video, edl_path, sample_hz=4):
    """Render the real caption alpha canvas at sampled times (not the raw style `y` field, see
    review-2 finding 15) and check its bounding box against the union safe box."""
    edl = json.load(open(edl_path))
    words = edl.get('words') or []
    style_path = _resolve(edl['style_path'], edl_path) if edl.get('style_path') else None
    style = json.load(open(style_path)) if style_path else {}
    ccfg = style.get('captions') or {}
    if not ccfg or not words:
        return {'kind': None, 'frames_checked': 0, 'breaches': [], 'breach_rate': 0.0, 'note': 'no captions in this edit'}

    W, H, fps, duration = check.probe(video)
    band = (style.get('layout') or {}).get('band')
    aw, ah = map(int, edl['aspect'].split(':'))
    cW, cH = (W, int(round(W * 9 / 16 / 2) * 2)) if band and ah > aw else (W, H)

    render.load_ext()
    cap = capm.Renderer(ccfg, cW, cH, words)

    # A standalone caption-only context: no picture, no subject matte. Every caption kind this
    # gate has been run against (kinetic, hud_row) only reads ctx['edl']/['style'] for timing and
    # falls back cleanly when ctx['mask']/['img'] are None (kinetic.py:84, hud_lyric.py:160-161),
    # so this is enough to probe the alpha bounding box without re-running the full renderer.
    store = {}
    times = sorted({round(w['t0'], 3) for w in words} | {round(t, 3) for t in np.arange(0, duration, 1.0 / sample_hz)})
    breaches, checked, errors = [], 0, []
    for t in times:
        frame = int(round(t * fps))
        ctx = {'edl': edl, 'style': style, 'words': words, 'mask': None, 'img': None,
               'store': store, 'frame': frame, 'fps': fps, 'depth_pass': None,
               'rng': np.random.default_rng(frame)}
        try:
            canvas = cap.render(t, ctx)
        except Exception as ex:
            errors.append({'t': t, 'error': str(ex)})
            continue
        if canvas is None:
            continue
        bbox = _alpha_bbox(canvas)
        if bbox is None:
            continue
        checked += 1
        y0, y1, x0, x1 = bbox
        if y1 > SAFE_Y[1] or y0 < SAFE_Y[0] or x1 > SAFE_X[1] or x0 < SAFE_X[0]:
            breaches.append({'t': t, 'y0': round(y0, 3), 'y1': round(y1, 3), 'x0': round(x0, 3), 'x1': round(x1, 3)})

    return {
        'kind': ccfg.get('kind'),
        'caption_y_semantic': CAPTION_Y_SEMANTIC.get(ccfg.get('kind'), 'undocumented caption kind'),
        'safe_box': {'x': SAFE_X, 'y': SAFE_Y},
        'frames_checked': checked,
        'breaches': breaches,
        'breach_rate': round(len(breaches) / checked, 3) if checked else 0.0,
        'render_errors': errors,
    }


def flash_frequency_check(video, luma_delta=_WCAG_FLASH_LUMA_DELTA):
    """Measure frame luminance on the rendered file (not flash events in the EDL, per review-3
    finding 11) and report the busiest one-second window against WCAG 2.3.1's limit of 3."""
    W, H, fps, duration = check.probe(video)
    sw, sh = 64, 36
    a = check.extract_gray_frames(video, fps=None, w=sw, h=sh) / 255.0
    lum = a.mean((1, 2))
    d = np.diff(lum)

    # A flash is a pair of opposite luminance changes that each clear the WCAG threshold: a sharp
    # rise immediately followed by a sharp fall, or the reverse. Counted at the turning frame.
    is_flash = np.zeros(len(lum), dtype=bool)
    for i in range(1, len(d)):
        if d[i - 1] * d[i] < 0 and abs(d[i - 1]) >= luma_delta and abs(d[i]) >= luma_delta:
            is_flash[i] = True

    win = max(1, int(round(fps)))
    if len(is_flash) >= win:
        counts = [int(is_flash[i:i + win].sum()) for i in range(len(is_flash) - win + 1)]
    else:
        counts = [int(is_flash.sum())]
    max_per_second = max(counts) if counts else 0

    return {
        'fps': round(fps, 3),
        'n_frames': len(lum),
        'n_flash_events': int(is_flash.sum()),
        'max_flashes_per_second': max_per_second,
        'breaches_wcag_2_3_1': max_per_second > _WCAG_MAX_FLASHES_PER_S,
        'wcag_limit': _WCAG_MAX_FLASHES_PER_S,
    }


def dead_frame_check(video, max_static_s=3.5, thr_mult=0.6):
    """Flag runs of near-static frames longer than the pacing budget (selection-plan-2026-10-14.md
    section 5: 'nothing static for more than 3 to 5 seconds'). Reports, does not fix."""
    W, H, fps, duration = check.probe(video)
    sw, sh = 64, 36
    a = check.extract_gray_frames(video, fps=fps, w=sw, h=sh)
    d = np.abs(np.diff(a, axis=0)).mean((1, 2))
    med = np.median(d) + 1e-3
    thr = thr_mult * med
    static = d < thr

    runs, start = [], None
    for i, s in enumerate(static):
        if s and start is None:
            start = i
        elif not s and start is not None:
            runs.append((start, i)); start = None
    if start is not None:
        runs.append((start, len(static)))

    max_run_frames = int(round(max_static_s * fps))
    breaches = [{'t0': round(s / fps, 2), 't1': round(e / fps, 2), 'duration_s': round((e - s) / fps, 2)}
                for s, e in runs if (e - s) >= max_run_frames]

    return {
        'fps': round(fps, 3),
        'max_static_s': max_static_s,
        'n_static_runs': len(runs),
        'breaches': breaches,
    }


def licence_check(edl, index_path=None):
    """True iff every sfx event naming a `sample` resolves to a cleared, credited library entry
    (sfx_library.is_cleared); an event with no `sample` (the synthesised default) never fails
    this gate. Fails render rather than letting an uncleared clip name slip through a style's
    sfx_library.map untested (plan.md:228). Reads `sfx_events` or the real edl schema's own `sfx`
    key, whichever the caller used; index_path defaults to sfx_library's own configured root."""
    path = Path(index_path) if index_path else sfx_library.ROOT / 'index.json'
    try:
        with open(path) as f:
            entries = {e['id']: e for e in json.load(f)['effects']}
    except (OSError, ValueError, KeyError):
        entries = {}
    events = edl.get('sfx_events')
    if events is None:
        events = edl.get('sfx', [])
    for e in events:
        sample = e.get('sample')
        if not sample:
            continue
        entry = entries.get(sample)
        if entry is None or not sfx_library.is_cleared(entry):
            return False
    return True


def talking_split_allowed(brief):
    """Refuse talking-head-split for an automatic choice when there are no real screen captures to
    show, instead of letting the renderer's placeholder fallback draw invented figures on screen
    (review-2 finding 13)."""
    return bool(brief.get('cards_dir'))


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('video'); ap.add_argument('edl')
    a = ap.parse_args()
    print(json.dumps({
        'safe_area': safe_area_check(a.video, a.edl),
        'flash_frequency': flash_frequency_check(a.video),
        'dead_frames': dead_frame_check(a.video),
    }, indent=1))

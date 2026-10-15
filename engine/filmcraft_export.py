#!/usr/bin/env python3
"""Turn an engine edl.json into FilmCraft command steps (python 3, standard library only).

    python3 engine/filmcraft_export.py path/to/edl.json [-o filmcraft-steps.json]

The output JSON holds
    media_import   the files to import first (newline separated text for the media_import tool)
    steps          ordered {id, params} steps for mcp__filmcraft-video__command_batch (or command_run one by one)
    export_step    one file.exportMedia step (run it last, it is not part of steps)
    manual         everything FilmCraft cannot do, each with a plain instruction
    ids            how the clip, item and sequence ids in the steps were predicted
    notes          mapping notes, calibration values and the limits of the approximation

FilmCraft hands out ids when commands run, and later steps need them (effects.setParam wants a clip id), so the
script predicts them. Workflow: import the media (media_import with the text from media_import), note the item ids
it returns, run file.newSequence once (the first step) to read its sequence id, then run the exporter again with
    --media-ids 48,49,50,...   (the ids media_import returned, in the order of media_import)
    --seq-id 79                (the id file.newSequence returned)
and delete the probe sequence. The id rules measured on the live engine are: file.newSequence takes video+audio
track ids and then its own id, every timeline.place takes one id, file.newColorMatte takes one, graphics.newText takes two.
The test harness checks the predicted ids against the ids command_batch returns.

Window: --from S --to S exports only shots and events between those timeline seconds (times stay absolute).
Options: --short-side 720|540, --name, --root (the edits folder, default: the folder above engine/).
"""
import argparse, json, math, os, random, shutil, struct, subprocess, sys, wave

TICKS = 254016000000

# --- calibration of engine grade values to FilmCraft parameters (measured against the engine's demo mp4 frames)
CAL = {
    'contrast_gain': 3.0,            # brightness_contrast.contrast = 100 * d / (1 + gain * d) with d = engine_contrast - 1 (d > 0), 100 * d below
    'brightness_per_unit': 400.0,    # brightness_contrast.brightness = engine_brightness * this
    'vignette_slope': 135.0,         # vignette.amount = -max(0, slope * engine_vignette - offset), midpoint 60
    'vignette_offset': 5.25,
    'grain_per_unit': 40.0,          # noise.amount = engine_grain * this
    'sat_per_unit': 100.0,           # proc_amp.saturation = engine saturation * this
    'blur_per_zoom_blur': 60.0,      # gaussian_blur.blurriness at peak = zoom_blur amount * this (a guess, see the notes)
    'white_alpha_gamma': 2.0,        # FilmCraft composites in linear light: a white matte at alpha a is set to a ** this to look like the engine's sRGB mix
    'black_alpha_gamma': 2.2,        # black matte: alpha a becomes 1 - (1 - a) ** this
    'rgb_split_per_unit': 640.0,     # rgb_split.amount at peak = engine amount * this (judged by eye against the demo frame, see the notes)
}


def contrast_fc(c):
    d = c - 1.0
    return 100.0 * d / (1.0 + CAL['contrast_gain'] * d) if d > 0 else 100.0 * d


def fc_alpha(a_pct, color):
    """Engine alpha (0..100, mixed in sRGB) to the FilmCraft opacity that looks the same, because FilmCraft mixes in linear light."""
    a = max(0.0, min(1.0, a_pct / 100.0))
    if color.lower() == '#000000':
        return 100.0 * (1.0 - (1.0 - a) ** CAL['black_alpha_gamma'])
    return 100.0 * a ** CAL['white_alpha_gamma']


def tk(sec):
    return int(round(sec * TICKS))


class Ids:
    """Predicts the ids FilmCraft assigns (see the module docstring)."""
    def __init__(self, seq_id):
        self.seq = seq_id
        self.n = seq_id

    def take(self, k=1):
        first = self.n + 1
        self.n += k
        return first


def aspect_dims(aspect, short, fps):
    a, b = [float(x) for x in str(aspect).split(':')]
    if a >= b:
        h = short; w = int(round(short * a / b / 2) * 2)
    else:
        w = short; h = int(round(short * b / a / 2) * 2)
    return w, h


def audio_len(path):
    """Duration in seconds of an audio file, or None. wav through the wave module, anything else through ffprobe."""
    try:
        if path.lower().endswith('.wav'):
            with wave.open(path) as w:
                return w.getnframes() / float(w.getframerate())
    except Exception:
        pass
    if shutil.which('ffprobe'):
        try:
            out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                                 capture_output=True, text=True, timeout=20).stdout.strip()
            return float(out)
        except Exception:
            return None
    return None


def hexcol(c):
    c = c or [255, 255, 255]
    return '#%02x%02x%02x' % tuple(int(max(0, min(255, v))) for v in c[:3])


def lerp(a, b, u):
    return a + (b - a) * u


def prof(name, u, peak=0.5):
    u = max(0.0, min(1.0, u))
    if name == 'tri':
        return u / peak if u < peak else (1 - u) / (1 - peak)
    if name == 'decay':
        return (1 - u) ** 2
    if name == 'attack':
        return u ** 2
    return 1.0


def ease(name, u):
    u = max(0.0, min(1.0, u))
    return {'linear': u, 'in_cubic': u ** 3, 'out_cubic': 1 - (1 - u) ** 3, 'in_out': 3 * u * u - 2 * u ** 3}.get(name, u)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('edl')
    ap.add_argument('-o', '--out', default='filmcraft-steps.json')
    ap.add_argument('--name', default=None, help='sequence name (default dl-test-<style>)')
    ap.add_argument('--short-side', type=int, default=540, help='540 matches the demo mp4s, 720 for larger output')
    ap.add_argument('--root', default=None, help='edits folder that the edl paths are relative to')
    ap.add_argument('--seq-id', type=int, default=1000, help='id file.newSequence returned (predicted ids start here)')
    ap.add_argument('--media-ids', default=None, help='comma separated item ids returned by media_import, in order')
    ap.add_argument('--media-map', default=None, help='JSON file {path: item id} instead of --media-ids (paths as in the media_import text)')
    ap.add_argument('--media-first-id', type=int, default=48, help='first item id when --media-ids is not given (consecutive)')
    ap.add_argument('--from', dest='t_from', type=float, default=0.0)
    ap.add_argument('--to', dest='t_to', type=float, default=None)
    ap.add_argument('--export', default=None, help='output path for the export_step (default <name>.mp4 beside -o)')
    ap.add_argument('--no-text', action='store_true')
    ap.add_argument('--no-audio', action='store_true')
    ap.add_argument('--no-grade', action='store_true')
    a = ap.parse_args()

    edl = json.load(open(a.edl))
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(a.root) if a.root else os.path.dirname(here)
    fps = float(edl.get('fps', 30))
    W, H = aspect_dims(edl.get('aspect', '16:9'), a.short_side, fps)
    name = a.name or 'dl-test-' + str(edl.get('style', 'edit'))
    style = {}
    for cand in (edl.get('style_path'), os.path.join(root, str(edl.get('style')), 'style.json')):
        if cand and os.path.exists(cand):
            style = json.load(open(cand)); break
    ccfg = style.get('captions') or {}
    t_from = a.t_from
    t_to = a.t_to if a.t_to is not None else float(edl['duration'])
    D = min(float(edl['duration']), t_to)

    manual, notes = [], []
    steps, returns = [], []

    def step(cid, params=None, ret=None):
        steps.append({'id': cid, 'params': params or {}})
        returns.append(ret)

    def fr(sec):                       # seconds to a whole frame, then ticks
        return int(round(sec * fps * 1.0)) * TICKS // int(round(fps)) if abs(fps - round(fps)) < 1e-6 else tk(sec)

    def tick_at(sec):                  # exact ticks, not frame snapped (keyframes may sit between frames)
        return tk(sec)

    # ---- which shots, events and words are in the window
    shots = [s for s in edl['shots'] if s['t1'] > t_from + 1e-6 and s['t0'] < t_to - 1e-6]
    events = [e for e in edl['events'] if e['t1'] > t_from and e['t0'] < t_to]
    words = [w for w in edl.get('words', []) if w['t1'] > t_from and w['t0'] < t_to]
    if not shots:
        sys.exit('no shots in the window')

    # ---- media list
    files = []
    def add_file(p):
        full = p if os.path.isabs(p) else os.path.join(root, p)
        if full not in files:
            files.append(full)
        return full
    for s in shots:
        add_file(s['clip'])
    music = edl.get('music') or {}
    vo = edl.get('voiceover') or None
    if not a.no_audio:
        if music.get('path'):
            add_file(music['path'])
        if vo and vo.get('path'):
            add_file(vo['path'])
    if a.media_map:
        mm = json.load(open(a.media_map))
        mids = [int(mm[f]) for f in files]
    elif a.media_ids:
        mids = [int(x) for x in a.media_ids.split(',')]
        if len(mids) != len(files):
            sys.exit('--media-ids has %d ids but %d files are imported, see media_import in the output' % (len(mids), len(files)))
    else:
        mids = list(range(a.media_first_id, a.media_first_id + len(files)))
    item_of = dict(zip(files, mids))
    missing = [f for f in files if not os.path.exists(f)]
    if missing:
        notes.append('files not found on this machine: ' + ', '.join(missing))

    # ---- lanes: V1 picture, then text lanes, then flash lanes (mattes sit above the captions like the engine's post layer)
    def assign_lanes(items):
        ends = []; lane_of = []
        for (t0, t1) in items:
            for li, e in enumerate(ends):
                if e <= t0 + 1e-6:
                    ends[li] = t1; lane_of.append(li); break
            else:
                ends.append(t1); lane_of.append(len(ends) - 1)
        return lane_of, len(ends)

    MATTE_FX = {'flash', 'invert', 'dip_black', 'strobe', 'lyr_strobe_pop', 'lyr_haze_flash', 'lyr_radial_flash', 'lyr_dip_mosaic'}  # lyr_strobe_pop goes to manual
    matte_events = [e for e in events if e['fx'] in MATTE_FX]
    # strobe expands to several short mattes
    matte_specs = []
    for e in matte_events:
        p = e.get('params') or {}
        t0, t1 = max(e['t0'], t_from), min(e['t1'], t_to)
        if t1 - t0 < 1.0 / fps * 0.5:
            t1 = t0 + 1.0 / fps
        fx = e['fx']
        if fx == 'flash':
            col = hexcol(p.get('color')); al = p.get('alpha', 1.0); sh = p.get('shape', 'tri'); pk = p.get('peak', 0.5)
            pts = [(u, 100 * al * prof(sh, u, pk)) for u in (0, 0.25, 0.5, 0.75, 1.0)]
            matte_specs.append(dict(t0=t0, t1=t1, color=col, blend=0, pts=pts, fx=fx, src=e))
        elif fx == 'dip_black':
            pk = p.get('peak', 0.5)          # engine: the tri profile peak position, alpha reaches 1 there
            pts = [(u, 100 * prof('tri', u, pk)) for u in (0, pk, 1.0)]
            matte_specs.append(dict(t0=t0, t1=t1, color='#000000', blend=0, pts=pts, fx=fx, src=e))
        elif fx == 'invert':
            al = 100 * p.get('alpha', 1.0)
            sh = p.get('shape', 'hold')
            pts = [(u, al * prof(sh, u)) for u in ((0, 1.0) if sh == 'hold' else (0, 0.25, 0.5, 0.75, 1.0))]
            matte_specs.append(dict(t0=t0, t1=t1, color='#ffffff', blend=19, pts=pts, fx=fx, src=e))
        elif fx == 'strobe':
            n = int(p.get('count', 4)); span = e['t1'] - e['t0']
            for k in range(n):
                s0 = e['t0'] + span * (2 * k + 1) / (n * 2.0); s1 = e['t0'] + span * (2 * k + 2) / (n * 2.0)
                matte_specs.append(dict(t0=s0, t1=s1, color=hexcol(p.get('color')), blend=0, pts=[(0, 100), (1, 100)], fx=fx, src=e))
        elif fx == 'lyr_strobe_pop':
            manual.append({'t': round(e['t0'], 3), 'fx': fx,
                           'instruction': 'Strobe pop at %.3f s for %.2f s (every other frame the picture is about 1.75 times brighter and 1.35 times more saturated). Not built. On the shot that starts at the cut add keyframes with Hold interpolation on Brightness & Contrast (contrast about +50) and Proc Amp saturation (about 140) that alternate each frame for %.2f s.' % (e['t0'], e['t1'] - e['t0'], e['t1'] - e['t0'])})
        elif fx == 'lyr_haze_flash':
            fu = p.get('flash_u', [0.35, 0.45]); cu = p.get('cut_u', 0.1); v = 100 * p.get('veil', 0.65)
            f1 = max(cu, fu[1]); eps = 0.01
            pts = [(0, 0), (cu, v), (max(cu, fu[0] - eps), v), (fu[0], 98), (fu[1] - eps, 98), (fu[1], v)]
            for q in (0.33, 0.66):
                pts.append((f1 + (1 - f1) * q, v * (1 - q) ** 1.3))
            pts.append((1.0, 0))
            matte_specs.append(dict(t0=t0, t1=t1, color='#e1e1e6', blend=0, pts=pts, fx=fx, src=e))
            notes.append('lyr_haze_flash is built as a pale veil matte with the engine envelope (veil, hard white frame, fade). The engine also blurs the picture under the veil, which is left out')
        elif fx == 'lyr_radial_flash':
            wu = p.get('white_u', 0.18); cu = p.get('cut_u', 0.7)
            pts = [(0, 0), (max(0.0, cu - wu), 0), (cu, 95)]
            for q in (0.33, 0.66):
                pts.append((cu + (1 - cu) * q, 90 * (1 - q) ** 2))
            pts.append((1.0, 0))
            matte_specs.append(dict(t0=t0, t1=t1, color='#e8f5fa', blend=0, pts=pts, fx=fx, src=e))
            notes.append('lyr_radial_flash is built as a cream flash matte with the engine envelope. The radial zoom blur is left out')
        elif fx == 'lyr_dip_mosaic':
            bl = 100 * p.get('black', 0.25)
            matte_specs.append(dict(t0=t0, t1=t1, color='#000000', blend=0, pts=[(0, 0), (0.3, bl), (1.0, 0)], fx=fx, src=e))
            manual.append({'t': round(e['t0'], 3), 'fx': fx,
                           'instruction': 'The mosaic and desaturation part is not built. Apply the Mosaic video transition (dissolve folder) on the cut at %.3f s, or add Mosaic (Stylize) to both clips with horizontal and vertical blocks keyframed from 1 to about 16 and back.' % e['tc']})
    mlanes, n_matte_lanes = assign_lanes([(m['t0'], m['t1']) for m in matte_specs])

    text_specs = []
    if words and not a.no_text:
        kind = ccfg.get('kind', 'word_pop')
        size_px = ccfg.get('size_frac', 0.08) * min(W, H) * (1.15 if (kind == 'staircase' and W <= H) else 1.0)
        hold = ccfg.get('hold_after', 0.45) if kind == 'staircase' else 0.0
        by_ph = {}
        for w in edl.get('words', []):
            by_ph.setdefault(w.get('phrase', 0), []).append(w)
        for w in words:
            i = edl['words'].index(w)
            if kind == 'staircase':
                pw = by_ph[w.get('phrase', 0)]
                t_end = max(x['t1'] for x in pw) + hold
                ln = pw.index(w)
                ph = w.get('phrase', 0)
                direction = ccfg.get('direction', 'down')
                if direction == 'alternate':
                    direction = 'down' if ph % 2 == 0 else 'up'
                lh = ccfg.get('line_height', 1.15) * size_px
                x = ccfg.get('x', 0.2) * W + ln * ccfg.get('indent', 0.045) * W
                y = (ccfg.get('y', 0.35) * H + ln * lh) if direction == 'down' else (ccfg.get('y_up', 0.72) * H - ln * lh)
                text_specs.append(dict(w=w, t0=w['t0'], t1=t_end, x=x, y=y + 0.4 * size_px, align=0, size=size_px, kind=kind))
            else:
                # engine word_pop: the word stays until the next word starts (the last one for its own length plus linger)
                nxt = edl['words'][i + 1]['t0'] if i + 1 < len(edl['words']) else w['t1'] + ccfg.get('linger', 0.0)
                t_end = max(nxt, w['t0'] + 1.0 / fps)
                yfrac = ccfg.get('y', 0.5)
                text_specs.append(dict(w=w, t0=w['t0'], t1=t_end, x=ccfg.get('x', 0.5) * W, y=yfrac * H + 0.35 * ccfg.get('size_frac', 0.1) * min(W, H),
                                       align=1, size=ccfg.get('size_frac', 0.1) * min(W, H), kind=kind))
        tlanes, n_text_lanes = assign_lanes([(t['t0'], t['t1']) for t in text_specs])
    else:
        tlanes, n_text_lanes = [], 0
    n_video = 1 + n_text_lanes + n_matte_lanes
    n_audio = 3
    ids = Ids(a.seq_id)

    # ---- 1 sequence
    step('file.newSequence', {'name': name, 'width': W, 'height': H, 'fps': fps, 'video': max(3, n_video), 'audio': n_audio}, 'sequence')
    text_lane_track = lambda li: 1 + li                       # 0-based track index of V(2+li)
    matte_track = lambda li: 1 + n_text_lanes + li
    def trk(i):                                               # place wants "V1" style names
        return 'V%d' % (i + 1)

    # ---- 2 picture
    clip_of_shot = {}
    for si, s in enumerate(shots):
        t0, t1 = s['t0'], min(s['t1'], t_to)
        item = item_of[add_file(s['clip'])]
        sp = float(s.get('speed', 1.0)) or 1.0
        dur_tl = t1 - t0
        ramp = s.get('ramp')
        src_in = float(s.get('src_in', 0.0))
        if s.get('clip_kind') == 'image':
            src_span = dur_tl
        else:
            src_span = (float(s['src_dur']) * (dur_tl / (s['t1'] - s['t0']))) if ramp else dur_tl * sp
        cid = ids.take()
        clip_of_shot[si] = cid
        step('timeline.place', {'item': item, 'track': 'V1', 'time': fr(t0), 'sourceIn': tk(src_in), 'duration': tk(src_span)}, 'clip')
        avg = src_span / dur_tl if dur_tl > 0 else 1.0
        if abs(avg - 1.0) > 1e-3 and s.get('clip_kind') != 'image':
            step('clip.speedDuration', {'clips': [cid], 'speed': round(avg * 100.0, 4)})
            if ramp:
                manual.append({'t': round(t0, 3), 'fx': 'speed ramp',
                               'instruction': 'Shot at %.3f s ramps its speed from %.2fx to %.2fx (shape %s). The exporter applied the average speed (%.1f%%). For the ramp enable Time Remapping on the clip and add speed keyframes (effects.addKeyframe then effects.setParam on effect time_remap, param speed).' % (t0, ramp['s0'] * sp, ramp['s1'] * sp, ramp.get('shape', 'in_out'), avg * 100)})
        # fit to frame: cover scale, focus offset
        sw, sh_ = float(s.get('w', W)), float(s.get('h', H))
        k = max(W / sw, H / sh_)
        base = round(k * 100.0, 4)
        pos = None
        if abs(sw * k - W) > 1 or abs(sh_ * k - H) > 1:
            f = s.get('focus') or [0.5, 0.5]
            bw_, bh_ = sw * k, sh_ * k
            tx = min(0.0, max(W - bw_, W / 2 - f[0] * bw_)); ty = min(0.0, max(H - bh_, H / 2 - f[1] * bh_))
            pos = [round(tx + bw_ / 2, 2), round(ty + bh_ / 2, 2)]
        if abs(base - 100.0) > 1e-3:
            step('effects.setParam', {'clip': cid, 'effect': 'motion', 'param': 'scale', 'value': base})
        if pos and (abs(pos[0] - W / 2) > 0.5 or abs(pos[1] - H / 2) > 0.5):
            step('effects.setParam', {'clip': cid, 'effect': 'motion', 'param': 'position', 'value': pos})
        s['_base'] = base; s['_pos'] = pos; s['_cid'] = cid; s['_t1c'] = t1

    # ---- 3 grade effects per clip
    grade_warned = set()
    if not a.no_grade:
        for si, s in enumerate(shots):
            g = s.get('grade') or {}
            cid = s['_cid']
            bw = float(g.get('bw', 0)); sat = float(g.get('saturation', 1.0))
            if bw >= 0.95:
                step('effects.apply', {'clips': [cid], 'effect': 'black_white'})
            elif bw > 0.0 or abs(sat - 1.0) > 1e-3:
                step('effects.apply', {'clips': [cid], 'effect': 'proc_amp'})
                step('effects.setParam', {'clip': cid, 'effect': 'proc_amp', 'param': 'saturation', 'value': round((1 - bw) * sat * CAL['sat_per_unit'], 3)})
            c = float(g.get('contrast', 1.0)); br = float(g.get('brightness', 0.0))
            if abs(c - 1) > 1e-3 or abs(br) > 1e-3:
                step('effects.apply', {'clips': [cid], 'effect': 'brightness_contrast'})
                if abs(c - 1) > 1e-3:
                    step('effects.setParam', {'clip': cid, 'effect': 'brightness_contrast', 'param': 'contrast', 'value': round(contrast_fc(c), 3)})
                if abs(br) > 1e-3:
                    step('effects.setParam', {'clip': cid, 'effect': 'brightness_contrast', 'param': 'brightness', 'value': round(br * CAL['brightness_per_unit'], 3)})
            if g.get('vignette', 0):
                step('effects.apply', {'clips': [cid], 'effect': 'vignette'})
                step('effects.setParam', {'clip': cid, 'effect': 'vignette', 'param': 'amount', 'value': round(-max(0.0, CAL['vignette_slope'] * g['vignette'] - CAL['vignette_offset']), 3)})
                step('effects.setParam', {'clip': cid, 'effect': 'vignette', 'param': 'midpoint', 'value': 60})
            if g.get('grain', 0):
                step('effects.apply', {'clips': [cid], 'effect': 'noise'})
                step('effects.setParam', {'clip': cid, 'effect': 'noise', 'param': 'amount', 'value': round(g['grain'] * CAL['grain_per_unit'], 3)})
            for key in ('tint', 'gamma', 'lift', 'fade', 'highlights'):
                if g.get(key) and key not in grade_warned:
                    grade_warned.add(key)
                    manual.append({'fx': 'grade.' + key,
                                   'instruction': 'Grade key %s=%s is not mapped (all shots). Add a Lumetri Color effect (or Tint, Gamma Correction) on each clip and set it by eye.' % (key, g[key])})

    # ---- 4 camera events: scale (and position) keyframes, blur, rgb split
    # Every event is turned into a function of time, then sampled inside each shot it touches. Keyframes sit on the
    # shot boundaries too, so a cut-centred effect (zoom blur) keeps its peak on both sides of the cut.
    SCALE_FX = {'slow_zoom', 'punch_in', 'zoom_pulse', 'zoom_blur', 'shake', 'drift'}
    rng = random.Random(7)
    thr = 0.25 / fps                       # events that overlap a shot by less than a quarter frame are rounding, not overlap

    def touches(e, s_):
        return min(e['t1'], s_['_t1c']) - max(e['t0'], s_['t0']) > thr

    def ev_u(e, t):
        return (t - e['t0']) / max(1e-6, e['t1'] - e['t0'])

    def ev_x(e, t):                        # -1 .. 1 around the cut, 0 at e['tc'] (centre of the span when there is no tc)
        tc = e.get('tc', (e['t0'] + e['t1']) / 2)
        tc = min(max(tc, e['t0']), e['t1'])
        if t < tc:
            return (t - tc) / max(1e-6, tc - e['t0'])
        return (t - tc) / max(1e-6, e['t1'] - tc)

    def sample_times(e, s_):
        a0, b0 = max(e['t0'], s_['t0']), min(e['t1'], s_['_t1c'])
        fxn = e['fx']
        if fxn in ('slow_zoom', 'punch_in') and (e.get('params') or {}).get('ease', 'linear' if fxn == 'slow_zoom' else 'out_cubic') == 'linear':
            n = 2
        elif fxn == 'zoom_blur':
            n = 2
        else:
            n = 5
        ts = [a0 + (b0 - a0) * q / (n - 1) for q in range(n)]
        tc = e.get('tc')
        if fxn == 'zoom_blur' and tc is not None and a0 < tc < b0:
            ts.append(tc)
        return ts

    def merge_times(ts):
        out_ = []
        for t in sorted(ts):
            if not out_ or t - out_[-1] > 1e-4:
                out_.append(t)
        return out_

    def zfac(evs, t):
        f = 1.0
        for e in evs:
            if not (e['t0'] - 1e-9 <= t <= e['t1'] + 1e-9):
                continue
            p = e.get('params') or {}
            u = ev_u(e, t)
            if e['fx'] == 'slow_zoom':
                f *= lerp(p.get('from', 1.0), p.get('to', 1.12), ease(p.get('ease', 'linear'), u))
            elif e['fx'] == 'punch_in':
                f *= lerp(p.get('from', 1.0), p.get('to', 1.15), ease(p.get('ease', 'out_cubic'), u))
            elif e['fx'] == 'zoom_pulse':
                f *= 1 + p.get('amount', 0.06) * prof(p.get('shape', 'decay'), u)
            elif e['fx'] == 'zoom_blur':
                f *= 1 + 0.5 * p.get('amount', 0.18) * (1 - abs(ev_x(e, t))) ** p.get('power', 1.2)
            elif e['fx'] == 'shake':
                f *= 1 + p.get('zoom', 0.04)
            elif e['fx'] == 'drift':
                f *= p.get('scale', 1.12)
        return f

    def key(cid, eff, param, t, val):
        step('effects.addKeyframe', {'clip': cid, 'effect': eff, 'param': param, 'time': tick_at(t)})
        step('effects.setParam', {'clip': cid, 'effect': eff, 'param': param, 'time': tick_at(t), 'value': val})

    for si, s in enumerate(shots):
        cid = s['_cid']; base = s['_base']
        evs = [e for e in events if e['fx'] in SCALE_FX and touches(e, s)]
        if evs:
            times = [s['t0'], s['_t1c']]
            for e in evs:
                times += sample_times(e, s)
            times = merge_times(times)
            vals = [(t, round(base * zfac(evs, t), 4)) for t in times]
            if len({v for _, v in vals}) > 1:
                for (t, v) in vals:
                    key(cid, 'motion', 'scale', t, v)
            shk = [e for e in evs if e['fx'] == 'shake']
            if shk:
                pos0 = s['_pos'] or [W / 2, H / 2]
                for t in times:
                    amp = 0.0
                    for e in shk:
                        if e['t0'] - 1e-9 <= t <= e['t1'] + 1e-9:
                            amp = max(amp, (e.get('params') or {}).get('amount', 0.02) * (1 - ev_u(e, t)) ** 2 * W)
                    key(cid, 'motion', 'position', t, [round(pos0[0] + rng.uniform(-1, 1) * amp, 2), round(pos0[1] + rng.uniform(-1, 1) * amp, 2)])
            for e in evs:
                if e['fx'] == 'drift':
                    manual.append({'t': round(e['t0'], 3), 'fx': 'drift', 'instruction': 'Drift pan is applied as a constant scale only. Keyframe Motion position across the shot for the pan.'})
        zb = [e for e in events if e['fx'] == 'zoom_blur' and touches(e, s)]
        if zb:
            step('effects.apply', {'clips': [cid], 'effect': 'gaussian_blur'})
            pts = {s['t0']: 0.0, s['_t1c']: 0.0}
            for e in zb:
                p = e.get('params') or {}
                for t in sample_times(e, s) + [s['t0'], s['_t1c']]:
                    if e['t0'] - 1e-9 <= t <= e['t1'] + 1e-9:
                        v = round(CAL['blur_per_zoom_blur'] * p.get('amount', 0.18) * (1 - abs(ev_x(e, t))) ** p.get('power', 1.2), 3)
                        pts[t] = max(pts.get(t, 0.0), v)
            ts = merge_times(list(pts))
            for t in ts:
                key(cid, 'gaussian_blur', 'blurriness', t, pts[min(pts, key=lambda k_: abs(k_ - t))])
        rs = [e for e in events if e['fx'] == 'rgb_split' and touches(e, s)]
        if rs:
            step('effects.apply', {'clips': [cid], 'effect': 'rgb_split'})
            pts = {s['t0']: 0.0}
            for e in rs:
                p = e.get('params') or {}
                for q in range(4):
                    u = q / 3; t = min(max(e['t0'] + (e['t1'] - e['t0']) * u, s['t0']), s['_t1c'])
                    pts[t] = round(CAL['rgb_split_per_unit'] * p.get('amount', 0.012) * prof(p.get('shape', 'tri'), u), 3)
            ts = merge_times(list(pts))
            for t in ts:
                key(cid, 'rgb_split', 'amount', t, pts[min(pts, key=lambda k_: abs(k_ - t))])

    # ---- 5 matte items and matte clips (flashes, dips, inversions)
    matte_items = {}
    if matte_specs:
        for col in sorted({m['color'] for m in matte_specs}):
            matte_items[col] = ids.take()
            step('file.newColorMatte', {'color': col, 'seconds': 3.0}, 'item')
        for mi, m in enumerate(matte_specs):
            cid = ids.take()
            # the engine shows an event on the frames whose time t satisfies t0 <= t < t1, so the matte covers exactly those frames
            fa = int(math.ceil(m['t0'] * fps - 1e-6)); fb = max(fa + 1, int(math.ceil(m['t1'] * fps - 1e-6)))
            a_t, b_t = fa * TICKS // int(round(fps)), fb * TICKS // int(round(fps))
            b_t = min(b_t, a_t + 3 * TICKS)
            step('timeline.place', {'item': matte_items[m['color']], 'track': trk(matte_track(mlanes[mi])), 'time': a_t, 'sourceIn': 0, 'duration': b_t - a_t}, 'clip')
            if m['blend']:
                step('effects.setParam', {'clip': cid, 'effect': 'opacity', 'param': 'blend', 'value': m['blend']})
            vd = {}
            for (u, v) in m['pts']:                       # one keyframe per tick: adding a second at the same tick would toggle it off
                vd[min(b_t, max(a_t, tk(m['t0'] + u * (m['t1'] - m['t0']))))] = round(fc_alpha(v, m['color']), 2)
            vals = sorted(vd.items())
            if len({v for _, v in vals}) > 1 or vals[0][1] != 100:
                for (t, v) in vals:
                    step('effects.addKeyframe', {'clip': cid, 'effect': 'opacity', 'param': 'opacity', 'time': t})
                    step('effects.setParam', {'clip': cid, 'effect': 'opacity', 'param': 'opacity', 'time': t, 'value': v})

    # ---- 6 captions as text clips
    for ti, t in enumerate(text_specs):
        w = t['w']
        txt = w['text'].upper() if ccfg.get('upper', True) else w['text']
        emph = bool(w.get('emph'))
        size = t['size'] * (ccfg.get('emph_scale', 1.45) if emph else 1.0)
        a_t, b_t = max(fr(t['t0']), fr(t_from)), fr(t['t1'])
        if b_t <= a_t:
            b_t = a_t + TICKS // int(round(fps))
        cut_off = b_t > fr(D)                     # a caption that would run past the end of the exported window is trimmed to it
        b_t = min(b_t, fr(D))
        if b_t <= a_t:
            continue
        cid = ids.take(2)
        t['_a'], t['_b'] = a_t, b_t
        params = {'text': txt, 'size': round(size, 1), 'seconds': round((b_t - a_t) / TICKS, 6), 'time': a_t, 'track': text_lane_track(tlanes[ti]),
                  'newClip': True, 'position': [round(t['x'], 1), round(t['y'], 1)]}
        if ccfg.get('font'):
            params['font'] = ccfg['font']
        step('graphics.newText', params, 'text')
        if t['align']:
            step('effects.setParam', {'clip': cid, 'effect': 'graphic_text', 'param': 'align', 'value': 1})
        col = ccfg.get('emph_color') if emph and ccfg.get('emph_color') else (ccfg.get('color') or ((ccfg.get('themes') or [{}])[0].get('color')))
        if col and list(col)[:3] != [255, 255, 255]:
            step('effects.setParam', {'clip': cid, 'effect': 'graphic_text', 'param': 'fill_color', 'value': hexcol(col)})
        if ccfg.get('kind') == 'lyric_diff':
            step('effects.setParam', {'clip': cid, 'effect': 'opacity', 'param': 'blend', 'value': 19})
        fi = ccfg.get('fade_in', 0.0) if t['kind'] == 'staircase' else 0.0
        fo = ccfg.get('fade_out', 0.0) if t['kind'] == 'staircase' else 0.0
        if fi or fo:
            keys = []
            if fi: keys += [(a_t, 0), (min(b_t, a_t + tk(fi)), 100)]
            if fo and not cut_off: keys += [(max(a_t, b_t - tk(fo)), 100), (b_t, 0)]
            seen = set()
            for (tt, v) in keys:
                if tt in seen:
                    continue
                seen.add(tt)
                step('effects.addKeyframe', {'clip': cid, 'effect': 'opacity', 'param': 'opacity', 'time': tt})
                step('effects.setParam', {'clip': cid, 'effect': 'opacity', 'param': 'opacity', 'time': tt, 'value': round(fc_alpha(v, '#ffffff'), 2)})
    if words and a.no_text:
        manual.append({'fx': 'captions', 'instruction': 'Captions were skipped (--no-text). Add the %d words as text layers with graphics.newText.' % len(words)})

    # ---- 7 audio
    if not a.no_audio:
        if music.get('path'):
            mfull = add_file(music['path'])
            cid = ids.take()
            dur = D - t_from
            ln = audio_len(mfull)
            ms = float(music.get('start', 0.0)) + t_from
            if ln is not None:
                dur = min(dur, ln - ms)
            step('timeline.place', {'item': item_of[mfull], 'track': 'A1', 'time': fr(t_from), 'sourceIn': tk(ms), 'duration': tk(dur)}, 'clip')
            if vo and vo.get('path'):
                vfull = add_file(vo['path'])
                vid = ids.take()
                vstart = float(vo.get('start', 0.0))
                vl = audio_len(vfull)
                v_in = max(0.0, t_from - vstart)               # window: skip the part of the voiceover before the window
                v_at = max(vstart, t_from)
                vdur = D - v_at
                if vl is not None:
                    vdur = min(vdur, vl - v_in)
                if vdur > 0 and v_at < D:
                    step('timeline.place', {'item': item_of[vfull], 'track': 'A2', 'time': fr(v_at), 'sourceIn': tk(v_in), 'duration': tk(vdur)}, 'clip')
                    step('essentialSound.setType', {'clips': [vid], 'type': 'dialogue'})
                    step('essentialSound.setType', {'clips': [cid], 'type': 'music'})
                    step('essentialSound.set', {'clips': [cid], 'key': 'ducking.reduceDb', 'value': -9.0})
                    step('essentialSound.generateDucking', {'clips': [cid]})
                else:
                    ids.n -= 1                                  # nothing placed, give the id back
        if edl.get('sfx'):
            kinds = sorted({x['kind'] for x in edl['sfx']})
            manual.append({'fx': 'sfx', 'instruction': 'The engine synthesises %d sound effects (%s) at the times in edl.json sfx. FilmCraft has no generator for them. Render them with the engine (python3 engine/make_edit.py --edl edl.json) or add your own samples on A3 at those times.' % (len(edl['sfx']), ', '.join(kinds))})

    # ---- 8 things never built
    done_fx = SCALE_FX | MATTE_FX | {'rgb_split'}
    for e in events:
        if e['fx'] in done_fx:
            continue
        ins = {
            'mask_flash': 'Subject mask flash: duplicate the clip at %.3f s onto the next video track, keep only the subject (Ultra Key or Luma Key on the figure.mask.mp4 clip, or a Track Matte using it), fill it white and fade opacity 0 > 100 > 0 over %.2f s.',
            'tile': 'Tile effect: apply Clone (Utility) with 2 columns and 2 rows on the clip at %.3f s for %.2f s, then keyframe Opacity for the decay.',
            'glitch': 'Glitch: apply RGB Split or Wave Warp on the clip at %.3f s for %.2f s with a short keyframed amount.',
            'whip': 'Whip pan: apply the Push or Whip transition on the cut at %.3f s (duration %.2f s) and add Directional Blur keyframed 0 > 80 > 0.',
            'hud_bar': 'DETECTING HUD bar at %.3f s for %.2f s: add a brown rectangle (graphics.newRectangle, fill about #5a3a2a, full width, top of frame) with a text layer typing DETECTING plus dots, and small white text readouts. Keyframe the text for the typewriter.',
            'hud_wipe': 'Detect wipe at %.3f s for %.2f s: add a brown Color Matte band as tall as the caption row, slide it across with Motion position keyframes, and use Difference blend on a duplicate of the footage inside the band for the inverted cut-out look.',
            'hud_heat': 'Heat flash at %.3f s for %.2f s: on the footage clip apply Tint (black to deep red, white to cream) with Amount keyframed 0 > 100 > 0, and Crop or a Mask limited to the band between 11.5 and 88.4 percent of the frame height. Slide the band sideways with a Motion position keyframe.',
            'hud_marks': 'Corner markers at %.3f s for %.2f s: add small red squares (graphics.newShape rectangle) on the corners with Motion position keyframes jumping between corners.',
            'hud_glitch': 'Opening glitch at %.3f s for %.2f s: apply RGB Split (amount about 30) and Wave Warp or Mosaic with short keyframes on the first shot, plus two black Color Matte dropout frames.',
            'lyr_band_wipe': 'Band wipe: add a black Color Matte on the clip at %.3f s, crop it to a band with Crop (top about 20 percent, bottom about 38 percent) and keyframe the crop closed over %.2f s.',
            'lyr_card_up': 'Card slide up: nest the outgoing shot, scale it to 62 percent and keyframe Motion position upward over %.2f s starting %.3f s (the engine shows it as a card rising from the bottom).',
        }.get(e['fx'])
        if ins:
            if e['fx'] in ('lyr_card_up',):
                text = ins % (e['t1'] - e['t0'], e['t0'])
            else:
                text = ins % (e['t0'], e['t1'] - e['t0'])
        else:
            text = 'Effect %s with %s at %.3f s for %.2f s has no FilmCraft equivalent in the exporter. Recreate it by eye.' % (e['fx'], json.dumps(e.get('params') or {}), e['t0'], e['t1'] - e['t0'])
        manual.append({'t': round(e['t0'], 3), 'fx': e['fx'], 'instruction': text})
    if style.get('overlays'):
        for o in style['overlays']:
            manual.append({'fx': 'overlay:' + str(o.get('kind')), 'instruction': 'Overlay %s from style.json is a per-frame engine overlay (sticker, wordmark, HUD). Rebuild it with graphics.newText, graphics.newShape and keyframes, or leave it out.' % o.get('kind')})

    out_path = os.path.abspath(a.out)
    export_path = a.export or os.path.splitext(out_path)[0] + '.mp4'
    result = {
        'edl': os.path.abspath(a.edl), 'style': edl.get('style'), 'sequence': {'name': name, 'width': W, 'height': H, 'fps': fps, 'video_tracks': max(3, n_video), 'audio_tracks': n_audio},
        'window': [t_from, D],
        'media_import': {'text': '\n'.join(files), 'files': files},
        'ids': {'sequence_id_assumed': a.seq_id, 'media_ids_assumed': dict(zip(files, mids)),
                'how': 'ids are predicted: rerun with --media-ids and --seq-id from the real results (see the script docstring)'},
        'steps': steps,
        'export_step': {'id': 'file.exportMedia', 'params': {'path': export_path, 'format': 'h264', 'range': 'entire', 'wait': True}},
        'manual': manual,
        'notes': notes + (['caption kind %s is approximated as one centred word at a time' % ccfg.get('kind')] if words and not a.no_text and ccfg.get('kind') not in ('staircase', 'word_pop', 'lyric_diff', 'subtitle', None) else []) + ['lanes: V1 picture' + (', V2..V%d captions' % (1 + n_text_lanes) if n_text_lanes else '') + (', V%d..V%d flashes and dips' % (2 + n_text_lanes, 1 + n_text_lanes + n_matte_lanes) if n_matte_lanes else '') + ', A1 music, A2 voiceover'],
        'limits': [
            'FilmCraft mixes layers in linear light, the engine mixes in sRGB. Flash and dip opacities are converted with white_alpha_gamma and black_alpha_gamma in the calibration block, so they match best over mid-grey pictures and run a little bright over near-black ones.',
            'invert events are a white matte in Difference blend (blend index 19). Difference is computed in linear light, so mid-tones come out lighter than the engine inversion while colours and shapes match.',
            'zoom_blur is a Gaussian Blur plus a scale pulse. The engine blur is radial, FilmCraft has no radial blur.',
            'Film grain is the Noise effect and vignette the Vignette effect. Values were matched by eye and by region means against the demo frames, they are close but not pixel exact.',
            'Fonts: graphics.newText accepts a font name, but Avenir Next Bold rendered as the default sans in the live engine. Set the font in the Essential Graphics panel if it matters.',
            'The engine can render sound effects, FilmCraft cannot generate them (see manual).',
        ],
        'calibration': CAL,
        'counts': {'steps': len(steps), 'shots': len(shots), 'events': len(events), 'matte_clips': len(matte_specs), 'text_clips': len(text_specs), 'manual': len(manual)},
        'expected_returns': returns,
    }
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=1)
    print('wrote %s: %d steps, %d shots, %d flash/dip mattes, %d text clips, %d manual items' % (out_path, len(steps), len(shots), len(matte_specs), len(text_specs), len(manual)))


if __name__ == '__main__':
    main()

"""Compositor: renders an edl.json to video. Frames are decoded per shot with ffmpeg, processed in numpy and OpenCV
(grade, camera moves, captions, overlays, transition effects) and encoded through an ffmpeg pipe, with the music window
and synthesised sound effects mixed into the audio.
"""
import json, os, subprocess, sys, tempfile, shutil, importlib, pkgutil
from pathlib import Path
import numpy as np
import cv2
import fx as fxm
import captions as capm
import sfx as sfxm
import clips as clipmod
import audio as audiomod
import loudness as loudnessmod

HERE = Path(__file__).parent
OVERLAYS = {}


def overlay(name):
    def deco(f):
        OVERLAYS[name] = f
        return f
    return deco


def load_ext():
    """Import every module in engine/ext so styles can register effects, caption kinds and overlays."""
    sys.path.insert(0, str(HERE))
    for m in sorted((HERE / 'ext').glob('*.py')):
        if m.name.startswith('_'): continue
        importlib.import_module(f'ext.{m.stem}')


GEOMETRY = {'punch_in', 'slow_zoom', 'zoom_pulse', 'drift', 'shake', 'whip', 'zoom_blur'}
PRE_DEFAULT = {'punch_in', 'slow_zoom', 'zoom_pulse', 'drift', 'freeze', 'grade'}

RAMP_ANCHOR_MODE = 'beat'           # Stage 8: speed ramps are anchored to beat time (plan.py converts a
                                     # ramp's portion_beats to a shot-local fraction), not to shot fraction.
SLOWMO_THRESHOLD = 0.92              # a ramp or base speed below this multiplier counts as slow motion
MAX_DECODE_FPS = 240                 # cap on raised decode fps, so a near-freeze ramp can't demand an
                                      # unbounded ffmpeg filter rate


def ramp_anchor_mode():
    """'beat': a shot's ramp.portion is computed from beat offsets (plan.py), so a ramp's absolute
    duration follows the music's tempo rather than stretching or squeezing with the shot's own length."""
    return RAMP_ANCHOR_MODE


def _cover_params(sw, sh, W, H, focus):
    f = max(W / sw, H / sh)
    Wc, Hc = int(np.ceil(sw * f)), int(np.ceil(sh * f))
    cx = int(np.clip(focus[0] * Wc - W / 2, 0, Wc - W)); cy = int(np.clip(focus[1] * Hc - H / 2, 0, Hc - H))
    return Wc, Hc, cx, cy


class ShotReader:
    """Streams frames of one shot, cropped to the output size around the clip's focus point."""
    def __init__(self, shot, W, H, gray=False, path=None, fps_out=30, scale=1.0, still_os=1.4):
        self.W, self.H = int(W * scale) // 2 * 2, int(H * scale) // 2 * 2
        self.gray = gray; self.proc = None; self.last = None; self.idx = -1; self.dfps = fps_out
        self.path = path or shot['clip']; self.shot = shot
        self.still = shot['clip_kind'] == 'image' and path is None
        sw, sh = shot['w'], shot['h']
        self.Wc, self.Hc, self.cx, self.cy = _cover_params(sw, sh, self.W, self.H, shot['focus'])
        if shot['clip_kind'] == 'image':
            im = cv2.imread(self.path)
            if gray: im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            f = max(self.W * still_os / im.shape[1], self.H * still_os / im.shape[0])
            self.big = cv2.resize(im, None, fx=f, fy=f, interpolation=cv2.INTER_AREA if f < 1 else cv2.INTER_CUBIC)
            self.still_os = still_os
            return
        r = shot.get('ramp')
        mx = shot['speed'] * (max(r['s0'], r['s1']) if r else 1.0)
        mn = shot['speed'] * (min(r['s0'], r['s1']) if r else shot['speed'])
        self.dfps = int(max(fps_out, np.ceil(fps_out * mx)))
        slowmo = mn < SLOWMO_THRESHOLD
        if slowmo:                  # real slow motion needs frames the source never shot: raise the decode
            self.dfps = int(min(MAX_DECODE_FPS, max(self.dfps, np.ceil(fps_out / max(mn, fps_out / MAX_DECODE_FPS)))))
        sw_ = f'scale={self.Wc}:{self.Hc}:flags=bicubic,crop={self.W}:{self.H}:{self.cx}:{self.cy}'
        # fps duplicates the nearest decoded frame when upsampling (a stutter under slow motion);
        # minterpolate blends the two neighbouring frames instead, so a ramped-down shot reads as
        # smooth motion rather than repeated frames (Stage 8 scope).
        rate = f'minterpolate=fps={self.dfps}:mi_mode=blend' if slowmo else f'fps={self.dfps}'
        cmd = ['ffmpeg', '-v', 'error', '-ss', f"{shot['src_in']:.3f}", '-t', f"{shot['src_dur'] + 0.5:.3f}", '-i', self.path,
               '-vf', f'{rate},{sw_}', '-an', '-pix_fmt', 'gray' if gray else 'bgr24', '-f', 'rawvideo', '-']
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10 ** 7)
        self.fsz = self.W * self.H * (1 if gray else 3)

    def _read(self):
        b = self.proc.stdout.read(self.fsz)
        if len(b) < self.fsz: return None
        a = np.frombuffer(b, np.uint8)
        return a.reshape(self.H, self.W) if self.gray else a.reshape(self.H, self.W, 3)

    def frame(self, src_dt):
        """Frame at src_dt seconds after the shot's src_in (video), or the still view (images)."""
        if self.still: return self.big
        i = max(0, int(round(src_dt * self.dfps)))
        while self.idx < i:
            f = self._read()
            if f is None: break
            self.last = f; self.idx += 1
        return self.last if self.last is not None else np.zeros((self.H, self.W) if self.gray else (self.H, self.W, 3), np.uint8)

    def close(self):
        if self.proc:
            try: self.proc.stdout.close(); self.proc.kill()
            except Exception: pass


def kb_view(big, u, kb, W, H, os_, focus=(0.5, 0.5)):
    """Ken Burns view of a still: scale from 1 to kb.scale and a pan along kb.dir, sampled from the large image,
    always covering the frame and keeping the focus point in view."""
    s = 1.0 + (kb['scale'] - 1.0) * u
    a = np.deg2rad(kb['dir']); amt = kb['amount'] * (u - 0.5)
    bh, bw = big.shape[:2]
    k = max(W / bw, H / bh) * s
    tx = W / 2 - focus[0] * bw * k + np.cos(a) * amt * W
    ty = H / 2 - focus[1] * bh * k + np.sin(a) * amt * H
    tx = float(np.clip(tx, W - bw * k, 0)); ty = float(np.clip(ty, H - bh * k, 0))
    M = np.float32([[k, 0, tx], [0, k, ty]])
    return cv2.warpAffine(big, M, (W, H), flags=cv2.INTER_AREA if k < 1 else cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def time_map(shot, n):
    """Source seconds (after src_in) for each of n output frames of the shot, honouring speed and ramps."""
    dur = shot['t1'] - shot['t0']
    u = (np.arange(n) + 0.0) / max(1, n)
    sp = np.ones(1000) * shot['speed']
    uu = np.linspace(0, 1, 1000)
    r = shot.get('ramp')
    if r:
        a, b = r['portion']
        for i, x in enumerate(uu):
            if x < a: s = r['s0']
            elif x > b: s = r['s1']
            else: s = r['s0'] + (r['s1'] - r['s0']) * fxm.ease(r['shape'], (x - a) / max(1e-6, b - a))
            sp[i] = shot['speed'] * s
    cum = np.cumsum(sp) / 1000 * dur
    return np.interp(u, uu, cum)


def mix_audio(edl, out_wav, song_path, vo_path=None, tail_fade=True):
    SR = sfxm.SR
    D = edl['duration']
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f"{edl['music']['start']:.4f}", '-t', f'{D + 0.1:.3f}', '-i', song_path, '-vn',
                          '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    m = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    n = int(D * SR)
    if len(m) < n: m = np.pad(m, ((0, n - len(m)), (0, 0)))
    m = m[:n]
    if tail_fade:
        fo = int(0.45 * SR); m[-fo:] *= np.linspace(1, 0, fo)[:, None]
    for e in edl['sfx']:                                    # gap events mute the music for a span (the reference's stop-start hits)
        if e['kind'] == 'gap':
            a = int(e['t'] * SR); b = min(len(m), a + int(e.get('dur', 0.12) * SR)); r = int(0.004 * SR)
            if a < len(m) and b > a:
                m[a:b] *= 0.0
                if a - r > 0: m[a - r:a] *= np.linspace(1, 0, r)[:, None]
    fi = int(0.01 * SR); m[:fi] *= np.linspace(0, 1, fi)[:, None]
    mix = m * edl.get('audio', {}).get('music_gain', 1.0)
    if vo_path:
        v = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', vo_path, '-vn', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32).reshape(-1, 2)
        vs = int(edl['voiceover']['start'] * SR) if edl.get('voiceover') else 0
        vv = np.zeros_like(mix); L = min(len(v), len(vv) - vs)
        if L > 0: vv[vs:vs + L] = v[:L]
        env = np.abs(vv).mean(1); k = int(0.15 * SR)
        env = np.convolve(env, np.ones(k) / k, 'same'); duck = 1 - 0.65 * np.clip(env / (env.max() + 1e-9) * 4, 0, 1)
        mix = mix * duck[:, None] + vv
    sx = sfxm.mix(D, [e for e in edl['sfx'] if e['kind'] != 'gap'])
    mix = mix + sx[:len(mix)]
    mix, _loudness_report = loudnessmod.normalise(mix, SR)
    import wave
    pcm = (np.clip(mix, -1, 1) * 32767).astype('<i2')
    with wave.open(str(out_wav), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


def gen_masks(shot, W, H, fps, tmp):
    """Person masks for a shot: the clip's own .mask.mp4 if present, else Apple Vision on a downscaled pass."""
    if shot.get('mask') and os.path.exists(shot['mask']):
        return ShotReader(shot, W, H, gray=True, path=shot['mask'], fps_out=fps)
    vb = clipmod.vision_bin()
    sc = 0.5
    n = int(round((shot['t1'] - shot['t0']) * fps))
    rd = ShotReader(shot, W, H, scale=sc, fps_out=fps)
    tm = time_map(shot, n)
    d = Path(tmp) / f"m_{shot['t0']:.3f}"; (d / 'in').mkdir(parents=True, exist_ok=True)
    for i in range(n):
        fr = rd.frame(tm[i]) if not rd.still else kb_view(rd.big, i / max(1, n - 1), shot.get('kenburns', {'scale': 1, 'dir': 0, 'amount': 0}), rd.W, rd.H, rd.still_os, shot['focus'])
        cv2.imwrite(str(d / 'in' / f'{i:05d}.png'), fr)
    rd.close()
    if vb: subprocess.run([str(vb), 'mask', str(d / 'in'), str(d / 'out')], capture_output=True)
    kind = 'person'
    if not _vision_mask_ok(d / 'out', n):          # no person found (or the whole frame): salient-object matte instead
        _grabcut_masks(d / 'in', d / 'out', n); kind = 'object'
    return ('files', d / 'out', n, kind)


def _vision_mask_ok(outdir, n):
    covs = []
    for i in sorted({0, n // 2, max(0, n - 1)}):
        p = outdir / f'{i:05d}.png'
        if not p.exists(): return False
        m = cv2.imread(str(p), 0)
        covs.append(float((m > 127).mean()))
    return 0.04 < float(np.median(covs)) < 0.45


def _saliency(small):
    """Spectral-residual saliency blended with centre-surround colour contrast, 0..1."""
    g = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY).astype(np.float32)
    f = np.fft.fft2(cv2.resize(g, (64, 64)))
    lg = np.log(np.abs(f) + 1e-6); ph = np.angle(f)
    res = lg - cv2.blur(lg, (3, 3))
    sal = np.abs(np.fft.ifft2(np.exp(res + 1j * ph))) ** 2
    sal = cv2.GaussianBlur(sal.astype(np.float32), (0, 0), 2.5)
    sal = cv2.resize(sal, (small.shape[1], small.shape[0]))
    lab = cv2.cvtColor(small, cv2.COLOR_BGR2LAB).astype(np.float32)
    con = np.linalg.norm(lab - lab.reshape(-1, 3).mean(0), axis=2)
    con = cv2.GaussianBlur(con, (0, 0), 3)
    n = lambda a: (a - a.min()) / (a.max() - a.min() + 1e-6)
    return 0.5 * n(sal) + 0.5 * n(con)


def _grabcut_masks(indir, outdir, n):
    """Foreground matte for footage with no person: GrabCut seeded from saliency, smoothed over time."""
    outdir.mkdir(parents=True, exist_ok=True)
    prev = None
    for i in range(n):
        p = indir / f'{i:05d}.png'
        im = cv2.imread(str(p))
        if im is None: continue
        h0, w0 = im.shape[:2]
        sm = cv2.resize(im, (160, max(8, int(160 * h0 / w0))))
        sal = _saliency(sm)
        gm = np.full(sal.shape, cv2.GC_PR_BGD, np.uint8)
        gm[sal > 0.55] = cv2.GC_PR_FGD
        gm[sal > 0.8] = cv2.GC_FGD
        b = max(2, int(0.04 * sal.shape[0]))
        gm[:b] = cv2.GC_BGD; gm[-b:] = cv2.GC_BGD; gm[:, :b] = cv2.GC_BGD; gm[:, -b:] = cv2.GC_BGD
        try:
            bg = np.zeros((1, 65), np.float64); fg = np.zeros((1, 65), np.float64)
            if (gm == cv2.GC_FGD).sum() < 20: gm[sal > np.percentile(sal, 85)] = cv2.GC_FGD
            cv2.grabCut(sm, gm, None, bg, fg, 3, cv2.GC_INIT_WITH_MASK)
            m = ((gm == cv2.GC_FGD) | (gm == cv2.GC_PR_FGD)).astype(np.float32)
        except Exception:
            m = (sal > 0.6).astype(np.float32)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        m = cv2.GaussianBlur(m, (0, 0), 1.2)
        if prev is not None: m = 0.5 * m + 0.5 * prev
        prev = m
        cv2.imwrite(str(outdir / f'{i:05d}.png'), cv2.resize((np.clip(m, 0, 1) * 255).astype(np.uint8), (w0, h0), interpolation=cv2.INTER_LINEAR))


DEPTH_DEFAULT = {'enabled': True, 'behind_ratio': 0.5, 'min_cover': 0.03, 'max_cover': 0.85, 'min_visible': 0.55}


def assign_depth(words, dcfg):
    """Key (emphasis) words alternate between behind and in front of the subject by behind_ratio, supporting words stay in front.
    With ratio 0.5 the first key word sits behind, the next in front, and so on through the edit."""
    r = dcfg.get('behind_ratio', 0.5); k = 0
    for w in words:
        w['depth'] = 'front'
        if w.get('emph'):
            if np.ceil((k + 1) * r - 1e-9) > np.ceil(k * r - 1e-9): w['depth'] = 'behind'
            k += 1


def render(edl, out_path, song_path, vo_path=None, size_short=720, keep_tmp=False, progress=True):
    load_ext()
    fps = edl['fps']; D = edl['duration']
    aw, ah = map(int, edl['aspect'].split(':'))
    if ah >= aw: W, H = size_short, int(round(size_short * ah / aw / 2) * 2)
    else: H, W = size_short, int(round(size_short * aw / ah / 2) * 2)
    style = json.load(open(edl['style_path'])) if edl.get('style_path') else {}
    band = style.get('layout', {}).get('band')
    cW, cH = (W, int(round(W * 9 / 16 / 2) * 2)) if band and ah > aw else (W, H)
    nf = int(round(D * fps))
    words = edl.get('words', [])
    ccfg = style.get('captions') or {}
    cap = capm.Renderer(ccfg, cW, cH, words) if ccfg and words else None
    dcfg = dict(DEPTH_DEFAULT); dcfg.update(ccfg.get('depth_text') or {})
    if dcfg['enabled'] and words: assign_depth(words, dcfg)
    mask_all = bool(ccfg.get('behind_subject')) or style.get('needs_mask') or (dcfg['enabled'] and bool(words) and ccfg.get('kind') != 'hud_row')
    mask_spans = [(e['t0'], e['t1']) for e in edl['events'] if e['fx'] == 'mask_flash' or e.get('needs_mask')]
    def shot_needs_mask(s_):
        return mask_all or any(a < s_['t1'] and b > s_['t0'] for a, b in mask_spans)
    overlays_cfg = style.get('overlays', [])
    tmp = tempfile.mkdtemp(prefix='edit_')
    wav = Path(tmp) / 'mix.wav'
    mix_audio(edl, wav, song_path, vo_path, tail_fade=not style.get('cuts', {}).get('loop_seam_beats'))
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
                            '-i', str(wav), '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                            '-movflags', '+faststart', '-t', f'{D:.4f}', str(out_path)], stdin=subprocess.PIPE)
    store = {}
    shots = edl['shots']
    events = edl['events']
    si = -1; reader = None; mreader = None; tm = None; sh = None; sstart = 0
    for f in range(nf):
        t = f / fps
        while si + 1 < len(shots) and t >= shots[si + 1]['t0'] - 1e-6:
            if reader: reader.close()
            if mreader and hasattr(mreader, 'close'): mreader.close()
            si += 1; sh = shots[si]; sstart = int(round(sh['t0'] * fps))
            store['prev_shot_last'] = store.get('cur_last')      # last graded frame of the previous shot, for transitions that need the outgoing picture
            n = max(1, int(round(sh['t1'] * fps)) - sstart)
            tm = time_map(sh, n)
            reader = ShotReader(sh, cW, cH, fps_out=fps)
            mreader = gen_masks(sh, cW, cH, fps, tmp) if shot_needs_mask(sh) else None
            mkind = mreader[3] if isinstance(mreader, tuple) and len(mreader) > 3 else 'person'
        li = f - sstart; u_shot = li / max(1, int(round(sh['t1'] * fps)) - sstart - 1)
        seed = (edl.get('seed', 1) * 100003 + f) & 0xffffffff
        ctx = {'w': cW, 'h': cH, 'fps': fps, 'frame': f, 't': t, 'rng': np.random.default_rng(seed), 'store': store, 'mask': None,
               'shot': sh, 'shot_index': si, 'mask_kind': mkind if mreader is not None else None, 'u_shot': u_shot, 'edl': edl, 'style': style, 'words': words}
        if reader.still:
            img = kb_view(reader.big, u_shot, sh.get('kenburns', {'scale': 1.0, 'dir': 0, 'amount': 0}), cW, cH, reader.still_os, sh['focus'])
        else:
            img = reader.frame(tm[li] if li < len(tm) else tm[-1])
        img = img.copy()
        if sh.get('grade'): img = fxm.grade_fx(img, {'u': 0}, sh['grade'], ctx)
        store['cur_last'] = img
        # mask
        if mreader is not None:
            if isinstance(mreader, tuple):
                p = mreader[1] / f'{min(li, mreader[2] - 1):05d}.png'
                m = cv2.imread(str(p), 0) if p.exists() else None
                m = cv2.resize(m, (cW, cH)) if m is not None else None
            else:
                m = mreader.frame(tm[li] if li < len(tm) else tm[-1]) if not mreader.still else cv2.resize(cv2.cvtColor(mreader.big, cv2.COLOR_BGR2GRAY) if mreader.big.ndim == 3 else mreader.big, (cW, cH))
            if m is not None:
                ctx['mask'] = (m.astype(np.float32) / 255.0)
                cov = float(ctx['mask'].mean())
                ctx['mask_ok'] = dcfg['min_cover'] < cov < dcfg['max_cover']
        active = [e for e in events if e['t0'] - 1e-6 <= t < e['t1'] - 1e-6]
        # pre layer: camera moves
        for e in active:
            layer = e.get('layer') or ('pre' if e['fx'] in PRE_DEFAULT else 'post')
            if layer != 'pre': continue
            k = {'u': (t - e['t0']) / max(1e-6, e['t1'] - e['t0']), 'x': 0.0, 't': t - e['t0'], 'span': e['t1'] - e['t0']}
            img, ctx['mask'] = _run(e, img, k, ctx)
        # captions and overlays
        if cap is not None:
            ctx['img'] = img                                     # caption kinds that blend with the picture (difference) read this
            two = dcfg['enabled'] and ccfg.get('kind') != 'hud_row' and ctx['mask'] is not None and ctx.get('mask_ok')
            if two:
                ctx['depth_pass'] = 'behind'; lb = cap.render(t, ctx)
                ctx['depth_pass'] = 'front'; lf = cap.render(t, ctx)
                ctx['depth_pass'] = None
                layers = [(lb, True), (lf, False)]
            else:
                ctx['depth_pass'] = None
                layers = [(cap.render(t, ctx), False)]
            if ccfg.get('scrim'):                      # soft dark band behind the caption rows for legibility on busy footage
                comb = np.zeros(cH, bool)
                for lay, _ in layers:
                    if lay is not None: comb |= lay[..., 3].max(1) > 20
                ys = np.where(comb)[0]
                if len(ys):
                    pad = max(4, int(0.035 * cH)); band = np.zeros(cH, np.float32)
                    band[max(0, ys.min() - pad):ys.max() + pad] = 1.0
                    band = cv2.GaussianBlur(band.reshape(-1, 1), (0, 0), pad * 0.6).reshape(-1)
                    img = (img.astype(np.float32) * (1 - ccfg['scrim'] * band)[:, None, None]).astype(np.uint8)
            for layer, is_behind in layers:
                if layer is None: continue
                a = layer[..., 3:4].astype(np.float32) / 255.0
                if (ccfg.get('behind_subject') or is_behind) and ctx['mask'] is not None:
                    vis = float((a * (1 - ctx['mask'][..., None])).sum() / max(1e-6, a.sum()))
                    if not (is_behind and not ccfg.get('behind_subject') and vis < dcfg['min_visible']):   # a behind word the subject hides too much stays in front
                        a = a * (1 - ctx['mask'][..., None])
                img = (img.astype(np.float32) * (1 - a) + layer[..., :3][..., ::-1].astype(np.float32) * a).astype(np.uint8)
        for oc in overlays_cfg:
            fn = OVERLAYS.get(oc['kind'])
            if fn: img = fn(img, t, ctx, oc)
        # post layer
        for e in active:
            layer = e.get('layer') or ('pre' if e['fx'] in PRE_DEFAULT else 'post')
            if layer != 'post': continue
            tc = e.get('tc', (e['t0'] + e['t1']) / 2)
            half = (tc - e['t0']) if t < tc else (e['t1'] - tc)
            x = (t - tc) / max(1e-6, half) if half > 1e-6 else 0.0
            k = {'u': (t - e['t0']) / max(1e-6, e['t1'] - e['t0']), 'x': float(np.clip(x, -1, 1)), 't': t - e['t0'], 'span': e['t1'] - e['t0']}
            img, ctx['mask'] = _run(e, img, k, ctx)
        if cW != W or cH != H:
            canvas = np.zeros((H, W, 3), np.uint8); y0 = (H - cH) // 2; canvas[y0:y0 + cH] = img; img = canvas
        enc.stdin.write(np.ascontiguousarray(img).tobytes())
        if progress and f % 60 == 0: print(f'  frame {f}/{nf}', flush=True)
    if reader: reader.close()
    enc.stdin.close(); enc.wait()
    if not keep_tmp: shutil.rmtree(tmp, ignore_errors=True)
    return out_path


def _run(e, img, k, ctx):
    fn = fxm.FX[e['fx']]
    seed = int(ctx['rng'].integers(0, 2 ** 31))
    c1 = dict(ctx); c1['rng'] = np.random.default_rng(seed)
    out = fn(img, k, e.get('params', {}), c1)
    m = ctx['mask']
    if m is not None and e['fx'] in GEOMETRY:
        c2 = dict(ctx); c2['rng'] = np.random.default_rng(seed)
        m3 = cv2.merge([(m * 255).astype(np.uint8)] * 3)
        m = fn(m3, k, e.get('params', {}), c2)[..., 0].astype(np.float32) / 255.0
    return out, m

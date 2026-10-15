"""Clip analysis for the edit engine: scenes, motion energy, brightness, focus point, usable windows.

Works on any video or still image. A still is treated as a clip of unlimited length with zero motion
(the renderer animates it with a pan or punch-in).
"""
import json, os, re, subprocess, hashlib, shutil
from pathlib import Path
import numpy as np
import cv2

IMG_EXT = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff'}
VID_EXT = {'.mp4', '.mov', '.m4v', '.mkv', '.webm', '.avi'}
AN_FPS = 8
AW, AH = 96, 54

# Screen-capture heuristic (16:9 or 9:16, near-zero motion, high edge density, flat colour
# regions), calibrated against the three real acceptance-test folders, none of which is a
# screen capture (edits/_study/corpus.json records the measured numbers these came from).
SCREEN_ASPECT_TOL = 0.06
SCREEN_MOTION_MAX = 2.0
SCREEN_EDGE_MIN = 0.06
SCREEN_FLAT_MIN = 0.45
LARGE_FACE_AREA = 0.08   # selection-plan-2026-10-14.md:37, "area at least 8 percent of frame"


def probe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                        'stream=width,height,r_frame_rate,duration,nb_frames:stream_side_data=rotation:format=duration',
                        '-of', 'json', str(path)], capture_output=True, text=True)
    j = json.loads(r.stdout or '{}')
    st = (j.get('streams') or [{}])[0]
    w, h = int(st.get('width', 0)), int(st.get('height', 0))
    rot = 0
    for sd in st.get('side_data_list', []) or []:
        if 'rotation' in sd: rot = int(sd['rotation'])
    if abs(rot) in (90, 270): w, h = h, w
    num, den = (st.get('r_frame_rate') or '30/1').split('/')
    fps = float(num) / max(1.0, float(den))
    dur = float(st.get('duration') or j.get('format', {}).get('duration') or 0)
    return w, h, fps, dur


VISION = Path(__file__).parent / 'bin' / 'vision'


def vision_bin():
    """Build the Swift Vision helper on first use (macOS). Returns None when unavailable."""
    if VISION.exists():
        return VISION
    src = Path(__file__).parent / 'vision.swift'
    if src.exists() and shutil.which('swiftc'):   # Windows has no `which`; shutil.which is portable
        VISION.parent.mkdir(exist_ok=True)
        if subprocess.run(['swiftc', '-O', str(src), '-o', str(VISION)], capture_output=True).returncode == 0:
            return VISION
    return None


def _focus(frames_bgr, gray_small):
    """Focus point (cx, cy in 0..1), a face flag, the max face count in one frame, and the
    largest single face's area (fraction of frame): Vision faces, then person mask, then saliency."""
    import tempfile
    vb = vision_bin()
    if vb and frames_bgr:
        with tempfile.TemporaryDirectory() as td:
            ps = []
            for i, f in enumerate(frames_bgr):
                p = f'{td}/{i:02d}.png'; cv2.imwrite(p, f); ps.append(p)
            try:
                res = json.loads(subprocess.run([str(vb), 'faces'] + ps, capture_output=True, text=True).stdout or '[]')
            except Exception:
                res = []
            pts = [(c[0], c[1], c[2] * c[3]) for r in res for c in r['faces']]
            face_count = max((len(r.get('faces', [])) for r in res), default=0)
            face_area = max((c[2] * c[3] for r in res for c in r['faces']), default=0.0)
            if pts:
                a = np.array(pts); w = a[:, 2].sum()
                return [float((a[:, 0] * a[:, 2]).sum() / w), float((a[:, 1] * a[:, 2]).sum() / w)], True, face_count, float(face_area)
            subprocess.run([str(vb), 'mask', td, td + '/m'], capture_output=True)
            cs = []
            for i in range(len(ps)):
                mp = f'{td}/m/{i:02d}.png'
                if os.path.exists(mp):
                    m = cv2.imread(mp, 0)
                    if m is not None and (m > 128).mean() > 0.02:
                        ys, xs = np.where(m > 128)
                        cs.append((xs.mean() / m.shape[1], np.percentile(ys, 15) / m.shape[0]))   # upper body, near the head
            if cs:
                c = np.mean(cs, 0); return [float(c[0]), float(c[1])], True, 0, 0.0
    # saliency fallback: centroid of local contrast, lightly biased to the centre
    acc = np.zeros((36, 64), np.float32)
    for f in frames_bgr:
        g = cv2.cvtColor(cv2.resize(f, (64, 36)), cv2.COLOR_BGR2GRAY).astype(np.float32)
        acc += np.abs(g - cv2.GaussianBlur(g, (0, 0), 4))
    acc = cv2.GaussianBlur(acc, (0, 0), 3) + 1e-3
    yy, xx = np.mgrid[0:36, 0:64]
    acc *= np.exp(-(((xx - 32) / 40) ** 2 + ((yy - 18) / 24) ** 2))
    return [float((acc * xx).sum() / acc.sum() / 64), float((acc * yy).sum() / acc.sum() / 36)], False, 0, 0.0


def _edge_and_flat(frames_bgr):
    """Mean edge-pixel fraction (Canny) and mean flat-block fraction (low local variance),
    the two screen-capture signals beyond aspect ratio and motion."""
    if not frames_bgr:
        return 0.0, 0.0
    edge_fracs, flat_fracs = [], []
    for f in frames_bgr:
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(g, 50, 150)
        edge_fracs.append(float((edges > 0).mean()))
        h, w = g.shape
        bh, bw = max(1, h // 16), max(1, w // 16)
        gc = g[:bh * 16, :bw * 16].astype(np.float32)
        blocks = gc.reshape(16, bh, 16, bw)
        var = blocks.var(axis=(1, 3))
        flat_fracs.append(float((var < 25.0).mean()))
    return float(np.mean(edge_fracs)), float(np.mean(flat_fracs))


def _has_audio_stream(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index',
                        '-of', 'csv=p=0', str(path)], capture_output=True, text=True)
    return bool(r.stdout.strip())


def _speech_present(path, dur):
    """Non-silent audio ratio via ffmpeg silencedetect: a stand-in for 'has spoken or voiced
    audio' (selection-plan-2026-10-14.md:37 names this as an acceptable method), not a speech
    vs. music classifier. No audio stream, or no duration, is always False."""
    if dur <= 0 or not _has_audio_stream(path):
        return False
    r = subprocess.run(['ffmpeg', '-v', 'info', '-i', str(path), '-af', 'silencedetect=noise=-30dB:d=0.2',
                        '-f', 'null', '-'], capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', r.stderr)]
    ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', r.stderr)]
    silence = 0.0
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else dur
        silence += max(0.0, e - s)
    non_silent_ratio = 1.0 - min(1.0, silence / dur)
    return bool(non_silent_ratio > 0.1)


def _appearance_descriptor(item):
    """A crude colour descriptor (HSV histogram) of the clip's focus region, for the
    distinct-subject clustering below. None when the region can't be sampled."""
    path = Path(item['path'])
    fx, fy = item['focus']
    if item['kind'] == 'image':
        im = cv2.imread(str(path))
    else:
        t = item['dur'] / 2
        o = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', str(path), '-frames:v', '1',
                            '-vf', 'scale=160:-2', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
        im = cv2.imdecode(np.frombuffer(o, np.uint8), cv2.IMREAD_COLOR) if o else None
    if im is None or im.size == 0:
        return None
    h, w = im.shape[:2]
    cx, cy = int(fx * w), int(fy * h)
    r = max(8, min(w, h) // 6)
    x0, x1 = max(0, cx - r), min(w, cx + r)
    y0, y1 = max(0, cy - r), min(h, cy + r)
    crop = im[y0:y1, x0:x1]
    if crop.size == 0:
        return None
    hist = cv2.calcHist([cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)], [0, 1], None, [8, 8], [0, 180, 0, 256])
    return cv2.normalize(hist, hist).flatten()


def distinct_subjects(items, thresh=0.6):
    """Cluster a folder's analysed clips into distinct subjects by focus-region colour
    histogram correlation (greedy single-link). Returns the subject count; 0 if nothing
    could be sampled (an all-stills or all-screen-capture folder)."""
    descs = [d for d in (_appearance_descriptor(it) for it in items) if d is not None]
    groups = []
    for d in descs:
        placed = False
        for g in groups:
            if cv2.compareHist(g[0], d, cv2.HISTCMP_CORREL) > thresh:
                g.append(d); placed = True; break
        if not placed:
            groups.append([d])
    return len(groups)


def analyse(path, cache_dir=None):
    path = Path(path)
    if path.is_dir():
        return analyse_folder(path, cache_dir)
    key = hashlib.md5(f'{path}{path.stat().st_mtime}{path.stat().st_size}'.encode()).hexdigest()[:10]
    cpath = Path(cache_dir) / f'{path.stem}.{key}.json' if cache_dir else None
    if cpath and cpath.exists():
        return json.load(open(cpath))
    ext = path.suffix.lower()
    if ext in IMG_EXT:
        im = cv2.imread(str(path))
        h, w = im.shape[:2]
        foc, face, face_count, face_area = _focus([im], None)
        edge_density, flat_frac = _edge_and_flat([im])
        r = {'path': str(path), 'kind': 'image', 'w': w, 'h': h, 'fps': 0, 'dur': 3600.0, 'scenes': [],
             'motion': [0.0], 'bright': [float(im.mean())], 'sat': [float(cv2.cvtColor(im, cv2.COLOR_BGR2HSV)[..., 1].mean())],
             'focus': foc, 'face': face, 'step': 1.0, 'mean_motion': 0.0, 'mean_bright': float(im.mean()),
             'sharp': float(cv2.Laplacian(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()),
             'face_count': face_count, 'face_area': round(face_area, 4), 'speech_present': False,
             'screen_capture': _is_screen_capture(w, h, 0.0, edge_density, flat_frac)}
    else:
        w, h, fps, dur = probe(path)
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-vf', f'fps={AN_FPS},scale={AW}:{AH}',
                              '-pix_fmt', 'bgr24', '-f', 'rawvideo', '-'], capture_output=True).stdout
        a = np.frombuffer(raw, np.uint8).reshape(-1, AH, AW, 3).astype(np.float32)
        n = len(a)
        if n == 0:
            raise RuntimeError(f'cannot decode {path}')
        g = a.mean(3)
        d = np.r_[0, np.abs(np.diff(g, axis=0)).mean((1, 2))] if n > 1 else np.zeros(1)
        # scene cuts: a spike well above the clip's own typical motion
        med = np.median(d) + 1e-3
        scenes = [round(i / AN_FPS, 3) for i in range(1, n) if d[i] > max(18.0, 6 * med) and d[i] >= d[max(0, i - 2):i + 3].max()]
        mo = d.copy()
        for i in range(1, n):
            if d[i] > max(18.0, 6 * med): mo[i] = mo[i - 1]   # a cut is not motion
        # sample frames for focus and sharpness
        idxs = np.linspace(0, max(dur - 0.1, 0), 5)
        fr = []
        for t in idxs:
            o = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', str(path), '-frames:v', '1',
                                '-vf', 'scale=480:-2', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
            im = cv2.imdecode(np.frombuffer(o, np.uint8), cv2.IMREAD_COLOR) if o else None
            if im is not None: fr.append(im)
        foc, face, face_count, face_area = _focus(fr, None) if fr else ([0.5, 0.5], False, 0, 0.0)
        edge_density, flat_frac = _edge_and_flat(fr)
        sharp = float(np.mean([cv2.Laplacian(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var() for f in fr])) if fr else 0.0
        sat = [float(cv2.cvtColor(x.astype(np.uint8), cv2.COLOR_BGR2HSV)[..., 1].mean()) for x in a[::2]]
        mean_motion = float(mo.mean())
        r = {'path': str(path), 'kind': 'video', 'w': w, 'h': h, 'fps': fps, 'dur': round(dur or n / AN_FPS, 3),
             'scenes': scenes, 'motion': [round(float(x), 3) for x in mo], 'bright': [round(float(x), 2) for x in g.mean((1, 2))],
             'sat': [round(x, 1) for x in sat], 'focus': foc, 'face': face, 'step': 1.0 / AN_FPS,
             'mean_motion': round(mean_motion, 3), 'mean_bright': round(float(g.mean()), 2), 'sharp': round(sharp, 1),
             'face_count': face_count, 'face_area': round(face_area, 4),
             'speech_present': _speech_present(path, dur),
             'screen_capture': _is_screen_capture(w, h, mean_motion, edge_density, flat_frac)}
    mp = Path(path).with_suffix('.mask.mp4')
    r['mask'] = str(mp) if mp.exists() else None
    if cpath:
        os.makedirs(cache_dir, exist_ok=True)
        json.dump(r, open(cpath, 'w'))
    return r


def _is_screen_capture(w, h, mean_motion, edge_density, flat_frac):
    ar = w / h if h else 0.0
    is_screen_ar = abs(ar - 16 / 9) < SCREEN_ASPECT_TOL or abs(ar - 9 / 16) < SCREEN_ASPECT_TOL
    return bool(is_screen_ar and mean_motion < SCREEN_MOTION_MAX and edge_density > SCREEN_EDGE_MIN and flat_frac > SCREEN_FLAT_MIN)


def analyse_folder(folder, cache_dir=None):
    folder = Path(folder)
    items = []
    for p in sorted(folder.iterdir()):
        if p.name.startswith('.') or '.mask.' in p.name: continue
        if p.suffix.lower() in IMG_EXT | VID_EXT:
            try:
                items.append(analyse(p, cache_dir))
            except Exception as e:
                print('skip', p.name, e)
    return items


def windows(clip, dur_src, margin=0.12):
    """Candidate source start times (step 0.25 s) whose window [s, s+dur_src] crosses no scene cut."""
    if clip['kind'] == 'image':
        return [(0.0, 0.0, 0.0)]
    cuts = [0.0] + list(clip['scenes']) + [clip['dur']]
    out = []
    mo = np.array(clip['motion']); st = clip['step']
    for a, b in zip(cuts[:-1], cuts[1:]):
        lo, hi = a + (margin if a > 0 else 0), b - (margin if b < clip['dur'] else 0)
        t = lo
        while t + dur_src <= hi + 1e-6:
            i0, i1 = int(t / st), max(int((t + dur_src) / st), int(t / st) + 1)
            m = float(mo[i0:i1].mean()) if len(mo[i0:i1]) else 0.0
            out.append((round(t, 3), m, float(np.mean(clip['bright'][i0:i1])) if clip['bright'][i0:i1] else 0.0))
            t += 0.25
    return out


if __name__ == '__main__':
    import sys
    for c in analyse_folder(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None):
        print(Path(c['path']).name, c['w'], c['h'], c['dur'], 'motion', c['mean_motion'], 'scenes', c['scenes'], 'focus', [round(x, 2) for x in c['focus']], 'face', c['face'])

"""Measure how well the rendered cuts land on the beats, independently of the planner.

1. Cuts are detected in the rendered video from frame differences.
2. The beat grid is re-detected from the rendered audio track (a second, independent analysis of what a viewer hears).
3. Each detected cut is compared with the nearest beat and the nearest eighth note, in milliseconds.
"""
import subprocess, tempfile, json
from pathlib import Path
import numpy as np
import audio


def probe(video):
    """(width, height, fps, duration_s) via ffprobe. Shared with gate.py so both measure a
    rendered file's frame grid the same way (plan.md Stage 3 names check.py as shared helpers)."""
    out = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
         '-show_entries', 'stream=width,height,r_frame_rate', '-show_entries', 'format=duration',
         '-of', 'json', str(video)],
        capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    s = j['streams'][0]
    num, den = s['r_frame_rate'].split('/')
    fps = float(num) / float(den)
    return int(s['width']), int(s['height']), fps, float(j['format']['duration'])


def extract_gray_frames(video, fps=None, w=64, h=36):
    """Downscaled greyscale frames as a (N, h, w) float32 array, values 0-255. `fps=None` keeps
    the source's native frame rate (used by gate.py's flash check, which must not resample)."""
    vf = f'fps={fps},scale={w}:{h}' if fps else f'scale={w}:{h}'
    raw = subprocess.run(
        ['ffmpeg', '-v', 'error', '-i', str(video), '-vf', vf, '-pix_fmt', 'gray', '-f', 'rawvideo', '-'],
        capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)


def detect_cuts(video, fps=30, thr_mult=5.0):
    a = extract_gray_frames(video, fps=fps)
    d = np.abs(np.diff(a, axis=0)).mean((1, 2))
    med = np.median(d) + 1e-3
    thr = max(10.0, thr_mult * med)
    cuts = [(i + 1) / fps for i in range(len(d)) if d[i] > thr and d[i] >= d[max(0, i - 2):i + 3].max()]
    return cuts, d


def nearest(t, grid):
    i = int(np.argmin(np.abs(grid - t))); return grid[i]


def check(video, edl):
    fps = edl['fps']
    P = edl['music']['beat_period']
    planned = [s['t0'] for s in edl['shots'][1:]]
    # independent beat grid from the rendered audio
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / 'a.wav'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(video), '-vn', '-ac', '1', '-ar', '22050', str(wav)])
        song = audio.analyse(wav)
    beats = np.array(song['beats']); eighths = np.sort(np.r_[beats, beats + song['beat_period'] / 2])
    cuts, d = detect_cuts(video, fps)
    meas = []
    for t in planned:
        c = [x for x in cuts if abs(x - t) <= 3.5 / fps]
        if c: meas.append(min(c, key=lambda x: abs(x - t)))
    off_beat = [(m - nearest(m, beats)) * 1000 for m in meas]
    off_eighth = [(m - nearest(m, eighths)) * 1000 for m in meas]
    plan_off = [(t - nearest(t, np.arange(0, edl['duration'] + P, P / 4))) * 1000 for t in planned]
    sixteenths = np.sort(np.r_[beats, beats + song['beat_period'] / 4, beats + song['beat_period'] / 2, beats + 3 * song['beat_period'] / 4])
    off_16 = [(m - nearest(m, sixteenths)) * 1000 for m in meas]
    # beats from the planner's own grid versus the independent grid: systematic offset of the analysis itself
    sys_off = [((b * P) - nearest(b * P, beats)) * 1000 for b in range(0, edl['n_beats'], 4)]
    # does each planned beat sit on a real attack in the music? Local search for the sharpest rise within +-50 ms of every beat.
    support = None
    try:
        y = audio.load(edl['music']['path'])
        sr = audio.SR; k = int(0.004 * sr)
        sm = np.convolve(np.abs(y), np.ones(k) / k, 'same')
        d = np.maximum(0, np.diff(sm, prepend=sm[0]))
        offs_a = []
        for b_ in range(0, edl['n_beats']):
            c = int((edl['music']['start'] + b_ * P) * sr); w = int(0.05 * sr)
            if c - w < 0 or c + w >= len(d): continue
            seg = d[c - w:c + w]
            floor = np.median(d[max(0, c - 4 * w):c + 4 * w]) + 1e-9
            if seg.max() > 6 * floor:
                offs_a.append((int(np.argmax(seg)) - w) / sr * 1000)
        if offs_a:
            oa = np.array(offs_a)
            support = {'beats_with_a_clear_attack': round(len(oa) / edl['n_beats'], 2), 'median_offset_ms': round(float(np.median(oa)), 1),
                       'mean_abs_offset_ms': round(float(np.mean(np.abs(oa))), 1), 'share_within_25ms': round(float(np.mean(np.abs(oa) <= 25)), 2)}
    except Exception as ex:
        support = {'error': str(ex)}
    truth = None
    tp = Path(str(edl['music']['path']).rsplit('.', 1)[0] + '.truth.json')
    if tp.exists():
        tj = json.load(open(tp)); Pt = 60.0 / tj['bpm']
        g = np.arange(0, edl['duration'] + 2 * Pt, Pt / 4) - (edl['music']['start'] - tj['first_beat']) % Pt
        g = np.sort(np.r_[g, g + Pt / 4 * 0])
        phase = (edl['music']['start'] - tj['first_beat']) % Pt                  # timeline time of the first true beat is Pt - phase
        g = np.arange(-phase, edl['duration'] + Pt, Pt / 4)
        tm_off = [(m - nearest(m, g)) * 1000 for m in meas]
        tp_off = [(t - nearest(t, g)) * 1000 for t in planned]
        truth = {'true_bpm': tj['bpm'], 'video_cut_offset_vs_true_sixteenth_grid_ms_mean_abs': round(float(np.mean(np.abs(tm_off))), 2),
                 'planned_cut_offset_vs_true_sixteenth_grid_ms_mean_abs': round(float(np.mean(np.abs(tp_off))), 2),
                 'video_cut_offset_vs_true_sixteenth_grid_ms_max_abs': round(float(np.max(np.abs(tm_off))), 2)}
    res = {
        'bpm_planned': edl['music']['bpm'], 'bpm_rendered_audio': song['bpm'], 'n_planned_cuts': len(planned), 'n_cuts_detected_in_video': len(meas),
        'planned_cut_offset_from_sixteenth_grid_ms_mean_abs': round(float(np.mean(np.abs(plan_off))), 2) if plan_off else None,
        'video_cut_offset_from_nearest_sixteenth_ms_mean_abs': round(float(np.mean(np.abs(off_16))), 2) if off_16 else None,
        'share_of_cuts_within_one_frame_of_a_sixteenth': round(float(np.mean(np.abs(off_16) <= 1000 / fps)), 3) if off_16 else None,
        'share_of_cuts_on_a_beat_or_eighth_within_one_frame': round(float(np.mean(np.abs(off_eighth) <= 1000 / fps)), 3) if off_eighth else None,
        'video_cut_offset_from_nearest_eighth_ms_mean_abs': round(float(np.mean(np.abs(off_eighth))), 2) if off_eighth else None,
        'video_cut_offset_from_nearest_eighth_ms_median_abs': round(float(np.median(np.abs(off_eighth))), 2) if off_eighth else None,
        'video_cut_offset_from_nearest_beat_ms_mean_abs': round(float(np.mean(np.abs(off_beat))), 2) if off_beat else None,
        'video_cut_offset_signed_mean_ms': round(float(np.mean(off_eighth)), 2) if off_eighth else None,
        'frame_ms': round(1000 / fps, 2),
        'planned_beats_vs_local_attack_in_music': support,
        'vs_synthesised_ground_truth': truth,
        'cuts': [{'planned': round(p, 3), 'measured': round(m, 3), 'off_sixteenth_ms': round(o, 1)} for p, m, o in zip(planned, meas, off_16)],
    }
    return res


if __name__ == '__main__':
    import sys
    edl = json.load(open(sys.argv[2])); print(json.dumps({k: v for k, v in check(sys.argv[1], edl).items() if k != 'cuts'}, indent=1))

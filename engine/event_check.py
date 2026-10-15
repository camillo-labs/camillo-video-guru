"""Beat alignment of planned effect events (not only cuts): start time of every event in an edl.json against the beat grid
re-detected from the rendered audio (independent of the planner), in milliseconds to the nearest eighth note.
usage: event_check.py edit.mp4 edl.json"""
import json, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
import audio


def event_alignment(video, edl, fx_names=None):
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / 'a.wav'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(video), '-vn', '-ac', '1', '-ar', '22050', str(wav)])
        song = audio.analyse(wav)
    b = np.array(song['beats']); g = np.sort(np.r_[b, b + song['beat_period'] / 2])
    fps = edl['fps']; out = {}
    for e in edl['events']:
        if fx_names and e['fx'] not in fx_names: continue
        t = round(e['t0'] * fps) / fps                       # events start on a frame
        out.setdefault(e['fx'], []).append((t - g[int(np.argmin(np.abs(g - t)))]) * 1000)
    allv = [v for l in out.values() for v in l]
    return {'per_fx_mean_abs_ms': {k: round(float(np.mean(np.abs(v))), 1) for k, v in out.items()},
            'all_events_mean_abs_ms': round(float(np.mean(np.abs(allv))), 1) if allv else None, 'n_events': len(allv), 'frame_ms': round(1000 / fps, 1)}


if __name__ == '__main__':
    print(json.dumps(event_alignment(sys.argv[1], json.load(open(sys.argv[2]))), indent=1))

"""Audio shaping learned from the bw-flash-vo walkthrough reel (re-measured 13 Oct 2026, see edits/lessons/reels-2026-10-13.md).

All three options are off unless a style has an "audio_shape" block, so every existing style renders exactly as before.

    "audio_shape": {
      "intro_gate":   {"rate_hz": 3.3, "duty": 0.68, "depth_db": -30, "until_s": 2.2},
      "vo_low_duck":  {"cut_hz": 150, "depth_db": -20, "attack": 0.12, "rise": 1.8, "pad": 0.1},
      "hit_gaps":     {"kinds": ["impact"], "dur": 0.1, "lead": 0.02, "min_gain": 0.4}
    }

intro_gate   Chops the music with a regular tremolo gate while the flash intro plays (the reel's bass runs 0.2 s on, 0.1 s off for 2.2 s,
             each off slot sits on a white frame). until_s defaults to the style's intro_beats.
vo_low_duck  Pulls the music's low band (below cut_hz) down by depth_db for the span of the voiceover and lets it swell back over `rise`
             seconds before the speech ends, so the voice sits in a clean mix and the low end returns as a build into the drop. The reel's low band is
             about 24 dB lower under the voice (2.4 to 5.1 s), then climbs back over 5.2 to 6.9 s. Mids are untouched. Needs a voiceover.
hit_gaps     Mutes the music for `dur` seconds, ending `lead` seconds before each sfx event of the listed kinds, so the hit lands out of silence
             (the reel dips 12 dB or more for 60 to 150 ms before the hits at 9.8 s, 12.3 s and the end).
"""
import subprocess

import numpy as np

SR = 44100


def _decode(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-vn', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def _lowpass(x, fc):
    """Zero-phase 4th-order-style low-pass by FFT (no scipy). x is (n, ch)."""
    n = len(x)
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(n, 1 / SR)
    H = 1.0 / (1.0 + (f / fc) ** 4)
    return np.fft.irfft(X * H[:, None], n, axis=0)


def gate_curve(n, t0, cfg, sr=SR):
    """Linear gain per sample for the intro gate. t0 is the song time of sample 0 relative to the edit start (0 for the edit window)."""
    rate, duty = cfg.get('rate_hz', 3.3), cfg.get('duty', 0.68)
    floor = 10 ** (cfg.get('depth_db', -30) / 20)
    until = cfg['until_s']
    t = np.arange(n) / sr + t0
    phase = (t * rate) % 1.0
    g = np.where(phase < duty, 1.0, floor)
    ramp = max(1, int(cfg.get('ramp_s', 0.005) * sr))
    g = np.convolve(g, np.ones(ramp) / ramp, 'same')                 # soften the edges so the gate does not click
    return np.where(t < until, g, 1.0)


def duck_curve(n, t0, spans, cfg, sr=SR):
    """Linear gain for the low band: depth_db inside each (a, b) span, ramping in over `attack` and back up over `rise` seconds before b."""
    depth = cfg.get('depth_db', -20)
    att, rise, pad = cfg.get('attack', 0.12), cfg.get('rise', 1.8), cfg.get('pad', 0.1)
    t = np.arange(n) / sr + t0
    db = np.zeros(n)
    for a, b in spans:
        a -= pad
        rs = max(a + att, b - rise)
        d = np.interp(t, [a, a + att, rs, b], [0, depth, depth, 0], left=0, right=0)
        db = np.minimum(db, d)
    return 10 ** (db / 20)


def vo_spans(edl, cfg):
    if cfg.get('spans'):
        return [tuple(s) for s in cfg['spans']]
    ws = edl.get('words') or []
    if not edl.get('voiceover') or not ws:
        return []
    return [(min(w['t0'] for w in ws), max(w['t1'] for w in ws))]


def add_hit_gaps(edl, cfg):
    """Append 'gap' sfx events (render.mix_audio mutes the music for them) ahead of the listed sfx kinds. Returns the number added."""
    kinds, dur, lead, mg = set(cfg.get('kinds', ['impact'])), cfg.get('dur', 0.1), cfg.get('lead', 0.02), cfg.get('min_gain', 0.4)
    new = []
    for e in edl.get('sfx', []):
        if e.get('kind') in kinds and e.get('gain', 0.5) >= mg and not e.get('end_at_t'):
            t = e['t'] + e.get('offset', 0.0) - lead - dur
            if t >= 0 and not any(abs(g['t'] - t) < 0.02 for g in edl['sfx'] if g.get('kind') == 'gap'):
                new.append({'kind': 'gap', 't': round(t, 4), 'dur': dur, 'gain': 1, 'at': 'hit_gap'})
    edl['sfx'] = sorted(edl['sfx'] + new, key=lambda e: e['t'])
    return len(new)


def plan(edl, style):
    """Edl-level part: hit gaps. Safe to call once after planning, the result is saved in edl.json. Returns what was done."""
    import copy
    cfg = copy.deepcopy(style.get('audio_shape'))
    if not cfg:
        return {}
    done = {}
    if cfg.get('intro_gate') and 'until_s' not in cfg['intro_gate']:
        cfg['intro_gate']['until_s'] = round(style.get('structure', {}).get('intro_beats', 4) * edl['music']['beat_period'], 3)
    if cfg.get('hit_gaps'):
        done['hit_gaps'] = add_hit_gaps(edl, cfg['hit_gaps'])
    edl['audio_shape'] = cfg
    return done


def shape_music(song_path, edl, out_wav):
    """Audio-level part: writes a full-length copy of the song with the intro gate and the voiceover low duck applied inside the edit's window.
    Returns the path to render from, or the original song_path when the edl has nothing for it (so unchanged styles never touch the file)."""
    cfg = edl.get('audio_shape') or {}
    gate, duck = cfg.get('intro_gate'), cfg.get('vo_low_duck')
    spans = vo_spans(edl, duck) if duck else []
    if not gate and not (duck and spans):
        return song_path
    import soundfile as sf
    m = _decode(song_path)
    start, D = edl['music']['start'], edl['duration']
    i0, i1 = int(start * SR), min(len(m), int((start + D + 0.5) * SR))
    x = m[i0:i1].astype(np.float64)
    if duck and spans:
        low = _lowpass(x, duck.get('cut_hz', 150))
        g = duck_curve(len(x), 0.0, spans, duck)
        x = (x - low) + low * g[:, None]
    if gate:
        gc = dict(gate)
        if 'until_s' not in gc:
            gc['until_s'] = 4 * edl['music'].get('beat_period', 0.5)
        x = x * gate_curve(len(x), 0.0, gc)[:, None]
    m[i0:i1] = x.astype(np.float32)
    sf.write(str(out_wav), m, SR, subtype='FLOAT')
    return str(out_wav)

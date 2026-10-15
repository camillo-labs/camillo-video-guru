"""Song analysis for the edit engine: tempo, beat grid, downbeats, energy, sections, drops, phrases, onsets.

Everything the planner needs to land cuts and moves on the beats of a NEW song.
Uses librosa for onset strength and tracking, then fits a constant beat grid, which is what
almost every pop, hip-hop and EDM track needs. Falls back to the tracked beats if the tempo drifts.
"""
import json, subprocess
import numpy as np
import librosa

SR = 22050
HOP = 256


def load(path, sr=SR):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-vn', '-ac', '1', '-ar', str(sr),
                          '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def _tempo(env, sr, hop, lo=70.0, hi=175.0, prior=120.0):
    """Autocorrelation tempo with a log-normal prior, octave errors resolved towards the prior."""
    fps = sr / hop
    env = env - env.mean()
    ac = np.correlate(env, env, 'full')[len(env) - 1:]
    ac /= (ac[0] + 1e-9)
    lags = np.arange(len(ac)) / fps
    best, best_s = prior, -1
    for bpm in np.arange(lo, hi, 0.25):
        lag = 60.0 / bpm
        i = lag * fps
        s = 0.0
        for k, wgt in ((1, 1.0), (2, 0.8), (4, 0.6)):   # beat, bar halves, bar
            j = int(round(i * k))
            if j < len(ac) - 2:
                s += wgt * ac[j - 1:j + 2].max()
        s *= np.exp(-0.5 * (np.log2(bpm / prior) / 0.35) ** 2)
        if s > best_s:
            best, best_s = bpm, s
    return best


def _fit_grid(env, fps, bpm, dur):
    """Find period and phase of a constant grid that maximises onset strength at the beats."""
    best = (None, None, -1)
    for scale in np.linspace(0.985, 1.015, 31):
        P = 60.0 / (bpm * scale)
        for ph in np.arange(0, P, 0.005):
            ts = np.arange(ph, dur, P)
            idx = np.clip((ts * fps).round().astype(int), 0, len(env) - 1)
            sc = env[idx].mean()
            if sc > best[2]:
                best = (P, ph, sc)
    return best


def _refine_phase(y, P, ph, dur, sr=SR):
    """Jointly refine period and phase so beats sit on the physical attack of the drums (about 2 ms resolution),
    not on the smoothed onset peak, which lags the transient by 20 to 40 ms. Returns (P, phase)."""
    from scipy.ndimage import maximum_filter1d
    k = int(0.004 * sr)
    sm = np.convolve(np.abs(y), np.ones(k) / k, 'same')
    d = np.maximum(0, np.diff(sm, prepend=sm[0]))
    dm = maximum_filter1d(d, size=int(0.012 * sr))
    best = (-1, P, 0.0)
    for sc_ in np.linspace(0.996, 1.004, 41):
        Pc = P * sc_
        for off in np.arange(-0.07, 0.0701, 0.002):
            ts = np.arange(ph + off, dur - 0.1, Pc)
            ts = ts[ts > 0.05]
            idx = (ts * sr).astype(int)
            idx = idx[idx < len(dm)]
            sc = dm[idx].mean() if len(idx) else 0
            if sc > best[0]: best = (sc, Pc, off)
    _, P2, bo = best
    ph2 = ph + bo
    # half-beat ambiguity: eighth-note hats and bass fit both phases, so let the kick (below 150 Hz) decide
    X = np.fft.rfft(y); fr = np.fft.rfftfreq(len(y), 1 / sr)
    low = np.fft.irfft(X * (fr < 150), len(y))
    sl = np.convolve(np.abs(low), np.ones(int(0.01 * sr)) / int(0.01 * sr), 'same')
    dl = maximum_filter1d(np.maximum(0, np.diff(sl, prepend=sl[0])), size=int(0.03 * sr))
    def sc_low(p0):
        ts = np.arange(p0, dur - 0.1, P2); idx = (ts * sr).astype(int); idx = idx[(idx > 0) & (idx < len(dl))]
        return dl[idx].mean() if len(idx) else 0
    if sc_low(ph2 + P2 / 2) > 1.25 * sc_low(ph2):
        ph2 += P2 / 2
    while ph2 < 0: ph2 += P2
    while ph2 >= P2: ph2 -= P2
    return P2, ph2


def _local_scale(x, win):
    """Scale each beat by the 90th percentile of its own +/- win neighbourhood, not one
    global percentile, so a drop late in a track is not swamped by a louder passage
    elsewhere and a quiet track does not read as all-drop."""
    n = len(x)
    if n == 0:
        return x
    out = np.empty(n)
    for i in range(n):
        lo, hi = max(0, i - win), min(n, i + win + 1)
        m = np.percentile(x[lo:hi], 90)
        out[i] = x[i] / (m + 1e-9)
    return out


def analyse(path, cache=None):
    y = load(path)
    dur = len(y) / SR
    env = librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP)
    fps = SR / HOP
    bpm0 = _tempo(env, SR, HOP)
    # phase from the kick and snare bands (hats on the off-beat would otherwise win), then refined to the attack
    S0 = np.abs(librosa.stft(y, n_fft=2048, hop_length=HOP))
    fr0 = librosa.fft_frequencies(sr=SR, n_fft=2048)
    lm = np.log1p(S0[(fr0 >= 30) & (fr0 < 2500)].sum(0) * 0.1)
    env_lm = np.maximum(0, np.diff(lm, prepend=lm[0]))
    P, ph, _ = _fit_grid(0.7 * env_lm / (env_lm.max() + 1e-9) + 0.3 * env / (env.max() + 1e-9), fps, bpm0, dur)
    P, ph = _refine_phase(y, P, ph, dur)
    # grid starts at the first beat at or after zero, extended back so beat 0 is the first full beat
    beats = np.arange(ph, dur, P)
    bpm = 60.0 / P

    # low-band onset (kick) for downbeats and kick/snare split
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=HOP))
    fr = librosa.fft_frequencies(sr=SR, n_fft=2048)
    def band_env(lo, hi):
        b = np.log1p(S[(fr >= lo) & (fr < hi)].sum(0) * 0.1)
        d = np.maximum(0, np.diff(b, prepend=b[0]))
        return d
    low = band_env(30, 150); mid = band_env(150, 2500); high = band_env(4000, 10000)
    def at(e, t, w=2):
        i = int(round(t * fps)); return float(e[max(0, i - w):i + w + 1].max()) if 0 <= i < len(e) else 0.0
    # downbeat: phase with most kick plus overall energy over the first 16 bars
    sc = np.zeros(4)
    for k, t in enumerate(beats):
        sc[k % 4] += at(low, t) * 1.0 + at(env, t) * 0.3
    # RMS energy at each beat
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=HOP)[0]
    def rms_at(t0, t1):
        a, b = int(t0 * fps), max(int(t1 * fps), int(t0 * fps) + 1)
        return float(rms[a:b].mean()) if a < len(rms) else 0.0
    be = np.array([rms_at(t, t + P) for t in beats])
    if len(be):
        be = be / (np.percentile(be, 95) + 1e-9)
    # choose downbeat phase: prefer kick, tie-break with energy jumps at bar starts
    dphase = int(np.argmax(sc))
    downbeats = [float(t) for k, t in enumerate(beats) if k % 4 == dphase]
    bar_idx = np.array([(k - dphase) // 4 for k in range(len(beats))])

    # sections: smoothed energy over 8 beats, drops are big upward jumps at bar boundaries
    sm = np.convolve(be, np.ones(8) / 8, 'same') if len(be) else be
    nxt = np.array([be[k:k + 8].mean() if k + 8 <= len(be) else be[k:].mean() for k in range(len(be))]) if len(be) else be
    prv = np.array([be[max(0, k - 8):k].mean() if k > 0 else be[0] for k in range(len(be))]) if len(be) else be
    jump = nxt - prv
    # drops: the kick and bass (below 150 Hz) returning at a bar start after a quieter stretch
    X = np.fft.rfft(y); frq = np.fft.rfftfreq(len(y), 1 / SR)
    lowsig = np.fft.irfft(X * (frq < 150), len(y))
    bl = np.array([np.sqrt((lowsig[int(t * SR):int((t + P) * SR)] ** 2).mean() + 1e-12) for t in beats])
    bl = _local_scale(bl, 16) if len(bl) else bl
    cand = []
    for k in range(4, len(bl) - 3):
        if (k - dphase) % 4 == 0:
            j = bl[k:k + 4].mean() - bl[max(0, k - 4):k].mean()
            if j > 0.3 and bl[k:k + 8].mean() > 0.5:
                cand.append((k, j))
    drops = []
    for k, j in sorted(cand, key=lambda c: -c[1]):
        if all(abs(beats[k] - d) > 16 * P for d in drops):
            drops.append(float(beats[k]))
    drops.sort()
    roles = []
    q_lo, q_hi = np.percentile(be, 30), np.percentile(be, 65)
    for k in range(len(be)):
        if sm[k] >= q_hi: r = 'high'
        elif sm[k] <= q_lo: r = 'low'
        else: r = 'mid'
        roles.append(r)
    # phrase boundaries: every 8 beats (2 bars) from the first downbeat, plus drops
    phrases = [float(beats[k]) for k in range(len(beats)) if (k - dphase) % 8 == 0 and k >= dphase]
    for d in drops:
        if all(abs(d - p) > 0.5 * P for p in phrases): phrases.append(d)
    phrases.sort()

    # onsets with band tags
    pk = librosa.onset.onset_detect(onset_envelope=env, sr=SR, hop_length=HOP, backtrack=False, units='frames',
                                    delta=0.07, wait=2)
    onsets = []
    mx = env.max() + 1e-9
    for f in pk:
        t = f / fps
        l, m, h = at(low, t), at(mid, t), at(high, t)
        band = 'kick' if l >= max(m, h) * 0.9 and l > 0.15 else ('snare' if m > h else 'hat')
        onsets.append({'t': round(float(t), 3), 's': round(float(env[f] / mx), 3), 'band': band})
    out = {
        'path': str(path), 'duration': round(dur, 3), 'bpm': round(bpm, 2), 'beat_period': round(P, 5),
        'first_beat': round(float(beats[0]), 4) if len(beats) else 0.0, 'downbeat_phase': dphase,
        'beats': [round(float(b), 4) for b in beats], 'downbeats': [round(d, 4) for d in downbeats],
        'beat_energy': [round(float(x), 3) for x in be], 'roles': roles,
        'drops': [round(d, 3) for d in drops], 'phrases': [round(p, 3) for p in phrases], 'onsets': onsets,
    }
    if cache:
        json.dump(out, open(cache, 'w'))
    return out


if __name__ == '__main__':
    import sys
    r = analyse(sys.argv[1])
    print({k: v for k, v in r.items() if k not in ('beats', 'beat_energy', 'roles', 'onsets', 'downbeats')})
    print('first beats', r['beats'][:6], 'downbeats', r['downbeats'][:4], 'n onsets', len(r['onsets']))

"""Synthesised sound effects for edit styles: whoosh, impact, riser, click, tick, hiss, swell. All generated, no samples."""
import numpy as np

SR = 44100
SFX = {}


def sfx(name):
    def deco(f):
        SFX[name] = f
        return f
    return deco


def _lp(x, fc):
    X = np.fft.rfft(x); fr = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / (1 + (fr / fc) ** 2), len(x))


def _hp(x, fc):
    return x - _lp(x, fc)


@sfx('whoosh')
def whoosh(dur=0.45, seed=0, **k):
    rng = np.random.default_rng(seed); n = int(dur * SR)
    nz = rng.standard_normal(n)
    out = np.zeros(n)
    # swept band: crossfade between low-passed versions with a rising cut-off
    for i, fc in enumerate(np.geomspace(300, 6000, 8)):
        w = np.exp(-0.5 * ((np.linspace(0, 1, n) - (i + 0.5) / 8) / 0.14) ** 2)
        out += _hp(_lp(nz, fc * 1.6), fc * 0.6) * w
    env = np.sin(np.linspace(0, np.pi, n)) ** 1.5
    return out * env * 0.5


@sfx('impact')
def impact(dur=1.0, seed=0, **k):
    rng = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    f = 38 + 90 * np.exp(-t / 0.05)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.28)
    crack = _hp(rng.standard_normal(n), 800) * np.exp(-t / 0.05) * 0.5
    tail = _lp(rng.standard_normal(n), 400) * np.exp(-t / 0.5) * 0.25
    return (body * 0.9 + crack + tail)


@sfx('riser')
def riser(dur=2.0, seed=0, **k):
    rng = np.random.default_rng(seed); n = int(dur * SR); t = np.linspace(0, 1, n)
    nz = rng.standard_normal(n)
    out = np.zeros(n)
    for i, fc in enumerate(np.geomspace(250, 9000, 10)):
        w = np.exp(-0.5 * ((t - (i + 0.5) / 10) / 0.2) ** 2)
        out += _hp(_lp(nz, fc * 1.5), fc * 0.5) * w
    tone = np.sin(2 * np.pi * np.cumsum(180 * 2 ** (t * 2.5)) / SR) * 0.12
    return (out * 0.35 + tone) * (t ** 1.7)


@sfx('click')
def click(dur=0.05, seed=0, **k):
    rng = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    return (_hp(rng.standard_normal(n), 2500) * np.exp(-t / 0.004) * 0.8 + np.sin(2 * np.pi * 1800 * t) * np.exp(-t / 0.006) * 0.3)


@sfx('tick')
def tick(dur=0.04, seed=0, **k):
    n = int(dur * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 1200 * t) * np.exp(-t / 0.004) * 0.6


@sfx('hiss')
def hiss(dur=0.5, seed=0, **k):
    rng = np.random.default_rng(seed); n = int(dur * SR); t = np.linspace(0, 1, n)
    return _hp(rng.standard_normal(n), 4000) * np.sin(np.pi * t) ** 2 * 0.25


@sfx('swell')
def swell(dur=1.5, seed=0, **k):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * t) for f in (110, 164.8, 220, 277.2)) * 0.1
    return s * np.sin(np.pi * np.linspace(0, 1, n)) ** 2


@sfx('glitch')
def glitch_s(dur=0.25, seed=0, **k):
    rng = np.random.default_rng(seed); n = int(dur * SR); out = np.zeros(n)
    for i in range(6):
        a = int(rng.uniform(0, n * 0.8)); l = int(rng.uniform(0.01, 0.04) * SR)
        f = rng.uniform(300, 3000)
        out[a:a + l] += np.sign(np.sin(2 * np.pi * f * np.arange(min(l, n - a)) / SR)) * 0.25
    return out


def make(name, **kw):
    return SFX[name](**kw)


def mix(duration, events, gain_master=1.0):
    """events: list of {kind, t, gain, dur?}. Returns stereo float array at 44.1 kHz."""
    out = np.zeros(int(duration * SR) + SR)
    for i, e in enumerate(events):
        x = None
        peak_s = 0.0
        if e.get('sample'):                  # a library effect (sfx_library.py), falls back to the synthesised kind
            try:
                import sfx_library
                entry = sfx_library.resolve(e['sample'])   # same clearance filter load() below applies; only read here for its measured attack_s/peak_s
                if entry is not None:
                    _, peak_s = sfx_library.offsets(entry)
                x = sfx_library.load(e['sample'], sr=SR, fallback=e['kind'] if e['kind'] in SFX else None, dur=e.get('dur'), seed=i) * e.get('gain', 0.5)
            except Exception:
                x = None
        if x is None:
            if e['kind'] not in SFX: continue
            kw = {k: v for k, v in e.items() if k in ('dur',)}
            x = SFX[e['kind']](seed=i, **kw) * e.get('gain', 0.5)
        t = e['t'] + e.get('offset', 0.0) - peak_s   # a measured library sample's peak lands on t, on top of any manual offset
        if e.get('end_at_t'):               # riser or swell that must finish on the beat
            t = e['t'] - len(x) / SR
        s = int(t * SR)
        if s < 0:
            x = x[-s:]; s = 0
        if s >= len(out): continue
        j = min(len(out), s + len(x)); out[s:j] += x[:j - s]
    out = out[:int(duration * SR)] * gain_master
    return np.stack([out, out], 1)

"""Self-generated test music. Everything here is synthesised from scratch, so it is free of any licence.

python synth.py --bpm 128 --bars 16 --seed 1 --kind house --out song.wav

Structure: intro (hats and pad), build (snare roll and riser), drop (kick, bass, lead), break, final drop.
"""
import argparse, wave
import numpy as np

SR = 44100


def sine(f, n, ph=0):
    return np.sin(2 * np.pi * np.cumsum(np.full(n, f) / SR) + ph)


def env_exp(n, decay):
    return np.exp(-np.arange(n) / (decay * SR))


def kick(dur=0.3):
    n = int(dur * SR)
    f = 45 + 110 * np.exp(-np.arange(n) / (0.025 * SR))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env_exp(n, 0.12) * 1.0


def snare(rng, dur=0.25):
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    noise = noise - np.r_[0, noise[:-1]] * 0.6
    return (noise * 0.5 + sine(190, n) * 0.4) * env_exp(n, 0.07)


def clap(rng):
    out = np.zeros(int(0.3 * SR))
    for d in (0, 0.01, 0.022):
        s = int(d * SR); n = int(0.12 * SR)
        nz = rng.standard_normal(n) * env_exp(n, 0.04)
        out[s:s + n] += nz * 0.4
    return out


def hat(rng, open_=False):
    n = int((0.25 if open_ else 0.05) * SR)
    nz = rng.standard_normal(n)
    nz = nz - np.r_[0, nz[:-1]]
    return nz * env_exp(n, 0.15 if open_ else 0.015) * 0.35


def saw(f, n):
    ph = np.cumsum(np.full(n, f) / SR) % 1.0
    return 2 * ph - 1


def lowpass(x, a):
    y = np.zeros_like(x); s = 0.0
    for i in range(len(x)):
        s += a * (x[i] - s); y[i] = s
    return y


def lp_fast(x, cutoff):
    # one pole via FFT for speed
    X = np.fft.rfft(x); fr = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (fr / cutoff) ** 2)
    return np.fft.irfft(X, len(x))


def place(buf, x, t):
    i = int(t * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(x)); buf[i:j] += x[:j - i]


def riser(dur, rng):
    n = int(dur * SR)
    nz = rng.standard_normal(n)
    sweep = np.linspace(0.05, 1, n) ** 2
    out = np.zeros(n)
    # crude rising filter: mix high-passed noise with rising gain
    hp = nz - lp_fast(nz, 600)
    return hp * sweep * 0.5


def make(bpm=128, bars=16, seed=1, kind='house'):
    rng = np.random.default_rng(seed)
    beat = 60.0 / bpm
    total = bars * 4 * beat + 1.5
    buf = np.zeros(int(total * SR))
    K, S, C = kick(), snare(rng), clap(rng)
    root = [55.0, 61.74, 49.0, 58.27][seed % 4]          # A1, B1, G1, Bb1
    scale = np.array([0, 3, 5, 7, 10, 12, 15])          # minor pentatonic-ish
    prog = [0, 0, 5, 3] if seed % 2 == 0 else [0, 3, 5, 7]
    # section map in bars: intro 0-3, build 4-7, drop 8-11, break 12-13 (if bars>=16), drop final
    def sec(b):
        if b < bars * 0.25: return 'intro'
        if b < bars * 0.5: return 'build'
        if b < bars * 0.75: return 'drop'
        if b < bars * 0.875: return 'break'
        return 'drop'
    for b in range(bars):
        s = sec(b)
        t0 = b * 4 * beat
        chord = prog[b % 4]
        for q in range(4):
            tb = t0 + q * beat
            if s in ('drop',):
                if kind == 'hiphop':
                    if q in (0, 2) or (q == 3 and b % 2): place(buf, K * 1.0, tb + (0.5 * beat if q == 3 else 0))
                    if q in (1, 3): place(buf, S, tb)
                else:
                    place(buf, K, tb)
                    if q in (1, 3): place(buf, C, tb)
                    place(buf, hat(rng, True), tb + beat * 0.5)
                for e in range(2):
                    place(buf, hat(rng), tb + e * beat * 0.5)
                # bass
                f = root * 2 ** (chord / 12)
                n = int(beat * 0.5 * SR)
                for e in range(2):
                    bn = saw(f * (2 if (q + e) % 4 == 3 else 1), n) * env_exp(n, 0.25) * 0.5
                    place(buf, lp_fast(bn, 500), tb + e * beat * 0.5 + 0.0)
                # lead arpeggio sixteenths
                for e in range(4):
                    note = scale[(q * 4 + e + b) % len(scale)] + chord
                    fq = root * 8 * 2 ** (note / 12)
                    n = int(beat * 0.25 * SR)
                    ld = (saw(fq, n) + 0.5 * sine(fq * 2, n)) * env_exp(n, 0.09) * 0.16
                    place(buf, lp_fast(ld, 3000), tb + e * beat * 0.25)
            elif s == 'build':
                place(buf, hat(rng), tb); place(buf, hat(rng), tb + beat * 0.5)
                if q == 0 and b % 2 == 0: place(buf, K, tb)
                if b >= bars * 0.4:    # snare roll doubling each bar
                    div = 2 ** min(3, b - int(bars * 0.4) + 1)
                    for e in range(div):
                        place(buf, S * (0.3 + 0.7 * e / div), tb + e * beat / div)
            elif s == 'intro':
                place(buf, hat(rng), tb + beat * 0.5)
                if q == 0: place(buf, K * 0.6, tb)
            else:   # break
                if q == 0:
                    pad = sum(saw(root * 4 * 2 ** ((chord + iv) / 12), int(4 * beat * SR)) for iv in (0, 3, 7)) * 0.06
                    place(buf, lp_fast(pad, 1200) * np.hanning(len(pad)) ** 0.3, t0)
        if s == 'build' and b == int(bars * 0.5) - 1:
            place(buf, riser(4 * beat, rng), t0)
        if s == 'break' and b == int(bars * 0.875) - 1:
            place(buf, riser(4 * beat, rng), t0)
    # pad bed
    for b in range(bars):
        chord = prog[b % 4]; t0 = b * 4 * beat
        pad = sum(saw(root * 4 * 2 ** ((chord + iv) / 12), int(4 * beat * SR)) for iv in (0, 3, 7)) * 0.03
        place(buf, lp_fast(pad, 900) * np.hanning(len(pad)) ** 0.2, t0)
    # impact at each drop
    for b in range(bars):
        if sec(b) == 'drop' and (b == 0 or sec(b - 1) != 'drop'):
            n = int(1.2 * SR)
            imp = (sine(40, n) * 0.9 + rng.standard_normal(n) * 0.2) * env_exp(n, 0.35)
            place(buf, imp, b * 4 * beat)
    # gentle sidechain-free soft limit
    buf = np.tanh(buf * 1.1)
    buf = buf[:int((bars * 4 * beat + 0.8) * SR)]
    fade = int(0.5 * SR); buf[-fade:] *= np.linspace(1, 0, fade)
    buf /= np.abs(buf).max() / 0.9
    return buf


def write(path, x):
    st = np.stack([x, x * 0.98], 1)
    pcm = (st * 32767).astype('<i2')
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--bpm', type=float, default=128); ap.add_argument('--bars', type=int, default=16)
    ap.add_argument('--seed', type=int, default=1); ap.add_argument('--kind', default='house')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    write(a.out, make(a.bpm, a.bars, a.seed, a.kind))
    import json
    json.dump({'bpm': a.bpm, 'first_beat': 0.0, 'bars': a.bars, 'kind': a.kind, 'seed': a.seed,
               'drops': [a.bars * 0.5 * 4 * 60 / a.bpm, a.bars * 0.875 * 4 * 60 / a.bpm]}, open(str(a.out).rsplit('.', 1)[0] + '.truth.json', 'w'))

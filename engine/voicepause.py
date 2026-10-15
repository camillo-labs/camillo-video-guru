"""Voice pauses that never click: open a gap in a voice track at the quietest 10 ms inside a chosen window.

The voice section of scripts/mix_soundtrack.py (the playbook's mixer) as a library: each pause is placed at the quietest 10 ms window within 0.25 s of where it was asked for, the piece before
fades out over 60 ms and the piece after fades in over 15 ms. The picture must use the same pauses, so
shift_time() and shift_words() map voice time to film time.

    cuts = plan_cuts(vo, sr, [(16.5, 1.2), (18.9, 1.2)])      # [(quiet_time_s, pause_s), ...]
    out = insert_pauses(vo, sr, cuts)                          # vo with the gaps in, longer by the pauses
    t_film = shift_time(t_voice, cuts)                         # where a voice moment lands after the pauses

This is a library only. Nothing in the planner or render.mix_audio calls it yet, because the engine's styles caption
the voice as recorded and do not re-cut it (see research/from-will.md for the wiring it would need).
"""
import numpy as np

SEARCH_S = 0.25      # how far either side of the asked-for time to look for a quiet spot
WINDOW_S = 0.010     # width of the window whose energy is compared
FADE_OUT_S = 0.060   # the piece before a pause
FADE_IN_S = 0.015    # the piece after a pause


def quiet_point(vo, sr, at, search=SEARCH_S, window=WINDOW_S):
    """(time_s, level_db): the centre of the quietest `window` within `search` seconds of `at`, and its mean-square
    level in dB. A level above about -60 dB means no real silence was found and the cut may be audible."""
    x = vo if vo.ndim == 1 else vo.mean(1)
    w = max(1, int(window * sr))
    a0 = max(0, int((at - search) * sr))
    a1 = min(len(x) - w, int((at + search) * sr))
    if a1 <= a0:
        raise ValueError(f'no room to search around {at}s in a {len(x) / sr:.2f}s voice track')
    hop = max(1, w // 2)
    starts = np.arange(a0, a1, hop)
    energy = np.array([float(np.mean(x[i:i + w].astype(np.float64) ** 2)) for i in starts])
    i = int(np.argmin(energy))
    return (starts[i] + w // 2) / sr, 10 * np.log10(energy[i] + 1e-12)


def plan_cuts(vo, sr, pauses):
    """pauses: [(voice_time_s, pause_length_s), ...]. Returns [(quiet_time_s, pause_length_s), ...] sorted by time."""
    return [(quiet_point(vo, sr, at)[0], float(d)) for at, d in sorted(pauses)]


def insert_pauses(vo, sr, cuts):
    """vo (n,) or (n, ch) float. Returns a copy with silence of each cut's length opened at its time, with the
    fades above on both sides of each gap so no join clicks."""
    if not cuts:
        return vo.copy()
    mono = vo.ndim == 1
    v = vo[:, None] if mono else vo
    total = len(v) + sum(int(round(d * sr)) for _, d in cuts)
    out = np.zeros((total, v.shape[1]), v.dtype)
    edges = [0] + [int(round(q * sr)) for q, _ in cuts] + [len(v)]
    fo, fi = int(FADE_OUT_S * sr), int(FADE_IN_S * sr)
    off = 0
    for k in range(len(edges) - 1):
        piece = v[edges[k]:edges[k + 1]].copy()
        if k > 0 and len(piece) > fi:
            piece[:fi] *= np.linspace(0, 1, fi)[:, None]
        if k < len(edges) - 2 and len(piece) > fo:
            piece[-fo:] *= np.linspace(1, 0, fo)[:, None]
        out[edges[k] + off:edges[k] + off + len(piece)] = piece
        if k < len(cuts):
            off += int(round(cuts[k][1] * sr))
    return out[:, 0] if mono else out


def shift_time(t, cuts):
    """Film time of voice time t: t plus the length of every pause cut at or before it."""
    return t + sum(d for q, d in cuts if t >= q)


def shift_words(words, cuts):
    """A copy of caption word dicts (t0, t1) moved to film time. A word that straddles a cut keeps its start and
    stretches its end across the pause, so it stays on screen until its audio finishes."""
    out = []
    for w in words:
        w2 = dict(w)
        w2['t0'] = shift_time(w['t0'], cuts)
        w2['t1'] = shift_time(w['t1'], cuts)
        out.append(w2)
    return out

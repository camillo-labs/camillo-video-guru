"""Sound effect library loader: real recorded effects from sfx/ (index.json in git, WAV files kept locally, see sfx/README.md and $SFX_LIBRARY), with the synthesised effects in sfx.py as fallback.

    import sfx_library as lib
    lib.find(category='transitions/whoosh')          # index entries
    lib.find(tag='riser')
    x = lib.load('riser')                            # mono float array at sfx.SR, or the synthesised riser if the file is missing
    x = lib.load('tag:whoosh', fallback='whoosh')    # a query is a name, 'category:<dir>' or 'tag:<tag>'; first match wins
    lib.apply_to_edl(edl, style.get('sfx_library'))  # style option, see below

Style option (off unless present, so existing styles render exactly as before):

    "sfx_library": {"enabled": true,
                    "map": {"whoosh": "woosh", "impact": "outro-hit", "riser": "riser", "click": "camera-click"}}

Every edl sfx event whose kind is in the map gets a `sample` field. sfx.mix plays the sample when it loads and plays the synthesised
effect otherwise. An event can also carry `sample` directly. Library clips are normalised to about -16 LUFS with a -1 dBFS peak ceiling,
so event gains in the styles (made for the synthesised effects, peak about 0.5) still land sensibly.

Cleared set (2026-10-15, build stage 5, Cam's note N2): the 13 clips cut from the two reels are
"unknown, personal and internal use only" (README.md), so `find`/`resolve`/`load` only return a
cleared-licence entry (CC0, CC BY, Sonniss GDC's own EULA, or similar, and a recorded `credit`)
unless the caller explicitly passes `include_uncleared=True`. This is a strict opt-in on top of
the existing opt-in (`sfx_library.enabled` in a style): the library stays off by default exactly
as before, and once on, it now only ever serves an effect that is actually clear to ship. No
cleared clip has been added yet: a Sonniss GDC 2026 (gdc.sonniss.com) or FMA CC0/CC-BY (ND/NC
filtered out) pull needs network the sandbox refuses (confirmed this stage, `curl` to both hosts
returns `deny network-outbound ...: user denied`), the same block build-2 already logged as card
`2998a8b4` ("Let the video build reach TikTok, Instagram and the music and SFX sites"). Until
that card is actioned or clips are added by hand, `include_uncleared=False`'s filtering simply
means every real query returns nothing and `load` falls through to the synthesiser, which is the
plan's own stated fallback (selection-plan-2026-10-14.md, R2-5: "stays the safe default
meanwhile, not a blocked fallback").
"""
import json
import os
from pathlib import Path

import numpy as np

import sfx as synth

ROOT = Path(os.environ.get('SFX_LIBRARY', Path(__file__).resolve().parents[1] / 'sfx'))

# synthesised stand-in for each library category, used when a clip is missing or the library is absent
CATEGORY_FALLBACK = {
    'transitions/whoosh': 'whoosh', 'impacts': 'impact', 'risers': 'riser', 'clicks-and-switches': 'click',
    'glitches': 'glitch', 'ui': 'tick', 'ambience': 'swell', 'other': 'hiss',
}
_cache = {'index': None, 'audio': {}}

# Prefixes of a cleared licence string. Checked case-insensitively against entry['licence'];
# "unknown, personal and internal use only until cleared" (the 13 reel clips) matches none of
# these, which is the point.
CLEARED_LICENCE_PREFIXES = ('cc0', 'cc by', 'cc-by', 'public domain', 'sonniss', 'fma', 'free music archive')


def is_cleared(entry):
    """True when an index entry carries both a recognised cleared licence and a credit string."""
    lic = (entry.get('licence') or '').strip().lower()
    if not lic or not entry.get('credit'):
        return False
    return any(lic.startswith(p) for p in CLEARED_LICENCE_PREFIXES)


def offsets(entry):
    """(attack_s, peak_s) for a sample, 0.0 when not measured (sfx.py's alignment, extending the
    existing offset/end_at_t mechanism rather than replacing it)."""
    return entry.get('attack_s', 0.0) or 0.0, entry.get('peak_s', 0.0) or 0.0


def index(reload=False):
    """The index.json entries, or [] when the library has not been built."""
    if _cache['index'] is None or reload:
        p = ROOT / 'index.json'
        try:
            with open(p) as fh:
                _cache['index'] = json.load(fh)['effects']
        except (OSError, ValueError, KeyError):
            _cache['index'] = []
        _cache['audio'].clear()
    return _cache['index']


def find(name=None, category=None, tag=None, include_uncleared=False):
    """Entries matching all given filters. A name matches the id, the display name or the file stem, case-insensitively.
    Only a cleared entry (see `is_cleared`) is returned unless `include_uncleared=True`."""
    out = []
    for e in index():
        if not include_uncleared and not is_cleared(e):
            continue
        if name and name.lower().replace(' ', '-') not in (e['id'], e['name'].lower().replace(' ', '-'), Path(e['file']).stem):
            continue
        if category and e['category'] != category:
            continue
        if tag and tag.lower() not in [t.lower() for t in e.get('tags', [])]:
            continue
        out.append(e)
    return out


def resolve(query, include_uncleared=False):
    """First entry for a query: 'category:<dir>', 'tag:<tag>' or a name."""
    if not query:
        return None
    if query.startswith('category:'):
        r = find(category=query[9:], include_uncleared=include_uncleared)
    elif query.startswith('tag:'):
        r = find(tag=query[4:], include_uncleared=include_uncleared)
    else:
        r = find(name=query, include_uncleared=include_uncleared)
    return r[0] if r else None


def _read(entry, sr):
    key = (entry['file'], sr)
    if key not in _cache['audio']:
        import soundfile as sf
        x, src_sr = sf.read(ROOT / entry['file'], always_2d=True)
        x = x.mean(1)
        if src_sr != sr:                                    # FFT resample, no scipy needed
            n = int(round(len(x) * sr / src_sr))
            X = np.fft.rfft(x)
            Y = np.zeros(n // 2 + 1, complex)
            m = min(len(X), len(Y))
            Y[:m] = X[:m]
            x = np.fft.irfft(Y, n) * (n / len(x))
        _cache['audio'][key] = x.astype(np.float64)
    return _cache['audio'][key]


def load(query, sr=None, fallback=None, dur=None, seed=0, include_uncleared=False):
    """Mono float array for a library effect at `sr` (default sfx.SR).

    Falls back to the synthesised effect `fallback` (or the one for the entry's category) when the query has no match or the file cannot be read;
    raises KeyError only when there is nothing to fall back to either. `dur` trims or zero-pads a library clip, and sets the length of a synthesised one.
    """
    sr = sr or synth.SR
    e = resolve(query, include_uncleared=include_uncleared)
    if e is not None:
        try:
            x = _read(e, sr)
            if dur:
                n = int(dur * sr)
                x = x[:n] if len(x) >= n else np.pad(x, (0, n - len(x)))
            return x.copy()
        except Exception:
            pass
    kind = fallback or (CATEGORY_FALLBACK.get(e['category']) if e else None)
    if kind is None and query in synth.SFX:
        kind = query
    if kind is None or kind not in synth.SFX:
        raise KeyError(f'no library effect and no synthesised fallback for {query!r}')
    kw = {'dur': dur} if dur else {}
    return synth.SFX[kind](seed=seed, **kw)


def apply_to_edl(edl, cfg):
    """Tag edl['sfx'] events with library samples as the style's sfx_library option asks. Returns how many events were tagged."""
    if not cfg or not cfg.get('enabled', True):
        return 0
    m = cfg.get('map', {})
    n = 0
    for e in edl.get('sfx', []):
        if e.get('kind') in m and 'sample' not in e:
            e['sample'] = m[e['kind']]
            n += 1
    return n

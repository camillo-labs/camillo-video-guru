"""Picks a library track and a window for a brief, per selection-plan-2026-10-14.md section 2:
score tempo fit, energy-curve/drop fit, a per-style beat-clarity floor, the genre/mood map and
length, with a variety penalty that Stage 10's acceptance renders can turn off.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

GENRE_MOOD = {
    'energetic': ('house', 'hip-hop', 'phonk', 'trap'),
    'edgy': ('house', 'hip-hop', 'phonk', 'trap'),
    'calm': ('orchestral', 'ambient', 'light acoustic'),
    'heritage': ('orchestral', 'ambient', 'light acoustic'),
    'playful': ('pop', 'funk'),
    'premium': ('minimal electronic', 'cinematic'),
}

# Per-genre floor, not one blanket 0.9: the flash styles need a drum-led track, the
# word-per-beat lyric styles can ride a looser one (research doc section 2).
BEAT_CLARITY_FLOOR = {
    'flash': 0.9,
    'lyric': 0.6,
    'default': 0.6,
}

# Set by the last candidate_windows() call so is_downbeat() can check a time against the
# actual tracks it searched, without threading a track reference through every caller.
_last_downbeats = set()


def _load_index(index_path):
    """index_path may be given relative to the caller's cwd, or (as the repo's other library
    loaders do, e.g. sfx_library.ROOT) relative to the repo root music/ sits in."""
    p = Path(index_path)
    if not p.is_file():
        root_relative = Path(__file__).resolve().parents[1] / index_path
        if root_relative.is_file():
            p = root_relative
    with open(p) as f:
        return json.load(f)


def candidate_windows(index_path, bpm_target, duration, bpm_tol=0.15):
    """Every phrase start (ordinary phrase boundaries and drops) across every track within
    bpm_tol of bpm_target that has room for duration plus one bar. Downbeat-aligned only,
    since audio.analyse's phrases and drops are both beat-grid positions."""
    global _last_downbeats
    index = _load_index(index_path)
    _last_downbeats = set()
    starts = []
    for t in index:
        bpm = t.get('bpm', 0)
        if bpm <= 0 or abs(bpm - bpm_target) / bpm_target > bpm_tol:
            continue
        bar = 60.0 / bpm * 4
        dur = t.get('duration', 0)
        _last_downbeats.update(round(d, 3) for d in t.get('downbeats') or [])
        for p in t.get('phrases', []):
            if p + duration + bar <= dur:
                starts.append(round(p, 3))
    return starts


def is_downbeat(s, tol=0.02):
    return any(abs(s - d) <= tol for d in _last_downbeats)


def pick(brief, index_path, disable_variety_penalty=False, top_n=3):
    """brief keys: bpm_target, duration, mood, style_kind ('flash'|'lyric'|other, sets the
    beat-clarity floor), drop_at (fraction of duration), vocals_ok, recent_tracks (paths used
    in recent renders, for the variety penalty). Returns the best candidate with its window,
    plus the top `top_n` under 'candidates' for decisions.json."""
    index = _load_index(index_path)
    bpm_target = brief['bpm_target']
    duration = brief['duration']
    drop_at = brief.get('drop_at', 0.4)
    floor = BEAT_CLARITY_FLOOR.get(brief.get('style_kind'), BEAT_CLARITY_FLOOR['default'])
    recent = set(brief.get('recent_tracks', []))
    mood = brief.get('mood')
    scored = []
    for t in index:
        bpm = t.get('bpm', 0)
        if bpm <= 0:
            continue
        clarity = t.get('beat_clarity', 0.0)
        if clarity < floor:
            continue
        if mood and GENRE_MOOD.get(mood) is not None and t.get('genre') not in GENRE_MOOD[mood]:
            continue
        if not brief.get('vocals_ok', True) and t.get('vocals', False):
            continue
        tempo_fit = max(0.0, 1 - abs(bpm - bpm_target) / bpm_target)
        dur = t.get('duration', 0)
        bar = 60.0 / bpm * 4
        best_start, best_window_score = None, -1.0
        for p in t.get('phrases', []):
            if p + duration + bar > dur:
                continue
            wanted = p + drop_at * duration
            drop_fit = 0.0
            for d in t.get('drops', []):
                if p <= d <= p + duration:
                    drop_fit = max(drop_fit, 1 - min(1.0, abs(d - wanted) / max(duration * 0.15, 1e-9)))
            window_score = 0.6 * drop_fit + 0.4 * tempo_fit
            if window_score > best_window_score:
                best_start, best_window_score = round(p, 3), window_score
        if best_start is None:
            continue
        score = 0.35 * tempo_fit + 0.35 * best_window_score + 0.2 * clarity
        if not disable_variety_penalty and t['path'] in recent:
            score -= 0.25
        scored.append({
            'path': t['path'], 'start': best_start, 'score': round(score, 3),
            'bpm': bpm, 'beat_clarity': clarity, 'tempo_fit': round(tempo_fit, 3),
        })
    scored.sort(key=lambda c: -c['score'])
    if not scored:
        return {
            'path': None, 'start': None, 'candidates': [],
            'reason': 'forced pick, library below target: no track cleared the beat-clarity '
                      'floor, genre/mood map or tempo window for this brief',
        }
    top = scored[:top_n]
    best = dict(top[0])
    best['candidates'] = top
    return best


if __name__ == '__main__':
    print(json.dumps(pick({'bpm_target': 122, 'duration': 15}, sys.argv[1]), indent=2))

"""Music library: per-track analysis (tempo, drops, beat clarity) and the index file pick_track reads.

Builds on audio.analyse, which already computes the beat grid, energy, drops and phrase
boundaries; this module adds beat clarity and the index-building step described in
edits/research/selection-plan-2026-10-14.md section 2.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import audio


def detect_drops(path):
    return audio.analyse(path)['drops']


def beat_clarity(analysis, window=0.025):
    """Fraction of beats with an onset within `window` seconds. Calibrated against the
    selection plan's own figure: Raving-Energy's clean drum attacks should read about 0.97.
    """
    beats, onsets = analysis['beats'], analysis['onsets']
    if not beats or not onsets:
        return 0.0
    ot = np.array([o['t'] for o in onsets])
    hits = sum(1 for t in beats if np.abs(ot - t).min() <= window)
    return hits / len(beats)


def analyse_track(path):
    a = audio.analyse(path)
    return {
        'bpm': a['bpm'],
        'duration': a['duration'],
        'beat_clarity': round(beat_clarity(a), 3),
        'drops': a['drops'],
        'drop_count': len(a['drops']),
        'first_drop': a['drops'][0] if a['drops'] else None,
        'phrases': a['phrases'],
        'downbeats': a['downbeats'],
        'beat_period': a['beat_period'],
        'first_beat': a['first_beat'],
    }


def build_index(tracks, out_path):
    """tracks: list of dicts carrying at least 'path' plus authored metadata (mood, genre,
    source, licence, credit, vocals). Runs analyse_track on each path, merges the measured
    fields in, and writes out_path as a JSON list. Returns the list built."""
    index = []
    for t in tracks:
        entry = dict(t)
        entry.update(analyse_track(t['path']))
        index.append(entry)
    with open(out_path, 'w') as f:
        json.dump(index, f, indent=2)
    return index


if __name__ == '__main__':
    print(json.dumps(analyse_track(sys.argv[1]), indent=2))

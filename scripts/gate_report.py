#!/usr/bin/env python3
"""Run gate.py's three checks against every rendered test and demo edit, and print a report.
Stage 3's scope (plan.md:174) is to report what currently breaches the gates, not to fix it.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'engine'))
import paths
import gate

TARGETS = [
    ('green-label (real test)', 'tests/green-label/green-label.mp4', 'tests/green-label/edl.json'),
    ('fontainebleau (real test)', 'tests/fontainebleau/fontainebleau.mp4', 'tests/fontainebleau/edl.json'),
    ('dachshunds (real test)', 'tests/dachshunds/out/edit.mp4', 'tests/dachshunds/out/edl.json'),
    ('dachshunds HUD variant (real test)', 'tests/dachshunds/hud/out/edit.mp4', 'tests/dachshunds/hud/out/edl.json'),
    ('fontainebleau-bw-flash-vo (demo)', 'tests/fontainebleau-bw-flash-vo/fontainebleau-bw-flash-vo.mp4', 'tests/fontainebleau-bw-flash-vo/edl.json'),
    ('fontainebleau-hud-lyric-heat (demo)', 'tests/fontainebleau-hud-lyric-heat/fontainebleau-hud-lyric-heat.mp4', 'tests/fontainebleau-hud-lyric-heat/edl.json'),
    ('fontainebleau-hud-lyric-light (demo)', 'tests/fontainebleau-hud-lyric-light/fontainebleau-hud-lyric-light.mp4', 'tests/fontainebleau-hud-lyric-light/edl.json'),
    ('green-label-hud-lyric-heat (demo)', 'tests/green-label-hud-lyric-heat/green-label-hud-lyric-heat.mp4', 'tests/green-label-hud-lyric-heat/edl.json'),
    ('green-label-hud-lyric-light (demo)', 'tests/green-label-hud-lyric-light/green-label-hud-lyric-light.mp4', 'tests/green-label-hud-lyric-light/edl.json'),
    ('green-label-lyric-word-beat (demo)', 'tests/green-label-lyric-word-beat/green-label-lyric-word-beat.mp4', 'tests/green-label-lyric-word-beat/edl.json'),
]


def main():
    results = {}
    for name, video, edl in TARGETS:
        v, e = paths.media(video), paths.ROOT / edl
        if not v.exists() or not e.exists():
            results[name] = {'error': f'missing {v if not v.exists() else e}'}
            continue
        results[name] = {
            'safe_area': gate.safe_area_check(str(v), str(e)),
            'flash_frequency': gate.flash_frequency_check(str(v)),
            'dead_frames': gate.dead_frame_check(str(v)),
        }
    print(json.dumps(results, indent=1))
    return results


if __name__ == '__main__':
    main()

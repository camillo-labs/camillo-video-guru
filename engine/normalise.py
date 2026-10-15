"""Normalise-before-stylise: measures the real exposure and saturation of a clip set so a style's
own base grade (contrast, saturation, vignette) starts from a common target instead of drifting
with whatever a given shoot's raw white balance and exposure happened to be. Opt in per style with
`"grade": {"normalise": true, ...}`; plan.build_edl then seeds each shot's grade dict from this
module's `grade_base` before layering the style's own `base`/`timeline` grade on top, the same
"layer over, don't replace" pattern make_edit.merge_audio already uses for the audio dict.
"""
import sys, os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clips as clipmod

TARGET_LUMA = 0.5
TARGET_SATURATION = 0.4


def _item_luma(item):
    v = item['bright'][0] if item['kind'] == 'image' else item['mean_bright']
    return v / 255.0 if v > 1.0 else v


def _item_sat(item):
    v = item['sat'][0] if item['kind'] == 'image' else (sum(item['sat']) / len(item['sat']) if item['sat'] else 0.0)
    return v / 255.0 if v > 1.0 else v


def from_items(items, target_luma=TARGET_LUMA, target_saturation=TARGET_SATURATION):
    """items: clips.analyse_folder's own output (or build_edl's clip_list, already analysed once,
    so this never re-reads the footage from disk). Returns the measured mean luma/saturation
    across the set plus `grade_base`, the grade.py keys a style's base grade should start from."""
    if not items:
        raise ValueError('no clips to normalise')
    n = len(items)
    luma = sum(_item_luma(i) for i in items) / n
    sat = sum(_item_sat(i) for i in items) / n
    sat_gain = 1.0 if sat <= 1e-3 else min(2.0, max(0.5, target_saturation / sat))
    return {
        'measured_luma': round(luma, 4),
        'measured_saturation': round(sat, 4),
        'target_luma': target_luma,
        'target_saturation': target_saturation,
        'grade_base': {
            'target_luma': target_luma,
            'target_strength': 0.6,
            'saturation': round(sat_gain, 4),
        },
    }


def target_luma_sat(folder, cache_dir=None):
    """folder is an assets-style directory: analyses folder/clips when that subfolder exists (the
    convention every real test folder uses, matching brief.from_footage), else the folder itself."""
    folder = Path(folder)
    clips_dir = folder / 'clips' if (folder / 'clips').is_dir() else folder
    items = clipmod.analyse_folder(clips_dir, cache_dir)
    return from_items(items)

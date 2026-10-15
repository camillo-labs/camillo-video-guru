"""Reads a brief for the style chooser: footage features from clips.py plus the caller's stated
mood, audience, caption kind, voiceover and target length/aspect (selection-plan-2026-10-14.md
section 1). choose_style.choose() consumes the flat dict this returns.
"""
import sys, os
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
import clips

STILL_WEIGHT_S = 2.0     # seconds a still typically holds on screen once the renderer pans it
LONG_CLIP_CAP_S = 10.0   # caps one long take from dominating the weighted shares
LONG_CLIP_MIN_S = 5.0    # "clips of 5 seconds or more", selection-plan-2026-10-14.md:49


def _weight(item):
    return min(item['dur'], LONG_CLIP_CAP_S) if item['kind'] == 'video' else STILL_WEIGHT_S


def _clip_sat(item):
    return item['sat'][0] if item['kind'] == 'image' else (sum(item['sat']) / len(item['sat']) if item['sat'] else 0.0)


def _clip_luma(item):
    return item['bright'][0] if item['kind'] == 'image' else item['mean_bright']


def from_footage(folder, mood=None, audience=None, caption_kind=None, voiceover=None,
                  duration=None, aspect=None, cards_dir=None, cache_dir=None):
    """folder is an assets-style directory. Analyses folder/clips when that subfolder exists
    (the convention every real test folder uses, so stills sitting beside it, like a logo, do
    not get counted as the main footage), else the folder itself.
    """
    folder = Path(folder)
    clips_dir = folder / 'clips' if (folder / 'clips').is_dir() else folder
    items = clips.analyse_folder(clips_dir, cache_dir)
    if not items:
        raise ValueError(f'no clips found under {clips_dir}')
    n = len(items)
    weights = [_weight(i) for i in items]
    total_w = sum(weights) or 1.0

    def share(pred):
        return sum(w for i, w in zip(items, weights) if pred(i)) / total_w

    stills_share = sum(1 for i in items if i['kind'] == 'image') / n
    screen_capture_count = sum(1 for i in items if i['screen_capture'])
    mean_motion = sum(w * i['mean_motion'] for i, w in zip(items, weights)) / total_w
    mean_saturation = sum(w * _clip_sat(i) for i, w in zip(items, weights)) / total_w
    mean_luma = sum(w * _clip_luma(i) for i, w in zip(items, weights)) / total_w
    distinct_subjects = clips.distinct_subjects(items)

    has_cards = bool(cards_dir and Path(cards_dir).is_dir() and any(Path(cards_dir).iterdir()))
    # A caption-worthy text source sits beside the assets folder on every real test
    # (captions.txt or facts.md next to tests/<name>/assets); the chooser must not pick a
    # lyric/HUD style and render it blank when neither exists (review-3 finding 17).
    captions_sibling = (folder.parent / 'captions.txt').exists() or (folder.parent / 'facts.md').exists()

    return {
        'clip_count': n,
        'stills_share': round(stills_share, 4),
        'screen_capture_count': screen_capture_count,
        'screen_capture_share': round(share(lambda i: i['screen_capture']), 4),
        'speech': share(lambda i: i['speech_present']) > 0.3,
        'speech_share': round(share(lambda i: i['speech_present']), 4),
        'large_face_share': round(share(lambda i: i['face_area'] >= clips.LARGE_FACE_AREA), 4),
        'long_clip_share': round(share(lambda i: i['kind'] == 'video' and i['dur'] >= LONG_CLIP_MIN_S), 4),
        'mean_motion': round(mean_motion, 4),
        'mean_saturation': round(mean_saturation, 2),
        'mean_luma': round(mean_luma, 2),
        'subjects': distinct_subjects,
        'cards_dir': cards_dir,
        'has_cards': has_cards,
        'has_caption_source': bool(caption_kind) or captions_sibling,
        'mood': mood,
        'audience': audience,
        'caption_kind': caption_kind,
        'voiceover': bool(voiceover),
        'duration': duration,
        'aspect': aspect,
    }

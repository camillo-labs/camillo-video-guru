"""Scores the six learned styles against a brief (brief.py's output) and picks the best fit.

Rules translated from edits/research/selection-plan-2026-10-14.md section 1 into numeric scores
(each style returns a score in [0, 1] plus the gap it hit if a hard precondition failed) rather
than the plan's prose AND/OR chain, so a close call is visible as a margin, not a silent branch.
The highest score wins; a margin under MARGIN_MIN between the top two, or a best score under
FLOOR, returns "no fit" and names the gap (review-3 R3-19's own fallback for this case).

STYLE_REGISTRY is explicit, not every edits/<name>/style.json on disk: edits/a03a-fontainebleau
is a client-brand variant of bw-flash-vo made for one ad, not a learned style, and the aspect
tie-break the plan's rule 4 proposed is dropped rather than applied (review-3 finding R3-19:
four of the six styles default to 16:9 while every real test renders 9:16, so matching aspect
would push every 9:16 brief toward the two voice styles).
"""

STYLE_REGISTRY = [
    'bw-flash-vo',
    'lyric-word-beat',
    'hud-lyric-heat',
    'hud-lyric-light',
    'talking-head-split',
    'kinetic-card-explainer',
]

MARGIN_MIN = 0.15
FLOOR = 0.5

MOOD_ENERGETIC = {'energetic', 'dark', 'edgy'}
MOOD_CALM = {'calm', 'heritage'}
STEP_CAPTION_KINDS = {'steps', 'tool', 'how-to', 'workflow'}
LYRIC_CAPTION_KINDS = {'lyric', 'slogan'}

# selection-plan-2026-10-14.md:51, default durations per style, used only for the no-aspect
# duration-closeness tie-break (the aspect tie-break itself is dropped, see module docstring).
DEFAULT_DURATION = {
    'bw-flash-vo': 16.0,
    'lyric-word-beat': 17.0,
    'hud-lyric-heat': 16.0,
    'hud-lyric-light': 16.0,
    'talking-head-split': 30.0,
    'kinetic-card-explainer': 31.0,
}


def _clip01(x):
    return max(0.0, min(1.0, x))


def _is_talker(b):
    return bool(b.get('speech', False)) and b.get('large_face_share', 0.0) >= 0.6


def _score_talking_head_split(b):
    if not (b.get('speech', False) and b.get('large_face_share', 0.0) >= 0.6):
        return 0.0, None
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    import gate
    if not gate.talking_split_allowed(b):
        return 0.0, 'talker_no_captures'
    speech_share = b.get('speech_share', 0.0)
    face_share = b.get('large_face_share', 0.0)
    return _clip01(0.55 + 0.25 * _clip01(speech_share / 0.5) + 0.2 * _clip01(face_share / 0.9)), None


def _score_kinetic_card_explainer(b):
    if not b.get('voiceover', False) or _is_talker(b):
        return 0.0, None
    content_shape = max(
        _clip01(b.get('screen_capture_share', 0.0) / 0.3),
        _clip01(b.get('stills_share', 0.0) / 0.5),
        1.0 if b.get('has_cards', False) else 0.0,
        1.0 if b.get('caption_kind') in STEP_CAPTION_KINDS else 0.0,
    )
    if content_shape <= 0.0:
        return 0.0, 'voiceover_no_drawable_content'
    return _clip01(0.5 + 0.5 * content_shape), None


def _score_bw_flash_vo(b):
    # rule 2b (plan:46) and rule 3c (plan:50) are each a full AND chain, not subject count
    # alone: a no-voiceover pick needs the energetic/dark/edgy mood too, or 12 unexplained
    # "subjects" with no mood and no motion reading (the plan's own no-fit acceptance case)
    # would otherwise out-score everything else on subject count alone.
    best = 0.0
    if b.get('voiceover', False) and not _is_talker(b) and b.get('clip_count', 0) >= 8:
        best = max(best, _clip01(0.5 + 0.5 * _clip01(b.get('clip_count', 0) / 12)))
    if not b.get('voiceover', False) and b.get('mood') in MOOD_ENERGETIC:
        many_subjects = _clip01((b.get('subjects', 0) - 1) / 5.0)
        high_motion = _clip01((b.get('mean_motion', 0.0) - 3.0) / 6.0)
        subject_signal = max(many_subjects, high_motion)
        best = max(best, _clip01(0.55 + 0.3 * subject_signal))
    gap = None if best > 0.0 else 'no_broll_turn_or_energetic_signal'
    return best, gap


def _score_lyric_word_beat(b):
    if b.get('voiceover', False):
        return 0.0, 'voiceover_present'
    caption_hit = 1.0 if b.get('caption_kind') in LYRIC_CAPTION_KINDS else 0.0
    stills_hit = _clip01(b.get('stills_share', 0.0) / 0.4)
    low_motion_hit = _clip01((5.0 - b.get('mean_motion', 5.0)) / 5.0)
    aspect_hit = 1.0 if b.get('aspect') == '16:9' else 0.0
    mood_hit = 1.0 if b.get('mood') in MOOD_CALM else 0.0
    best_signal = max(caption_hit, stills_hit, low_motion_hit, aspect_hit, mood_hit)
    # a genuine OR: being the safe fallback keeps a floor under a footage set that fits no
    # other style's signal at all, matching rule 4's "lyric-word-beat as the safest renderer".
    return _clip01(0.45 + 0.4 * best_signal), None


def _score_hud(b, variant):
    single_subject = _clip01(1.0 - max(0.0, b.get('subjects', 0) - 1) / 4.0)
    long_clips = _clip01(b.get('long_clip_share', 0.0) / 0.5)
    base_fit = _clip01(0.5 * single_subject + 0.5 * long_clips)
    # a talking-head clip is also a single long-held subject, so without this guard it
    # out-scores lyric-word-beat's safe fallback whenever talking-head-split is gated off
    # (no cards_dir) — _is_talker already excludes it from bw_flash_vo and kinetic_card_explainer.
    if b.get('voiceover', False) or base_fit < 0.5 or _is_talker(b):
        return 0.0, None
    sat = b.get('mean_saturation', 0.0) / 255.0 if b.get('mean_saturation', 0.0) > 1.0 else b.get('mean_saturation', 0.0)
    luma = b.get('mean_luma', 0.0) / 255.0 if b.get('mean_luma', 0.0) > 1.0 else b.get('mean_luma', 0.0)
    is_heat = sat >= 0.35 and luma < 0.6
    is_light = luma >= 0.6 or sat < 0.25
    if variant == 'heat':
        return (_clip01(base_fit + 0.1) if is_heat else 0.0), None
    return (_clip01(base_fit + 0.1) if (is_light and not is_heat) else 0.0), None


SCORERS = {
    'talking-head-split': _score_talking_head_split,
    'kinetic-card-explainer': _score_kinetic_card_explainer,
    'bw-flash-vo': _score_bw_flash_vo,
    'lyric-word-beat': _score_lyric_word_beat,
    'hud-lyric-heat': lambda b: _score_hud(b, 'heat'),
    'hud-lyric-light': lambda b: _score_hud(b, 'light'),
}


def _tie_break(style_a, style_b, b):
    """No aspect tie-break (review-3 R3-19). Duration closeness, then lyric-word-beat."""
    target = b.get('duration')
    if target:
        da = abs(DEFAULT_DURATION[style_a] - target)
        db = abs(DEFAULT_DURATION[style_b] - target)
        if da != db:
            return style_a if da < db else style_b
    if 'lyric-word-beat' in (style_a, style_b):
        return 'lyric-word-beat'
    return style_a


# bed_db by mood, for a music-led edit (selection-plan-2026-10-14.md's mood groups, reused from
# above rather than a third set). Styles already fixing music_gain to 0 for voice-only content
# (kinetic-card-explainer, talking-head-split) take their own style.json value over this.
_BED_DB_ENERGETIC = -14.0
_BED_DB_CALM = -20.0
_BED_DB_DEFAULT = -17.0


def _audio_decision(b):
    """A bed-level/gain starting point for make_edit.py's audio merge (plan.md:228, "landing
    together with choose_style.choose() actually writing a bed-level/gain decision into
    edl['audio'] so the fix isn't a no-op"). Speech present ducks the bed well under the
    voiceover; otherwise the mood groups already scored above set how hot the music bed sits."""
    if b.get('voiceover') or b.get('speech'):
        return {'music_gain': 0.2}
    mood = b.get('mood')
    if mood in MOOD_ENERGETIC:
        bed_db = _BED_DB_ENERGETIC
    elif mood in MOOD_CALM:
        bed_db = _BED_DB_CALM
    else:
        bed_db = _BED_DB_DEFAULT
    return {'bed_db': bed_db}


def choose(b):
    """b is a brief dict (brief.from_footage's output, or a sparse hand-built dict — every key
    is read with .get() and a safe default). Returns {'style', 'score', 'runner_up',
    'runner_up_score', 'scores', 'gap', 'audio'}. style is None on no fit; gap names why whenever
    it is known (a hard precondition that failed), even on a fit, so decisions.json can show the
    runner-up's own blocked reason. audio is always present (see _audio_decision), even on no
    fit, so a caller can still use it."""
    scores = {}
    gaps = {}
    for name in STYLE_REGISTRY:
        score, gap = SCORERS[name](b)
        scores[name] = round(score, 4)
        if gap:
            gaps[name] = gap
    ranked = sorted(STYLE_REGISTRY, key=lambda n: scores[n], reverse=True)
    best, second = ranked[0], ranked[1]
    if scores[best] == scores[second]:
        best = _tie_break(best, second, b)
    margin = scores[best] - scores[second]
    result = {
        'scores': scores,
        'runner_up': second,
        'runner_up_score': scores[second],
        'audio': _audio_decision(b),
    }
    if scores[best] < FLOOR or margin < MARGIN_MIN:
        result['style'] = None
        result['score'] = scores[best]
        result['gap'] = gaps.get(best) or (
            'best score below floor' if scores[best] < FLOOR else f'margin {margin:.3f} under {MARGIN_MIN}'
        )
        return result
    result['style'] = best
    result['score'] = scores[best]
    if gaps:
        result['gap'] = None
    return result

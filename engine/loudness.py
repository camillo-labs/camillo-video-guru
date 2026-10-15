"""Final mix loudness: one static gain from a single ffmpeg loudnorm measurement pass, then a
brick-wall lookahead limiter (ffmpeg alimiter) to catch what the gain alone would clip.

render.mix_audio's final stage used to be a plain peak scale (if the loudest sample exceeds 0.89,
turn the whole mix down until it doesn't) with no loudness target at all, so a sparse edit and a
sfx-heavy one could land at very different perceived volumes, and a hot single hit would turn the
whole mix down rather than just itself. The alternative a single-pass loudnorm filter (the
dynamic, one-shot mode) is worse: it rides gain over the length of the mix and audibly pumps under
the hit gaps and voiceover ducking render.mix_audio already shapes in. This follows the practice in
scripts/mix_soundtrack.py, the playbook's mixer: measure
once, apply one constant gain, then limit only the peaks that remain.

    mix, report = normalise(mix, sr)   # mix at TARGET_I LUFS integrated, peaks under TARGET_TP dBTP
"""
import json
import subprocess

import numpy as np

TARGET_I = -14.0    # LUFS integrated: the common short-form (Reels/Shorts/TikTok) delivery target
TARGET_TP = -1.0    # dBTP ceiling the limiter is set to after the static gain
MAX_GAIN_DB = 24.0  # clamp: a near-silent mix should not be boosted all the way up to clipping


def _measure_integrated_lufs(x, sr):
    """One ffmpeg loudnorm pass in measure-only mode: loudnorm always reports what it measured
    in its print_format=json block on stderr, whether or not anything downstream uses its own
    (dynamic, pumping) gain, so this reads that block instead of applying the filter's output."""
    ch = x.shape[1] if x.ndim > 1 else 1
    p = subprocess.run(
        ['ffmpeg', '-v', 'info', '-f', 'f32le', '-ar', str(sr), '-ac', str(ch), '-i', '-',
         '-af', f'loudnorm=I={TARGET_I}:TP={TARGET_TP}:print_format=json', '-f', 'null', '-'],
        input=x.astype(np.float32).tobytes(), capture_output=True)
    text = p.stderr.decode('utf-8', 'ignore')
    if p.returncode != 0:
        raise RuntimeError(f'loudnorm measurement pass failed (exit {p.returncode}): {text[-500:]}')
    start, end = text.rfind('{'), text.rfind('}')
    if start < 0 or end < start:
        raise RuntimeError(f'loudnorm measurement pass produced no report: {text[-500:]}')
    stats = json.loads(text[start:end + 1])
    return float(stats['input_i']), float(stats['input_tp'])


def _limit(x, sr, limit_db, attack_ms=5, release_ms=50):
    """ffmpeg's alimiter: a lookahead brick-wall limiter, not a second loudness pass. `level`
    (ffmpeg's own auto output-level compensation) is off so the limiter only removes peaks and
    does not relitigate the gain normalise() just set. `latency=true` compensates for the
    filter's own lookahead delay (the attack window): without it every mix comes out shifted
    later by about `attack_ms`, dragging the soundtrack out of sync with the picture and with
    the peak-aligned sfx sfx.mix() already placed on the beat."""
    ch = x.shape[1] if x.ndim > 1 else 1
    limit = float(np.clip(10 ** (limit_db / 20), 0.0625, 1.0))
    p = subprocess.run(
        ['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(sr), '-ac', str(ch), '-i', '-',
         '-af', f'alimiter=limit={limit:.6f}:attack={attack_ms}:release={release_ms}:level=false:latency=true',
         '-f', 'f32le', '-ar', str(sr), '-ac', str(ch), '-'],
        input=x.astype(np.float32).tobytes(), capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f'alimiter pass failed (exit {p.returncode}): {p.stderr.decode("utf-8", "ignore")[-500:]}')
    y = np.frombuffer(p.stdout, np.float32)
    out = y.reshape(-1, ch) if ch > 1 else y
    if len(out) != len(x):
        raise RuntimeError(f'alimiter pass returned {len(out)} frames for {len(x)} in; expected latency=true to keep them equal')
    return out


def normalise(mix, sr, target_i=TARGET_I, target_tp=TARGET_TP):
    """mix: (n, ch) float array. Returns (mix, report); report carries the measured and applied
    numbers so a before/after test can assert on them instead of on raw output samples."""
    if not np.any(mix):
        return mix, {'measured_i': None, 'gain_db': 0.0, 'target_i': target_i, 'target_tp': target_tp,
                      'note': 'silent mix, nothing to measure'}
    measured_i, _ = _measure_integrated_lufs(mix, sr)
    gain_db = float(np.clip(target_i - measured_i, -MAX_GAIN_DB, MAX_GAIN_DB))
    gained = mix * (10 ** (gain_db / 20))
    limited = _limit(gained, sr, target_tp)
    return limited, {'measured_i': round(measured_i, 2), 'gain_db': round(gain_db, 2),
                      'target_i': target_i, 'target_tp': target_tp}

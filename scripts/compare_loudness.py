"""Before/after for engine/loudness.py (render.mix_audio's final gain stage): renders the bw-flash-vo
demo A edl's audio twice, once with the old peak-only scale and once with the new static-gain + alimiter,
and writes compare/before.m4a, compare/after.m4a and compare/report.json.

Writes to $TMPDIR-style output given as the first argument (default: ./compare-out). Needs the design-library media.
Run from the repo root: .venv/bin/python -I scripts/compare_loudness.py [out_dir]
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'engine'))
import render
import loudness
import paths


def _old_normalise(mix, sr):
    """What render.mix_audio did before this change: a plain peak scale, no loudness target."""
    pk = np.abs(mix).max()
    if pk > 0.89:
        mix = mix * (0.89 / pk)
    return mix, {'measured_i': None, 'gain_db': 0.0, 'note': 'old peak-only scale, no LUFS target'}


def main():
    demo = ROOT / 'styles' / 'bw-flash-vo' / 'demo' / 'A' / 'edl.json'
    edl = json.loads(demo.read_text())
    music = paths.media(edl['music']['path'])
    vo = paths.media(edl['voiceover']['path'])
    if not music.exists() or not vo.exists():
        print(paths.skip_reason(edl['music']['path'], edl['voiceover']['path']) + ' Skipping before/after.')
        return None

    compare = Path(sys.argv[1] if len(sys.argv) > 1 else 'compare-out')
    compare.mkdir(parents=True, exist_ok=True)

    real_normalise = render.loudnessmod.normalise
    try:
        render.loudnessmod.normalise = _old_normalise
        render.mix_audio(edl, compare / 'before.wav', str(music), str(vo))
    finally:
        render.loudnessmod.normalise = real_normalise
    render.mix_audio(edl, compare / 'after.wav', str(music), str(vo))

    report = {}
    for name in ('before', 'after'):
        wav = compare / f'{name}.wav'
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(wav), '-vn', '-ac', '2', '-ar', '44100',
                               '-f', 'f32le', '-'], capture_output=True).stdout
        x = np.frombuffer(raw, np.float32).reshape(-1, 2)
        measured_i, measured_tp = loudness._measure_integrated_lufs(x, 44100)
        report[name] = {
            'integrated_lufs': round(measured_i, 2),
            'true_peak_dbtp': round(measured_tp, 2),
            'sample_peak_dbfs': round(float(20 * np.log10(np.abs(x).max() + 1e-12)), 2),
        }
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(wav), '-c:a', 'aac', '-b:a', '160k',
                         str(compare / f'{name}.m4a')])
        wav.unlink()
    report['note'] = ('before is the old plain-peak-scale mix (no loudness target, see _old_normalise above); '
                       'after is engine/loudness.py: a single ffmpeg loudnorm measurement pass sets one static '
                       f'gain to {loudness.TARGET_I} LUFS integrated, then ffmpeg alimiter catches peaks at '
                       f'{loudness.TARGET_TP} dBTP.')
    (compare / 'report.json').write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))
    return report


if __name__ == '__main__':
    main()

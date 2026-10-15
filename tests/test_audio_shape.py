"""Tests and before/after audio for the options added on 13 Oct 2026 (audio_shape.py and sfx_library.py).

Run from the repo root:  .venv/bin/python -I tests/test_audio_shape.py
The before/after render needs the design-library media (see fixtures/README.md) and is skipped with a message when it is absent.
It writes before.m4a, after.m4a and report.json to tests/reels-2026-10-13/ only when run as a script (before = bw-flash-vo
demo A as it renders today, after = the same plan with the new style options on)."""
import copy, json, subprocess, sys, tempfile, unittest
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'tests' / 'reels-2026-10-13'
sys.path.insert(0, str(ROOT / 'engine'))
import audio_shape as A, sfx_library as lib, render, paths

SR = 44100
OPTS = {
    'intro_gate': {'rate_hz': 3.3, 'duty': 0.68, 'depth_db': -30},
    'vo_low_duck': {'cut_hz': 150, 'depth_db': -20, 'attack': 0.12, 'rise': 1.8, 'pad': 0.1},
    'hit_gaps': {'kinds': ['impact'], 'dur': 0.1, 'lead': 0.02, 'min_gain': 0.4},
}


def band_db(x, t0, t1, lo, hi):
    seg = x[int(t0 * SR):int(t1 * SR)]
    seg = seg.mean(1) if seg.ndim > 1 else seg
    X = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2
    f = np.fft.rfftfreq(len(seg), 1 / SR)
    return 10 * np.log10(X[(f >= lo) & (f < hi)].sum() + 1e-12)


class UnitTests(unittest.TestCase):
    def test_curves(self):
        g = A.gate_curve(SR * 4, 0.0, {'rate_hz': 4, 'duty': 0.5, 'depth_db': -30, 'until_s': 2.0})
        self.assertAlmostEqual(g[int(0.05 * SR)], 1.0, places=2)           # on slot
        self.assertAlmostEqual(g[int(0.18 * SR)], 10 ** (-30 / 20), places=2)  # off slot
        self.assertTrue(np.all(g[int(2.1 * SR):] == 1.0))                 # gate ends at until_s
        d = A.duck_curve(SR * 10, 0.0, [(2.0, 7.0)], {'depth_db': -20, 'attack': 0.1, 'rise': 2.0, 'pad': 0.0})
        self.assertAlmostEqual(20 * np.log10(d[int(3 * SR)]), -20, places=1)
        self.assertEqual(d[int(1 * SR)], 1.0)
        self.assertGreater(d[int(6.5 * SR)], d[int(5.5 * SR)])             # rising back before the end of the speech
        self.assertEqual(d[int(7.5 * SR)], 1.0)

    def test_unchanged_without_options(self):
        edl = {'sfx': [{'kind': 'impact', 't': 3.0, 'gain': 0.7}], 'music': {'start': 0, 'beat_period': 0.5}, 'duration': 5}
        self.assertEqual(A.plan(copy.deepcopy(edl), {}), {})
        self.assertEqual(A.shape_music('song.wav', edl, 'x.wav'), 'song.wav')    # nothing asked, file untouched

    def test_hit_gaps(self):
        edl = {'sfx': [{'kind': 'impact', 't': 3.0, 'gain': 0.7}, {'kind': 'whoosh', 't': 4, 'gain': 0.5}, {'kind': 'impact', 't': 0.05, 'gain': 0.7}]}
        self.assertEqual(A.add_hit_gaps(edl, OPTS['hit_gaps']), 1)             # the one at 0.05 s has no room for a gap
        gap = [e for e in edl['sfx'] if e['kind'] == 'gap'][0]
        self.assertAlmostEqual(gap['t'] + gap['dur'], 3.0 - 0.02, places=3)

    def test_low_duck_on_synthetic_music(self):
        t = np.arange(SR * 10) / SR
        x = (0.4 * np.sin(2 * np.pi * 60 * t) + 0.2 * np.sin(2 * np.pi * 1000 * t))
        stereo = np.stack([x, x], 1).astype(np.float32)
        with tempfile.TemporaryDirectory() as td:
            import soundfile as sf
            src = Path(td) / 's.wav'; sf.write(src, stereo, SR, subtype='FLOAT')
            edl = {'music': {'start': 0.0, 'beat_period': 0.5}, 'duration': 9.0, 'voiceover': {'start': 2}, 'words': [{'t0': 2.0, 't1': 6.0}],
                   'audio_shape': {'vo_low_duck': {'cut_hz': 150, 'depth_db': -20, 'attack': 0.1, 'rise': 1.0, 'pad': 0.0}}}
            out = A.shape_music(str(src), edl, Path(td) / 'o.wav')
            y, _ = sf.read(out)
        low_in, low_out = band_db(stereo, 2.5, 4.5, 20, 150), band_db(y, 2.5, 4.5, 20, 150)
        mid_in, mid_out = band_db(stereo, 2.5, 4.5, 500, 2000), band_db(y, 2.5, 4.5, 500, 2000)
        self.assertLess(low_out - low_in, -17)                                  # about -20 dB in the low band under the voice
        self.assertAlmostEqual(mid_out - mid_in, 0, delta=0.6)                  # mids untouched
        self.assertAlmostEqual(band_db(y, 7.5, 9, 20, 150) - band_db(stereo, 7.5, 9, 20, 150), 0, delta=0.6)   # back to normal after the speech


class LibraryInMixTest(unittest.TestCase):
    def test_library_style_option_tags_events(self):
        edl = {'sfx': [{'kind': 'whoosh', 't': 1.0, 'gain': 0.3}, {'kind': 'impact', 't': 2.0, 'gain': 0.7}, {'kind': 'click', 't': 3.0, 'gain': 0.4}]}
        n = lib.apply_to_edl(edl, {'enabled': True, 'map': {'whoosh': 'woosh', 'impact': 'outro-hit'}})
        self.assertEqual(n, 2)
        self.assertEqual([e.get('sample') for e in edl['sfx']], ['woosh', 'outro-hit', None])


def before_after():
    demo = ROOT / 'styles' / 'bw-flash-vo' / 'demo' / 'A' / 'edl.json'
    base = json.loads(demo.read_text())
    music = paths.media(base['music']['path']); vo = paths.media(base['voiceover']['path'])
    if not music.exists() or not vo.exists():
        print(paths.skip_reason(base['music']['path'], base['voiceover']['path']) + ' Skipping before/after.'); return None
    style = {'structure': {'intro_beats': 5}, 'audio_shape': OPTS, 'sfx_library': {'enabled': True, 'map': {'impact': 'outro-hit', 'whoosh': 'woosh', 'riser': 'riser', 'click': 'camera-click'}}}
    after = copy.deepcopy(base)
    lib.apply_to_edl(after, style['sfx_library'])
    done = A.plan(after, style)
    with tempfile.TemporaryDirectory() as td:
        shaped = A.shape_music(str(music), after, Path(td) / 'm.wav')
        for name, edl, song in (('before', base, str(music)), ('after', after, shaped)):
            render.mix_audio(edl, Path(td) / f'{name}.wav', song, str(vo))
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(Path(td) / f'{name}.wav'), '-c:a', 'aac', '-b:a', '96k', str(HERE / f'{name}.m4a')])
        import soundfile as sf
        b, _ = sf.read(Path(td) / 'before.wav'); a, _ = sf.read(Path(td) / 'after.wav')
        i0 = int(base['music']['start'] * SR); n = int((base['duration'] + 0.2) * SR)
        mb, ma = A._decode(str(music))[i0:i0 + n], A._decode(shaped)[i0:i0 + n]      # the music alone, before and after shaping
    ws = base['words']; vt0, vt1 = ws[0]['t0'], ws[-1]['t1']
    hits = [e['t'] for e in after['sfx'] if e['kind'] == 'gap' and e.get('at') == 'hit_gap']
    rep = {
        'applied': done, 'voiceover_span_s': [round(vt0, 2), round(vt1, 2)],
        'music_only_low_band_20_150Hz_db_under_voice': {'before': round(band_db(mb, vt0 + 0.3, vt0 + 2.3, 20, 150), 1), 'after': round(band_db(ma, vt0 + 0.3, vt0 + 2.3, 20, 150), 1)},
        'music_only_mid_band_500_3000Hz_db_under_voice': {'before': round(band_db(mb, vt0 + 0.3, vt0 + 2.3, 500, 3000), 1), 'after': round(band_db(ma, vt0 + 0.3, vt0 + 2.3, 500, 3000), 1)},
        'music_only_low_band_db_after_the_speech': {'before': round(band_db(mb, vt1 + 0.3, vt1 + 1.3, 20, 150), 1), 'after': round(band_db(ma, vt1 + 0.3, vt1 + 1.3, 20, 150), 1)},
        'music_only_intro_rms_db_per_50ms_before': [round(float(20 * np.log10(np.sqrt(np.mean(mb[int(i * .05 * SR):int((i + 1) * .05 * SR)] ** 2)) + 1e-9)), 1) for i in range(0, 44)],
        'music_only_intro_rms_db_per_50ms_after': [round(float(20 * np.log10(np.sqrt(np.mean(ma[int(i * .05 * SR):int((i + 1) * .05 * SR)] ** 2)) + 1e-9)), 1) for i in range(0, 44)],
        'low_band_20_150Hz_db_under_voice': {'before': round(band_db(b, vt0 + 0.3, vt0 + 2.3, 20, 150), 1), 'after': round(band_db(a, vt0 + 0.3, vt0 + 2.3, 20, 150), 1)},
        'mid_band_500_3000Hz_db_under_voice': {'before': round(band_db(b, vt0 + 0.3, vt0 + 2.3, 500, 3000), 1), 'after': round(band_db(a, vt0 + 0.3, vt0 + 2.3, 500, 3000), 1)},
        'intro_rms_db_per_50ms_before': [round(float(20 * np.log10(np.sqrt(np.mean(b[int(i * .05 * SR):int((i + 1) * .05 * SR)] ** 2)) + 1e-9)), 1) for i in range(0, 44)],
        'intro_rms_db_per_50ms_after': [round(float(20 * np.log10(np.sqrt(np.mean(a[int(i * .05 * SR):int((i + 1) * .05 * SR)] ** 2)) + 1e-9)), 1) for i in range(0, 44)],
        'hit_gap_times_s': hits,
        'sfx_with_library_sample': sorted({e['sample'] for e in after['sfx'] if e.get('sample')}),
    }
    (HERE / 'report.json').write_text(json.dumps(rep, indent=1))
    return rep


if __name__ == '__main__':
    r = unittest.main(exit=False, verbosity=1)
    rep = before_after()
    if rep:
        print(json.dumps({k: v for k, v in rep.items() if 'intro_rms' not in k and 'per_50ms' not in k}, indent=1))
    sys.exit(0 if r.result.wasSuccessful() else 1)

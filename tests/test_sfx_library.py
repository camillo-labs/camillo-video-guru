"""Tests for the sfx library loader. Run from the repo root: .venv/bin/python -I tests/test_sfx_library.py

Every test runs against a fixture index in a fresh temp folder (not the real design-library/sfx),
so these assertions do not depend on what is actually in the real library at the time, or on its
clearance state (build stage 5: the 13 real clips are all "unknown, personal and internal use
only until cleared", so a test asserting content against the real library would now assert
against an empty, filtered result instead of what it means to).
"""
import json, sys, tempfile, unittest
from pathlib import Path
import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'engine'))
import sfx, sfx_library as lib, gate

SR = 48000

# id -> duration, so _write_fixture and the tests below agree on what each clip actually holds.
_DURATIONS = {'camera-click': 0.40, 'riser': 2.00, 'woosh': 0.30, 'uncleared-clip': 0.20}

FIXTURE_ENTRIES = [
    {'name': 'Camera Click', 'id': 'camera-click', 'file': 'clicks-and-switches/camera-click.wav',
     'category': 'clicks-and-switches', 'tags': ['click', 'camera'], 'licence': 'CC0', 'credit': 'Fixture Audio'},
    {'name': 'Riser', 'id': 'riser', 'file': 'risers/riser.wav', 'category': 'risers', 'tags': ['riser'],
     'licence': 'CC BY', 'credit': 'Fixture Audio', 'attack_s': 0.05, 'peak_s': 0.4},
    {'name': 'Woosh', 'id': 'woosh', 'file': 'transitions/whoosh/woosh.wav', 'category': 'transitions/whoosh',
     'tags': ['whoosh'], 'licence': 'CC0', 'credit': 'Fixture Audio'},
    # no licence string that starts with a cleared prefix, and no credit: stays filtered out by
    # default, the same shape as the real 13 reel clips until they are cleared.
    {'name': 'Uncleared Clip', 'id': 'uncleared-clip', 'file': 'other/uncleared-clip.wav', 'category': 'other',
     'tags': [], 'licence': 'unknown, personal and internal use only until cleared'},
]


def _write_fixture(root):
    entries = [dict(e) for e in FIXTURE_ENTRIES]
    for e in entries:
        n = int(_DURATIONS[e['id']] * SR)
        t = np.arange(n) / SR
        tone = 0.3 * np.sin(2 * np.pi * 440 * t)
        if 'peak_s' in e:
            # a single, narrow envelope bump at the recorded peak_s, well above the steady tone,
            # so argmax(|x|) lands exactly where the metadata says the measured peak is, the way
            # a real transient would (test_mix_aligns_a_measured_peak_to_the_beat needs this).
            bump = 0.6 * np.exp(-0.5 * ((t - e['peak_s']) / 0.01) ** 2)
            x = tone + bump
        else:
            x = tone
        p = root / e['file']
        p.parent.mkdir(parents=True, exist_ok=True)
        sf.write(p, np.stack([x, x], 1), SR)
        e['duration'] = round(n / SR, 3)
    (root / 'index.json').write_text(json.dumps({'version': 1, 'effects': entries}))
    return entries


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        lib.ROOT = Path(self._tmp.name)
        _write_fixture(lib.ROOT)
        lib.index(reload=True)

    def test_index_and_queries(self):
        self.assertEqual(len(lib.index()), len(FIXTURE_ENTRIES))
        self.assertEqual(lib.find(name='Camera Click')[0]['category'], 'clicks-and-switches')
        self.assertTrue(lib.find(category='transitions/whoosh'))
        self.assertTrue(lib.find(tag='riser'))
        self.assertEqual(lib.resolve('tag:riser')['id'], 'riser')

    def test_load_returns_mono_at_engine_rate(self):
        x = lib.load('riser')
        self.assertEqual(x.ndim, 1)
        self.assertAlmostEqual(len(x) / sfx.SR, lib.find(name='riser')[0]['duration'], delta=0.01)
        self.assertLessEqual(np.abs(x).max(), 1.0)
        self.assertEqual(len(lib.load('woosh', dur=0.3)), int(0.3 * sfx.SR))

    def test_fallback_to_synth_when_missing(self):
        with tempfile.TemporaryDirectory() as td:
            lib.ROOT = Path(td); lib.index(reload=True)
            self.assertEqual(lib.index(), [])
            x = lib.load('tag:whoosh', fallback='whoosh', seed=3)
            np.testing.assert_allclose(x, sfx.SFX['whoosh'](seed=3))
            np.testing.assert_allclose(lib.load('impact'), sfx.SFX['impact'](seed=0))   # a synth name needs no fallback argument
            with self.assertRaises(KeyError):
                lib.load('no-such-effect')

    def test_mix_unchanged_without_sample_and_falls_back_with_missing_sample(self):
        ev = [{'kind': 'whoosh', 't': 0.2, 'gain': 0.5}, {'kind': 'impact', 't': 1.0}]
        base = sfx.mix(2.0, ev)
        with tempfile.TemporaryDirectory() as td:
            lib.ROOT = Path(td); lib.index(reload=True)
            fb = sfx.mix(2.0, [dict(e, sample='woosh') for e in ev])
        np.testing.assert_allclose(base, fb)                                           # empty library -> same synthesised audio

    def test_mix_uses_sample_when_present(self):
        base = sfx.mix(2.0, [{'kind': 'whoosh', 't': 0.2}])
        with_lib = sfx.mix(2.0, [{'kind': 'whoosh', 't': 0.2, 'sample': 'woosh'}])
        self.assertFalse(np.allclose(base, with_lib))
        self.assertGreater(np.abs(with_lib).max(), 0.1)

    def test_apply_to_edl_is_opt_in(self):
        edl = {'sfx': [{'kind': 'whoosh', 't': 0}, {'kind': 'tick', 't': 1}]}
        self.assertEqual(lib.apply_to_edl(edl, None), 0)
        self.assertNotIn('sample', edl['sfx'][0])
        self.assertEqual(lib.apply_to_edl(edl, {'enabled': True, 'map': {'whoosh': 'woosh'}}), 1)
        self.assertEqual(edl['sfx'][0]['sample'], 'woosh'); self.assertNotIn('sample', edl['sfx'][1])

    def test_cleared_filtering_is_the_default(self):
        self.assertIsNone(lib.resolve('uncleared-clip'))
        self.assertEqual(lib.find(name='uncleared-clip'), [])
        uncleared = lib.find(name='uncleared-clip', include_uncleared=True)[0]
        self.assertEqual(lib.resolve('uncleared-clip', include_uncleared=True)['id'], 'uncleared-clip')
        self.assertFalse(lib.is_cleared(uncleared))
        self.assertTrue(lib.is_cleared(lib.find(name='riser')[0]))
        # load() defaults to the same filter: an uncleared query falls back to the synthesiser
        # rather than ever reading the uncleared file.
        x = lib.load('uncleared-clip', fallback='hiss', seed=7)
        np.testing.assert_allclose(x, sfx.SFX['hiss'](seed=7))

    def test_offsets(self):
        e = lib.find(name='riser')[0]
        self.assertEqual(lib.offsets(e), (0.05, 0.4))
        self.assertEqual(lib.offsets({'id': 'no-offsets-recorded'}), (0.0, 0.0))

    def test_mix_aligns_a_measured_peak_to_the_beat(self):
        # 'riser' carries peak_s 0.4 in the fixture: its measured peak should land at t, not at
        # t + 0.4, the way an un-annotated sample's file start would.
        out = sfx.mix(3.0, [{'kind': 'riser', 't': 1.0, 'sample': 'riser', 'gain': 1.0}])
        mono = out[:, 0]
        peak_frame = int(np.abs(mono).argmax())
        self.assertAlmostEqual(peak_frame / sfx.SR, 1.0, delta=0.02)

    def test_licence_check_happy_and_unhappy_paths(self):
        # The plan's own acceptance test (an unindexed sample against 'sfx/index.json') passes
        # whether or not that relative path resolves, since a missing index and a found-but-not-
        # cleared sample both return False. This proves the gate on a path that does resolve, for
        # a cleared sample (should pass), an uncleared sample (should fail) and an unindexed
        # sample (should fail), all against the same real index.
        index_path = lib.ROOT / 'index.json'
        self.assertTrue(gate.licence_check({'sfx_events': [{'sample': 'riser'}]}, index_path))
        self.assertFalse(gate.licence_check({'sfx_events': [{'sample': 'uncleared-clip'}]}, index_path))
        self.assertFalse(gate.licence_check({'sfx_events': [{'sample': 'nope-not-in-index'}]}, index_path))
        # an event naming no sample at all (the synthesised default) never fails the gate.
        self.assertTrue(gate.licence_check({'sfx_events': [{'kind': 'whoosh', 't': 0}]}, index_path))


if __name__ == '__main__':
    unittest.main()

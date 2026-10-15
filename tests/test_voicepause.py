"""Tests for engine/voicepause.py.
Run from the repo root: .venv/bin/python -I tests/test_voicepause.py
"""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'engine'))
import voicepause as vp

SR = 48000


def _voice(dur=6.0, gap=(2.9, 3.1)):
    """A 220 Hz tone with a near-silent gap, so the quiet point is known."""
    t = np.arange(int(dur * SR)) / SR
    x = 0.4 * np.sin(2 * np.pi * 220 * t)
    x[(t >= gap[0]) & (t < gap[1])] *= 0.001
    return x.astype(np.float64)


class QuietPointTests(unittest.TestCase):
    def test_finds_the_gap_near_the_asked_time(self):
        q, level = vp.quiet_point(_voice(), SR, 3.15)
        self.assertGreaterEqual(q, 2.9)
        self.assertLessEqual(q, 3.1)
        self.assertLess(level, -60)

    def test_reports_loud_level_when_there_is_no_silence(self):
        t = np.arange(SR * 4) / SR
        x = 0.4 * np.sin(2 * np.pi * 220 * t)
        _, level = vp.quiet_point(x, SR, 2.0)
        self.assertGreater(level, -20)

    def test_search_outside_the_track_raises(self):
        with self.assertRaises(ValueError):
            vp.quiet_point(_voice(dur=2.0), SR, 50.0)


class InsertTests(unittest.TestCase):
    def test_track_grows_by_the_pause_and_the_gap_is_silent(self):
        vo = _voice()
        cuts = vp.plan_cuts(vo, SR, [(3.0, 1.2)])
        out = vp.insert_pauses(vo, SR, cuts)
        self.assertEqual(len(out), len(vo) + int(round(1.2 * SR)))
        q = cuts[0][0]
        gap = out[int((q + 0.07) * SR):int((q + 1.2 - 0.02) * SR)]
        self.assertEqual(float(np.abs(gap).max()), 0.0)

    def test_audio_outside_the_pause_is_unchanged(self):
        vo = _voice()
        cuts = vp.plan_cuts(vo, SR, [(3.0, 1.0)])
        out = vp.insert_pauses(vo, SR, cuts)
        q = cuts[0][0]
        a = int(1.0 * SR)                                              # well before the cut and its fade
        np.testing.assert_array_equal(out[:a], vo[:a])
        b = int((q + 0.3) * SR)                                        # after the fade-in, shifted by the pause
        np.testing.assert_allclose(out[b + SR:b + SR + 1000], vo[b:b + 1000])

    def test_fades_have_the_stated_lengths(self):
        x = np.full(SR * 4, 0.5)
        cuts = [(2.0, 1.0)]
        out = vp.insert_pauses(x, SR, cuts)
        fo, fi = int(0.06 * SR), int(0.015 * SR)
        edge = int(2.0 * SR)
        self.assertAlmostEqual(out[edge - fo - 5], 0.5)                # before the fade-out starts
        self.assertAlmostEqual(out[edge - 1], 0.0, delta=0.5 / fo * 2) # ends at silence
        start = edge + SR
        self.assertAlmostEqual(out[start], 0.0, delta=0.5 / fi * 2)    # fade-in starts at silence
        self.assertAlmostEqual(out[start + fi + 5], 0.5)

    def test_no_click_at_the_joins(self):
        vo = _voice()
        cuts = [(3.0, 1.0)]                                            # deliberately mid-tone, not in the gap
        out = vp.insert_pauses(vo, SR, cuts)
        self.assertLess(float(np.abs(np.diff(out)).max()), 0.05)       # a raw cut would jump by up to 0.8

    def test_stereo_shape_is_kept_and_no_cuts_is_a_copy(self):
        st = np.stack([_voice(), _voice()], 1)
        out = vp.insert_pauses(st, SR, [(3.0, 0.5)])
        self.assertEqual(out.shape, (len(st) + SR // 2, 2))
        same = vp.insert_pauses(st, SR, [])
        np.testing.assert_array_equal(same, st)
        self.assertIsNot(same, st)

    def test_two_pauses_accumulate(self):
        out = vp.insert_pauses(_voice(dur=8.0, gap=(2.9, 3.1)), SR, [(3.0, 1.0), (5.0, 0.5)])
        self.assertEqual(len(out), 8 * SR + int(1.5 * SR))


class TimeMapTests(unittest.TestCase):
    def test_shift_time(self):
        cuts = [(3.0, 1.0), (5.0, 0.5)]
        self.assertEqual(vp.shift_time(1.0, cuts), 1.0)
        self.assertEqual(vp.shift_time(4.0, cuts), 5.0)
        self.assertEqual(vp.shift_time(6.0, cuts), 7.5)

    def test_shift_words_keeps_input_and_stretches_a_straddling_word(self):
        words = [{'text': 'a', 't0': 1.0, 't1': 1.5}, {'text': 'b', 't0': 2.8, 't1': 3.2}]
        out = vp.shift_words(words, [(3.0, 1.0)])
        self.assertEqual(words[1]['t1'], 3.2)
        self.assertEqual((out[0]['t0'], out[0]['t1']), (1.0, 1.5))
        self.assertEqual(out[1]['t0'], 2.8)
        self.assertAlmostEqual(out[1]['t1'], 4.2)


if __name__ == '__main__':
    unittest.main()

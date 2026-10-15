"""Tests for engine/loudness.py (the final-mix gain stage render.mix_audio calls).
Run from the repo root: .venv/bin/python -I tests/test_loudness.py
"""
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'engine'))
import loudness

SR = 44100


def _tone(amp, dur=6.0, freq=440, sr=SR):
    t = np.arange(int(dur * sr)) / sr
    x = (amp * np.sin(2 * np.pi * freq * t)).astype(np.float32)
    return np.stack([x, x], 1)


class LoudnessTests(unittest.TestCase):
    def test_quiet_mix_is_boosted_toward_target(self):
        quiet = _tone(0.02)
        out, report = loudness.normalise(quiet, SR)
        self.assertGreater(report['gain_db'], 0)
        self.assertAlmostEqual(report['measured_i'] + report['gain_db'], loudness.TARGET_I, delta=0.3)
        self.assertGreater(np.abs(out).max(), np.abs(quiet).max())

    def test_loud_mix_is_turned_down_and_peaks_stay_under_the_ceiling(self):
        loud = _tone(0.95)
        out, report = loudness.normalise(loud, SR)
        self.assertLess(report['gain_db'], 0)
        ceiling = 10 ** (loudness.TARGET_TP / 20)
        self.assertLessEqual(np.abs(out).max(), ceiling * 1.05)   # alimiter headroom, not an exact brick wall

    def test_silent_mix_short_circuits(self):
        out, report = loudness.normalise(np.zeros((SR * 2, 2), np.float32), SR)
        self.assertIsNone(report['measured_i'])
        self.assertEqual(report['gain_db'], 0.0)
        np.testing.assert_array_equal(out, np.zeros((SR * 2, 2), np.float32))

    def test_gain_is_one_static_number_not_a_moving_curve(self):
        # A loud first half and a quiet second half should still get exactly one scalar gain
        # applied throughout, not something that rides the level the way dynamic loudnorm does:
        # the ratio between the two halves' RMS must survive the call unchanged. Measured a beat
        # in from the splice so the limiter's lookahead reaction to the two tones' arbitrary-phase
        # discontinuity (a real but tiny artifact of this synthetic test, not of real audio, which
        # is never two tones spliced with no crossfade) does not skew either window's RMS.
        x = _tone(0.6, dur=3.0)
        y = _tone(0.05, dur=3.0)
        mix = np.concatenate([x, y], axis=0)
        out, report = loudness.normalise(mix, SR)
        rms = lambda a: float(np.sqrt(np.mean(a.astype(np.float64) ** 2)))
        trim = int(0.05 * SR)
        ratio_in = rms(x[trim:-trim]) / rms(y[trim:-trim])
        n = len(x)
        ratio_out = rms(out[trim:n - trim]) / rms(out[n + trim:n + len(y) - trim])
        self.assertAlmostEqual(ratio_in, ratio_out, delta=0.05 * ratio_in)

    def test_limiter_keeps_an_impulse_at_its_sample_position(self):
        # alimiter's lookahead (the attack window) delays its output unless latency=true
        # compensates for it: without that flag an impulse at sample 44100 would come out
        # around sample 44320 (one attack_ms later), dragging the whole mix out of sync with
        # the picture and with the peak-aligned sfx sfx.mix() placed on the beat.
        n, pos = int(2 * SR), int(1.0 * SR)
        x = np.zeros((n, 2), np.float32)
        x[pos] = 0.5
        out = loudness._limit(x, SR, loudness.TARGET_TP)
        self.assertEqual(len(out), len(x))
        self.assertEqual(int(np.abs(out[:, 0]).argmax()), pos)


class FfmpegFailureTests(unittest.TestCase):
    """A failed ffmpeg pass must raise, never hand back a silently truncated or empty mix."""

    def _fake(self, returncode, stdout=b'', stderr=b''):
        return mock.Mock(return_value=subprocess.CompletedProcess(args=['ffmpeg'], returncode=returncode,
                                                                   stdout=stdout, stderr=stderr))

    def test_limiter_failure_raises_with_stderr(self):
        x = _tone(0.5, dur=1.0)
        with mock.patch.object(loudness.subprocess, 'run', self._fake(1, stderr=b'Unknown filter option boom')):
            with self.assertRaises(RuntimeError) as cm:
                loudness._limit(x, SR, loudness.TARGET_TP)
        self.assertIn('Unknown filter option boom', str(cm.exception))

    def test_limiter_length_mismatch_raises(self):
        x = _tone(0.5, dur=1.0)
        short = np.zeros((len(x) - 10, 2), np.float32).tobytes()
        with mock.patch.object(loudness.subprocess, 'run', self._fake(0, stdout=short)):
            with self.assertRaises(RuntimeError) as cm:
                loudness._limit(x, SR, loudness.TARGET_TP)
        self.assertIn('frames', str(cm.exception))

    def test_measurement_failure_raises_with_stderr(self):
        x = _tone(0.5, dur=1.0)
        with mock.patch.object(loudness.subprocess, 'run', self._fake(1, stderr=b'loudnorm exploded')):
            with self.assertRaises(RuntimeError) as cm:
                loudness.normalise(x, SR)
        self.assertIn('loudnorm exploded', str(cm.exception))

    def test_normalise_keeps_the_length_of_the_mix(self):
        x = _tone(0.3, dur=2.0)
        out, _ = loudness.normalise(x, SR)
        self.assertEqual(len(out), len(x))


if __name__ == '__main__':
    unittest.main()

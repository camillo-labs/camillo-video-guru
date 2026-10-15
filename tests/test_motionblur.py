"""Tests for engine/motionblur.py and the pan_blur effect.
Run from the repo root: .venv/bin/python -I tests/test_motionblur.py
"""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'engine'))
import motionblur as mb
import fx


def _bars(w=200, h=100):
    img = np.zeros((h, w, 3), np.uint8)
    img[:, 95:105] = 255            # a vertical white bar
    return img


class MappingTests(unittest.TestCase):
    def test_rule_from_motion_md(self):
        self.assertEqual(mb.sigma_for_velocity(0), 0)
        self.assertEqual(mb.sigma_for_velocity(5), 0)                 # 0.6 px snaps to no blur
        self.assertAlmostEqual(mb.sigma_for_velocity(50, quantise=False), 6.0)
        self.assertEqual(mb.sigma_for_velocity(50), 6)                # 0.12 * 50 = 6, a preset step
        self.assertEqual(mb.sigma_for_velocity(100), 11)              # 12 snaps to 11
        self.assertEqual(mb.sigma_for_velocity(-100), 11)             # direction does not matter

    def test_cap_at_22(self):
        self.assertEqual(mb.sigma_for_velocity(180), 22)              # 21.6 snaps to 22
        self.assertEqual(mb.sigma_for_velocity(1000), 22)
        self.assertEqual(mb.sigma_for_velocity(1000, quantise=False), 22.0)

    def test_always_a_preset_step_and_never_decreasing(self):
        last = -1
        for v in range(0, 400, 3):
            s = mb.sigma_for_velocity(v)
            self.assertIn(s, mb.STEPS)
            self.assertGreaterEqual(s, last)
            last = s

    def test_velocity_is_a_central_difference(self):
        self.assertAlmostEqual(mb.velocity(lambda f: 12.0 * f, 7), 12.0)
        self.assertAlmostEqual(mb.velocity(lambda f: 3.0, 7), 0.0)


class BlurTests(unittest.TestCase):
    def test_slow_move_returns_the_image_untouched(self):
        img = _bars()
        self.assertIs(mb.directional_blur(img, 3, 0), img)

    def test_horizontal_move_blurs_across_x_only(self):
        img = _bars()
        out = mb.directional_blur(img, 80, 0)
        self.assertGreater(int(out[50, 80].max()), 0)                 # bar smeared sideways
        self.assertLess(int(out[50, 100].max()), 255)
        np.testing.assert_array_equal(out[0], out[99])                # rows identical: nothing moved vertically

    def test_vertical_move_blurs_across_y_only(self):
        img = np.zeros((200, 100, 3), np.uint8); img[95:105, :] = 255   # a horizontal bar, 100 wide, 200 tall
        out = mb.directional_blur(img, 0, 80)
        self.assertGreater(int(out[80, 50].max()), 0)                 # bar smeared up
        self.assertEqual(out.shape, (200, 100, 3))
        np.testing.assert_array_equal(out[:, 0], out[:, 99])

    def test_dominant_axis_wins(self):
        img = _bars()
        out = mb.directional_blur(img, 80, 10)
        self.assertGreater(int(out[50, 80].max()), 0)

    def test_faster_move_blurs_more(self):
        img = _bars()
        spread = lambda o: int((o[50, :, 0] > 8).sum())
        self.assertGreater(spread(mb.directional_blur(img, 150, 0)), spread(mb.directional_blur(img, 60, 0)))


class PanBlurEffectTests(unittest.TestCase):
    def _run(self, u, **p):
        img = _bars()
        k = {'u': u, 'x': 0.0, 't': u * 0.5, 'span': 0.5}
        ctx = {'w': 200, 'h': 100, 'fps': 30, 'frame': 0}
        return fx.FX['pan_blur'](img, k, dict({'distance': 0.5}, **p), ctx)

    def test_registered(self):
        self.assertIn('pan_blur', fx.FX)

    def test_fast_start_is_blurrier_than_the_eased_end(self):
        spread = lambda o: int((o[50, :, 0] > 8).sum())
        self.assertGreater(spread(self._run(0.05)), spread(self._run(0.95)))   # out_cubic: fast first, slow last

    def test_end_of_the_move_is_sharp(self):
        out = self._run(1.0)
        self.assertEqual(out.shape, (100, 200, 3))
        self.assertEqual(int(out[50].max()), 255)


if __name__ == '__main__':
    unittest.main()

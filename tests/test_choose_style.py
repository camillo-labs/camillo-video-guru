"""Regression tests for the style chooser and the auto-mode render settings.

Run: cd edits && .venv/bin/python -I tests/test_choose_style.py
Uses the feature vectors recorded in the committed tests/*/auto/decisions.json, so no footage is read.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'engine'))
import choose_style  # noqa: E402


def features(test):
    return json.load(open(ROOT / 'tests' / test / 'auto' / 'decisions.json'))['features']


class ChooseStyleTest(unittest.TestCase):
    def test_green_label_edgy_picks_bw_flash_vo(self):
        b = dict(features('green-label'), mood='edgy')
        self.assertEqual(choose_style.choose(b)['style'], 'bw-flash-vo')

    def test_heritage_and_calm_pick_lyric_word_beat(self):
        for test, mood in (('fontainebleau', 'heritage'), ('dachshunds', 'calm')):
            b = dict(features(test), mood=mood)
            self.assertEqual(choose_style.choose(b)['style'], 'lyric-word-beat', test)

    def test_no_mood_green_label_is_no_fit(self):
        d = choose_style.choose(dict(features('green-label'), mood=None))
        self.assertIsNone(d['style'])
        self.assertTrue(d['gap'])

    def test_registry_is_six_named_styles(self):
        self.assertNotIn('a03a-fontainebleau', choose_style.STYLE_REGISTRY)
        for s in choose_style.STYLE_REGISTRY:
            self.assertTrue((ROOT / 'styles' / s / 'style.json').exists(), s)


class AutoAspectTest(unittest.TestCase):
    def test_auto_mode_defaults_to_vertical(self):
        src = (ROOT / 'engine' / 'make_edit.py').read_text()
        self.assertIn("aspect = a.aspect or ('9:16' if decision is not None", src)

    def test_decisions_rewritten_after_music_pick(self):
        src = (ROOT / 'engine' / 'make_edit.py').read_text()
        pick = src.index("decision['music_pick'] = picked")
        self.assertIn("json.dump({'features': b, **decision}, open(out / 'decisions.json'", src[pick:pick + 400])


if __name__ == '__main__':
    unittest.main()

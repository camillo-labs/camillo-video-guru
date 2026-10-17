"""Tests for the storyboard stage. Run from the repo root: .venv/bin/python -I tests/test_storyboard.py

The media-free tests use a fixture EDL. The frame test skips unless the fontainebleau media is present."""
import json, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'engine'))
import storyboard, paths

EDL = {
    'style': 'fixture', 'fps': 30, 'aspect': '9:16', 'duration': 12.0,
    'music': {'beat_period': 0.5, 'drops_in_window': [6.0]},
    'shots': [
        {'role': 'intro', 't0': 0.0, 't1': 3.0, 'clip': 'a.mp4', 'src_in': 1.0, 'speed': 1.0},
        {'role': 'mid', 't0': 3.0, 't1': 6.0, 'clip': 'b.mp4', 'src_in': 2.0, 'speed': 2.0},
        {'role': 'drop', 't0': 6.0, 't1': 9.0, 'clip': 'c.mp4', 'src_in': 0.0, 'speed': 1.0},
        {'role': 'outro', 't0': 9.0, 't1': 12.0, 'clip': 'a.mp4', 'src_in': 4.0, 'speed': 1.0},
    ],
    'events': [{'fx': 'flash', 't0': 3.0, 't1': 3.2, 'tc': 3.0, 'at': 'cut'},
               {'fx': 'slow_zoom', 't0': 0.0, 't1': 3.0, 'tc': 0.0, 'at': 'shot'}],
    'sfx': [{'kind': 'click', 't': 3.0, 'gain': 0.2}],
    'words': [{'text': 'Hello', 't0': 4.0, 't1': 4.4, 'phrase': 0, 'line': 0},
              {'text': 'world', 't0': 4.4, 't1': 4.8, 'phrase': 0, 'line': 0}],
}


class Moments(unittest.TestCase):
    def test_deterministic_and_sorted(self):
        a = storyboard.select_moments(EDL); b = storyboard.select_moments(json.loads(json.dumps(EDL)))
        self.assertEqual(a, b)
        self.assertEqual([m['t'] for m in a], sorted(m['t'] for m in a))

    def test_expected_kinds(self):
        kinds = {k for m in storyboard.select_moments(EDL) for k in m['kinds']}
        self.assertEqual(kinds, {'hook', 'section', 'drop', 'transition', 'caption', 'end'})

    def test_hook_first_and_end_last(self):
        m = storyboard.select_moments(EDL)
        self.assertIn('hook', m[0]['kinds']); self.assertIn('end', m[-1]['kinds'])
        self.assertLess(m[0]['t'], 2.0)

    def test_cap_keeps_hook_end_drop(self):
        m = storyboard.select_moments(EDL, cap=4)
        self.assertEqual(len(m), 4)
        kinds = {k for x in m for k in x['kinds']}
        self.assertTrue({'hook', 'end', 'drop'} <= kinds)


class Panels(unittest.TestCase):
    def setUp(self): self.panels = storyboard.build_panels(EDL, {'style': 'fixture', 'score': 0.9})

    def test_metadata(self):
        p = next(x for x in self.panels if 'caption' in x['kinds'])
        self.assertEqual(p['text'], 'Hello world')
        self.assertEqual(p['frame'], round(p['t'] * 30))
        self.assertIn('mid', p['section'])
        self.assertEqual(p['source'], 'b.mp4 @ %ss' % round(2.0 + (p['t'] - 3.0) * 2.0, 2))
        tr = next(x for x in self.panels if 'transition' in x['kinds'])
        self.assertIn('flash', tr['effect']); self.assertIn('click', tr['sfx'])
        dr = next(x for x in self.panels if 'drop' in x['kinds'])
        self.assertEqual(dr['beat'], 'drop')
        self.assertTrue(all(x['intent'].endswith('.') for x in self.panels))

    def test_html(self):
        meta = {'title': 'Storyboard', 'subtitle': 'x <b>', 'mode': 'plan'}
        for i, p in enumerate(self.panels): p['image'] = f'f/{i}.jpg'
        h = storyboard.render_html(self.panels, meta)
        self.assertIn('<h1>Storyboard</h1>', h)
        self.assertLess(h.index('<h1>'), h.index('<img'))           # opens on the title
        self.assertEqual(h.count('<img'), len(self.panels))
        self.assertIn('x &lt;b&gt;', h)                              # escaped
        self.assertIn('A4 landscape', h)
        self.assertEqual(h.count('class="page"'), -(-len(self.panels) // 6))


@unittest.skipIf(paths.skip_reason('tests/fontainebleau/assets/music/Court-of-the-Queen.mp3'), 'fontainebleau media not available')
class WithMedia(unittest.TestCase):
    def test_plan_frames_and_files(self):
        edl = json.load(open(ROOT / 'tests/fontainebleau/edl.json'))
        miss = [s['clip'] for s in edl['shots'] if not paths.media(s['clip']).exists()]
        if miss: self.skipTest('clips missing: ' + miss[0])
        with tempfile.TemporaryDirectory() as d:
            r = storyboard.storyboard(edl, d, pdf=False)
            self.assertTrue((Path(d) / 'storyboard.html').exists())
            data = json.load(open(Path(d) / 'storyboard.json'))
            self.assertEqual(len(data['panels']), len(r['panels']))
            for p in data['panels']: self.assertTrue((Path(d) / p['image']).exists())


if __name__ == '__main__':
    unittest.main()

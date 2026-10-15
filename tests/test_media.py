"""Tests that need the design-library media (generated test clips and music, see fixtures/README.md).
They skip with a clear message when the media is absent.
Run from the repo root: .venv/bin/python -I tests/test_media.py
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'engine'))
import paths

CLIPS, MUSIC = '_testdata/clips/A_9x16', '_testdata/music/house128.wav'
VO = '_testdata/vo/vo1.aiff'


class PathsTests(unittest.TestCase):
    def test_absolute_and_existing_paths_pass_through(self):
        self.assertEqual(paths.media('/x/y.wav'), Path('/x/y.wav'))
        self.assertEqual(paths.media(__file__), Path(__file__))

    def test_relative_paths_resolve_under_the_media_root(self):
        if paths.MEDIA_ROOT is None:
            self.skipTest('no media root on this machine')
        self.assertEqual(paths.media('_testdata/x'), paths.MEDIA_ROOT / '_testdata/x')

    def test_skip_reason_names_the_missing_file_and_the_variable(self):
        msg = paths.skip_reason('definitely/not/here.wav')
        self.assertIn('definitely/not/here.wav', msg)
        self.assertIn('VIDEO_ENGINE_MEDIA', msg)
        self.assertIsNone(paths.skip_reason(__file__))


_why = paths.skip_reason(CLIPS, MUSIC, VO, 'tests/green-label/assets')


@unittest.skipIf(_why, _why)
class MediaTests(unittest.TestCase):
    def test_auto_plan_only_writes_an_edl(self):
        with tempfile.TemporaryDirectory() as td:
            r = subprocess.run([sys.executable, '-I', str(ROOT / 'engine/make_edit.py'), '--style', 'auto',
                                '--clips', str(paths.media(CLIPS)), '--music', str(paths.media(MUSIC)),
                                '--captions', 'one\ntwo\nthree', '--duration', '8', '--aspect', '9:16',
                                '--plan-only', '--out', td], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr[-800:])
            edl = json.loads((Path(td) / 'edl.json').read_text())
            self.assertGreater(len(edl['shots']), 2)
            self.assertTrue((Path(td) / 'decisions.json').exists())

    def test_demo_edl_paths_resolve_to_real_files(self):
        import make_edit
        edl = json.loads((ROOT / 'styles/bw-flash-vo/demo/A/edl.json').read_text())
        make_edit.resolve_edl_media(edl)
        self.assertTrue(Path(edl['music']['path']).exists())
        self.assertTrue(Path(edl['shots'][0]['clip']).exists())

    def test_demo_mix_lands_on_the_loudness_target(self):
        import render, loudness
        edl = json.loads((ROOT / 'styles/bw-flash-vo/demo/A/edl.json').read_text())
        music, vo = paths.media(edl['music']['path']), paths.media(edl['voiceover']['path'])
        with tempfile.TemporaryDirectory() as td:
            wav = Path(td) / 'mix.wav'
            render.mix_audio(edl, wav, str(music), str(vo))
            raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(wav), '-ac', '2', '-ar', '44100', '-f', 'f32le', '-'],
                                 capture_output=True).stdout
        x = np.frombuffer(raw, np.float32).reshape(-1, 2)
        lufs, _ = loudness._measure_integrated_lufs(x, 44100)
        self.assertAlmostEqual(lufs, loudness.TARGET_I, delta=0.6)


if __name__ == '__main__':
    unittest.main()

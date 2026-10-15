# Third-party notices

## Will Leikauskas's making-short-videos (MIT)

Source: `making-short-videos` (https://github.com/Mokzy/making-short-videos), a Remotion, ffmpeg and Python
skill by Will Leikauskas. The repository's licence file names the copyright holder as "Mokzy", which is
reproduced as written below.

Parts of this repository are adapted from it:

| Our file | Adapted from | What was taken |
| --- | --- | --- |
| `engine/loudness.py` | `scripts/mix_soundtrack.py` (final section) | One loudnorm measurement pass, one static gain to the target, then a limiter. Never single-pass loudnorm. |
| `engine/motionblur.py`, the `pan_blur` effect in `engine/fx.py` | `references/motion.md` (fast-moves rule) and `remotion-kit/mblur.tsx` | The 0.12 px of blur per px/frame rule, the cap of 22 px, the nine preset steps, the dominant-axis choice and the central-difference velocity. |
| `engine/voicepause.py` | `scripts/mix_soundtrack.py` (voice section) | Pauses placed at the quietest 10 ms window, with a 60 ms fade-out and a 15 ms fade-in. |
| `research/from-will.md`, `research/compare-making-short-videos-2026-10-15.md` | The whole repository | Notes on the ideas, not code. |

The code is rewritten for this engine's own structures and tested here. Where a file is adapted, its docstring
says so.

```
MIT License

Copyright (c) 2026 Mokzy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## HyperFrames ridged-burn shader (Apache-2.0): not used

Will's `scripts/burn_transition.py` is a numpy port of the HyperFrames `ridged-burn` shader (Copyright HeyGen,
Apache License 2.0, https://github.com/heygen-com/hyperframes) and is the one file in his repository that is not
MIT. Nothing from it is in this repository. If it is ever ported, add the Apache-2.0 notice, state the changes
and keep the file under Apache-2.0.

## Fonts and sound effects

Fonts in `engine/assets/fonts/` carry their own SIL Open Font Licence texts next to them (see `LICENSES.md`
there). The sound effect index in `sfx/` records each clip's licence. All 13 clips are marked "unknown,
personal and internal use only until cleared", and `engine/gate.py` fails a render that uses an uncleared clip
unless told otherwise.

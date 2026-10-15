# Video engine

Cam's video edit engine. Give it clips, a song and some caption text. It returns a short video in one of
several learned editing styles, with cuts, moves, transitions, sound effects and captions placed on the new
song's beats.

It started in `design-library/edits` and now lives here on its own. It also holds the best ideas from Will
Leikauskas's `making-short-videos` repo, with credit.

## What it does

- Reads the song (tempo, beat grid, downbeats, drops, phrases) and the clips (scenes, motion, faces, focus).
- With `--style auto` it scores every style against the footage and brief and picks one. It writes
  `decisions.json` with the score, the runner-up and, when nothing fits, the reason.
- Plans an edit decision list (`edl.json`) from the style's rules, then renders it with ffmpeg and OpenCV.
- Checks the result: beat alignment, safe areas, flash frequency, dead frames and sound effect licences.
- Mixes the sound to -14 LUFS with a limiter at -1 dBTP.

## Layout

| Folder | What is in it |
| --- | --- |
| `engine/` | The code. `make_edit.py` is the entry point. `engine/README.md` explains the style file format. |
| `engine/ext/` | Style-specific effects, captions and overlays. |
| `styles/` | One folder per style: `style.json`, a README with the measured rules, `analysis.json`, `filmcraft.md`. |
| `lessons/`, `research/` | What each reference video taught the engine, plus plans and reviews. |
| `tests/` | Unit tests, and one folder per real test project with its plan and reports. |
| `scripts/` | Setup, test media generation, credits, contact sheets, gate report, loudness comparison. |
| `sfx/` | The sound effect index. The WAV files are not in git. |
| `examples/explainer/` | The scripts that made the engine's own explainer film. Kept for reference, paths not updated. |
| `fixtures/README.md` | Where the media lives and how to get it back. |
| `THIRD_PARTY.md` | Licences and credit for what was adapted. |

Older notes under `styles/` and `tests/` still say `edits/` and `.venv` in their old places. Read `edits/` as
the repo root.

## Set up

You need Python 3 and ffmpeg on the PATH.

```
scripts/setup.sh                 # .venv, requirements.txt, the Swift Vision helper on macOS
scripts/setup.sh --testdata      # also builds the generated test songs and clips
```

Media is found through `engine/paths.py`. By default it uses `/Users/student/dev/design-library/edits`. Set
`VIDEO_ENGINE_MEDIA` to use another folder. Voiceover transcription uses a local Whisper environment, set with
`VIDEO_ENGINE_WHISPER_PY`.

## Render an edit

```
.venv/bin/python engine/make_edit.py --style auto --mood calm \
    --clips ./footage --music ./song.mp3 --captions captions.txt \
    --duration 15 --aspect 9:16 --res 720 --out ./out
```

`--out` gets `edit.mp4`, `edl.json`, `song.json`, `check.json` and `decisions.json`. Edit the plan and re-render
it with `--edl out/edl.json`. Use `--plan-only` to write only the plan. `--list` shows the styles, effects and
caption kinds. Without a mood hint the chooser may say no style fits. Pass `--mood`, `--audience` or
`--caption-kind` to help it, or name a style with `--style lyric-word-beat`.

## From Will Leikauskas's making-short-videos (MIT)

| Idea | Where |
| --- | --- |
| One measured static gain to -14 LUFS, then a limiter, instead of a peak scale | `engine/loudness.py` |
| Motion blur from speed: 0.12 px per px/frame, capped at 22 | `engine/motionblur.py` and the `pan_blur` effect |
| Voice pauses at the quietest 10 ms with short fades | `engine/voicepause.py` (a library, not wired in yet) |

The comparison, what was left out and why are in `research/from-will.md`. Licence text is in `THIRD_PARTY.md`.

## Test

```
.venv/bin/python -m unittest discover -s tests
```

Tests that need the design-library media skip with a message when it is absent. See `fixtures/README.md`.

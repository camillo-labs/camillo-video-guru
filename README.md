# short-videos

Will and Cam's shared kit for short videos: reels, ads, explainers and motion graphics. It has two parts and one
Claude Code skill that picks between them.

- **The engine** (`engine/`, `styles/`). Give it clips, a song and some caption text. It returns a finished cut in
  one of several learned editing styles, with cuts, moves, transitions, sound effects and captions placed on the
  song's beats, and checks its own render.
- **The playbook** (`references/`, `remotion-kit/`, `scripts/`). For a bespoke, voiceover-led piece built in
  Remotion: study a reference reel, lock the script, generate the voice, keep one visual language, mix at fixed
  levels, check every number.

`SKILL.md` is what Claude reads first. It says which part to use and holds the rules both share.

## Install as a Claude Code skill

```
git clone https://github.com/Mokzy/short-videos.git ~/.claude/skills/making-short-videos
```

Or clone it anywhere and link it in. On Windows:
`cmd /c mklink /J %USERPROFILE%\.claude\skills\making-short-videos <clone>`. Restart Claude Code and ask for a video.

## Layout

| Path | What is in it |
| --- | --- |
| `SKILL.md` | Which part to use, the shared sound and QA rules, the red flags |
| `engine/` | The edit engine. `make_edit.py` is the entry point. `engine/README.md` explains the style file format |
| `engine/ext/` | Style-specific effects, captions and overlays |
| `styles/` | One folder per style: `style.json`, a README with the measured rules, `analysis.json`, `filmcraft.md` |
| `references/` | The playbook: making it yours, reference study, visual language, motion, sound, toolchain, sources |
| `references/lessons.md` | The Fontainebleau ad, round by round: what was said, the root cause, the fix |
| `remotion-kit/` | Motion blur, shots and word-timed captions for Remotion |
| `scripts/` | Reference analysis, ElevenLabs, the soundtrack mixer, dead frames, contact sheets, side-by-sides, gate report, credits, setup |
| `lessons/`, `research/` | What each reference video taught the engine, plus plans, reviews and comparisons |
| `tests/` | Unit tests, and one folder per real test project with its plan and reports |
| `sfx/` | The sound effect index. The WAV files are not in git |
| `examples/explainer/` | The scripts that made the engine's own explainer film. Kept for reference, paths not updated |
| `fixtures/README.md` | Where the media lives and how to get it back |

Older notes under `styles/` and `tests/` still say `edits/` and `.venv` in their old places. Read `edits/` as the
repo root.

## Set up

Both parts need ffmpeg on the PATH.

Engine, Python 3:

```
scripts/setup.sh                 # macOS/Linux: .venv, requirements.txt, the Swift Vision helper on macOS
scripts/setup.sh --testdata      # also builds the generated test songs and clips
```

On Windows: `py -m venv .venv` then `.venv\Scripts\pip install -r requirements.txt`, and run everything with
`.venv\Scripts\python`. The Vision helpers are macOS only; without them the engine falls back to a saliency
focus point.

Media is found through `engine/paths.py`. Set `VIDEO_ENGINE_MEDIA` to the folder that holds `_testdata/` and
`tests/*/assets/`. Voiceover transcription uses a local Whisper environment, set with `VIDEO_ENGINE_WHISPER_PY`.

Playbook: Node 20+ and a Remotion project (`npx create-video@latest`); Python with `numpy` and `matplotlib`; for
studying a reference, `pip install demucs faster-whisper yt-dlp`; an ElevenLabs key in `ELEVENLABS_API_KEY` for
voice, music and sound effects.

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

## Test

```
.venv/bin/python -m unittest discover -s tests
```

Tests that need the media skip with a message when it is absent. See `fixtures/README.md`.

## Next

`research/from-will.md` lists playbook ideas not yet in the engine (Demucs when learning a style, 4x subframe
motion blur, band-limited sound effects, the red flags as gate checks, wiring in voice pauses). The end of
`research/compare-making-short-videos-2026-10-15.md` lists engine ideas the playbook could use (style files,
low-band voice ducking, the post-render gates).

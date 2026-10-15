# Sound effect library

Real recorded effects for the video systems, cut from two short reels Cam downloaded on 13 October 2026. The reels show each effect's name on screen as a scrolling waveform, and the clips here carry those names. 13 clips, 48 kHz 24-bit WAV, stereo, about 5 MB in all.

## Provenance and licence

| Source reel | Downloaded | Role |
| --- | --- | --- |
| `2b7b86e46eaf4886a19f5c5a342a7d92.MP4` (@mr.biss, "Sounds you need in your next edits") | 13 Oct 2026 22:12 | primary source of every clip |
| `aad7a9353ad8440f88e31cd76b65f48c.MP4` (@lorenzoadams_photography, "SFX you need Vol 1") | 13 Oct 2026 22:29 | same twelve effects in the same order, a re-post. All 11 audio segments start and end within 10 ms of the primary's and the end sting correlates at 0.9999, so it adds nothing new |

Both reels come from social media. **Licence: unknown, personal and internal use only until cleared.** Do not ship these clips inside anything that leaves Cam's own systems until the licence is cleared with the creators. The raw reels and the work folder (`edits/work/`) are not in git, and neither are the WAV files (see below).

## What is in it

`index.json` has one entry per clip: name, id, file, category, duration, peak_dbfs, lufs, loudness_limited_by_peak, sample_rate, channels, source_reel, timestamp_in_source (start and end in the primary reel, in seconds), tags, licence and an optional note.

| Category folder | Clips |
| --- | --- |
| `transitions/whoosh` | cinematic-woosh, woosh |
| `impacts` | outro-hit |
| `risers` | riser |
| `clicks-and-switches` | counter, camera-click |
| `ui` | 8-bit-talking, nextel, digital-text, shine |
| `other` | old-flash, night-vision, bicycle-chain |
| `glitches`, `ambience` | empty, ready for the next reel |

Names are the on-screen names in lowercase kebab case. The reel spells it "Woosh" and "Cinematic Woosh", and that spelling is kept. The categories are my call from how each effect sounds, so move a clip if you disagree and rerun the script.

Two things to know. `outro-hit` is not on the reel's list. It is the end-card sting the reel wrapper adds, and the same sound is the boom after the end card of the edit-walkthrough reel (correlation 0.9997), but it is a clean sub boom so it is kept and tagged `end-card-sting`. `8-bit-talking` starts at 0.00 s of the reel, so its first few milliseconds may have been cut by the reel's own start.

## How it was made

Each name was read from the contact sheets and crops of the reel. Each effect's start and end came from the audio (silence gaps and onsets, many gaps are digital silence) aligned to the order of the names, with the waveform in the video as a cross-check. Each clip has 5 ms of padding either side, 5 ms fades in and out, and a gain to -16 LUFS integrated measured with ffmpeg ebur128. Short sparse effects such as clicks would clip at that gain, so the gain is capped at a -1 dBFS sample peak. Those clips (`loudness_limited_by_peak: true` in the index) end up between -16.5 and -21.9 LUFS. That is correct behaviour for a click, which is loud in peak and quiet in loudness.

The effects are ordered in the reel as: 8 Bit Talking, Old Flash, Cinematic Woosh, Night Vision, Nextel, Digital Text, Riser, Counter, Bicycle Chain, Camera Click, Shine, Woosh. `build_from_reels.py` holds the table of start and end times and reproduces everything:

```
mkdir -p edits/work/reels-2026-10-13/2b7b86 && cp ~/Downloads/2b7b86e46eaf4886a19f5c5a342a7d92.MP4 edits/work/reels-2026-10-13/2b7b86/src.mp4
edits/.venv/bin/python -I sfx/build_from_reels.py
```

## Using it from the edit engine

The loader is `edits/engine/sfx_library.py` and the synthesised effects in `edits/engine/sfx.py` are the fallback, so nothing breaks if the WAV files are absent.

```python
import sfx_library as lib
lib.find(category='transitions/whoosh')     # index entries
lib.find(tag='riser')
x = lib.load('camera-click')                # mono float array at the engine rate
x = lib.load('tag:whoosh', fallback='whoosh')
```

In a style, switch it on per effect kind. Without the block the style renders as before:

```json
"sfx_library": {"enabled": true, "map": {"whoosh": "woosh", "impact": "outro-hit", "riser": "riser", "click": "camera-click"}}
```

Set `SFX_LIBRARY=/other/path` to point the loader at another copy. Tests are `edits/tests/test_sfx_library.py` and `edits/tests/reels-2026-10-13/test_audio_shape.py`.

## WAV files are not in git

The repo tracks no audio files (its tracked media are the test videos), so `sfx/**/*.wav` is gitignored. `index.json`, this README and the build script are committed. To get the WAV files on another machine, copy the reel into the work folder as above and run the script.

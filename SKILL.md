---
name: camillo-video-guru
description: Use when making or improving a short video, reel, ad, explainer, launch or product video, promo or motion graphic (9:16 or other), whether cutting clips to a song in a learned edit style or building a voiceover-led piece with Remotion, HyperFrames or ffmpeg, especially with maps or data, real footage, generated music or sound effects, or a reference reel to match; or when someone says a cut looks AI-made, templated, cheap, rushed, sudden or badly mixed.
---

# Camillo Video Guru

## Overview

Two tools in one repo, sharing one set of sound and QA rules. **The core principle: decide your own look first, then keep one visual language, keep everything moving, mix the sound at fixed levels, and check every number.** Viewers judge on a phone, and they stop at anything that feels templated, jarring or wrong.

| You have | Use | Start at |
|---|---|---|
| Clips and a song, and want a cut in a known style (montage, lyric or HUD edit, talking-head split, kinetic explainer) | **The engine** | `engine/make_edit.py --style auto` |
| A storyboard of an edit's key frames, to review before the full render or to share with a client | **The engine's storyboard stage** | `engine/make_edit.py --plan-only --storyboard`, or `engine/storyboard.py out/edl.json` (`engine/README.md`) |
| A story to tell over a voiceover (ad, explainer, fundraising film, maps or data) | **The playbook** | The workflow below, `remotion-kit/` |
| A launch or product video for an app, tool or repo | **The engine** for screen captures and kinetic text cut to music (`kinetic-card-explainer`, `talking-head-split`); **the playbook** when a voiceover tells the story | If the brief doesn't say whether there's a voiceover, ask |
| A reference reel to match | Measure it first (`scripts/analyse_reference.py`, `references/reference-study.md`) | Then learn it as an engine style (`engine/README.md`) or build it with the playbook |

## The engine

```
python engine/make_edit.py --style auto --mood calm --clips ./footage --music ./song.mp3 \
    --captions captions.txt --duration 15 --aspect 9:16 --res 720 --out ./out
```

- Run Python from the repo's `.venv` (`.venv\Scripts\python` on Windows). Set `VIDEO_ENGINE_MEDIA` for test media and `VIDEO_ENGINE_WHISPER_PY` for voiceover transcription.
- `--list` shows the styles, effects, caption kinds, overlays and sound effects. `--style auto` scores every style and writes `decisions.json`; if it says nothing fits, pass `--mood`, `--audience` or `--caption-kind`, or name a style.
- `--voiceover` captions a voice by its Whisper word times; `--transcribe` captions the song's own vocals.
- The plan is `out/edl.json`. Edit it and re-render with `--edl out/edl.json`; `--plan-only` writes only the plan.
- A style is data: `styles/<name>/style.json` plus a README of measured rules. `lessons/` and each style's review rounds record what the reference taught.

## The playbook (in order)

0. **Make it yours** (`references/making-it-yours.md`). Before building, write a one-page style brief: your reference reel, your story angle and hook, your visual language, two typefaces and a palette, your voice, and your music direction. The Fontainebleau ad in `references/lessons.md` is one look, not the default.
1. **Study the reference properly.** Get approval to download it, then produce 10 fps frame sheets, cut times, **Demucs stems** and a Whisper transcript, and write rules from what you measure. Tools: `scripts/analyse_reference.py` and `references/reference-study.md`.
2. **Lock the facts and the script.** Check every number against its live source on the day. Make no claim you can't verify (no "€10 plants a tree").
3. **Generate the voice in one take with word timestamps.** Add pauses afterwards, at the quietest point of each gap, with fades (`scripts/elevenlabs_tools.py`, `scripts/mix_soundtrack.py`). The word times drive every cut and caption.
4. **Use one visual language** throughout (`references/visual-language.md`). Never cut between unrelated styles, such as paper illustration and real footage. Give every frame enough design detail that it never looks empty.
5. **Motion** (`references/motion.md`): nothing static; cuts hidden in motion; motion blur on anything faster than about 12 px per frame; captions rise in; labels readable for at least 2 s.
6. **Sound**: see below. Mix in Python, then mux onto the video.
7. **Check before showing anyone**: see below.

## Sound (both)

- **Loudness**: one measured static gain to -14 LUFS, then a limiter. Never single-pass `loudnorm`, it pumps. The engine does it in `engine/loudness.py` (-1 dBTP), the playbook in `scripts/mix_soundtrack.py` (-1.5 dBTP).
- **Music at a constant level**, 12 to 15 dB under the voice. A style's `vo_low_duck` (`engine/audio_shape.py`) dips only the band below 150 Hz under the voice, so the music's level holds; a full-band duck is a red flag.
- **Voice pauses** at the quietest 10 ms of each gap, 60 ms fade-out and 15 ms fade-in (`scripts/mix_soundtrack.py`; the same rule as a library in `engine/voicepause.py`).
- **Effects** with their measured peak on the cut, band-limited, faded, 17 to 26 dB under the voice (`references/sound.md`). Generated or cleared samples only: a style that uses the sample library (`sfx_library`) refuses to render an uncleared sample from `sfx/index.json`.

## Check before showing anyone (both)

- **Stills at every beat**: `scripts/framegrid.py` (add `--ref` to compare against the reference), and `scripts/sidebyside.py` for two renders.
- **Beat alignment**: the engine writes `check.json`; `engine/event_check.py` checks effect events too.
- **Gates**: `python engine/gate.py edit.mp4 edl.json` checks caption safe areas, flash frequency (WCAG 2.3.1) and dead frames; `scripts/deadframes.py` works on any render. `scripts/gate_report.py` runs the gates over every test edit.
- Voice splits land in silence, loudness is on target, the file spec matches the platform (`references/toolchain.md`).
- **Watch it on a phone.**

## Red flags: stop and fix

| You're about to… | Instead |
|---|---|
| Copy the example's look, or a classmate's | Go back to step 0 and choose your own reference, angle and language |
| Duck the music, or use single-pass `loudnorm` | Keep the music level fixed and apply one measured static gain |
| Splice the voice sentence by sentence | Use one take, with pauses added at the quietest point and faded |
| Mix two visual languages | Bring everything into one language |
| Use text-only cards or coloured label chips | Annotate the subject itself: a photo, a map or a diagram |
| Fade elements in, or use icon sets | Hard cuts or motion reveals; draw on the subject |
| Stagger pop-ups on their own timers | Move elements as one system on a shared clock |
| Slide or pan without blur | Use `remotion-kit/mblur.tsx`, or the engine's `pan_blur` effect |
| Use synthesised SFX or drones, generic "NCS" music, or identical repeated elements | Generate with ElevenLabs and shape the result; vary every repeat |
| Compare areas in Web Mercator | Use a local equal-scale metric frame |

## Toolkit

- **`engine/`**: the edit engine (`README.md` explains the style file format). **`styles/`**: the learned styles.
- **`scripts/`**:
  - `analyse_reference.py`: turns a reference reel into frames, cuts, stems, a transcript and an audio map.
  - `elevenlabs_tools.py`: voice with timestamps, music plans, sound effects.
  - `mix_soundtrack.py`: inserts voice pauses, shapes the effects, holds the score at a fixed level, sets loudness.
  - `burn_transition.py`: the HyperFrames ridged-burn shader applied to real frames.
  - `deadframes.py`, `framegrid.py`, `sidebyside.py`, `gate_report.py`: checks and comparisons.
  - `framecheck.py`: compares frames of a Remotion render with direct stills (parallel rendering can draw a frame wrong).
  - `splice_tail.py`: replaces the end of a render (an end card that changed) without rendering it all again.
  - `extend_music.py`: lengthens a track by repeating whole bars, joined on bar lines, and checks the joins for clicks.
  - `credits.py`: credits text from the music, SFX and footage manifests.
  - `setup.sh`, `make_testdata.sh`: engine setup and generated test media.
- **`remotion-kit/`**: motion blur (directional, and real sub-frame blur for camera moves), a camera for drawn 3D objects, shots, word-timed captions. See its README.
- **What worked and what failed, round by round:** `references/lessons.md` (an ad with a voiceover) and `references/lessons-product-film.md` (a product launch film, no voice). **Footage, licences, credits and ad rules:** `references/sources-and-facts.md`.
- **Open ideas** to carry between the two parts: `research/from-will.md` and the end of `research/compare-making-short-videos-2026-10-15.md`.

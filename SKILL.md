---
name: making-short-videos
description: Use when making or improving a short video, reel, ad, explainer or motion graphic (9:16 or other) with Remotion, HyperFrames or ffmpeg, especially with a voiceover, maps or data, real footage, generated music or sound effects, or a reference reel to match; or when someone says a cut looks AI-made, templated, cheap, rushed, sudden or badly mixed.
---

# Making short videos

## Overview

A method and toolkit proven on a 38 s fundraising ad that went through twelve rounds of very picky feedback. **The core principle: decide your own look first, then keep one visual language, keep everything moving, mix the sound at fixed levels, and check every number.** Viewers judge on a phone, and they stop at anything that feels templated, jarring or wrong.

## Workflow (in order)

0. **Make it yours** (`references/making-it-yours.md`). Before building, write a one-page style brief: your reference reel, your story angle and hook, your visual language, two typefaces and a palette, your voice, and your music direction. The example in this kit is one look, not the default.
1. **Study the reference properly.** Get approval to download it, then produce 10 fps frame sheets, cut times, **Demucs stems** and a Whisper transcript, and write rules from what you measure. Tools: `scripts/analyse_reference.py` and `references/reference-study.md`.
2. **Lock the facts and the script.** Check every number against its live source on the day. Make no claim you can't verify (no "€10 plants a tree").
3. **Generate the voice in one take with word timestamps.** Add pauses afterwards, at the quietest point of each gap, with fades (`scripts/elevenlabs_tools.py`, `scripts/mix_soundtrack.py`). The word times drive every cut and caption.
4. **Use one visual language** throughout (`references/visual-language.md`). Never cut between unrelated styles, such as paper illustration and real footage. Give every frame enough design detail that it never looks empty.
5. **Motion** (`references/motion.md`):
   - nothing static;
   - cuts hidden in motion;
   - motion blur on anything faster than about 12 px per frame;
   - captions rise in;
   - labels readable for at least 2 s.
6. **Sound** (`references/sound.md`):
   - the score at a **constant** level, 12 to 15 dB under the voice, with no ducking;
   - one static gain to -14 LUFS;
   - effects band-limited, faded, swelling into the cut, 17 to 26 dB under the voice.
   - Mix in Python, then mux onto the video.
7. **Check before showing anyone** (`references/toolchain.md`):
   - stills at every beat;
   - `scripts/deadframes.py`;
   - voice splits land in silence;
   - loudness;
   - file spec;
   - **watch it on a phone**.

## Red flags: stop and fix

| You're about to… | Instead |
|---|---|
| Copy the example's look, or a classmate's | Go back to step 0 and choose your own reference, angle and language |
| Duck the music, or use single-pass `loudnorm` | Keep the music level fixed and apply one measured static gain |
| Splice the voice sentence by sentence | Use one take, with pauses added at the quietest point and faded |
| Mix two visual languages | Bring everything into one language |
| Use text-only cards or coloured label chips | Annotate the subject itself: a photo, a map or a diagram |
| Slide or pan without blur | Use `remotion-kit/mblur.tsx` |
| Use synthesised SFX or drones, generic "NCS" music, or identical repeated elements | Generate with ElevenLabs and shape the result; vary every repeat |
| Compare areas in Web Mercator | Use a local equal-scale metric frame |

## Toolkit

- **`scripts/`**:
  - `analyse_reference.py`: turns a reference reel into frames, cuts, stems, a transcript and an audio map.
  - `elevenlabs_tools.py`: voice with timestamps, music plans, sound effects.
  - `mix_soundtrack.py`: inserts voice pauses, shapes the effects, holds the score at a fixed level, sets loudness.
  - `burn_transition.py`: the HyperFrames ridged-burn shader applied to real frames.
  - `deadframes.py`: finds frozen stretches in a render.
- **`remotion-kit/`**: motion blur, shots, word-timed captions. See its README.
- **Case study, what worked and what failed:** `references/case-study.md`.
- **Footage, licences, credits and ad rules:** `references/sources-and-facts.md`.

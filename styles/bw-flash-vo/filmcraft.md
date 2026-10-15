# bw-flash-vo in FilmCraft

A recipe for building this style in the FilmCraft editor (MCP tools `mcp__filmcraft-video__*`), by hand or through `command_batch`. Everything marked "tested" was run on the live engine on 12 Oct 2026 against the engine's own demo (`demo/A/edl.json`, `_testdata` clips, `house128.wav`, `vo1.aiff`) and compared frame by frame with `demo-A-house128-16x9.mp4`.

Time is in ticks, 254016000000 per second. A frame at 30 fps is 8467200000 ticks.

## Automatic route

```
python3 edits/engine/filmcraft_export.py edits/bw-flash-vo/demo/A/edl.json -o filmcraft-steps.json
```

The output holds `media_import` (files to import first), `steps` (paste into `command_batch`), `export_step`, `manual` (what to do by hand) and `limits`. FilmCraft hands out ids as commands run and later steps need them, so the script predicts them. Run once, then fix the ids:

1. `media_import` with the `media_import.text` from the output. Note the item ids it returns (in order).
2. Run `steps[0]` (`file.newSequence`) alone and note `result.sequence`.
3. Run the exporter again with `--media-ids 48,49,...` (or `--media-map file.json`, a `{path: id}` object) and `--seq-id <the sequence id>`.
4. Run `steps[1:]` through `command_batch` in chunks of about 100. The id rules measured on the live engine are: a new sequence takes one id per track and then its own, every `timeline.place` takes one, `file.newColorMatte` takes one, `graphics.newText` takes two. The test run checked all predicted clip ids against what `command_batch` returned and they matched.
5. Optional: `--from 7.3 --to 8.5` exports only that window (times stay absolute), `--short-side 720` for 1280x720 (default 540 gives the 960x540 of the demo mp4s), `--no-text`, `--no-audio`, `--no-grade`.
6. Export with `export_step`, then remove the test sequence with `project.delete {"items":[<sequence id>]}`.

## The recipe by hand (all tested)

| Step | Command | Params |
| --- | --- | --- |
| 1 | `file.newSequence` | `{"name":"dl-test-bw-flash-vo","width":1280,"height":720,"fps":30,"video":7,"audio":3}` (V1 picture, middle tracks captions, top track flashes) |
| 2 | `timeline.place` per shot | `{"item":<id>,"track":"V1","time":<t0 ticks>,"sourceIn":<src_in ticks>,"duration":<src_dur ticks>}` |
| 3 | `clip.speedDuration` when speed is not 1 | `{"clips":[<clip>],"speed":50}` (percent, the timeline duration becomes src_dur divided by speed, so place first and speed second, one shot at a time) |
| 4 | fit to frame | `effects.setParam {"clip":<c>,"effect":"motion","param":"scale","value":133.3333}` for 960x540 footage in a 1280x720 sequence (no step needed at 960x540). A focus offset uses `param":"position"` with `[x,y]` |
| 5 | black and white | `effects.apply {"clips":[<c>],"effect":"black_white"}` when engine `bw` is 0.95 or more. Otherwise `effects.apply proc_amp` then `effects.setParam proc_amp saturation` = (1 - bw) x saturation x 100 |
| 6 | contrast, brightness | `effects.apply brightness_contrast`, then `effects.setParam` `contrast` = 100 d / (1 + 3 d) with d = engine contrast - 1 (1.25 gives 14.3), `brightness` = engine brightness x 400 (-0.02 gives -8) |
| 7 | vignette | `effects.apply vignette`, `amount` = -(135 x engine vignette - 5.25) (0.35 gives -42), and `midpoint` 60 |
| 8 | grain | `effects.apply noise`, `amount` = engine grain x 40 |
| 9 | slow zoom and punch-ins | `effects.addKeyframe {"clip":<c>,"effect":"motion","param":"scale","time":<ticks>}` then `effects.setParam {...,"time":<ticks>,"value":<scale>}`. Keyframe time is the absolute timeline time. addKeyframe toggles, so never add twice at one tick. Value = cover scale x event factor (slow_zoom 1.0 to 1.09 over the shot) |
| 10 | zoom blur at a cut | `effects.apply gaussian_blur`, keyframe `blurriness` on both clips around the cut (0 at the outer ends, about 13 at the cut) and a small scale pulse on both |
| 11 | RGB split on the drop | `effects.apply rgb_split`, keyframe `amount` from the peak to 0 |
| 12 | shake on the drop | keyframe `motion` `position` with a few jittered `[x,y]` values that decay |
| 13 | flash frames | `file.newColorMatte {"color":"#ffffff","seconds":3}` once, then per flash `timeline.place {"item":<matte>,"track":"V7","time":<t0>,"sourceIn":0,"duration":<frames>}` and keyframe `opacity` on effect `opacity` |
| 14 | invert | the same white matte with `effects.setParam {"clip":<m>,"effect":"opacity","param":"blend","value":19}` (19 is Difference) |
| 15 | captions | `graphics.newText {"text":"WHAT","size":54,"seconds":1.2,"time":<ticks>,"track":1,"newClip":true,"position":[x,y],"font":"Avenir Next Bold"}` (track is 0-based, 1 is V2), then `effects.setParam` on `graphic_text` (`fill_color` "#961414" for the emphasis word, `align` 1 for centred) and opacity keyframes 0 to 100 for the fade |
| 16 | music | `timeline.place {"item":<wav>,"track":"A1","time":0,"sourceIn":<music.start ticks>,"duration":<edit length>}` |
| 17 | voiceover and ducking | `timeline.place` on `A2` at `voiceover.start`, then `essentialSound.setType {"clips":[<vo>],"type":"dialogue"}`, `essentialSound.setType {"clips":[<music>],"type":"music"}`, `essentialSound.set {"clips":[<music>],"key":"ducking.reduceDb","value":-9}`, `essentialSound.generateDucking {"clips":[<music>]}`. Result: music keyframes at about -9 dB under the voice |
| 18 | export | `file.exportMedia {"path":"/abs/out.mp4","format":"h264","range":"entire","wait":true}` (tested: 1280x720, 8.5 s, 255 frames with an audio track, 2.3 s to render) |

Flash opacities are not copied straight from the engine. FilmCraft mixes layers in linear light and the engine mixes in sRGB, so the exporter sets a white matte to `alpha ** 2.0` and a black dip to `1 - (1 - alpha) ** 2.2` (the `CAL` block at the top of the script).

## What the exporter automates

Cuts and source ranges on V1, constant speed (average speed for ramps), cover scale and focus offset, the per-shot grade timeline (black and white melting into colour is one grade per shot, see below), slow zoom and other scale keyframes, zoom blur, RGB split, shake, white flashes, black dips, inverts, staircase captions with emphasis colour and fades, music on A1 from `music.start`, voiceover on A2 with dialogue and music tagging and generated ducking.

## What must be done by hand

* `mask_flash` on the last shot (a white flash in the shape of the subject). Duplicate the clip, key the subject out with the `figure.mask.mp4` clip (Track Matte or Luma Key), fill white, fade 0 > 100 > 0.
* `tile` (a 2 x 2 hue-shifted tile, rare). Use Clone (Utility) with 2 columns and 2 rows.
* Sound effects. The engine synthesises whooshes, clicks, impacts, risers and hiss. FilmCraft cannot generate them, so either render the audio with the engine or add your own samples on A3 at the times in `edl.json` `sfx`.
* Fonts. `font` was accepted by `graphics.newText` but Avenir Next Bold rendered as the default sans in the live engine.
* Speed ramps, if a style or seed ever asks for them. The exporter applies the average speed and lists the ramp in `manual`. Time Remapping has a keyframable `speed` parameter, but the demos contain no ramps so ramp keyframes were not tested.

## What FilmCraft could not reproduce

* Radial zoom blur. FilmCraft has Gaussian, directional, channel and focus blurs only, so zoom_blur is a Gaussian blur plus a scale pulse. At the cut it is softer and not radial.
* Invert is Difference blend of a white matte. FilmCraft computes it in linear light, so mid-tones come out lighter than the engine's 255 - v.
* Grade pixels. Contrast, brightness, vignette and grain were fitted by eye and by region means against the demo frames. They match within a few levels but not exactly. Grain is a different noise pattern.
* The grade timeline is stepped per shot. The engine also interpolates per shot, so this matches. A grade that changes inside a long shot would not.
* Film look of the RGB split. The amount unit of the FilmCraft effect is not documented, the value (engine amount x 640) was set by eye and is slightly stronger than the engine at the drop.
* Frame timing of flashes is exact (matte clips cover the same frames the engine uses) but flash brightness runs 10 to 20 levels brighter than the engine over near-black footage.

## Match against the demo (tested)

Window 0 to 3.6 s and 7.3 to 8.5 s of demo A, compared with ffmpeg frames from `demo-A-house128-16x9.mp4`:

* Cut positions and clip choice: identical on every frame checked, cuts are placed on the same frame numbers by construction.
* Frame 0.25 s (slow zoom, black and white): mean 92.6 against 91.8, correlation 0.91. Region means (top, bottom, corners) within 2 levels after calibration.
* Frame 1.1 s: correlation 0.98. Frame 2.37 s (just after a zoom blur cut): correlation 0.90, mean 94.4 against 94.1.
* Drop frame 7.57 s (shake, RGB split, zoom blur): the same shapes land at the same positions, RGB split a little heavier. Staircase captions at 8.13 s sit at the same positions as the engine's (THAT, DOES, NOT, EVEN), in the default sans instead of Avenir Next Bold and without the engine's blur ghost.
* Flash decay frames 22 to 24: flash curve follows the engine (about 52 percent, 18 percent, 2 percent) within a 10 to 20 level brightness offset.

Not tested live: portrait output (`demo/B`), the colour-melt section of the grade timeline (5 to 7 s) beyond its numbers, and the second half of the demo. The exporter writes steps for all of them without errors (`demo/B/edl.json` gives 957 steps at 540x960).

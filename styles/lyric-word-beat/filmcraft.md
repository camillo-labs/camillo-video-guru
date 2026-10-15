# lyric-word-beat in FilmCraft

A recipe for building this style in the FilmCraft editor (MCP tools `mcp__filmcraft-video__*`), by hand or through `command_batch`. Tested on the live engine on 12 Oct 2026 with the whole of `demo/demo-A-house128.edl.json` (16.9 s, 9 shots, 61 words) and frames compared with `demo/demo-A-house128.mp4`.

Time is in ticks, 254016000000 per second.

## Automatic route

```
python3 edits/engine/filmcraft_export.py edits/lyric-word-beat/demo/demo-A-house128.edl.json -o filmcraft-steps.json
```

The output holds `media_import`, `steps`, `export_step`, `manual` and `limits`. Because FilmCraft assigns ids as commands run, import the media first, run `steps[0]` (`file.newSequence`) alone, then rerun the exporter with `--media-ids <ids from media_import>` (or `--media-map`) and `--seq-id <sequence id>` and paste `steps[1:]` into `command_batch` in chunks of about 100. Section "Automatic route" of `bw-flash-vo/filmcraft.md` has the id rules and the options (`--from`, `--to`, `--short-side`, `--no-text`).

## The recipe by hand (tested)

| Step | Command | Params |
| --- | --- | --- |
| 1 | `file.newSequence` | `{"name":"dl-test-lyric-word-beat","width":1280,"height":720,"fps":30,"video":3,"audio":3}` (V1 picture, V2 captions, V3 transitions) |
| 2 | `timeline.place` per shot | `{"item":<id>,"track":"V1","time":<t0 ticks>,"sourceIn":<src_in ticks>,"duration":<ticks>}`. Shots are 3 to 6 beats long and speed is always 1 in this style. The last short shot repeats the first picture (the loop seam), place it like any other |
| 3 | fit | `effects.setParam {"clip":<c>,"effect":"motion","param":"scale","value":133.3333}` for 960x540 footage in 1280x720 |
| 4 | grade (the same for every shot) | `effects.apply proc_amp` with `saturation` 105, `effects.apply brightness_contrast` with `contrast` 6, `effects.apply vignette` with `amount` -15 and `midpoint` 60, `effects.apply noise` with `amount` 0.5 (the live test ran with 1.2, before the grain value was recalibrated down) |
| 5 | one word at a time, centred, difference fill | `graphics.newText {"text":"NIGHT","size":69.1,"seconds":0.2333,"time":<ticks>,"track":1,"newClip":true,"position":[640,384.2],"font":"Arial Black"}`, then `effects.setParam {"clip":<t>,"effect":"graphic_text","param":"align","value":1}` and `effects.setParam {"clip":<t>,"effect":"opacity","param":"blend","value":19}` (19 is Difference, the word inverts whatever is below it). The word stays until the next word starts |
| 6 | dip to black on the last cut | `file.newColorMatte {"color":"#000000","seconds":3}`, `timeline.place` on V3, keyframe `opacity` on effect `opacity` with `effects.addKeyframe` then `effects.setParam` (both with an absolute `time`) |
| 7 | invert on the last cut | a white matte on V3 with `effects.setParam {"clip":<m>,"effect":"opacity","param":"blend","value":19}` |
| 8 | haze flash, radial flash | pale matte (`#e1e1e6` for the haze, `#e8f5fa` cream for the radial flash) with the opacity envelope from `style.json` params |
| 9 | export | `file.exportMedia {"path":"/abs/out.mp4","format":"h264","range":"entire","wait":true}` |

Flash and dip opacities are converted for FilmCraft's linear-light mixing: white `alpha ** 2.0`, black `1 - (1 - alpha) ** 2.2` (the `CAL` block in the script).

## What the exporter automates

Cuts, grade, the loop seam, centred difference-blend captions with the engine word timing, the closing dip to black and invert, and approximations of the haze flash and radial flash. Music goes on A1 from `music.start`. This style has no voiceover and no sound effects in the demo.

## What must be done by hand

The exporter lists each of these in `manual` with the time and a plain instruction.

* `lyr_dip_mosaic` (hard dip to black, a 3 x 3 mono mosaic filling in, then a strobe snap). The exporter builds only the black dip at 25 percent. Add Mosaic (Stylize) or the Mosaic transition on the cut.
* `lyr_strobe_pop` (every other frame about 1.75 times brighter and 1.35 times more saturated). Key Hold-interpolated contrast and saturation on the shot that starts at the cut.
* `lyr_band_wipe` (band closes over the old shot), `lyr_card_up` (old shot as a card rising from below), `mask_flash` with the sticker tag (brand sticker and wordmark behind the subject) and the `lyric_sticker` overlay. These need nests, crops and masks. The sticker needs the `figure.mask.mp4` clip as a matte.
* The radial zoom blur inside `lyr_radial_flash` and the fog blur inside `lyr_haze_flash`. Only the cream and pale veil envelopes are built.

## What FilmCraft could not reproduce

* Radial blur. FilmCraft has no radial blur, only Gaussian, directional, channel and focus blurs.
* Transitions that bring the previous shot into the next one (band wipe, card up, mosaic fill) are not one command. They are nests or two-clip builds, so they stay manual.
* Difference blend runs in linear light, so a caption over mid-tones is a little lighter than the engine's text.
* Grade, grain and vignette are fitted, not exact. Grain is a different noise pattern.
* Fonts. "Arial Black" rendered as a heavy sans in the live engine, which suited this style. A font that is not installed falls back to the default sans (Avenir Next Bold did in the bw-flash-vo test).
* The engine draws the captions inside its own frame loop with its own anti-aliasing and drop shadow. FilmCraft's text has its own shadow settings (`graphic_text` `shadow`), left off.

## Match against the demo (tested)

Frames of the FilmCraft sequence compared with ffmpeg frames from `demo-A-house128.mp4` (480 x 270 resized, no flashes unless stated):

| Time | Content | Mean absolute difference | Correlation | Channel means FilmCraft vs engine |
| --- | --- | --- | --- | --- |
| 0.7 s | stars, caption NIGHT | 4.7 | 0.87 | 42 / 9 / 9 vs 40 / 7 / 5 |
| 2.5 s | plasma | 3.7 | 0.99 | 147 / 99 / 110 vs 147 / 99 / 108 |
| 5.2 s | figure | 5.2 | 0.98 | 156 / 86 / 83 vs 156 / 86 / 82 |
| 9.5 s | shapes | 4.2 | 0.98 | 116 / 74 / 73 vs 116 / 72 / 69 |
| 12.5 s | metaballs | 14.2 | 0.94 | 168 / 95 / 115 vs 168 / 94 / 113 (the engine has a caption and a radial flash tail here) |
| 16.5 s | closing dip and invert | n/a | 0.36 | both near black (31 vs 25) |

Cuts sit on the same frames as the engine because shots are placed at the engine's frame-quantised times. Only the first eight words were built in the live test, the rest of the 61 are the same steps and the exporter writes them without errors. The strobe pop and haze flash frames did not match in the first live test (they were built then as a plain white matte), so the exporter now builds the haze as an envelope and lists the strobe pop as manual. That revised haze envelope was not re-run live.

The 9:16 demo (`demo-B-hiphop100.edl.json`) was exported (262 steps at 540x960) but not run in FilmCraft.

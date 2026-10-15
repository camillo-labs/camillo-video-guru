# hud-lyric-heat in FilmCraft

Written from `style.json`, `README.md` and the demo `edl.json` as they stand on 12 Oct 2026. The exporter was run on this style (`demo/demo-A-house128.edl.json`, 76 steps) but the result was not built live in FilmCraft and no frames were compared. Treat the recipe below as untested, apart from the commands marked tested, which were used in the other two styles.

## What FilmCraft can build

One continuous take with a saturated grade and a lyric row between the subject and the camera, plus a HUD of timed overlays.

```
python3 edits/engine/filmcraft_export.py edits/hud-lyric-heat/demo/demo-A-house128.edl.json -o filmcraft-steps.json
```

Automatic (the commands are tested in the other styles, see `bw-flash-vo/filmcraft.md` for the id workflow):

* `file.newSequence`, `timeline.place` for the few long shots (6 to 12 beats each), the cover scale, `effects.apply proc_amp` (saturation 1.2 becomes 120) and `brightness_contrast` (contrast 1.08 becomes about 6.5).
* The `zoom_pulse` at the drop as scale keyframes.
* The lyric row as one centred `graphics.newText` per word (about 22 words in the demo), `size` from `captions.size_frac`, fill from the theme colour (`#d41117` in heat).
* Music on A1 from `music.start`.

## Manual

The exporter lists each item in `manual` with its time and a plain instruction. All of these are per-frame engine overlays.

* Text behind the subject. Place the caption on V2, put the footage again on V3 above it and cut the subject out with `figure.mask.mp4` (Track Matte or Luma Key, `track_matte` is in the effect list). The middle word of a three word phrase then disappears behind the body.
* `hud_bar` (brown DETECTING bar with typed dots, readouts, X marks and brackets). Build with `graphics.newRectangle`, `graphics.newText` and keyframes.
* `hud_wipe` (brown band across the caption row, subject shown as a pale inverted cut-out). A brown Color Matte band with Motion position keyframes and a Difference blend (`blend` 19 on effect `opacity`).
* `hud_heat` (thermal gradient map in a band between 11.5 and 88.4 percent of the frame height, sliding sideways, subject rim). Try `effects.apply tint` (parameters `black`, `white`, `amount`) with a Crop or mask on the band. This was not tried.
* `hud_marks`, `hud_glitch`. Red squares and a block-displacement reveal. RGB Split and Mosaic with short keyframes get near.
* The tint of the grade (`tint [0.93, 1.0, 1.05]`). Set it by eye with Lumetri Color.
* Sound effects (ticks), none can be generated in FilmCraft.

## What FilmCraft could not reproduce

* The subject cut-out behind the text. It needs the engine's mask clip and a per-frame matte, FilmCraft can only follow it as a Track Matte layer you wire up.
* The network of ringed nodes, the scrolling readouts and the typed label are drawn per frame by the engine. FilmCraft would need many text and shape layers with keyframes.
* The heat gradient map is a custom palette (black, deep red, orange, gold, cream). The Tint effect is two colours.

Honest status: the exporter gives you the cut, grade, captions and music. The look of this style is the overlays, which are manual.

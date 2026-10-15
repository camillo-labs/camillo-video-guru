# hud-lyric-light in FilmCraft

The same template as `hud-lyric-heat` on pale, ungraded footage with four glowing caption colours and a dark end card. Written from `style.json`, `README.md` and the demo `edl.json` as they stand on 12 Oct 2026. Nothing here was built live in FilmCraft, so it is untested apart from the commands that were tested in the other styles.

Read `hud-lyric-heat/filmcraft.md` first. The recipe is the same. The differences are these.

```
python3 edits/engine/filmcraft_export.py edits/hud-lyric-light/demo/demo-A-house140.edl.json -o filmcraft-steps.json
```

Automatic: sequence, long shots, cover scale, the lyric row as one centred text clip per word, music on A1, the drop zoom pulse. No grade steps, because `grade.base` is empty and the footage is used as shot.

Different from heat:

* Caption themes change at each heat flash (pink `#e60a96`, blue `#1c6fe0`, gold `#ffc040`, orange `#ff781e`) with a glow. The exporter uses one colour. Set `fill_color` per word with `effects.setParam {"clip":<text>,"effect":"graphic_text","param":"fill_color","value":"#e60a96"}` and the glow with `shadow` on `graphic_text` (`shadow_color` the same colour, `shadow_blur` about 40, `shadow` true). The shadow route was not tried.
* The caption row sits lower (`y` 0.59 against 0.49).
* A dark end card for the last 8 beats (`hud_end_card`, handle text `@your.handle`). Build with `file.newColorMatte {"color":"#000000","seconds":4}` placed above V1 and a `graphics.newText` typing the handle.

Manual and not reproducible: as in `hud-lyric-heat/filmcraft.md` (subject cut-out behind the text, HUD bar, detect wipe, heat band, marks, glitch, sound effects).

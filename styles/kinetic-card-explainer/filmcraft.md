# kinetic-card-explainer in FilmCraft

A recipe for building this style in the FilmCraft editor (MCP tools `mcp__filmcraft-video__*`). Status on 12 October 2026: the exporter ran on the demo edit and produced a complete step file, but the steps were not replayed in the live FilmCraft engine, so nothing below is marked tested. The command names are the ones tested in `lyric-word-beat/filmcraft.md`.

Time is in ticks, 254016000000 per second.

## Automatic route

```
python3 edits/engine/filmcraft_export.py edits/kinetic-card-explainer/demo/demo-house128.edl.json -o filmcraft-steps.json
```

Result for the demo: 208 steps, 21 shots, 90 text clips, 22 manual items (one per scene, because `kc_scene` has no FilmCraft equivalent). Import the media first, run `steps[0]` (`file.newSequence`) alone, rerun the exporter with `--media-ids` and `--seq-id`, then paste `steps[1:]` into `command_batch` in chunks of about 100. The id rules are in `bw-flash-vo/filmcraft.md`.

## The recipe by hand

| Step | Command | Params |
| --- | --- | --- |
| 1 | `file.newSequence` | `{"name":"kinetic-card-explainer","width":720,"height":1280,"fps":30,"video":5,"audio":2}` (V1 talker, V2 scene mattes, V3 diagram elements, V4 captions, V5 end card) |
| 2 | scene backgrounds | `file.newColorMatte` per colour (`#0E0B11`, `#E8E8E8`, `#E7E3D8`, `#C87359`), `timeline.place` on V2 for each scene, 1.2 to 2 s, cut on the first word of the phrase |
| 3 | talker | on V1 under everything. Scenes with `head: full` get no matte on V2. Split scenes get a matte for the top 47 percent only (crop) and a 3 percent feathered edge |
| 4 | pills | `graphics.newShape` rounded rectangle plus `graphics.newText` in Inter Bold, fills `#26B2F1` (answer) and `#0E0B11` or white. Scale keyframes 0 to 100 percent with overshoot (the engine curve: damping 0.55, 24 rad/s, about 12 percent overshoot at 0.1 s), 0.1 s stagger |
| 5 | arrows | a line shape with a trim or a width keyframe over 0.3 s, a dot at the start and a triangle at the tip appearing at 85 percent |
| 6 | mascot | an 11 by 8 grid of squares (`graphics.newShape`) or an imported PNG sprite, `#DE7050`, white on terracotta |
| 7 | captions | `graphics.newText` per chunk, Inter Tight Bold 47 px at x 360, y 896, ink `#FBF8FD` on dark and `#0F0F11` on light. The accent word is a separate clip in Playfair Display Italic 55 px, `#3BADDD`. Cut-ins: Playfair Italic white at y 883 and bold `#A0E0FF` below |
| 8 | end card | at 23.97 s a light matte with "comment" (Playfair Italic 42 px), the keyword (Playfair Bold Italic, `#26B2F1`, 0.9 of the width) and two lines of Playfair and Inter text, a card image at y 44 percent, and a `#000000` matte at 75 percent from 27.17 s |
| 9 | audio | voice on A1, no music, -14 LUFS |
| 10 | export | `file.exportMedia {"path":"/abs/out.mp4","format":"h264","range":"entire","wait":true}` |

## What the exporter automates

Cuts, the talker clip, one text clip per caption word with the engine timing, the voice track. Everything inside a scene is manual.

## What must be done by hand

* Every `kc_scene` (the exporter lists one manual item per shot with its spec), `kc_end`, the accent styling and the chunking of words.
* Springs: FilmCraft keyframes are bezier, so the overshoot is approximated with three keyframes (0, 1.12, 1.0) per element.

## What FilmCraft could not reproduce

* Per-frame procedural elements (waveform bars that react to time, the typing terminal). Use a pre-rendered clip from the engine (`make_edit.py` at 540 px) as a nested sequence instead.
* Closed-form springs evaluated at every frame. The bezier approximation drifts by about 20 ms.
* Fonts that are not installed fall back to the default sans.

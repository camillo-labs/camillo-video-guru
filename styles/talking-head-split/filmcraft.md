# talking-head-split in FilmCraft

A recipe for building this style in the FilmCraft editor (MCP tools `mcp__filmcraft-video__*`). Status on 12 October 2026: the exporter ran on the demo edit and produced a complete step file, but the steps were not replayed in the live FilmCraft engine, so none of the commands below are marked tested. The command names are the ones used and tested in `lyric-word-beat/filmcraft.md`.

Time is in ticks, 254016000000 per second.

## Automatic route

```
python3 edits/engine/filmcraft_export.py edits/talking-head-split/demo/demo-house128.edl.json -o filmcraft-steps.json
```

Result for the demo: 276 steps, 7 shots, 116 text clips (one per Whisper word, see below), 6 manual items. Import the media first, run `steps[0]` (`file.newSequence`) alone, rerun the exporter with `--media-ids` and `--seq-id`, then paste `steps[1:]` into `command_batch` in chunks of about 100. The id rules and options are in `bw-flash-vo/filmcraft.md`.

## The recipe by hand

| Step | Command | Params |
| --- | --- | --- |
| 1 | `file.newSequence` | `{"name":"talking-head-split","width":720,"height":1280,"fps":30,"video":4,"audio":2}` (V1 talker, V2 cards, V3 title and captions) |
| 2 | `timeline.place` the take | place the take once per shot with `timeline.place` and a `sourceIn`, using the shot list in the edl (4 to 8 s each, cut within 0.05 s of a word start) |
| 3 | close shots | on every second shot `effects.setParam` motion scale 170 and position y about 62 percent of the frame so the head sits in the lower half |
| 4 | cards | `media_import` the captures, `timeline.place` on V2 at x 9 percent, width 82 percent (`motion` scale from the source size), hard cuts, 0.2 to 0.7 s for the first 5 s of the card run, then 1.2 to 3.2 s. A 3 percent scale keyframe over each card gives the push |
| 5 | captions | `graphics.newText` per chunk (not per word), font Playfair Display or Didot, size 63 px, tracking -35, white, shadow on (`graphic_text` shadow: distance 3, blur 6, opacity 60), position x 360, y 938 + line pitch 64 for the second line, duration from the chunk start to the next chunk start |
| 6 | title | three `graphics.newText` lines at x 60, y 330, 412, 494 on V3, white with the gold runs as separate clips in `#F0C815`, from 0 to 4.43 s |
| 7 | end dim | `file.newColorMatte {"color":"#000000"}` on V3 for the last 4 s at 75 percent opacity (keyframe opacity with `alpha ** 2.0` linear-light correction as in `lyric-word-beat/filmcraft.md`) |
| 8 | audio | voice on A1, no music, normalise to -14 LUFS |
| 9 | export | `file.exportMedia {"path":"/abs/out.mp4","format":"h264","range":"entire","wait":true}` |

## What the exporter automates

Cuts, the loop-free shot list, one text clip per caption word with the engine timing (the engine draws chunks, so merge the words of a chunk into one clip by hand, or keep the word clips and accept a word-by-word build), the voice track. Music is muted, `audio.music_gain` is 0.

## What must be done by hand

* `th_zoom` (static punch-in on alternate shots): set motion scale and position per shot.
* `th_title`, `th_cards`, `th_outro`: per-frame engine overlays, rebuilt with `graphics.newText`, `timeline.place` and a matte as in the table.
* The chunking of captions into two-line blocks. The engine breaks on 82 percent of the width or an 8 word limit.

## What FilmCraft could not reproduce

* Playfair Display with a negative tracking value. Set the font in the Essential Graphics panel, because an uninstalled font falls back to the default sans.
* The generated stand-in cards. Use real captures, which are better than the engine's anyway.
* Cuts that follow word starts are in the edl but FilmCraft shows them on the frame grid (33 ms).

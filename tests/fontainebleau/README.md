# Chateau de Fontainebleau short

A 20.2 s vertical (720x1280) short celebrating the château, made with the lyric-word-beat style (variant in style.json: no brand sticker, no strobe pop, a warm grade, slower words, a dark band behind the caption for legibility). It was chosen because the style's long shots of 4 to 5 beats, one word at a time and soft dip, haze and wipe transitions suit stills and aerials better than a flash-cut montage. Four video excerpts and three stills are cut in the order of the clip names (clips.select sequential), so the story runs from the forest to the château to the gardens to the interior.

Files: fontainebleau.mp4 (the film), edl.json (the plan), style.json and captions.txt (the inputs), check.json and events.json (beat alignment), credits.md, sources.json and facts.md (every file, its licence and every caption fact with its source and retrieval date). Footage and music are in assets/ (not committed).

Reproduce from the edits folder (work/clips holds numbered links to the chosen files in assets/clips):

```
.venv/bin/python engine/make_edit.py --style tests/fontainebleau/style.json --clips tests/fontainebleau/work/clips \
  --music tests/fontainebleau/assets/music/Court-of-the-Queen.mp3 --captions tests/fontainebleau/captions.txt \
  --duration 22 --aspect 9:16 --seed 2 --res 720 --out tests/fontainebleau/work
```

Inputs: filmaviator's "Forêt et château de Fontainebleau" (CC BY 3.0, four excerpts), three CC0 stills (two by Jebulon, one Rijksmuseum), Court of the Queen by Kevin MacLeod (CC BY 4.0, 95 BPM, detected 94.97). The five CC BY-SA stills in the asset set were left out so the film has no share-alike obligation. Captions are four cited lines, see facts.md. The dropped claims: no source says Napoleon stood on the Horseshoe staircase and no source gives a distance from INSEAD, so neither is on screen.

Beat alignment (check.json):

| Measure | Result |
| --- | --- |
| Shots and cuts | 8 shots, 7 cuts (about 4 beats each), all 7 found in the video |
| Planned cut times against the sixteenth-note grid | 8.9 ms mean absolute (frame rounding at 30 fps) |
| Cuts found in the video against the grid re-detected from the rendered audio | 35 ms, all late: every cut starts a dip, mosaic, haze or wipe, so the change in the picture peaks after the cut, and the 22 s excerpt gives the tempo only to about 0.2 per cent |
| Planned beats against the sharpest attack within 50 ms in the music itself | every beat has a measurable attack, 23.8 ms mean absolute, median -15 ms, 47 per cent within 25 ms |

The music is strings and brass with soft attacks, so the beat grid is looser than on a drum-led track and the cuts feel on the pulse rather than on a hit. A drum-led track would give the 10 ms figures seen on the other styles. The window starts at 169.4 s so the track's drop at about 177 s lands 7.6 s into the film.

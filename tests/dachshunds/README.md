# Dachshund short

A 13.8 s vertical (720x1280) short made with the lyric-word-beat style (the Fontainebleau variant in style.json), chosen for its one-word-at-a-time captions over longer shots. It was a quick pass: ten Pexels clips, Raving Energy by Kevin MacLeod (CC BY 4.0, 122 BPM), four captions from Wikipedia (facts.md).

Reproduce from the edits folder:

```
.venv/bin/python engine/make_edit.py --style tests/dachshunds/style.json --clips tests/dachshunds/assets/clips \
  --music tests/dachshunds/assets/music/Raving-Energy.mp3 --captions tests/dachshunds/captions.txt \
  --duration 15 --aspect 9:16 --seed 3 --res 720 --out tests/dachshunds/out
```

Beat alignment (out/check.json): 7 cuts planned, 7 found, planned cuts 8.0 ms from the sixteenth grid, rendered cuts 16.2 ms (half a frame at 30 fps), tempo 122.0 detected 122.1.

Known gaps: the first shot is a greyscale tile intro from the style, the footage is mostly calm dogs because most Pexels dachshund clips are resting, the caption word for "breed" repeats at the end, and a longer 18 to 22 s cut with 8 to 14 clips was dropped for speed.

## HUD cut

hud/out/edit.mp4 is a 15.7 s hud-lyric-heat render (lyric words behind the dog, DETECTING HUD, heat flash) of eight single-dog clips with the same song, seed 3. Reproduce from the edits folder:

```
.venv/bin/python engine/make_edit.py --style hud-lyric-heat --clips tests/dachshunds/hud/clips \
  --music tests/dachshunds/assets/music/Raving-Energy.mp3 --captions tests/dachshunds/hud/captions.txt \
  --duration 17 --aspect 9:16 --seed 3 --res 720 --out tests/dachshunds/hud/out
```

Captions: BADGER HUNTER, FIRST OLYMPIC MASCOT, BORN TO TUNNEL, LOUD BARK, WIENER OR SAUSAGE, 300 YEARS OF ATTITUDE. The six lines are in the plan once each and then the first five cycle again to fill the time. 300 YEARS OF ATTITUDE is planned but was not in the six frames checked. It has no black first frame (the style opens with a glitch reveal on the dog).

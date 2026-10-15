# Green Label deadstock short

A 19.7 s vertical (720x1280) short about textile waste, made with the bw-flash-vo style (variant in style.json). It was chosen because the style's black and white opening that turns to colour tells the story of waste becoming resource, and its staircase captions hold longer facts better than single words. Flash density is cut to about half of the learned style and the emphasis colour is the brand sand (#e6c88a), with a green (#084908) logo end card in the last 4 beats.

Files: green-label.mp4 (the film), edl.json (the plan), style.json and captions.txt (the inputs), check.json and events.json (beat alignment), credits.md, sources.json and facts.md (every file, its licence and every caption fact with its source). Footage and music are in assets/ (not committed, the Pexels licence forbids redistributing the raw files).

Reproduce from the edits folder:

```
.venv/bin/python engine/make_edit.py --style tests/green-label/style.json --clips tests/green-label/assets/clips \
  --music tests/green-label/assets/music/Raving-Energy.mp3 --captions tests/green-label/captions.txt \
  --duration 20 --aspect 9:16 --seed 4 --res 720 --out tests/green-label/work
```

Inputs: ten Pexels textile clips (the ones the site already credits), Raving Energy by Kevin MacLeod (CC BY 4.0, 122 BPM, detected 122.0), captions only from /Users/student/Documents/Claude/deck-research/03-green-label.md: the EEA's 4 to 9 per cent of textiles placed on the EU market destroyed before use, and the EU ban on destroying unsold clothes in application for large companies since 19 July 2026, each with its source line.

Beat alignment (check.json):

| Measure | Result |
| --- | --- |
| Shots, cuts planned, cuts found in the rendered video | 64 shots, 63 cuts, 59 found (the rest hide under flashes) |
| Planned cut times against the sixteenth-note grid | 7.3 ms mean absolute |
| Cuts found in the video against the grid re-detected from the rendered audio | 10.2 ms mean absolute, every cut within one frame (33.3 ms) of a sixteenth |
| Planned beats against the sharpest attack within 50 ms in the music itself | 97 per cent of beats have a clear attack, 10.5 ms mean absolute, median +10 ms, 97 per cent within 25 ms |

The first drop in the track is at 7.9 s, so it lands at 7.9 s in the film and the colour change follows the black and white opening. What is not matched: the style's usual drop placement (the track's only drop is too early in the song to move), and the logo card is a plain fade, not an animated reveal. Facts are on screen for about 3 s each, which is short for a 12-word line, so the captions suit a repeat viewing or a 25 s version (set --duration 25).

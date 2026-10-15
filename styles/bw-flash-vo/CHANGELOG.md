# bw-flash-vo changelog

Reviewer: a fresh Opus subagent each round against the 576x1024 explainer (band 548x308). Reports in review-round-N.md, grids in review-round-N/, renders in rounds/round-N.mp4 (out of git).

## Round 1 (MAJOR 8, MINOR 12, COSMETIC 7)
Found: one-word staircase vs 2 to 3 word chunks, caption face and size, captions running through the montage, intro cut rate half the reference, 7 white flashes against 34, grade too bright (luma 115 against 75), no voiceover or ducking, music-led rather than cut-led sound.
Changed: new `kinetic` caption kind (Anton, chunks, scaled key word, scrim, depth), intro cuts 0.25 to 0.75 beats with a 0.5 beat first shot, intro flash and invert rules, darker grade stops, intro `click` louder, `gap` sound events that mute the music for 0.12 s, voiceover used for the render.

## Round 2 (MAJOR 3, MINOR 15, COSMETIC 10)
Closed: intro cut rate, voiceover, caption layout and face (owner directive, recorded cosmetic). Open: captions and voiceover spanning 72 per cent of the edit, grade still too bright, impact tails filling the gaps.
Changed: `target_luma` grade key (per-shot normaliser), shorter voiceover, intro impact removed, depth `min_visible` 0.7.

## Round 3 (MAJOR 0, MINOR 20, COSMETIC 11)
No major differences. Remaining: 11 white frames against 34, luma 95 against 83, drop at 50 per cent without a blur build, loudness -20.5 against -15 LUFS, "4-9%" split by the transcriber, text drawn under blur and flash effects.
Changed after the round: target luma 0.26 and 0.32, high and drop flash probability 0.6.

## Remaining differences
Flash density, brightness a few points high, no blur build into the drop, loudness, caption face deliberately different (owner directive).

# lyric-word-beat changelog

Reviewer: a fresh Opus subagent each round against the 16:9 band of ScreenRecording 22-33-20. Reports in review-round-N.md, grids in review-round-N/, renders in rounds/round-N.mp4 (out of git).

## Round 1 (MAJOR 12, MINOR 15, COSMETIC 9)
Found: captions stopping at 8.85 s, blank gaps between phrases, fades instead of hard swaps, two-word chunks, caption size twice the reference, text hidden behind objects, grey low-contrast difference blend, extra strobe cut, card-up transition missing, audio fading at the loop seam.
Changed: `fill` timing option (phrases repeat to cover the edit), kinetic diff plate with `anim: none`, `hold_until_next`, one word per swap, size 0.096 (landscape) and 0.13 (portrait), Archivo Black, strobe pop removed and move rotation changed to a period of 7, darker grade, no tail fade when `loop_seam_beats` is set.

## Round 2 (MAJOR 3, MINOR 14, COSMETIC 9)
10 of 12 majors closed. Open: legibility on bright or textured footage, grade luma 98 against 51, caption overprinting the wordmark.
Changed: one contrast target per word plus a soft halo, `y_alt` during the sticker moment, `target_luma` grade.

## Round 3 (MAJOR 1, MINOR 16, COSMETIC 12)
Closed: legibility, sticker-moment placement. Open: grade luma 78 against 51, colour accents lost at guard 0.92, no caption pause when graphics land.
Changed: grade exponent solved against the real mean, guard 0.7 to 0.8.

## Round 4 (MAJOR 2, MINOR 17, COSMETIC 12)
Found: luma 71 against 51, and a regression where the last phrase was dropped (1.8 s with no word).
Changed: whole-phrase fill only for HUD styles, `hold_last` for kinetic, `target_strength`, target luma 0.2, guard 0.7.

## Remaining differences
Word rate 3 a second against 5, accents of colour, caption pause at graphics, shot lengths and a plain hard cut, seam dip ramps instead of cutting to black, depth layering of words (owner directive).

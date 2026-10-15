# hud-lyric-heat changelog

Reviewer: a fresh Opus subagent each round against the 1288x724 screen recording. Reports in review-round-N.md, grids in review-round-N/, renders in rounds/round-N.mp4 (out of git).

## Round 1 (MAJOR 7, MINOR 16, COSMETIC 6)
Found: condensed face, words spread across 80 per cent of the width, mint wipe colour, long flat wipe, pale heat band down to 88 per cent, no ending matte, steady overlays.
Changed: Archivo Black, `gap_em` natural spacing, `wipe_color` theme with no ghost, wipe `band_y`, `texture`, 2 frame duration, heat `y0`, `y1`, `normalise`, `subject_black`, bar `flicker` and `mark_frames`, caption `fill` so the edit never runs out of words.

## Round 2 (MAJOR 5, MINOR 18, COSMETIC 8)
Found: scale-to-fit made short phrases 45 per cent taller, black subject fill on false mattes, pale wipe, overlays still steady.
Changed: `fit_up` false, size 0.14, black fill only for a real person matte, darker wipe texture, wipe `width`, 1.0 beat bars with flicker every 5 frames.

## Round 3 (MAJOR 3, MINOR 20, COSMETIC 8)
Found: 1.2 s of bare footage at the end, Vision finding a person in a fabric pile, 10 scene changes against 25.
Changed: `hold_last`, `hud_end_matte` overlay (caption on black, 3 frames) with a `gap` sound, black fill gated on matte area, re-rolled readout and card positions, deeper heat colour.

## Round 4 (MAJOR 2, MINOR 22, COSMETIC 7)
Ending closed. Open: false person matte on the fabric pile, 12 scene changes against 25.
Changed: person matte accepted only below 45 per cent coverage, whole-phrase fill, an extra head wipe and larger square markers.

## Remaining differences
Scene-change density, loudness (-18.6 against -12.6 LUFS), heat band slide seam, sound effects set, matte shapes (object footage), face is Archivo Black by owner directive.

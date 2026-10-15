# hud-lyric-light changelog

Reviewer: a fresh Opus subagent each round against the 1024x576 TikTok download. Reports in review-round-N.md, grids in review-round-N/, renders in rounds/round-N.mp4 (out of git).

## Round 1 (MAJOR 5, MINOR 17, COSMETIC 9)
Found: third heat flash missing, last captions under the end card, theme order, caption unreadable inside the heat band, dark warm grade.
Changed: Archivo Black, natural spacing, themes pink, pink, blue, blue, `band_color` redraw of the caption over the heat band, `frac_max` 0.8, pale grade, wipe and bar changes shared with heat, placeholder handle text removed from the end card.

## Round 2 (MAJOR 3, MINOR 18, COSMETIC 10)
Found: edit cut to the bar (15.7 s), end card on top of the third flash, orange band, dark intro.
Changed: render length 18.5 s, end card 10 beats, heat `normalise` range 0.45, `fit_up` false, `target_luma` 0.6.

## Round 3 (MAJOR 3, MINOR 16, COSMETIC 11)
Found: end card 1.75 s after heat 3, orange band, grey intro.
Changed: `frac_max` 0.7 so no fourth cycle, `hold_last`, band colour tan, grade exponent clamp widened, cool tint.

## Round 4 (MAJOR 1, MINOR 19, COSMETIC 13)
Closed: end card timing (0.75 s after the last flash), deep red band, pale caption in band. Open: grade (intro luma 114 against 163).
Changed: target luma 0.68 and a solved exponent.

## Remaining differences
Intro grade still greyer than the reference, wipes 2 frames, mint wipe in the blue phase, heat flash without readouts, theme red hold missing, Archivo Black by owner directive.

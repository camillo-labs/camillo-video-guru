MAJOR: 1, MINOR: 19, COSMETIC: 13. Major differences remain (1, the grade).

# hud-lyric-light, review of round 4

Reference: `_source/v26044gc0000dau3ftvog65vlo4gptag.MP4` (1024x576, 30 fps, 17.17 s). Render: `hud-lyric-light/rounds/round-4.mp4` (1280x720, 30 fps, 17.70 s, 36 beats at 122 BPM). Times are seconds in each file. The TikTok watermark, logo and search bar, the footage subject (person against objects, so matte shapes differ) and the caption words are out of scope.

Scene detection (`select='gt(scene,0.2)'`): reference 5.17, 5.73, 5.83, 6.17, 6.53, 6.57, 6.93, 7.93, 8.10, 8.67, 8.77, 8.93, 9.10, 9.47, 9.50, 9.87, 10.90, 11.07, 11.20, 11.63, 11.73, 11.90, 12.07, 12.43, 12.83, 13.17 (end card). Render 3.93 (cut), 6.17, 6.20, 6.50, 6.90 (cut), 9.10, 9.13, 9.17, 9.43, 12.07, 12.10, 12.40, 12.80 (end card).

Measured (320x180 frames, caption row 0.48 to 0.70 H, heat band median over rows 0.30 to 0.50 H):

| Quantity | Reference | Round 4 |
|---|---|---|
| Intro grade (0.8 to 3.5 s), mean RGB, saturation, luma p1/p50/p99 | 136,152,169, 0.22, 17/163/185 | 131,136,133, 0.08, 73/114/220 |
| Body grade | 130 to 135, 132 to 138, 149 to 154, sat 0.24 to 0.27, p50 151 to 158 | shot 2 138,142,150, 0.15, p50 151. Shot 3 151,137,126, 0.21 (warm) |
| Heat band background, luma | 153 to 176, 4 to 25, 2, luma 52 to 68 | 165 to 168, 9 to 15, 1 to 2, luma 55 to 57 |
| Brightest caption pixels in the band | flash 1 212,181,161 tan, flashes 2 and 3 254,207,105 to 254,211,115 gold | 254,219,140 pale gold on all three |
| Heat band rows | 0.12 to 0.88 H | 0.11 to 0.72 H |
| Pink theme | 254,5,86 (to flash 1), 222,11,138 (after flash 1) | 226,9,146 throughout |
| Red phrase after flash 2 | 236,27,28 (9.87 to 10.30) | none |
| Blue theme | 0,100,197 | 25,111,221 |
| Wipe pop colour | mint 0,245,167 (5.00, 8.00), orange 252,151,55 in the blue phase (10.90) | mint 2,244,159 every wipe |
| Captions on screen | 4.53 to 13.13 continuous | 4.20 to 12.77 continuous |
| Heat flashes | 6.53, 9.47, 12.43 (3) | 6.15, 9.10, 12.05 (3) |
| End card start after the last heat start | +0.74 s (13.17) | +0.75 s (12.80) |
| End card mean RGB | 19,20,32 | 14,18,31 |
| Audio RMS, 0.25 s windows | -21 to -30 dBFS to 4.4 s, -14 to -16 body, peak -5 at 13.3, silent from 14.5 s | -19 to -23 flat 0 to 17.5 s, dip to -25 at 6.75 to 7.5 |
| SFX in the EDL | none | 22 ticks, 6 clicks, 3 whooshes, 1 impact |

## Status of round 3 findings

| ID | Round 3 issue | Severity in round 3 | Status | Evidence in round 4 |
|---|---|---|---|---|
| N01 | End card timing after the last heat flash, HUD on the card | major | closed | Card at 12.80, 0.75 s after heat 3 (reference 0.74 s). No HUD event after 12.42, nothing draws on the card (grid 06, 07). |
| N02 | Heat band red level, caption colour in the band | major | closed | Band 165,9,1, luma 56 (reference 52 to 68), caption pale gold 254,219,140, the brightest thing in frame (grid 04 to 06). Residual flash 1 tan is P32. |
| N03 | Grade (pale, flat, cool) | major | open | Unchanged from round 3: intro p50 114 against 163, neutral grey, shot 3 warm 151,137,126 (P01). |
| N04 | Colour theme order | minor | open | Blue from 9.47 at the band exit, no red phrase (P02). |
| N05 | Glitch reveal | minor | open | Full frame from frame 0 to 0.47 (grid 02, P03). |
| N06 | Panel strips at cycle start | minor | open | Bar directly at 3.93 (grid 03, P04). |
| N07 | Detect wipe placement | minor | open | Top strip 0.08 to 0.28 H at 4.68, half-width strip at 5.41 (grid 10, P05). |
| N08 | Square markers | minor | open | Small red and blue squares at 6.15, 6.64, 9.10, 9.59, 12.05 (P08). |
| N09 | Readouts | minor | open | Small grey monospace (grid 09, P09). |
| N10 | X marks and brackets | minor | open | L brackets on every bar (P11). |
| N11 | Caption glow | minor | open | `glow` still 6 (P12). |
| N12 | Pink colour | minor | open | 226,9,146 against 254,5,86 (P13). |
| N13 | Cut glitches | minor | open | 6.90 to 7.15 and 15.73 under the card (P14). |
| N14 | Zoom pulse | minor | open | 7.87 to 8.11 (P15). |
| N15 | Sound effects | minor | open | 32 SFX (P16). |
| N16 | Audio structure | minor | open | Flat level, music full under the card (P17). |
| N17 | Words per caption | minor | partly closed | The trailing OF is gone. DESTROYED, DESTROYING single words and SINCE 19 JULY 2026 four words remain (P18). |
| N18 | Heat entry and exit | minor | open | White-washed first frames 6.15, 9.10, 12.05, faded tails 6.50, 9.43, 12.40 (P19). |
| N19 | Heat band height | minor | open | 0.11 to 0.72 H (P20). |
| N20 | Depth layering | cosmetic | intentional, owner directive | P21. |
| N21 | Caption face | cosmetic | intentional, owner directive | P22. |
| N22 | Detect wipe timing | cosmetic | open | P23. |
| N23 | Heat band contour lines | cosmetic | open | Gold rim lines along the cloth edges at 6.18, 9.13, 12.08 (P24). |
| N24 | Free-floating wipe cut-out | cosmetic | open | Pale blob in the top strip at 4.68 (P25). |
| N25 | Readout content | cosmetic | open | P26. |
| N26 | Blue colour | cosmetic | open | P27. |
| N27 | End card artwork | cosmetic | unchanged, platform UI | P28. |
| N28 | Clips spent under the end card | cosmetic | open | Now shots 4 and 5 (12.80 to 17.70) both sit entirely under the card (P29). |
| N29 | First top bar length | cosmetic | open | P30. |
| N30 | Caption entry fade | cosmetic | open | P31. |

Closed: N01, N02 (both round 3 majors). Partly closed: N17. No round 3 minor is fully closed.

## Current differences

| ID | Category | Reference time | Render time | Description | Severity | Suggested change |
|---|---|---|---|---|---|---|
| P01 | Grade (pale, flat, cool) | 0.00 to 4.03, luma 17/163/185, B above R by 33, sat 0.22 | 0.00 to 3.93, luma 73/114/220, neutral (B above R by 2), sat 0.08. 6.90 to 12.80 warm, R above B by 25 | The clean 8 beat hold that sets the look is mid grey with clipped highlights, not pale and cool. Shot 3 stays beige. The `grade.base` values are the same as round 3 and the measurements did not move. | major | `style.json` `grade.base`: `target_luma` 0.6 to 0.68, `contrast` 0.85 to 0.72, `saturation` 0.78 to 0.9, `tint` [0.93,1.0,1.08] to [0.88,1.0,1.14]. `engine/grade` code path: compress highlights so p99 sits near 0.73 (white point 188). `engine/clips.py`: prefer a pale, cool clip (luma median above 140, B above R) for the intro shot. |
| P02 | Colour theme order | pink 254,5,86 to 6.53, magenta-pink 222,11,138 after flash 1, red 236,27,28 STAR TREK 9.87 to 10.30 after flash 2, blue from 10.37 | pink 226,9,146 from 4.20 to 9.10, blue from 9.47 | No hue step at flash 1 and no red phrase after flash 2. | minor | `style.json` `captions.themes`: [0] [254,5,86], [1] [222,11,138], add a per-theme `after_flash` colour [236,27,28] for 1 phrase on [2]. `ext/hud_lyric.py` `hud_row`: honour `after_flash`. |
| P03 | Glitch reveal | 0.00 to 0.13 clean, 0.13 to 0.57 blocks on the subject only | 0.00 to 0.47 full frame from frame 0 | Grid 02. | minor | `style.json` first `hud_glitch`: `sec` 0.13, `span_beats` [0, 0.9]. `ext/hud_lyric.py` `hud_glitch`: confine blocks to the matte bounding box or the centre 40 percent. |
| P04 | Overlay rhythm, panel strips | 4.03 to 4.30 white and grey panels slide in, then the bar at 4.33 | 3.93 bar directly | First event of each cycle missing (grid 03). | minor | `ext/hud_lyric.py` `hud_bar`: `panels` option. `style.json`: new `hud_bar` rule offset 7.4, `dur_beats` 0.6, `panels: true`. |
| P05 | Detect wipe placement | 5.00 brown band behind the caption row (0.55 to 0.70 H), 5.73 tall top panel with large DETECTING | 4.68 thin top strip 0.08 to 0.28 H, 5.41 half-width strip under the words | Order and geometry differ (grid 10). | minor | `style.json`: first `hud_wipe` `band_y` 0.62, `band_h` 0.15, no `width`. Second `band_y` 0.15, `band_h` 0.30. `ext/hud_lyric.py` `hud_wipe` `label_size` 0.04 H. |
| P06 | Detect wipe duration | 5.00 to 5.13 (4 frames), 5.73 to 5.97 (8 frames) | 4.68 to 4.73, 5.41 to 5.47 (2 frames each) | Wipes read as a flicker, the mint pop is barely seen (new). | minor | `style.json` `hud_wipe` `dur_beats` 0.125 to 0.27 (first) and 0.5 (second). |
| P07 | Wipe pop colour per theme | mint 5.00, 8.00, orange 252,151,55 at 10.90 in the blue phase | mint at 10.58 and 11.31 | No orange pop in the blue phase (new). | minor | `style.json` `captions.themes[2]` and `[3]`: `wipe_color` [252,151,55]. `ext/hud_lyric.py` `hud_wipe`: read the pop colour from the active theme. |
| P08 | Square markers | one large red square 5.97, 8.90, 9.10, 11.90 (about 0.12 W) | small red and blue squares at 6.15, 6.64, 9.10, 9.59, 12.05 | Grid 05, 06. | minor | `style.json` `hud_marks`: one rule offset 11.5, `count` 1, `size` 130, `color` [200,16,16]. Drop the offset 13.5 rule and the size 50 rule. |
| P09 | Readouts | 4.40, 5.35, 7.30 white bold wide sans, about 2.3 percent H | 4.00, 4.95, 6.92 small grey monospace, about 1.2 percent H | Grid 09. | minor | `ext/hud_lyric.py` `hud_bar`: bold sans at 0.022 H, opacity 1.0. |
| P10 | HUD inside the heat flash | 6.57 to 6.90, 9.47 to 9.83, 12.47 to 12.80 red readout column at the right and X mark over the band, 6.43, 9.40, 12.30 red bar slides in at the lower left before the band | heat band clean apart from small squares, no lead-in | Grid 04 to 06 (new). | minor | `ext/hud_lyric.py` `hud_heat`: `readouts` option drawing the readout column in (255,80,60) at x 0.62 W, plus an X mark. `style.json` `hud_heat.params`: `readouts: true`, `lead_in_beats` 0.25 with a red bar at y 0.80 to 0.88 H. |
| P11 | X marks and brackets | 4.53, 7.50 large two-tone X at the bar edge, no brackets | thin X inside L brackets on every bar | Grid 09. | minor | `style.json` `hud_bar` `brackets: false`. `ext/hud_lyric.py` `hud_bar`: `xmark_size` 0.17 W on the bar edge. |
| P12 | Caption glow | wide pale halo lighter than the letter (4.60 to 6.50) | tight same-colour halo | Grid 08. | minor | `style.json` `themes[*].glow` 6 to 14. `ext/hud_lyric.py` `hud_row`: mix the glow 50 percent toward white. |
| P13 | Caption colour, pink | 254,5,86 (4.60 to 6.50) | 226,9,146 (4.20 to 9.10) | Magenta rather than red pink for the opening phrases. | minor | Covered by P02 (`themes[0].color` [254,5,86]). |
| P14 | Cut glitches | none | 6.90 to 7.15 (tears BEFORE USE), 15.73 to 15.98 under the card | Grid 04, 09. | minor | `style.json`: remove the `hud_glitch` `at: cut` move. |
| P15 | Zoom pulse | none | 7.87 to 8.11 | | minor | `style.json`: remove the `zoom_pulse` move. |
| P16 | Sound effects | song only | 22 caption ticks, 6 clicks (wipes), 3 whooshes (heat), 1 impact (7.87) | | minor | `style.json`: `captions.caption_sfx` null, `sfx` []. |
| P17 | Audio structure | quiet intro to 4.4 then +7 dB body, peak at 13.3, silent from 14.5 s | flat -19 to -23 dBFS, music full under the card to 17.5 s | No lift into the body, no outro cut. | minor | `engine/audio.py`: pick the song start so the biggest rise lands on beat 8. Add `structure.outro_fade_s` 0.8 from the card start in `style.json`. |
| P18 | Words per caption | always 2 or 3 | DESTROYED 5.90, SINCE 19 JULY 2026 7.87, DESTROYING 10.82 | One or four words. | minor | `engine/captions.py` grid phrasing: merge single words into a neighbour phrase, split four words into two plus two. |
| P19 | Heat entry and exit | hard on 6.53 (band slides in), hard off 6.93 | white-washed first frames 6.15, 9.10, 12.05, desaturated fading tails 6.50, 9.43, 12.40 | Grid 04 to 06. | minor | `ext/hud_lyric.py` `hud_heat`: remove the `u < 0.12` white mix and the `u > 0.85` alpha ramp. |
| P20 | Heat band height | 0.12 to 0.88 H | 0.11 to 0.72 H | Bottom fifth stays in the normal picture. | minor | `style.json` `hud_heat.params.y1` 0.73 to 0.884. |
| P21 | Depth layering | middle word hidden by the subject | some phrases in front, some behind | Intentional, owner directive. | cosmetic | none, intentional, owner directive. |
| P22 | Caption face | wide geometric heavy face | Archivo Black | Intentional, owner directive. | cosmetic | none, intentional, owner directive. |
| P23 | Detect wipe timing | +0.67 s, +1.40 s after the bar | +0.74 s, +1.48 s | | cosmetic | `style.json` `hud_wipe` offsets 9.375 and 10.875. |
| P24 | Heat band texture | 6.53 to 6.90 rim only on the subject | 6.18, 9.13, 12.08 gold contour lines along cloth edges | | cosmetic | `ext/hud_lyric.py` `hud_heat`: skip the edge rim when the matte is the fallback or spans more than 40 percent of the frame. |
| P25 | Wipe cut-out | 5.73 white subject silhouette | 4.68 pale blob in the top strip | | cosmetic | `ext/hud_lyric.py` `hud_wipe`: skip the cut-out on the fallback matte. |
| P26 | Readout content | glyph blocks | hex strings | | cosmetic | `ext/hud_lyric.py` `hud_bar`: glyph block column. |
| P27 | Caption colour, blue | 0,100,197 | 25,111,221 | Slightly lighter. | cosmetic | `style.json` `themes[2].color`, `themes[3].color` [0,100,197]. |
| P28 | End card artwork | gradient bar into a search bar with logo | plain white bar | Platform UI. | cosmetic | none needed. |
| P29 | Structure | single take | shots 4 (12.80 to 15.73) and 5 (15.73 to 17.70) both entirely under the card | Clips spent where nobody sees them. | cosmetic | `engine/plan.py`: end the last shot at the card start. |
| P30 | First top bar length | 4.33 to 4.97 (0.64 s) | 3.93 to 4.43 (0.49 s) | | cosmetic | `style.json` `hud_bar` offset 8 `dur_beats` 1.0 to 1.3. |
| P31 | Caption entry | hard pop (GRAB MAMA A 4.53) | 4 TO 9% fades in over about 3 frames from 4.18 | Grid 03. | cosmetic | `ext/hud_lyric.py` `hud_row`: hard pop when the onset is not under a wipe. |
| P32 | Band caption colour, flash 1 | 212,181,161 tan | 254,219,140 gold | Flash 1 in the reference is tan, gold only from flash 2 (new). | cosmetic | `style.json` `captions.band_color` as a list per flash: [[212,181,161],[254,207,105],[254,211,115]]. `ext/hud_lyric.py`: index it by heat count. |
| P33 | Hold after heat 3 | 12.83 to 13.13 blue caption with an X mark and readouts at the left | 12.42 to 12.77 blue caption on clean footage | (new) | cosmetic | `style.json`: a `hud_bar` rule offset 14.0, `dur_beats` 0.6, `side: left`, `when.frac_max` 0.74, no top bar (`bar: false`). |

## Grid files

All in `hud-lyric-light/review-round-4/`. Reference row above (REF), render row below (R4), times in each cell. Grids 02 to 10 pair matching events, not proportional times.

1. `01-overview-proportional.png` 24 frames over the whole duration (reference time scaled to its length)
2. `02-intro-glitch.png` glitch reveal and the clean hold, ref 0.00 to 3.90 vs render 0.00 to 3.85
3. `03-cycle1-start.png` panel strips, top bar, first caption and first detect wipes, ref 4.03 to 5.85 vs render 3.93 to 5.45
4. `04-heat-flash-1.png` heat flash 1 and the next cycle, ref 6.43 to 7.93 vs render 6.05 to 7.63
5. `05-heat-flash-2.png` square lead-in, heat flash 2 and the theme change, ref 8.90 to 10.90 vs render 8.70 to 10.58
6. `06-heat-flash-3-to-card.png` heat flash 3 into the end card, ref 11.63 to 13.50 vs render 11.31 to 13.20
7. `07-end-card.png` end card, ref 13.30 to 17.10 vs render 13.00 to 17.60
8. `08-captions-themes.png` caption colours and holds across all themes
9. `09-top-bar-readouts.png` top bar, DETECTING, readouts, X marks and the cut glitch at 6.92
10. `10-wipes.png` every detect wipe, ref 5.00 to 11.00 vs render 4.68 to 11.33

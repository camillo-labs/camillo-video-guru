MAJOR: 3, MINOR: 18, COSMETIC: 10. Major differences remain (3).

# hud-lyric-light, review of round 2

Reference: `_source/v26044gc0000dau3ftvog65vlo4gptag.MP4` (1024x576, 30 fps, 17.17 s). Render: `hud-lyric-light/rounds/round-2.mp4` (1280x720, 30 fps, **15.73 s**, 32 beats at 122 BPM). The brief says 17.2 s, but the file is 15.73 s (16 s requested, `end_on_bar`), the same length as round 1. Times are seconds in each file. The TikTok watermark, the TikTok logo and search bar, the footage subject and the caption words are out of scope.

Scene detection (`select='gt(scene,0.2)'`): reference 5.17, 5.73, 5.83, 6.17, 6.53, 6.93, 7.93, 8.10, 8.67, 8.93, 9.10, 9.47, 9.87, 10.90, 11.07, 11.20, 11.63, 11.90, 12.07, 12.43, 12.83, 13.17 (all HUD events, end card at 13.17). Render 0.03, 3.93 (cut), 6.17, 6.50, 6.90 (cut), 9.10, 9.43, 11.83 (end card), 12.07 (heat 3 on the end card).

Measured (320x180 frames, caption row 0.50 to 0.68 H):

| Quantity | Reference | Round 2 |
|---|---|---|
| Intro grade, mean RGB, saturation, luma p1/p50/p99 | 138,153,169, 0.21, 19/166/187 | 104,108,105, 0.11, 0/77/228 (dark rack shot) |
| Body grade | 129,133,150, 0.24, 18/153/177 | shot 2 (3.93 to 6.90) 175,170,175, 0.12, 86/188/210. Shot 3 (6.90 to 11.83) 152,138,126, 0.25, 50/151/220 |
| Heat band background | 166,13,5 (flash 1), 155,0,4 (flash 2), 173,15,5 (flash 3) | 196,77,17 (flash 1), 179,45,10 (flash 2) |
| Caption inside the band | 192,175,161 tan (flash 1), 246,201,101 pale gold (flashes 2 and 3) | 249,146,47 orange gold (both) |
| Pink theme | 233,0,86 | 226,9,146 |
| Blue theme | 10,104,193 | 25,111,221 |
| Caption pixel share of the row | 0.15 to 0.20 | 0.36 to 0.39 (about twice the area) |
| Captions on screen | 4.53 to 13.13 continuous | 4.18 to 11.83 continuous |
| Audio RMS, 0.54 s windows | -22 dBFS to 4.3 s, -15 dBFS body, silent from 14.1 s | flat -20 dBFS from 0 to 15.7 s, dip to -25 at 6.5 |

## Status of round 1 majors

| ID | Round 1 issue | Status | Evidence in round 2 |
|---|---|---|---|
| D01 | Only two heat flashes, end card too early | **open (worse)** | The third heat is now planned (`frac_max` 0.8) but the end card still starts at 11.83 (beat 24 of 32), so heat 3 (12.05 to 12.42), its red and blue squares (12.05, 12.54) and a cut glitch (12.80) are drawn on top of the dark end card. Body is 7.9 s against 8.6 s (4.53 to 13.13) in the reference. |
| D02 | Phrases hidden under the end card, last phrase cut | **closed** | Words stop at 11.07, the last phrase DESTROYING holds 11.07 to 11.83 (0.76 s, reference 0.70 s), and the caption row is never empty from 4.18 to 11.83. |
| D03 | Theme order | **partly closed** | Pink now survives flash 1 (pink 4.18 to 9.10) as in the reference. Blue starts straight after flash 2 at 9.47, where the reference keeps STAR TREK red for 9.87 to 10.30 and turns blue only on the next phrase at 10.37. Remaining part is minor (C04). |
| D04 | Caption unreadable inside the heat band | **partly closed** | The caption is now redrawn over the band in `band_color`, so it no longer turns maroon. But the band itself is orange (196,77,17) instead of deep red (166,13,5), and the orange gold text sits on orange with little contrast. Still major (C02). |
| D05 | Grade not pale and flat | **partly closed** | `grade.base` now lifts and desaturates. Shot 2 is pale and flat (luma median 188, saturation 0.12), close to the reference. The intro rack shot is still dark and contrasty (p1 0, median 77, p99 228) for the whole 3.93 s hold, and shot 3 is warm beige (R above B) where the reference is cool (B above R). Still major for the intro (C03). |

## Current differences

| ID | Category | Reference time | Render time | Description | Severity | Suggested change |
|---|---|---|---|---|---|---|
| C01 | Number of heat flashes, end card timing | heat 3 12.43 to 12.80, end card 13.17 (heat 3 + 0.74 s) | end card 11.83, heat 3 12.05 to 12.42 on the end card, squares 12.05 and 12.54, cut glitch 12.80 to 13.05 on the end card | Only two flashes happen over footage. The third flash, its squares and a glitch fire over the dark card, painting it red with a gold contour (grid 07). The body loses its closing phrase over a heat band. | major | `engine/plan.py`: set the end card start to the last planned `hud_heat` start plus 1.5 beats (beat 26 of 34 here), and lengthen the edit to fit (`defaults.duration` 17.2 or `structure.outro_beats` 8 after that point). `engine/render.py`: drop every move whose t0 falls inside the end card, as a guard. |
| C02 | Heat band colour, caption colour in the band | 6.53 to 6.90, 9.47 to 9.83, 12.43 to 12.80 | 6.15 to 6.52, 9.10 to 9.47 | Band is orange (196,77,17 and 179,45,10, luma median 118 and 84) where the reference is deep red (166,13,5, luma median 47 to 58). The band caption is orange gold 249,146,47 on that orange, low contrast. The reference band text is pale tan (192,175,161) on flash 1 and pale gold (246,201,101) on flashes 2 and 3, the brightest thing in frame. The lift in `grade.base` raises footage luma, so `beta -70` no longer keeps it red. | major | `style.json` `hud_heat.params`: `normalise: true`, `range: 0.45`, `floor: 0.02` (module already supports it) or `beta: -110`. `captions.band_color` to [246, 201, 101], and in `ext/hud_lyric.py` `hud_heat` add the theme glow to the redrawn band caption. |
| C03 | Grade (pale and flat) | 0.00 to 4.03 (luma 19/166/187, cool) | 0.00 to 3.93 (luma 0/77/228, neutral dark), 6.90 to 11.83 (warm, 152,138,126) | The 8 beat clean hold that sets the look is a dark, contrasty rack of clothes. Shot 3 is warm beige under the cool tint. | major | `style.json` `clips.select`: add a pale score (`prefer_bright: true` or a luma median above 140 for the intro shot) in `engine/clips.py`. `grade.base`: `contrast` 0.82 to 0.7, `lift` 0.12, `tint` [0.92, 1.0, 1.10], `saturation` 0.65. |
| C04 | Colour theme order | red 9.87 to 10.30 after flash 2, blue from 10.37 | blue from 9.47 | No short red after flash 2. Blue arrives with the band exit instead of on the next phrase. | minor | `ext/hud_lyric.py` `hud_row`: change theme on the first phrase onset after the flash ends, and add an optional `after_flash` colour per theme (`themes[2].after_flash: [238, 28, 31]`, 1 beat). |
| C05 | Glitch reveal | 0.00 to 0.13 clean, 0.13 to 0.57 blocks on the subject, 3 strong frames | 0.00 to 0.47, full frame, from frame 0 | Unchanged from round 1 (D06). | minor | `style.json` first `hud_glitch`: `sec: 0.13`, `span_beats [0, 0.9]`. `ext/hud_lyric.py` `hud_glitch`: confine blocks to the centre box and pulse `amount` on three frames. |
| C06 | Overlay rhythm, panel strips | 4.03 to 4.30 white and grey panels slide in, 4.43 large white card | 3.93 bar appears directly, small white card 5.10 (about 10 percent W) | The first beat of each cycle (sliding panels) is still missing, the card is smaller and later (D07). | minor | `ext/hud_lyric.py` `hud_bar`: `panels: true` and `card_size`. New rule `hud_bar` offset 7.4, `dur_beats 0.6`. |
| C07 | Overlay rhythm, second top bar | 5.30 to 5.70, 8.23 to 8.63, 11.20 to 11.60 (0.40 s) | 4.92 to 5.66, 7.87 to 8.61, 10.82 to 11.56 (0.74 s) | Unchanged (D08). | minor | `style.json` `hud_bar` offset 10: `dur_beats` 1.5 to 0.8. |
| C08 | Detect wipe placement | 5.00 row band behind the caption row (about 0.55 to 0.70 H), 5.73 top panel from the top edge (0 to 0.30 H) with large DETECTING | 4.67 thin band 0.08 to 0.28 H, 5.41 band 0.59 to 0.73 H below the text | Two variants now exist, but in the wrong order, the top one is a floating strip instead of a panel from the edge, and the lower one sits below the words instead of behind them. | minor | `style.json`: swap the params of the two `hud_wipe` rules. Offset 9.5 `band_y 0.62, band_h 0.08`. Offset 11 `band_y 0.15, band_h 0.15` and a `label_size` of 0.04 H in `ext/hud_lyric.py` `hud_wipe`. |
| C09 | Overlay elements, square markers | one large red square (about 10 percent W) at 5.97, 8.90, 9.10, 11.89 | small red and blue squares (3.5 percent W) at 6.15, 6.64, 9.10, 9.59, 12.05, 12.54 | Unchanged (D10). | minor | `style.json` `hud_marks`: one rule at offset 11.5, `dur_beats 1.0`, `count 1`, `size 130`, `color [200,16,16]`. Drop the offset 13.5 rule. |
| C10 | Overlay elements, readouts | 4.40, 5.40 white bold wide sans, about 2.3 percent H | 5.10, 7.10 small grey monospace, about 1.2 percent H | Unchanged (D11). | minor | `ext/hud_lyric.py` `hud_bar`: bold sans at 0.022 H, opacity 1.0. |
| C11 | Overlay elements, X marks and brackets | 4.53, 7.40 large two-tone X on the bar edge, no brackets | 4.00 to 11.56 thin X marks inside L brackets | Unchanged (D12). | minor | `style.json` `hud_bar` offset 8 `brackets: false`. `ext/hud_lyric.py` `hud_bar`: `xmark_size` 0.17 W on the bar edge. |
| C12 | Word spacing, caption size | cap height constant about 9.5 percent H, phrase width varies (NOW HIT about 45 percent W, THE GROCERY SHOP about 80 percent) | every phrase stretched to the full 0.80 span, text area twice the reference (0.36 to 0.39 of the row against 0.15 to 0.20) | Natural word spacing is fixed (D13 closed). The new `fit_up` scales short phrases up to 1.6x, so the type size jumps between phrases and is mostly oversized. | minor | `style.json` `captions.fit_up: false` (shrink only), keep `gap_em 0.35`. |
| C13 | Caption glow | 4.53 onwards, wide pale halo lighter than the letter | 4.18 onwards, tight same-colour halo | Unchanged (D14). | minor | `style.json` `themes[*].glow` 6 to 14. `ext/hud_lyric.py` `hud_row`: mix the glow colour 50 percent toward white. |
| C14 | Caption colour, pink | 233,0,86 (4.53 to 9.47) | 226,9,146 (4.18 to 9.10) | Still magenta instead of red pink (D15). | minor | `style.json` `themes[0].color` and `themes[1].color` to [255, 8, 87]. |
| C15 | Flashes, cut glitches | none | 6.90 to 7.15 (tears BEFORE USE), 12.80 to 13.05 (on the end card) | Unchanged (D17). | minor | `style.json`: remove the `hud_glitch` `at: cut` move. |
| C16 | Flashes, zoom | none | 7.87 to 8.11 | Unchanged (D18). | minor | `style.json`: remove the `zoom_pulse` move. |
| C17 | Sound effects | song only | 20 caption ticks, 6 clicks, 2 whooshes, 1 impact at 7.87 | Unchanged (D19). | minor | `style.json`: `captions.caption_sfx: null`, `sfx: []`. |
| C18 | Audio structure | rise of 7 dB at 4.3 s with the HUD body, music silent from 14.1 s | flat -20 dBFS, dip at 6.5, music at full level under the end card | Unchanged (D20). | minor | `engine/audio.py`: pick the song start so the biggest rise lands on beat 8. Add `structure.outro_fade_s: 1.0` from the end card start. |
| C19 | Words per caption | always 2 or 3 words | DESTROYED 5.90 (1 word), SINCE 19 JULY 2026 7.87 (4 words), DESTROYING 10.82 (1 word) | Unchanged (D21). | minor | `engine/captions.py` / `plan.py` grid phrasing: merge single words into a neighbour and split 4 or more into 2 plus 2. |
| C20 | Heat band entry and exit | 6.50 slide in from the left, hard cut out at 6.93 | 6.15 and 9.10 white washed first frame, 6.47 and 9.43 fading tail | Unchanged (D22). | minor | `ext/hud_lyric.py` `hud_heat`: remove the `u < 0.12` white mix and the alpha ramp at the end, hard out. |
| C21 | Caption handover | caption held at full opacity until the next phrase (5.13, 5.80) | 4 TO 9% fades from 4.92 to 5.16 (row saturation 0.22 to 0.16), partly covered by the white card | The phrase dims in the half-beat gap instead of holding. | minor | `style.json` `captions.timing.phrase_gap_beats` 0.5 to 0, or hold the last word until the next onset in `ext/hud_lyric.py` `hud_row`. |
| C22 | Depth layering | 4.53 onwards, middle word hidden by the subject | 4.18 onwards, no phrase visibly occluded, the fallback ellipse fades the left word at 5.13 | Intentional, owner directive (a share in front, the rest behind, objects not a person). | cosmetic | none, intentional, owner directive. |
| C23 | Caption font | 4.53 onwards (wide geometric heavy face) | Archivo Black | Intentional, owner directive. | cosmetic | none, intentional, owner directive. |
| C24 | Detect wipe timing | +0.67 s, +1.40 s after the bar | +0.74 s, +1.48 s | Unchanged (D23). | cosmetic | `style.json` `hud_wipe` offsets 9.375 and 10.875. |
| C25 | Heat band texture | 6.53 to 6.90 | 6.20, 9.17 | Bright contour lines along object edges remain (D24). | cosmetic | `ext/hud_lyric.py` `hud_heat`: drop the edge overlay when there is no matte. |
| C26 | Detect wipe cut-out | 5.73 white subject silhouette | 4.67 pale blue blob at the top band | Free-floating cut-out with no person (D25). | cosmetic | `ext/hud_lyric.py` `hud_wipe`: skip the inverted cut-out when the matte is the fallback. |
| C27 | Readout content | glyph blocks | hex strings | Unchanged (D26). | cosmetic | `ext/hud_lyric.py` `hud_bar`: glyph block column. |
| C28 | Caption colour, blue | 10,104,193 | 25,111,221 | Slightly lighter (D28). | cosmetic | `style.json` `themes[2].color`, `themes[3].color` to [10, 104, 193]. |
| C29 | End card artwork | 13.17 gradient bar into a search bar | 11.83 plain white bar | Platform UI, outside the style (D29). | cosmetic | none needed. |
| C30 | Structure | single take | shot 4 (12.80 to 15.73) entirely under the end card | One clip spent on hidden frames (D30). | cosmetic | `engine/plan.py`: end the last shot at the end card start. |
| C31 | Aspect and length | 1024x576, 17.17 s | 1280x720, 15.73 s | Aspect matches, the render is 1.4 s shorter than the reference. Fixing C01 restores the length. | cosmetic | `style.json` `defaults.duration` 17.2. |

Closed since round 1: D02 (phrases under the end card), D13 (justified word gaps), the pink-through-flash-1 part of D03. Partly closed: D01 (third heat now planned but lands on the card), D04, D05, D09.

## Grid files

All in `hud-lyric-light/review-round-2/`. Reference row above (REF), render row below (R2), times in each cell.

1. `01-overview-proportional.png` 24 frames over the whole duration (reference time scaled to its length)
2. `02-intro-glitch.png` glitch reveal, ref 0.00 to 0.60 vs render 0.00 to 0.53
3. `03-cycle1-hud-start.png` panel strips, top bar and first caption, ref 3.97 to 4.70 vs render 3.87 to 4.45
4. `04-detect-wipes-c1.png` both detect wipes of cycle 1
5. `05-heat-flash-1.png` heat flash 1 dense, ref 6.47 to 6.97 vs render 6.10 to 6.60
6. `06-heat-flash-2.png` square lead-in and heat flash 2, ref 8.90 to 9.90 vs render 8.80 to 9.50
7. `07-cycle3-heat3-endcard.png` third cycle, ref heat 3 at 12.43 vs render heat 3 on the end card at 12.07
8. `08-outro-end-card.png` end card, ref 13.17 to 17.10 vs render 11.84 to 15.70
9. `09-caption-typography.png` caption row crops, colour, glow, size and spacing
10. `10-cut-glitches.png` render cut glitches at 6.90 and 12.80 vs reference at the same times
11. `11-top-bar-readouts.png` top bar, DETECTING, readouts and X marks at full size
12. `12-caption-handover.png` frames around caption changes, wipes and the band caption

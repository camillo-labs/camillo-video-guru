MAJOR: 3, MINOR: 16, COSMETIC: 11. Major differences remain (3).

# hud-lyric-light, review of round 3

Reference: `_source/v26044gc0000dau3ftvog65vlo4gptag.MP4` (1024x576, 30 fps, 17.17 s). Render: `hud-lyric-light/rounds/round-3.mp4` (1280x720, 30 fps, 17.70 s, 36 beats at 122 BPM). Times are seconds in each file. The TikTok watermark, logo and search bar, the footage subject and the caption words are out of scope.

Scene detection (`select='gt(scene,0.2)'`): reference 5.17, 5.73, 5.83, 6.17, 6.53, 6.57, 6.93, 7.93, 8.10, 8.67, 8.77, 8.93, 9.10, 9.47, 9.50, 9.87, 10.90, 11.07, 11.20, 11.63, 11.73, 11.90, 12.07, 12.43, 12.83, 13.17 (end card). Render 3.93 (cut), 6.17, 6.23, 6.90 (cut), 9.10, 9.17, 12.07, 12.13, 12.80 (cut), 13.80 (end card).

Measured (320x180 frames, caption row 0.50 to 0.68 H):

| Quantity | Reference | Round 3 |
|---|---|---|
| Intro grade (0.8 to 3.5 s), mean RGB, saturation, luma p1/p50/p99 | 136,152,169, 0.22, 19/163/186 | 128,131,128, 0.08, 68/108/221 |
| Body grade | 128,133,150, 0.26, 18/153/187 | shot 2 142,140,144, 0.13, 58/151/231. Shot 3 147,133,122, 0.24, 30/150/231 (warm) |
| Heat band background, luma median | 139,3,2 / 150,5,2 / 162,11,2, luma 51 to 64 | 172,60,13 / 163,53,11 / 164,54,11, luma 124 to 128 |
| Brightest caption pixels in the band | 197,178,158 tan, 240,159,78 and 252,205,107 gold | 248,153,60 orange (all three) |
| Heat band rows | 0.08 to 0.88 H | 0.115 to 0.73 H |
| Pink theme | 241,13,88 (first phrases), 213,19,138 (THE GROCERY SHOP) | 215,21,144 |
| Blue theme | 9,102,193 | 31,110,213 |
| Caption pixel share of the row | 0.12 to 0.24 | 0.09 to 0.29 |
| Captions on screen | 4.53 to 13.13 continuous | 4.20 to 13.80 continuous |
| Heat flashes | 6.53, 9.47, 12.43 (3) | 6.15, 9.10, 12.05 (3) |
| End card start after the last heat start | +0.74 s (13.17) | +1.75 s (13.80) |
| Audio RMS, 0.37 s windows | -22 dBFS to 4.4 s, -15 dBFS body, silent from 14.0 s | flat -20 dBFS 0 to 17.6 s, dip to -25 at 7.0 |

## Status of round 2 findings

| ID | Round 2 issue | Severity in round 2 | Status | Evidence in round 3 |
|---|---|---|---|---|
| C01 | Heat 3 on the end card, end card too early | major | partly closed | All three flashes now fire over footage (6.15, 9.10, 12.05) and the body is 9.6 s. The card now comes 1.75 s after heat 3 instead of 0.74 s, and a top bar, network, X mark and card draw over the dark end card at 13.77 to 14.26. Still major (N01). |
| C02 | Heat band orange, band caption low contrast | major | open | `normalise` on with `range 0.6`, `floor 0.06`, but the band is still orange (172,60,13, luma 128 against 51 to 64) and the caption is orange on orange (N02). |
| C03 | Grade, dark intro, warm shot 3 | major | partly closed | Intro blacks lifted (p1 68 against 0) and saturation 0.08, but median luma 108 against 163 and neutral grey, not cool. Shot 3 still warm (R 147 above B 122) (N03). |
| C04 | Theme order after flash 2 | minor | open | Blue from 9.47 at the band exit, no red phrase (N04). |
| C05 | Glitch reveal | minor | open | Full frame from frame 0, 0.00 to 0.47 (N05). |
| C06 | Panel strips at cycle start | minor | open | Bar appears directly at 3.93 (N06). |
| C07 | Second top bar too long | minor | closed | Now 0.49 s (offset 10, `dur_beats 1.0`), reference 0.40 s. |
| C08 | Detect wipe placement | minor | open | 4.68 thin top strip 0.08 to 0.28 H, 5.41 half-width strip under the words (N07). |
| C09 | Square markers | minor | open | Small red and blue squares at 6.15, 6.64, 9.10, 9.59, 12.05, 12.54 (N08). |
| C10 | Readouts | minor | open | Small grey monospace (N09). |
| C11 | X marks and brackets | minor | open | L brackets on every bar (N10). |
| C12 | Caption size consistency | minor | closed | `fit_up: false`, cap height constant, text area 0.09 to 0.29 of the row against 0.12 to 0.24. |
| C13 | Caption glow | minor | open | Tight same-colour halo (N11). |
| C14 | Pink colour | minor | open | 215,21,144 against 241,13,88 for the opening phrases (N12). |
| C15 | Cut glitches | minor | open | 6.90 to 7.15 tears BEFORE USE, 15.73 on the end card (N13). |
| C16 | Zoom pulse | minor | open | 7.87 to 8.11 (N14). |
| C17 | Sound effects | minor | open | 26 caption ticks, 6 clicks, 3 whooshes, 1 impact (N15). |
| C18 | Audio structure | minor | open | Flat -20 dBFS, music at full level under the card (N16). |
| C19 | Words per caption | minor | open | DESTROYED, DESTROYING, OF single words, SINCE 19 JULY 2026 four words (N17). |
| C20 | Heat entry and exit | minor | open | White washed first frames 6.15, 9.10, 12.05 and fading tails 6.47, 9.42 (N18). |
| C21 | Caption dims in the phrase gap | minor | closed | Row share holds through 5.0 to 5.1 and every later handover, row never empty 4.20 to 13.80. |
| C22 | Depth layering | cosmetic | intentional, owner directive | See N20. |
| C23 | Caption font | cosmetic | intentional, owner directive | See N21. |
| C24 | Detect wipe timing | cosmetic | open | N22. |
| C25 | Heat band contour lines | cosmetic | open | N23. |
| C26 | Free-floating wipe cut-out | cosmetic | open | N24. |
| C27 | Readout content | cosmetic | open | N25. |
| C28 | Blue colour | cosmetic | open | N26. |
| C29 | End card artwork | cosmetic | unchanged, platform UI | N27. |
| C30 | Clips spent under the end card | cosmetic | open | N28. |
| C31 | Length | cosmetic | closed | 17.70 s against 17.17 s. |

Closed: C07, C12, C21, C31. Partly closed: C01, C03.

## Current differences

| ID | Category | Reference time | Render time | Description | Severity | Suggested change |
|---|---|---|---|---|---|---|
| N01 | End card timing relative to the last heat flash | heat 3 12.43, end card 13.17 (+0.74 s), nothing after heat 3 but the held caption | heat 3 12.05, end card 13.80 (+1.75 s). Extra half cycle: bar 12.79, wipe 13.52, bar plus network, X mark and white card 13.77 to 14.26 on the dark card. Last phrase OF (one word) 13.03 to 13.80 | Flash count is right, but the edit runs a fourth cycle after the last flash, and HUD artwork draws over the end card for 0.5 s (grid 08, 13.83 and 14.20). | major | `style.json`: `when.frac_max` 0.8 to 0.7 on both `hud_bar` and both `hud_wipe` rules so nothing fires after the last heat, and `defaults.duration` to give 34 beats (card at last heat + 1.5 beats). `ext/hud_lyric.py` (line 90, `end_card_beats`): skip every `hud_*` event whose t0 is inside the card as a guard. |
| N02 | Heat band red level, caption colour in the band | 6.53 to 6.90, 9.47 to 9.83, 12.43 to 12.80 | 6.15 to 6.52, 9.10 to 9.47, 12.05 to 12.42 | Band is orange (172,60,13, luma median 128) where the reference is deep red (139 to 162, 3 to 11, 2, luma 51 to 64). The band caption is orange 248,153,60 on that orange. Reference band text is tan 197,178,158 on flash 1 and pale gold 240,159,78 to 252,205,107 on flashes 2 and 3, the brightest thing in frame. | major | `style.json` `hud_heat.params`: `range` 0.6 to 0.38, `floor` 0.06 to 0.02 so the band median sits near 0.22 of the colormap (deep red). `captions.band_color` [250,146,45] to [246,201,101]. `ext/hud_lyric.py` `hud_heat`: draw the band caption with the theme glow. |
| N03 | Grade (pale, flat, cool) | 0.00 to 4.03, luma 19/163/186, B above R by 33 | 0.00 to 3.93 luma 68/108/221, neutral grey. 6.90 to 12.80 warm, R above B by 25 | The clean 8 beat hold that sets the look is mid grey, not pale and not cool. Shot 3 stays beige. | major | `style.json` `grade.base`: `target_luma` 0.6 to 0.68, `contrast` 0.85 to 0.72, `tint` [0.96,1.0,1.06] to [0.90,1.0,1.12]. `engine/clips.py`: add a pale-shot preference for the intro shot (luma median above 140). |
| N04 | Colour theme order | STAR TREK red 9.87 to 10.30 after flash 2, blue from 10.37 | blue from 9.47 | No red-gold phrase after flash 2. | minor | `ext/hud_lyric.py` `hud_row`: change theme on the first phrase onset after the flash, with an optional per-theme `after_flash` colour ([238,28,31], 1 beat). |
| N05 | Glitch reveal | 0.00 to 0.13 clean, 0.13 to 0.57 blocks on the subject | 0.00 to 0.47 full frame from frame 0 | Grid 02. | minor | `style.json` first `hud_glitch`: `sec` 0.13, `span_beats` [0, 0.9]. `ext/hud_lyric.py` `hud_glitch`: confine blocks to the centre box. |
| N06 | Overlay rhythm, panel strips | 4.03 to 4.30 white and grey panels slide in, 4.43 large white card | 3.93 bar directly, small card 4.95 | First beat of each cycle missing. | minor | `ext/hud_lyric.py` `hud_bar`: `panels` option, new `hud_bar` rule offset 7.4, `dur_beats` 0.6. |
| N07 | Detect wipe placement | 5.00 row band behind the caption (0.55 to 0.70 H), 5.73 top panel from the top edge with large DETECTING | 4.68 thin strip 0.08 to 0.28 H, 5.41 half-width strip under the words | Order and geometry differ (grid 04). | minor | `style.json`: first `hud_wipe` `band_y` 0.62, `band_h` 0.15, no `width`. Second `band_y` 0.15, `band_h` 0.15, `ext/hud_lyric.py` `hud_wipe` `label_size` 0.04 H. |
| N08 | Square markers | one large red square at 5.97, 8.90, 9.10, 11.89 | small red and blue squares at 6.15, 6.64, 9.10, 9.59, 12.05, 12.54 | Grid 06, 09. | minor | `style.json` `hud_marks`: one rule offset 11.5, `count` 1, `size` 130, `color` [200,16,16]. Drop the offset 13.5 rule. |
| N09 | Readouts | 4.40, 5.40 white bold wide sans, about 2.3 percent H | 4.00, 5.00 small grey monospace, about 1.2 percent H | Grid 11. | minor | `ext/hud_lyric.py` `hud_bar`: bold sans at 0.022 H, opacity 1.0. |
| N10 | X marks and brackets | 4.53, 7.40 large two-tone X at the bar edge, no brackets | thin X inside L brackets every bar | Grid 11. | minor | `style.json` `hud_bar` `brackets: false`. `ext/hud_lyric.py` `hud_bar`: `xmark_size` 0.17 W on the bar edge. |
| N11 | Caption glow | wide pale halo lighter than the letter | tight same-colour halo | Grid 10. | minor | `style.json` `themes[*].glow` 6 to 14. `ext/hud_lyric.py` `hud_row`: mix the glow 50 percent toward white. |
| N12 | Caption colour, pink | 241,13,88 (4.53 to 6.53) | 215,21,144 (4.20 to 9.10) | Magenta rather than red pink for the opening phrases. | minor | `style.json` `themes[0].color` [255,8,87], keep `themes[1]` at [230,10,150]. |
| N13 | Cut glitches | none | 6.90 to 7.15 (tears BEFORE USE), 15.73 under the card | Grid 11, 7.00. | minor | `style.json`: remove the `hud_glitch` `at: cut` move. |
| N14 | Zoom pulse | none | 7.87 to 8.11 | | minor | `style.json`: remove the `zoom_pulse` move. |
| N15 | Sound effects | song only | 26 ticks, 6 clicks, 3 whooshes, 1 impact | | minor | `style.json`: `captions.caption_sfx` null, `sfx` []. |
| N16 | Audio structure | -22 dBFS to 4.4 s then -15 dBFS, silent from 14.0 s | flat -20 dBFS, music full under the card to 17.6 s | No rise into the body, no outro cut. | minor | `engine/audio.py`: pick the song start so the biggest rise lands on beat 8, add `structure.outro_fade_s` 0.8 from the card start. |
| N17 | Words per caption | always 2 or 3 | DESTROYED 5.90, SINCE 19 JULY 2026 7.87, DESTROYING 10.82, OF 13.03 | One or four words. | minor | `engine/captions.py` grid phrasing: merge single words into a neighbour, split four into two plus two, drop a trailing fragment that would land after the last heat. |
| N18 | Heat entry and exit | 6.50 slide in, hard out 6.93 | white washed first frames 6.15, 9.10, 12.05, fading tails 6.47, 9.42 | Grid 05, 06. | minor | `ext/hud_lyric.py` `hud_heat`: remove the `u < 0.12` white mix and the `u > 0.85` alpha ramp. |
| N19 | Heat band height | 0.08 to 0.88 H | 0.115 to 0.73 H | Band stops above the lower fifth, the reference covers almost the full frame (new). | minor | `style.json` `hud_heat.params.y1` 0.73 to 0.884. |
| N20 | Depth layering | middle word hidden by the subject | some phrases in front, some behind, behind ones partly translucent through the fallback ellipse (DESTROYED 5.95) | Intentional, owner directive. | cosmetic | none, intentional, owner directive. |
| N21 | Caption face | wide geometric heavy face | Archivo Black | Intentional, owner directive. | cosmetic | none, intentional, owner directive. |
| N22 | Detect wipe timing | +0.67 s, +1.40 s after the bar | +0.74 s, +1.48 s | | cosmetic | `style.json` `hud_wipe` offsets 9.375 and 10.875. |
| N23 | Heat band texture | 6.53 to 6.90 | 6.22, 9.17, 12.12 | Bright contour lines along object edges. | cosmetic | `ext/hud_lyric.py` `hud_heat`: skip the edge rim when the matte is the fallback. |
| N24 | Wipe cut-out | 5.73 white subject silhouette | 4.68 pale blob in the top strip | | cosmetic | `ext/hud_lyric.py` `hud_wipe`: skip the cut-out on the fallback matte. |
| N25 | Readout content | glyph blocks | hex strings | | cosmetic | `ext/hud_lyric.py` `hud_bar`: glyph block column. |
| N26 | Caption colour, blue | 9,102,193 | 31,110,213 | Slightly lighter. | cosmetic | `style.json` `themes[2].color`, `themes[3].color` [10,104,193]. |
| N27 | End card artwork | gradient bar into a search bar with logo | plain white bar | Platform UI. | cosmetic | none needed. |
| N28 | Structure | single take | shot 4 runs into the card, shot 5 (15.73 to 17.70) entirely under it | | cosmetic | `engine/plan.py`: end the last shot at the card start. |
| N29 | First top bar length | 4.33 to 4.97 (0.64 s) | 3.93 to 4.43 (0.49 s) | | cosmetic | `style.json` `hud_bar` offset 8 `dur_beats` 1.0 to 1.3. |
| N30 | Caption entry | hard pop (GRAB MAMA A 4.53) | 4 TO 9% fades in over about 3 frames from 4.18 | | cosmetic | `ext/hud_lyric.py` `hud_row`: hard pop when the onset is not under a wipe. |

## Grid files

All in `hud-lyric-light/review-round-3/`. Reference row above (REF), render row below (R3), times in each cell.

1. `01-overview-proportional.png` 24 frames over the whole duration (reference time scaled to its length)
2. `02-intro-glitch.png` glitch reveal, ref 0.00 to 0.53 vs render 0.00 to 0.47
3. `03-intro-hold-grade.png` clean intro hold and cycle start, ref 1.00 to 4.20 vs render 1.00 to 4.05
4. `04-cycle1-hud.png` top bar, first captions and both detect wipes of cycle 1
5. `05-heat-flash-1.png` heat flash 1, ref 6.53 to 6.97 vs render 6.15 to 6.60
6. `06-heat-flash-2.png` square lead-in and heat flash 2, ref 8.95 to 9.90 vs render 8.90 to 9.55
7. `07-heat-flash-3-to-card.png` heat flash 3 into the end card, ref 12.43 to 13.20 vs render 12.05 to 13.30
8. `08-end-card.png` end card, ref 13.13 to 17.10 vs render 13.50 to 17.60 (HUD on the card at 13.83 and 14.20)
9. `09-cycle2-3-captions.png` cycles 2 and 3, theme order and caption holds
10. `10-caption-typography.png` caption rows at full size, colour, glow and size
11. `11-top-bar-readouts.png` top bar, DETECTING, readouts, X marks and the cut glitch at 7.00

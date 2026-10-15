MAJOR: 2, MINOR: 22, COSMETIC: 7. Major differences remain: yes (2).

# hud-lyric-heat, review round 4

Reference: `_source/ScreenRecording_10-11-2026 19-40-58_1.mov`, cropped to the picture (crop=1288:724:0:8, scaled to 1280x720, 30 fps) as `review-round-4/ref-crop.mp4`, 12.6 s. Render: `rounds/round-4.mp4` (1280x720, 30 fps, 15.73 s, 122 BPM). Render event times come from `rounds/round-4.edl.json`.

Alignment for paired grids is unchanged from earlier rounds: reference loop point (black matte 1.83 to 1.90 s) maps to render 0.0 s, reference first HUD 6.37 s to render 3.93 s, reference heat flashes 8.27 and 10.60 s to render 6.15 and 9.10 s, reference end matte 11.73 s to render 15.67 s.

Measurements behind the table:

- Scene detection (scene > 0.2): reference 25 changes in 12.6 s, none of them cuts. Render 13 changes in 15.7 s (0.03, 3.93, 6.17, 6.20, 6.90, 7.90, 9.10, 9.17, 12.07, 12.13, 12.80, 12.83, 15.67), three of them cuts and one the new end matte. Bar flicker and mark re-placement do not register.
- Caption (red pixel bbox, 5 fps): reference glyph height 9.4 % on every phrase, centre 49.4 %, span up to 5 to 94 %, colour (189, 16, 16). Render 9.2 % on most phrases, 10.6 % on EEA, 2024 (7.2 to 7.8), 8.9 % on SINCE 19 JULY 2026 (8.0 to 8.2), 8.1 % on 6.94 MILLION TONNES (12.4 to 12.8), centre 48.8 %, span up to 5 to 91 %, colour (206, 18, 20).
- Heat band (rows 11.5 to 73 %): reference mean (173, 73, 35), saturation 0.77, 14 % near black (the person), horizontal detail 11. Render flash 1 (6.20 to 6.37) mean 160 to 210, 76 to 107, 15 to 20, saturation 0.91, near black alternating 7 % and 30 % frame to frame (blobs on the fabric pile), detail 4 to 5. Flashes 2 and 3 mean (188, 84, 16), saturation 0.93, detail 3.
- Grade of clean footage: reference (119, 144, 155), saturation 0.31, luma 1st and 99th percentile 4 and 246. Render 0.6 to 3.9 white 224; 4.0 to 6.1 black 50, white 206, saturation 0.16 (milky); 6.95 to 9.0 white 212; 12.85 to 15.6 black 34, white 209, saturation 0.15.
- Audio: reference -12.6 LUFS, silences 1.88 to 2.01 and 11.80 to 11.92 s (under and just after the matte). Render -18.6 LUFS, one silence 15.50 to 15.65 s, which ends before the matte at 15.67. EDL lists 28 caption ticks, 8 clicks, 4 whooshes (one at 15.00 with no heat flash), impact at 7.87 and the new gap.
- Ending: last phrase OF TEXTILE WASTE holds 13.03 to 15.73 (2.7 s), no HUD after 14.32, black matte with the caption on 15.67 and 15.70 (2 frames).

## Round 3 findings

| Round 3 ID | Topic | Status | Evidence in round 4 |
|---|---|---|---|
| M1 | Ending | closed | `hold_last` keeps the last caption to the end, a black matte with the caption on black closes the edit (15.67 to 15.70) and a 0.15 s audio gap sits at 15.50 (grid 09). Residual timing and HUD details are now m21 and m22, minor. |
| M2 | Heat flash subject fill | open | Vision still labels the fabric pile a person. At 6.17 to 6.30 dark maroon blobs fill up to 30 % of the band, flicker frame to frame and cover DESTROYED (grid 06). Flashes 2 and 3 are clean. Now M1. |
| M3 | Overlay rhythm | partly closed | Bars now flicker (blank frame at 4.17), readouts and X marks re-roll every 3 frames (grid 05). Scene changes 12 (excluding the matte) against 25; card and bracket frame still hold, nothing big (band, panel, square) changes every 3 to 6 frames. Now M2. |
| m1 | Caption size, long phrases | partly closed | Span now reaches 91 %, SINCE 19 JULY 2026 grows to 8.9 %. 6.94 MILLION TONNES still 8.1 %, EEA, 2024 now 10.6 %. Now m1. |
| m2 | Detect wipe | partly closed | Head band moved to the upper row (y 0.18) like the reference and reaches full width by its 3rd frame (4.73). Still flat brown, pale grey cut-out block, lower band 1 frame at 30 % width (grid 08). Now m2. |
| m3 | Caption animation in | open | Now m3. |
| m4 | Words per caption | open | Now m4. |
| m5 | Heat colour and grain | partly closed | Mean (188, 84, 16) against (173, 73, 35), closer than round 3's (210, 113, 30); still over-saturated (0.93) and smooth (detail 3). Now m5. |
| m6 | Heat slide and seam | open | 6.13 to 6.27, 9.12 to 9.18, 12.07 to 12.13. Now m6. |
| m7 | Caption inside heat band | open | Now m7. |
| m8 | Square markers | open | Now m8. |
| m9 | Heat timing | open | Now m9. |
| m10 | DETECTING top bar | open | Now m10. |
| m11 | Readouts | open | Now m11. |
| m12 | X marks | open | Now m12. |
| m13 | Card | open | Now m13. |
| m14 | Glitch reveal | open | Now m14. |
| m15 | Glitch at cuts | open | Now m15. |
| m16 | Zoom pulse | open | Now m16. |
| m17 | Sound effects | open | Now m17. |
| m18 | Loudness | open | -18.6 LUFS. Now m18. |
| m19 | Grade | open (worse on shot 2) | Now m19. |
| m20 | First HUD on a cut | open | Now m20. |
| C1 to C5 | Colour, brackets, network, heat first frame, intro length | open | Unchanged. |
| C6 | Audio at loop point | closed | A gap now exists; its placement against the matte is m21. |
| C7, C8 | Face, depth | intentional, owner directive | Unchanged. |

Minors closed this round: none fully (m1, m2 and m5 partly).

## Current differences

| ID | Category | Reference time (s) | Render time (s) | Description | Severity | Suggested change |
|---|---|---|---|---|---|---|
| M1 | Heat flash, subject fill | 8.27 to 8.57, 10.60 to 10.93 (only the person is black, caption readable) | 6.17 to 6.33 | Vision returns a person matte on the fabric pile, so flash 1 fills up to 30 % of the band with dark maroon blobs that change shape every frame, slide with the band and erase most of DESTROYED. | major | `engine/ext/hud_lyric.py` `hud_heat`: before `subject_black`, require matte area below 0.35 of the band and a Vision face or head hit, and hold the mask from the flash's first frame. `engine/render.py`: set `mask_kind` to `object` when Vision confidence is low. Fallback: `style.json` `hud_heat.params.subject_black` false. |
| M2 | Overlay rhythm and scene-change density | 6.37 to 11.83: 25 scene changes, overlays pop 1 to 4 frames, wipe bands, heat-textured panels and squares jump in every 3 to 6 frames | 3.93 to 15.73: 12 changes, bars flicker and marks re-roll, but bracket frame and card hold for the bar, no extra bands or panels | Better texture, still steady. The reference changes something large every 3 to 6 frames; the render changes something large about every 0.75 s. | major | `engine/ext/hud_lyric.py` `hud_bar`: card hold 4 frames then re-place, brackets on alternate `mark_frames`. `style.json`: add a 1-frame head `hud_wipe` at `offset` 8, a second `hud_marks` at `offset` 11.5 with `size` 90, and a `hud_wipe` lower-band rule at `offset` 10.5. |
| m1 | Caption size | 9.4 % on every phrase, span up to 94 % | 7.2 to 7.8 EEA, 2024 (10.6 %, comma descender), 12.4 to 12.8 6.94 MILLION TONNES (8.1 %) | Height varies by phrase; reference holds one cap height. | minor | `engine/ext/hud_lyric.py` `hud_row`: size by cap height, not ink bbox, so punctuation does not change scale. `style.json` `captions.span` 0.90 to 0.94. |
| m2 | Detect wipe | 8.67 to 8.73, 11.07 to 11.10 (upper band, sepia footage texture, cream cut-out); 7.03 to 7.13 (lower band, 45 % width, 13 % high, 4 to 5 frames) | 4.67 to 4.73, 7.62, 10.57, 13.52 (upper band, flat brown, pale grey translucent block); 5.43, 8.37, 11.32, 14.27 (lower band, 1 frame, 30 % wide, 7 % high, label about 1 % high) | Position and count match. Texture, cut-out and lower band do not. `texture: true` has no visible effect. | minor | `engine/ext/hud_lyric.py` `hud_wipe`: texture as `BROWN * (0.35 + 0.6 * g0)` of the footage under the band, skip the cut-out when `mask_kind != 'person'`. `style.json` lower-band rule: `dur_beats` 0.3, `band_h` 0.12, label 0.025. |
| m3 | Caption animation in | 6.80 (pale 1 frame), 7.17 to 7.23 (from pale pink over 3 frames) | 4.17, 5.13, 13.03 and every onset | Hard pop. | minor | `style.json` `captions.fade_in_wash`: {"color": [255, 190, 200], "frames": 3}, blend in `engine/ext/hud_lyric.py` `hud_row`. |
| m4 | Words per caption | always 2 or 3 | 5.90 DESTROYED (1), 7.87 SINCE 19 JULY 2026 (4), 10.82 DESTROYING (1) | Unchanged. | minor | `engine/captions.py` grid phrase builder, `style.json` `captions.timing.min_words` 2, `max_words` 3. |
| m5 | Heat colour and grain | 8.27 to 8.57: mean (173, 73, 35), saturation 0.77, detail 11 | 9.10 to 9.47, 12.05 to 12.42: (188, 84, 16), saturation 0.93, detail 3 | Hue close now; too saturated (blue channel crushed) and smooth. | minor | `engine/ext/hud_lyric.py` `hud_heat`: CLAHE (2.0, 8x8) on `g` before the LUT, mix 15 % luma back. `style.json` `hud_heat.params.floor` 0.02 to 0.06. |
| m6 | Heat slide and seam | static band | 6.13 to 6.27, 9.12 to 9.18, 12.07 to 12.13 | Band rolls sideways and the caption doubles across a seam (grid 07). | minor | `style.json` `hud_heat.params.slide`: false. |
| m7 | Caption inside heat band | stays red (190 to 198, 33, 11 mix) | 6.37 to 6.44 BEFORE USE near black, 9.2 and 12.2 dark maroon (172, 33, 6 mix) | Caption goes through the LUT. | minor | `style.json` `captions.band_color`: [190, 18, 16]. |
| m8 | Square markers | 7.63 to 8.20 (heat-textured orange squares, about 10 % wide, left side) | 6.15 to 6.27, 6.64 to 6.76, 9.10 to 9.22, 9.59, 12.05, 12.54 (flat red and blue, about 4 %) | Unchanged. | minor | `engine/ext/hud_lyric.py` `hud_marks`: `fill: "heat"`, drop the blue. `style.json`: `size` 90. |
| m9 | Heat timing against cycle | HUD start to heat 1.90 s (3.9 beats) | 3.93 to 6.15 = 2.21 s (4.5 beats) | Unchanged. | minor | `style.json` `hud_heat`, its `hud_marks` and `whoosh`: `offset` 12.5 to 12.0. |
| m10 | DETECTING top bar | 6.37 to 6.93 (sepia footage texture, white text about 2.2 % high) | 3.93 to 4.43 and every bar | Flat #6b5442 fill, text about 1.3 % high. | minor | `engine/ext/hud_lyric.py` `hud_bar`: reuse the wipe texture, text 0.022 x H white heavy. |
| m11 | Readouts | 7.17 to 7.27 (large white labelled floats upper left), 8.37 to 8.50 (top right during heat) | small grey blocks near the caption row, none during heat | Unchanged. | minor | `engine/ext/hud_lyric.py` `hud_bar` readouts 0.025 x H, white, y 0.08 to 0.30; `hud_heat` param `readouts: true`. |
| m12 | X marks | 6.30, 6.63 (about 25 % wide, top right) | 3.96 to 4.30 (about 8 % wide, mid frame) | Size and position. | minor | `style.json` `hud_bar.params.xmark_size` 0.25, positions top right, top centre, left edge. |
| m13 | Card | 6.33 to 6.47 (translucent pale panels) | 5.10 to 5.40, 7.89 to 8.06, 11.0, 13.95 (opaque white) | Unchanged. | minor | `engine/ext/hud_lyric.py` card alpha 0.55, or `style.json` `hud_bar.params.card` false. |
| m14 | Glitch reveal | 1.97 to 2.63 (20 frames, local to the subject, mosaic, cyan-orange fringe) | 0.00 to 0.49 (15 frames, full-width bands and black blocks) | Unchanged (grid 02). | minor | `engine/ext/hud_lyric.py` `hud_glitch`: confine to `focus` box, add mosaic. `style.json` first rule `span_beats` [0, 1.25]. |
| m15 | Glitch at cuts | none | 6.90 to 7.15, 12.80 to 13.05 | Unchanged. | minor | `style.json` `moves`: remove the `hud_glitch` rule with `at: cut`. |
| m16 | Zoom pulse | none | 7.87 to 8.11 | Unchanged. | minor | `style.json` `moves`: remove `zoom_pulse`. |
| m17 | Sound effects | song only | 28 ticks, 8 clicks, whooshes 6.15, 9.10, 12.05, 15.00 (no flash), impact 7.87 | Unchanged. | minor | `style.json`: `captions.caption_sfx` null, remove both `click` rules and `impact`, `whoosh` `when.frac_max` 0.9. |
| m18 | Loudness | -12.6 LUFS | -18.6 LUFS | Unchanged. | minor | `engine/audio.py` final mix `loudnorm=I=-13`. |
| m19 | Grade and white point | clean 2.7 to 6.3: (119, 144, 155), black 4, white 246, saturation 0.31 | 4.0 to 6.1 black 50, white 206, saturation 0.16; 12.85 to 15.6 black 34, white 209 | Whites short, two shots milky and flat, no teal bias. | minor | `style.json` `grade.base`: `white_point` 245, `black_point` 3 (per-shot percentile stretch in `engine/render.py`), `tint` [0.88, 1.0, 1.10]. |
| m20 | First HUD on a cut | 6.37 (over continuous footage) | 3.93 (HUD and cut on the same frame) | Unchanged. | minor | `style.json` `cuts.first_shot_beats` 8 to 10, or `engine/plan.py` keep cuts 1 beat from `hud_bar` starts. |
| m21 | End matte and audio gap | matte 11.73 to 11.83 (3 frames), silence 11.80 to 11.92 (starts under the matte) | matte 15.67 to 15.70 (2 frames), silence 15.50 to 15.65 (ends before the matte) | Matte one frame short, gap 0.17 s early so the music returns on the matte. | minor | `style.json` `overlays` `hud_end_matte.frames` stays 3 but anchor to the last 3 frames in `engine/ext/hud_lyric.py`; `sfx` gap rule: replace `frac` 0.985 with `at: "end"`, `offset_s` -0.07, `dur` 0.12 in `engine/audio.py`. |
| m22 | Ending, held caption | 10.60 to 11.73: last phrase held 1.1 s with a DETECTING top bar and readouts 11.20 to 11.70 | 13.03 to 15.67: held 2.6 s, no HUD after 14.32 | The last 1.35 s are a static caption over footage. | minor | `style.json`: one `hud_bar` with `at: "end"`, `offset_s` -0.55, `dur_beats` 1.0; or lower `structure.outro_beats` 4 to 2. |
| C1 | Caption colour | (189, 16, 16) | (206, 18, 20) | Brighter. | cosmetic | `style.json` `captions.themes[0].color` [190, 17, 16]. |
| C2 | Brackets | none at caption row | 3.96 to 4.43 and every left bar | L brackets frame the caption row. | cosmetic | `style.json` `hud_bar.params.brackets` false. |
| C3 | Node network | 7.27 to 7.40 (upper right) | 4.94 to 5.40, 7.89 to 8.10 (across the middle) | Unchanged. | cosmetic | `engine/ext/hud_lyric.py` network in the upper right quadrant. |
| C4 | Heat first frame | 10.58 (heat already on, no white) | 6.13 (pale wash), 9.08 (near-white band) | Unchanged. | cosmetic | `engine/ext/hud_lyric.py` `hud_heat` white blend 0.75 to 0.25. |
| C5 | Intro length | glitch end 2.63 to first HUD 6.37 = 3.74 s | 0.49 to 3.93 = 3.44 s | Unchanged. | cosmetic | `style.json` `hud.start_beat` and `captions.timing.start_beat` plus 0.5. |
| C7 | Caption face | wide heavy grotesque | Archivo Black | intentional, owner directive | cosmetic | none |
| C8 | Caption depth | middle word behind the person on every phrase | phrases read in front on this object footage | intentional, owner directive (share in front, rest behind; the behind share depends on a person matte) | cosmetic | none |

Out of scope by design: picture content, caption words, matte shapes on objects, the TikTok overlay, 30 fps render against the 60 fps recording.

Matches (no action): 16:9 framing, caption vertical centre (48.8 % against 49.4 %), one red theme with no glow, caption height on most phrases, held last caption to the end, black matte with caption at the end, an audio gap at the end, heat band extent (11.5 to 73 %), heat duration, heat hue now near the reference, bar duration 0.49 s, bar flicker and mark re-placement every 3 frames, upper head wipe band 3 frames, clean intro with no captions.

## Grid files

All in `/Users/student/dev/design-library/edits/hud-lyric-heat/review-round-4/`, reference row above, render row below.

- `01-overview-proportional.png`: 24 pairs over the whole duration (reference time scaled to render time, framegrid.py).
- `02-glitch-reveal-dense.png`: reference 1.83 to 2.57, render 0.00 to 0.73.
- `03-clean-intro.png`: reference 2.60 to 6.40, render 0.60 to 3.90.
- `04-first-hud-cycle.png`: reference 6.30 to 8.14, render 3.90 to 6.18.
- `05-bar-typewriter-dense.png`: reference 6.33 to 6.70, render 3.93 to 4.30, every frame.
- `06-heat-flash-1-dense.png`: reference 8.20 to 8.57, render 6.10 to 6.47, every frame.
- `07-heat-flash-2-dense.png`: reference 10.55 to 10.92, render 9.05 to 9.42, every frame.
- `08-detect-wipe-dense.png`: reference 6.97 to 7.13 and 8.63 to 8.80, render 4.63 to 4.77, 5.37 to 5.47 and 7.60 to 7.67.
- `09-loop-end-outro.png`: reference 11.30 to 11.97 (held caption, black matte, glitch), render 14.30 to 15.70 (held caption, matte).
- `10-caption-typography-crop.png`: caption row crops, reference 7.0, 7.9, 9.2, 9.8, 10.0, 11.4 against render 4.5, 5.5, 7.5, 8.6, 10.2, 14.0.
- `11-caption-onset-dense.png`: reference 6.77 to 6.93 and 7.10 to 7.27, render 4.13 to 4.23, 5.10 to 5.20 and 13.00 to 13.10.
- `12-heat-flash-3-dense.png`: reference 8.20 to 8.57 against render 12.00 to 12.37.
- `13-squares-and-readouts.png`: reference 7.57 to 8.15, render 6.10 to 6.68.
- `14-hud-second-cycle.png`: reference 8.60 to 10.50, render 6.85 to 8.75.
- `ref-crop.mp4`: the cropped reference used for all grids and measurements.

MAJOR: 3, MINOR: 20, COSMETIC: 8. Major differences remain: yes (3).

# hud-lyric-heat, review round 3

Reference: `_source/ScreenRecording_10-11-2026 19-40-58_1.mov`, cropped to the picture (crop=1288:724:0:8, scaled to 1280x720, 30 fps) as `review-round-3/ref-crop.mp4`, 12.6 s. Render: `rounds/round-3.mp4` (1280x720, 30 fps, 15.73 s, 122 BPM). Render event times come from `rounds/round-3.edl.json`.

Alignment for paired grids is unchanged from rounds 1 and 2: reference loop point (black matte 1.83 to 1.90 s) maps to render 0.0 s, reference first HUD 6.37 s to render 3.93 s, reference heat flashes 8.27 and 10.60 s to render 6.15 and 9.10 s.

Measurements behind the table:

- Scene detection (scene > 0.2): reference 25 changes in 12.6 s, none of them cuts. Render 10 changes in 15.7 s (0.03, 3.93, 6.17, 6.90, 9.10, 9.17, 12.07, 12.13, 12.80, 12.83), three of them cuts. Round 2 had 13, the drop is the removed outro heat flash. No HUD bar, wipe or mark registers as a change.
- Caption (red pixel bbox, 10 fps): reference glyph height 9.2 to 9.4 % of frame height on every phrase, centre 49.4 %, span 56 to 89 %, colour (189, 16, 16). Render 9.2 % on most phrases, 10.3 % on EEA, 2024 (comma descender), 8.6 % on SINCE 19 JULY 2026, 8.1 % on 6.94 MILLION TONNES (span cap 0.85 shrinks them), centre 48.8 %, span 33 to 86 %, colour (206, 18, 20).
- Heat band (rows 11.5 to 73 %): reference mean (174 to 181, 73 to 88, 35 to 40), saturation 0.75 to 0.77, 12 to 14 % near black (the subject), horizontal detail 10.5 to 12. Render (209 to 222, 112 to 143, 30 to 45), saturation 0.81 to 0.87, detail 3.8 to 5.9; flash 1 has 39 % near black at 6.25 s (black fill on the fabric pile), flashes 2 and 3 have 6 %.
- Grade of clean footage: reference (121, 145, 156), saturation 0.30, luma 1st and 99th percentile 2 and 246. Render 3.95 to 6.1 s (162, 144, 121), white point 233; 6.95 to 9.0 s white point 231; 12.85 to 15.7 s black point 33, white point 208, saturation 0.14.
- Audio: reference -12.6 LUFS, silences 1.88 to 2.01 and 11.80 to 11.92 s (loop points). Render -18.6 LUFS, no silences. EDL lists 28 caption ticks, 8 clicks, 4 whooshes (one at 15.00 with no heat flash under it) and an impact at 7.87 s.
- Last caption leaves at 14.50 s; 14.53 to 15.73 s is the bare final shot.

## Round 2 findings

| Round 2 ID | Topic | Status | Evidence in round 3 |
|---|---|---|---|
| M1 | Caption size | closed | `fit_up` false: glyph height 9.2 % on most phrases against 9.4 %, no more 14 % short phrases (grid 10). Long phrases still shrink to 8.1 to 8.6 %, now m1. |
| M2 | Heat flash subject fill | partly closed | Fill is gated on `mask_kind == 'person'`, flashes 2 and 3 are clean. Vision labels the fabric pile of shot 2 a person, so flash 1 (6.17 to 6.33) still paints dark maroon blobs over DESTROYED (grids 06, 13). Now M2. |
| M3 | Detect wipe | partly closed | Head band is brown now and holds 3 frames like the reference. It still stops at about two thirds of the width, has no sepia texture, the lower band shows for 1 frame at about 30 % width, and no wipe fires at the HUD start (grid 08). Now m2. |
| M4 | Outro and ending | partly closed | No heat flash or squares in the outro, no repeated filler phrase. The caption now leaves at 14.50 and 1.23 s of bare footage ends the edit, with no matte frame and no audio gap (grid 09). Now M1. |
| M5 | Overlay rhythm | partly closed | Bars hold 0.49 s, inside the reference 0.4 to 0.6 s. Scene changes fell to 10 against 25, readout blocks, card and brackets still hold position through the bar. Now M3. |
| m1 | Caption animation in | open | Hard pop at every onset (grid 11). Now m3. |
| m2 | Words per caption | open | DESTROYED, SINCE 19 JULY 2026, DESTROYING. Now m4. |
| m3 | Heat colour | open (worse) | Mean (210, 113, 30) against (177, 80, 37), more gold than round 2, still smooth. Now m5. |
| m4 | Heat slide and seam | open | Seam at 6.17 to 6.30, 9.12 to 9.18, 12.07 to 12.13. Now m6. |
| m5 | Caption inside heat band | open | BEFORE USE near-black at 6.40 to 6.47, dark red elsewhere; `band_color` still unset. Now m7. |
| m6 | Square markers | open | Flat red and blue, about 4 % wide. Now m8. |
| m7 | Heat timing against cycle | open | Offset 12.5 unchanged. Now m9. |
| m8 | DETECTING top bar | open | Flat fill, text about 1.3 % high. Now m10. |
| m9 | Readouts | open | Now m11. |
| m10 | X marks | open | Now m12. |
| m11 | Card | open | Opaque white card 5.10 to 5.20. Now m13. |
| m12 | Glitch reveal | open | Now m14. |
| m13 | Glitch at cuts | open | 6.90 and 12.80. Now m15. |
| m14 | Zoom pulse | open | 7.87. Now m16. |
| m15 | Sound effects | open | Now m17. |
| m16 | Loudness | open | -18.6 LUFS. Now m18. |
| m17 | Grade | open | Now m19. |
| m18 | First HUD on a cut | open | 3.93. Now m20. |
| C1 to C6 | Colour, brackets, network, heat first frame, intro length, loop audio gap | open | Unchanged. |
| C7, C8 | Face, depth | intentional, owner directive | Unchanged. |

## Current differences

| ID | Category | Reference time (s) | Render time (s) | Description | Severity | Suggested change |
|---|---|---|---|---|---|---|
| M1 | Ending | 11.37 to 11.73 (held caption with top bar), 11.73 to 11.83 (black matte: subject and caption on black), 11.80 to 11.92 (silence), then glitch | 14.53 to 15.73 | The caption leaves at 14.50 and the edit runs 1.23 s of untouched texture with no caption, no HUD, no matte frame and no audio gap. The reference never shows a captionless frame after the first caption and ends on the black matte. | major | `style.json` `captions.timing.fill_tail_beats` 4 to 0 with a new `hold_last: true` (last phrase holds to the end, logic in `engine/captions.py`), `hud.end_matte_frames: 3` with the matte drawn in `engine/ext/hud_lyric.py` next to `end_card` (caption on black when no person matte), `engine/audio.py` 0.12 s gap under it. Optionally one `hud_bar` with `when.frac_min` 0.92. |
| M2 | Heat flash, subject fill | 8.27 to 8.57, 10.60 to 10.93 (only the person is black, caption readable) | 6.17 to 6.33 | The person gate works, but Vision returns a person matte on the fabric pile, so flash 1 fills 39 % of the band dark maroon and erases most of DESTROYED. The blob also changes shape every frame and slides with the band. | major | `engine/ext/hud_lyric.py` `hud_heat`: also require matte area below 0.35 of the band and a face or head hit (Vision face rectangles) before `subject_black`; take the mask from the flash's first frame and hold it. `engine/render.py`: set `mask_kind` to `object` when Vision confidence is low. |
| M3 | Overlay rhythm and scene-change density | 6.37 to 11.83: 25 scene changes, overlays pop 1 to 4 frames and jump | 3.93 to 15.73: 10 scene changes, readout block and brackets fixed for each 0.49 s bar, card 5.10 to 5.40 fixed | Bar length now matches, but the HUD still reads steady. Only the X mark moves. The reference changes something big (bar, band, panel, square) every 3 to 6 frames. | major | `engine/ext/hud_lyric.py` `hud_bar`: re-roll readout block side and the card position every `mark_frames`, card hold 4 frames, blank the bar for 1 frame in 4. `style.json`: add a 1-frame head `hud_wipe` at `offset` 8 and a second `hud_marks` at `offset` 11.5, `size` 90. |
| m1 | Caption size, long phrases | 7.80 to 8.70 BRAND NEW WAGON, 9.63 to 10.50 THE GROCERY SHOP at 9.4 % height, span 87 to 89 % | 7.87 to 9.08 (8.6 %), 12.05 to 12.80 (8.1 %), 12.8 (7.8 %) | Long phrases shrink up to 14 % to stay inside the 0.85 span; the reference allows 89 %. | minor | `style.json` `captions.span` 0.85 to 0.90. |
| m2 | Detect wipe | 8.67 to 8.73, 11.07 to 11.10 (head band, full width, sepia footage, cream cut-out); 7.03 to 7.13 and 7.67 to 7.73 (lower band, about 45 % width, about 13 % high, DETECTING about 2.5 % high, 4 to 5 frames) | 4.67 to 4.73, 7.62, 10.57, 13.52 (head band, ends at about 67 % width, flat brown); 5.40, 8.37, 11.32, 14.27 (lower band, 1 frame, about 30 % wide, 7 % high, label about 1 % high) | Head band count and length now match. The head band does not reach the right edge, has no footage texture, the lower band is too short, small and brief, and no wipe at the HUD start (6.37). | minor | `engine/ext/hud_lyric.py` `hud_wipe`: enter over 1 frame so `cover` is full width from frame 2, texture as `BROWN * (0.35 + 0.6 * g0)`, label 0.025 x H. `style.json` lower-band rule: `dur_beats` 0.3, `band_h` 0.12. |
| m3 | Caption animation in | 6.80 (pale for 1 frame), 7.17 to 7.23 (A CRIB AND A from pale pink over 3 frames) | 4.17, 5.13, 7.13 and every onset | Hard pop. | minor | `style.json` `captions.fade_in_wash`: {"color": [255, 190, 200], "frames": 3}, blend in `engine/ext/hud_lyric.py` `hud_row`. |
| m4 | Words per caption | always 2 or 3 | 5.90 DESTROYED (1), 7.87 SINCE 19 JULY 2026 (4), 10.82 DESTROYING (1) | Unchanged. | minor | `engine/captions.py` grid phrase builder, `style.json` `captions.timing.min_words` 2, `max_words` 3. |
| m5 | Heat colour and grain | 8.27 to 8.57, 10.60 to 10.93: mean (177, 80, 37), saturation 0.76, fine grain (detail 11) | 6.17 to 6.50, 9.10 to 9.47, 12.05 to 12.42: mean (210, 113, 30), saturation 0.87, smooth (detail 4) | Reads orange-gold where the reference is red-orange, and flat on fabric. Worse than round 2. | minor | `style.json` `hud_heat.params`: `range` 0.85 to 0.6, `floor` 0.08 to 0.04. `engine/ext/hud_lyric.py` `hud_heat`: CLAHE (2.0, 8x8) on `g` before the LUT. |
| m6 | Heat slide and seam | static band (one-frame sliver at 8.23) | 6.17 to 6.30, 9.12 to 9.18, 12.07 to 12.13 | Band rolls sideways and the caption doubles across a seam. | minor | `style.json` `hud_heat.params.slide`: false. |
| m7 | Caption inside heat band | stays red (192, 35, 12 mix) | 6.40 to 6.47 BEFORE USE near black, 9.2 and 12.2 dark red (165, 21, 3 mix) | Caption goes through the LUT; the redraw hook needs `band_color`. | minor | `style.json` `captions.band_color`: [190, 18, 16]. |
| m8 | Square markers | 7.63 to 8.20 (heat-textured orange squares, about 10 % wide, left side) | 6.15 to 6.27, 6.64 to 6.76, 9.10, 9.59, 12.05, 12.54 (flat red and blue, about 4 %) | Blue is not in the reference. | minor | `engine/ext/hud_lyric.py` `hud_marks`: `fill: "heat"`, drop the hard-coded blue. `style.json`: `size` 90, `fill` "heat", first rule `offset` 12.0. |
| m9 | Heat timing against cycle | HUD start to heat 1.90 s (3.9 beats) | 3.93 to 6.15 = 2.21 s (4.5 beats) | Unchanged. | minor | `style.json` `hud_heat`, its `hud_marks` and `whoosh`: `offset` 12.5 to 12.0. |
| m10 | DETECTING top bar | 6.37 to 6.93, 7.27 to 7.50 (sepia footage texture, bold white text about 2.2 % high) | 3.97 to 4.43 and every bar | Flat #6b5442 fill and small grey text. | minor | `engine/ext/hud_lyric.py` `hud_bar`: reuse the wipe texture, text 0.022 x H white heavy. |
| m11 | Readouts | 7.17 to 7.27 (large white labelled floats upper left), 8.37 to 8.50 and 10.70 (top right during heat) | small grey hex blocks in the caption row, none during heat | Unchanged. | minor | `engine/ext/hud_lyric.py` `hud_bar` readouts 0.025 x H, white, y 0.08 to 0.30; `hud_heat` param `readouts: true`. |
| m12 | X marks | 6.30, 6.63 (about 25 % wide, top right) | 3.97 to 4.30 (about 8 % wide, caption row and right edge) | Flicker matches, size and position do not. | minor | `style.json` `hud_bar.params.xmark_size` 0.25 (new key in `hud_bar`), positions top right, top centre, left edge. |
| m13 | Card | 6.33 to 6.47 (translucent pale panels) | 5.10 to 5.40, 8.06, 11.0, 13.95 (opaque white, low centre) | Unchanged. | minor | `engine/ext/hud_lyric.py` card alpha 0.55, or `style.json` `hud_bar.params.card` false. |
| m14 | Glitch reveal | 1.97 to 2.63 (20 frames, local to the subject, mosaic, cyan-orange fringe) | 0.00 to 0.49 (15 frames, full-width bands and black blocks) | Unchanged (grid 02). | minor | `engine/ext/hud_lyric.py` `hud_glitch`: confine to `focus` box, add mosaic. `style.json` first rule `span_beats` [0, 1.25]. |
| m15 | Glitch at cuts | none | 6.90 to 7.15, 12.80 to 13.05 | Unchanged. | minor | `style.json` `moves`: remove the `hud_glitch` rule with `at: cut`. |
| m16 | Zoom pulse | none | 7.87 to 8.11 | Unchanged. | minor | `style.json` `moves`: remove `zoom_pulse`. |
| m17 | Sound effects | song only | 28 ticks from 4.18, 8 clicks, whooshes at 6.15, 9.10, 12.05 and 15.00 (no flash at 15.00), impact 7.87 | The whoosh rule kept `frac_max` 1.0 so it now fires over nothing. | minor | `style.json`: `captions.caption_sfx` null, remove both `click` rules and `impact`, `whoosh` `when.frac_max` 0.9 and gain 0.2. |
| m18 | Loudness | -12.6 LUFS | -18.6 LUFS | Unchanged. | minor | `engine/audio.py` final mix `loudnorm=I=-13`. |
| m19 | Grade and white point | clean 2.6 to 6.3: (121, 145, 156), black 2, white 246, saturation 0.30 | 3.95 to 6.1 white 233, 6.95 to 9.0 white 231, 12.85 to 15.7 black 33 and white 208 (milky) | Whites short of the reference, last shot lifted and flat. No teal bias. | minor | `style.json` `grade.base`: `white_point` 245, `black_point` 2 (per-shot percentile stretch in `engine/render.py`), `tint` [0.88, 1.0, 1.10]. |
| m20 | First HUD on a cut | 6.37 (HUD over continuous footage) | 3.93 (HUD start and cut on the same frame) | Unchanged. | minor | `style.json` `cuts.first_shot_beats` 8 to 10, or `engine/plan.py` keep cuts 1 beat from `hud_bar` starts. |
| C1 | Caption colour | (189, 16, 16) | (206, 18, 20) | Brighter. | cosmetic | `style.json` `captions.themes[0].color` [192, 17, 16]. |
| C2 | Brackets | none at caption row | 3.97 to 4.43 and every left bar | L brackets frame the caption row. | cosmetic | `style.json` `hud_bar.params.brackets` false. |
| C3 | Node network | 7.27 to 7.40 (upper right) | 5.10 to 5.40 (across the middle) | Unchanged. | cosmetic | `engine/ext/hud_lyric.py` network in the upper right quadrant. |
| C4 | Heat first frame | 10.58 (heat already on, no white) | 6.15 (grey blob), 9.08 (near-white band) | Unchanged. | cosmetic | `engine/ext/hud_lyric.py` `hud_heat` white blend 0.75 to 0.25. |
| C5 | Intro length | glitch end 2.63 to first HUD 6.37 = 3.74 s | 0.49 to 3.93 = 3.44 s | Unchanged. | cosmetic | `style.json` `hud.start_beat` and `captions.timing.start_beat` plus 0.5. |
| C6 | Audio at loop point | silences 1.88 to 2.01, 11.80 to 11.92 | none | Tied to M1. | cosmetic | `engine/audio.py` 4-frame gap at the end matte. |
| C7 | Caption face | wide heavy grotesque | Archivo Black | intentional, owner directive | cosmetic | none |
| C8 | Caption depth | middle word behind the person on every phrase | all phrases read in front on this object footage | intentional, owner directive (share in front, rest behind; behind share depends on a person matte) | cosmetic | none |

Out of scope by design: picture content, caption words, matte shapes on objects, the TikTok overlay, 30 fps render against the 60 fps recording.

Matches (no action): 16:9 framing, caption vertical centre (48.8 % against 49.4 %), one red theme with no glow, consistent caption size on short and medium phrases, natural word spacing, heat band extent (11.5 to 73 %), heat duration (0.37 s against 0.30 to 0.33 s), no heat flash in the outro, bar duration 0.49 s, head wipe 3 frames, X marks re-placing every 3 frames, clean intro with no captions.

## Grid files

All in `/Users/student/dev/design-library/edits/hud-lyric-heat/review-round-3/`, reference row above, render row below.

- `01-overview-proportional.png`: 24 pairs over the whole duration (reference time scaled to render time).
- `02-glitch-reveal-dense.png`: reference 1.83 to 2.57, render 0.00 to 0.73, every 2 frames.
- `03-clean-intro.png`: reference 2.60 to 6.40, render 0.60 to 3.96.
- `04-first-hud-cycle.png`: reference 6.30 to 8.14, render 3.90 to 6.18.
- `05-bar-typewriter-dense.png`: reference 6.33 to 6.73, render 3.90 to 4.30, every frame.
- `06-heat-flash-1-dense.png`: reference 8.20 to 8.60, render 6.10 to 6.50, every frame.
- `07-heat-flash-2-dense.png`: reference 10.55 to 10.95, render 9.05 to 9.45, every frame.
- `08-detect-wipe-dense.png`: reference 6.97 to 7.13 and 8.63 to 8.80, render 4.63 to 4.77 and 5.37 to 5.57, every frame.
- `09-loop-end-outro.png`: reference 11.30 to 12.00 (held caption, black matte, glitch), render 15.03 to 15.70.
- `10-caption-typography-crop.png`: caption row crops, reference 7.0, 7.9, 9.2, 9.8, 10.0, 11.4 against render 4.5, 5.4, 7.5, 8.6, 9.6, 13.6.
- `11-caption-onset-dense.png`: reference 6.77 to 6.90 and 7.10 to 7.30, render 4.13 to 4.27, 5.10 to 5.20 and 7.10 to 7.17, every frame.
- `12-heat-flash-3-dense.png`: reference 8.20 to 8.57 against render 12.00 to 12.37, every frame.
- `13-squares-and-readouts.png`: reference 7.57 to 8.15, render 6.10 to 6.68.
- `ref-crop.mp4`: the cropped reference used for all grids and measurements.

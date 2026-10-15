MAJOR: 2, MINOR: 17, COSMETIC: 12. Major differences remain: yes (grade brightness, and a new 1.8 s caption blackout at the end).

# lyric-word-beat, review round 4

Reference: `_source/ScreenRecording_10-11-2026 22-33-20_1.MP4`, band cropped to 1290x724 at y 911 and resampled to 30 fps (`review-round-4/ref_band.mp4`, 16.93 s).
Render: `rounds/round-4.mp4` (1280x720, 30 fps, 15.73 s, 122 BPM, 8 shots, 48 words). The brief says 17 s, the file is 15.73 s.
Method: paired frame grids at exact timestamps (reference row above render row), per-frame mean luma (`*.yavg.txt`), ffmpeg scene detection at scene > 0.2 (`*.scenes.txt`), EBU R128 loudness, RMS of the first and last 0.2 s, the round-4 EDL against the round-3 EDL, `style.json` and the engine files changed since the round-3 render.

What changed since round 3: `engine/fx.py` raises the `target_luma` exponent clamp from 2.2 to 3.0, `style.json` `captions.guard` goes from 0.92 to 0.8, and `engine/plan.py` changed so the last phrase (5 words, 14.02 to 15.25 s in round 3) is no longer placed. Cuts, transitions, overlays and every other word time are identical to round 3. `engine/ext/lyric_word_beat.py` and `engine/ext/kinetic.py` are unchanged.

Scene cuts detected. Reference: 1.47, 2.00, 3.70 to 4.10 (haze cluster), 8.40 to 8.67 (radial cluster), 10.27, 12.50, 14.60, 16.43, 16.87. Render: 1.47, 1.97, 2.00, 4.40 to 4.63 (haze cluster), 9.30 to 9.40 (radial), 11.30, 13.77, 15.23, 15.63 (the band wipe at 6.40 is planned and visible but under the detector threshold). Same as round 3.

Mean luma (0 to 255): reference 51.2, render 71.4 (round 3 78.4, round 2 98). Per shot, reference 30, 28, 38, 21, 56, 97, 45, 60, 71, 53. Render 77, 74, 76, 65, 77, 69, 48, 63 (seam shot without the invert frames).
Loudness: reference -13.0 LUFS integrated, render -14.3 LUFS. Seam RMS (mono, 0.2 s): reference tail -10.3 dB into head -15.1 dB, render tail -16.6 dB into head -11.2 dB.

## Round 3 findings

| id | round 3 finding | severity in round 3 | status | evidence in round 4 |
|----|-----------------|---------------------|--------|---------------------|
| N2 | grade 1.5 times too bright | major | partly closed | mean luma 78 to 71, still 1.4 times the reference, see N2 below |
| P27 | difference-blend colour accents gone | minor | open | guard 0.8 still gives pure white or near-black words on every shot, grid 09 (TO, DESTROYED, 19, CLOTHES, (EU), OF), no tinted word anywhere in grid 01 |
| P28 | no caption pause when a graphic lands | minor | open | words run through 11.30 (sticker) and 12.30 (wordmark), grid 06 |
| N4 | mosaic exit strobe | minor | open | 1.97 colour (74), 2.00 one pop (104), then flat 74, grid 02 |
| N5 | dip to black late and lifted | minor | open | frame 1.467 still the incoming shot (luma 75), black 1.50 to 1.60 at 17, card-up black 13.80 to 13.90 at 17 |
| N6 | mosaic tiles are whole-frame copies | minor | open | grid 02, 1.63 to 1.93 |
| N7 | haze flash missing dark card, long fog | minor | open | 4.43 to 4.53 pale haze (161), 4.57 to 4.60 two white frames (229), fog 4.63 to 4.87 (8 frames), grid 03 |
| N8 | band wipe middle band held | minor | open | grid 04 |
| N9 | no plain hard cut | minor | open | same move rotation |
| N10 | wordmark jumps in front at shot end | minor | open | 13.50 to 13.73 KEEP GOING whole and in front of the rack, grid 06 last frame and grid 10 |
| N11 | no silhouette strobe | minor | open | sticker shot luma flat, no white matte frames, grid 06 |
| N12 | seam dip is a ramp | minor | open | 15.27 to 15.50 ramp 70 to 17, back to 77 by 15.60, grid 08 |
| N13 | no carried-over word on frame 0 | minor | open | frame 0 is "4", and now no word at all over the seam, see P32 |
| N14 | shot lengths | minor | open | 3, 6, 4, 6, 4, 5, 3, 1 beats, unchanged |
| N15 | word rate | minor | open, worse | 3.05 words a second (round 3 3.37) |
| N16 | cut vs music arc | minor | open | same plan |
| P29 | card-up held too long, square corners | minor | open | black 13.80 to 13.90, card 13.93 to 14.63, full by 14.83, grid 07 |
| N17 | caption shadow is a halo with no offset | cosmetic | open | unchanged |
| N18 | band wipe flare | cosmetic | open | 6.90 one-frame bloom (93), no streak, grid 04 |
| N19 | radial flash lighter, one white frame | cosmetic | open | 9.33 one white frame (216), grid 05 |
| N20 | invert flash 3 frames, tan | cosmetic | partly closed | 15.63 to 15.70, 3 frames at 173 against 2 frames at 228 |
| N21 | 1280x720 | cosmetic | open | unchanged |
| N22 | duration 15.73 s | cosmetic | open | unchanged |
| N23 | vignette 0.3, light grain | cosmetic | open | unchanged |
| N24 | portrait clip in 16:9 | cosmetic | open | pexels-8453554 at 4.43 to 6.40 |
| P30 | seam audio tail quieter than head | cosmetic | open | tail -16.6 dB, head -11.2 dB |
| P31 | loudness 1.3 LU low | cosmetic | open | -14.3 LUFS |
| N25 | Archivo Black face | cosmetic | intentional, owner directive | unchanged |
| N26 | caption behind foreground objects | cosmetic | intentional, owner directive | unchanged |

Minors closed this round: none.

## Current differences

| id | category | reference time (s) | render time (s) | description | severity | suggested change |
|----|----------|--------------------|-----------------|-------------|----------|------------------|
| P32 (new) | word rate, caption continuity | 12.50 to 16.93, a word on every frame (SHIT, I, IT, AGAIN, BE, MY, MAKE, DIE, 10, THE), caption runs across the card-up, the seam cut, the black and the invert | 13.90 to 15.73, no word at all (1.83 s, 12 percent of the edit), over the whole card-up shot, the seam dip and the invert | Regression from the round-4 `plan.py` change. The "never start a phrase that cannot finish" break in grid timing drops the last phrase, and `fill_tail_beats: 1` shortens the limit further, so the last word (2024, t0 13.28) ends and nothing follows. The core rule of the style, a caption layer that never stops, is broken at the end, and the loop can no longer carry THE into LEVEL. | major | `engine/plan.py` `time_words`: when `fill` is on, start the next phrase and cut it at `limit` instead of breaking, then set the last word's `t1` to `D` (hold to the end). `style.json` `captions.timing.fill_tail_beats` 1 to 0. |
| N2 | grade brightness | whole clip, mean luma 51, night shots 21 to 38, p1 near 0 | whole clip, mean luma 71, every shot 63 to 77 | Still 1.4 times brighter, the low-key night look is missing. `target_luma: 0.24` (61 of 255) is overshot because the exponent is computed from the mean (`log(t)/log(mean)`), and for a spread histogram the mean of `f**k` is above `mean**k`, so bright footage ends above target. Contrast 1.12, grain and the white caption add a little more. | major | `engine/fx.py` `grade_img`: solve the exponent so that the mean of `f**k` equals `target_luma` (bisection, 4 to 6 steps on a 1/8 downscale) instead of the one-shot log ratio. Then set `style.json` `grade.base.target_luma` to 0.2 and aim for a mean of 50 to 55. |
| P33 (new) | grade, shot-to-shot spread | per shot 21 to 97 (night 21 to 38, sunset 97, dusk 60 to 71) | per shot 63 to 77 except card-up 48 | The target pulls every shot to the same brightness, so the dark-to-bright arc between shots (dark gym, bright sunset) is flattened. | minor | `engine/fx.py`: add `target_strength` (0.6) that blends the exponent toward 1 (`k = 1 + s * (k - 1)`), so each shot keeps part of its own level, set it in `grade.base`. |
| P27 | difference-blend colour | 2.5 GRIP sky blue, 6.6 DANCE blue, 7.5 THE blue, 9.0 MUCH olive on pink | every word pure white on dark or near black on light, grids 01 and 09 | Guard 0.8 still removes the colour accent. | minor | `style.json` `captions.guard` 0.8 to 0.5, or in `engine/ext/kinetic.py` scale the guard by `1 - abs(box_luma - 0.5) * 2` so only mid-tone boxes are pushed. |
| P28 | caption pause for a graphic | 10.27 to 10.43, 11.37 to 11.67, 16.43 to 16.57 no word | words continue through 11.30 and 12.30 | The reference blanks the caption 4 to 9 frames when a graphic lands. | minor | `engine/ext/kinetic.py`: skip drawing within `captions.pause_on_graphic` (0.3 s) after the sticker start and after `wordmark_after_beats`. |
| N4 | mosaic exit strobe | 2.00 to 2.10, mosaic and colour alternate (68, 40, 76, 41) | 1.97 colour, 2.00 single pop (104), then flat 74 | One pop instead of a two-pulse strobe. | minor | `lyr_dip_mosaic` in `engine/ext/lyric_word_beat.py`: `strobe_frames: 4` alternating mosaic and colour after `mosaic_end`. |
| N5 | dip to black | 1.467 black (luma 4), card-up black 12.50 to 12.57 at 3 to 5 | 1.467 still the incoming shot (75), black 1.50 to 1.60 at 17, card-up black 13.80 to 13.90 at 17 | Dip one frame late and lifted. | minor | `engine/render.py`: zero the dip window after grade and grain, `lyr_dip_mosaic` black window inclusive of u = 0. |
| N6 | mosaic tiles | 1.53 to 1.97, crops of one grey grainy frame | 1.63 to 1.93, whole-frame miniatures, luma climbs to 74 | Unchanged. | minor | `lyr_dip_mosaic`: per-cell crops, full desaturation, cell gain 0.6, grain 0.05. |
| N7 | haze flash | 3.70 veil, 3.73 to 3.87 dark card, 3.90 one white frame, clean 4.10 | 4.40 veil, 4.43 to 4.53 haze, 4.57 to 4.60 two white frames, fog to 4.87 | Dark card missing, white one frame long, fog three times longer. | minor | `lyr_haze_flash`: `card_scale: 0.5` dark stage, `flash_u` [0.35, 0.40], 2-frame fog. |
| N8 | band wipe | 6.03 to 6.51, middle band moving | 6.40 to 6.87, middle band held | Unchanged. | minor | `lyr_band_wipe`: live outgoing frames instead of `prev_shot_last`. |
| N9 | transition types | 14.60 plain hard cut | none | Unchanged. | minor | One more shot (N14), hard cut at index 7 in `style.json` `moves`. |
| N10 | wordmark depth | wordmark behind the runner throughout | 13.50 to 13.73 KEEP GOING whole and in front | Matte drops out at the end of the shot. | minor | `lyric_sticker` overlay: hold the last good mask when a frame's mask is empty or under half the window median. |
| N11 | silhouette strobe | 10.67 to 10.83, white silhouette on alternate frames | none | No person in the sticker shot. | minor | `engine/plan.py` or `engine/clips.py`: give the `sticker` shot a clip with a person matte, or use the object matte in `lyric_sticker`. |
| N12 | loop seam dip | 16.73 to 16.77 hard black (4), 16.80 to 16.83 dim, 16.87 invert | 15.27 to 15.50 ramp to 17, recovered by 15.60, invert 15.63 | Ramp instead of a held black. | minor | last-shot `dip_black` in `style.json`: `params.shape: "hold"`, `peak` 1.0, end the black on the frame the invert starts. |
| N13 | loop seam words | ends on THE, frame 0 LEVEL then IS | no word at the end, frame 0 "4" | No carried-over word. Depends on P32. | minor | `captions.timing.start_beat: -0.5` and show the last word on frame 0 in `engine/plan.py` grid timing. |
| N14 | shot lengths | 3.4, 3.9, 5.4, 5.5, 4.3, 5.2, 4.9, 4.2, 1.0 beats, nine shots | 3, 6, 4, 6, 4, 5, 3, 1 beats, eight shots | Unchanged. | minor | `cuts.lengths.mid` [[4,3],[5,3]], `drop` [[5,3],[4,2]], `cuts.jitter_beats: 0.5`, bar lock for the first two cuts in `engine/plan.py`. |
| N15 | word rate | 5.1 words a second, gaps 0.133, 0.20, 0.267 s | 3.05 words a second, gaps 0.123 (12), 0.246 (25), 0.369 (5), 0.738 (4), 0.861 (1) | Worse than round 3 because of P32. | minor | `captions.timing.step_beats` [0.5, 0.25, 0.5, 0.25, 0.5, 0.5, 0.25], `phrase_gap_beats` 1.0 to 0.5. |
| N16 | cut vs music arc | drop at 5.45 gets the longest transition, quiet bar gets the sticker | band wipe at 6.40, sticker on a high bar | Unchanged. | minor | `engine/plan.py`: drop cut on the drop beat, sticker on the quietest bar. |
| P29 | card-up timing | 12.50 black 3 frames, card 12.60 to 13.07, full by 13.27 | 13.80 black 4 frames, card 13.93 to 14.63, full by 14.83 | Card held a third longer, square corners. | minor | `lyr_card_up.span_beats` [0, 2.8] to [0, 2.1], `radius: 0.04` in `lyr_card_up`. |
| N17 | caption shadow | soft drop shadow, offset down | halo all round | Unchanged. | cosmetic | `engine/ext/kinetic.py`: offset the halo 2 px down and right. |
| N18 | band wipe flare | 6.56 orange bloom with streak | 6.90 one-frame bloom, no streak | Unchanged. | cosmetic | `lyr_band_wipe`: higher flare gain, horizontal streak kernel. |
| N19 | radial flash | 8.40 to 8.53 heavy streaks, two cream frames | 9.03 to 9.30 light blur, one white frame | Unchanged. | cosmetic | `radial_flash.params.amount` 0.35, `white_u` 0.27. |
| N20 | invert flash | 16.87 to 16.90, 2 frames, luma 228 | 15.63 to 15.70, 3 frames, 173 | Unchanged. | cosmetic | invert `span_beats` to 2 frames ([-0.14, 0]). |
| N21 | resolution | recipe 1920x1080 | 1280x720 | Unchanged. | cosmetic | Render with `--res 1080`. |
| N22 | duration | 16.9 s | 15.73 s | Unchanged. | cosmetic | `structure.end_on_bar`: round up to the next bar when `defaults.duration` is 17. |
| N23 | vignette and texture | no vignette, heavy grain | vignette 0.3, light grain | Unchanged. | cosmetic | `grade.base.vignette: 0`, `grain: 0.03`. |
| N24 | framing | all landscape sources | 4.43 to 6.40 portrait clip cropped | Unchanged. | cosmetic | `engine/clips.py`: penalise portrait clips in a 16:9 edit. |
| P30 | seam audio | tail -10.3 dB into head -15.1 dB | tail -16.6 dB into head -11.2 dB | Loop drops then jumps, the reverse of the reference. | cosmetic | `engine/audio.py` window pick: score tail RMS minus head RMS. |
| P31 | loudness | -13.0 LUFS | -14.3 LUFS | 1.3 LU quieter. | cosmetic | `mix_audio` in `engine/render.py`: normalise to -13 LUFS. |
| N25 | display face | Montserrat ExtraBold look | Archivo Black | Intentional, owner directive. | cosmetic | None. |
| N26 | caption depth | caption always in front | words partly behind foreground objects (for example 2.5 DESTROYED, grid 09) | Intentional, owner directive. | cosmetic | None. |

## Checked with no difference

- One word per swap with a hard swap on a single frame, held to the next word (up to 13.90).
- Caption above transitions: white on the black dips and the mosaic, near black on the haze white and radial white.
- Caption size, cap height about 8 percent of frame height in both.
- Caption jumps to 75 percent for the sticker shot and back to centre on the card-up cut.
- Sticker size and place, wordmark landing about one second into the shot.
- No speed ramps, punch-ins or freeze frames in either. No fade at the seam in either.

## Grid files

All in `/Users/student/dev/design-library/edits/lyric-word-beat/review-round-4/`, reference row above render row in each pair.

- `01-overview-whole-duration.png`: 24 pairs over the whole duration (framegrid.py, time-scaled to each clip's length).
- `02-mosaic-dip.png`: every frame 1.40 to 2.17 in both.
- `03-haze-flash.png`: reference 3.63 to 4.23 against render 4.33 to 4.93, every frame.
- `04-band-wipe.png`: reference 6.00 to 6.70 against render 6.37 to 7.07, every frame.
- `05-radial-flash.png`: reference 8.33 to 8.73 against render 9.03 to 9.43, every frame.
- `06-sticker-moment.png`: reference 10.27 to 12.47 against render 11.30 to 13.50, every third frame.
- `07-card-up.png`: reference 12.47 to 13.73 against render 13.73 to 15.00, every second frame.
- `08-ending-loop-seam.png`: reference 16.37 to 16.90 then frames 0 to 2, render 15.17 to 15.70 then frames 0 to 2.
- `09-caption-closeup.png`: six larger caption pairs (reference 0.3, 2.5, 5.0, 6.6, 7.5, 9.0 against render 0.3, 2.5, 5.0, 7.5, 8.5, 10.0).
- `10-caption-tail.png`: the last third, reference 12.5 to 16.5 against render 13.0 to 15.6, showing the missing words (P32).

Scratch data in the same folder: `ref_band.mp4`, `ref_band.yavg.txt` and `round-4.yavg.txt` (per-frame luma), `ref_band.scenes.txt` and `round-4.scenes.txt`.

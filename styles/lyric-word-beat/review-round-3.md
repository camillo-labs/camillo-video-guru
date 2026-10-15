MAJOR: 1, MINOR: 16, COSMETIC: 12. Major differences remain: yes (grade brightness only).

# lyric-word-beat, review round 3

Reference: `_source/ScreenRecording_10-11-2026 22-33-20_1.MP4`, band cropped to 1290x724 at y 911 and resampled to 30 fps (`review-round-3/ref_band.mp4`, 16.93 s).
Render: `rounds/round-3.mp4` (1280x720, 30 fps, 15.73 s, 122 BPM, 8 shots, 53 words). The brief says 17 s, the file is 15.73 s.
Method: paired frame grids at exact timestamps (reference row above render row), per-frame mean luma (`review-round-3/*.yavg.txt`), ffmpeg scene detection at scene > 0.2 (`*.scenes.txt`), EBU R128 loudness, RMS and sample values at the loop seam, the round-3 EDL, `style.json` and the engine diff since round 2.

What changed since round 2: the EDL differs only in the grade (`gamma 0.8, brightness -0.04` replaced by `target_luma: 0.24`). `engine/ext/kinetic.py` now picks one guard target per word from the mean luma of the word box, draws a dark or light halo (`halo: 0.5`) and moves to `y_alt` while the sticker window is live. Cut times, word times, transitions and overlays are identical to round 2.

Scene cuts detected. Reference: 1.47, 2.00, 3.70 to 4.10 (haze cluster), 8.40 to 8.67 (radial cluster), 10.27, 12.50, 14.60, 16.43, 16.87. Render: 1.47, 1.97, 2.00, 4.40 to 4.63 (haze cluster), 6.40, 9.30 to 9.40 (radial), 11.30, 13.77, 15.23, 15.63.

Mean luma (0 to 255): reference 51.2, render 78.4 (round 2 98, round 1 75 to 155 per shot). Per shot, reference 21 to 101 with night shots 27 to 44, render 46 to 110 with most shots 69 to 82.
Loudness: reference -13.0 LUFS integrated, render -14.3 LUFS.

## Round 2 findings

| id | round 2 finding | severity in round 2 | status | evidence in round 3 |
|----|-----------------|---------------------|--------|---------------------|
| N1 | weak difference-blend contrast, words vanish on woven texture | major | closed | one guard target per word plus halo, every word readable on the woven texture (CLOTHES, FROM, DESTROYING, 2024/1781), on cream (2024, SINCE turn near black) and on the warehouse (4, OF, ON), grids 01, 04, 05, 09. Side effect: colour accents gone, see P27 |
| N2 | grade twice as bright | major | partly closed | mean luma 98 to 78, still 1.5 times the reference, see N2 below |
| N3 | caption over the wordmark in the sticker moment | major | closed | caption jumps to 75 percent at 11.30 and stays there to 13.77, clear of KEEP GOING, grid 06 |
| N4 | mosaic exit strobe | minor | open | luma 60:113 then flat 81, reference 68, 40, 76, 41 |
| N5 | lifted dip black | minor | open | luma 17 at 1.50 to 1.60 and at the card-up black, reference 3 to 5 |
| N6 | mosaic tiles are whole-frame copies | minor | open | grid 02 |
| N7 | haze flash missing dark card, long fog | minor | open | grid 03, fog decays over 8 frames |
| N8 | band wipe middle band is a held frame | minor | open | grid 04 |
| N9 | no plain hard cut | minor | open | same move rotation |
| N10 | wordmark jumps in front at the end of the shot | minor | open | 13.50 to 13.73 KEEP GOING whole and in front, grid 06 |
| N11 | no silhouette strobe | minor | open | clothes-rack shot, luma flat 65 to 72 |
| N12 | seam dip is a ramp | minor | open | 7-frame ramp to luma 18, recovers before the invert |
| N13 | no carried-over word on frame 0 | minor | open | frame 0 is "4" |
| N14 | shot lengths | minor | open | same cuts as round 2 |
| N15 | word rate | minor | open | 3.37 words a second |
| N16 | cut vs music arc | minor | open | same plan |
| N17 | no caption shadow | minor | partly closed | a soft dark halo now sits around light words, similar in effect to the reference shadow, carried as cosmetic |
| N18 | band wipe flare | cosmetic | open | grid 04, 6.90 pink bloom, no streak |
| N19 | radial flash lighter, one white frame | cosmetic | open | grid 05 |
| N20 | invert flash too long, brown | cosmetic | partly closed | invert now reads light (luma 170 against 228) but still 3 frames against 2 |
| N21 | 1280x720 | cosmetic | open | unchanged |
| N22 | duration 15.73 s | cosmetic | open | unchanged |
| N23 | vignette 0.3 | cosmetic | open | `grade.base.vignette` still 0.3 |
| N24 | portrait clip in a 16:9 edit | cosmetic | open | pexels-8453554 (1012x1920) at 4.43 to 6.40 |
| N25 | Archivo Black face | cosmetic | intentional, owner directive | unchanged |
| N26 | caption behind foreground objects | cosmetic | intentional, owner directive | unchanged, still legible |

## Current differences

| id | category | reference time (s) | render time (s) | description | severity | suggested change |
|----|----------|--------------------|-----------------|-------------|----------|------------------|
| N2 | grade brightness | whole clip, mean luma 51, night shots 27 to 44, p1 near 0 | whole clip, mean luma 78, shots 69 to 82, cream cloth shot 4.43 to 6.40 at 110 | Still about 1.5 times brighter than the reference, so the moody low-key look is missing. `target_luma: 0.24` should give about 61, but the exponent in `grade_fx` is clamped to 2.2, so bright shots (mean about 0.6) cannot reach the target, and contrast 1.12 is applied after the target and lifts the mids. | major | `engine/fx.py` line 268: raise the exponent clamp from 2.2 to 3.5 and apply `target_luma` after contrast (or re-measure the mean after contrast and correct). `style.json` `grade.base.target_luma` 0.24 to 0.19 if the clamp stays. Target mean luma 50 to 60. |
| P27 (new) | difference-blend colour | 2.5 GRIP sky blue, 6.6 DANCE blue over the orange flare, 7.5 THE blue, 8.4 MY blue, 8.7 to 9.5 TOO and FOR olive on pink | every word pure white on dark or near black on light (grid 09, 04 at 6.90, 05) | The per-word guard at 0.92 almost removes the difference blend, so the word never picks up the colour accent of the shot. Legibility is right, the coloured accent that defines the style is gone. | minor | `style.json` `captions.guard` 0.92 to 0.55, keep the per-word target and halo for legibility, or in `engine/ext/kinetic.py` scale the guard by how far the box mean luma is from 128 (full guard only for mid-tones). |
| P28 (new) | caption pause for the graphic | 10.27 to 10.43 no word as the sticker lands, 11.37 to 11.67 no word as JUST DO IT lands, 16.43 to 16.57 no word on the seam cut | words continue through 11.30, 12.30 (wordmark landing) and 15.23 | The reference blanks the caption for 4 to 9 frames when a graphic lands so the graphic reads alone. The render never pauses. | minor | `engine/ext/kinetic.py`: skip drawing while `t` is within 0.3 s after the sticker start and after `wordmark_after_beats`, add `captions.pause_on_graphic: 0.3` to `style.json`. |
| N4 | mosaic exit strobe | 2.00 to 2.10, mosaic and colour alternate (luma 68, 40, 76, 41) | 1.97 colour, 2.00 one over-bright frame (113), then flat 81 | One pop instead of the two-pulse mosaic and colour strobe. | minor | `lyr_dip_mosaic` in `engine/ext/lyric_word_beat.py`: add `strobe_frames: 4` that alternates the mosaic frame and the colour frame after `mosaic_end`. |
| N5 | dip to black | 1.467 black on the cut frame (luma 4), card-up black 12.50 to 12.57 at 3 to 5 | 1.467 still shows one frame of the incoming shot (luma 81), black 1.50 to 1.60 at 17, card-up black 13.80 to 13.90 at 17 | The dip starts one frame late and the black is lifted by grain and grade. | minor | `engine/render.py`: clamp the dip window to 0 after the grade and grain, and in `lyr_dip_mosaic` start the black at u = 0 on the cut frame (`black` window inclusive of frame 0). |
| N6 | mosaic tiles | 1.53 to 1.97, crops of one grey grainy frame on mostly black (luma 13 to 37) | 1.63 to 1.97, whole-frame copies, cool, luma climbs to 76 | Unchanged. Cells are miniatures, and the mosaic is twice as bright. | minor | `lyr_dip_mosaic`: each cell samples its own third of the frame, full desaturation, cell gain 0.6, grain 0.05 inside the cells. |
| N7 | haze flash | 3.70 veil, 3.73 to 3.87 dark card, 3.90 one white frame, 4.03 to 4.07 fog, clean 4.10 | 4.40 blur veil, 4.43 to 4.53 pale haze, 4.57 to 4.60 two white frames, 4.63 to 4.86 fog (8 frames), clean 4.87 | Dark card stage missing, white one frame too long, fog tail about three times longer. | minor | `lyr_haze_flash`: add a `card_scale: 0.5` stage with a dark surround between `cut_u` and `flash_u`, `flash_u` [0.35, 0.40], post-flash fog 2 frames. |
| N8 | band wipe | 6.03 to 6.51, middle band is the outgoing shot still moving | 6.40 to 6.87, middle band held | Unchanged. | minor | `lyr_band_wipe`: feed live frames from the outgoing clip instead of `prev_shot_last`. |
| N9 | transition types | 14.60 plain hard cut | none | Unchanged. No plain hard cut between card up and the seam. | minor | Planner needs one more shot (N14), then a hard cut at index 7 in `style.json` `moves`. |
| N10 | wordmark depth | wordmark behind the runner the whole time | 12.30 to 13.47 behind the rack, 13.50 to 13.73 whole and in front | Matte drops out, the wordmark jumps forward. | minor | `lyric_sticker` overlay: hold the last non-empty mask when a frame's mask is empty or much smaller than the window median. |
| N11 | silhouette strobe | 10.67 to 10.83, white person silhouette on alternate frames | none | Sticker shot has no person, so no strobe. | minor | `engine/plan.py` or `engine/clips.py`: give the `sticker` shot a clip with a person matte, or let `lyric_sticker` use the object matte for the silhouette. |
| N12 | loop seam dip | 16.73 to 16.77 hard black (luma 4) 2 frames, 16.80 to 16.83 dim (15), 16.87 invert | 15.30 to 15.47 ramp down over 7 frames to 18, back up 15.50 to 15.57, invert 15.63 | Ramp instead of a hard black, recovers before the invert. | minor | last-shot `dip_black` in `style.json`: `params.shape: "hold"`, `span_beats` [0.6, 0.15], `peak` 1.0, invert starting the frame the black ends. |
| N13 | loop seam words | ends on THE, frame 0 is LEVEL then IS | ends on THE, frame 0 is "4" | No carried-over word at the start. | minor | `captions.timing.start_beat: -0.5` and show the last word on frame 0 in `engine/captions.py` grid timing. |
| N14 | shot lengths | 3.4, 3.9, 5.4, 5.5, 4.3, 5.2, 4.9, 4.2, 1.0 beats, nine shots | 3, 6, 4, 6, 4, 5, 3, 1 beats, eight shots | Unchanged. Two 6-beat shots, one shot fewer, second cut not on a bar. | minor | `cuts.lengths.mid` [[4,3],[5,3]] and `drop` [[5,3],[4,2]], `cuts.jitter_beats: 0.5`, bar lock for the first two cuts in `engine/plan.py`. |
| N15 | word rate | 5.1 words a second, gaps 0.133, 0.20, 0.267 s | 3.37 words a second, gaps 0.123 (13), 0.246 (28), 0.369 (5), 0.738 (5) s | Unchanged. Slower words, five long holds. | minor | `captions.timing.step_beats` [0.5, 0.25, 0.5, 0.25, 0.5, 0.5, 0.25], `phrase_gap_beats` 1.0 to 0.5. |
| N16 | cut vs music arc | drop at 5.45 gets the longest transition, quiet bar 10.64 gets the sticker | band wipe at 6.40, sticker on a high bar | Unchanged. | minor | `engine/plan.py`: drop cut on the drop beat, sticker shot on the quietest bar. |
| P29 (new) | card-up timing | 12.50 black 3 frames, card 12.60 to 13.07 (15 frames), full by 13.27 (0.77 s after the cut) | 13.80 black 4 frames, card 13.93 to 14.50 (22 frames), full by 14.80 (1.03 s) | Card held about a third longer. Corners square against slightly rounded. | minor | `style.json` `lyr_card_up.span_beats` [0, 2.8] to [0, 2.1], and a `radius: 0.04` corner in `lyr_card_up`. |
| N17 | caption shadow | soft dark drop shadow, offset down | dark halo all round the word | Close in effect, no offset. | cosmetic | `engine/ext/kinetic.py`: offset the halo by 2 px down and right. |
| N18 | band wipe flare | 6.56 orange bloom with a horizontal streak | 6.90 to 6.93 pink bloom, no streak | Unchanged. | cosmetic | `lyr_band_wipe`: higher flare gain and a horizontal streak kernel. |
| N19 | radial flash | 8.40 to 8.53 heavy streaks, 8.57 to 8.60 two cream frames, hard cut 8.63 | 9.03 to 9.27 lighter blur, 9.33 one white frame, 9.37 milky incoming | Unchanged. | cosmetic | `radial_flash.params.amount` 0.22 to 0.35, `white_u` 0.18 to 0.27, hard end of the white in `lyr_radial_flash`. |
| N20 | invert flash | 16.87 to 16.90, 2 frames, luma 228 | 15.63 to 15.70, 3 frames, luma 170 | Lighter than round 2, still one frame long and darker. | cosmetic | invert `span_beats` [-0.75, 1.0] to 2 frames ([-0.14, 0]). |
| N21 | resolution | README recipe 1920x1080 | 1280x720 | Unchanged. | cosmetic | Render with `--res 1080`. |
| N22 | duration | 16.9 s | 15.73 s | Unchanged, 1.2 s short. | cosmetic | `structure.end_on_bar`: round up to the next bar when `defaults.duration` is 17. |
| N23 | vignette and texture | no vignette, heavy grain | vignette 0.3, light grain | Unchanged. | cosmetic | `grade.base.vignette: 0`, `grain: 0.03`. |
| N24 | framing | all landscape sources | 4.43 to 6.40 portrait clip cropped to 16:9, soft | Unchanged. | cosmetic | `engine/clips.py`: penalise portrait clips in a 16:9 edit. |
| P30 (new) | seam audio | last 0.2 s RMS -13.3 dB into a first 0.2 s at -18.1 dB, the music rises into the cut | last 0.2 s RMS -19.3 dB into a first 0.2 s at -14.1 dB | Both seams are hot with no fade (fine). The render tail is 5 dB quieter than the head, so the loop drops then jumps, the reverse of the reference. | cosmetic | `engine/audio.py` window pick: prefer an end point on a louder bar than the start (score tail RMS minus head RMS). |
| P31 (new) | loudness | -13.0 LUFS | -14.3 LUFS | 1.3 LU quieter. | cosmetic | `mix_audio` in `engine/render.py`: normalise to -13 LUFS. |
| N25 | display face | Montserrat ExtraBold look | Archivo Black | Intentional, owner directive. | cosmetic | None. |
| N26 | depth layering of the caption | caption always in front | 1.84 EU, 2.46 DESTROYED, 6.5 COMPANIES, 11.6 MARKET, 14.06 to 14.40 SINCE and 19 partly behind objects | Intentional, owner directive. At most one letter hidden, every word readable for its whole hold. | cosmetic | None. |

## Checked with no difference

- One word per swap with a hard cut on a single frame, every hold carries the previous word to the next.
- Caption over transitions: white on the black dips, near black on the haze white (4.57) and the radial white (9.33), as in the reference.
- Caption size: cap height about 8 percent of the frame height in both (grid 09).
- Caption in the sticker moment: jumps to 75 percent for the whole sticker shot and back to centre on the card-up cut.
- Sticker size and place, wordmark landing about one second into the shot (reference 1.10 s, render 1.00 s).
- Audio at the seam: no fade in either.
- No speed ramps, punch-ins or freeze frames in either.

## Grid files

All in `/Users/student/dev/design-library/edits/lyric-word-beat/review-round-3/`, reference row above render row in each pair.

- `01-overview-whole-duration.png`: 24 pairs over the whole duration (framegrid.py, time-scaled to each clip's length).
- `02-mosaic-dip.png`: every frame 1.40 to 2.17 in both.
- `03-haze-flash.png`: reference 3.63 to 4.23 against render 4.33 to 4.93, every frame.
- `04-band-wipe.png`: reference 6.00 to 6.70 against render 6.37 to 7.07, every frame.
- `05-radial-flash.png`: reference 8.33 to 8.73 against render 9.03 to 9.43, every frame.
- `06-sticker-moment.png`: reference 10.27 to 12.47 against render 11.30 to 13.60, every third frame.
- `07-card-up.png`: reference 12.47 to 13.73 against render 13.73 to 15.00, every second frame.
- `08-ending-loop-seam.png`: reference 16.37 to 16.90 then frames 0 to 2, render 15.17 to 15.70 then frames 0 to 2.
- `09-caption-closeup.png`: six larger caption pairs (reference 0.3, 2.5, 5.0, 7.5, 9.5, 13.5 against render 0.3, 2.5, 5.0, 7.5, 10.0, 12.2).

Scratch data in the same folder: `ref_band.mp4`, `ref_band.yavg.txt` and `round-3.yavg.txt` (per-frame luma), `ref_band.scenes.txt` and `round-3.scenes.txt`.

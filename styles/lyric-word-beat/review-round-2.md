MAJOR: 3, MINOR: 14, COSMETIC: 9. Major differences remain: yes.

# lyric-word-beat, review round 2

Reference: `_source/ScreenRecording_10-11-2026 22-33-20_1.MP4`, band cropped to 1290x724 at y 911 and resampled to 30 fps (`review-round-2/ref_band.mp4`, 16.93 s).
Render: `rounds/round-2.mp4` (1280x720, 30 fps, 15.73 s, 122 BPM, 8 shots, 53 words).
Method: paired frame grids (reference above, render below), per-frame mean luma (`review-round-2/*.yavg.txt`), ffmpeg scene detection at scene > 0.2 (`*.scenes.txt`), RMS and peak level at the seam, EBU R128 loudness, the round-2 EDL and `style.json`.

Scene cuts detected. Reference: 1.47, 2.00, 3.70 to 4.10 (haze cluster), 8.40 to 8.67 (radial cluster), 10.27, 12.50, 14.60, 16.43, 16.87. Render: 1.47, 1.50, 1.97, 4.40 to 4.63 (haze cluster), 6.40, 6.90 to 6.93 (band wipe flare), 9.30 to 9.40 (radial), 11.30, 13.77 to 13.80, 15.23, 15.63.

Mean luma (0 to 255): reference 51, render 98 (round 1 render was higher still, 75 to 155 per shot, now 60 to 130).
Loudness: reference -13.0 LUFS integrated, render -14.3 LUFS.

Note on the caption kind: `captions.kind` is still `kinetic` (engine/ext/kinetic.py), now configured as one word, `anim: none`, `hold_until_next`, size 0.096 and `plate: diff`. That closes the round 1 timing, chunking, fade and size findings. Kinetic has no `y_alt`, no shadow and a per-pixel guard, which is the source of the three remaining caption findings (N1, N3, N17).

## Round 1 majors

| id | round 1 finding | status | evidence |
|----|-----------------|--------|----------|
| D1 | captions ran out at 8.85 s | closed | words fill to 15.25 and the last word holds over the seam (`timing.fill`), grid 01 and 08 |
| D2 | blank caption between phrases | closed | phrase gaps 3.32 to 3.81, 4.18 to 4.67, 7.75 to 8.24, 8.85 to 9.34, 12.66 to 13.16 and 13.52 to 14.02 all hold the previous word (`hold_until_next`), grids 03, 05, 06, 07 |
| D3 | words faded in and out | closed | `anim: none`, every swap is a single-frame hard cut, grids 02 and 04 |
| D4 | two-word stacked chunks | closed | `chunk_sizes: [1]`, one word on every frame |
| D5 | Anton condensed face | closed (intentional, owner directive) | Archivo Black, a wide heavy grotesque, close to the reference weight and width |
| D6 | text twice the reference size | closed | cap height about 7.8 percent of height against 8 percent in the reference, grid 09 |
| D7 | caption occluded by foreground | closed as a difference (intentional, owner directive), see N26 for legibility | depth matte still active by design |
| D8 | weak difference-blend contrast on bright footage | open | see N1 |
| D9 | footage two to five times brighter | partly closed | mean luma 98 against 51 (round 1 about 75 to 155), see N2 |
| D10 | card-up transition missing | closed | card up at 13.77 to 14.80, grid 07 |
| D11 | standalone strobe-pop cut | closed | no strobe-pop move in `moves`, no pulse train in the luma trace |
| D25 | music faded out at the seam | closed | `mix_audio(tail_fade=False)` for loop styles, peaks stay at -2.7 to -13 dBFS to the last frame, last 0.2 s RMS -17 to -21 dB against -13.8 dB at frame 0 (music, not a fade) |

Other round 1 items: D20 (sticker shot too short) closed, 5 beats and a 1.48 s wordmark. D31 (tracking) closed. D13 partly closed (timing fixed, black still lifted). D21 partly closed. D12, D14, D15, D16, D17, D18, D19, D22, D23, D24, D26 to D30, D32 to D36 open, carried below.

## Current differences

| id | category | reference time (s) | render time (s) | description | severity | suggested change |
|----|----------|--------------------|-----------------|-------------|----------|------------------|
| N1 (D8) | difference blend, contrast, legibility | 0 to 16.9, white on dark, sky blue on orange (6.6), olive on pink (8.7), black on the white flash (3.90) | 0.0 to 1.4 (grey on white rolls), 1.63 to 1.97 (EU over mosaic), 4.7 to 6.4 (grey on cream), 6.6 to 9.3 (woven texture: FROM, DESTROYING, CLOTHES, 2024/1781 near invisible), 9.4 to 11.3 (4, OF, TEXTILES over the warehouse) | The reference word reads as near white with a colour accent almost everywhere. The render word is mid grey on bright or mid-tone footage, and on the woven texture the per-pixel guard flips between near-black and near-white inside the letters, so the word takes on the texture and disappears for about 2.7 s. | major | `engine/ext/kinetic.py` diff plate: pick the guard target from the mean luma inside the word box (one target per word, not per pixel), and add an automatic 30 percent dark scrim or the shadow when the box mean luma is above about 0.45. Also lower the picture first (N2). Alternatively `captions.kind: "lyric_diff"`, which has the shadow and `y_alt`. |
| N2 (D9) | grade brightness | mean luma 51, shots 16 to 98, p1 near 0 | mean luma 98, shots 60 to 130 (0.0 to 4.4 at 102 to 107, 4.8 to 6.4 at 129, 7.0 to 9.3 at 112) | Still about twice as bright as the reference. Gamma 0.8 and brightness -0.04 took the top off, but the moody low-key look is not there, and the bright picture is why N1 happens. | major | `style.json` `grade.base`: `gamma` 0.8 to 0.65 (or `exposure: -0.35` if the grade supports it), `brightness` -0.04 to -0.10, keep `contrast` 1.12. Target mean luma 50 to 70. |
| N3 (D22) | caption placement in the sticker moment | 10.27 to 12.50, caption jumps to 75 percent height, sits clear below the wordmark | 11.30 to 13.77, caption stays at 50 percent, from 12.29 it sits on top of the KEEP GOING wordmark (USE, EEA, 2024 overprint the wordmark letters) | Caption and wordmark collide for 1.5 s and both become hard to read. Kinetic does not read `y_alt` or the sticker window. | major | `engine/ext/kinetic.py`: when `ctx` has a live `sticker` mask_flash window, use `cfg['y_alt']`, and add `captions.y_alt: 0.75` to `style.json` (lyric_diff already does this). |
| N4 (D12) | mosaic exit strobe | 2.00 to 2.10, mosaic and colour alternate (luma 67, 39, 76, 40) | 1.97 colour, 2.00 one over-bright colour frame (luma 153), 2.03 colour | One pop instead of the two-pulse mosaic/colour strobe. Frame strip 10 shows mosaic, mosaic, colour, bright colour, colour. | minor | `lyr_dip_mosaic` in `engine/ext/lyric_word_beat.py`: add `strobe_frames: 3` that alternates the mosaic frame and the colour frame after `mosaic_end`. |
| N5 (D13) | dip to black | 1.47 to 1.50 true black (luma 3) | 1.50 to 1.60 lifted black (luma 16 to 17) | Timing now on the cut frame (closed). Black is still lifted by grade grain and gamma after the dip. | minor | `engine/render.py`: apply the grade before pre-layer transitions, or clamp the dip window to 0 after the grade. |
| N6 (D14) | mosaic tiles | 1.53 to 1.97, crops of one grey grainy frame | 1.63 to 1.97, whole-frame copies, cool blue grey | Unchanged since round 1. | minor | `lyr_dip_mosaic`: each cell samples its own third of the frame, full desaturation, grain 0.05 inside the cells. |
| N7 (D15) | haze flash | 3.70 veil, 3.73 to 3.87 50 percent dark card, 3.90 white, 4.03 to 4.07 fog, clean 4.10 | 4.40 blur veil, 4.43 to 4.53 pale haze, 4.57 to 4.60 white, 4.63 to 4.83 fog and blurred incoming (7 frames), clean 4.86 | Dark card stage still missing, fog tail about three times longer. | minor | `lyr_haze_flash`: add a `card_scale: 0.5` stage with a dark surround between `cut_u` and `flash_u`, and shorten the post-flash fog to 2 frames. |
| N8 (D16) | band wipe | 6.03 to 6.51, middle band is the outgoing shot still moving | 6.40 to 6.87, middle band held (frame-to-frame change 0.5 to 1.4 against 2 to 2.5 before the cut) | Outgoing band still a held frame. | minor | `lyr_band_wipe`: feed live frames from the outgoing clip (extend its source by the span) instead of `prev_shot_last`. |
| N9 (D19) | transition types | 14.60 plain hard cut | none | The rotation fills indices 1 to 6 and index 7 is the seam, so no plain hard cut appears. The reference has one between card up and the seam. | minor | Give the planner one more shot (see N13) or move the hard cut to index 6 and card up to index 5 sharing with the sticker shot, in `style.json` `moves` index offsets. |
| N10 (D21) | wordmark depth | wordmark behind the runner the whole time | 12.29 to 13.50 behind the clothes rack, 13.61 to 13.77 fully in front | Matte drops out near the end of the shot, the wordmark jumps forward. | minor | `lyric_sticker` overlay: hold the last non-empty mask when a frame's mask is empty or much smaller than the window median. |
| N11 (new) | silhouette strobe | 10.67 to 10.83, white person silhouette on alternate frames, three flashes | none (luma flat at 60 to 62 over 11.30 to 12.30) | The sticker shot is a clothes rack with no person, so the silhouette strobe never fires. Round 1 showed it. | minor | `engine/plan.py` or `engine/clips.py`: for the shot carrying the `sticker` tag, prefer a clip with a person or object matte, or have `lyric_sticker` fall back to the object matte for the silhouette. |
| N12 (D23) | loop seam dip | 16.43 full, 16.73 to 16.80 hard black for 2 frames, then invert | 15.27 to 15.47 ramp down over 7 frames, one black frame 15.47, ramp up 15.50 to 15.57, invert 15.60 | Dip is a ramp and recovers to the picture before the invert. Reference is a hard 2-frame black straight into the invert. | minor | `style.json` last-shot `dip_black`: add `params.shape: "hold"`, `span_beats` [0.6, 0.15], and start the invert on the frame the black ends. |
| N13 (D26) | loop seam words | ends on THE, frame 0 is LEVEL then IS, so the loop reads THE LEVEL IS | ends on THE, frame 0 is "4", the first word of the phrase | No carried-over word at the start. | minor | `captions.timing.start_beat: -0.5` and show the last caption word on frame 0, in `engine/captions.py` grid timing. |
| N14 (D27, D36) | shot lengths | 3.4, 3.9, 5.4, 5.5, 4.3, 5.2, 4.9, 4.2, 1.0 beats, nine shots, first two cuts on downbeats | 3, 6, 4, 6, 4, 5, 3, 1 beats, eight shots, second cut on beat 9 (4.43) | Identical to round 1. Two 6-beat shots, one shot fewer than the reference, the second cut misses the bar. | minor | `cuts.lengths.mid` [[4,3],[5,3]] and `drop` [[5,3],[4,2]] (drop the 6), `cuts.jitter_beats: 0.5`, and a bar lock for the first two cuts in `engine/plan.py`. |
| N15 (D28) | word rate | 5.1 words a second, gaps 0.133, 0.20, 0.267 s | 3.4 words a second, gaps 0.123, 0.246, 0.369 s | Words change slower with longer holds. | minor | `captions.timing.step_beats` [0.5, 0.25, 0.5, 0.25, 0.5, 0.5, 0.25] at 122 BPM, or a step in seconds (0.2 s mean) in `engine/captions.py`. |
| N16 (D29) | cut vs music arc | drop at 5.45 gets the longest transition, lull bar 10.64 gets the sticker | drop at 5.90, band wipe lands at 6.40 (one beat late), sticker on a `high` bar | Unchanged. | minor | `engine/plan.py`: place the drop cut on the drop beat and the sticker shot on the quietest bar, `engine/audio.py` window pick scoring loudness range. |
| N17 (D30) | caption shadow | soft dark drop shadow under every word | none | Kinetic draws no shadow. The shadow is what keeps the reference word readable on its few bright frames. | minor | `engine/ext/kinetic.py`: draw `cfg['shadow']` (offset 2, blur 3, 35 percent black) under the diff text, and add `captions.shadow: [2, 2, 3, 0.35]`. |
| N18 (D17) | band wipe flare | 6.56 orange bloom with a horizontal streak | 6.90 to 6.93 pink bloom, no streak | Unchanged. | cosmetic | `lyr_band_wipe`: higher flare gain and a horizontal streak kernel. |
| N19 (D18) | radial flash | 8.40 to 8.53 heavy streaks, 8.57 to 8.60 cream white, hard cut 8.63 | 9.03 to 9.30 lighter blur, 9.33 one white frame, 9.36 to 9.40 milky blurred incoming | Blur lighter, one white frame instead of two, incoming fades from haze. | cosmetic | `radial_flash.params.amount` 0.22 to 0.35, `white_u` 0.18 to 0.27, and a hard end of the white in `lyr_radial_flash`. |
| N20 (D24) | invert flash | 16.84 to 16.87, 2 frames, reads near white | 15.63 to 15.70, 3 frames, reads brown and pink | Longer, colour follows the bright footage. | cosmetic | Invert `span_beats` to 2 frames. Colour follows N2. |
| N21 (D32) | resolution | 16:9 band, README recipe 1920x1080 crf 18 | 1280x720 | Aspect matches. | cosmetic | Render with `--res 1080`. |
| N22 (D33) | duration | 16.9 s | 15.73 s | Unchanged, about 1.2 s short. | cosmetic | `structure.end_on_bar`: round up to the next bar instead of down when `defaults.duration` is 17. |
| N23 (D34) | texture and vignette | heavy compression grain, soft, no vignette | `vignette: 0.3` (raised from 0.15), visible dark corners, light grain | The vignette grew instead of going to 0. | cosmetic | `grade.base.vignette: 0`, `grain: 0.03`. |
| N24 (D35) | framing | all sources landscape | 4.43 to 6.40 portrait clip (1012x1920) cropped to 16:9, soft | Unchanged. | cosmetic | `engine/clips.py`: penalise portrait clips in a 16:9 edit. |
| N25 (new) | display face | Montserrat ExtraBold look | Archivo Black | Intentional, owner directive. Legible at every size seen. | cosmetic | None. |
| N26 (new) | depth layering of the caption | caption always in front | 1.84 EU, 2.46 DESTROYED, 6.5 COMPANIES, 11.30 EU, 11.6 MARKET, 12.2 BEFORE, 14.06 to 14.40 SINCE and 19 behind the denim roll | Intentional, owner directive. Legibility check: at most one letter is hidden per word (SIN E, BEF RE, MAR ET) and every word stays readable for its full hold, so timing is unaffected. The only failures in these windows come from contrast (N1), not the matte. | cosmetic | None. If wanted, `depth_text.min_visible` 0.7 to 0.8 so a word with more than one letter covered moves in front. |

## Checked with no difference

- One word per swap with a hard cut: yes, every swap is a single frame.
- Hold between phrases: every gap holds the previous word, as in the reference.
- Caption over transitions: the word stays on the black dip (white), the haze white flash (near black, 4.57 to 4.60, same as the reference 3.90) and the radial white (near black, 9.33).
- Card up: black, slide up with slight tilt, hold as a card, scale to full (13.77 to 14.80 against 12.50 to 13.75). Corners are square where the reference rounds them slightly, too small to list.
- Sticker size and place: red tick upper left at about a quarter of the width, in front of the subject. Sticker shot 5 beats.
- Audio at the seam: no fade, the cut is hot as in the reference.
- Speed ramps, punch-ins, freeze frames, added sound effects: none in either.

## Grid files

All in `/Users/student/dev/design-library/edits/lyric-word-beat/review-round-2/`, reference row above render row in each pair.

- `01-overview-whole-duration.png`: 24 evenly spaced pairs over the whole duration (time-scaled).
- `02-mosaic-dip.png`: every frame 1.40 to 2.17 in both.
- `03-haze-flash.png`: reference 3.63 to 4.20 against render 4.33 to 4.93, every frame.
- `04-band-wipe.png`: reference 6.00 to 6.70 against render 6.37 to 7.07, every frame.
- `05-radial-flash.png`: reference 8.33 to 8.73 against render 9.03 to 9.50, every frame.
- `06-sticker-moment.png`: reference 10.27 to 12.47 against render 11.30 to 13.72.
- `07-card-up.png`: reference 12.47 to 13.80 against render 13.73 to 15.17, every second frame.
- `08-ending-loop-seam.png`: reference 16.37 to 16.90 then 0.00, render 15.17 to 15.72 then 0.00.
- `09-caption-closeup.png`: six larger caption pairs (reference 0.3, 2.5, 5.0, 7.5, 9.5, 13.5 against render 0.3, 2.5, 5.0, 7.5, 10.0, 12.2).
- `10-mosaic-exit-frames.png`: render only, frames 57 to 62 (1.90 to 2.07), for N4.

Scratch data in the same folder: `ref_band.mp4`, `ref_band.yavg.txt` and `round-2.yavg.txt` (per-frame luma), `ref_band.scenes.txt` and `round-2.scenes.txt`.

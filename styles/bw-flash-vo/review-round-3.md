MAJOR: 0, MINOR: 20, COSMETIC: 11. No major differences remain. The two round 2 majors that were not closed are now minor.

# bw-flash-vo, round 3 review

Reference: `_source/v24044gl0000dagu96vog65oq9i5qe0g.MP4`, band cropped to 548x308 at x14 y97, 0 to 16.3 s (`review-round-3/scratch/ref_band.mp4`).
Render: `rounds/round-3.mp4`, 720x1280, 15.74 s, seed 4, 122 BPM (beat 0.492 s), 55 shots. The shot plan and effect events match round 2 frame for frame. What changed is the per-shot `grade.target_luma` normaliser (engine/fx.py line 266) and a shorter voiceover (2.95 to 7.75 s, one sentence, 14 Whisper words).

Owner directive applies: caption face, scale, layout, accent colour, scrim and depth layering are recorded as cosmetic, "intentional, owner directive". Legibility and timing of that treatment are judged on their own rows.

## Measurements

| Measure | Reference band | Round 2 | Round 3 |
| --- | --- | --- | --- |
| Scene changes (ffmpeg scene > 0.2, incl. flash frames) | 73 in 16.3 s | 82 in 15.7 s | 88 in 15.74 s |
| Intro cut rate | about 5 per s (0 to 2.2 s) | 4.4 per s | 4.4 per s (unchanged plan) |
| Montage | 9.3 to 12.9 s, about 4.9 per s | 7.87 to 11.8 s, 5.6 per s | same |
| Close | 12.9 to 15.5 s, about 3.4 per s, 5 white flashes | 2.5 per s, 0 flashes | same |
| Frames with mean luma > 200 | 34 | 11 | 11 (0.60, 1.10, 1.83, 2.33, 7.90, 8.23, 8.50, 9.10, 9.70, 10.83, 11.43) |
| Mean luma, whole edit | 83 | 108 | 95 |
| Mean luma, opening B&W / colour / closing B&W | 76 / 90 / 72 | 96 / 112 / 118 | 86 / 103 / 86 (montage 7.87 to 11.8 s alone 113) |
| Mean YHIGH / YLOW | 143 / 44 | 162 / 54 | 153 / 43 |
| Per-shot median luma against target | n/a | n/a | B&W shots 54 to 120 against 76, colour shots 78 to 168 against 92 (the 167 and 168 shots are whole-shot inverts) |
| Colour arrives / leaves | one switch at 4.9 s / about 13.4 s | stepped 4.43 to 5.4 s / 13.27 to 14.0 s | same |
| Integrated loudness / true peak | -15.0 LUFS / -4.4 dB | -21.5 LUFS / -1.3 dB | -20.5 LUFS / -1.2 dB |
| Intro audio gaps (50 ms RMS) | 5 gaps of 0.15 to 0.25 s, floor -36 to -54 dB | 1 gap | 7 gaps of about 0.1 s at 0.25, 0.75, 1.1, 1.85, 2.0, 2.2, 2.35 s, floor -82 to -120 dB (digital silence) |
| Dips before montage hits | 9.65 to 9.8 s, 12.15 to 12.35 s, 14.6 s | none | none |
| Voiceover | 3.1 to 8.2 s (31 to 50 per cent) | 2.95 to 14.37 s (19 to 91 per cent) | 2.95 to 7.75 s (19 to 49 per cent), captions end at 8.23 s |
| Masking flash on the final shot | luma 68 to 109 at 15.90 s, full silhouette | rise 4 | rise 7 at 15.33 and 15.50 s, small white patches on the cloth pile |
| End of audio | full level to 16.3 s | n/a | fades from -16 to -38 dB over 15.4 to 15.7 s |
| Cut offset from 122 BPM sixteenth grid (check.json) | not beat locked | 13.5 ms | 19.9 ms mean, 86.5 per cent within one frame (planned 7.9 ms) |

## Status of round 2 findings

| id | round 2 issue | round 2 severity | status | evidence |
| --- | --- | --- | --- | --- |
| R1 | caption layout | cosmetic | owner directive, unchanged | |
| R2 | caption face and scale | cosmetic | owner directive, unchanged | DESTROYED at 6.6 s still runs to about 8 per cent from the right edge |
| R3 | caption placement low in the platform UI band | cosmetic | open | block bottom still at y 0.84 to 0.88 |
| R4 | accent colour | cosmetic | owner directive, unchanged | |
| R5 | scrim | cosmetic | owner directive, unchanged | |
| R6 | depth layering | cosmetic | owner directive, unchanged | |
| R7 | captions and voiceover run through montage and close | major | closed | VO 2.95 to 7.75 s, montage and close textless; residual 0.36 s tail into the drop logged as N1 |
| R8 | "4-9%" tokenised as "4 / -9 / %" | minor | open | 3.0 to 4.2 s reads "4 -9" then "% OF" (grid 05, 10) |
| R9 | depth matte slices letters, behind words fade | minor | open | TEXTILES at 4.25 to 4.3 s reads "T XTILES" with the E cut out by the pile matte (grid 05, 12) |
| R10 | effects hit the captions | minor | open | 3.42 to 3.71 s zoom blur smears "4 -9", 7.87 to 8.1 s flash and RGB split wash out BEFORE USE. (grid 07, 11) |
| R11 | no pre-voiceover hold, VO enters mid-shot | minor | open | VO at 2.95 s inside the 2.7 to 3.2 s hanger shot |
| R12 | no white open, no flash in the VO stretch | minor | open | nothing white from 2.46 to 7.87 s; first frame is a normal picture (ref opens on a high-key negative eye) |
| R13 | drop at 50 per cent with no blur build | minor | open | drop 7.87 s on flash + RGB split + shake, ref build 8.2 to 9.3 s |
| R14 | thin montage flashes | minor | open | 7 near-white frames in the montage against about 20 |
| R15 | close slow and flash-free | minor | open | no white frame after 11.43 s |
| R16 | grade too bright, closing B&W brightest | major | partly closed, now minor | whole edit 108 to 95 against 83; closing B&W 118 to 86 against 72; section order is now right (colour brightest) |
| R17 | staged colour turn, return late | minor | open | same four-step and three-step ramps |
| R18 | no teal and orange push | cosmetic | open | |
| R19 | no tile events | minor | open | |
| R20 | x-ray overlay | cosmetic | open, known gap | |
| R21 | no whip smear or speed ramp | minor | open | every shot speed 1.0 |
| R22 | intro gaps filled, no pre-hit dips | major | partly closed, now minor | 7 intro gaps now audible, but each about 0.1 s and dead silent; pre-hit dips still missing |
| R23 | loudness -21.5 LUFS | minor | open (slightly better) | -20.5 LUFS |
| R24 | riser not heard | minor | open | 4 kHz high band rises 6.5 to 7.2 s then falls 6 dB before 7.87 s, no continuous build |
| R25 | masking flash invisible | minor | partly closed | faint white patches on the pile at 15.33 s, luma rise 7 against 41 in the reference |
| R26 | final shot shorter than the one before | minor | open | 1 s hold at 14.0 s, final shot 0.5 s |
| R27 | duration 15.73 s | cosmetic | open | 15.74 s |
| R28 | near-black reframes | cosmetic | partly closed | hanger shot 2.7 to 3.2 s now luma 54 (was about 30) |

## Current differences

| id | category | reference time | render time | description | severity | suggested change |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | caption layout | 3.1 to 8.2 s staircase | 2.95 to 8.23 s, 1 to 3 word chunks | Chunks replace each other. | cosmetic | Intentional, owner directive. |
| R2 | caption face and scale | small bold sans, accent 1.5x | Anton, `size_frac 0.115`, key 1.8x | Different face and scale, legible. | cosmetic | Intentional, owner directive. Optional width cap 0.86 in engine/captions.py. |
| R3 | caption placement | upper middle | lower left, bottom at y 0.84 to 0.88 | Bottom line sits in the band that TikTok and Reels cover. | cosmetic | Intentional, owner directive. Consider `captions.y: 0.78`. |
| R4 | caption accent colour | dark red, cyan | gold (230,200,138) | Different accent. | cosmetic | Intentional, owner directive. |
| R5 | caption scrim | none | subtle dark band | Reads as intended. | cosmetic | Intentional, owner directive. |
| R6 | depth layering | none | words alternate behind and in front | Different layering. | cosmetic | Intentional, owner directive. |
| R8 | caption legibility, tokens | n/a | 3.0 to 4.2 s | "4 / -9" then "% / OF": the opening number is unreadable. | minor | engine/make_edit.py: merge pass after `whisper_words` joining tokens that start with "-", "%", ",", "." onto the previous token. |
| R9 | caption legibility, matte | n/a | 4.25 to 4.33 s TEXTILES | Matte cuts the E out of the key word on a subject-less pile. | minor | engine/captions.py depth pass: never put the key word behind; skip behind pass when mask coverage is under 8 per cent or word overlap under 30 per cent; `depth_text.min_visible: 0.8`. |
| R10 | caption layering under effects | text never blurred | 3.42 to 3.71 s zoom blur, 7.87 to 8.1 s flash and RGB split on text | Captions are composited before the post layer (engine/render.py lines 321 to 357). | minor | engine/render.py: composite captions after the post-layer loop, or `captions.layer: "top"`. |
| R11 | pre-voiceover hold | 2.17 to 3.13 s one held shot, VO on the cut | VO at 2.95 s mid-shot | No breath before the first word. | minor | `structure.pre_vo_hold_beats: 2` in engine/plan.py, cut on the first word. |
| R12 | flashes before the drop | white at 0.0, 0.2, 1.5 to 1.63, 4.3 s; inverted frame 7.27 to 7.4 s | nothing from 2.46 to 7.87 s; normal first frame | VO stretch unpunctuated, no white or negative open. | minor | style.json moves: `flash` at `phrase` with `max: 1`; `invert` at `drop` with `span_beats: [-1,-0.75]`; `cuts.first_flash: true` in engine/plan.py. |
| R13 | drop position and build | blur build 8.2 to 9.3 s, montage on white at 9.3 s (57 per cent) | drop at 7.87 s (50 per cent), flash + split + shake at once | No build into the montage. | minor | `structure.drop_at: 0.57`; `zoom_blur` at `drop` with `span_beats: [-2,0]`, amount ramp 0.05 to 0.3; drop `rgb_split` and `shake` to 0.008. |
| R14 | montage flash density | about 20 near-white frames 9.3 to 12.7 s, six-frame burst at 12.0 s | 7 frames 7.87 to 11.8 s, each one frame | Thinner, never holds. | minor | flash on `high`/`drop`: `p: 0.55`, `span_beats: [0,0.35]`, `params.hold_frames: 1` (engine/fx.py); one 0.5 beat flash near the montage end. |
| R15 | close rhythm and flashes | 12.9 to 15.5 s, 0.2 to 0.5 s cuts, white at 13.4, 13.9, 14.73, 15.33, 15.53 s | 11.8 to 15.74 s, 2.5 cuts per s, no white after 11.43 s | Close slower and flash-free. | minor | flash rule on `mid` after the drop and on `outro`, `p: 0.4`, last shot excluded; `cuts.lengths.outro: [[0.5,4],[0.25,2],[1,1]]`. |
| R16 | grade and contrast | 76 / 90 / 72 by section, whole 83, YHIGH 143 | 86 / 103 / 86, whole 95, montage 113, YHIGH 153 | Normaliser works (most shots within 15 of target) but the result still sits 10 to 14 above the reference in every section; B&W shots such as 1.47 s (120) and 1.1 s (112) overshoot because contrast 1.35 and vignette are applied after the luma pull. | minor | engine/fx.py grade: apply `target_luma` after contrast and vignette, or lower targets to `0.27` (B&W) and `0.33` (colour) in style.json `grade.timeline`. |
| R17 | B&W to colour turn | one switch at 4.9 s and at about 13.4 s | four steps 4.43 to 5.4 s, three steps 13.27 to 14.0 s | Staged rather than a single switch, return about 0.6 s late. | minor | `grade.timeline` points 0.305/0.31 and 0.835/0.84, or `grade.snap_to_cut: "single"` in engine/plan.py. |
| R18 | colour palette | teal and orange push | natural footage colour | Not graded. | cosmetic | `split_tone` on colour stops in engine/fx.py. |
| R19 | tiles | colour-wheel tile at 10.0 s, tiles at 14.66 to 15.5 s | none | `tile` only fires on role `high`, which this plan never produces. | minor | `moves.tile.when.role: ["high","drop","outro"]`, `p: 0.15`. |
| R20 | x-ray overlay | 6.9 to 7.4 s | none | Content-dependent. | cosmetic | No change. |
| R21 | speed ramps and whips | whips at 1.28 and 11.6 s, speed push 12.8 s | none | No directional smear or speed change. | minor | `whip` move (directional blur plus 2x speed over 0.25 beat) on `intro` and `drop`, `p: 0.15`, engine/fx.py and engine/plan.py. |
| R22 | sound gaps and dips | 5 intro gaps 0.15 to 0.25 s at -36 to -54 dB; dips at 9.7, 12.2, 14.6 s | 7 intro gaps about 0.1 s at -82 to -120 dB; no pre-hit dips | Gaps now there but short and dead silent, which sounds like dropouts rather than the reference's breathing room tone. No dips before montage hits. | minor | sfx gap: `dur: 0.2`, add `floor_db: -40` (engine/render.py mix_audio keeps a room-tone floor), `p: 0.3`; add a `gap` at `cut` on role `drop` with `p: 0.12`, `dur: 0.15`, `offset: -0.15`. |
| R23 | loudness | -15.0 LUFS | -20.5 LUFS | 5.5 LU quieter. | minor | engine/render.py mix_audio: `loudnorm=I=-15:TP=-1.5` on the final mix. |
| R24 | riser | build audible into the 9.3 s white | no continuous build before 7.87 s | Build into the drop not heard. | minor | `sfx.riser.gain: 0.7`, duck music 3 dB under the riser span. |
| R25 | masking flash | full white silhouette 15.90 to 15.93 s, luma 68 to 109 | 15.33 and 15.50 s, white patches on a cloth pile, rise 7 | Better than round 2 but no silhouette reads. | minor | engine/clips.py `clips.last_prefers_person: true`; fallback full-frame flash `alpha: 0.6` when mask coverage is under 5 per cent; `mask_flash.portion: [0.3,0.42]`. |
| R26 | final hold | final shot 15.56 to 16.3 s is the longest | 1 s hold at 14.0 s, final shot 0.5 s | Ends on a cut, not a hold. | minor | `cuts.last_shot_beats: 1.5` in engine/plan.py, outro shots before it 0.5 beat or less. |
| R27 | duration | 16.3 s | 15.74 s | 0.56 s shorter. | cosmetic | `--duration 16.3` or `structure.end_on_bar: false`. |
| R28 | framing | 16:9 band | 9:16 by brief; hanger shot 2.7 to 3.2 s luma 54 | Improved, still dim behind the first caption. | cosmetic | engine/clips.py: reject focus crops under luma 25 or pick another `src_in`. |
| N1 | caption tail into the drop | words end at 8.2 s, montage enters at 9.3 s with no running text | "BEFORE USE." held 7.23 to 8.23 s, 0.36 s past the drop at 7.87 s, washed by the drop flash and RGB split | The last card bleeds into the montage and is hit by its first effects. | minor | engine/captions.py: clamp the last chunk's hold to end at `structure.drop_at` minus one frame (`captions.until: "drop"`), or set `captions.hold_beats: 0.5` for the final chunk. |
| N2 | negative frames | inverted frames are negative pictures (7.27 to 7.4 s high-key skull) | 0.733 s flash and invert on the same cut give a full black frame; 8.37 and 8.87 s inverts cover whole 0.13 s shots (luma 167, 168) | Stacking invert on a flash turns white into black, and whole-shot inverts lift montage luma. | minor | engine/plan.py: skip `invert` on a cut that already has a `flash`; style.json invert `span_beats: [0, 0.125]` so one or two frames invert, not the whole shot. |
| N3 | outro audio | music at full level to 16.3 s | fades from -16 to -38 dB over 15.4 to 15.7 s | Ends on a fade, the reference ends on a held level into the end card. | cosmetic | engine/render.py mix_audio: `audio.fade_out` of 0.05 s, or 0 when the edit ends on a hold. |
| N4 | montage words | giant OH in red at 9.6 to 9.8 s, K in cyan on white at 9.9 s | none | The montage now has no text at all, so the reference's one or two full-height accent words are missing. | minor | `captions.montage_words: 2` (key words from the VO, full height, accent colour, 0.2 s each, on a flash) in engine/captions.py. |

Out of scope: footage subjects, spoken words, the 9:16 aspect, and the snap to the 122 BPM sixteenth grid (19.9 ms mean measured, 86.5 per cent within one frame).

## Grid files

All grids are in `/Users/student/dev/design-library/edits/bw-flash-vo/review-round-3/`, reference row above the render row, timestamps in each cell.

1. `01-overview-0-5.4s.png` overview, 12 evenly spaced pairs, render 0 to 5.2 s (framegrid.py, times mapped proportionally)
2. `02-overview-5.4-10.8s.png` overview, render 5.3 to 10.5 s
3. `03-overview-10.8-16.3s.png` overview, render 10.6 to 15.63 s
4. `04-intro-dense.png` intro flash cuts, ref 0 to 2.17 s, render 0 to 2.33 s
5. `05-vo-entry-captions.png` voiceover entry and first captions, ref 2.8 to 4.8 s, render 2.75 to 4.8 s
6. `06-colour-turn.png` B&W to colour turn, ref 4.6 to 7.27 s, render 4.45 to 7.5 s
7. `07-drop-entry.png` drop and montage entry, ref 7.4 to 9.3 s, render 7.6 to 8.4 s
8. `08-montage-flashes.png` montage, ref 9.93 to 12.6 s, render 8.5 to 11.43 s
9. `09-outro-maskflash.png` return to B&W, close and masking flash, ref 13.4 to 16.25 s, render 12.6 to 15.7 s
10. `10-caption-legibility.png` 10 caption moments, ref 3.3 to 8.0 s, render 3.1 to 7.4 s
11. `11-caption-tail-drop.png` last caption against the drop, ref 7.6 to 9.9 s (incl. OH and K), render 7.7 to 8.2 s
12. `12-caption-end-and-matte.png` caption end at 8.23 s, TEXTILES matte cut at 4.3 s, masking flash at 15.33 and 15.5 s against the reference silhouette

Scratch (cropped reference band, scene lists, per-frame luma and saturation, audio envelope and pairing scripts) is in `review-round-3/scratch/`.

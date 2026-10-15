MAJOR: 3, MINOR: 15, COSMETIC: 10. Major differences remain (3).

# bw-flash-vo, round 2 review

Reference: `_source/v24044gl0000dagu96vog65oq9i5qe0g.MP4`, band cropped to 548x308 at x14 y97, 0 to 16.3 s (`review-round-2/scratch/ref_band.mp4`).
Render: `rounds/round-2.mp4`, 720x1280, 15.73 s, seed 4, 122 BPM (beat 0.492 s), 55 shots, TTS voiceover from 2.95 s, captions on Whisper word times.

Owner typography directive applies: caption face, scale, layout, accent colour, scrim and depth layering are recorded as cosmetic, "intentional, owner directive". Legibility, placement safety and timing of that treatment are judged on their own rows.

## Measurements

| Measure | Reference band | Round 1 | Round 2 |
| --- | --- | --- | --- |
| Scene changes (ffmpeg scene > 0.2, incl. flash frames) | 73 in 16.3 s | 74 in 15.7 s | 82 in 15.7 s |
| Intro cut rate | about 5 per s (0 to 2.2 s), shots 0.1 to 0.37 s | 2.5 per s | 4.4 per s (0 to 2.7 s), shots 0.13 to 0.37 s, first shot 0.23 s |
| Montage | 9.3 to 12.9 s, about 4.9 per s | 7.87 to 11.8 s, 5.3 per s | 7.87 to 11.8 s, 5.6 per s |
| Close (after montage) | 12.9 to 15.5 s, about 3.4 per s, 5 white flashes | 2.3 per s, 1 flash | 11.8 to 15.73 s, 2.5 per s, 0 flashes |
| Frames with mean luma > 200 | 34 | 7 | 11 (0.6, 1.1, 1.83, 2.33, 7.9, 8.23, 8.5, 9.1, 9.7, 10.83, 11.43) |
| Mean luma, whole edit | 83 | 115 | 108 |
| Mean luma, opening B&W / colour / closing B&W | 76 / 90 / 72 | n/a | 96 / 112 / 118 |
| Mean YHIGH / YLOW | 143 / 44 | 172 / 50 | 162 / 54 |
| Colour arrives | hard switch on the cut at 4.9 s | ramp 4.4 to 5.7 s | stepped over four shots, bw 0.90, 0.72, 0.46, 0.10 at 4.43, 4.67, 4.93, 5.4 s |
| Back to B&W | about 13.4 s, one step | ramp 13.2 to 14.2 s | stepped bw 0.27, 0.62, 1.0 at 13.27, 13.53, 14.0 s |
| Integrated loudness / true peak | -15.0 LUFS / -4.0 dB | -19.5 LUFS | -21.5 LUFS / -1.3 dB |
| Intro audio gaps (50 ms RMS) | 5 gaps to -36 to -54 dB at 0.35, 0.6, 0.8, 1.3, 2.0 s, 0.15 to 0.25 s long | none | 1 gap (0.65 s, silent); 4 more planned gaps (0.73, 1.1, 1.23, 1.97 s) are filled by impact tails |
| Dips before montage hits | 9.65 to 9.8 s (-28 dB), 12.15 to 12.35 s (-40 dB), 14.6 s (-24 dB) | none | none |
| Voiceover | 3.1 to 8.2 s (31 to 50 per cent of the edit) | none | 2.95 to 14.37 s (19 to 91 per cent) |
| Masking flash, luma rise on the final shot | 68 to 109 at 15.90 to 15.93 s | soft wash | 137 to 141 at 15.33 and 15.5 s (not visible) |
| Cut offset from 122 BPM sixteenth grid (check.json) | n/a, not beat locked | 10.8 ms | 13.5 ms mean, 92.5 per cent within one frame |

## Status of round 1 majors

| id | round 1 issue | status | evidence |
| --- | --- | --- | --- |
| D1 | caption layout (staircase vs 2 to 3 word chunks) | closed by owner directive, reclassified cosmetic (R1) | owner settled the kinetic chunk layout |
| D2 | caption font, size, weight | closed by owner directive, reclassified cosmetic (R2) | Anton is the owner's choice |
| D5 | captions run through the montage and close | open (R7) | words on screen from 2.95 to 14.9 s without a break longer than 0.5 s; reference montage and close carry no running text |
| D10 | intro cut rate and first shot | closed | 12 shots in 0 to 2.7 s (4.4 per s), shots 0.13 to 0.37 s, first shot 0.23 s (grid 04) |
| D11 | no flashes or negative frames before the drop | partly closed (R12) | intro flashes at 0.6, 1.1, 1.47, 1.83, 2.33 s and an invert at 0.73 s now present; still nothing at 0.0 s, and no flash anywhere from 2.46 to 7.87 s where the reference has its 4.3 s phrase-change flash and the 7.27 s inverted frame |
| D15 | grade too bright, not low key | partly closed (R16) | whole-edit mean luma 115 to 108 against 83; the closing B&W stretch got brighter (118 against 72) |
| D21 | no voiceover, no ducking | closed | TTS voiceover from 2.95 s, word-timed captions, music ducked about 9 dB under speech (render.py duck 0.65) |
| D22 | intro sound not cut-led | partly closed (R22) | clicks, intro impacts and one audible gap at 0.65 s; four of five planned gaps are masked, no pre-hit dips |

Round 1 minors and cosmetics: D6 caption timing closed (voiceover word times), D21-dependent D6 rhythm now follows speech. D3, D4, D8, D9 reclassified as owner directive (R3 to R6). D7, D12, D13, D14, D16, D18, D20, D23, D24, D25, D26, D27 open or partly open, see table.

## Current differences

| id | category | reference time | render time | description | severity | suggested change |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | caption layout | 3.1 to 8.2 s staircase, one word per line | 2.95 to 14.9 s, 1 to 3 word chunks, stacked flush left | Kinetic chunks replace each other instead of accumulating as a staircase. | cosmetic | Intentional, owner directive. No change. |
| R2 | caption face and scale | small humanist bold sans, accent 1.5x | Anton, `size_frac 0.115`, key word 1.8x (TEXTILES, DESTROYED, DESTROYING span almost the full width) | Different face and scale. Legible at phone size. DESTROYED at 6.6 s and DESTROYING at 13.0 s run to about 3 per cent from the right edge. | cosmetic | Intentional, owner directive. Optional: cap key-word width at 0.86 of frame width in engine/captions.py (kinetic fit). |
| R3 | caption placement | upper middle block | lower left, block bottom at y 0.84 to 0.86 | Lower-left by directive. The bottom line sits inside the band that TikTok and Reels cover with the caption and username overlay (bottom 15 to 20 per cent). | cosmetic | Intentional, owner directive. Consider `captions.y: 0.78` to keep the last line above the platform UI. |
| R4 | caption accent colour | dark red (DREAM), cyan with red split (CONSCIOUSNESS) | gold (230,200,138), body cream | Different accent colour. | cosmetic | Intentional, owner directive. |
| R5 | caption scrim | none, 2 px shadow | subtle dark band under the block | Visible on bright shots (5.6 to 6.3 s, 13.5 to 14.0 s), reads as intended. | cosmetic | Intentional, owner directive. |
| R6 | depth layering of text | none, text always in front | `depth_text.enabled`, words alternate behind and in front | Different layering. Its legibility is judged in R9. | cosmetic | Intentional, owner directive. |
| R7 | caption span and voiceover structure | voiceover and text 3.1 to 8.2 s, montage and close textless apart from giant OH (9.6 s) and K (10.0 s) | voiceover and captions 2.95 to 14.9 s, "SINCE / 19 JULY 2026," held 8.0 to 10.7 s over the montage, "UNSOLD CLOTHES." held into the B&W close | The montage and the close read as a subtitle track. The voiceover covers 72 per cent of the edit against 31 per cent in the reference, so the drop lands mid-sentence and the picture never gets its wordless stretch. Partly driven by script length, but placement against the structure is style. | major | engine/plan.py: place `structure.drop_at` after the voiceover's last phrase end (new key `structure.drop_after_vo: true`) or cap the VO at 45 per cent of the edit and tell the caller; add `captions.until: "drop"` so running captions end at the drop, with an optional `captions.montage_words` (one or two key words, full height, accent colour, 0.2 s each). Shorter script for this test (two phrases, about 5 s). |
| R8 | caption legibility, tokenising | n/a | 3.1 to 4.4 s | Whisper split "4-9%" into "4", "-9", "%", so the first two cards read "4 / -9" then "% / OF". The opening fact is unreadable. | minor | engine/make_edit.py `group_phrases` (or a new `merge_tokens` pass after `whisper_words`): join a token that starts with "-", "%", "," or "." onto the previous one and keep number ranges together ("4-9%"). |
| R9 | caption legibility, depth matte | n/a | SINCE 8.07 s (letters cut, reads "SI CE"), PLACED ON THE 4.85 s and COMPANIES FROM 12.0 s (faded, low contrast) | On textile shots with no clear subject, the matte slices letters out of front words and the behind words drop to roughly half opacity. | minor | engine/captions.py (depth pass, lines 183 and 207): skip the behind pass when the mask covers under 8 per cent of the frame or the word box overlaps the mask by less than 30 per cent; raise `captions.depth_text.min_visible` from 0.55 to 0.8; never put the key word behind. |
| R10 | caption layering under effects | text is never blurred; CONSCIOUSNESS keeps colour through the 7.27 s inverted frame | 3.47 s zoom blur smears "4 / -9", 7.91 s RGB split on BEFORE USE, 9.37 and 10.4 s zoom blur on 19 JULY 2026, 11.0 s invert turns THE EU dark, 12.2 and 13.18 s zoom blur on COMPANIES FROM and DESTROYING | Captions are still composited before the post layer (render.py lines 321 to 357), so blur, split and invert hit the text. | minor | engine/render.py: move the caption block after the post-layer loop, or add `captions.layer: "top"`; keep flash affecting text if wanted via `captions.effects_hit: ["flash"]`. |
| R11 | pre-voiceover hold | 2.17 to 3.13 s, one slow-zoomed eye shot, voiceover starts on the cut | 2.33 to 2.7 s and 2.7 to 3.2 s, voiceover enters mid-shot at 2.95 s on a near-black hanger shot | No breath before the first word, and the entry is not on a cut. | minor | Add `structure.pre_vo_hold_beats: 2` (engine/plan.py: force one shot spanning `vo_start_beats - 2` to `vo_start_beats`, then cut on the first word). |
| R12 | flashes before the drop | white at 0.0, 0.2, 1.5 to 1.63, 4.3 s; inverted frame 7.27 to 7.4 s | white at 0.6, 1.1, 1.47, 1.83, 2.33 s, invert 0.73 s, then nothing from 2.46 to 7.87 s | Intro is now right, but the voiceover stretch has no punctuation flash and the edit does not open on white. | minor | style.json moves: add `{"fx":"flash","at":"phrase","when":{"p":1.0,"max":1}}` for the first phrase change and an `invert` at `"at":"drop","span_beats":[-1,-0.75]`; set `cuts.first_flash: true` (engine/plan.py) for a white first frame. |
| R13 | drop position and entry | blur build 8.2 to 9.3 s (radial and zoom blur, colour smear), montage enters on white at 9.3 s (57 per cent) | montage enters at 7.87 s (50 per cent) on flash + RGB split + shake at once, no build | Unchanged from round 1. | minor | `structure.drop_at: 0.57`, add `zoom_blur` with `at: drop`, `span_beats: [-2, 0]`, ramping amount 0.05 to 0.3; remove the drop `shake` and `rgb_split` or cut them to `amount: 0.008`. |
| R14 | montage flash density | 9.3 to 12.7 s, about 20 near-white frames, including a six-frame white burst 12.0 to 12.17 s and white smear frames | 7.87 to 11.8 s, 7 near-white frames; flashes decay in 0.12 s so only one frame reads as white | Montage flashes are there but thinner and never hold. | minor | flash on `high` and `drop`: `p: 0.55`, `span_beats: [0, 0.35]`, add `params.hold_frames: 1` (engine/fx.py flash) and one `flash` with `span_beats: [0, 0.5]` near the montage end. |
| R15 | close rhythm and flashes | 12.9 to 15.5 s, cuts every 0.2 to 0.5 s, white at 13.4, 13.9, 14.73, 15.33, 15.53 s | 11.8 to 15.73 s, 2.5 cuts per s, a 1 s hold at 14.0 to 15.0 s, no flash at all after 11.43 s | Close is slower than the reference and flash-free. | minor | `moves`: add a flash rule on `mid` after the drop and on `outro` with `p: 0.4`, excluding the last shot; `cuts.lengths.outro: [[0.5,4],[0.25,2],[1,1]]`. |
| R16 | colour grade and contrast | low key: 76 / 90 / 72 mean luma by section, highlights about 143 | 96 / 112 / 118, highlights 162; bright grey shots at 0.32 s (pile), 1.12 s (machine), 6.4 to 7.37 s (cream pile, luma 135 to 143), last shot 15.23 to 15.73 s (luma 140 against 68) | Fixed brightness offsets do not tame bright cream footage. The closing B&W is the brightest part of the render while it is the darkest in the reference. | major | engine/fx.py grade: add a per-shot exposure normaliser, `grade.target_luma` (B&W stops 72, colour stops 88) with a clamp of plus or minus 0.25, applied before contrast; or set B&W stops to `brightness: -0.22, contrast: 1.4, gamma: 0.85` and colour stops to `brightness: -0.12`. Check each section against the targets above. |
| R17 | B&W to colour turn and back | one hard switch at 4.9 s, one at about 13.4 s | colour comes in over four shots (4.43 to 5.4 s) and leaves over three (13.27 to 14.0 s); strong colour shelves still on screen at 13.54 to 13.9 s | Now changes on cuts, but staged rather than one switch, and the return is about 0.6 s late. | minor | `grade.timeline`: put the 0.28 and 0.36 points 0.005 apart (0.305, 0.31) and the 0.84 and 0.90 points likewise (0.835, 0.84), or `grade.snap_to_cut: "single"` in engine/plan.py so the whole change lands on one cut. |
| R18 | colour section palette | teal and orange push, saturation 10 to 17 | natural colour; teal floor and orange shelves come from the footage | Not graded, footage colour. | cosmetic | Add `split_tone` to the colour stops (shadows teal, highlights orange) in engine/fx.py. |
| R19 | overlays and tiles | colour-wheel tile with K at 10.0 s, small colour tiles in the B&W timeline at 14.66 to 15.5 s | no tile events | `tile` still only fires on role `high`, which this song plan does not produce. | minor | `moves.tile.when.role: ["high","drop","outro"]`, `p: 0.15`. |
| R20 | x-ray overlay | x-ray skull in the silhouette 6.9 to 7.4 s | none | Content-dependent, known gap. | cosmetic | No change. |
| R21 | speed ramps and whip smears | motion-smear whips at 1.28 and 11.6 s, speed-blurred push at 12.8 s | every shot at speed 1.0; zoom blur only | No directional smear or speed change. | minor | Add a `whip` move (directional blur plus 2x speed over 0.25 beat) on `intro` and `drop` cuts, `p: 0.15`, in engine/fx.py, and allow `speed` ramps in engine/plan.py. |
| R22 | sound design, gaps and dips | five intro gaps of 0.15 to 0.25 s to -36 to -54 dB; dips before montage hits at 9.7, 12.2, 14.6 s | one 0.1 s gap at 0.65 s; planned gaps at 0.73, 1.1, 1.23, 1.97 s are filled by impact tails (still -17 to -24 dB); no pre-hit dips | The stop-start, cut-led intro sound is still mostly missing. | major | style.json sfx gap: `dur: 0.2`, `p: 0.5`; engine/render.py mix_audio: apply gap muting to the sfx bus too, or skip intro impacts that fall inside a gap; add `{"kind":"gap","at":"cut","when":{"role":["drop"],"p":0.12},"dur":0.15,"offset":-0.15}` for pre-hit dips. |
| R23 | loudness | -15.0 LUFS integrated | -21.5 LUFS (round 1 -19.5) | 6.5 LU quieter, regressed. mix_audio only peak-limits to 0.89, so the drop impact sets the level. | minor | engine/render.py mix_audio: soft-limit then normalise to -15 LUFS (ffmpeg `loudnorm=I=-15:TP=-1.5` on the final wav). |
| R24 | riser | riser audible into the 9.3 s white | 5.67 to 7.87 s, level -20 to -29 dB, not heard over voiceover and music | Build into the drop is not heard. | minor | `sfx.riser.gain: 0.7`; duck music 3 dB over the riser span. |
| R25 | masking flash | white silhouette of the man at 15.90 s, luma 68 to 109 | 15.29 and 15.48 s on a pile of cloth with no person, luma rise 4 (invisible) | The signature closing flash does not read at all (raised from cosmetic). | minor | engine/clips.py: `clips.last_prefers_person: true`; fall back to a full-frame white flash with `alpha: 0.6` when the mask covers under 5 per cent; `mask_flash.portion: [0.3, 0.42]`. |
| R26 | outro, final hold | final shot is the longest hold, 15.56 to 16.3 s (0.74 s) | 1 s hold at 14.0 to 15.0 s, then 0.23 s and a 0.5 s final shot | The final shot is shorter than the one before, so the edit ends on a cut rather than a hold. | minor | `cuts.last_shot_beats: 1.5` (engine/plan.py) and keep `outro` shots before it at or under 0.5 beat. |
| R27 | duration | 16.3 s | 15.73 s | 0.57 s shorter. | cosmetic | `--duration 16.3` or `structure.end_on_bar: false`. |
| R28 | aspect and framing | 16:9 band | 9:16 by brief; near-black hanger crops at 1.28 s and 2.7 to 3.2 s (luma about 30) carry the first caption | Some reframes lose the subject. | cosmetic | engine/clips.py: reject focus crops with mean luma under 25 or pick another `src_in`. |

Out of scope: footage subjects, spoken words, the 9:16 aspect, and the snap to the 122 BPM sixteenth grid (13.5 ms mean offset, 92.5 per cent within one frame).

## Grid files

All grids are in `/Users/student/dev/design-library/edits/bw-flash-vo/review-round-2/`, reference row above the render row, timestamps in each cell.

1. `01-overview-0-5.4s.png` overview, ref 0 to 5.3 s, render 0 to 5.2 s
2. `02-overview-5.4-10.8s.png` overview, ref 5.45 to 10.75 s, render 5.25 to 10.4 s
3. `03-overview-10.8-16.3s.png` overview, ref 10.9 to 16.25 s, render 10.5 to 15.7 s
4. `04-intro-dense.png` intro flash cuts, 0 to 2.4 s both, 16 pairs
5. `05-vo-entry-captions.png` voiceover entry and first captions, ref 2.8 to 4.9 s, render 2.7 to 4.8 s
6. `06-colour-turn.png` B&W to colour turn, ref 4.2 to 7.2 s, render 4.0 to 7.0 s
7. `07-drop-entry.png` drop and montage entry, ref 7.2 to 9.5 s, render 7.3 to 9.6 s
8. `08-montage-flashes.png` dense montage strip, ref 9.8 to 12.8 s, render 9.6 to 12.6 s
9. `09-outro-maskflash.png` return to B&W, close and masking flash, ref 13.3 to 16.25 s, render 13.0 to 15.7 s
10. `10-caption-legibility.png` 20 caption moments side by side, ref 2.9 to 13.9 s, render 3.1 to 13.95 s

Scratch (cropped reference band, scene lists, per-frame luma and saturation, audio envelope script, pairing script, mask flash strip) is in `review-round-2/scratch/`.

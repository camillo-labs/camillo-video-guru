# lyric-word-beat (also: one-word lyric captions, difference-blend captions, TikTok CapCut lyric template)

Source: the 16:9 edit inside the phone screen recording ScreenRecording 22-33-20 (16.9 s, 1290x2796 frame, edit band 1290x724 at y 911). The raw measurements are in analysis.json. The source clips are not redistributed.

## What it looks like

A 16.9 s landscape music edit of night and dusk running and gym shots, about nine shots long. One lyric word at a time sits dead centre in heavy white capitals, and the word changes five times a second with no animation at all. The caption uses a difference blend, so it is white over dark footage, sky blue over orange, olive green over pink and navy over white. Between shots the footage is thrown through short, loud transitions (mono tile mosaic, strobe, haze card, band wipe, radial zoom blur, card slide up) while the caption layer carries on untouched above them. Mid-way a Nike swoosh sticker and a JUST DO IT wordmark replace the sung words "just do it", sit behind the runner, and push the caption to the lower third. It ends on the first shot again, so it loops.

## What makes it work

- The caption layer is independent of the picture. It never stops for a transition, a black dip or a flash, so the lyric always reads and the picture can be violent.
- Word timing follows the vocal, one word per sung word, held until the next word. Median gap is 0.20 s, so the text moves faster than the cuts and creates the rhythm.
- The difference blend makes legibility automatic on any footage and gives each shot a colour accent for free.
- Each shot gets about one bar and a bit (4 to 5.5 beats) and each change has a different transition, so no two look the same, while the cut spacing stays steady.
- Loud moments are saved for the music: the first two transitions land on bar downbeats, a drop at bar 4 gets the longest transition, the quiet bar 6 gets the logo moment.
- Footage is left in its own grade (moody, low-key night and dusk). The style does not need a LUT.

## Measured facts

- Tempo 138.7 BPM (beat 0.4326 s, bar 1.73 s), beat phase 0.26 s. Kick on beat 1, snare on beats 2 and 4 (accent ratio 0.25 on beats 2 and 4 against 0.14 on 1 and 3). Bars start at 0.26, 1.99, 3.72, 5.45, 7.18, 8.91, 10.64, 12.37, 14.10 s. Bar loudness (RMS) 0.11, 0.13, 0.16, 0.245, 0.22, 0.15, 0.115, 0.15, 0.20: quiet intro, build, drop at bar 4 (5.45 to 8.9 s), lull at bar 6 (10.6 s), second build.
- Audio is a rap track (Whisper large-v3-turbo transcribes it cleanly). The words on screen are the real lyric, timed to the vocal within 0.1 s of Whisper's word starts. The caption shows 84 words in 16.5 s, 5.1 words per second.
- Word gaps: 0.133 s (37 words), 0.20 s (26), 0.267 s (9), then rare longer holds up to 0.73 s at line ends. In eighth notes that is 0.6, 0.9 and 1.2 eighths, so the words are not on the eighth grid, they sit on the vocal. Mean offset of word onset to the nearest 16th is 27 ms, which equals chance, so do not snap words to the grid when real word times exist.
- Shot lengths (landing to landing) in beats: 3.4, 3.9, 5.4, 5.5, 4.3, 5.2, 4.9, 4.2 then a 1 beat tail. Mean of the middle six is 4.9 beats (2.1 s), range 3.9 to 5.5. The first two boundaries sit on bar downbeats (offsets +10 ms and -21 ms), later ones drift to beat 13.4, 18.8, 23.1, 28.3, 33.2, 37.4, so the cut does not stay bar-locked. Transition start to nearest kick onset averages 86 ms (14 events), with flash peaks and the strobe landing within 15 to 40 ms of a kick or 16th.
- No speed ramps, no punch-ins, no freeze frames. All camera motion is in the source clips. The only scaling is the card moves (50 percent card, 62 percent card).

## Shot by shot

Times in seconds. Beats = shot length at 138.7 BPM.

| # | In | Out | Beats | Content | Transition in |
|---|----|-----|-------|---------|---------------|
| 1 | 0.00 | 1.47 | 3.4 | A: night bridge runner, handheld, warm lamps | none, caption LEVEL then IS (loop seam) |
| 2 | 1.47 | 2.00 | 1.2 | black, then 3x3 mono tile mosaic of shot 3 | hard dip to black 1.467 (held 4 frames), cells appear one every 1 to 2 frames 1.63 to 1.9, cool desaturated with grain |
| 3 | 2.00 | 3.70 | 3.9 | B: runner legs close-up | 2-frame strobe 2.00 to 2.10 (luma 37, 68, 40, 78, 41), colour snaps in on downbeat |
| 4 | 3.70 | 6.03 | 5.4 | C: gym pull-up from behind | white haze veil 3.70, shot appears as a 50 percent dark card 3.77 to 3.9, hard white flash 3.90, fog peak 4.10, full frame 4.13 |
| 5 | 6.03 | 8.40 | 5.5 | D: two runners from behind, night road | band wipe 6.03 to 6.57 (new shot enters as a top band of about 20 percent and bottom band of about 38 percent, middle closes over 13 frames), orange flare and bloom at 6.567 fading over 4 frames |
| 6 | 8.40 | 10.27 | 4.3 | E: sunset pull-up silhouette | radial zoom blur 8.40 to 8.57, cream white 8.57 to 8.63, hard cut at 8.667 |
| 7 | 10.27 | 12.50 | 5.2 | F: night bridge runner (Nike moment) | hard cut at 10.267 with red swoosh sticker, white silhouette strobe 10.667 to 10.833 (on, off x3), JUST DO IT wordmark 11.333 to 12.5 behind the runner, caption at 75 percent height |
| 8 | 12.50 | 14.60 | 4.9 | G: dusk field push-up | dip to black 12.5, card slides up from the bottom edge at 12.733 with a slight perspective tilt, holds as a 62 percent card with rounded corners 13.0 to 13.55, scales to full by 13.75 |
| 9 | 14.60 | 16.43 | 4.2 | H: sunset duo from behind | hard cut 14.60 |
| 10 | 16.43 | 16.87 | 1.0 | A again | hard cut 16.433, dip to black 16.67, invert flash 16.77 to 16.87, then loop to shot 1 |

## Caption rules

- One word at a time. Hard swap on the frame the word is sung, no fade, no slide, no scale. Held until the next word. Between lines the previous word stays (the last word of a line stays up to 0.7 s).
- Case and font: uppercase, heavy geometric sans (Montserrat ExtraBold look, Arial Black or Futura Bold are acceptable stand-ins), tracking +1 percent, cap height 6.9 percent of band height (50 px at 724), widest word about 26 percent of band width.
- Position: horizontal centre, vertical centre at 50 percent. During a graphic that owns the middle (the logo section) move to 75 percent. The move is a hard jump.
- Colour: white fill, difference blend over the picture. Add a soft dark drop shadow (about 35 percent black, 6 px blur, 2 px offset at 1290 wide). The result must follow the footage colour, not be a fixed tint.
- Layer order: caption above the footage and the transitions, below nothing. It stays visible over black dips (white), flashes (turns near black) and the invert flash.
- Words the lyric treats as a brand phrase (just do it) are replaced by a graphic and the caption pauses for them (11.33 to 11.8 s).
- Lead-in and loop: the video begins on the last word of the previous bar (LEVEL) and ends on THE LEVEL, so a loop reads as continuous.

## Overlays

- Brand sticker: a red swoosh at 12 percent of frame width, upper left of the subject (x 28 percent, y 38 percent), in front of the subject, on screen from 10.27 to 12.5.
- Wordmark: JUST DO IT in white condensed heavy capitals, about 60 percent of frame width, at y 45 percent, behind the subject (it needs a person matte), the swoosh crosses its O.
- Silhouette flash: a person matte filled white, shown on alternate frames three times (6 frames) on the accented word.
- TikTok interface icons on the right edge and the tiny "but there's some place" text in shot 1 belong to the recording and the source clip, not to the style.

## Colour grade

No shared grade. The footage is moody and low-key. Per-shot stats (mean RGB, luma, saturation) are in analysis.json. Typical values: luma 0.06 to 0.38, black level p1 0.00 to 0.06, p99 0.26 to 0.64, saturation 0.27 to 0.59. Night shots are warm amber (R minus B about 0.09), the gym is neutral (0.01), sunset shots are magenta or orange. Compression noise is heavy and edges soft (upscaled low-resolution clips). The mosaic cells are the only graded look: desaturated, cool, grainy.

## Recipe (ffmpeg and engine terms)

1. Analyse the song: BPM and beat phase, bars, bar RMS. Cut points at bar 1 (first downbeat after 1.5 beats), then every 4 to 5.5 beats, rounded to the nearest beat, with the transition peak (white or flare frame) on a beat or 8th. Put the longest transition on the loudest bar and a quiet logo bar after it.
2. Assign clips by energy: calm clips on lull bars, fast or bright clips at the drop. Repeat shot 1 as the last shot for the loop.
3. Transitions (rotate, never repeat back to back): mono_mosaic (black dip 4 frames, 3x3 cells in random order, 8 frames, then 2-frame strobe), haze_card_flash, band_wipe, radial_zoom_blur_flash, card_up, hard_cut. Frame counts at 30 fps: strobe 2 to 3 frames, flash 1 to 2 frames, radial blur 5 frames plus 2 frames white, band wipe 13 frames plus 4 flare, card slide 6 frames, hold 16, scale 6.
4. Caption layer at 30 fps: text rendered white on black, composed with blend=difference over the picture, shadow added first. Word times from Whisper word timestamps, or if only text is supplied, one word per 0.2 s (0.9 eighth) with 0.133 s for short words and a hold at line ends.
5. Optional graphic moment: sticker plus wordmark behind the subject (person matte) on the quietest bar, caption to 75 percent, silhouette strobe on the accent word.
6. Output at 1920x1080 (the original is 16:9), crf 18, AAC 192k.

## When to use it

- Lyric or voice-over driven reels, brand films and trailers where a song carries the message and the footage is already moody.
- Fast, high-contrast social content where captions must stay legible over anything.

## When it hurts

- Whole sentences: five words a second is too fast to read for anything that is not sung. Keep it for lyrics or slogans.
- Bright, mid-grey or pastel footage: the difference blend turns text into weak colour on mid tones. Add a 30 percent dark scrim, or fall back to white with a stronger shadow.
- Accessibility: the strobe frames (3 flashes in 0.17 s) are risky. Keep strobes under three flashes a second and offer a reduced mode.

## Needs engine support (met by the engine, see the Engine section)

- Difference-blend caption layer and word-level timing from audio, plus a fixed font stack with fallbacks (no drawtext or libass in the local ffmpeg, render captions with Pillow).
- Transitions: dip_black, mono_mosaic, strobe, haze_card_flash, band_wipe, radial_zoom_blur_flash, card_up, invert_flash.
- Sticker and wordmark placement behind a person matte, silhouette strobe.
- Beat grid from the new song, loop seam (repeat the first clip last).

## Engine

The style runs through the generic engine. Any clips and any song give a new edit with cuts, transitions and word changes on the new beat grid.

```
edits/.venv/bin/python edits/engine/make_edit.py --style lyric-word-beat \
  --clips ./footage --music ./song.mp3 --captions ./lyrics.txt \
  --aspect 16:9 --duration 17 --res 540 --out ./out
```

Output: edit.mp4, edl.json (the plan, editable, re-render with --edl), song.json and check.json (cut offsets from the beat grid). One line of the captions file is one phrase. Without --captions the style renders no words. With --transcribe the Whisper word times of the song's vocals are used instead of the beat grid.

The style rules are in style.json and the new effects are in engine/ext/lyric_word_beat.py (captions kind lyric_diff, effects lyr_dip_mosaic, lyr_strobe_pop, lyr_haze_flash, lyr_band_wipe, lyr_radial_flash, lyr_card_up and the overlay lyric_sticker).

| Parameter | Meaning | Measured value |
|-----------|---------|----------------|
| structure.drop_at, drop_beats | where in the edit the song's first drop lands, and how many beats the drop role lasts | 0.32, 4 |
| cuts.lengths | shot length in beats, weighted, by section role (intro, low, mid, high, drop, outro) | mostly 4 or 5, some 3 or 6, mean 4.9 in the source |
| cuts.first_shot_beats | opening shot length | 3 (3.4 in the source) |
| cuts.loop_seam_beats | a final shot of this length repeats the first clip so the edit loops | 1 |
| moves (layer pre) | one transition per cut, picked by shot index modulo 8 so no two neighbours match: 1 mosaic, 2 strobe pop, 3 haze flash, 4 band wipe, 5 radial blur, 6 sticker moment (hard cut), 7 card up, 0 hard cut | source order |
| moves, last | dip_black then invert at the seam | source ending |
| captions.timing.step_beats | beats between words, a list that is cycled so word gaps are uneven, plus phrase_gap_beats at line ends | 0.5, 0.5, 0.25, 0.5, 0.75, 0.5, 0.25, 0.5 and 1 |
| captions.size_frac, size_frac_portrait | cap height as a share of picture height (landscape) or width (portrait) | 0.096, 0.13 |
| captions.guard | pushes weak mid-tone difference colours toward white or black, 0 is a pure difference blend | 1.0 |
| captions.y, y_alt | centre height, and lower third while the sticker moment is live | 0.5, 0.75 |
| overlays.lyric_sticker | brand tick sticker, wordmark text behind the subject (needs a person matte), silhouette strobe | text KEEP GOING |

How each measured behaviour maps onto the rules:

- One word at a time, hard swap, held to the next word: caption kind lyric_diff, grid timing with a cycled step list.
- Difference blend and caption above every transition: the transitions run on the pre layer and the caption reads the picture through ctx['img'], so it blends with whatever is under it, dips and flashes included.
- Shots of about one bar and a bit with a different transition each: cuts.lengths and the index-modulo move rules.
- Mosaic, strobe, haze, band wipe, radial blur and card slide: the six lyr_ effects. Band wipe and card up use the outgoing picture, held on its last frame (ctx['store']['prev_shot_last']).
- Sticker moment on the quiet bar: a mask_flash event with alpha 0 and tag sticker marks the window and forces person-matte generation, the overlay draws the sticker, the wordmark behind the subject and the six-frame silhouette strobe.
- Loop: loop_seam_beats and the dip and invert flash on the last cut.

## Generalisation

Four runs with the self-generated test clips and songs, all at 540 px short side, check.json from the engine (cuts re-detected in the rendered video, beat grid re-detected from the rendered audio).

| Run | Clips | Song | Aspect | Shots | Cuts detected | Mean cut offset from nearest eighth (ms) | Offset from the true 16th grid (ms) |
|-----|-------|------|--------|-------|---------------|------------------------------------------|-------------------------------------|
| demo A | A | house128 | 16:9 | 9 | 7 of 8 | 7.6 | 8.0 (max 16) |
| demo B | B | hiphop100 | 9:16 | 7 | 5 of 6 | 3.2 | 0.5 (max 0.5) |
| extra | B | house140 | 16:9 | 9 | 8 of 8 | 7.2 | 8.0 (max 18) |
| extra | A | hiphop122 | 9:16 | 8 | 6 of 7 | 9.7 | 12.0 (max 28) |

A frame is 33.3 ms at 30 fps, so every mean offset is under one frame. The undetected cuts are the ones hidden by a dip or flash, which the frame-difference detector cannot see. In every run the caption layer stays above the transitions, the words change at the beat-locked step list, and the sticker moment appears when the edit has at least seven shots (demo A and the 140 BPM run, not demo B). The look differs from the source because the test footage is bright and saturated, so the difference blend gives coloured text where the source gave mostly white. Frames of the two demos are in demo/*.sheet.png.

Reproduce the demos:

```
cd edits
.venv/bin/python engine/make_edit.py --style lyric-word-beat --clips _testdata/clips/A_16x9 --music _testdata/music/house128.wav --captions lyric-word-beat/demo/lyrics-A.txt --aspect 16:9 --res 540 --out /tmp/demoA
.venv/bin/python engine/make_edit.py --style lyric-word-beat --clips _testdata/clips/B_9x16 --music _testdata/music/hiphop100.wav --captions lyric-word-beat/demo/lyrics-B.txt --aspect 9:16 --res 540 --out /tmp/demoB
```

Run engine/make_testdata.sh first if edits/_testdata is missing. The demos are re-encoded with ffmpeg at crf 24.

## What the engine does not capture

- Word times come from a beat-locked step list, not from the vocal. The source followed the sung words, which sit off the 16th grid as much as chance. Use --transcribe on a song with vocals to follow the vocal instead.
- The source's word rate (about 5 a second) belongs to 139 BPM. Slower songs give fewer words a second because the step is in beats.
- Transitions hold the outgoing shot on its last frame, where the source kept it moving.
- The mosaic cells show copies of the whole incoming frame, the source tiles looked like crops.
- The 50 percent dark card step in the haze flash, the horizontal slat offsets of the band wipe and the perspective tilt in the card slide are simplified or missing.
- The sticker is a generic curved tick, not a real brand mark, and the wordmark text is a style parameter, not the lyric. The sticker moment needs seven or more shots and a person matte (Apple Vision, or a .mask.mp4 beside the clip).
- Shot lengths follow beats exactly. The source drifted off the bar, mean 4.9 beats, the engine's mean is 4.0 because the intro and seam shots are short and the planner snaps to phrases.
- Heavy source compression grain and the soft upscaled look. Montserrat ExtraBold is replaced by Arial Black.
- Weak-contrast footage: the guard keeps text readable but gives up a pure difference blend on mid-tone pictures.

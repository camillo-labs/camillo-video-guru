# hud-lyric-heat (also: lyric text behind the subject, detect HUD, thermal flash)

Source: Cam's screen recording of the CapCut-style template playing over a ski summit selfie (1288x764 recording, the video inside is 1288x724 at y=8, 16:9, plus a TikTok UI overlay that is not part of the style). This README holds the shared description of the whole "hud-lyric" template. hud-lyric-light/README.md covers the second rendering (a 1024x576 download over a snowfield hoodie shot) and refers back here. Raw numbers are in analysis.json.

## What makes the edit work

One continuous take is never cut. All the energy comes from a stack of overlays that fire on a repeating clock while huge lyric captions sit between the subject and the camera.

1. Text behind the subject. Each lyric phrase is one line of fat uppercase letters set across the middle of the frame, 2 or 3 words. The subject's body is cut out and laid back on top of the text, so the middle word is hidden and only the first and last words show on either side. The eye reads the phrase and the person together as one object.
2. A fake machine-vision HUD. A brown top bar types "DETECTING" with a growing run of dots, small white coordinate readouts scroll in (x, y, A%ps, X%ps, SIN&q, Xor, And, Or, then rows of dense glyph blocks), white X marks and L brackets flick in, a white card with a drop shadow slides across, and a network of thin curves with ringed nodes drifts over the shot. It says "the computer is tracking this person".
3. The detect wipe. At a phrase change a brown band as tall as the caption row slides across the middle. Inside it the subject turns into a pale inverted cut-out (the mask made visible), the "DETECTING......" label sits over it and the new caption pops in mint green with a pink ghost offset behind it. It lasts 4 to 8 frames, then the caption settles to its theme colour.
4. The heat flash. A thermal-camera look fires for about 0.3 s two or three times in a clip (loop time 6.3 s and 8.7 s in v1, 6.5, 9.5 and 12.4 s in v4). The picture inside a band between 11.5 and 88.4 percent of the frame height is converted to a black, deep red, orange, gold, cream gradient map, the subject gets a hot rim, red squares jump in at the corners, the caption goes tan or gold, and the band slides sideways so the caption appears twice with a seam (WAGON then BRAND). The text colour theme changes on a heat flash (pink to red-gold to blue).
5. Glitch reveal. The clip opens with 0.4 to 0.5 s of block displacement and RGB tear on the subject, then settles.
6. A long clean intro. About 4 s of untouched footage with no captions follows the glitch, so the first caption lands as an event.

## What is template and what is footage

Template (identical in both renderings): the glitch reveal, the clean intro of about 4 s, the HUD bar styling, the readout text, the X marks and brackets, the detect wipe, the heat gradient map and its band, the caption font and size, the 2.95 s effect clock, the red square markers, the node network, the single black matte frame at the loop point.

Footage dependent: the caption row height (49 percent of frame height in the ski shot, 59 percent in the hoodie shot, always across the subject's torso or head), the caption words, the theme colours (v1 uses a single red, v4 uses pink then red-gold then blue), the grade of the footage (v1 is a cool teal grade baked into the source, v4 is a flat grey-blue), the TikTok overlay and watermark.

## Measured numbers (this rendering, v1)

- Tempo 124 BPM (beat 0.484 s), grid phase 0.27 s in the recording. Fitted on three bands, results 123.9 to 124.3.
- The video loops every 9.9 s under a song that keeps playing, so loop two (from 1.93 s) is not in sync with the music. Only the first pass, 1.93 to 11.83 s, is musically aligned.
- Captions follow lyric word onsets, mean absolute offset 78 ms (range -200 to +90). Heat flash and detect wipe are not on the beat grid. Their offsets to the nearest eighth note average 58 ms, which is chance level (60 ms for random times). The effect clock is 2.95 s, which is 6.1 beats at 124 BPM, so on a new song the engine should snap it to 6 beats (2.90 s).
- Caption on-screen time 0.4 to 1.1 s. Phrase length 2 to 3 words.
- Grade of the clean footage: mean RGB 121, 144, 155, saturation 0.30, black point at 1st percentile luma 2, white point at 99th percentile 245. Heat flash mean RGB 149, 87, 64, saturation 0.63.

## Shot by shot (v1 timestamps, seconds in the recording)

| Time | What happens |
|---|---|
| 0.00 to 0.50 | Tail of the previous loop. Caption THE GROCERY SHOP (red, behind the subject) |
| 0.67 to 1.03 | Heat flash (loop time 8.7 s, the same event as 10.6 s), caption changes to LOOKING LAVISH, small gold and orange squares jump in |
| 1.17 to 1.20 | Detect midband flick |
| 1.30 to 1.80 | Brown top bar with DETECTING, readouts, X mark |
| 1.93 | Single black matte frame, only the subject and the red caption remain on black. The loop point |
| 2.00 to 2.50 | Glitch reveal of the subject, block displacement and RGB split, 15 frames |
| 2.50 to 6.30 | Clean footage, subject drifts, no captions, no overlays (3.8 s) |
| 6.37 to 6.80 | First HUD, bar and readouts enter, a white X |
| 6.83 | Caption 1 BOUGHT MAMA appears (red, 2 words with the subject hiding the join) |
| 7.17 to 7.23 | Caption 2 A CRIB AND A, fades in from a pink wash over about 4 frames |
| 7.30 to 7.50 | Top bar again with DETECTING |
| 7.80 to 7.83 | Caption 3 BRAND NEW WAGON, orange square marker at the lower left |
| 8.27 to 8.57 | Heat flash (0.3 s), caption goes dark red inside the heat band, readouts fill the right edge |
| 8.70 | Detect midband flick |
| 8.80 to 9.30 | Top bar with readouts |
| 9.00 | Caption 4 NOW SHE HIT |
| 9.60 to 9.90 | Top bar, caption 5 THE GROCERY SHOP at 9.63 |
| 10.60 to 10.93 | Heat flash again, caption 6 LOOKING LAVISH |
| 11.07 to 11.10 | Detect midband flick |
| 11.20 to 11.80 | Top bar and readouts, then black matte at 11.83 and the loop restarts |

## Style rules as general parameters

- Structure: glitch 0.45 s, clean intro 4 s (about 8 beats at 124 BPM), then captioned body in cycles of 6 beats, finish on a held caption or a black matte frame.
- One caption per lyric phrase. Onset equals the first word onset of the phrase, give or take 80 ms. Hold until the next phrase starts. Phrases of 2 to 3 words, shown on one line.
- The effect clock: every 6 beats run the sequence top bar on (0.64 s), detect wipe (0.13 s), top bar again (0.4 s), detect wipe (0.24 s), and a heat flash 2.2 s after the cycle start (0.3 to 0.4 s). Measured cycle 2.95 s in v4, where the heat flash fires every cycle. In v1 the loop is shorter and the two flashes sit 2.3 s apart, so treat the cycle as 2.3 to 2.95 s and place flashes at colour theme changes.
- Caption change: always masked by an event (detect wipe or heat flash or the pink-to-final wash), never a bare cut of text.
- Overlay objects fire in front of the subject, but the caption sits behind it.
- Subject motion: none added. The shot is the performer's own movement. Do not push in.

## Recipe with exact parameters

Reference canvas 1024x576 (scale everything by height/576).

Caption text
- Font: heavy geometric grotesque, flat terminals, uppercase. Closest installed on macOS is Arial Black, closest free is Montserrat ExtraBold or Archivo Black. Cap height 55 px (9.5 percent of the frame height), letter spacing 0, line gap not needed (one line).
- Colour in v1: #d41117 (red), no glow, no outline. In the light rendering: pink #e60a96 with a 6 px soft glow of the same colour at 60 percent opacity, blue #1c6fe0, gold #ffc040 inside heat.
- Placement: centred on x, vertical centre at 49 percent of the height for a head-and-shoulders shot (0.59 for a lower subject). Words spaced so the line spans 54 to 90 percent of the width. The middle word goes behind the subject.
- Animation in: hard pop under the detect wipe (green #00f5a0 with a pink ghost at -4 px, 4 to 8 frames at 30 fps, then the theme colour). In the second variant a 4 frame fade from a pale pink wash.

HUD
- Top bar: height 11 percent, colour #6b5442, text "DETECTING" white, extended heavy sans at about 11 px, dots appended one per frame up to 18, a scramble of random capitals for the first 3 frames (DETECNIOH). On for 0.4 to 0.65 s.
- Readouts: white, monospaced or condensed 10 px, 8 lines (x, y, A%ps, X%ps, SIN&q, Xor, And, Or) with 15 digit random floats re-rolled every 2 frames, a block of 6 to 8 lines of dense CJK-style glyph blocks at 9 px, placed at the left (x 9 percent, y 17 percent) or the right edge (x 87 percent). Opacity 0.9, no background.
- X marks: two crossing 2 px lines, white with a black twin offset by 2 px, 90 px across, placed at the top right or the centre. L brackets: 2 px white, 40 px legs, at the frame edge. Show for 3 to 4 frames then move.
- Card: 200x110 px, #e6e8ee, drop shadow 4 px at 50 percent black, slides 80 px sideways in 6 frames.
- Network: 14 thin curves, 1 px, white at 55 percent, with 10 ring nodes of 5 px radius (some dark rings), drifting slowly over 0.6 s.
- Red square marker: #c0100e, 70 px square, jumps to a corner for 3 to 5 frames at a flash.

Detect wipe
- Band: brown #6b5442, rows 55 to 78 percent of the height (the caption row plus 6 percent), full width, enters from the left over 3 frames.
- Subject inside the band: matte filled with an inverted, brightened version (luma plus 90, saturation 0.2, a light blue tint).
- Label: "DETECTING......" white at 11 px under the caption, caption mint #00f5a0 with the pink ghost.

Heat flash
- Band: rows 11.5 to 88.4 percent of the height. Convert the picture to luma, then gradient map with the stops black (0,0,0), (97,3,6), (170,10,3), (221,122,29), (251,133,18), (246,197,80), (255,240,175) at 0, 0.15, 0.35, 0.55, 0.7, 0.88, 1.0.
- Add a hot rim to the subject: edge detect the matte, dilate 2 px, fill gold (255,191,109).
- Slide: the band content offsets 100 percent of the width over 6 frames, with the caption repeated at the seam.
- Duration 0.3 s on, 2 frames flash to near white at the first frame.

Glitch reveal
- 12 to 15 frames. Per frame 6 to 14 random horizontal bands 4 to 40 px tall displaced by up to 80 px, 20 percent of frames with 2 px RGB channel offset, a few black rectangular dropouts on the subject.

Grade
- Cool teal bias, saturation 1.25, contrast up, black point near zero, white point 245. Hoodie variant stays flat and desaturated.

## Effects and caption features an engine needs

1. Person matte per frame (Vision person segmentation, or a luma key for a dark subject on a bright background, or a centre ellipse as a fallback) with 1 px feather.
2. Text-behind-subject compositor: footage, then caption, then footage times matte on top.
3. Word-onset caption timing (from a lyric SRT or Whisper word timestamps), 2 to 3 word phrases, middle word hidden.
4. HUD generator: top bar typewriter, random readout lines, X marks, brackets, card, network curves, red square.
5. Detect wipe band with inverted cut-out and a green-and-pink caption pop.
6. Heat gradient map with hot rim and a sliding band.
7. Glitch reveal generator.
8. Effect clock quantised to 6 beats of the new song, caption onsets snapped to word onsets.
9. Optional black matte frame at a loop point, and an end card.

## When to use it

Lyric edits of a single locked-off or slow performer shot, 10 to 20 s, for rap or trap. It makes any solo performance feel designed. It needs a subject that separates from the background and room behind them for text.

## When it hurts

- Readability: the middle word is hidden by design, so keep the hidden word a connective such as "and", "new" or "she".
- Flashing: the heat flash has two near-white frames. Keep it below three flashes per second and offer a reduced version without the flash.
- Busy backgrounds: the text behind the subject needs a calm field behind it.
- Legibility of the readouts is not intended, they are texture.


## Engine

Style file: `hud-lyric-heat/style.json`. Effects, the caption kind and the end card overlay live in `engine/ext/hud_lyric.py` and are shared by hud-lyric-heat and hud-lyric-light. Run it on any clips and any song:

```
edits/.venv/bin/python edits/engine/make_edit.py --style hud-lyric-heat --clips <folder> --music <song> \
  --captions $'grab the red\nkeep it moving\nnever slow down' --duration 16 --aspect 16:9 --out ./out
```

One caption line is one phrase, keep it to 2 or 3 words, `*word*` marks emphasis (unused by this style). Lyrics from the song itself: pass `--transcribe` instead of `--captions` and the Whisper word times drive the phrases. Aspect 9:16 also works, the type scales down and the row stays at the same height fraction. Footage with a person gets the real text-behind-subject effect through Apple Vision person segmentation (compiled on first use from `engine/vision.swift`), a clip with a `name.mask.mp4` next to it uses that matte, and footage with no person falls back to a soft centre ellipse that hides the middle word.

How the measured behaviour maps onto `style.json` (all times are in beats of the new song, so the tempo can be anything):

| Measured in the source | Rule in style.json |
|---|---|
| 0.45 s glitch reveal at the start | `hud_glitch` event, `at: time`, `sec: 0`, `span_beats: [0, 1]`, plus a milder one on 70 percent of cuts |
| About 4 s (8 beats) of clean footage, first caption lands after it | `structure.intro_beats: 8`, `cuts.first_shot_beats: 8`, `captions.timing.start_beat: 8.5` |
| Effect clock of 2.95 s, 6.1 beats | every `hud_*` rule is `at: beat`, `every: 6`, with `offset` giving the position in the cycle, snapped to the beat grid |
| Top bar with DETECTING at cycle start and again 2 beats in | `hud_bar` offsets 8 and 10, `dur_beats: 1.5` (left readouts and X marks, then right readouts, card and network) |
| Detect wipe 1.5 and 3 beats into the cycle | `hud_wipe` offsets 9.5 and 11, `dur_beats: 0.5`, `layer: pre` so the caption sits on top |
| Heat flash 4.5 beats into the cycle, theme change on it | `hud_heat` offset 12.5, `dur_beats: 0.75`, caption theme index equals the number of heat flashes started |
| Red and blue squares after the flash | `hud_marks` offsets 12.5 and 13.5 |
| 2 to 3 word phrases, about 0.77 s hold | `captions.timing`: grid, `step_beats: 0.5`, `phrase_gap_beats: 0.5`, `max_hold_beats: 3` |
| Caption row height and size | `captions.y` (0.49), `size_frac: 0.133` of the frame height (cap height about 9.5 percent), `span: 0.80` |
| Single red theme, teal biased grade | `captions.themes`: one colour #d41117, `grade.base`: saturation 1.2, contrast 1.08, tint 0.93, 1.0, 1.05 |
| No end card in the loop cut | `hud.end_card_beats: 0` |

Multi-shot input is supported. The originals are one long take, so the default shot lengths are long (6, 8 or 12 beats, never below 6) and the energy comes from the overlays, which keep cycling over the cuts. Pass many clips and each is used once or twice, matched to the song's energy by `clips.select: energy_match`. Parameters you can edit in style.json: `hud.row_y`, `hud.end_card_beats`, the caption `themes` list (colour as RGB, optional `glow` radius in pixels at 576 high), `size_frac`, `span`, the `offset` and `dur_beats` of every HUD rule, and `params` of each effect (`hud_heat`: `contrast`, `beta`, `slide`, `slide_portion`, `colormap` stops are fixed in the module, `hud_bar`: `side`, `xmark`, `brackets`, `card`, `network`, `hud_marks`: `count`, `size`, `color`).

Every planned event lands in `edl.json`, so the HUD cycle can be moved by editing offsets there and re-rendering with `--edl edl.json`.

hud-lyric-heat differs from hud-lyric-light only in parameters: one red theme, no glow, a graded footage look, no end card and stronger default heat (contrast 1.25, beta 5).

## Generalisation

Both runs use self-generated clips and music (`engine/make_testdata.sh`), 16:9, 16 s, at 540 px. The numbers are against the synthesised ground-truth grid (the song's true tempo and phase), which is more exact than the grid re-detected from the rendered audio. One frame is 33.3 ms, so a cut or event can be up to 16.7 ms from the grid just from quantising to a frame.

| Run | Clips | Song | Shots | Cut offset from true grid | Event starts, mean absolute | Caption onsets |
|---|---|---|---|---|---|---|
| demo-A-house128 | A_16x9 | house128, 128 BPM | 3 | 12.5 ms (max 16.2) | 7.6 ms over 30 events (max 16.2) | 7.3 ms |
| demo-B-hiphop100 | B_16x9 | hiphop100, 100 BPM | 4 | 0.4 ms | 0.4 ms over 22 events | 0.4 ms |

Events are HUD effect starts (bar, wipe, heat, marks, glitch, zoom pulse). Cuts are few because the style holds shots for 6 to 12 beats. Caption word onsets sit on the eighth-note grid by construction (mean 0.4 to 8.6 ms). Visual check: the sheets in `demo/` show the intro glitch, the clean 8 beats, the DETECTING bar with readouts, the mint caption and pale subject cut-out during wipes, the heat band with red and blue squares, and the theme change at each flash. A real person test (a local trim of the original v4 footage, not in the repo) gave a clean text-behind-subject result with the Apple Vision matte, the hood and shoulders hiding the middle word and the heat band showing the gold rim.

## What the engine does not capture

- The original effect clock drifts against the beat (6.1 beats). The engine snaps to 6 beats, so the engine is tighter than the source, by design.
- Exact artwork: the font is Arial Black (the original is a Montserrat ExtraBold style face), the readouts are random numbers and hexadecimal rather than the original glyph blocks, and the network, X marks and card are approximations.
- The pale inverted cut-out in the detect wipe is a luma inversion tinted light blue, not the original's exact look. The thermal map is the measured gradient, but its character depends on the footage luma (the light style lowers `beta` to keep pale footage red instead of gold).
- The black matte frame at the loop point and the 4 s platform end card with its logo are not reproduced. `hud_end_card` is a generic dark card with a typed handle and no logo.
- Person segmentation is Apple Vision, macOS only. Footage with no person can produce a false matte (Vision sometimes finds a person in abstract shapes), and then the wipe shows a pale block. Pass `name.mask.mp4` to override.
- Words longer than about 11 letters shrink the whole phrase. Phrases of 4 or more words get small.
- The caption fade-in from a pale pink wash seen in some v4 phrases is a hard pop here.

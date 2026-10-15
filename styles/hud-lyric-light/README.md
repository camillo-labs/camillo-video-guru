# hud-lyric-light (hud-lyric template on a pale snowfield shot, longer cut)

Source: a 1024x576, 30 fps, 17.2 s TikTok download of the same template as hud-lyric-heat, over a flat grey-blue snowfield shot of a hooded dancer in sunglasses (a black Nike hoodie), with a TikTok watermark at the top left and a 4 s TikTok search end card. Read hud-lyric-heat/README.md first for the shared template, the recipe parameters and the engine feature list. This file records what this rendering adds or does differently. Raw numbers are in analysis.json.

## What makes this version work

The v4 cut is the template at full length, so it shows the whole colour progression. Because the footage is nearly colourless (a pale grey-blue sky and a black hoodie), the saturated caption colours and the red heat band carry the entire look. Three caption themes appear in order, each introduced by a heat flash:

1. Pink #e60a96 with a soft pink glow for the first six phrases.
2. Red-gold inside the heat band for STAR TREK (the band turns the pink into tan and gold).
3. Blue #1c6fe0 with glow for GROOVE THE and WRAITH CALLING, then a gold flash and orange for GIRLS GET LOOSE.

## Measured numbers

- Tempo 124 BPM (beat 0.484 s), grid phase 0.21 s. Fitted on three bands, results 123.95 to 124.0.
- Caption onsets sit on lyric word onsets, mean absolute offset 59 ms. Individual offsets are +50, -50, +10, -10, -10, -110, -80, +90, +70, +110 ms.
- The effect clock is exact: the top bar starts at 4.33, 7.27 and 10.23 s (2.94 and 2.96 s apart), the detect wipe at 5.00, 7.93 and 10.90 s, the heat flash at 6.53, 9.47 and 12.43 s (2.94 and 2.96 s apart). The cycle is 2.95 s, which is 6.1 beats at 124 BPM, so it runs on a fixed clock and drifts against the beat grid. Offsets to the eighth-note grid average 36 ms for the detect wipe and 51 ms for the top bar, chance level.
- Caption hold times: 0.64, 0.66, 1.10, 0.70, 1.00, 0.97, 0.77, 0.70, 1.36 s, median 0.77 s.
- Grade of the clean footage: mean RGB 138, 153, 170, saturation 0.22, luma 1st percentile 19, median 165, 99th percentile 188 (low contrast, lifted blacks). Heat flash mean RGB 159, 51, 46, saturation 0.78. End card mean RGB 19, 20, 32.

## Shot by shot (seconds)

| Time | What happens |
|---|---|
| 0.00 to 0.13 | Clean first frames, subject with a hand at the sunglasses |
| 0.13 to 0.57 | Glitch reveal: black block displacement and RGB tearing on the subject (3 strong frames at 0.17, 0.47, 0.53, rest mild) |
| 0.60 to 4.00 | Clean footage, no overlays and no captions (3.4 s). The subject turns from front to profile to back |
| 4.03 to 4.30 | White and grey panel strips slide in (the first HUD event, mean diff 22), readouts and X marks start |
| 4.33 to 4.97 | Top bar with DETECTING |
| 4.53 | Caption 1 GRAB MAMA A, pink, glow |
| 5.00 to 5.13 | Detect wipe flick, mint text with pink ghost |
| 5.17 | Caption 2 CRIB AND A, pink |
| 5.30 to 5.70 | Top bar, network curves over the shot |
| 5.73 to 5.97 | Detect wipe with the white subject cut-out |
| 5.83 | Caption 3 BRAND NEW WAGON, pink |
| 6.53 to 6.90 | Heat flash (red band, text turns tan, red squares at the corners, band slides so WAGON and BRAND meet at the seam) |
| 6.93 | Caption 4 NOW SHE HIT |
| 7.27 to 7.90 | Top bar, readouts, X marks |
| 7.63 | Caption 5 THE GROCERY SHOP |
| 7.93 to 8.07 | Detect wipe, mint text |
| 8.23 to 8.63 | Top bar |
| 8.63 | Caption 6 LOOKING LAVISH |
| 8.67 to 8.90 | Detect wipe with large brown panel |
| 9.00 to 9.40 | Red square and X marks |
| 9.47 to 9.83 | Heat flash, caption 7 STAR TREK arrives at 9.6 in gold |
| 10.23 to 10.87 | Top bar |
| 10.37 | Caption 8 GROOVE THE, blue |
| 10.90 to 11.03 | Detect wipe, orange text |
| 11.07 | Caption 9 WRAITH CALLING, blue |
| 11.20 to 11.60 | Top bar, red square |
| 11.63 to 11.87 | Detect wipe with the white subject |
| 12.43 to 12.80 | Heat flash, caption 10 GIRLS GET LOOSE in gold |
| 12.83 to 13.13 | Blue held |
| 13.17 to 17.17 | End card: dark navy #0d0f1f with the TikTok logo and an animated search bar typing a handle (platform UI, not part of the style) |

## What differs from hud-lyric-heat

- The cut is 13.1 s of content, three full effect cycles and three heat flashes, versus a 9.9 s loop with two flashes.
- Text row is lower (59 percent of the height) because the subject is lower in frame, the cap height is the same 55 px at 1024x576.
- Text has a soft same-colour glow (6 px), whereas v1 text is flat red.
- Three colour themes instead of one.
- The footage has almost no saturation, so a flat grey-blue grade plus saturated text is the formula. Do not grade the footage.
- The song starts at frame 0, so the cut is synced to the music from the first frame. The template starts counting the effect clock at 4.03 s, about 8.3 beats in.

## Style rules to carry into the engine

- Open with 0.45 s of glitch, hold clean footage for 8 beats, start the captioned body on the first lyric phrase after beat 8.
- Run a 6 beat effect clock from the first caption. Place the heat flash 2.2 s (4.5 beats) after each cycle start and let it carry the colour theme change.
- Change theme colour at heat flashes only. Cycle theme colours pink, red-gold, blue, gold in that order of warmth, or any palette of 3 to 4 saturated colours that are not the footage hues.
- A caption lasts for its phrase. Median 0.77 s, so keep phrases to 2 to 3 words and about 1.5 to 3 words per second.
- Finish on the last lyric word, then cut to an outro card or a hold.

## When to use it

The same as hud-lyric-heat, and in particular for a pale or desaturated subject shot where saturated type and the heat band give colour. Use hud-lyric-heat when the footage is already saturated and graded.


## Engine

Style file: `hud-lyric-light/style.json`. Effects, the caption kind and the end card overlay live in `engine/ext/hud_lyric.py` and are shared by hud-lyric-heat and hud-lyric-light. Run it on any clips and any song:

```
edits/.venv/bin/python edits/engine/make_edit.py --style hud-lyric-light --clips <folder> --music <song> \
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
| Caption row height and size | `captions.y` (0.59), `size_frac: 0.133` of the frame height (cap height about 9.5 percent), `span: 0.80` |
| Pink, blue, gold, orange themes with a 6 px glow | `captions.themes`: four colours, each with `glow: 6` |
| Footage left ungraded | `grade.base` empty |
| 4 s end card (8 beats) | `hud.end_card_beats: 8`, `overlays: hud_end_card`, HUD rules stop at `frac_max: 0.72` |
| Pale footage turns red, not gold, in the heat band | `hud_heat` params `contrast: 1.0`, `beta: -70` |

Multi-shot input is supported. The originals are one long take, so the default shot lengths are long (6, 8 or 12 beats, never below 6) and the energy comes from the overlays, which keep cycling over the cuts. Pass many clips and each is used once or twice, matched to the song's energy by `clips.select: energy_match`. Parameters you can edit in style.json: `hud.row_y`, `hud.end_card_beats`, the caption `themes` list (colour as RGB, optional `glow` radius in pixels at 576 high), `size_frac`, `span`, the `offset` and `dur_beats` of every HUD rule, and `params` of each effect (`hud_heat`: `contrast`, `beta`, `slide`, `slide_portion`, `colormap` stops are fixed in the module, `hud_bar`: `side`, `xmark`, `brackets`, `card`, `network`, `hud_marks`: `count`, `size`, `color`).

Every planned event lands in `edl.json`, so the HUD cycle can be moved by editing offsets there and re-rendering with `--edl edl.json`.

hud-lyric-light differs from hud-lyric-heat only in parameters, see the table above. Use it when the footage is pale or flat and the saturated type plus the heat band must supply the colour.

## Generalisation

Both runs use self-generated clips and music (`engine/make_testdata.sh`), 16:9, 16 s, at 540 px. The numbers are against the synthesised ground-truth grid (the song's true tempo and phase), which is more exact than the grid re-detected from the rendered audio. One frame is 33.3 ms, so a cut or event can be up to 16.7 ms from the grid just from quantising to a frame.

| Run | Clips | Song | Shots | Cut offset from true grid | Event starts, mean absolute | Caption onsets |
|---|---|---|---|---|---|---|
| demo-A-house140 | B_16x9 | house140, 140 BPM | 5 | 12.6 ms (max 17.4) | 9.3 ms over 27 events (max 17.4) | 8.3 ms |
| demo-B-hiphop122 | A_16x9 | hiphop122, 122 BPM | 4 | 9.9 ms (max 17.8) | 7.7 ms over 22 events (max 18.3) | 8.6 ms |

Events are HUD effect starts (bar, wipe, heat, marks, glitch, zoom pulse). Cuts are few because the style holds shots for 6 to 12 beats. Caption word onsets sit on the eighth-note grid by construction (mean 0.4 to 8.6 ms). Visual check: the sheets in `demo/` show the intro glitch, the clean 8 beats, the DETECTING bar with readouts, the mint caption and pale subject cut-out during wipes, the heat band with red and blue squares, and the theme change at each flash. A real person test (a local trim of the original v4 footage, not in the repo) gave a clean text-behind-subject result with the Apple Vision matte, the hood and shoulders hiding the middle word and the heat band showing the gold rim.

## What the engine does not capture

- The original effect clock drifts against the beat (6.1 beats). The engine snaps to 6 beats, so the engine is tighter than the source, by design.
- Exact artwork: the font is Arial Black (the original is a Montserrat ExtraBold style face), the readouts are random numbers and hexadecimal rather than the original glyph blocks, and the network, X marks and card are approximations.
- The pale inverted cut-out in the detect wipe is a luma inversion tinted light blue, not the original's exact look. The thermal map is the measured gradient, but its character depends on the footage luma (the light style lowers `beta` to keep pale footage red instead of gold).
- The black matte frame at the loop point and the 4 s platform end card with its logo are not reproduced. `hud_end_card` is a generic dark card with a typed handle and no logo.
- Person segmentation is Apple Vision, macOS only. Footage with no person can produce a false matte (Vision sometimes finds a person in abstract shapes), and then the wipe shows a pale block. Pass `name.mask.mp4` to override.
- Words longer than about 11 letters shrink the whole phrase. Phrases of 4 or more words get small.
- The caption fade-in from a pale pink wash seen in some v4 phrases is a hard pop here.

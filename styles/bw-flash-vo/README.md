# bw-flash-vo (black and white flash cuts with a voiceover staircase)

Source: the 16:9 edit band inside a vertical explainer video (576x1024, 21.4 s, the band is 548x308 at x14 y97, 30 fps, 16.3 s of edit followed by a 4 s platform end card that is not part of the style). Raw measurements are in analysis.json. The explainer carries the creator's own timeline annotations, which name the moves in the edit, and they are used below as ground truth.

## What makes the edit work

- It starts in black and white and earns its colour. The first 4.8 s are fully monochrome, the picture goes to full colour at about 5 s on the first wide shot of the voiceover, stays colourful through the middle, then drops back to black and white for the last two shots. The grade change is the narrative, so the colour reveal feels like the point of the voiceover.
- Cut density breathes. A flash intro runs at 4.2 cuts per second (2.4 s), the voiceover section relaxes to 1.6 cuts per second so the words can be read, the middle montage returns to 4.9 cuts per second, and the close settles at 3.4 per second before one long final hold of 0.85 s. Median shot length is 0.43 beats and the mean 0.6, so almost everything is shorter than one beat.
- White flash frames punctuate the cuts. There are 22 near-white frames in 16 s, bunched in the montage (9.3 to 12.7 s), plus single negative or inverted frames and a masking flash that fills the subject's silhouette with white.
- Captions are a voiceover spelled out one word per line. Each new word sits one line lower and one step further right (first phrase, growing downward) or one line higher and one step right (last phrase, growing upward). Words stay on screen across cuts, so the text is a second rhythm laid over the picture, and one word per phrase breaks the colour: DREAM in dark red, CONSCIOUSNESS in cyan with a red split, OH and K in red and cyan.
- Sound design carries the cuts. The creator's labels list riser, charge, whoosh, tremolo, clicks, impact, page flick and hiss, so every flash or zoom has a sound under it.
- It is not beat-locked in the original. Cuts sit at chance level against the 128 BPM grid (31.2 ms mean offset from the sixteenth grid against 29.1 ms expected by chance) because the cuts follow the sound effects and the voiceover rather than a track. The engine snaps cuts to the new song's sixteenth grid, which is what Cam asked for.

## Shot by shot (approximate to 0.1 s, 30 fps)

| Time | Content | Move |
| --- | --- | --- |
| 0.0 to 0.5 | Extreme close-up of an eye, black and white, held one beat | hold, low-key grade |
| 0.5 to 2.2 | Eleven cuts: hand on white, page edge, book text, phone, motion-smeared lights, camera cage, pen, SSD, keyboard typing | flash cuts of 0.1 to 0.37 s, two white frames, whip smear |
| 2.2 to 3.0 | Eye closes, eye opens, face close-up | slow zoom, hold |
| 3.0 to 4.3 | Face close-up, voiceover begins on beat 6 | staircase WHAT, DO, YOU, PLAN, TO DO, growing downward, 4.3 s white flash |
| 4.3 to 4.9 | Keyboard | IF THIS WHOLE, DREAM in red |
| 4.9 to 5.9 | First colour shots, a man at a window over a city at dusk | colour arrives, OF YOURS DOESN'T, WORK OUT |
| 5.9 to 7.2 | The same view in blue hour, then snow (a season match cut) | THAT, DOESN'T, EVEN, MY |
| 7.2 to 8.2 | Head silhouette in a softbox ring | CONSCIOUSNESS in cyan with red split, x-ray skull overlay, inverted frame, black with red word |
| 8.2 to 9.3 | Screen text blur, colour scopes, colour smear | radial blur and zoom blur into a white flash at 9.3 |
| 9.3 to 12.9 | Rapid montage: camera lens, timeline UI, colour wheels, clock, teal disc, man at a desk | 0.1 to 0.3 s cuts, a white flash every 0.2 to 0.3 s, negative flashes, tiled colour and zoom, OH in red at 9.6 to 9.8 s then K in cyan on white at 9.9 s |
| 12.9 to 15.5 | Office shots, book pages flicking, a watch flipping between negative and positive, timeline UI | 0.2 to 0.5 s cuts, white flashes at 13.4, 13.9, 14.7 and 15.3 s, small tiles of colour inside a blurred timeline |
| 15.6 to 16.8 | A man working at a desk, black and white | one long hold, two masking flashes (white silhouette) at about 15.9 and 16.7 s, then the end card |

## Measured style rules (generalised)

- Shot lengths in beats: 22 per cent at 0.25, 30 per cent at 0.5, 17 per cent at 0.5 to 0.6, 13 per cent at 0.75, 8 per cent at 1, 7 per cent at 1.5 to 2, 3 per cent at 3. Intro and montage use the shortest shots, the voiceover stretch uses 1 to 3 beats.
- Flash frames: about 40 per cent of cuts in the high-energy stretch, 12 per cent elsewhere, each one frame of full white decaying within 0.25 beat. Negative (inverted) frames on about 12 per cent of montage cuts. Zoom blur across the cut on about 22 per cent of mid and high cuts.
- Slow zoom of 1.0 to 1.09 over every shot of 0.75 beat or more.
- Grade timeline (fraction of the edit): 0.00 to 0.28 black and white, contrast 1.25, vignette 0.35. 0.36 to 0.84 colour, saturation 1.05 to 1.1, contrast 1.12. 0.90 to 1.00 black and white, contrast 1.3, vignette 0.4.
- Captions: uppercase bold humanist sans (the engine uses Avenir Next Bold), size 7.5 per cent of the short side, white, a 2 px soft shadow, accent word 1.5 times larger in dark red (150, 20, 20). Block anchored at x 30 per cent, y 28 per cent growing down, or y 74 per cent growing up, 3.4 per cent of the width indent per line, fade in 0.05 s, linger 0.5 s after the last word, no clearing at cuts.
- Voiceover starts on beat 6 (2.7 s at 128 BPM) so the first word lands on a beat, music ducked about 8 dB under speech.
- Sound effects: whoosh at a third of mid and high cuts, impact and a riser that ends on the drop, hiss on half of the phrase boundaries, a click per caption word, clicks on half of the intro cuts.

## Recipe in engine terms

style.json in this folder holds all of it: structure (intro 5 beats, outro 4, drop at 45 per cent of the edit, voiceover start beat 6), cuts.lengths per section role, the grade timeline, moves (slow_zoom, flash, invert, zoom_blur, rgb_split, shake, mask_flash, tile), sfx and captions (kind staircase, timing mode grid or the voiceover's own word times).

```
edits/.venv/bin/python edits/engine/make_edit.py --style bw-flash-vo \
  --clips ./footage --music ./song.mp3 --voiceover ./vo.wav --aspect 16:9 --duration 16 --out ./out
```

Without --voiceover pass --captions "line one\nline two with a *key* word" and the words land one per half beat from beat 6. The voiceover is transcribed with the local Whisper model (word timestamps) and mixed over the music with ducking. --aspect 9:16 crops each clip around its detected face or focus point.

## Generalisation

Two renders from different inputs live in demo/ (reproduce with the commands in demo/A/edl.json's header fields: style, seed, music window). Both use self-generated footage and music, a text-to-speech voiceover from macOS say, and the numbers below come from check.py (cuts detected in the rendered video against the known beat grid of the synthesised song).

| Run | Song | Clips | Aspect | Shots | Cut offset from the true sixteenth grid, mean (planned) | One frame |
| --- | --- | --- | --- | --- | --- | --- |
| A | house, 128 BPM | set A, 16:9 | 16:9 | 55 | 11.3 ms (8.0 ms planned) | 33.3 ms |
| B | hip-hop, 100 BPM | set B, 9:16 | 9:16 | 44 | 10.2 ms (6.2 ms planned) | 33.3 ms |

Cuts therefore land within a third of a frame of the new beat grid on average, the residual being frame quantisation at 30 fps and detection noise. 52 of 54 and 41 of 43 planned cuts were found in the video, the rest are hidden under flashes. In both runs the black and white to colour to black and white arc, the staircase captions, the flash density and the voiceover pacing are recognisable from the contact sheets (demo/contact-A.png, demo/contact-B.png).

## What the engine does not capture

- The creator's actual B-roll, which is footage about editing (colour wheels, scopes, timeline screens). The engine takes whatever clips it is given.
- The AI-generated shots and the match cut between seasons. The engine can only repeat the clip you give it, so the match cut is replaced by an ordinary cut with a zoom blur.
- The x-ray skull overlay and the exact cyan and red chromatic text split on CONSCIOUSNESS (the staircase caption has an emph_split option that draws a cyan and red ghost, off by default).
- The masking flash needs a person in the clip. It uses Apple Vision person segmentation on macOS and falls back to a plain flash when no person is found (the synthetic test clips contain none, so the demos show a flash).
- Sound effects are synthesised (sfx.py), not the creator's samples, so the character of the whooshes and impacts is similar but not identical.

## When to use it

Explainers, trailers and hooks that need to feel like an editor's reel in the first 15 seconds: a short voiceover claim over a fast montage, with a visible turn from monochrome to colour at the answer. It suits vertical and horizontal formats, fast moving B-roll and clips under 5 s. It hurts for calm brand films, anything needing legible subtitles faster than 3 words per second, and viewers sensitive to flashing, because the montage section has a white frame every 0.2 to 0.3 s. Limit flash density with the flash probabilities in style.json when photosensitivity matters.

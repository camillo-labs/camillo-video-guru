# kinetic-card-explainer (also: one-idea scene cards, word-by-word explainer, mascot explainer, repo promo short)

Source: @alekseitalksai, a 31.2 s vertical promo for OpenMontage, a GitHub repo of about 66k stars that turns Claude Code into a video production studio (720x1280, 30 fps), received by AirDrop on 12 October 2026. The raw measurements are in analysis.json and the transcript is in `../techniques-2026-10-12.md`. The source clip is not redistributed (a copy sits in `_source/`, which is gitignored).

## What it looks like

Twenty hard-cut scenes, each about 1.4 s, each one idea. The scenes sit on flat colours that alternate dark (`#0E0B11`), light grey (`#E8E8E8`), beige (`#E7E3D8`) and, once, terracotta (`#C87359`). Each holds a small diagram in the upper half: an orange pixel mascot, round icons joined to it by arrows that draw themselves, pills that spring in ("research", "voice", "final cut"), a README card, a terminal, a timeline, a waveform. The mascot is in nearly every scene, so the viewer follows one character through the explanation.

Under the diagram, at 70 percent of the height, one or two bold words at a time appear in a clean sans. A noun every few chunks switches to an italic serif in sky blue ("the *research*", "the *footage*", "builds *yours*"). Twice the edit cuts to the talker full frame, and there the words become a serif italic in white with the closing words in bold pale blue. It opens with a split (a card over the talker's face) and ends with a split again, then a "comment MONTAGE" card and a four-second dim.

## What makes it work

- One scene per idea, one idea per phrase. Scene length median 1.37 s and the cut lands on a word start (median 0.05 s), so the picture changes exactly when the thought does.
- The text and the diagram never fight for the same place. The diagram owns the upper 60 percent, the words own one line at 70 percent, and the line is short enough (one or two words) that it reads before the cut.
- Flat colour changes do the rhythm. Dark, light, dark, light is a visible pulse every 1.4 s without any transition effect. All 20 cuts are hard single-frame cuts.
- Motion is spring motion. Pills and the mascot overshoot and settle, arrows draw along their length, bars move. Nothing slides at a constant speed, so a 1.4 s scene still feels alive for its whole length.
- A single accent. Sky blue is used for the noun in the caption, the pill that names the answer and the keyword on the end card, so the eye learns where the point is.
- Two talker cut-ins break the pattern and prove there is a person behind it. Both are 1.6 s or less, and both come right after a stack of diagrams.
- The audio is the voice and nothing else: -13.6 LUFS, loudness range 3.0 LU, no music, no sound effects.

## Measured facts

- 20 shots in 31.2 s: 1.43, 1.87, 2.0, 1.27, 1.86, 1.37, 0.83, 1.6, 1.07, 1.17, 1.6, 1.3, 1.5, 1.23, 0.93, 1.7, 1.24, 1.26, 1.94, then the 4.03 s dim. Median 1.37 s, mean 1.43 s (of the first 19).
- Cuts: 19 hard single-frame cuts, one three-frame cut (17.37 s). Median distance from a cut to the nearest word start 0.05 s.
- Palette (sampled): dark `#0E0B11`, light `#E8E8E8`, beige `#E7E3D8`, terracotta `#C87359`. Ink on dark `#FBF8FD`, ink on light `#0F0F11`. Caption accent `#3BADDD`, keyword blue `#26B2F1`, mascot orange about `#DE7050`.
- Caption: baseline band y 881 to 915 of 1280 (centre 70 percent), text height 34 px (bold sans about 47 px at 720 wide), accent serif about 1.17 times larger. In the split the caption moves up to 43 percent, just above the head picture.
- Word rate 3.6 a second (95 words in 26.7 s). Caption chunks of 1 to 2 words, hard swaps, median offset from the Whisper word start 0.04 s.
- End: split with the head from 23.97 s, card from 25.23 s, dim to 25 percent from 27.17 s to the end (4.03 s).
- Audio: -13.6 LUFS integrated, true peak 0.0 dBFS, speech RMS -19.1 dB, digital silence between phrases, 2 non-speech onsets at the very end.

## Shot by shot

Times in seconds.

| # | In | Out | Background and scene | Caption |
|---|----|-----|----------------------|---------|
| 1 | 0.00 | 1.43 | split: dark GitHub card over the talker | Sixty five / thousand stars (at 43 percent) |
| 2 | 1.43 | 3.30 | dark: stat pill "65,896 stars", logo, arrow draws to the mascot | for / a repo / that / turns *Claude* |
| 3 | 3.30 | 5.30 | light: README card with a highlight bar growing across "full video production studio", mascot row | into / a full / video *studio* |
| 4 | 5.30 | 6.57 | terracotta: white mascot over a logo card | It's called / OpenMontage |
| 5 | 6.57 | 8.43 | dark: terminal card, the command types in | You describe / the video / in plain / words |
| 6 | 8.43 | 9.80 | light: three source icons, arrows draw to the mascot, "research" pill | agent does / the *research* |
| 7 | 9.80 | 10.63 | dark: script card | writes / the script |
| 8 | 10.63 | 12.23 | beige: free-stock icon, paid-API pills, two rotated stills | or generates / the *footage* |
| 9 | 12.23 | 13.30 | dark: "voice" and "music" pills with waveforms | adds voice / and music |
| 10 | 13.30 | 14.47 | light: five pills converge to a "final cut" pill, a tick | and / edits the / final *cut* |
| 11 | 14.47 | 16.07 | talker cut-in, full frame | or paste a Reel (serif italic) / you love (bold pale blue) |
| 12 | 16.07 | 17.37 | light: row of six small cards, timeline ruler with labelled spans | It breaks / down / the *pacing* |
| 13 | 17.37 | 18.87 | dark: doc card, highlight over "scenes, keyframes, and style" | scenes and / the style |
| 14 | 18.87 | 20.10 | beige: ruler, "yours" pill, bars in two colours, mascot | then / builds *yours* / from that |
| 15 | 20.10 | 21.03 | talker cut-in | the demos / on the repo |
| 16 | 21.03 | 22.73 | light: rocket-launch still on a card, "Veo-generated clips" pill | include / a sci-fi / and a *trailer* |
| 17 | 22.73 | 23.97 | dark: banana still, "6 Kling clips" pill | Pixar-style / short |
| 18 | 23.97 | 25.23 | light split: "comment" and MONTAGE over the talker | none |
| 19 | 25.23 | 27.17 | light: "and I'll send you the link", "and a setup guide", a setup card rising | none |
| 20 | 27.17 | 31.20 | the same card dimmed to 25 percent | none |

## Caption rules

- One or two words at a time, hard swap on the first word's start (median 0.04 s from the Whisper word start), no animation, no fade, no scale. A chunk closes after two words or after the accent word, whichever comes first.
- Plain words: bold grotesk (Inter Tight 700 in the engine), 6.5 percent of the width, centred at 70 percent of the height. Ink follows the background: `#FBF8FD` on dark and terracotta, `#0F0F11` on light and beige.
- Accent word: italic Didone serif (Playfair Display Italic in the engine), 1.17 times the plain size, sky blue `#3BADDD`. About one chunk in four carries one, always a noun or the answer word. The engine marks a word as an accent when it has six letters or more and is not a stop word, or when it is `*starred*` in the captions file.
- Split scenes: the caption sits at 43 percent, between the card and the head picture.
- Talker cut-ins: serif italic white, two lines at most, built up through the phrase, with the closing words in bold pale blue (`#A0E0FF`) and a soft shadow. Centred at 69 percent.
- The end card has its own typography: "comment" in black serif italic, the keyword in 800 weight italic serif at 0.9 of the width, "and I'll send you the link" in italic, "and a setup guide" in bold sans. The row of captions stops 7.2 s before the end.

## Overlays

- Scenes: each shot repaints the whole frame with its background and its diagram, so there are no layers of footage under a scene. The talker footage shows through only in the split (below 47 percent, with a soft 3 percent gradient edge) and in the cut-ins.
- Mascot: an orange pixel creature, white on terracotta, with two cut-out eyes. The engine draws an original eleven by eight block creature, not the source's character.
- Pills (dark, white, blue, outline, grey), round icons, arrows with a start dot and an arrow head that draw over 0.3 s, rotated stills, a setup card with a soft shadow.
- The Instagram glyph and @handle in the corners are platform overlays, not part of the style.

## Colour grade

None on the footage. The talker is a warm, low-light phone shot. The style's colour is entirely the flat backgrounds and the sky-blue accent.

## Recipe (ffmpeg and engine terms)

1. Write the script as one idea per phrase, about 3.5 words a second. Record the voice, or the talker, and transcribe for word times.
2. Plan one scene per phrase, 1.2 to 2 s, with cuts on the first word of the phrase. Alternate dark and light backgrounds, use beige and terracotta once or twice, and drop in a talker cut-in after every five or six scenes.
3. Build each scene from the mascot, two to four pills or icons, arrows from the sources to the mascot and one blue pill for the answer. Spring each element in with 0.1 s staggers (damping 0.55, 24 rad/s). Scene motion ends within 1 s so the last half second is calm.
4. Captions: 1 to 2 words, bold sans at 70 percent, a blue italic serif for the noun. White serif italic over the talker.
5. Finish with the split (keyword over the talker), a card, and a dim for the platform end screen.
6. Master at -14 LUFS with no music.

## When to use it

- Explaining a tool, a repo, a workflow or an idea that can be drawn as boxes and arrows. Product and developer promos, "how it works" shorts.
- Anything where the script already has one idea per phrase.

## When it hurts

- Ideas that cannot be drawn. Each scene needs a picture, and a long abstract argument leaves empty diagrams.
- Long scripts. 20 scenes in 30 s is tiring past a minute, so vary the pace or add a longer scene.
- Brand-sensitive material. The scene generator makes generic stand-ins. Real logos and product shots need cleared assets.

## Needs engine support (met by the engine, see the Engine section)

- Whole-frame scene painting with a split mode that keeps the talker below (`kc_scene`), eight scene templates, a pixel mascot, pills, icons, arrows, waveforms and cards, all moving with closed-form springs (`ext.typeset.spring`).
- One or two word chunks with an accent word and a background-aware ink, plus a stacked serif treatment for the talker cut-ins (`kc_word`).
- An end card with a keyword and a dim (`kc_end`).
- Cuts snapped to word starts (`cuts.snap_words`, in `make_edit.py`) and a voice-only mix (`audio.music_gain` 0).
- Bundled faces: Inter Tight (existing), Playfair Display and Instrument Serif (SIL OFL 1.1).

## Engine

```
edits/.venv/bin/python edits/engine/make_edit.py --style kinetic-card-explainer \
  --clips ./footage --music ./any-song.wav --voiceover ./voice.wav \
  --duration 31 --aspect 9:16 --res 720 --out ./out
```

--clips is the talker (used in the split and the cut-ins), --music gives the beat grid only, --voiceover is transcribed locally for the captions and cuts. The scene order is the `sequence` list on the `kc_scene` move in style.json: each entry is `{bg, scene, head, labels, name, tag, stat, command, lines, highlight, pill, tint}`. Without `labels` the pills use the longer words spoken during the shot.

| Parameter | Meaning | Measured value |
|-----------|---------|----------------|
| cuts.lengths.default | shot length in beats (1.4 s at 128 BPM is 3 beats) | 3, 2 and 4 weighted 5, 3, 2 |
| cuts.snap_words.tol, min_len | each cut moves to the nearest word start within tol seconds | 0.3, 0.8 |
| moves kc_scene.sequence | scene specs cycled by shot index. bg dark, light, beige, terra. scene hub, doc, terminal, chips, timeline, media, stat, logo, none. head none, split, full | 17 specs in source order |
| moves kc_scene.split_y | where the head picture starts in a split | 0.47 |
| captions.size_frac, y, y_split, y_head | plain word size, caption row, row in a split, row over the talker, as shares of width and height | 0.07, 0.70, 0.435, 0.69 |
| captions.max_words, accent_min_len, accent | words per chunk, shortest accent word, accent colour | 2, 6, 59 173 221 |
| captions.stop_before_end_s | captions stop before the end card | 7.2 |
| overlays kc_end | keyword, pre, lines, split_s, card_s, dim_s, dim | MONTAGE, comment, 1.26, 1.94, 4.03, 0.75 |

The code is in engine/ext/kinetic_card.py with shared helpers in engine/ext/typeset.py. `typeset.spring(t, zeta, omega)` is the closed-form damped spring (underdamped, critical and overdamped branches), so every frame is a pure function of time.

## Generalisation

demo/demo-house128.mp4 (31 s, 540x960): a synthesised voice (macOS `say`, script in demo/voiceover.txt, written for the demo), the synthetic dancing-figure clip as the talker, the 128 BPM house test track as a muted beat grid. 21 shots with a median of 1.43 s (source 1.37 s), 13 cuts moved to word starts, the dark and light alternation, the talker cut-ins, the split at the start and end, the end card with the dim. demo/vs-source.png (kept out of the repository because it holds frames of the source video, regenerate it with tools/framegrid.py and the clip in _source/) puts frames of the source over frames of the render and demo/demo-house128.sheet.png is a contact sheet.

Reproduce:

```
cd edits
mkdir -p _testdata/clips/head_9x16 && ln -sf ../A_9x16/figure.mp4 _testdata/clips/head_9x16/figure.mp4
say -v Daniel -r 190 -o _testdata/vo/kc_demo.aiff "$(tail -n +3 kinetic-card-explainer/demo/voiceover.txt)"
.venv/bin/python engine/make_edit.py --style kinetic-card-explainer --clips _testdata/clips/head_9x16 --music _testdata/music/house128.wav --voiceover _testdata/vo/kc_demo.aiff --duration 31 --aspect 9:16 --res 540 --out /tmp/demoKC
```

Run engine/make_testdata.sh first if edits/_testdata is missing. One render takes 22 s, peak 0.95 GB resident during the Whisper pass and 0.56 GB for the render.

## What the engine does not capture

- The scene content. The source scenes show real things: a GitHub page, Hacker News, Reddit, tool logos, real stills from generated videos, a README with a live highlight. The engine draws generic stand-ins (play button, letter tile, speech bubble, a dark gradient still). The mascot is an original eleven by eight pixel creature.
- Scenes do not follow the script. The sequence is a fixed list cycled by shot number, and only the pill labels come from the speech. In the source each scene was built for its phrase.
- Motion detail. The source's arrows have curved heads and bouncing end dots, the stills tilt in 3D as they rise, the README highlight sweeps and the waveform bars respond to the voice. The engine springs scale and draws arrows progressively but has no per-element curves.
- The three-frame cut at 17.37 s and the teal card flash before it.
- The source mascot clapperboard on the terracotta card and the pixel-mascot blink.
- Type: the caption sans is Inter Tight (the source looks like Inter or SF Pro Bold) and the serif is Playfair Display Italic (a close match for the source accent and the keyword).
- Word times and spellings come from Whisper, which mishears names and splits hyphenated words. Pass a corrected captions file with SRT times for a published cut.
- Beat alignment. Cuts follow the speech, so check.json reports them as off-beat (the planned cuts sit 21 ms from a sixteenth on average in this demo, against 9 ms before snapping). That is intended for this style.
- Platform overlays (the Instagram glyph and handle).

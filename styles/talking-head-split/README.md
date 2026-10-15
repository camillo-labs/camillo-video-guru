# talking-head-split (also: talker with inset screen captures, serif caption chunks, explainer reel, how-to short)

Source: @raycfu, "How to do motion design with Claude Opus 5.5", a 58.7 s vertical phone video (720x1280, 30 fps), received by AirDrop on 12 October 2026. The raw measurements are in analysis.json and the transcript is in `../techniques-2026-10-12.md`. The source clip is not redistributed (a copy sits in `_source/`, which is gitignored).

## What it looks like

One person talks to camera in one continuous take. The edit never leaves them. It is built from four layers that run on their own clocks:

- The talker fills the frame and is reframed by hard jump cuts between a wide shot (a standing figure, small, low in the frame) and a close shot (head and shoulders, about 1.7 times bigger). The reframe happens at sentence boundaries, every 4.5 s in the middle.
- A 16:9 card sits in the upper third of the frame, from 4.4 s to 49 s (76 percent of the runtime). It is a real screen recording, a product site or a chat UI, and it hard-cuts to the next capture every 1.7 s, in a burst of 0.2 s cuts at the start (4.4 to 9.3 s). A tool logo floats above the card when a tool is named.
- Two-line serif caption chunks sit in the lower third and swap with the speech, about one chunk a second.
- A white title with two gold runs opens the video on the empty upper third and leaves on the cut that brings the first card.

The last 4 s are dimmed to a quarter of the brightness for the platform's end screen.

## What makes it work

- The top half and the bottom half carry different jobs. The face stays at the bottom, so the viewer never loses the speaker, and the proof for each claim arrives above it. A claim is never made without something to look at.
- The cuts follow the speech. The head reframes land within 0.02 s of a word start (median of 11 cuts), not on a beat grid. A new sentence is a new framing, so one camera feels like two.
- The card changes faster than the talker. Median head shot 4.5 s against a median card of 1.1 s (burst 0.23 s). The picture moves all the time and the voice never has to.
- Captions are phrase chunks, not words. Median chunk 1.1 s and 5.6 words, with onsets on the first word of the chunk (median offset 0.00 s, range -0.17 to +0.23 s). They are big (64 px at 720 wide), two lines at most, in a tight serif with a soft shadow, so they read in a glance over a busy room.
- Gold is spent once, on the title. Every other pixel of colour comes from the footage and the cards.
- The audio is the voice and nothing else: -13.9 LUFS integrated, loudness range 2.5 LU, no music bed, no sound effects.

## Measured facts

- Cuts: all hard and one frame long. 12 reframes in 58.7 s (medians 4.48 s, mean 4.56 s, range 1.67 to 7.6 s) plus 27 card events.
- Head shot lengths in seconds: 4.43, 3.2, 1.67, 2.2, 7.5, 4.87, 6.83, 2.23, 4.54, 3.86, 5.77, 7.6, then the 4.0 s end screen.
- Caption position: first line top at 938 px (73.3 percent of the height), second line top at about 1002 px, line pitch 64 px (8.9 percent of the width), widest line 82 percent of the width, centred. Captions sit over the lower body and desk, and the card never reaches them.
- Card rectangle: x 65 to 654, y 291 to 622 (x 0.09, y 0.227, width 0.82, 16:9), square corners, no shadow, no border.
- Title: x 60 px (8.3 percent), top 330 px, three lines at an 82 px pitch, bold serif, white with `#F0C815` gold on "motion design" and "Claude Opus 5.5".
- Speech: 269 words in 54.5 s (4.9 words a second), Whisper large-v3-turbo.
- Audio: -13.9 LUFS, true peak 0.1 dBFS, speech RMS -18.4 dB, gaps fall to digital silence. 4 non-speech onsets in the whole file, all at the end.

## Shot by shot

Times in seconds. "Card" is the 16:9 inset.

| # | In | Out | Framing | Card | Caption (first words) |
|---|----|-----|---------|------|------------------------|
| 1 | 0.00 | 4.43 | wide | none, title on screen | most people don't realize that the insane AI |
| 2 | 4.43 | 7.63 | close | burst of five captures, 0.2 to 1 s each (ant illustration, orange poster, price card) | it's rather a studio that you set up once |
| 3 | 7.63 | 9.30 | wide | five 0.1 to 0.3 s flashes (MOTION, CLAUDE title cards) | here's exactly how you build it |
| 4 | 9.30 | 11.50 | close | white chat UI, 2.2 s | start by building the headless render engine loop system |
| 5 | 11.50 | 19.00 | wide | dark swoosh clip, install code, Playwright and FFmpeg sites, 1.5 to 3 s each | you have to understand that Claude does not make a video |
| 6 | 19.00 | 23.87 | close | chat UI and capture bar | the Playwright browser captures every frame |
| 7 | 23.87 | 30.70 | wide | reference sites (orange, purple, cyber tech, 1.5 to 2 s each) | then you need to give it a reference and real assets |
| 8 | 30.70 | 32.93 | close | chat UI with spring chart | make sure to enforce real spring physics and audio |
| 9 | 32.93 | 37.47 | wide | CSS banned card, spring card | ban basic CSS |
| 10 | 37.47 | 41.33 | close | beat-lock card, then a dark clip | tell it to synthesize the sound and code |
| 11 | 41.33 | 47.10 | wide | dead-frame report, scored bar charts | you make Claude watch its own frames and critique them |
| 12 | 47.10 | 54.70 | close | none after 48.97 | I created a step-by-step guide to build this out |
| 13 | 54.70 | 58.70 | close, dimmed to 25 percent | none | follow for ways to make money (platform end screen) |

## Caption rules

- Phrase chunks, hard swap, no fade, no slide, no scale, no word-by-word highlight. A chunk appears on the first word's start (median 0.00 s from the Whisper word start) and stays until the next chunk. The row never empties between sentences, so the last chunk holds until the next one begins.
- Two lines at most, about 25 characters a line, centred, 8 words at most. A chunk breaks where the second line would overflow 82 percent of the width, or at a pause in the speech (gap above 0.45 s).
- Font: a high-contrast condensed Didone serif (Ivy Presto Display or Canela class). The engine uses Playfair Display at weight 600 and tracking -0.035 em, size 8.8 percent of the width, line pitch 8.9 percent of the width. Nearest installed or bundled alternatives: Playfair Display (bundled, OFL), Bodoni 72 and Didot (macOS), Instrument Serif (bundled, narrower and lighter).
- Colour: white, soft black shadow 3 px down with 6 px blur at 60 percent. No stroke, no plate, no scrim.
- Position: lower third, first line top at 73.3 percent of the height. Fixed for the whole video, the head framing changes under it.

## Overlays

- Title hook: three lines, the second and third in gold on the key phrases. On from frame 0 until the first card, which hard-cuts it away.
- Card: 16:9, x 9 percent, y 22.7 percent, width 82 percent. A slow push of about 3 percent over each card's life gives static captures some motion. Real screenshots and recordings in the source, six generated stand-ins in the engine.
- Tool logo above the card when a tool is named (FFmpeg, Playwright). Not in the engine.
- The Instagram glyph and @handle drifting in the corners belong to the platform export, not to the style.
- End screen: the last 4 s at 25 percent brightness, a platform feature.

## Colour grade

None. The footage is natural phone video in a grey room, and the grade is the camera's. The only colours the style adds are the gold (`#F0C815`) in the title and whatever the cards bring.

## Recipe (ffmpeg and engine terms)

1. Record one continuous take, vertical, 720x1280 or better. Transcribe it for word times.
2. Cut the take into 3 to 8 s shots at sentence starts, with each cut within 0.05 s of the first word of a sentence. Alternate a wide framing with a 1.7x punch-in around (0.5, 0.62).
3. Make or collect one 16:9 capture per claim. Place them in the card rectangle from the first claim (about 8 percent into the video) to about 9 s before the end. Use 0.2 to 0.7 s cuts for the first 5 s, then 1.2 to 3.2 s.
4. Group the transcript into chunks of up to two lines (82 percent width), break on pauses, and swap on the chunk's first word.
5. Title: three lines, gold runs on the topic, until the first card.
6. Master at -14 LUFS with no music. Add a 4 s dimmed tail if the platform needs an end card.

## When to use it

- Explainers, tutorials, product tips and "how I do X" shorts where one person talks and every claim has something to show.
- Content that must read with the sound off. The captions carry the whole script.

## When it hurts

- A speaker with no screen material to show. The card stays empty and the layout looks half done.
- Fast music edits. The cuts follow sentences, so the style feels slow next to a beat-led cut.
- Long videos. Two framings and one caption face wear thin after two or three minutes without a third visual idea.

## Needs engine support (met by the engine, see the Engine section)

- Phrase-chunk captions in a serif with a soft shadow (`serif_chunk`) and word times from Whisper (`--voiceover`).
- A title overlay with highlight runs (`th_title`), an inset card layer that cuts on a schedule and takes real captures from a folder (`th_cards`), a dim for the end screen (`th_outro`).
- A static punch-in effect (`th_zoom`) placed on alternate shots.
- Cuts snapped to word starts (`cuts.snap_words`, in `make_edit.py`) and a style-level audio mix (`audio.music_gain` 0 for voice only).
- A bundled serif: Playfair Display and Instrument Serif, SIL OFL 1.1 (engine/assets/fonts).

## Engine

```
edits/.venv/bin/python edits/engine/make_edit.py --style talking-head-split \
  --clips ./footage --music ./any-song.wav --voiceover ./voice.wav \
  --duration 36 --aspect 9:16 --res 720 --out ./out
```

--clips is the talker (any long vertical take, one file is enough). --music is used only for its beat grid, because `audio.music_gain` is 0, so any track works. --voiceover is transcribed with local Whisper (about 12 s, 0.9 GB peak) for the captions and the cut points. Put real screen captures in a folder and set `cards_dir` on the `th_cards` overlay, the generated cards are stand-ins.

| Parameter | Meaning | Measured value |
|-----------|---------|----------------|
| cuts.lengths.default, first_shot_beats | shot length in beats (about 4.5 s at 128 BPM is 9.6 beats), weighted | 7, 9, 12, 14 and a first shot of 9 |
| cuts.snap_words.tol, min_len | each cut moves to the nearest word start within tol seconds | 0.45, 1.5 |
| moves th_zoom | static punch-in on every second shot, cx cy is the zoom centre | scale 1.7, cy 0.62 |
| captions.size_frac, tracking, line_pitch | serif size, letter spacing in em, line pitch, as shares of the width | 0.088, -0.035, 0.089 |
| captions.y, max_width, max_lines, max_words | top of the first line, widest line, lines per chunk, words per chunk | 0.733, 0.82, 2, 8 |
| captions.shadow | dx, dy, blur px, alpha | 0, 3, 6, 0.6 |
| overlays th_title | lines of runs with hi flags, gold colour, on time | until 4.43 s, gold 240 200 21 |
| overlays th_cards | start_s, end_before_end_s, burst_s, burst_len, len, push, kinds, cards_dir, texts | 4.43, 9.7, 4.9, [0.3, 0.7], [1.2, 3.2], 0.03 |
| overlays th_outro | seconds, dim | 4.0, 0.75 |

The code is in engine/ext/talking_split.py with shared helpers in engine/ext/typeset.py. The snap function is in engine/make_edit.py.

## Generalisation

demo/demo-house128.mp4 (36 s, 540x960): the engine's synthetic dancing-figure clip as the talker, a synthesised voice (macOS `say`, script in demo/voiceover.txt, written for the demo), the 128 BPM house test track as the beat grid with the music muted. Seven shots, median 4.27 s (source 4.48 s), cuts within 14 ms of a word start, the card burst from 4.4 s, the title gone on the first card, the captions in two lines at 73 percent, the last 4 s dimmed. demo/vs-source.png (kept out of the repository because it holds frames of the source video, regenerate it with tools/framegrid.py and the clip in _source/) puts frames of the source over frames of the render. demo/demo-house128.sheet.png is a contact sheet.

Reproduce:

```
cd edits
mkdir -p _testdata/clips/head_9x16 && ln -sf ../A_9x16/figure.mp4 _testdata/clips/head_9x16/figure.mp4
say -v Daniel -r 185 -o _testdata/vo/th_demo.aiff "$(tail -n +3 talking-head-split/demo/voiceover.txt)"
.venv/bin/python engine/make_edit.py --style talking-head-split --clips _testdata/clips/head_9x16 --music _testdata/music/house128.wav --voiceover _testdata/vo/th_demo.aiff --duration 36 --aspect 9:16 --res 540 --out /tmp/demoTH
```

Run engine/make_testdata.sh first if edits/_testdata is missing. One render takes 45 s and the Whisper pass peaks at 0.95 GB resident, the render itself at 0.5 GB.

## What the engine does not capture

- The talker. The demo uses a synthetic figure. A real take brings its own wide and close framing, and the 1.7x punch-in is a digital crop of one take, not a second camera.
- Real captures. The generated cards (chat UI, price, title, poster, code, score chart) are stand-ins with no motion inside. The source cards are screen recordings of real sites with scrolling, typing and hover. Put recordings in `cards_dir` for the real thing.
- Tool logos above the card, and the card content being chosen to match what the speaker says at that moment. Card order is random with the measured length distribution.
- The exact serif. The source face is a tighter Didone than Playfair Display. "most people don't realize" measures 570 px in the source and 664 px in Playfair at the same height (16 percent wider), so engine lines hold about 21 characters against the source's 25 and chunks wrap sooner.
- The speaker-side details: a wide shot with the standing figure walking in, hand gestures timed to chunk changes.
- Caption words come from Whisper and carry its mistakes ("startups" heard as "start to start", "closed-form" as "close-form"). Pass a corrected --captions file with SRT times to fix them.
- Platform overlays (the Instagram glyph and handle) and the platform end screen are not reproduced beyond the dim.
- Beat alignment. Cuts follow the speech, so the beat-grid check in check.json reports them as off-beat (mean 44 ms from a sixteenth in the demo). That is intended for this style.

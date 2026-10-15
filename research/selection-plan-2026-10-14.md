# Selection plan: making the edit engine choose its own ingredients

Captured 14 October 2026. Reads the engine as it stands (make_edit.py, plan.py, clips.py, sfx_library.py, the six styles, the three real-footage tests) and adds web research from 2025 and 2026 sources.

## Bottom line

Today the caller hand-picks the style, the track, the music window, the captions, the aspect and the length, so the engine is a good renderer with no judgement in front of it: add a brief and footage reader that scores the six styles, a cleared-music library that is searched by tempo, drop position and energy curve, a cleared sound effect set with a density policy, a caption and safe-area rule set, and a hook, loop and end card block, all written to a decisions.json so every choice can be checked.

## What the engine decides now, and what the caller passes in by hand

Decided inside the engine:

- The song window. plan.pick_window starts on a downbeat and places the first drop at the style's `drop_at` fraction, ends on a bar.
- Cut lengths per section role (intro, low, mid, high, drop, outro) from the style's weighted tables, snapped to phrases and the sixteenth grid, or to word starts for the two voice styles.
- Which clip goes in which shot (motion energy matched to song energy, repeat penalties) and the crop around the focus point (Vision faces, person mask, saliency).
- Camera moves, transitions, flashes, speed ramps, sound effect events, grade keyframes and caption timing, all from the style's rules.
- Beat analysis of the song and the post-render beat check.

Passed in by hand every time (make_edit.py has no default for any of these except aspect and duration, which come from the style):

- `--style`, required. Nothing reads the brief or the footage to choose it.
- `--music`, required, and `--music-start` when the automatic window is wrong. Green Label reused Raving Energy although its only drop is too early in the song to move, and Dachshunds reused the same track, so track choice is a manual habit, not a decision.
- `--clips`, a folder Cam has already curated. The engine never rejects a clip as unsuitable for the style. Fontainebleau needed a hand-built `work/clips` folder of numbered links to force the order.
- `--captions`, written and fact-checked by hand, with `*word*` marking emphasis. The engine does not decide how many lines the length allows.
- `--duration` and `--aspect` when the style default is wrong, `--voiceover` and `--vo-start-beats`, `--seed` as the only way to get a different plan.
- Everything that is a style variant: each test copied a style.json and edited it by hand (Green Label halved the flash density and set a sand emphasis colour, Fontainebleau removed the sticker and strobe and added a dark caption band). Variants are the right mechanism but nothing chooses them.
- Hook, loop seam and end card exist only as per-style keys (`loop_seam_beats` in lyric-word-beat, a dim end in talking-head-split, `logo_card.py`), not as decisions made per brief.

What clips.py already measures and can feed a chooser: width and height, duration, scene cuts, mean motion, brightness, saturation, sharpness, a focus point and a boolean face flag. What it does not measure: face count and face size, person count, whether the clip has speech, whether it is a screen capture, and how many different subjects the set contains.

## 1. Style choice

### Rule

Extract these features, then apply the ordered rules. Each rule returns a score, the highest score wins, and a margin under 0.15 or a best score under 0.5 returns "no fit" and logs which gap it hit.

Features from the footage (clips.py additions marked new): clip count, total footage seconds, share of stills, share of clips that are screen captures (new: 16:9 or 9:16 with near-zero motion, high edge density from text and flat colour regions), face count and largest face area per clip (new), share of footage with a large face (area at least 8 percent of frame), speech present in clip audio (new, ffmpeg silencedetect or a Whisper voice activity pass), mean motion, mean saturation, mean luma, number of distinct subjects (new, cluster the Vision person masks or saliency crops).

Features from the brief: voiceover supplied or not, caption text kind (lyric or slogan under 6 words per line, facts of 6 to 14 words, numbered steps, a how-to), target length, target aspect, mood word (energetic, dark, playful, calm, heritage, premium), and the audience (see section 4).

Rules, in order:

1. Talker on camera. Speech in the clips, a large face in at least 60 percent of footage seconds, and at least 3 screen captures or cards available: **talking-head-split**. A talker with no captures is a gap (below).
2. Voiceover supplied and no on-camera talker.
   - Mostly cards, screenshots or no footage, or the caption kind is steps or a tool or workflow: **kinetic-card-explainer** (it draws boxes and arrows, so it needs a content shape that can be drawn).
   - At least 8 real b-roll clips and the brief is a claim with a turn (problem, then answer): **bw-flash-vo** (the mono to colour turn is the story).
3. No voiceover, music-led.
   - Captions are a lyric or slogan, or stills share is above 40 percent, or mean motion is low, or the aspect is 16:9, or the mood is calm or heritage: **lyric-word-beat**. Fontainebleau and Dachshunds are this case.
   - A single clear subject (one distinct subject in at least 70 percent of footage seconds, Vision mask success on at least 80 percent of sampled frames) and clips of 5 seconds or more: **hud-lyric-heat** when mean saturation is at least 0.35 and mean luma under 0.6, **hud-lyric-light** when luma is at least 0.6 or saturation under 0.25. The Dachshunds HUD cut is this case.
   - Several subjects or many short high-motion clips, facts as captions, and an energetic, dark or edgy mood: **bw-flash-vo** without a voiceover. Green Label is this case.
4. Tie-breaks: prefer the style whose `defaults.aspect` equals the requested aspect, then the style with the closer default duration (bw 16 s, lyric 17 s, hud 16 s, talking-head 30 s, kinetic-card 31 s), then lyric-word-beat as the safest renderer.

The two voice-led styles ignore the beat, so the chooser must also set `audio.music_gain` (0 for the sources' voice-only look, or a bed at -18 to -22 dB, see section 2) rather than leave it to the style default.

Evidence for the numbers: the shot-length fingerprints are in each style's README (bw-flash-vo median 0.43 beats, lyric-word-beat 4 to 5 beats, hud one long take with overlays). The thresholds above are starting values and should be tuned by running the chooser over the three real tests and the six demos and checking it returns the style that was used.

### Gaps where none of the six fits

- A talker with no screen captures (a plain to-camera clip, an interview, a testimonial). talking-head-split's upper-third card would be empty.
- Natural-sound b-roll with a music bed and no captions to speak of (a vlog, a day in the life, a travel recap). bw-flash-vo is too aggressive, lyric-word-beat needs words.
- A single hero subject with speed changes (gym, car, sport, dance), the velocity edit.
- Two simultaneous pictures (a story over looping gameplay or satisfying footage).
- A product demo with a hook, proof and a call to action, and still image sets that want a strobe of stills against black.
- 1:1 and long 16:9 output. The styles are learned in 9:16 or 16:9 only.

### Up to three new styles worth learning next

Each copies a format that is popular now. Cam would supply one reference reel per format, the same way the six were learned, and the engine would measure it.

1. **velocity-ramp-edit**, the CapCut "velocity edit". A speed-ramp edit where a clip runs fast, slows to near freeze on the beat, then snaps fast again, usually on gym, car, attitude and anime-style footage over phonk or hard-hitting tracks, using the CapCut velocity and speed-ramp templates (CapCut's own 2026 transitions guide calls velocity "one of the biggest trending CapCut transitions"). It fills the single-hero-subject and music-led gap, and the engine already has `speed.ramps`, so most of the work is measuring ramp curves and beat anchors from a reference. Sources: CapCut best-velocity-templates and transitions guides.
2. **stacked-story-split**. The story-over-gameplay format: a narrated Reddit-style or true-crime story with a karaoke-highlight caption in the lower half and looping high-contrast gameplay or satisfying footage in the other half. One vendor guide calls it "currently the single most viral format in short-form video" and quotes completion above 75 percent, which is a vendor claim, but the format's popularity is not in doubt. It fills the two-pictures gap and needs a new layout (stacked panes), a karaoke caption kind and a gameplay-style background loop, no music-driven cuts.
3. **strobe-photo-dump**, the beat-synced photos against black screens trend. Kapwing lists "in heat black screens" as a Reels and TikTok template that alternates photos or clips with black screens to the beat. It fills the stills gap, a dozen stills each get a one-beat flash against black with a different punch-in, and it reuses the engine's flash, dip_black, strobe and Ken Burns moves, so it is the cheapest of the three.

Ranking by value for Cam's use (brand pieces for Green Label, Emerald and the AI venture): strobe-photo-dump first (stills are what he usually has, small effort), velocity-ramp-edit second, stacked-story-split third.

## 2. Music

### How to pick a track for a brief

Build a track index once (the engine already computes tempo, beat grid, downbeats, energy per beat, roles, drops and phrase boundaries in audio.analyse) and store, per track: bpm, beat clarity, first drop time, drop count, energy per bar, duration, a vocals flag, genre, mood tags, source, licence id and the exact credit string. Then score each track against the brief:

- **Tempo.** Choose the BPM that makes the style's shot length land in its target seconds. Target shot seconds = median shot beats x 60 / bpm. bw-flash-vo (0.43 beats) wants 120 to 130 BPM so cuts sit near 0.2 s, lyric-word-beat (4 to 5 beats) works from 95 to 140 (the source ran at 138.7, Fontainebleau at 95 on strings), the hud pair sit on a 6.1 beat clock at 124 BPM so 118 to 130, the two voice styles do not care. Practitioner ranges: calm content 60 to 80 BPM, energetic 120 to 140, boom bap about 95 to 100, EDM 120 to 150 (beatsyncpro and foximusic guides, vendor sources).
- **Energy curve.** The wanted curve comes from the style: a quiet intro of `intro_beats`, a lift, a drop near `drop_at` x duration, a lull, an outro. Score the track window by how well its per-bar energy matches that curve. The lyric source measured bar loudness 0.11, 0.13, 0.16, 0.245, 0.22, 0.15, 0.115, 0.15, 0.20 (drop at bar 4), a drop-to-pre-drop ratio near 2, so require a ratio of at least 1.5.
- **Drop position.** Reject any track where `drop_time - lead_in` leaves the drop earlier than `drop_at` x duration. This is the Green Label lesson: the track was chosen first, then the window could not be moved. Drops should be chosen before windows, not after.
- **Beat clarity.** Prefer drum-led tracks. Green Label's track had a clear attack on 97 percent of beats (10.5 ms mean offset), Fontainebleau's strings and brass only 47 percent within 25 ms, and the cuts felt looser. Beat clarity at least 0.9 for the flash styles, 0.6 is enough for lyric-word-beat.
- **Genre and mood map.** energetic or edgy: house, hip-hop, phonk, trap. calm or heritage: orchestral, ambient, light acoustic. playful: pop, funk. premium: minimal electronic, cinematic. Instrumental only when a voiceover exists (lyrics compete with narration), and for captioned lyric styles prefer a track with no vocals unless `--transcribe` is on.
- **Length.** The track must contain the whole window plus one bar, and a loop-friendly ending when a loop seam is on.
- **Variety.** Penalise a track used in the last N renders so two tests do not share Raving Energy by habit.

Under a voiceover, set the bed at -18 to -22 dB below the voice, duck 3 to 6 dB when the voice starts and recover between sentences, and finish the mix near -14 LUFS (the figure the short-form platforms normalise to). The sources measured for the voice-only styles were -13.6 and -13.9 LUFS.

### Legally reusable sources, with the terms that matter for published shorts

| Source | Terms | Use in a published short |
| --- | --- | --- |
| Kevin MacLeod, incompetech | Creative Commons Attribution 4.0 for the free licence. Required credit text from the FAQ: "Title Kevin MacLeod (incompetech.com) Licensed under Creative Commons: By Attribution 4.0". Commercial use and monetised YouTube are allowed. Credit must be reasonably discoverable, such as the video description, a profile section or credits. A paid Standard licence removes the credit (the search summary gave $30 for one song, which was not confirmed on the FAQ). | Safe on any platform with the credit in the caption or description. Already used in the tests, keep credits.md. The FAQ points to a separate YouTube Content ID article that was not read. Read it before uploading to YouTube. |
| Free Music Archive | Licence is set per track. The FMA licence guide: CC0 (commercial yes, derivatives yes, no credit), CC BY (commercial yes, derivatives yes, credit), CC BY-SA (commercial yes, derivatives with the same licence), CC BY-NC and BY-NC-SA (no commercial use), CC BY-ND and BY-NC-ND (no derivatives). The guide states that syncing a track to video is a derivative work, so every ND licence rules out a video edit. FMA-Limited is no commercial use and no derivatives. | Filter to CC0 and CC BY only. Skip BY-SA because the share-alike duty on a video that embeds the track is uncertain. Skip anything NC for brand work. |
| Pixabay Music | Pixabay Content Licence. The summary page: use for free, no attribution required (credit appreciated), modify or adapt into new works. Forbidden: selling or distributing the content standalone, using recognisable people or trademarks misleadingly or illegally. The summary says nothing about Content ID. A secondary source reports that some composers have tracks registered in Content ID, so keep the track page and download record. | Usable on any platform without credit. Keep proof of download in credits.md because a claim can arrive after publishing. |
| YouTube Audio Library | Official help page: audio library music and effects are "copyright-safe" on YouTube and will not be claimed through Content ID. A track with a Creative Commons licence needs the artist credited in the description. Filter "Attribution not required" to avoid that. Whether non-CC tracks may be used on TikTok or Instagram is not stated on the page. Secondary sources say the standard tracks are YouTube-only, which I could not confirm officially. | Safe for YouTube Shorts. For TikTok and Reels use only tracks marked CC BY 4.0 and credit them. Treat the rest as YouTube-only. |
| Uppbeat | Free plan: three downloads a month and a credit to Uppbeat is required (a link in the description). Uppbeat states all downloads, free ones included, are covered for YouTube, TikTok and Instagram. Paid plans drop the credit and add channel safelisting against Content ID claims. The Uppbeat terms and pricing pages returned HTTP 429 during this research, so these terms come from Uppbeat's own blog comparisons and a licence summary site. | Usable for published shorts with the credit line, three tracks a month is too few for an automatic picker. Re-read the terms page before relying on it. |
| Mixkit (Envato) | Mixkit Free Licence: commercial and non-commercial use, social media, YouTube, podcasts and online ads, no attribution needed. Not allowed in CDs, DVDs, video games, or TV and radio broadcasts. Taken from a summary of Mixkit's own information page. | Usable without credit, small catalogue. |
| TikTok Commercial Music Library | Free to TikTok Business Accounts, and the licence covers TikTok content only. A video re-posted to YouTube or Instagram is no longer licensed (Soundstripe summary). | Only for a TikTok-only post. Not usable by a pipeline that exports one file for three platforms. |

Pick order for the library: Pixabay Music and Kevin MacLeod first (no hard per-month limit), CC0 and CC BY tracks from FMA second, Mixkit third, YouTube Audio Library CC BY tracks fourth, Uppbeat for one-off premium choices. The index must carry the licence id and the credit string so `credits.md` is generated, not typed.

### How the engine picks the section of the song

Replace "first drop at the wanted fraction" with a candidate search over every phrase start (every 8 beats and at each drop) that has room for the duration:

1. A candidate starts on a downbeat at a phrase boundary and does not start inside a sung line when the style shows lyrics or voice.
2. The drop is within one bar of `drop_at` x duration, and the window ends at a bar end that is also a phrase end if possible.
3. For loop-seam styles choose the end so the last bar's energy is close to the first bar's, then add the one-beat tail.
4. Score = energy-curve fit + drop fit + clean ending + vocal-free intro. Take the best, and log the top three in decisions.json with their scores so a bad choice can be re-rolled by name.
5. Voice-led styles pick the calmest dropless section and ignore beats, tempo is irrelevant.

## 3. Sound effects

### Which effect on which event

| Event | Effect | Placement | Level |
| --- | --- | --- | --- |
| Hard cut with a flash or flash frame | short click or camera shutter, or a very short hit | transient on the first frame of the flash | low |
| Transition longer than about 0.2 s (whip, wipe, zoom blur, mosaic) | whoosh | peak on the cut, so the whoosh starts 0.1 to 0.25 s early | medium |
| Punch-in or zoom pulse | short whoosh up or a low thump | transient on the start of the zoom | low |
| Caption pop (chunk of 2 s or longer, a title, a key word) | pop, tick or soft click | on the caption's first frame | very low |
| Word-per-beat captions (lyric styles) | none, the music carries it | | |
| Glitch, RGB split, heat band | glitch or digital burst | on the effect's first frame | medium |
| Build into a drop | riser | ends exactly at the drop, 1 to 2 bars long | rises, then a gap |
| The drop | impact or sub boom | transient on the drop beat | highest |
| End card or logo | one sting | on the card's first frame | medium |
| Voice-only styles | none, or one pop per card | the sources had no sound effects at all | |

### How loud and how many

Sources (Epidemic Sound, Descript, FlexClip, vendor mixing guides) agree on the shape, with different numbers:

- Dip the music 3 to 6 dB right under a significant effect and recover fast, and keep effects on their own track.
- Effects sit well below the voice. One guide gives 30 to 61 percent of the voiceover level and 0.6 to 2 seconds long. Another puts effects at -10 to -20 dB and music at -18 to -22 dB, dialogue near -18 to -9 dB.
- "A handful of clean, well-synced cues reads as intentional, a sound on every beat becomes noise."

Engine policy: (a) at most one cue per 0.4 s and at most one per cut in the flash styles, in practice give a sound to every second or third cut and to every transition longer than 0.2 s (bw-flash-vo's creator labels list riser, charge, whoosh, tremolo, clicks, impact, page flick and hiss, so about one cue per flash or zoom, not per cut), (b) caption pops only when the gap to the previous pop is at least 1.5 s, (c) one riser and one impact per drop, never two risers closer than 8 beats, (d) cap the sum of simultaneous cues at two, (e) the sum of all effects peaks at least 6 dB below the voice or the loudest music hit.

### Aligning to the music

- Find each sample's own attack time at load (the first sample above -30 dBFS relative to peak) and place the event at `event_time - attack`, so the transient and not the file start lands on the cut or hit. Today `sfx.mix` plays the file start at the event time.
- Quantise to the same sixteenth grid as the cuts, keep a free offset of up to 40 ms early for whooshes, and none for hits.
- A riser's `end_at_t` equals the drop time, then the style's `gap` rule mutes the music for one beat before the drop for contrast.
- Pitch is not a worry for noise-based whooshes and hits, but tonal risers and pops should be pitch-shifted to the song's key when the index stores the track key (small gain, later).

### Licensed sources

| Source | Terms | Notes |
| --- | --- | --- |
| Freesound | Each sound has its own licence: CC0 (any use, no credit), Attribution (credit required, commercial allowed), Attribution NonCommercial (no earning from the work). The FAQ's suggested video credit: "This video uses these sounds from freesound: 'sound1' by user1 (http://freesound.org/s/soundID/) licensed under CCBYNC 4.0" or one line pointing to a credits page. The old Sampling+ licence was retired in 2011, and older sounds can still carry it. | API text search accepts `license:"Creative Commons 0"` and `duration:[0.0 TO 3.0]` filters. Fetch with CC0 first, then CC BY with the credit stored in the index. Never download BY-NC. Skip Sampling+. |
| Pixabay sound effects | Same Pixabay Content Licence as the music (no credit, no standalone redistribution). | Easiest for pops, whooshes and UI sounds. |
| Sonniss GDC bundles | Royalty free, commercial use allowed, no attribution, unlimited projects. The files may not be resold as standalone files or inside sound libraries, though finished creative projects may contain them. AI and ML training is "strictly prohibited". The Sonniss page read during this research listed the GDC 2024 bundle (23.5 GB) as latest and said there was no 2025 bundle. A trade report says a 2026 bundle of about 7.5 GB from 17 vendors exists, so check the page for the newest. | Keep the raw files out of git (they are redistribution if the repository is public). Do not feed them into any model training. Index them locally with a licence tag. Good for impacts, risers and hits with real transients. |
| BBC Sound Effects (RemArc) | BBC copyright. Free for personal, educational or research use. Commercial use requires a licence, and "research" excludes AI training. The BBC page itself could not be opened by the fetch tool, so this is from news reports of the licence. The whole library is sold for commercial use through Pro Sound Effects. | Not usable for a brand short or a monetised account. Use only for personal tests, or buy a licence. |
| TikTok Commercial Music Library sound effects | Free to Business Accounts, TikTok only. | Skip for multi-platform export. |

Flag for Cam, once: `design-library/sfx` holds 13 clips cut from two social reels with licence "unknown, personal and internal use only", and the sfx README already says not to ship them. The engine's `sfx_library` map points at them, so a Green Label or Emerald render that leaves the machine needs these swapped for cleared files first.

## 4. Caption styles

### Which look suits which style and audience

| Look | What it is | Suits | Audience and notes |
| --- | --- | --- | --- |
| Word-by-word pop | One to three words at a time, scale pop, hard swap, colour on a key word | lyric-word-beat, bw-flash-vo, kinetic-card-explainer | Entertainment and music-led, sound-on viewers, short sentences. Vendor guides call kinetic word timing "the most recognisable editing signature on short-form". |
| Karaoke highlight | A phrase sits on screen and the current word lights up | A voiceover explainer or a story. Missing from the engine. | Educational and story audiences. One vendor reports word-by-word presets with the best retention for educational content. Vendor claim, treat as directional. |
| Two-line chunks | 1 to 2 short lines, 3 to 6 words, swap per sentence, no word animation | talking-head-split (serif_chunk) | Professional and B2B audiences, sound-off reading, a talker the viewer should keep looking at. |
| Behind-subject text | Big words between the subject and camera through a matte | hud-lyric-heat and hud-lyric-light, and `depth_text` in kinetic | One clear subject, a few key words only, music-led. CapCut and FlexClip both document the effect. The engine's rule to keep a word in front when the subject hides more than half of it is right. |
| Kinetic type | Scale, colour and motion on keywords over the speech | kinetic-card-explainer, kinetic default | Hooks and keyword emphasis. Use sparingly: one accent colour. |
| Staircase | One word per line stepping down | bw-flash-vo | Voiceover hooks with a claim. A signature of that style, not a general caption. |

Chooser rule: caption kind follows the style by default. Override to `kinetic` word-by-word when the line is 6 words or under and the music is energetic. Override to two-line chunks when the voice is slow (under 2.2 words per second) or the audience is professional. Add a karaoke kind for stacked-story-split and for long voiceover phrases.

### Safe area and readability for 9:16

Platform interface margins on a 1080 x 1920 frame, from a 2026 safe-zone checker dated 23 September 2026 (a third-party tool, platform apps change so treat them as margins):

| Platform | Top | Bottom | Left | Right |
| --- | --- | --- | --- | --- |
| TikTok | 240 px (12.5%) | 660 px (34.4%) | 120 px | 120 px |
| Instagram Reels | 269 px (14%) | 672 px (35%) | 65 px | 65 px |
| YouTube Shorts | 288 px (15%) | 672 px (35%) | 48 px | 192 px (17.8%) |

Engine rule for one file posted everywhere: keep all text and faces inside the union box, which is x from 11% to 82% of the width (120 to 888 px of 1080), y from 15% to 65% of the height (288 to 1248 px). Fractions apply at any `--res`. For a 720 x 1280 render that is x 79 to 590, y 192 to 832.

- Text size: 60 to 75 px at 1080 x 1920 for plain subtitles (3.1 to 3.9% of height, from a Reels sizing guide). The engine's measured talking-head caption is 64 px at 720 wide (about 96 px at 1080) and is deliberately bigger. Do not go below 3% of height.
- Two lines at most, and 3 to 6 words per chunk (the talking-head source median was 5.6 words in 1.1 s).
- Contrast: bold white with a thin dark outline or a scrim, the difference blend, or the auto_contrast ink. A text-to-background contrast check belongs in the gate (section 5 of the previous research).
- No caption row under the 35% bottom band unless the platform is chosen. The kinetic lower-left default and talking-head's lower-third caption need an audit against this box, because the bottom of the box sits at 65% of the height.
- Keep a hold of at least 0.4 s per phrase so a viewer can read it, except in the deliberate word-per-beat styles.

## 5. Everything else the engine should decide

- **Hook in the first 1 to 2 seconds.** Industry benchmark sources say about 70 percent of viewers decide in the first 2 to 3 seconds and a 3-second retention under 60 percent gets little distribution (vendor benchmark sites, kineclip and kapwing). Rule: shot 1 is the clip with the highest motion x sharpness x face score, text or a visible subject by frame 0, a hook line of at most 6 words on screen by 0.3 s, and the first change (cut, zoom or caption swap) by 1.5 s. Two styles currently open slowly by design: hud-lyric has about 4 s of clean intro with no caption and bw-flash-vo opens on a black-and-white eye. Give those a `hook` block that shortens the clean intro to 2 s or pre-rolls a caption, and let the chooser turn it on.
- **Pacing curve.** Nothing static for more than 3 to 5 seconds (the sources call this resetting attention every few seconds). The 12 October techniques note already ranks dead-frame hunting first for the same reason. Decide the cuts-per-second curve from the style (bw-flash-vo breathes 4.2, 1.6, 4.9, 3.4 cuts a second, talking-head reframes every 4.5 s, kinetic-card every 1.4 s) and check it after render.
- **Length.** Music-led: 13 to 22 s. Voiceover explainers: 30 to 60 s. Trend sources push a 45 to 90 s "longer short" for explainers. Let the voiceover length set the duration when one exists, or the facts count x 3 s (Green Label's 3 s per 12-word fact was too short, the README says 25 s would read better).
- **Grade.** Normalise first, then stylise: match each clip's exposure and white balance to a shared target, then apply the style's grade timeline. This is item 6 of the 14 October research. Mean luma and saturation from clips.py already choose hud-heat or hud-light, reuse them for `target_luma`. Warm film and high-contrast looks are the 2026 default for LUT-led social edits, which fits the Fontainebleau variant's warm grade.
- **Loop seam.** Rewatch is weighted heavily in 2026 algorithm write-ups (vendor and blog sources, unverified numbers), and loops cost one beat. Rule: for music-led shorts under 30 s with no end card, turn on `loop_seam_beats` (last shot repeats the first picture) and end the audio on a phrase whose energy matches the intro. Voiceover explainers use an end card instead.
- **End card.** A comment-KEYWORD card for explainers (kinetic-card-explainer does this), a logo card for brand pieces (logo_card.py, Green Label), nothing for lyric loops. Do not dim for a platform end screen unless the target platform needs it, the talking-head source dimmed its last 4 s for TikTok's.
- **Credits and facts.** Generate credits.md from the music and SFX index (licence id, credit string, URL) and from the footage manifest, so the caption, description line and the file stay in step.
- **Decision log.** `decisions.json` beside `edl.json` with every choice, the features that drove it and the runner-up with its score. This is item 5 of the 14 October research, and the chooser needs it to be debuggable.

## Ranked build list

| Rank | Change | File | Effort |
| --- | --- | --- | --- |
| 1 | Brief and footage reader plus style chooser, `--style auto` as default, decisions.json. Add face count and area, speech present, screen capture flag, distinct subject count to the clip cache. | new `engine/choose_style.py`, `engine/brief.py`, extend `engine/clips.py`, `engine/make_edit.py` | medium |
| 2 | Music library and picker: index of cleared tracks (bpm, drop time, energy per bar, beat clarity, vocals, genre, licence, credit string), scoring against the brief, `--music auto`, candidate window search over phrase starts with a top-three log, credits.md generated. | new `engine/musiclib.py`, `engine/pick_track.py`, `music/index.json`, change `plan.pick_window` | medium |
| 3 | Safe-area box and caption rules: union box as fractions in the style schema, a lint step in the gate that checks every caption bbox, and a caption-kind chooser. | `engine/check.py` or new `engine/gate.py`, `engine/captions.py`, style.json `captions.safe` | small |
| 4 | Sound effect policy and a cleared set: attack-time alignment, density caps, music dip of 3 to 6 dB under hits, a fetch tool that pulls CC0 and CC BY sounds from Freesound (license filter) and Pixabay, an index with licence and credit fields, replace the unknown-licence clips before anything ships. | `engine/sfx_library.py`, `engine/sfx.py`, `engine/audio_shape.py`, new `engine/tools/fetch_sfx.py`, `sfx/index.json` | medium |
| 5 | Hook, pacing, loop seam and end card rules as a `finish` block the chooser sets per brief, including a shorter clean intro for the hud pair and a first-shot scorer. | `engine/plan.py`, style.json `hook`, `loop`, `end_card` keys, `engine/ext/logo_card.py` | medium |
| 6 | Dead-frame hunting and the post-render gate (already ranked first in the 12 and 14 October notes). The chooser's output needs it to catch bad picks. | new `engine/deadframes.py`, `engine/gate.py` | small to medium |
| 7 | Karaoke highlight caption kind. | `engine/captions.py` or new `engine/ext/karaoke.py` | small to medium |
| 8 | Duration chooser (voiceover length, fact count, style default) and a style-variant mechanism (named overrides such as `green-label` or `fontainebleau` stored with the style, selected by brand or mood instead of hand-copied style.json). | `engine/make_edit.py`, `engine/plan.py`, `edits/<style>/variants/` | small |
| 9 | Normalise-before-stylise grade pass. | `engine/render.py` or new `engine/normalise.py` | small |
| 10 | strobe-photo-dump style from one reference reel. | `edits/strobe-photo-dump/` | medium |
| 11 | velocity-ramp-edit style from one reference reel. | `edits/velocity-ramp-edit/`, speed ramp work in `engine/render.py` | large |
| 12 | stacked-story-split style (stacked layout, karaoke captions, gameplay background loop). | `edits/stacked-story-split/`, layout work in `engine/render.py` | large |

Validate the chooser by running it over the three real tests, the six demos and the four self-generated song sets and requiring it to return the style that was used, then keep that as a regression test next to tests/test_sfx_library.py.

## Source quality, and what could not be reached

Licence terms come from the primary pages for Kevin MacLeod (incompetech FAQ), Free Music Archive (licence guide), Pixabay (licence summary), YouTube (Audio Library help), Sonniss (GDC page) and Freesound (FAQ). Uppbeat's terms and pricing pages returned HTTP 429, the BBC page could not be fetched, and the Mixkit, TikTok CML and BBC terms come from secondary summaries, so re-read those before relying on them. The YouTube Audio Library page does not say whether non-CC tracks are allowed off YouTube, secondary sources say no. Retention, rewatch and completion figures (65 percent at 3 seconds, 75 percent completion for split screen, 23 to 40 percent watch time from dynamic captions) are from vendor blogs and are directional only, none of the structural rules above depends on them. Mixing levels are from vendor guides and disagree on exact numbers, so the engine should expose them as style settings and calibrate against the sources' measured -14 LUFS voice mix. No finished reel was watched for any trend format, the three proposed styles need a reference reel from Cam before their measurements can be taken.

## Sources

- Kevin MacLeod licence and FAQ: https://incompetech.com/music/royalty-free/faq.html and https://wiki.creativecommons.org/wiki/Case_Studies/Kevin_MacLeod
- Free Music Archive licence guide: https://freemusicarchive.org/License_Guide and FAQ https://freemusicarchive.org/faq/
- Pixabay licence summary: https://pixabay.com/service/license-summary/ and terms https://pixabay.com/service/terms/
- YouTube Audio Library terms: https://support.google.com/youtube/answer/3376882
- Uppbeat comparisons and credit rule: https://uppbeat.io/blog/royalty-free-and-copyright-free-music/uppbeat-vs-epidemic-sound-how-do-they-compare and https://licenseorg.com/guide/music-audio/uppbeat
- Mixkit information page: https://mixkit.co/llm-info/
- TikTok Commercial Music Library: https://www.soundstripe.com/blogs/tiktok-music-library-explained
- Sonniss GDC bundle: https://sonniss.com/gameaudiogdc and https://rekkerd.org/sonniss-releases-gdc-2026-game-audio-bundle/
- BBC Sound Effects RemArc reports: https://www.diyphotography.net/the-bbc-sound-effects-archive-is-now-free-to-download-with-over-33000-files/ and https://cdm.link/bbc-gives-away-16k-wav-sound-effects-disallows-using/
- Freesound FAQ and licence field: https://freesound.org/help/faq/ and https://freesound.org/docs/api and https://creativecommons.org/2011/09/12/celebrating-freesound-2-0-retiring-sampling-licenses/
- Safe zones: https://reap.video/blog/short-form-video-safe-zones and https://www.upload-post.com/tools/safe-zone-checker/ and https://blitzcutai.com/blog/best-caption-size-instagram-reels-2026
- Caption styles: https://www.opus.pro/blog/best-caption-presets-styles-boost-retention and https://www.clipspeed.ai/blog/11-caption-styles-ranked-viral-performance-2026.html and https://blitzcutai.com/blog/best-caption-style-youtube-shorts-2026 and https://openclip.app/learn/caption-styling
- Text behind a person: https://www.capcut.com/resource/how-to-put-text-behind-a-person-in-capcut and https://www.flexclip.com/learn/text-behind-person-effect.html
- Kinetic type: https://www.influencers-time.com/kinetic-typography-boost-video-retention-on-tiktok-and-reels/
- Trend formats: https://www.capcut.com/resource/best-velocity-capcut-templates and https://www.capcut.com/help/capcut-transitions and https://ghostshorts.com/blog/how-to-make-split-screen-gaming-videos-2026 and https://www.kapwing.com/explore/in-heat-black-screens-trend-template and https://socialbu.com/blog/instagram-reel-templates and https://kineclip.com/blog/short-form-video-trends-2026/
- Hooks and retention: https://www.kapwing.com/resources/short-form-video-statistics-tiktok-reels-and-shorts-by-the-numbers-in-2026/ and https://kineclip.com/blog/short-form-retention-benchmarks-2026/ and https://eliro.pro/blog/short-form-video-hooks-script-guide-2026
- Loops: https://joyspace.ai/looping-hack-trick-algorithm-double-views and https://thesocialcat.com/glossary/video-loop-short-form-content
- Music and beat sync guides: https://beatsyncpro.ai/blog/free-music-tiktok-background.html and https://www.foximusic.com/blog/?p=597 and https://openclip.app/learn/audio-ducking
- Sound effect use and levels: https://www.flexclip.com/learn/transition-sound-effects.html and https://sonilo.com/blog/guides/transition-effect-sound-video-edits and https://www.epidemicsound.com/blog/audio-mixing-for-video
- Open-source auto-edit projects surveyed: https://pypi.org/project/cutai/ and https://braindetox.kr/en/posts/openshorts_video_to_shorts_automation_2026.html and https://github.com/topics/ai-captions
- Colour trends: https://news.samsung.com/global/interview-make-every-moment-cinematic-how-cinematic-lut-transforms-video-on-the-galaxy-s26-series
- Earlier notes this plan builds on: edits/techniques-2026-10-12.md and edits/research/one-prompt-video-2026-10-14.md

## Measured, Stage 1 (2026-10-15)

Build stage 1 of overnight-improve-video-edit-e ran the new `clips.py` features (face count/area,
speech-present, screen-capture, distinct-subject count, line 37 above) over the three real
acceptance-test folders, to replace this plan's rough thresholds with real numbers. `clips.analyse()`
on each folder's actual clip set (`edits/engine/clips.py`, `.venv/bin/python -I`, no cache):

| Folder | Clips analysed | Stills share | Screen-capture share | Speech-present share | Large-face share (>=8%) | Mean motion | Mean saturation | Distinct subjects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| green-label/assets (top level: 2 logo stills, no clips/ subfolder) | 2 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 2 |
| fontainebleau/assets/clips | 18 | 0.556 | 0.0 | 0.0 | 0.0 | 0.919 | 82.4 | 11 |
| dachshunds/assets/clips | 10 | 0.0 | 0.0 | 0.0 | 0.0 | 4.695 | 73.1 | 8 |

None of the three real tests is a screen capture or has a large face or measurable speech, which
matches the screen-capture heuristic's own comment in `clips.py` ("calibrated against the three
real acceptance-test folders, none of which is a screen capture") and gives Stage 4 three true
negatives to validate `choose_style.py`'s screen-capture and face branches against, not evidence
for calibrating them (those branches still need the held-out cases Stage 4 names: a real
talking-head clip, a real screen-capture/card set). The distinct-subject counts (2, 11, 8) are
higher than line 49's "one distinct subject" example folder, because `distinct_subjects()`
clusters by a crude colour histogram of the focus region, not by identity, so stills of different
colours or clips lit differently cluster as separate subjects; Stage 4 should treat this count as
a rough variety signal, not a literal person count, when calibrating the "single clear subject"
branch.

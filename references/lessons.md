# Lessons from the Fontainebleau ad (13 Oct 2026)

(The second case study, a product launch film with a 3D camera and no voice, is in `lessons-product-film.md`.)

This is Will's feedback round by round: what he said, the root cause, and the fix that worked. The final film is `ForestPop3FR` in the worked example (38 s, 9:16, French voiceover in his ElevenLabs clone). It was submitted for LDMS A03a, and his verdict was "good, I like it" and "can't tell that it's AI at all".

## What he liked (keep doing)

- **Maps drawn as light linework over dimmed real drone footage**, Vox-style. "By far the best. Very professional." This also applies to data shown as an instrument in the same language: a km grid, corner brackets, a red hatched "gap", numbered markers with photos pinned beside them.
- **Engraved, 19th-century map styling as a deliberate opening beat only**: a paper sheet that opens to reveal the same map over footage, which reads as the drawing becoming reality.
- **The Opal reel's grammar**: wordless photo hook → turn → evidence → one demonstration → stakes → what the money does → the money → hush → the ask.
- **His own cloned voice, fast and urgent**, with captions built word by word in mid-size bold capitals.
- **An urgent, organic string score**: driving strings and drums. Not EDM.
- **Bookending**: the film ends on the same map it opened with, now turning green.

## Round by round

| He said | Root cause | Fix that worked |
|---|---|---|
| "Too AI" (first typographic draft) | Text cards and generic motion | Real diagrams and maps instead of text |
| "Too much impact frames and shake" | Effects used as decoration | Calm hard cuts; one impact per film, at most |
| "Still looks AI: the fade-ins and the icons" | Opacity fades and icon sets are the AI tell | Hard cuts or motion reveals; draw on the map instead of using icons |
| "Text goes by too fast; you don't know where to look" | Several text elements competing and short holds | One focal caption per beat, held longer |
| "The pop-ups appear randomly, it looks cheap" | Unsynchronised staggered entrances | Elements move as one system on a shared clock |
| "The styles clash (real video vs illustrated map)" | Two visual languages cut against each other | Overlay mode: the same map as linework over dimmed footage |
| "Weird humming noise; the sound effects sound weird" | Synthesised drone, beat and effects | Real generated sound (ElevenLabs), no synthesis |
| "Effects too loud; the music changes volume when I speak; generic NCS music" | Single-pass `loudnorm` pumping, plus an EDM-like prompt | Music at a constant level, one static gain, effects 20+ dB down; prompts that ban EDM/NCS |
| "Effects too sudden, almost hurt my ears" | Hard starts and stops, harsh top end | 15–80 ms fade-in and 250–600 ms fade-out, band-limit 150 Hz–5 kHz, whoosh peak aligned on the cut |
| "Opal is far more dynamic and well structured" | We had copied its tricks, not its rules | Study it frame by frame and stem by stem (see `reference-study.md`), then rebuild |
| "The opening could be much more detailed" | One card on an empty table | Strobe card that changes size and angle every 3 frames → parallax table of prints → engraved sheet slides in → paper opens onto footage |
| "Map borders look empty, cheap, too much like Claude" | A lone map floating on a dark field | Cartouche, black-and-white bar border, km grid with numbers; over footage, a moving grid, edge ticks and corner brackets |
| "Pop-ups too immediate, can't read them" | Labels appeared on the word and left about 1 s later | Labels start drawing as their panel arrives and are readable for 2–2.5 s; 1–1.4 s pauses added to the voice to make room |
| "Photos 100% denser, not 10,000%" | Over-corrected to a wall of about 50 prints | About twice the original: 18 prints with paper visible between them |
| "The labels are basic and AI-like" | Coloured bars, leader lines and text on photos | Steps become annotations on the forest map: the camera flies zone to zone, a numbered marker drops, the action is written beside it, and the photo is pinned with a dotted line |
| "My voice cuts out abruptly in places" | Splits at word-timing midpoints and hard joins | Split at the quietest 10 ms in each gap, with a 60 ms fade-out and 15 ms fade-in; check each split is quieter than -60 dB |
| "Text-only parts are less interesting than the maps" | Captions over photos | Château as a map (the 1.6 km line draws itself, planes fly); money as a data panel with the gap hatched red; the hush pushes into the gap; the closing map turns green |
| "The plane cut is random; the planes look templated and identical" | Two clones of one icon on one curve | Canadair silhouettes on different curves and timings with banking, trails, scoop rings and splash; an iris opens from the drop point onto the real helicopter photo and closes onto the next marker |

## What failed technically (do not repeat)

- **ElevenLabs music ignores "silent" sections** in a composition plan, so cut the music in the edit instead. It also rejects prompts that name real studios or artists ("A24…" returned a ToS error).
- **Burn fill stacking**: overlapping semi-transparent circles add up to opaque. Use one shape with a union mask.
- **A `Sequence` cannot show negative local frames**, so a context like `BurnDelay` holds an animation back instead.
- **Over-correcting**: when he says "more", change things in proportion, by about ×2.
- **Hedged deliverables**: commit to one choice, such as one button label; Ads Manager options must actually exist.

## Accuracy checks that saved us

- Re-read the live donation page before delivery. "Total raised" (1 435 940 €) included 50 000 € of corporate sponsorship, so the label "collecte" was wrong and became "total réuni".
- The burned area in the brief was 1,900–2,050 ha; ours was 1,955 ha from the EU satellite fire maps (EFFIS). The brief said "about 2 km" from the château; ours, measured, was 1.6 km.
- Photo locations come from the Commons file titles ("signs @ Faisanderie"; "Rocher du Long Boyau @ Mont Pierreux").

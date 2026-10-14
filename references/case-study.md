# Case study: twelve feedback rounds on a fundraising ad

A 38 s vertical fundraising ad (cloned-voice French narration, real fire and forest footage, data overlays, generated score) made in Remotion in October 2026 for a very demanding client. The final verdict was "can't tell that it's AI at all". The **principles** below transfer to any video. The specific look does not: choose your own (`making-it-yours.md`).

## What the client said, why, and the fix that worked

| Feedback | Root cause | Principle that fixed it |
|---|---|---|
| "Too AI" (first typographic draft) | Text cards and generic motion | Show diagrams and real material, not text about them |
| "Too much impact frames and shake" | Effects used as decoration | Calm hard cuts; one impact per film at most |
| "Still looks AI: the fade-ins and the icons" | Opacity fades and icon sets are the AI tell | Motion reveals instead of fades; draw the real thing instead of icons |
| "Text goes by too fast; you don't know where to look" | Competing elements, short holds | One focal caption per beat, held longer |
| "The pop-ups appear randomly, it looks cheap" | Unsynchronised staggered entrances | Elements move as one system on a shared clock |
| "The styles clash" | Illustration cut against real footage | One visual language for the whole film |
| "Weird humming noise; the sound effects sound weird" | Synthesised drone, beat and effects | Real generated sound, shaped; no synthesis |
| "Effects too loud; the music changes volume when I speak; generic music" | Single-pass `loudnorm` pumping, and an EDM-like prompt | Music at one constant level, one static gain, prompts that ban EDM |
| "Effects too sudden, they hurt my ears" | Hard starts and stops, harsh top end | Fades, band-limiting, the peak aligned on the cut, 20+ dB under the voice |
| "The reference is far more dynamic and well structured" | Its tricks were copied, not its rules | Measure the reference (frames, stems, transcript) and rebuild from rules |
| "The opening could be much more detailed" | One element on an empty background | Layered, moving opening: strobing photo, parallax collage, a reveal into the main language |
| "The borders look empty and cheap" | A lone graphic on a dark field | Real design detail in the margins: grid, ticks, brackets, cartouche |
| "Pop-ups too immediate, can't read them" | Labels appeared on the word and left about 1 s later | Labels start drawing as their panel arrives and stay readable for at least 2 s; pauses added to the voice to make room |
| "Photos 100% denser, not 10,000%" | Over-correction | When asked for "more", change things by about ×2 |
| "The labels are basic and AI-like" | Coloured bars, leader lines, text on photos | Annotate the subject itself: markers on the map, the action beside them, the photo pinned as evidence |
| "My voice cuts out abruptly" | Splits at word-timing midpoints, hard joins | Split at the quietest 10 ms of the gap, fade out over 60 ms and in over 15 ms, check each cut is below -60 dB |
| "The text-only parts are boring next to the data parts" | Captions over photos | Show figures as instruments (a gauge, a map, a diagram) in the film's language |
| "This cut is random; the two planes look templated and identical" | Two clones of one element on one curve | Vary every repeat (curve, timing, size); motivate cuts (iris from a meaningful point) |

## Technical failures (don't repeat)

- **ElevenLabs music ignores "silent" sections**, so make the hush in the mix. The model also rejects prompts naming real studios or artists.
- **Overlapping semi-transparent shapes add up to opaque.** Use one shape with a union mask.
- **A Remotion `Sequence` never shows negative local frames.** Hold animations back with a context or a frame offset instead.
- **`OffthreadVideo` fails with "No frame found at position…"** on long-GOP clips. Re-encode with `-g 15 -bf 0` (`toolchain.md`).
- **Deliverables:** hedged choices in deliverables ("X if available, otherwise Y") read as indecisive. Commit to one.
- **Labels:** must match their source exactly. "Total raised" and "donations collected" were different figures on the same page, because the total included corporate sponsorship.

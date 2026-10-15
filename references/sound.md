# Sound

Build the whole soundtrack in Python (`scripts/mix_soundtrack.py`) and mux it onto a silent render. Don't mix inside Remotion: you can't shape effects there, and its AAC encode adds about 43 ms of delay.

## Voice (your ElevenLabs voice: a clone of your own voice, or a library voice)

- Use `POST /v1/text-to-speech/{voice_id}/with-timestamps` with model `eleven_v4`. Take the voice's saved settings from `/v1/voices/{id}/settings`, then set `speed` to 1.12 for an urgent read. Read the key from the `ELEVENLABS_API_KEY` user variable and never print it.
- Generate the **whole script in one call**. One take keeps tone and pacing continuous, while splicing per sentence causes jumps. Turn the character alignment into word start and end times (`scripts/elevenlabs_tools.py tts`).
- **Pauses** (for breathing room, a sound moment, or labels): choose break points between words. Cut the voice at the **quietest 10 ms window within ±0.25 s**, fade the end of the piece out over 60 ms and the start of the next in over 15 ms, and offset the later pieces. Check that every cut is quieter than -60 dB.
- Keep **one timeline function** shared by picture and sound: `frame(voice_seconds) = (s + sum(pauses before s)) × fps`. Use the same pause list in the TSX and the mixer.
- About 3.5 words a second suits an urgent ad. 31 s of voice plus pauses made a 38 s film.

## Music (ElevenLabs `POST /v1/music`, `model_id: music_v1`)

- Send a `composition_plan` with positive and negative global styles and sections (each at least 3,000 ms) timed to the edit. The output format is `mp3_44100_192`.
- **It does not honour a "silence" section.** Make the hush in the mix: a 0.3 s cos² fade-out, mute, then come back on the ask with a 0.08 s fade-in. Alternatively, generate a separate short cue for the ask.
- **What worked:**
  - Positive: "urgent cinematic nature-documentary score, driving spiccato string ostinato, pounding frame drums and deep toms, low strings pulsing on every beat, rising intensity and urgency, organic, acoustic".
  - Negative: "EDM, NCS, dubstep, trap, four-on-the-floor kick, synth lead, supersaw, drop, vocals, choir, cheesy, corporate".
- **What failed:** "modern cinematic … felt piano, pizzicato, tight percussion" came out generic, which the client called "NCS". Naming a real studio ("A24 trailer style") returned a ToS rejection.
- Make 2–3 variants and mux each onto the same silent render (no re-render), so the client can pick by ear.
- The account allows 2–4 concurrent requests; a 429 means too many at once, so run them in sequence.

## Sound effects (ElevenLabs `POST /v1/sound-generation`)

- Use `duration_seconds` 0.6–2.2 and `prompt_influence` 0.6. The prompts that worked:
  - "fast clean cinematic whoosh, airy swish passing left to right, no tone";
  - "short soft swoosh transition";
  - "deep cinematic impact boom with a short dark tail";
  - "soft reverse swell opening into a gentle airy shimmer";
  - "descending soft whoosh fading into silence";
  - "firefighting water-bomber helicopter passing low overhead …".
- **Shape every effect:**
  - band-limit to 150 Hz–5 kHz (impact: 40 Hz–3.5 kHz);
  - sin² fade-in of 15–150 ms and cos² fade-out of 250–600 ms;
  - align the effect's **loudness peak to the cut**, so it swells into the transition;
  - align impacts on their start instead.
- **Levels, relative to the voice's speaking level:** whooshes -22 to -26 dB; swell -24 to -26 dB; impact -17 dB; ambience in a voice pause about -11 dB.
- Put effects on real transitions only, not every cut. Cut anything that sounds synthetic: drones, hums, sine "pops", photo flicks.

## Mix and loudness

- **Speaking level:** the RMS of 50 ms voice blocks above -40 dBFS.
- **Music:** one **constant** gain so its RMS sits 12–15 dB under the speaking level (-12 for the urgent cut). No ducking, no automation apart from the hush, and a 1 s fade at the very end.
- **Loudness:** measure the integrated loudness of the mix with `loudnorm=I=-14:TP=-1.5:print_format=json` and apply **one static** `volume` gain, then `alimiter=limit=0.84:attack=5:release=80:level=false`. **Never** use single-pass `loudnorm` as the final filter: it rides the gain, and the music audibly pumps.
- Encode with AAC at 192 kb/s and 48 kHz, plus `-movflags +faststart`.

## What the reference's soundtrack does (stem study of the Opal reel)

- The voice runs almost continuously.
- Music comes in sections. The drums enter at about 6 s and **drop out completely for 2–3 s** before each turn (about 23 s and 41 s).
- Soft rising whooshes of about 0.6 s lead into transitions. There are only two big impacts, the turn and the climax.
- An expert's real voice speaks one line under his own footage, then the narrator names him. The case study's equivalent was a real sound moment inside a voice pause. Parliament or politician clips can get an ad rejected under Meta's EU ban on political and social-issue ads.

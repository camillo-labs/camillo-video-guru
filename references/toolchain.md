# Toolchain, pitfalls and QA

## Tools and repos used (and what for)

| Tool | Use | Notes |
|---|---|---|
| **Remotion** 4.0.531 (React 19) | Composition, maps (SVG), captions, motion | — |
| **ffmpeg / ffprobe** | Pre-crops, encodes, contact sheets, splices, muxing, loudness | — |
| **ElevenLabs API** | Voice clone with timestamps, music (`music_v1`), sound effects | Key in `ELEVENLABS_API_KEY`; see `sound.md` |
| **HyperFrames** (`github.com/heygen-com/hyperframes`, 0.8.152) | Catalog of shader transitions and caption styles | `npx --yes hyperframes@0.8.152 init <name> --example blank --resolution portrait` with `HYPERFRAMES_SKIP_SKILLS=1 DO_NOT_TRACK=1`; `catalog --tag transition --json`; `add <name> --no-clipboard --json`. Its Claude Code plugin: `claude plugin marketplace add heygen-com/hyperframes`. |
| **Demucs** 4.1.0, **faster-whisper**, **yt_dlp** | Reference study | See `reference-study.md` |
| **Prompt Motion** (prompt-motion.com) and **cinetic** / **product-film-skill** repos | Motion rules, seam catalogue, motion-blur recipe | See `motion.md` |
| **EFFIS WFS**, **OSM Overpass**, **Wikimedia Commons API**, **Pexels** | Burned perimeters, map layers, photos, drone video | See `sources-and-facts.md` |

## Render recipe (Windows)

1. **Pre-crop** 4K/60 drone clips to 1080×1920 at 30 fps, with **frequent keyframes and no B-frames**:
   `ffmpeg -i in.mp4 -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920,fps=30" -an -c:v libx264 -crf 18 -g 15 -keyint_min 15 -sc_threshold 0 -bf 0 out.mp4`.
   Without `-g 15 -bf 0`, `OffthreadVideo` intermittently fails with "Compositor error: No frame found at position …".
2. **Render** silent, with a retry loop:
   `for i in 1 2 3 4; do rm -f out.mp4; npx remotion render <Comp> out.mp4 --concurrency=4 --offthreadvideo-threads=2 --log=error > log.txt 2>&1; [ -f out.mp4 ] && break; done`.
   Keep concurrency at 4; 16 parallel jobs once crashed the PC.
3. Mount a clip only while it can be on screen, so its `startFrom` plus duration never runs past the clip's end.
4. **Splice** shader transitions on the silent render (`burn_transition.py`), then encode for the web: `-c:v libx264 -crf 22 -maxrate 6M -bufsize 12M -preset slow -pix_fmt yuv420p -movflags +faststart`.
5. **Mux** the soundtrack with `mix_soundtrack.py`, which copies the video stream.
6. **Previews:** run `npx remotion still <Comp> f.png --frame=N --scale=0.4` in parallel for the beats that changed, and tile them with `ffmpeg … hstack` or `tile`. Look at them before any full render.

## Pitfalls met (and fixes)

- **Git Bash rewrites `/api/...` arguments into Windows paths.** Prefix the command with `MSYS_NO_PATHCONV=1` (any CLI that takes URL paths).
- **Heredocs** with complex Python, nested quotes or backslashes fail. Write a `patch_*.py` file and run it.
- **`rm` on a `$VAR` path is blocked** by the safety check. Use literal paths or `"${VAR:?}"`.
- **A Remotion `Sequence` never renders before `from`,** so it can't show negative local frames. Hold animations back with a context (for example, `BurnDelay`).
- **Overlapping semi-transparent shapes add up to opaque.** Draw one shape with a mask made from the union of the circles.
- **SVG text over a scaled map gets big.** Keep camera zoom at about 2.0 or below, or counter-scale the labels.
- **ElevenLabs:** 2–4 concurrent requests at most; the music model can reject studio and artist names; "silence" sections are ignored.
- Run Python **`-I`** on anything that reads downloaded files.

## QA checklist (before sending any version)

- [ ] Stills at every beat and every transition midpoint, looked at, not just generated.
- [ ] `python -I scripts/deadframes.py out.mp4`: only deliberate holds may be flagged.
- [ ] Voice splits fall in silence (below -60 dB); no clipped word ends.
- [ ] Effects are 17+ dB under the voice and faded; the music level is constant; no pumping.
- [ ] Integrated loudness is about -14 LUFS and true peak at most -1.5 dBTP.
- [ ] `ffprobe`: H.264, yuv420p, 1080×1920, 30 fps, AAC, and the length the brief asks for.
- [ ] Every number re-checked against its live source; labels say exactly what the source says.
- [ ] Credits on the end card; footage licences recorded.
- [ ] Captions readable with the sound off; text between 14% and 65% of the height.

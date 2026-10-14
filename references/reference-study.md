# Studying a reference reel

Impressions of a reel ("it's dynamic") produce imitations of its surface. Measuring it produces rules. In the case study, two rounds were wasted copying a reference's tricks; the third worked after this study.

## Steps

1. **Get the file.** Downloading needs the client's (or your own) explicit approval each time: name the file, source and size. Use `python -I -m yt_dlp --no-playlist -f "best[ext=mp4]/best" -o ref.%(ext)s <url>` into a new empty folder. It's for analysis only, never reused in the work.
2. **Run** `python -I scripts/analyse_reference.py ref.mp4 <outdir>`. It writes:
   - `sheets/sheet_XX_YY.png`: 10 fps frames tiled 15×4, one image per 6 s. Read them in order.
   - `cuts.txt`: scene-change times (`select='gt(scene,0.25)'`).
   - `stems/`: Demucs `htdemucs` split into vocals, drums, bass and other.
   - `transcript.json`: faster-whisper `small` (int8, CPU) with word timestamps.
   - `audio_map.png`: loudness per stem, a spectrogram of drums + other, a vocals spectrogram, with the cuts marked.
   - `fx_events.json`: transients in drums + other, with duration, peak and whether the pitch rises or falls (whooshes, risers, impacts).
3. **Write the rules down** (keep them in the project's notes):
   - **Structure:** the beats, what each one does, and its length (shots per second by section).
   - **Hook:** the first 3 s; is there text? A face?
   - **Motion:** how cards and photos move, how cuts are hidden (pans, irises, match cuts), and whether anything is ever static.
   - **Type:** size relative to width, case, how words build (per word? stacking?), outline versus solid, where it sits.
   - **Sound:** whether the voice is continuous, the music sections and where they **drop out**, the effect types and their levels relative to the voice, and how many impacts.
   - **Special moves:** for example, a second real voice laid under the narration.
4. **Map each rule to your material** (what plays the role of their "technical drawing", "hearing" or "screen-time panel"?), and copy the **grammar, not the content**.

## Tools

- `yt_dlp` (Python module), ffmpeg, `pip install demucs` (needs torch), and `faster-whisper` (installed).
- `scipy` isn't installed: the scripts filter with numpy FFT.
- The browser tools have no sound output, so a breakdown made from snapshots alone misses all the audio. Always split the stems.

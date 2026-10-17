# Lessons from the Nightcrew launch film (15–17 Oct 2026)

The second case study, a product film this time. Nightcrew is a Windows tray app that keeps a laptop working
with the lid closed while Claude Code or Codex works. Eight rounds, from a 33 s hairline film to the launch cut:
v4 with a settings tour, 42 s, in 16:9, 9:16 and 4:5, with no voice and music at a constant level. The project is
`dev/nightcrew-launch` (Remotion; `src/Sting4.tsx`, `src/Tour4.tsx`, `src/t4.ts`). Will's verdicts: "really good" (v3),
"goood" (the 3D camera test), "very good" (v4 with the tour).

## What he liked (keep doing)

- **A keynote sting**, after prompt-motion.com's "Frame by Frame": shots enter already moving with an exponential
  ease-out, blur follows speed, a cursor clicks, cuts land on the music's drop, and the type moves (words rise in
  with a speed blur, italic words land a beat later).
- **The real UI, rendered from the app's own code** at 4×, never a mock-up. Tour it with a camera that stops on
  each part, a spotlight on that part, and one kinetic line per stop.
- **A drawn object with a real camera:** the hairline laptop opens, then the camera swings round to the screen and
  moves in, follows the typing and the tray, and swings back out for the lid close. One continuous move.
- **His own storyboard, built as he described it**, then tuned. He writes the beats ("you open your laptop, you type a
  prompt, you close it, the lantern lights up, it keeps working"); keep his order unless it says something false.
- **Plain claims with a clarifier**: "Claude *keeps working,*" over "even when the laptop is *closed.*"

## Round by round

| He said | Root cause | Fix that worked |
|---|---|---|
| "Not detailed enough at all" (round 1, cream outlines on flat night) | One simple drawing on an empty field | Two references he chose (a hairline isometric piece and a real-UI close-up piece); every key, port and hinge drawn |
| "Not straightforward; I can't tell what the app does; the type has no motion" | An aesthetic film without a story | A 15 s keynote sting: lockup → laptop at work → lid closes, the card keeps counting → done, it sleeps → the real panel on the drop |
| "A bit more detail: a without/with snippet, and more time on the menu" | — | v2 added both |
| "People are smart enough" (about the without/with) and "the menu tour is too fast to follow" | Explaining the problem instead of showing the product; about 1 s per UI stop | Drop the comparison; about 3 s per stop, with the line on screen about 2 s |
| "Can't it be in the same 3D model? Do we need Blender?" (about the cut from the laptop to a flat screen) | An isometric view never faces the camera, so we cut to a flat copy inside a blur | A perspective camera in our own model (`remotion-kit/isocam.ts`); no Blender. Show a 3 s test clip of the move before the full render |
| "Too much global motion blur, every time you zoom in and out" | A CSS `blur()` on the whole layer, scaled by speed | Real motion blur: whole frames drawn at sub-frame times and averaged (`remotion-kit/subframes.tsx`); directional blur only for shot entries and exits |
| "Work a little on the fire animation when night mode turns on" | The lit icon was a cross-faded PNG | The flame as its own shape over the unlit icon: a spark, an overshoot grow, sway and flicker, a white-hot core, warm glass, embers when it flares; the camera pushes in so it reads |
| "Add 'even when the laptop is closed'"; "15–20% more time to read the captions" | Captions held 3 s | One or two more beats per caption (3.5 s per stop, 5 s for the two-line caption), cuts still on the beat |

## What failed technically (do not repeat)

- **CSS-scaling a layer that holds SVG text.** Under `--concurrency=6`, Chrome drew the text at a stale scale in some
  frames (shifted, clipped), while a direct `remotion still` of the same frame was correct. Apply zooms as SVG
  `transform` attributes or computed sizes. Check by comparing decoded frames with stills (`scripts/framecheck.py`).
- **Averaging transparent copies with `mix-blend-mode: plus-lighter`** shifted the colours in Chrome's software
  compositor (dark fills went teal, amber went grey). Average whole opaque frames instead, each copy at opacity
  1/(i+1) with normal blending.
- **Too few motion-blur samples** showed as separate parallel hairlines. Keep copies at most about 1.2 px apart (up
  to 16), and measure speed at the fastest points: in perspective that is the near corners, not the screen centre.
- **Big frames time out** (16 blurred copies of a UI with large box shadows): use `--timeout=120000 --concurrency=4`.
- **A mixer that adds effects past the end of a short test clip** crashed on an empty slice; skip effects that start
  after the end.
- **`ffprobe … -of csv=p=0` prints `1260,`** with a trailing comma, so a frame-count check against `1260` fails
  silently. Strip the comma.
- **The track ended before the film** (32.8 s of music for a 42 s cut). Repeat whole bars on bar lines with short
  equal-power crossfades (`scripts/extend_music.py`); check the joins for clicks.

## Accuracy checks that saved us

- A review of the launch materials caught **"Sees every agent, automatically"**: the app detects two agents. The line
  became "Finds Claude and Codex *on its own.*"
- The tour showed **an old Settings page**, without the new "Stay awake for approvals" switch. Render UI shots from the
  version being launched; the new row moved the lower rows down by 120 px at 4×, so the spotlight positions moved too.
- **The lantern lights when work starts**, not when the lid closes, so the ignition happens on the screen's taskbar
  after Enter, and the lid-close close-up shows it flaring brighter.
- When the GitHub name changed, the end card's link changed with it: re-render only the end-card frames and splice
  them in (`scripts/splice_tail.py`).

## Delivery

- **Shapes:** 16:9 for X, Reddit, YouTube and the README; 9:16 for Shorts and Reels; 4:5 for LinkedIn and the
  Instagram feed. 4:5 (ratio 1.25) uses the square layout with room above and below.
- **GitHub README video:** upload the mp4 as an attachment (the issue form's text box; no need to submit the issue),
  under 10 MB on a free plan. `-crf 23 -preset slow -tune animation` gave 6.9 MB for 42 s of 1080p. Put the bare
  `https://github.com/user-attachments/assets/<id>` URL on its own line. It plays for signed-out visitors through a
  signed link, even though the bare URL returns 404 to them.

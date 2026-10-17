# Motion

The bar set in the case study: **"always very dynamic, but not sudden"**, measured against a polished app ad (the Opal reel, @opalapp). Study your own reference the same way (`reference-study.md`).

## What the reference actually does (frame-by-frame study)

- **Nothing is static.** Cards rotate in 3D while the photo inside changes every 2–3 frames, with the subject held in the same screen spot. Footage is handheld or slowly pushing in, and focus pulls move attention.
- **Cuts are hidden inside motion.** Collages and technical drawings slide sideways into the next panel. A circle opens from a meaningful point (a pupil, a fire) onto the next scene.
- **Illustrations animate.** The camera pans across an engraving, labels draw in with leader lines, and icons fly into an outline.
- **Data appears as an interface laid over footage.** The screen-time panel's number races up while the shot behind blurs.
- **Type** is mid-size bold capitals built word by word on the voice, stacking down, with solid and outline letters mixed. Tension moments use tiny capitals on black. A single word can hold the frame alone.

## Rules with numbers (30 fps)

| Situation | Rule |
|---|---|
| Easing | Arrivals ease out (cubic, or `bezier(.16,1,.3,1)`); moves between two holds in-out cubic over 12–16 frames; camera zoom interpolated in **log space**; springs critically damped (closed-form `spring(t,k≈400,c≈24)`), overshoot ≤2% except one or two landings per film. |
| Holds | Never a still frame: push 1.00 → 1.12 per shot and start the next shot moving. Run `deadframes.py`; only deliberate hushes may be flagged. |
| Camera moves | Never a global `blur()` that grows with speed: Will called it "too much global motion blur". For a camera move, draw the whole frame at sub-frame times and average them (`remotion-kit/subframes.tsx`): each part smears along its own path and anything still stays sharp. Keep samples at most about 1.2 px apart (up to 16) and measure speed at the fastest points (in perspective, the near corners). |
| Into a drawn object | Don't cut from a drawing to a flat copy of its screen. Give the drawing a real camera (`remotion-kit/isocam.ts`): swing from the iso view to face the screen and move in, in one move; face the plane exactly while its content must read. Show a 3 s test clip of the move before the full render. |
| UI tours | About 3 s per stop was the minimum; with the final pace Will asked for, 3.5 s per stop and 5 s for a two-line caption. Add whole beats so cuts stay on the music. A spotlight on the part, one kinetic line per stop, the camera drifting in while it holds. |
| Fast moves | Anything over ~12 px/frame gets directional blur: about 0.12 px of blur per px/frame, capped at 22 px, through an SVG `feGaussianBlur stdDeviation="s 0"` (`remotion-kit/mblur.tsx`). Without it, 90–180 px/frame slides strobe. |
| Transitions | Use, in order of preference: iris from a meaningful point; push into a point and reveal (scale 1 → 2.4 with `pow(t, 2.2)` over 22 frames); sideways strip of panels; vertical push; shared-element bookends. One themed shader transition at most (the ridged burn on "brûlé"). No crossfades, glitch or spin packs. |
| Strobe opening | Change the card's photo every 3 frames; each change pops to a new size and angle (scale 1.08 → 1 spring); the card tilts continuously (rotateY 22° → -10°), then grows into full-frame footage over 12 frames. |
| Labels and notes | Pointer line draws first (9 frames), then the bar or text (8 + 8 frames), and stays **readable for ≥2 s**. Start drawing while the panel arrives, not on the spoken word. |
| Numbers | Count up with ease-out over about 1.5 s, with a spring pop on the first frame and the label rising in under it. Put a focus pull behind the number (blur 0 → 9 px, darken 35%). |
| Repetition | Never two identical moving elements: vary the curve, timing, size and banking (the planes). |
| Density | When asked for "more", change by about ×2, not ×10. |

## Seam catalogue (choose a few that suit your language)

- **Iris** from a meaningful point (an eye, a fire, a marker) onto the next scene; reverse it to close onto the next subject.
- **Push into a point**, then reveal what is "inside" it (scale about 1 → 2.4, accelerating).
- **Sideways strip:** panels side by side, the camera slides from one to the next (with motion blur).
- **Vertical push:** the next scene pushes the current one out.
- **Drawing → reality:** an illustration, map or plan gives way to the real footage of the same thing.
- **Grow into frame:** a card or print scales up until it becomes the full-frame shot.
- **Shared element:** one object (a bar, a shape, a word) carries across the cut and changes role.
- **Shader transition**, at most one per film and thematically motivated (`burn_transition.py` ports HyperFrames' ridged burn).
- **Hard cut on a word or a hit,** for contrast after a run of motion.

## Sources for these rules

- **Prompt Motion** (prompt-motion.com): a gallery of motion videos made with Opus, with their prompts. Its "Frame by Frame" keynote sting set the Nightcrew film's look: shots enter moving with an exponential ease-out, blur follows speed, a cursor clicks, cuts land on the drop, type moves. The useful entries cover subframe motion blur (render at ×4 fps and `tmix=frames=4`, no blur across hard cuts), speed limits, easing tokens, log-space zoom, word-by-word captions, iris and flood timing (18–24 frames, overscan past the corners), and a QA scan of frame differences.
- **Reference repos**:
  - `github.com/Leonxlnx/cinetic`: Remotion starter with motion tokens, a seam catalogue and an offline motion-blur pass;
  - `github.com/Rieranthony/product-film-skill`: spring tracks, "magic move" transitions, the 240 fps `tmix` recipe.
- **HyperFrames** (`github.com/heygen-com/hyperframes`, Apache-2.0). Its catalog has 14 WebGL shader transitions (ridged-burn, thermal-distortion, light-leak, whip-pan, sdf-iris, cinematic-zoom, domain-warp-dissolve, …) and caption styles (clip-wipe, kinetic-slam, editorial-emphasis). Its blocks are demos: copy the GLSL and run it on your own frames (`scripts/burn_transition.py` does this in numpy), or render a HyperFrames composition with your clips.
- General house rules: no eyebrow text, no dead frames, springs, and voice-led edits cut on the words.

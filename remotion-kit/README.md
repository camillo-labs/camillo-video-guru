# Remotion kit

Small, self-contained pieces. Copy them into your project and restyle them to your style brief.

| File | What it does |
|---|---|
| `mblur.tsx` | Directional motion blur. Mount `<BlurDefs/>` once, then give the moving layer `filter: mblur(vx, vy)`, where `vel(fn, f)` gives its speed in px/frame. About 0.12 px of blur per px/frame, capped at 22. |
| `shot.tsx` | One full-bleed photo or clip: cover-cropped around a focus point, with a push or pull (`zoom`), drift, a colour grade and a vignette. `.mp4` files play through `OffthreadVideo`. Footage goes in `public/footage/`. |
| `word-captions.tsx` | Captions built word by word from the timestamps that `elevenlabs_tools.py tts` writes. Pages of up to 3 lines; rise, fade and un-blur entrance; `*emphasis*` and `_outline_`; a `toFrame` hook for inserted voice pauses. |
| `subframes.tsx` | Real motion blur for camera moves: the whole frame drawn at up to 16 sub-frame moments and averaged, so each part smears along its own path and still parts stay sharp. Wrap the composition's root; give it the fastest on-screen speed. Use `mblur.tsx` only for a layer that slides as one piece. |
| `isocam.ts` | A drawn 3D object you can film: the isometric projection of the hairline drawings plus a perspective camera (`camProj`) that matches it when far away, so a shot can swing from the iso view into the object. `planeFit` puts flat content (a screen) on a plane; `proj.sees` says which faces to draw. |

## Patterns worth building (the case study used them; restyle them to yours)

- **Shared timeline:** `frame(s) = round((s + sum of pauses before s) × fps)`. Use the same pause list in `mix_soundtrack.py`.
- **Number counter with a focus pull:**
  - the number eases out over about 1.5 s and pops on its first frame;
  - its label rises in underneath;
  - behind it, a `backdropFilter: blur(0 → 9px)` layer plus a 35% darken.
- **Data panel:** corner brackets, a source line, the number, and a scale bar. The missing part is drawn in the same pattern as the film's "problem" colour.
- **Annotations:**
  - a numbered marker (disc, ring, pulse) on the subject;
  - the action in your caption face beside it, with a place line underneath;
  - a real photo pinned by a dotted leader;
  - the camera flies between subjects with in-out easing and zoom in log space.
- **Iris:** `clipPath: circle(r at x y)`, with r eased from 0 to past the farthest corner over 12–16 frames. Start it from a point the viewer is already looking at.
- **Context switches** (React contexts) let one scene component render in two modes (for example, a map as a paper plate or as an overlay on footage), or hold an animation back. A `Sequence` never shows negative local frames.
- **Union masks** for growing semi-transparent shapes, so overlapping circles don't stack into opaque.
- **Camera into a drawn object** (Nightcrew, `isocam.ts`):
  - keyframe the camera (target, yaw, pitch, distance, zoom, anchor) and ease each key in from wherever the camera is;
  - interpolate distance and zoom in log space;
  - when a plane's content must read, face it exactly (yaw and pitch along its normal);
  - apply zooms as SVG transforms, never as a CSS scale on a layer with SVG text.
- **A living icon** (the Nightcrew lantern):
  - draw the moving part (a flame) as its own shape over the still icon, placed from the real icon's pixels;
  - animate it as a spark, then a spring overshoot, then sway and flicker from two or three sines, then a brighter inner core;
  - for a "flare", add brightness and movement rather than size if the shape is boxed in.

# Techniques from two short videos, 12 October 2026

Two vertical videos Cam received were transcribed locally with Whisper and read against the edit engine in `edits/engine/`. Video A (@raycfu, 58.7 s) describes a Claude, Playwright and FFmpeg motion design studio. Video B (@alekseitalksai, 31.2 s) presents the OpenMontage repository. Every claim about the engine below was checked in the named file on 12 October 2026. Every claim about OpenMontage is marked as from the repo or from the video.

## 1. Transcripts

Corrections: Whisper misheard "startups", "closed-form" and "re-render", and the on-screen captions were used to correct them. The raw word timings are in `talking-head-split/transcript-words.json` and `kinetic-card-explainer/transcript-words.json`.

### Video A, @raycfu, "How to do motion design with Claude Opus 5.5" (speech 0 to 54.5 s)

```
[00.00 - 04.16] Most people don't realize that the insane AI motion graphics videos all over your feed are not just one prompt.
[04.32 - 07.88] It's rather a studio that you set up once and startups are paying two to three thousand for these videos.
[08.08 - 09.12] Here's exactly how you build it.
[09.16 - 11.24] Start by building the headless render engine loop system.
[11.36 - 13.04] You have to understand that Claude does not make a video.
[13.20 - 14.82] It writes code that paints every single frame.
[14.94 - 18.76] Install Node, FFmpeg, and Playwright with Claude Opus 5.5 set on extra high.
[18.86 - 23.58] The Playwright browser captures every frame in Chrome and the FFmpeg stitches them together to make the final MP4.
[23.70 - 30.50] Then you need to give it a reference in real assets because on its own, Claude will default to all-caps centred text on a gradient which really looks like AI Slop.
[30.60 - 32.64] Make sure to enforce real spring physics and audio.
[32.84 - 37.24] Ban basic CSS so Claude has to actually use closed-form springs so it actually makes the UI look good.
[37.32 - 39.92] Tell it to synthesise the sound in code and lock every cut to the beat.
[40.00 - 41.08] This next part is the real secret.
[41.22 - 43.14] You make Claude watch its own frames and critique them.
[43.24 - 46.86] Tell it to hunt down dead frames and re-render them so every frame grades it at 8 out of 10.
[46.96 - 49.48] I created a step-by-step guide to build this out for your own business.
[49.66 - 52.08] If you want it, just like the video and comment motion and I'll send it to you.
[52.16 - 54.48] Follow for ways to make money and run your business with tech and AI.
```

### Video B, @alekseitalksai, OpenMontage (speech 0 to 26.7 s)

```
[00.00 - 05.00] 65,000 stars for a repo that turns Claude into a full video studio.
[05.30 - 06.40] It's called OpenMontage.
[06.50 - 08.10] You describe the video in plain words.
[08.26 - 14.26] The agent does the research, writes the script, finds or generates the footage, adds voice and music, and edits the final cut.
[14.46 - 19.92] Or paste a reel you love, it breaks down the pacing, the scenes, and the style, then builds yours from that.
[20.04 - 23.76] The demos on the repo include a sci-fi trailer and a Pixar-style short.
[23.90 - 26.74] Comment Montage, and I'll send you the link and a setup guide.
```

Note on the source: Video A's claims ("startups are paying two to three thousand", "every frame grades at 8 out of 10") are the creator's sales pitch. None of the technique descriptions below were verified against the creator's actual guide, which is gated behind a comment. Only the ideas are used.

## 2. Techniques

### 2.1 The render-loop architecture (Playwright frames into FFmpeg)

**What it is.** In the video's words: "Claude does not make a video. It writes code that paints every single frame. Install Node, FFmpeg, and Playwright... The Playwright browser captures every frame in Chrome and the FFmpeg stitches them together." The idea is a headless loop. A page exposes a pure function of time, a driver sets t = frame / fps, screenshots the page as a PNG, and FFmpeg encodes the numbered PNGs. Because nothing runs in real time, the render is deterministic and can be paused, resumed or re-rendered per span. Anything a browser can draw becomes a video layer: web fonts, CSS layout, SVG, canvas, WebGL.

**Does the engine do it already? Partly.**
- The frame loop is already deterministic and offline. `render.py` `render()` walks `for f in range(nf)`, computes `t = f / fps`, builds a per-frame `ctx` with an RNG seeded from `edl['seed'] * 100003 + f`, composites, and writes raw BGR to an ffmpeg encoder pipe (`enc.stdin.write`). So "pure function of time" is already true of the whole engine.
- The painter is Pillow and OpenCV, not a browser. Text is drawn with Pillow in `captions.py` `text_rgba()`, and ffmpeg is used without drawtext or libass (stated in `engine/README.md`).
- The extension contract is already close to a frame painter. A caption kind registered with `@captions.caption('kind')` returns an RGBA layer for time t, and `render()` composites that layer over the picture (including the behind-subject matte pass).
- Missing: no HTML, CSS, SVG, canvas or WebGL path. Playwright is not installed (`.venv/bin/python -c "import playwright"` fails, and `requirements.txt` lists only numpy, scipy, librosa, opencv-python-headless and pillow). Node is present on this machine (`/opt/homebrew/bin/node`).

**Concrete improvement.** Add a `render_html` layer source, as a hybrid and not a replacement.
- New file `engine/htmlpaint.py` plus a caption kind and an overlay in `engine/ext/html_layer.py`.
- Contract for authors: an HTML file defines `window.renderFrame(t, params)` which sets DOM, canvas or SVG state for time t synchronously and returns nothing. The page body has a transparent background. The driver awaits `document.fonts.ready` once, then for each frame calls `page.evaluate('t => window.renderFrame(t)', t)` and `page.screenshot(omit_background=True, type='png')`.
- Interface in `style.json`: `"overlays": [{"kind": "html_layer", "src": "layers/card.html", "params": {...}, "t0_beat": 0, "t1_beat": 8}]` or `"captions": {"kind": "html_caption", "src": "layers/caption.html"}`. The words and their times from `edl['words']` are passed as JSON into `renderFrame`.
- Hybrid flow: before the main loop, `htmlpaint.prerender(edl, spec, cache_dir)` renders all RGBA frames for the layer's span to `cache/html/<hash>/%05d.png`. The hash covers the HTML, params and fps, so reruns are free. During `render()`, the overlay function loads frame `f - f0`, premultiplies it, and blends it like any other caption layer. No change to the Pillow and OpenCV loop is needed, and the grade, camera moves and sound all stay where they are.
- What it adds: real web typography (variable fonts, OpenType features, `text-wrap`, proper kerning), CSS layout (flex, grid) for cards and lower thirds, SVG and canvas for diagrams and charts, WebGL shaders, and reuse of the design-library's web animation sources. The parent folder `/Users/student/dev/design-library/` holds vendored sources such as `pixijs`, `dotlottie` and `LottieFiles` (seen in a directory listing, their contents were not audited), so those could be driven by `renderFrame(t)` too.
- Cost. These figures are estimates, not measured here. A 720 by 1280 transparent screenshot likely takes tens of milliseconds, so an 18 s layer at 30 fps (540 frames) is plausibly 20 to 60 s on top of the current render. Memory is a Chromium process (a few hundred MB). The install is `pip install playwright` plus `playwright install chromium` (a download of a couple of hundred MB). The dependency is optional: if Playwright is missing, the overlay logs a clear message and the style falls back to the Pillow caption kind. Parallelism is limited by the "no parallel heavy local tools" rule, so render pages serially in one browser.
- Determinism rules to enforce in the HTML: no `Date.now`, no `requestAnimationFrame` timing, no CSS transitions or animations (drive everything from `t`), seeded random only.
- Size: about 200 lines Python (`htmlpaint.py`), 60 lines for the ext module, one example layer (about 80 lines HTML). Roughly one day with a test.

### 2.2 Real reference assets

**What it is.** In the video's words: "give it a reference in real assets because on its own, Claude will default to all-caps centred text on a gradient which really looks like AI Slop." The point is that a generator with no concrete visual inputs collapses to the statistical mean. Feeding real logos, screenshots, product shots and a reference frame breaks that.

**Does the engine do it already? Partly, and a little more since 12 October.** The `th_cards` overlay of `talking-head-split` (`engine/ext/talking_split.py`) takes a `cards_dir` of real screenshots and recordings and cuts them into the card rectangle on the measured schedule, falling back to generated stand-ins. It is the first real-asset hook, still style-specific, with no manifest.
- `engine/assets/` contains only `fonts/` (Anton, Archivo Black, Bebas Neue, Instrument Serif, Inter Tight, Playfair Display, Space Grotesk, with OFL texts and `LICENSES.md`). Footage and music for tests are self-generated (`engine/gen_clips.py`, `engine/synth.py`).
- One asset-placing hook exists: `engine/ext/logo_card.py` takes `"image": "/abs/path/logo.png"` in a style's `overlays` and draws it on an end card. It is single-purpose and uses absolute paths.
- The source clips that styles were learned from sit in `edits/_source/` but are reference material for analysis, not something a style can place.
- The engine already guards against the "all caps centred on a gradient" default in a different way: the `kinetic` caption kind (`engine/ext/kinetic.py`) uses a heavy face, scale contrast on a key word and depth text. That addresses typography, not imagery.

**Concrete improvement.** A per-style asset manifest.
- New file per style: `edits/<style>/references.json`, plus an `assets/` folder beside it. Schema: `{"logos": [{"id": "acme", "file": "assets/acme.png", "bg": "dark|light", "safe_pad": 0.08}], "screens": [{"id": "dash", "file": "assets/dash.png", "focus": [0.5, 0.3]}], "cards": [{"id": "pricing", "file": "assets/pricing.png", "caption": "Pricing page"}], "refs": [{"file": "assets/ref-frame.jpg", "note": "target look"}]}`.
- New module `engine/assetlib.py` with `load(style_dir)` returning ids to resolved paths and validating that files exist. A new overlay kind `asset_card` in `engine/ext/asset_card.py` places an asset by id with `at` (a beat, phrase or word match), a move (reuse `fx.ease`) and a frame (rounded corners, shadow-free plate, device bezel optional). `logo_card.py` then reads its image through `assetlib` instead of an absolute path.
- `plan.py` change: `build_edl` accepts `assets` and lets a rule say `{"fx": "asset_card", "asset": "dash", "at": "phrase", "when": {...}}`, placed by the existing rule engine in `place_rules`.
- A reference-frame check belongs to the grading loop (section 2.5): compare the render's palette and layout statistics to the `refs` entries.
- Size: about 120 lines for `assetlib.py` plus `asset_card.py`, small edits to `plan.py` and `make_edit.py` (a `--assets` flag). Small to medium.

### 2.3 Closed-form spring physics

**What it is.** In the video's words: "enforce real spring physics... Ban basic CSS so Claude has to actually use closed-form springs." A damped spring has an exact solution in t, so the position at any frame is computed directly. There is no CSS transition, no per-frame integration (no accumulated error or order dependence), and any frame can be rendered or seeked to independently.

**Does the engine do it already? Partly. The core has easing only, and a closed-form spring was added on 12 October in `engine/ext/typeset.py` (`spring(t, zeta, omega)`, all three damping regimes), used by every element of `kinetic-card-explainer` (`engine/ext/kinetic_card.py`, `pop()`).**
- `fx.py` `ease(name, u)` offers only `linear`, `in_cubic`, `out_cubic`, `out_expo`, `in_out`, `out_back`, `in_expo`. These are fixed curves on a normalised u from 0 to 1, with no overshoot control other than the fixed `out_back` constant 1.70158.
- Callers all use this: `ext/kinetic.py` rise (`_ease('out_cubic', ...)` over `cfg['rise']` seconds, with a `slam` scale from the same curve), `captions.py` `word_pop` (`out_back`), `ext/logo_card.py` (`out_cubic`), `ext/lyric_word_beat.py` (`out_cubic`, `in_out`, `out_back`), `ext/hud_lyric.py` (`out_cubic`).
- Because easing is normalised to a duration, an animation always finishes exactly at its span end. A spring never "finishes", it settles, which reads as physical and can be cut at any moment without a visible jump.

**Concrete improvement.** The helper exists but sits in an extension module. Move it into the core: add `spring()` to `fx.py` (or a new `engine/spring.py` imported by `fx`) and register spring names in `ease`.

With natural frequency ω0 = sqrt(k / m) and damping ratio ζ = c / (2 sqrt(k m)), a step from 0 to 1 with zero initial velocity has these exact solutions:
- Underdamped (ζ < 1), with ωd = ω0 sqrt(1 - ζ²):
  `y(t) = 1 - exp(-ζ ω0 t) * (cos(ωd t) + (ζ ω0 / ωd) * sin(ωd t))`
- Critically damped (ζ = 1):
  `y(t) = 1 - exp(-ω0 t) * (1 + ω0 t)`
- Overdamped (ζ > 1), with s1 = -ω0 (ζ - sqrt(ζ² - 1)) and s2 = -ω0 (ζ + sqrt(ζ² - 1)):
  `y(t) = 1 - (s2 * exp(s1 t) - s1 * exp(s2 t)) / (s2 - s1)`

All three give y(0) = 0 and y'(0) = 0. A start value a and end value b is `a + (b - a) * y(t)`. A velocity carried in from an earlier animation (v0, to retarget a spring mid-flight) adds a term `v0 * t * exp(-ω0 t)` for ζ = 1, and the matching sine or two-exponential terms otherwise.

```python
def spring(t, k=170.0, c=26.0, m=1.0):
    """Closed-form step response of a damped spring, 0 -> 1. t in seconds, no state."""
    if t <= 0: return 0.0
    w0 = (k / m) ** 0.5; z = c / (2.0 * (k * m) ** 0.5)
    if z < 1.0:
        wd = w0 * (1 - z * z) ** 0.5
        return 1 - math.exp(-z * w0 * t) * (math.cos(wd * t) + z * w0 / wd * math.sin(wd * t))
    if z == 1.0:
        return 1 - math.exp(-w0 * t) * (1 + w0 * t)
    r = (z * z - 1) ** 0.5; s1 = -w0 * (z - r); s2 = -w0 * (z + r)
    return 1 - (s2 * math.exp(s1 * t) - s1 * math.exp(s2 * t)) / (s2 - s1)

SPRINGS = {'snappy': (300, 30, 1), 'bouncy': (170, 12, 1), 'soft': (120, 22, 1), 'heavy': (200, 40, 2), 'wobble': (180, 8, 1)}
```

- Wiring: `ease('spring:bouncy', u)` is awkward because `ease` takes a normalised u. Add `fx.spring_at(name, t_seconds)` and let callers pass seconds. Change `kinetic.py` (rise and `slam`, via a new `cfg['spring']` key, default unset so existing demos are unchanged) and `captions.py` `word_pop`. `logo_card.py` can use `soft` for its logo entrance.
- A settle-time helper `settle(k, c, m, tol=0.01)` (numerically scanned once) lets `plan.py` and `check.py` know when the motion is effectively still, which also feeds the dead-frame detector.
- Test: a unit test comparing `spring()` against a small RK4 integration at 1 ms steps, tolerance 1e-4, for the three regimes.
- Size: about 40 lines plus 15 lines per call site. Small. Value is moderate, because the existing styles deliberately use hard swaps and short eases (the `lyric-word-beat` style is `anim: none`), so springs matter mainly for the kinetic and card styles.

### 2.4 Dead-frame hunting

**What it is.** In the video's words: "hunt down dead frames and re-render them." The on-screen example read "Scene 2 is 2/10: 21 dead frames, nothing moves after..." A dead frame belongs to a run of consecutive frames where nothing on screen changes. In a motion graphic that means an animation finished early and the scene sat frozen.

**Does the engine do it already? No, only a cut detector.**
- `check.py` `detect_cuts(video, fps, thr_mult)` already decodes the rendered output at 64 by 36 grey and computes `d = np.abs(np.diff(a, axis=0)).mean((1, 2))`, the per-frame mean difference. It returns `(cuts, d)`, but `check()` uses `d` only to find spikes (`d > max(10, 5 * median)`). Low-difference runs are never examined.
- `event_check.py` checks the start times of effect events against the beat grid. It does not look at pictures.
- Not every still stretch is a defect. Stills get a Ken Burns move (`render.py` `kb_view`) so they move, and the `lyric-word-beat` style deliberately holds one word at a time with hard swaps. A detector therefore needs a threshold per style and must read the plan to see which spans were meant to hold.

**Concrete improvement.** New file `engine/deadframes.py`, reusing the decode in `check.detect_cuts`.
- `find_dead(video, fps=30, size=(96, 160), eps=0.35, min_run_s=0.5)`: decode grey frames, compute the frame difference as the 99th percentile of a blockwise difference (8 by 8 blocks), not the global mean, so a small moving word in a large still frame still counts as motion. A run of at least `min_run_s` where the value stays under `eps` (on a 0 to 255 scale) is dead. Return `[{t0, t1, frames, max_diff}]`.
- Allow-list from the EDL: ignore runs inside shots with `role: outro` or a `hold` flag, and ignore runs that start within 2 frames after a cut (a deliberate beat of stillness after a hit). Per-style override in `style.json` as `"quality": {"dead_eps": 0.35, "dead_min_s": 0.5}`.
- Output: `dead.json` in the out folder and a line in `check.json`. Command line: `deadframes.py edit.mp4 edl.json`.
- Repair action: map each dead span to the shot or event that owns it (from `edl['shots']` and `edl['events']`), then either re-plan (add a `slow_zoom` or `drift` event via `place_rules`, shorten the shot to the next sixteenth) or re-render only that span. This repair step is shared with the grading loop below, so build it once there.
- Size: about 80 lines for the detector, 60 for the repair mapping. Small to medium, and cheap to run (decoding only).

### 2.5 The per-frame grading loop to a score threshold

**What it is.** In the video's words: "You make Claude watch its own frames and critique them... so every frame grades it at 8 out of 10." The author calls this the real secret. A model looks at sampled frames, scores them against a rubric, and the pipeline re-renders low scorers until the score passes or a limit is reached.

**Does the engine do it already? Partly, the pieces exist but no loop.**
- `tools/framegrid.py` builds contact sheets (`--n`, `--times`, reference over render with `--ref`). It is a viewing aid for a human or a model, and it scores nothing.
- `check.py` scores timing only: cut offsets from the sixteenth grid, the beat grid re-detected from the rendered audio, and the attack support under planned beats. It scores no visuals.
- Prior manual review rounds exist (`bw-flash-vo/review-round-1.md` to `review-round-3.md`), so the review practice is there but not automated. Whether the file contents match this loop was not checked.
- Determinism needed for re-render is present: `plan.build_edl(seed=...)` and per-frame RNG in `render.py` mean a changed seed produces a different but repeatable result. What is missing is a span-only render. `render()` renders the whole EDL start to end, so a span re-render needs a new `t_range` argument (and the audio mix reuses the same window).

**Concrete improvement.** New file `engine/grade_loop.py`, with measured checks first and a model critique second.
- Sampling: pick N frames (default 12) from `evenly spaced + 2 frames after each cut + the middle of each caption`, using `framegrid.grab`.
- Local rubric (no API, all measurable, score 0 to 10 per frame, then per span):
  - Legibility: WCAG-style contrast ratio between caption ink and the local background in the caption bounding box (from the RGBA layer alpha), target at least 4.5.
  - Text overflow: caption box inside the safe area (4 percent margins), no clipped glyphs.
  - Dead time: the result of `deadframes.find_dead` for the span.
  - Beat alignment: `check.check()` offsets for the cuts in the span, scored against one frame.
  - Palette and clutter: share of near-black or blown pixels, edge density, to catch washed-out spans.
- Model critique (optional, `--critic claude`): send the contact sheet with the rubric to the Claude API and request JSON `{"span": [t0, t1], "score": 0-10, "issues": [...], "suggestion": "..."}`. Cache by frame hash. Needs an API key, so default is off.
- Loop: render, grade, and for each span scoring below `--target` (default 8) re-render with `seed_offset += 1` stored per shot in `edl.json` (a new `shots[i].seed_offset` field read by `render.py` when building the per-frame RNG and by `plan` for clip choice). Stop at `--max-iter` (default 3) and keep the best-scoring take per span. Write `grade_report.json` and `grade_report.md` with the contact sheets and the final scores.
- Small changes elsewhere: `render.render(..., t_range=None)` to render a span to a temp file, and a splice step using `ffmpeg -c copy` on cut boundaries (spans should snap outward to shot boundaries so the splice is clean).
- Size: about 250 lines for the loop, 60 for the span render, 40 for the splice. Medium to large, and the span render is the hardest part. Caution: the grade is only as good as the rubric, so keep the 8 out of 10 threshold per rubric item, not one blended number.

### 2.6 Beat-locked cuts with sound synthesised in code

**What it is.** In the video's words: "synthesise the sound in code and lock every cut to the beat." Sound effects and music are generated by code and their timing is computed from the same beat grid as the cuts.

**Does the engine do it already? Yes, mostly.**
- Synthesised sound effects: `sfx.py` registers `whoosh`, `impact`, `riser`, `click`, `tick`, `hiss`, `swell` and `glitch_s` (all generated with numpy noise, filters and envelopes, no samples), placed by `sfx.mix(duration, events)` at `e['t'] + e['offset']`, with `end_at_t` so risers finish on the beat. Each uses `seed=i`, so the mix is repeatable.
- Synthesised music for tests: `synth.py` (`kick`, `snare`, `clap`, `hat`, `riser`, `make(bpm, bars, seed, kind)`) with a `.truth.json` of the exact tempo.
- Beat locking: `plan.py` lays cuts on the beat grid and frame-quantises them (`sh['t0'] = round(sh['beat0'] * P * fps) / fps`), snaps to phrase boundaries within `phrase_snap_beats`, and the planned offset from the sixteenth grid is reported in the EDL. `audio.py` fits the grid and refines it to the drum attack (about 2 ms). `check.py` measures the result independently, from the rendered video and audio.
- Gaps: the effect placement uses a fixed 30 fps frame grid so cuts land within 16.7 ms (the README quotes a mean error of about 8 ms). SFX are not pitched to the key of the song, and there is no sidechain from the sfx to the music (only `gap` events mute the music and the voiceover ducks it, in `render.py` `mix_audio`). Caption word impacts exist through `caption_sfx` in `plan.py`.

**Concrete improvement.** Small additions, not a rebuild.
- A key-aware `sfx` option: detect the song's root with a chroma pass in `audio.py` (`analyse` adds `key`), and let `impact` and `riser` take `pitch_hz` so the tone sits in key. Roughly 40 lines.
- A short sidechain duck of the music under every `impact` (10 to 15 dB for 120 ms) in `mix_audio`, which would make hits read louder without clipping. Roughly 15 lines.
- A subframe offset: `sfx` start times are already float seconds, so sound can sit on the true beat while the picture cut sits on the nearest frame. Add `lead_ms` per style to start the sound a few ms early or late for perceived sync. Roughly 5 lines.
- Value: low to medium, since this part of the engine is the strongest.

### 2.7 OpenMontage (github.com/calesthio/OpenMontage)

Source labels: **[repo]** was read on 12 October 2026 from github.com/calesthio/OpenMontage (the README, the LICENSE file and the root and `skills/` listings via fetch). **[video]** is from Video B. **[unverified]** is not checked. The fetch tool summarises pages with a small model, so wording quoted from the README below is as reported by that summary, and the LICENSE quotes were also relayed through it. Cam should open the LICENSE once to confirm the text before anything is copied.

**What it is.**
- [repo] "The first open-source, agentic video production system", described as turning an AI coding assistant into a video production studio: 12 production pipelines, 100+ tools and 700+ agent skill files.
- [repo] "There is no code orchestrator. Your AI coding assistant IS the orchestrator." The agent reads manifests, skills and knowledge packs and calls registered tools.
- [video] 65,000 stars. [repo] the page showed 67.5k stars, 8.6k forks and 478 commits on 12 October 2026, consistent with the video's figure of about 65.9k on 10 October.

**Architecture [repo].**
- Three knowledge layers: tools and pipeline definitions, then skills (markdown conventions and quality standards), then external technology knowledge packs.
- Top-level folders: `.agents/skills/`, `.claude/`, `.cursor/`, `.codex/`, `.github/`, `assets/`, `backlot/` (a local live production board), `docs/`, `ink-theater/`, `lib/` (config, checkpoints), `pipeline_defs/` (YAML manifests), `remotion-composer/`, `schemas/`, `scripts/`, `skills/` (with `core`, `creative`, `meta`, `pipelines` and `INDEX.md`), `styles/` (YAML visual style playbooks), `tests/`, `tools/` (100+ registered tools), plus `AGENT_GUIDE.md`, `PROJECT_CONTEXT.md`, `PROMPT_GALLERY.md`, `CLAUDE.md`, `AGENTS.md` and per-assistant guides.
- Every pipeline runs `research -> proposal -> script -> scene_plan -> assets -> edit -> compose`, with human approval gates at proposal, script, scene plan, assets and publish.
- A decision audit trail logs each major choice (provider, style, music, voices, renderer) with alternatives and confidence scores.
- Composition engines: Remotion (React, spring-animated scenes, stat cards, charts, word-level captions), HyperFrames (HTML, CSS and GSAP for kinetic typography and rigged SVG animation), and FFmpeg. The runtime is locked at the proposal stage.

**Supported pipelines [repo].** Animated Explainer, Animation, Avatar Spokesperson, Cinematic, Clip Factory, Documentary Montage, Hybrid, Localization and Dub, Podcast Repurpose, Screen Demo, Talking Head, and Character Animation.

**The "paste a reel" flow.**
- [video] "Paste a reel you love, it breaks down the pacing, the scenes, and the style, then builds yours from that."
- [repo] Accepts YouTube, Reels, Shorts, TikToks or local clips. The agent analyses "transcript, pacing, scenes, keyframes, and style", then proposes 2 to 3 differentiated concept variants with an honest tool path, cost estimates and a sample preview before full production. The `skills/` listing showed no file named for reference analysis, and the README and listing mention no dedicated reference folder. The analysis code was not read, so how it measures pacing is **[unverified]**.

**Quality controls [repo].**
- Post-render self-review: "after every render, the runtime runs ffprobe validation, extracts frames at 4 positions to check for black frames and broken overlays, analyzes audio levels for silence and clipping", plus delivery promise verification. The video is only output if review passes.
- Slideshow risk scoring on six dimensions: repetition, decorative visuals, weak motion, shot intent, typography overreliance and unsupported cinematic claims. Pre-compose validation blocks renders that fail it.
- Source media is probed before planning.

**Dependencies and costs [repo].**
- Python 3.10+, FFmpeg, Node.js 18+, and an AI coding assistant. Install is `git clone` then `make setup` (Python deps, Node modules for Remotion, Piper TTS). Optional GPU for local video models.
- No mandatory paid keys for the basic path: Piper TTS offline, Archive.org, NASA and Wikimedia footage, Pexels, Unsplash and Pixabay with free keys, local Remotion or HyperFrames rendering.
- Paid providers are optional (video: Kling, Seedance, Veo, Runway, MiniMax and others. Images: FLUX, Imagen and others. Voice: ElevenLabs, OpenAI, Azure. Music: Suno, ElevenLabs).
- Budget governance: cost estimate before execution, default approval pause at $0.50 per action, default total cap $10, spend reconciliation. Example productions listed at $1.33 to about $5.
- The repo documentation did not mention Playwright or Chrome. Video A's Playwright stack is a different project from OpenMontage.

**Licence.**
- [repo] GNU Affero General Public License, version 3 (AGPL-3.0), dated 19 November 2007. The LICENSE file opens "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3, 19 November 2007", and the README badge and footer say "GNU AGPLv3". The file contains no extra terms or exceptions beyond the standard text.
- Clauses that matter, quoted from the file:
  - Section 5(c): "You must license the entire work, as a whole, under this License to anyone who comes into possession of a copy."
  - Section 13: "Notwithstanding any other provision of this License, if you modify the Program, your modified version must prominently offer all users interacting with it remotely through a computer network (if your version supports such interaction) an opportunity to receive the Corresponding Source of your version by providing access to the Corresponding Source from a network server at no charge..."
- What this means for Cam's engine (a plain reading, not legal advice):
  - Reading OpenMontage and reimplementing ideas, interfaces and approaches in his own code is not restricted. Copyright covers expression, not ideas. Keep a clean-room discipline: write from the idea, do not paste or closely paraphrase files.
  - Copying or adapting its code, skill files, prompts or YAML playbooks into the engine makes the engine a derivative work. Under 5(c) the whole combined work would then have to be offered under AGPL-3.0, and under section 13 anyone interacting with a modified version over a network would have to be offered the source. That would apply to any hosted service built on the engine, which matters if the engine is ever used behind a paid product or an API.
  - Using OpenMontage unmodified, as a separate program on Cam's machine, carries no such obligation. The risk starts at copying into the engine, or modifying and hosting it.
  - Remotion, which OpenMontage uses, has its own licence terms for companies. That is **[unverified]**, not checked here, and relevant only if Cam adopts Remotion.

**What Cam's engine could reuse (ideas and interfaces only, because of the licence).**
- The stage contract `research, proposal, script, scene_plan, assets, edit, compose` with a checkpoint file between stages. Cam's engine already has plan then render (`edl.json`), so a `proposal` stage in front is the new part.
- The decision audit trail idea: write why each choice was made (clip, effect, style) beside `edl.json`, with the rejected alternatives. The engine's `plan.py` has the data already.
- Slideshow risk as a named score: repetition, weak motion, typography overreliance.
- Post-render self-review with sampled frames, black-frame and broken-overlay checks, and audio silence and clipping checks (`check.py` has no audio-level or black-frame check today).
- Spend and budget guardrails, relevant only if the engine starts calling paid APIs, such as the Claude critic in section 2.5.
- Style playbooks as data (`styles/` YAML). The engine already has `style.json`, so there is nothing to take.

**What it should adopt (concrete features, written independently).**
1. Reference-video analysis command `engine/ref_analyse.py` that reads a video and writes a draft `style.json` (shot-length histogram, cut rhythm, caption placement, grade statistics). The existing `analysis.json` in each style folder and the manual process in `edits/README.md` are the starting point, so this automates the library's own method. New file, large.
2. A `proposal` step: `make_edit.py --propose` writes two or three plan variants (different seeds or styles) with a contact sheet each, then `--pick N` renders one. Changes `make_edit.py`, uses `framegrid.py`. Medium.
3. A pre-compose and post-render gate in one module `engine/gate.py`: black frames, caption overflow, audio silence and clipping, a repetition score over `edl['shots']` clip ids, and the dead-frame result. Changes `check.py` callers in `make_edit.py`. Medium, and it shares code with section 2.4 and 2.5.
4. `decisions.json` written by `plan.build_edl` listing each major choice with alternatives. Small.

### 2.8 Found by measuring the two videos (not stated in either)

These came out of the shot and caption measurements for the two new styles (`talking-head-split/analysis.json`, `kinetic-card-explainer/analysis.json`) and are already in the engine.

- Cuts follow the speech, not the beat. In A the 11 head reframes land a median of 0.02 s from a word start, and in B the 19 scene cuts land a median of 0.05 s from one. The engine's cuts were quantised to the music grid only, so `make_edit.py` gained `snap_cuts_to_words` (style key `cuts.snap_words {tol, min_len}`). Cost: `check.json` now reports beat offset as worse for these styles, which is intended. Worth doing next: a `check.py` metric for cut-to-word offset so the check scores the right thing for voice styles.
- Voice-only styles need a style-level mix. Both videos have no music bed (digital silence between phrases) and sit near -13.8 LUFS. `render.mix_audio` already read `edl['audio']['music_gain']`, but nothing wrote it, so `make_edit.py` now copies `style.audio` into the edl. Worth doing next: a `loudnorm` pass to -14 LUFS on the mix, which the engine does not have.
- Caption chunking differs by style. A uses 5.6 words and two lines per swap, B uses one or two words. Both are hard swaps with the first-word onset, so the engine's caption kinds (`serif_chunk`, `kc_word`) share the timing and differ in layout only.
- Layer clocks are independent. A's card changes four times faster than its talker, B's scene changes every 1.4 s under captions that change every 0.5 s. The engine's overlay hook (`render.overlay`) supports this, and `kc_scene` and `th_cards` use their own schedules.

## 3. Summary table

| Technique | Verdict | Effort | Value |
| --- | --- | --- | --- |
| Render loop with an HTML painter (Playwright, hybrid RGBA layers) | partial | L | high |
| Real reference assets (`references.json`, `asset_card`) | partial (`cards_dir` on one overlay) | M | high |
| Closed-form springs (`spring()` and presets) | partial (helper added in `ext/typeset.py`, core still eases) | S | medium |
| Dead-frame hunting (`deadframes.py`) | missing | S to M | high |
| Per-frame grading loop (`grade_loop.py`) | partial | L | high |
| Beat-locked cuts and synthesised sound | have | S | low |
| OpenMontage ideas (proposal step, gate, decisions log, reference analysis) | missing | M | medium |

### Ranked: the three most valuable improvements

1. Dead-frame hunting plus the shared gate (`deadframes.py`, then `gate.py`). It reuses a decode the engine already does in `check.py`, needs no new dependency, and catches the most visible defect in a generated edit, so it pays back at once and also becomes the dead-time input of the grading loop.
2. The grading loop to a threshold (`grade_loop.py` with a measurable local rubric first). It turns the engine from "renders what it planned" into "renders and fixes what it planned", and the first useful version needs no API, only the span re-render in `render.py`.
3. Real reference assets (`references.json` and `asset_card`). The engine's weakest area is not timing or typography but having nothing real to put on screen, and this is the direct answer to the video's "AI slop" point, at modest cost and with no new dependency.

The HTML painter (2.1) ranks just below these. Its ceiling is the highest of all because it unlocks web layout, SVG and WebGL, but it brings Chromium and a slower render, so it is best added after the gate and the loop exist to keep its output honest.

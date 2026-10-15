# Edit engine

Takes any clips and any song and returns a video in one of the learned styles, with the cuts, moves, transitions, sound effects and captions placed on the new song's beats. One command:

```
cd /Users/student/dev/design-library/edits
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt     # once
.venv/bin/python engine/make_edit.py --style bw-flash-vo --clips ./footage --music ./song.mp3 \
    --captions "line one\nline two with a *key* word" --duration 18 --aspect 9:16 --out ./out
```

Output in --out: edit.mp4, edl.json (the plan, editable), song.json (beat analysis), check.json (beat alignment) and a cache folder for clip analysis. `--edl out/edl.json` re-renders an edited plan. `--plan-only` writes only the plan. `--list` prints styles, effects, caption kinds, overlays and sound effects.

Options: `--clips` folder of videos and stills (jpg, png, webp). `--music` any audio file. `--captions` text, or a .txt or .srt file (one line is one phrase, `*word*` marks emphasis). `--voiceover` speech audio, transcribed with the local Whisper model for caption timing and mixed over ducked music. `--transcribe` uses Whisper word times of the song's own vocals as captions. `--duration` seconds, `--aspect` 9:16 or 16:9 or 1:1, `--res` short side in pixels (720), `--fps` (30), `--seed` for a different but repeatable plan, `--music-start` seconds to start from a chosen part of the song.

## How it works

1. audio.py analyses the song with librosa onsets and an autocorrelation tempo with a 120 BPM prior, fits a constant beat grid, refines period and phase to the physical drum attack (about 2 ms), picks the downbeat phase from the kick, and finds energy per beat, roles (low, mid, high), drops (kick and bass returning at a bar start), phrase boundaries (every 8 beats and at drops) and onsets tagged kick, snare or hat.
2. clips.py analyses each clip: scene cuts, motion energy per 0.125 s, brightness, sharpness and a focus point (Apple Vision faces, then Vision person mask, then a saliency centroid). Stills are treated as zero-motion clips that get a Ken Burns move.
3. plan.py picks a window of the song (starting on a downbeat, placing the first drop where the style wants it), lays the cut schedule on the grid from the style's shot-length distribution per section role, snaps cuts to phrase boundaries, assigns clips to shots by matching motion energy to song energy (with repeat penalties), then applies the style's rules for moves, transitions, sound effects, grade and captions. The result is edl.json.
4. render.py decodes each shot with ffmpeg, crops it to the aspect around the focus point, grades it, applies camera moves, draws captions and overlays, applies transition effects centred on the cuts, encodes through an ffmpeg pipe and mixes the song window, the synthesised sound effects and the optional voiceover.
5. check.py detects the cuts in the rendered video and compares them with the beat grid (and, for the synthesised test songs, with their known true grid), in milliseconds.

macOS only for the Vision helpers (engine/vision.swift builds on first use with swiftc, bin/vision is gitignored). Everything else is portable. ffmpeg needs no drawtext or libass, text is drawn with Pillow.

## Style files

A style is edits/<name>/style.json. Every key is optional except name.

```
name, description
defaults      aspect "9:16"|"16:9"|"1:1", duration seconds
layout        band true puts a 16:9 picture in a black vertical frame
structure     intro_beats, outro_beats, drop_at (fraction of the edit where the first drop should land), drop_beats,
              end_on_bar, vo_start_beats (beat at which a voiceover starts)
cuts          lengths: {role: [[beats, weight], ...]} for roles intro, low, mid, high, drop, outro, default
              first_shot_beats, min_beats, phrase_snap_beats, bar_align, loop_seam_beats (a short final shot repeating the first picture)
clips         select energy_match | sequential | shuffle, avoid_repeat, jitter, energy_weight, prefer_faces
speed         choices [[multiplier, weight]], ramps [{when, ramp:{s0, s1, portion|portion_beats, shape}}]
              (speed ramps; portion is a shot fraction [a, b], portion_beats is beats from the shot's
              own start, anchoring the ramp's duration to the music rather than the shot's length)
grade         base {...}, timeline [{frac, grade:{...}}] (keyframes interpolated over the edit)
              grade keys: bw, saturation, contrast, brightness, gamma, tint [r,g,b], vignette, grain
moves         rules that place effects, see below
sfx           rules that place sound effects (kind, at, when, gain, offset, dur, end_at_t)
captions      kind (staircase, word_pop, subtitle and any registered kind), font, size_frac, colours, timing
overlays      [{kind, ...}] per-frame overlays registered with @render.overlay
```

A rule is `{fx, at, when, span_beats, params, layer, min_gap_beats}`. `at` is cut (every shot boundary), shot (a span of each shot, `portion` [a, b]), beat (`every`, `offset`, `dur_beats`), drop, phrase, onset (`bands`, `min_strength`) or time (`frac` or `sec`). `when` filters: role, downbeat, phrase, drop, first, last, bar_every, index_mod, shot_beats_min, shot_beats_max, frac_min, frac_max and p (probability). `span_beats` is [beats before, beats after] the anchor. `layer` is pre (before captions, camera moves and grade) or post (after captions, flashes and transitions). The engine ships these effects: punch_in, slow_zoom, zoom_pulse, drift, shake, whip, zoom_blur, flash, dip_black, strobe, invert, rgb_split, glitch, heat, mask_flash, tile, freeze, grade, letterbox, plus each style's own in engine/ext. Run `make_edit.py --list` for the live list.

Timing of captions: `captions.timing.mode` is grid (one word per `step_beats` from `start_beat`), bar_phrases (a line per `bars_per_phrase` bars) or onsets (words on kick and snare hits). Word times from Whisper (--voiceover, --transcribe) or an SRT are used as given.

## Auto style (decisions.json)

`--style auto` (the default when `--style` is omitted) reads the footage with brief.py and scores every
style in choose_style.STYLE_REGISTRY with choose_style.choose(), writing the result to `--out/decisions.json`
before anything is rendered:

```
{
  "features": { ...brief.from_footage()'s flat dict: clip_count, stills_share, screen_capture_share,
                speech, speech_share, large_face_share, long_clip_share, mean_motion, mean_saturation,
                mean_luma, subjects, has_cards, has_caption_source, mood, audience, caption_kind,
                voiceover, duration, aspect... },
  "style": "bw-flash-vo",        // the chosen style, or null on no fit
  "score": 0.83,                 // the winner's score, 0 to 1
  "runner_up": "lyric-word-beat",
  "runner_up_score": 0.61,
  "scores": { "bw-flash-vo": 0.83, "lyric-word-beat": 0.61, ... },   // every style's score
  "gap": null                    // null on a clean fit; else the named reason (e.g.
                                  // "talker_no_captures", "margin 0.090 under 0.15")
}
```

`brief.py`'s extra auto-mode flags: `--mood`, `--audience`, `--caption-kind`, `--cards-dir`. On no fit
(best score under choose_style.FLOOR, or margin under choose_style.MARGIN_MIN against the runner-up),
make_edit.py exits without rendering; decisions.json is still written so the gap is visible.

## Adding to the engine

Drop a module in engine/ext/ (auto-imported). Register effects with `@fx.fx('name')` (signature fn(img, k, p, ctx), k has u, x, t, span, ctx has w, h, fps, frame, rng, mask, store), caption kinds with `@captions.caption('kind')` (returns an RGBA layer or None), overlays with `@render.overlay('name')` (returns the frame), and sound effects with `@sfx.sfx('name')`. Then use the names in a style.json.

## Test material

engine/make_testdata.sh builds self-generated songs (synth.py) and footage (gen_clips.py) into edits/_testdata, so demos never redistribute anyone's media. The synthesised songs have a .truth.json with the exact tempo, which check.py uses to report how far the rendered cuts are from the true beat grid.

## Known limits

Constant-tempo songs only (a drifting tempo falls back to the average grid), 30 fps output grid so cuts are quantised to 33 ms (mean error about 8 ms), speech and vocals sit under the beat detector (a rap acapella may fool the downbeat choice), the segmentation masks are per frame and can flicker on thin edges, and effects are approximations of the original editor's plugins, not the plugins themselves.

## Typography and depth (defaults since 12 October 2026)

Caption kind `kinetic` (engine/ext/kinetic.py) is the default treatment: a heavy display face (Anton, Archivo Black, Bebas Neue, Space Grotesk and Inter Tight are bundled in engine/assets/fonts under the SIL OFL 1.1), one to three words per chunk, a scaled key word, tight leading, lower-left or centred placement, no drop shadow (a scrim, a solid band `plate: band`, or the difference blend `plate: diff` with one contrast target per word and a soft halo), `anim: none` for hard swaps, `hold_until_next` and `hold_last` so the row never empties, `auto_contrast` ink on pale pictures.

Depth text: `captions.depth_text {enabled, behind_ratio, min_visible, min_cover, max_cover}` (default enabled, 0.5). Key (emphasis) words alternate behind and in front of the subject through the matte, supporting words stay in front. The matte is Apple Vision person segmentation, and for footage with no person a saliency-seeded GrabCut matte (kind `object`). A behind word the subject hides more than 1 - `min_visible` stays in front so it can be read. hud_row phrases alternate the same way.

Other keys added in this pass: grade `target_luma` and `target_strength` (pull a shot to a mean luma), captions timing `fill` and `fill_whole` (repeat phrases to cover the edit), sfx kind `gap` (mutes the music), hud captions `gap_em`, `fit_up`, `wipe_color`, `band_color`, `hold_last`, hud effects `texture`, `band_y`, `normalise`, `reroll`, overlay `hud_end_matte`. tools/framegrid.py makes reference-over-render contact sheets for reviews.

## Speed ramps and slow motion (Stage 8, 15 October 2026)

Speed ramps are beat-anchored (`render.ramp_anchor_mode()` returns `'beat'`): a ramp rule's `portion_beats`
is read in beats from the shot's own start rather than as a fraction of the shot's length, so the same
`portion_beats: [0, 1]` ramp takes one beat on a four-beat shot and one beat on a one-beat shot, instead of
stretching to fill whichever shot it lands on. The older `portion` fraction key still works for anyone who
wants shot-relative timing instead. Any shot whose ramp (or base `speed`) dips under `render.SLOWMO_THRESHOLD`
(0.92x) now decodes at a raised frame rate through ffmpeg's `minterpolate` (blend mode), which interpolates
between the two neighbouring source frames, rather than the plain `fps` filter, which just repeats the
nearest decoded frame when upsampling — so a ramped-down shot reads as smooth slow motion, not a stutter.
`edits/stacked-story-split/` is a best-effort, explicitly incomplete prototype for a dual-stream (stacked
two-pane) layout: it ships with no `style.json`, so it cannot be selected by name or by the chooser.

# velocity-ramp-edit (designed)

"learned": "designed". No studied TikTok or Reels edit matches this name in `edits/_study/corpus.json` as of
this stage, so this style is assembled from existing and newly extended engine primitives rather than measured
off a real reel, per `plan.md`'s Stage 8 scope. If a studied reel naming this style arrives in the corpus
later, measure it against that and update this file, rather than taking this description as ground truth.

## What it is

A fast-cut montage where every downbeat-aligned shot of a beat or more drops into a one-beat slow-motion
ramp (1.0x down to 0.3x and back), and the drop's first shot gets a two-beat ramp down to 0.25x. The point of
the style is the ramp mechanism it exercises, built this stage: `edits/engine/render.py`'s
`ramp_anchor_mode()` (`'beat'`) and `edits/engine/plan.py`'s `portion_beats` handling, so the ramp always
takes exactly one (or two) beats of music regardless of whether the shot it lands on is one beat or four.

- `speed.ramps` rules use `portion_beats: [0, 1]` and `[0, 2]`, not the older `portion` shot-fraction key.
  `plan.py` (`build_edl`, speed-ramp loop) converts beats to a shot-local fraction by dividing by the shot's
  own `shot_beats`, so a one-beat ramp on a four-beat shot only covers the first quarter of it, where before
  this stage a ramp's `portion` fraction always spanned the same proportion of the shot no matter its length.
- Any shot whose ramp dips under `render.SLOWMO_THRESHOLD` (0.92x) decodes through ffmpeg's `minterpolate`
  (blend mode) instead of the plain `fps` filter, so the slow-motion portion blends between real decoded
  frames rather than repeating the nearest one. `ShotReader.__init__` picks this per shot from the ramp's
  minimum multiplier (`render.py`, the `mn`/`slowmo` logic added this stage).
- Base speed is a light 1.0-1.15x `speed.choices` pick, so the non-ramped portion of each shot already reads
  faster than real time, making the ramp's drop to 0.3x read as a bigger contrast.
- `clips.prefer_faces: true` and a short `avoid_repeat` (2) keep the ramped shots on footage worth slowing
  down for, since a ramp on a low-motion background grab would read as pointless rather than dramatic.

## Why these choices, given no measured reel

- The 1-beat default ramp length and 0.3x floor sit inside the range the engine's own `fx.ease` shapes already
  support (`in_out`), and 0.3x is slow enough to read as deliberate slow motion without the shot running out of
  source frames for most clip lengths in `tests/dachshunds/assets` (checked: none of that set's clips are under
  2 seconds, so a 1-beat ramp's extra source time needed stays well inside what `plan.py`'s existing
  "clip too short" fallback (`avail = max(0.3, ...)`) would otherwise have to rescue).
- The drop gets a longer, deeper ramp (2 beats, 0.25x) than the rest of the edit (1 beat, 0.3x) because that is
  the one moment in every other `style.json` in this repo with a `structure.drop_at` key that gets its own,
  more extreme treatment (`strobe-photo-dump`'s drop strobe, `bw-flash-vo`'s drop riser+impact pairing).
- No caption block: this style is about cut and motion contrast, not a captioned message, so it omits
  `captions` the same way `strobe-photo-dump` does (confirmed safe by the same `.get()` read pattern in
  `edits/engine/plan.py` and `make_edit.py`).

## Registry

Not added to `edits/engine/choose_style.py`'s `STYLE_REGISTRY`, which is explicit and reserved for the six
measured, learned styles (its own docstring: "not every `edits/<name>/style.json` on disk"). It exists as a
style folder selectable by name with `--style velocity-ramp-edit`. Stage 10's rationale should say whether it
was a candidate for any of the three re-renders.

## Try it

```
cd edits && .venv/bin/python -I engine/make_edit.py --style velocity-ramp-edit \
  --clips tests/dachshunds/assets --music music/index.json --duration 15 --out /tmp/velocity-test.mp4
```

Check the ramp mechanism directly:

```
cd edits && .venv/bin/python -I -c "
import sys; sys.path.insert(0,'engine'); import render
assert render.ramp_anchor_mode() == 'beat'
print('beat-anchored ramps: pass')"
```

## What the engine does not capture

Since this style is designed, not measured, there is no real-reel detail to list as uncaptured. The honest
gap is the reverse: nothing here has been checked against how a real speed-ramp edit actually times its ramps
against a drop, or whether 0.3x is the right floor, because no such reel is in the corpus yet.

## When to use it

Footage with clear motion worth slowing into (a jump, a turn, a reveal) cut to a track with a clean beat grid
and a single obvious drop. A poor fit for static or low-motion footage, since the ramp would just read as the
picture going soft rather than dramatic, and a poor fit for anything needing a caption, since none is defined.

## stacked-story-split: best effort, shipped incomplete

This stage's second item, `stacked-story-split` (a dual-stream, two-concurrently-decoded-video-readers
layout), did not land. See `edits/stacked-story-split/README.md` for what was attempted and why it stops
short of a working style.

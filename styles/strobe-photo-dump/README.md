# strobe-photo-dump (designed)

"learned": "designed". No studied TikTok or Reels edit matches this name in `edits/_study/corpus.json` as of this stage, so this style is assembled from existing engine primitives rather than measured off a real reel, per `plan.md`'s Stage 7 scope. If a studied reel naming this style arrives in the corpus later, measure it against that and update this file, rather than taking this description as ground truth.

## What it is

A "camera-roll dump" cut: the look of flicking fast through a photo roll in time with a beat. Every style primitive it uses already exists in the engine (`flash`, `strobe`, `slow_zoom`, `zoom_blur` in `edits/engine/fx.py`, and the automatic Ken Burns pan the engine already gives any still image clip in `edits/engine/plan.py`'s `kenburns` assignment). No engine code changes were needed for this stage.

- Shots are snap-length: a quarter to one beat, shortest in the intro/low/mid sections, almost all a quarter beat on the drop.
- A white flash frame lands on roughly half of the cuts through the intro/low/mid sections and three-quarters of the cuts in the high section, so the montage reads as a fast flicker rather than a clean cut.
- The drop gets a hard one-beat strobe pulse (`strobe`, alternating full-white and picture frames) instead of a single flash, plus a riser into an impact.
- A still photo dropped into the clip list gets its own slow Ken Burns pan automatically (the engine already drifts any `clip_kind == "image"` shot this way); a video clip gets a slow push-in instead, so stills and video grabs intercut without looking mismatched.
- `clips.select: energy_match` with a short `avoid_repeat` window (3) keeps the dump feeling like it is drawing from a big roll even with a handful of source files.

## Why these choices, given no measured reel

- Flash-per-cut density and the strobe-on-drop choice follow `bw-flash-vo`'s own measured numbers (`edits/bw-flash-vo/README.md`: "about 40 per cent of cuts in the high-energy stretch, 12 per cent elsewhere") scaled up, since a photo-dump reads as more flash-heavy than a flash-cut montage with a voiceover to protect — there is no voiceover here to keep legible.
- Shot lengths (0.25-1 beat) sit at the short end of every other style's `cuts.lengths` tables in this repo (`edits/lyric-word-beat/style.json`, `edits/bw-flash-vo/style.json`), since a photo dump has no caption or voiceover to pace against and can cut as fast as the beat grid allows.
- No caption block and no `needs_mask`: a photo dump is pictures and sound, not a captioned message, so this style carries neither key (both are read with `.get()` everywhere in `edits/engine/plan.py` and `make_edit.py`, so omitting them is safe, confirmed by `grep -n "style\['captions'\]\|style\['needs_mask'\]" edits/engine/*.py` finding nothing).

## Registry

Not added to `edits/engine/choose_style.py`'s `STYLE_REGISTRY`. That registry is explicit and reserved for the six measured, learned styles (its own docstring: "not every `edits/<name>/style.json` on disk"); a `"designed"` style with no studied reel behind it is not auto-selectable by the brief-driven chooser built in Stage 4. It exists as a style folder a human (or a later stage's rationale) can pick by name with `--style strobe-photo-dump`. Stage 10's rationale should say whether it was a candidate for any of the three re-renders.

## Try it

```
cd edits && .venv/bin/python -I engine/make_edit.py --style strobe-photo-dump \
  --clips tests/dachshunds/hud/clips --music music/index.json --duration 15 --out /tmp/strobe-test.mp4
```

## What the engine does not capture

Since this style is designed, not measured, there is no real-reel detail to list as uncaptured (contrast the "What the engine does not capture" sections in the learned styles). The honest gap is the reverse: nothing here has been checked against how a real photo-dump edit actually paces its flashes, its strobe length, or its mix of stills to video, because no such reel is in the corpus yet.

## When to use it

Fast-turnover footage with little or no spoken content and a handful of stills or short grabs to cycle through: a highlight reel, a "we did this" recap, a product-shot dump. It is a poor fit for anything that needs a legible caption or voiceover, and the drop's one-beat strobe should be disabled or dimmed for viewers sensitive to flashing (lower `moves[1,2].when.p` and `moves[3].params.count`, or drop the `strobe` move entirely).

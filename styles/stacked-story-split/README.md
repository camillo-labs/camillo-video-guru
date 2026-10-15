# stacked-story-split (incomplete, best effort)

No `style.json` ships in this folder, so this style cannot be selected by name (`--style stacked-story-split`)
or by the chooser's `STYLE_REGISTRY` in `edits/engine/choose_style.py`. It is a note on what was scoped and
why Stage 8 stopped short, per `plan.md`'s own instruction to ship this item incomplete rather than land a
style the chooser could pick that does not actually work.

## What it was meant to be

A two-pane, stacked "story split" layout: two independently cut video streams running at once, one above the
other (or side by side) in the 9:16 frame, each on its own cut rhythm and its own clip pool, rather than the
single shared timeline every other style in this repo renders.

## Why it does not land cleanly in the time this stage had

`edits/engine/render.py`'s frame loop (`render()`, from line 272) tracks exactly one active shot at a time:
one `si` (shot index), one `reader` (`ShotReader`), one `mreader` (mask reader), advanced together as the
frame clock `t` crosses each shot's `t0`/`t1` boundary. Every per-frame step after that, the grade, the mask,
the caption and effect `events` list, the audio mix, assumes a single picture is being built per frame.

A dual-stream layout needs, at minimum:

- A second, independent `(si, reader, mreader)` triple with its own shot list and its own advance-on-boundary
  check, since the two panes cut on their own rhythms rather than sharing one.
- `edits/engine/plan.py`'s `build_edl` to emit two shot lists against the same beat grid (so the two panes
  stay musically in sync even when they cut at different points) rather than the one `shots` list every
  style's EDL carries today, which is a schema change, not just a render-loop change, since `edl.json` is read
  by `gate.py`, `make_edit.py` and the acceptance tests' own `decisions.json`/`check.json` readers.
  Two readers decoding concurrently also roughly doubles ffmpeg subprocess load per frame, which was not
  profiled against the render budget established at `tests/dachshunds/hud/clips` sizes in the earlier stages.
- A compositing step that takes both panes' graded images and lays them into one `cW x cH` frame (a straight
  top/bottom split, or something adaptive to each clip's own aspect, was not decided) before the existing
  caption and overlay layers run on the combined frame, since captions and overlays are currently written
  against one image per frame, not two.
- A decision on how `moves` (cut-triggered effects like `flash`) and `sfx` placement work when the two panes'
  cuts do not land on the same frame, which the single-timeline `events` list and `match()` `when` clauses
  (`edits/engine/plan.py`) have no concept of today.

None of these four is a small patch on top of the existing single-stream render loop; together they are
closer to a second render path than an extension of the first, and Stage 8's scope (119 minutes expected, the
widest range in the plan, shared with `velocity-ramp-edit`) did not leave room to build and test that safely
alongside the beat-anchored ramp work, which is the item `plan.md` names as the stage's primary, non-optional
deliverable.

## What is actually needed to finish this

1. Decide the two-stream `edl.json` schema first (a `shots_b` list alongside `shots`, or a `tracks: [...]`
   list replacing the single `shots` key), and update every reader of `edl.json` (`render.py`, `gate.py`,
   `make_edit.py`) to handle it, old single-track EDLs included, before writing any render-loop code.
2. Duplicate the `(si, reader, mreader)` state and its boundary-advance `while` loop in `render()` for a
   second track, then composite before the caption/overlay layer.
3. Extend `plan.py`'s clip-assignment loop to run twice, once per track, sharing the beat grid but drawing
   from (optionally) separate clip pools so the two panes do not just show the same footage.
4. Write a `style.json` with a `layout.split` key (`top_bottom` or `left_right`) once the above renders a
   frame at all, then run it through the same acceptance pattern as every other style in this repo
   (`make_edit.py --style stacked-story-split ... && test -s ...mp4`).

## Status

Not started beyond this scoping note: no code in `render.py` or `plan.py` touches a second stream as of this
stage, since the schema decision in step 1 above has to happen before any of that code is safe to write, and
making that decision well needs more than the time this stage had left after the ramp work. The chooser in
`edits/engine/choose_style.py` does not and should not offer this style, per `plan.md`'s Stage 8 note that
"Stage 4's chooser should not offer stacked-story-split if it didn't land."

# Rationale: green-label, auto-selected

## Style
`choose_style.choose()` picked **bw-flash-vo** with score 0.85, well clear of the runner-up
**lyric-word-beat** at 0.45 (`decisions.json`). The clips carry no speech, no stills, no screen
capture and a high mean motion (8.12), none of which alone would clear the chooser's floor without
a mood hint, so `--mood edgy` was passed (matching `edits/tests/green-label/style.json`'s existing
hand-authored pick and `choose_style.py`'s `MOOD_ENERGETIC` set). That one input moved the score
from a no-fit to 0.85.

## Music
Picked from `music/index.json`, which holds only the 4 seeded Kevin MacLeod tracks across moods
`calm`, `energetic`, `playful`, `premium`. The library is below Cam's N3 target of 15 tracks
across 4 moods: N5's Codex handoff (`music/index-new.json`) would close this gap, but its done-file
(`_meta/health/codex-reels-2026-10-15.done`) does not exist yet, so this render used the seeded
library, not a forced or degraded pick (one track fits the mood here, so no "forced pick, library
below target" wording applies this time, but the shortfall against N3's target still stands).

## Captions and finish
`captions.txt` was supplied, giving the chooser `has_caption_source: true`; the caption kind
resolved to `kinetic`.

## SFX and licence
13 cleared sound effects (`sfx/index.json`, Stage 5's replacement for the 13 personal-use-only
clips). `gate.licence_check(edl, '../sfx/index.json')` returned `True`: every audio sample this
render used carries a licence id and credit in the index.

## Gate results
- **Safe-area:** 66/66 sampled caption frames (breach rate 1.0) sit outside the union safe box
  (`gate.py:22-23`, x 11-82%, y 15-65%). Every breach is on the x-axis: `x0` ranges 0.045 to 0.072,
  below the 0.11 left bound, so the kinetic caption's left edge sits in the zone a platform's own
  UI (handle, follow button) could cover. This is not a new finding this stage; it is a measured
  fact about the existing `bw-flash-vo` style surfaced by Stage 3's gate for the first time against
  a real re-render.
- **Flash frequency:** 9 flashes in the busiest one-second window, against WCAG 2.3.1's limit of 3
  (`breaches_wcag_2_3_1: true`). This is exactly the risk plan.md's G4 human gate names for
  `bw-flash-vo`: Cam should review this before the render is shown anywhere public. Nothing in this
  stage changed the style to fix it, per the plan's own instruction not to quietly alter a shipping
  style's look.
- **Dead frames:** 32 near-static runs detected, none longer than the 3.5s pacing budget. Pass.
- **Licence:** pass (above).

## Comparison
`sidebyside.mp4` plays the named baseline (`tests/green-label/green-label.mp4`, sha256
`1f0ae00ab8e91dc0ed45f2cc7906c0b36ef83a9592db2048eeb9e71913537a3e`) then this render back to back,
each with its own audio. 35.5s total, both video and audio streams present (`ffprobe`).

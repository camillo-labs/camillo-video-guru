# Rationale: fontainebleau, auto-selected

## Style
`choose_style.choose()` picked **lyric-word-beat** with score 0.85, well clear of the runner-up
**bw-flash-vo** at 0.0 (`decisions.json`). Without a mood hint the footage alone does not clear the
chooser's floor for any style, so `--mood heritage` was passed, matching the captions' UNESCO
heritage-site subject and `choose_style.py`'s `MOOD_CALM` set, and matching
`edits/tests/fontainebleau/style.json`'s existing hand-authored pick of `lyric-word-beat`.

## Music
Picked from the same 4-track seeded `music/index.json` as the other two tests, still below Cam's
N3 target of 15 tracks across 4 moods for the same reason (N5's handoff not yet folded in, done-file
absent).

## Captions and finish
`captions.txt` was supplied; the caption kind resolved to `kinetic`.

## SFX and licence
13 cleared sound effects (`sfx/index.json`). `gate.licence_check` returned `True`.

## Gate results
- **Safe-area:** 15 of 113 sampled caption frames (breach rate 0.133) sit outside the safe box.
  Every breach here is on the y-axis: `y1` reaches 0.782, above the 0.65 upper bound, so the
  caption's bottom edge occasionally runs into the zone a platform's caption bar or progress ring
  could cover. Smaller in share than green-label's breach, but real.
- **Flash frequency:** 5 flashes in the busiest one-second window, against WCAG 2.3.1's limit of 3
  (`breaches_wcag_2_3_1: true`). This is a new finding, not one plan.md's G4 gate already named:
  G4 flagged `bw-flash-vo` and `a03a-fontainebleau` by name, but this render used
  `lyric-word-beat`, which still trips the same limit. Worth carrying to Cam alongside G4 rather
  than treating G4 as the complete list of flash-risk styles.
- **Dead frames:** 8 near-static runs detected, none longer than the 3.5s budget. Pass.
- **Licence:** pass (above).

## Comparison
`sidebyside.mp4` plays the named baseline (`tests/fontainebleau/fontainebleau.mp4`, sha256
`9dbd263d153a25c7c64234162da45ace98c6af991e37e9d4571f0377db1b86c2`) then this render, each with its
own audio. 36.1s total, both video and audio streams present.

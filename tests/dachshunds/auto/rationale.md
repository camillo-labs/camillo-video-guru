# Rationale: dachshunds, auto-selected

## Style
`choose_style.choose()` picked **lyric-word-beat** with score 0.85, clear of the runner-up
**bw-flash-vo** at 0.0 (`decisions.json`). Without a mood hint the footage alone (10 clips, no
speech, no screen capture, moderate motion 4.49) does not clear the chooser's floor for any style,
so `--mood calm` was passed, matching the test's own `README.md` ("mostly calm dogs") and
`choose_style.py`'s `MOOD_CALM` set (`choose_style.py:29`), and matching
`tests/dachshunds/style.json`'s existing hand-authored pick of `lyric-word-beat`.

## Music
Picked from the same 4-track seeded `music/index.json` as the other two tests (122 bpm bed,
`check.json`'s `bpm_rendered_audio: 122.08`), still below Cam's N3 target of 15 tracks across 4
moods for the same reason as green-label and fontainebleau: N5's Codex handoff
(`music/index-new.json`) has not been folded in, since its done-file
(`_meta/health/codex-reels-2026-10-15.done`) does not exist.

## Captions and finish
`captions.txt` was supplied, giving `make_edit.py` real word timings to draw (`edl.json`'s
`words` list starts "Dachshund means badger dog. Bred to flush out badgers..."), matching
`facts.md`'s text. `decisions.json`'s own `has_caption_source` feature reads `false` because that
flag is computed from the brief step before `--captions` is applied to the render call, not from
the render itself; the safe-area gate below measures real caption boxes moving frame to frame, so
the captions did draw.

## SFX and licence
No sound effects in this render (`edl.json` has none), and no cleared sample library exists yet:
all 13 entries in `sfx/index.json` still read "unknown, personal and internal use only until
cleared". `gate.licence_check(edl, '../sfx/index.json')` returned `True` because there was nothing
to check. (Corrected by final-review, 15 Oct.)

## Gate results
- **Safe-area:** 13 of 106 sampled caption frames (breach rate 0.123) sit outside the safe box
  (`gate.py:22-23`, x 11-82%, y 15-65%). Every breach is on the y-axis: `y1` reaches 0.782, above
  the 0.65 upper bound, the same bottom-edge pattern fontainebleau shows with `lyric-word-beat`.
- **Flash frequency:** 2 flashes in the busiest one-second window, against WCAG 2.3.1's limit of
  3 (`breaches_wcag_2_3_1: false`). Pass, clear of G4's concern (which names `bw-flash-vo` and
  `a03a-fontainebleau`, neither used here).
- **Dead frames:** 52 near-static runs detected, none longer than the 3.5s pacing budget. Pass.
- **Licence:** pass (above).

## Comparison
`sidebyside.mp4` plays the named baseline (`tests/dachshunds/out/edit.mp4`, sha256
`be6875976cf77d8e6a122575c481b3ab7db080dafd7f72e741c421a6d2482786`) then this render back to
back, each with its own audio. 29.6s total, both video and audio streams present (`ffprobe`).

## Known defect (final-review, 15 Oct)
This render is 1280x720 (16:9, `edl.json` `"aspect": "16:9"`), because auto mode took the style's 16:9
default when no `--aspect` was passed. `make_edit.py` now defaults auto mode to 9:16, and a re-render is
queued as follow-up build work. The music pick also came from the style's mood, not the `--mood` above.

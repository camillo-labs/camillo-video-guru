# Gate report, 2026-10-15 (Stage 3)

Run with `edits/engine/tools/gate_report.py`, which calls `gate.safe_area_check`,
`gate.flash_frequency_check` and `gate.dead_frame_check` against the three real tests
(green-label, fontainebleau, dachshunds, both its plain and HUD variant) and the six demo
renders already on disk. This reports what currently breaches each gate; Stage 3's scope
(plan.md:174) is to report, not to fix any of it.

## Safe area (union safe box: x 11-82%, y 15-65%)

| Render | Caption kind | Breach rate | Frames checked |
|---|---|---|---|
| green-label | kinetic | 1.0 | 67 |
| fontainebleau | kinetic | 0.324 | 102 |
| dachshunds | kinetic | 0.145 | 69 |
| dachshunds HUD variant | hud_row | 1.0 | 75 |
| fontainebleau-bw-flash-vo | kinetic | 1.0 | 97 |
| fontainebleau-hud-lyric-heat | hud_row | 1.0 | 89 |
| fontainebleau-hud-lyric-light | hud_row | 1.0 | 89 |
| green-label-hud-lyric-heat | hud_row | 1.0 | 98 |
| green-label-hud-lyric-light | hud_row | 1.0 | 98 |
| green-label-lyric-word-beat | kinetic | 0.153 | 144 |

Every `hud_row` render breaches on every checked frame: that caption kind centres its row at
`cfg.get('y', 0.5)` of the frame height but the measured glyph height pushes its top above
`SAFE_Y[0]=0.15` or its bottom below `0.65` for the sizes these styles use (`size_frac` 0.133 of
H). The `kinetic` renders breach whenever a style anchors the block near the bottom
(`y` around 0.82, per `ext/kinetic.py`'s docstring default) — green-label and
fontainebleau-bw-flash-vo do this on every frame, while fontainebleau and
green-label-lyric-word-beat use a higher anchor and only breach on a minority of frames. None of
this is fixed here; a later stage (the gate is consulted by Stage 4's chooser, per plan.md:197)
decides whether to move the anchors or exempt kinds whose semantic position is deliberate (e.g.
a bottom third lower-third caption is a common, accepted placement outside this box; this gate
enforces the platform-UI union box literally, as plan.md:174 specifies, and reports the gap
rather than loosening the box on its own authority).

## Flash frequency (WCAG 2.3.1, limit 3/second, no small-area exemption)

| Render | Max flashes/second | Breaches |
|---|---|---|
| green-label | 2 | no |
| fontainebleau | 1 | no |
| dachshunds | 1 | no |
| dachshunds HUD variant | 1 | no |
| fontainebleau-bw-flash-vo | 2 | no |
| fontainebleau-hud-lyric-heat | 1 | no |
| fontainebleau-hud-lyric-light | 1 | no |
| green-label-hud-lyric-heat | 2 | no |
| green-label-hud-lyric-light | 1 | no |
| green-label-lyric-word-beat | 1 | no |

None of the ten renders breach WCAG 2.3.1 today. `fontainebleau-bw-flash-vo`, named for its
flash cuts, still only reaches 2/second measured on the rendered pixels, under the limit of 3.

## Dead frames (nothing static for more than 3.5s)

One breach: `fontainebleau-hud-lyric-heat`, a 4.4s static run from 0.63s to 5.03s (the
opening hold before the first cut). All other renders stay under the 3.5s pacing budget.

## Render errors

None across all ten renders. `safe_area_check`'s standalone caption context (no picture, no
subject matte: see `gate.py`'s comment above the per-frame `ctx` it builds) was enough for both
caption kinds in use, `kinetic` and `hud_row`; neither reads a field this context leaves unset in
a way that crashes (`kinetic.py` and `hud_lyric.py`'s `hud_row` both guard picture/mask reads with
`.get()`). If a later style adds a caption kind that needs `ctx['shot']` or an actual picture
(e.g. a kind doing a real difference blend), `render_errors` in the JSON this tool prints is where
that would show up, per render, without stopping the other nine.

## Reproduce

```
cd /Users/student/dev/build-overnight-improve-video-edit-e/edits
.venv/bin/python -I engine/tools/gate_report.py
```

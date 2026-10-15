# What this engine took from Will's making-short-videos

Will Leikauskas's `making-short-videos` (MIT, `/Users/student/dev/_study/making-short-videos`) is a Remotion,
ffmpeg, Python and ElevenLabs skill. The full comparison is in
`compare-making-short-videos-2026-10-15.md`. This note says what was ported, what was written up instead and what
was left alone. Licence text and credit are in `THIRD_PARTY.md`.

## Ported, with tests

| Rank | Idea | Where it is now | From Will's file | Test |
| --- | --- | --- | --- | --- |
| 1 | Final mix loudness: one measured static gain to -14 LUFS, then a limiter. | `engine/loudness.py`, called by `render.mix_audio` | `scripts/mix_soundtrack.py`, last section | `tests/test_loudness.py` |
| 2 | Velocity to motion blur: 0.12 px per px/frame, cap 22, nine preset steps, blur along the faster axis. | `engine/motionblur.py` and the `pan_blur` effect in `engine/fx.py` | `references/motion.md` (fast moves) and `remotion-kit/mblur.tsx` | `tests/test_motionblur.py` |
| 3 | Voice pauses at the quietest 10 ms, 60 ms fade-out, 15 ms fade-in. | `engine/voicepause.py` | `scripts/mix_soundtrack.py`, voice section | `tests/test_voicepause.py` |

### Loudness

The old final stage scaled the mix down only if one sample passed 0.89, so two edits could land at very different
volumes. The new stage measures once with ffmpeg `loudnorm` (measure only), applies one linear gain to -14 LUFS,
and runs `alimiter` at -1 dBTP with `level=false`.

Two fixes came from a review of the first version:

- `alimiter` now runs with `latency=true`. Without it the limiter delays the whole mix by about 5 ms.
  `test_limiter_keeps_an_impulse_at_its_sample_position` puts an impulse at sample 44100 and checks it stays there.
  Without the flag it comes out at sample 44319.
- Both ffmpeg calls check their return code and raise `RuntimeError` with stderr. The limiter also raises if it
  returns a different number of frames. `FfmpegFailureTests` covers all three.

Differences from Will: his true peak target is -1.5 dBTP, ours is -1.0. The limiter works on sample peaks, so
inter-sample true peak can still read slightly above the ceiling (-0.65 dBTP on the bw-flash-vo demo). Setting
`TARGET_TP` to -1.5 in `engine/loudness.py` gives more room if a platform is strict.
`scripts/compare_loudness.py` reproduces the before and after numbers.

### Motion blur

`motionblur.sigma_for_velocity(v)` is the rule. `directional_blur(img, vx, vy)` applies a Gaussian along the faster
axis, the OpenCV equivalent of his `feGaussianBlur stdDeviation="s 0"`. The `pan_blur` effect slides the frame with
an ease and sizes its blur from the slide's own speed, so a style can use it without working out the numbers.

Existing effects (`whip`, `zoom_blur`, `shake`) are unchanged. `whip` could move to `sigma_for_velocity` later.
That would alter the look of the six learned styles, so it needs a side-by-side render first.

### Voice pauses

`plan_cuts`, `insert_pauses`, `shift_time` and `shift_words` are the whole voice section of his mixer as a library.
It is not wired into the planner or `render.mix_audio`. Our styles caption the voice as recorded and never re-cut
it. Wiring it in takes four steps and about half a day:

1. A style option `voice.pauses` with `[time, length]` pairs, read in `plan.py`.
2. `plan.py` calls `plan_cuts` on the decoded voice and `shift_words` on the Whisper words, so captions match.
3. Shot times after each pause move by the pause length, or the pause becomes a held shot.
4. `render.mix_audio` calls `insert_pauses` with the same cuts.

## Written up, not ported

| Idea | Where it is in Will's repo | Why not now |
| --- | --- | --- |
| Demucs stem separation and pitch-classified transients when learning a style | `scripts/analyse_reference.py` | Heavy dependency, and styles are learned about twice a month. Worth it if that changes. |
| Subframe motion blur: render at 4x fps and average four frames with `tmix`, no blur across hard cuts | `references/motion.md`, sources section (from Prompt Motion) | It is a render-time change, not a helper. It costs four times the render and needs a per-cut guard. A good next experiment for `whip` and `zoom_blur`. |
| Band-limited, sin squared faded sound effects levelled to the voice | `scripts/mix_soundtrack.py`, `shape()` and `place()` | `sfx.mix()` already aligns the measured peak to the cut. The band-limiting is a small win once real clips are cleared. |
| Red-flags table of AI tells (fades, icon sets, ducked music, single-pass loudnorm, synced pop-ups) | `references/making-it-yours.md` | A checklist for a human. Could become gate checks later. |
| Ridged-burn shader transition | `scripts/burn_transition.py` (Apache-2.0) | Not used. See `THIRD_PARTY.md`. |
| Dead-frame check | `scripts/deadframes.py` | `engine/gate.py` already has an adaptive one. |
| ElevenLabs voice tools | `scripts/elevenlabs_tools.py` | The engine takes any voice file. No new dependency. |

## What Will's repo could take from this one

See the end of `compare-making-short-videos-2026-10-15.md`: the style-file system, frequency-selective voice
ducking, and the post-render gates.

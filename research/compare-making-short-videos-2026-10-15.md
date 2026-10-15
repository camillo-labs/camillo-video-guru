---
title: "Comparison: Will Leikauskas's making-short-videos against our edit engine"
namespace: reference
kind: reference
authority: derived
source: doc
captured: 2026-10-15
source_url: https://github.com/Mokzy/making-short-videos
found_by: build/video-ideas-from-will, per Cam's brief of 2026-10-15
---

**Update, same day, in this repo:** the motion blur mapping and the voice-pause cutting listed below as not yet adopted are now `engine/motionblur.py` and `engine/voicepause.py`. `research/from-will.md` says what was ported, what was not and why. Paths below say `edits/`, which is `engine/`, `styles/` and `tests/` here.

**Bottom line:** our engine already builds most of what Will's repo does well. The one real gap, the final
mix's loudness, is now fixed in `edits/engine/loudness.py`.

The clearest thing Will's repo could take from ours is the style-file system itself, not any one effect.

## What each repo is

Will's `making-short-videos` is MIT licensed, except `scripts/burn_transition.py`, an Apache-2.0 port of
HyperFrames' ridged-burn shader that needs credit if copied (nothing here does). It is a Remotion plus
ffmpeg plus Python plus ElevenLabs pipeline, distilled as a Claude Code skill from 12 rounds of client
feedback on one fundraising ad. It reads a single reference video, measures it (`scripts/analyse_reference.py`: 10 fps
frame sheets, scene cuts, Demucs stem separation, a faster-whisper transcript, an audio map, transient
detection classified by rising or falling pitch), writes the numbers it found into `references/*.md`
(`motion.md`'s easing and px/frame-to-blur table, `sound.md`'s mix recipe), and a human (or Claude, reading
the skill) then builds a new edit in Remotion against those numbers. There is no automatic style chooser
and no beat grid; a human picks the shape of the edit from `references/case-study.md` and
`making-it-yours.md` (a deliberate "choose your own look first" discipline, plus a red-flags table of
AI-video tells: fades, icon sets, ducked music, single-pass loudnorm, synced staggered pop-ups).

Ours (`design-library/edits`) is a Python plus ffmpeg engine that takes any clips and any song and
renders a cut in one of several learned styles (`edits/README.md`), with cuts, moves, transitions, sound
effects and captions placed on the new song's beat grid (`edits/engine/audio.py`'s onset and tempo
analysis). A style is a declarative `style.json` the engine interprets (`edits/engine/README.md`), so new
looks are learned once from a reference video and reused on any footage after, and `--style auto`
(`choose_style.py`, built in the overnight branch this work sits on top of) scores every style against the
footage and brief without a human picking.

## Capability table

| Capability | Will's repo | Ours | Which is better, and why |
| --- | --- | --- | --- |
| Reusable style | One Remotion project per edit, rebuilt by hand or by Claude reading the skill each time | `style.json` is data the engine reads; six styles ship, each reused on new footage and music with no new code | Ours. Will's own `making-it-yours.md` says as much: the repo teaches a method, it does not ship a reusable renderer. |
| Beat alignment | None measured in the repo; cuts follow the reference's timing, not a new track's grid | `audio.py`'s onset-based tempo and beat grid, cuts snapped to the sixteenth grid or phrase boundaries, verified post-render (`check.py`) | Ours, for anything set to music. Will's approach has no equivalent because it is not built for arbitrary new tracks. |
| Automatic style choice | A human (or an agent reading `case-study.md`) decides the look before building | `choose_style.py` scores every style against measured footage and brief features, writes `decisions.json` with a score, a runner-up and a named "no fit" reason | Ours now has this; Will's repo deliberately keeps the decision human ("choose your own look first" as the stated discipline, not a gap). |
| Reference analysis | `analyse_reference.py`: 10 fps frame sheets, scene cuts, Demucs stems, faster-whisper transcript, an audio map, transient detection with pitch direction | Each style folder's `analysis.json` plus a hand-written `filmcraft.md`, built the same way (measure a reference, write numbers) but without Demucs stem separation or automatic transient classification | Theirs is more automated on this one axis (Demucs, pitch-classified transients); ours relies on the recipe being captured once per style rather than re-run per edit. Worth adopting if we start learning new styles often (see below). |
| Final mix loudness | `mix_soundtrack.py`: one static gain from a single loudnorm measurement pass to -14 LUFS (TP -1.5), then `alimiter` (`level=false`); explicitly never single-pass loudnorm, "it pumps" | Was a plain peak scale with no loudness target at all (`render.py`'s old `mix_audio`: scale down only if the loudest sample passed 0.89) | Theirs was better, and is the one idea this work adopted: see below. |
| Voice/music balance | One constant music gain relative to speaking RMS, no ducking | Frequency-selective ducking: `audio_shape.py`'s `vo_low_duck` pulls only the low band under the voice and lets it swell back, mids untouched | Ours, by design: a full-band duck (Will's stated practice, chosen to avoid a bad duck envelope) is a blunter tool than touching only the band that actually masks speech. Worth telling Will about. |
| Sound effect placement | Band-limited sfx, sin²/cos² faded, peak-aligned to the cut | `sfx_library.py`'s `offsets()` records each clip's measured attack and peak time; `sfx.mix()` subtracts the peak offset so the measured transient, not the file start, lands on the cut | Roughly equivalent; both solved the same problem (a sample's loudest moment should land on the beat, not its first sample) the same way, independently. |
| Dead-frame / static-shot QA | `deadframes.py`: 96x160 grayscale, 8x8 block diff, 99th-percentile score, flags runs frozen ≥0.5 s | `gate.py`'s `dead_frame_check`: grayscale block-diff against a per-video median threshold, flags runs over the style's pacing budget (3.5 s default) | Ours is closer to adaptive (a per-edit median rather than a fixed threshold), and ships alongside a safe-area and WCAG 2.3.1 flash-frequency gate Will's repo does not have. |
| Accessibility / platform safety | Not covered | `gate.py`: safe-area box (union of TikTok/Reels/Shorts UI safe zones) checked against the real rendered caption alpha canvas, and a WCAG 2.3.1 flash-frequency check | Ours; a real gap in Will's repo worth naming to him. |
| Licence clearance | `THIRD_PARTY.md`, checked by a human | `gate.py`'s `licence_check` fails a render automatically if any named sfx sample is not in the cleared index | Ours automates what Will's repo leaves to a human to remember. |
| Motion blur | `mblur.tsx`: SVG `feGaussianBlur` directional blur keyed to the nearest of 9 preset steps, driven by `motion.md`'s px/frame-to-blur table (0.12 px per px/frame, capped at 22) | `fx.py`'s `zoom_blur`, `shake`, `whip` (a horizontal motion-blur convolution scaled to whip speed); no general velocity-to-blur helper for arbitrary camera moves | Will's repo, on this one axis: a documented numeric mapping from measured velocity to blur amount, reusable across any move. Worth adopting narrowly (see below), separate from this run's loudness work. |
| Voice-pause handling | Cuts the voice track itself at the quietest 10 ms window with 60/15 ms fades, so edits in speech never click | No equivalent found; voiceover is used as given (Whisper word times for captions), never re-cut | Theirs; not adopted here because our styles do not currently re-cut voiceover audio, only caption it, so the gap has no live consequence yet. Worth a note for whenever that changes. |

## Ideas worth taking, ranked

1. **Final mix loudness (adopted this run).** The engine's final gain stage had no loudness target: a loud
   single hit would turn the whole mix down, a sparse edit with no hits would never be turned up, so two
   edits could land at very different perceived volumes with no way to predict which. `edits/engine/loudness.py`
   now does what Will's `mix_soundtrack.py` does: one ffmpeg `loudnorm` measurement pass (not the dynamic,
   pumping mode), one static linear gain from that single number to -14 LUFS integrated, then ffmpeg's
   `alimiter` (lookahead, `level=false`) to -1 dBTP. Wired into `render.mix_audio`. Tested in
   `edits/tests/test_loudness.py` and shown before/after on a real edit in
   `edits/tests/final-mix-loudness/compare/` (see below).
2. **A numeric velocity-to-motion-blur helper**, worth a narrow follow-up, not done here: `motion.md`'s
   mapping (blur amount scales with measured px/frame, capped) is a small, testable rule our `fx.py` could
   adopt for any move that reports a velocity, not just `whip`. Low cost, not attempted this run because it
   is a separate change from the loudness fix and the brief scoped this run to the top improvements with
   tests and a render, not a full adoption pass.
3. **Demucs stem separation when learning a new style**, worth keeping in mind rather than building now:
   useful only when a new style is being learned from a reference video, which happens rarely (six styles
   in several months). Not worth the dependency weight for how often it would run.
4. **Everything else in the capability table either already exists here in a more automated form (beat
   alignment, style reuse, automatic style choice, dead-frame and licence gates) or is a deliberate choice
   in Will's repo that does not apply to ours** (the human-picks-the-look discipline makes sense for a
   bespoke one-off edit; it would be a regression for an engine whose point is reuse).

## What Will's repo could take from ours

Worth passing on, since Cam may want to share this with Will directly:

- **The style-file system.** `style.json` turns "a look we measured once" into something reusable on new
  footage and a new song with no new code. Right now his repo re-derives a Remotion project from the
  measured numbers each time; a declarative schema over the same measurements (cut lengths per section
  role, grade keyframes, caption timing rules) would let one analysed reference serve more than one edit.
- **Frequency-selective voiceover ducking** (`audio_shape.py`'s `vo_low_duck`) instead of one constant
  music gain. A full-band duck is simpler but blunter; pulling only the band that actually masks speech
  (below 150 Hz here) keeps more of the music audible under the voice and needs no manual gain choice per
  mix.
- **The post-render gates** (`gate.py`): a safe-area check against the real rendered caption alpha canvas
  (not a hand-set `y` field), a WCAG 2.3.1 flash-frequency check, and an automatic licence-clearance check
  that fails a render rather than relying on a human to remember `THIRD_PARTY.md`. None of these depend on
  the beat-grid machinery; they would work against any rendered video.
- **Beat-grid cutting**, if his pipeline ever needs to point an edit at an arbitrary new track rather than
  follow a fixed reference's timing.

## The before/after render

`edits/tests/final-mix-loudness/compare/` holds `before.m4a` (the old plain peak-scale mix) and
`after.m4a` (the new static-gain-plus-limiter mix) rendered from the same `bw-flash-vo` demo edl
(`edits/bw-flash-vo/demo/A/edl.json`, 15 s, with its voiceover and sfx hits), plus `report.json`:

| | before | after |
| --- | --- | --- |
| Integrated loudness | -14.93 LUFS | -14.00 LUFS |
| True peak | -0.73 dBTP | -0.65 dBTP |
| Sample peak | -1.01 dBFS | -1.00 dBFS |

This one demo happened to land close to target under the old method by chance (its loudest sfx hit
roughly matched the 0.89 ceiling the old code used); the point the unit tests make more clearly is that
the old method had no target at all, so a quieter edit with fewer hits was never turned up to match, and a
louder one was turned down by however much its single loudest sample demanded, not by how loud the whole
mix actually was. `edits/tests/test_loudness.py`'s `test_quiet_mix_is_boosted_toward_target` shows the case
the real demo could not: a quiet mix the old code would have left exactly as quiet as it started.

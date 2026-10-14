# making-short-videos

A playbook and toolkit for short vertical videos (ads, reels, explainers) built with Remotion, ffmpeg, Python and
ElevenLabs. It was distilled from twelve rounds of feedback on a 38 s fundraising ad. It works as a
**Claude Code skill**: Claude loads `SKILL.md` automatically when you ask for video work. The `references/`, `scripts/`
and `remotion-kit/` folders are also readable on their own.

> **Make it yours.** Read `references/making-it-yours.md` first. The case study is evidence of what works, not a look
> to reuse: pick your own reference, angle, visual language, type, palette, voice and music.

## Install as a Claude Code skill

```
git clone https://github.com/Mokzy/making-short-videos.git ~/.claude/skills/making-short-videos
```

On Windows, the folder is `%USERPROFILE%\.claude\skills\making-short-videos`. Restart Claude Code, then ask for a video and
it will load the skill. Update with `git pull` inside that folder.

## Requirements

- Node 20+ and a Remotion project (`npx create-video@latest`), plus ffmpeg on PATH.
- Python 3.11+ with `numpy` and `matplotlib`. For studying a reference: `pip install demucs faster-whisper yt-dlp`.
- An ElevenLabs API key in the `ELEVENLABS_API_KEY` environment variable, for voice, music and sound effects.

## What's inside

| Path | Contents |
|---|---|
| `SKILL.md` | The workflow and the red-flags table (what Claude reads first) |
| `references/making-it-yours.md` | Step 0: the style brief |
| `references/case-study.md` | Feedback round by round: root causes and the principles that fixed them |
| `references/reference-study.md` | How to measure a reference reel instead of eyeballing it |
| `references/visual-language.md` | Principles for any visual language, map and caption specs |
| `references/motion.md` | Rules with numbers, a seam catalogue, sources (HyperFrames, Prompt Motion) |
| `references/sound.md` | Voice, music, effects, mixing and loudness: settings and prompts |
| `references/toolchain.md` | Tools, Windows pitfalls, render recipe, QA checklist |
| `references/sources-and-facts.md` | Footage sources and licences, the fact routine, Meta ad constraints |
| `scripts/` | `analyse_reference.py`, `elevenlabs_tools.py`, `mix_soundtrack.py`, `burn_transition.py`, `deadframes.py` |
| `remotion-kit/` | Motion blur, shots, word-timed captions, plus patterns to build |

## Credits

`scripts/burn_transition.py` ports the `ridged-burn` shader from HyperFrames (github.com/heygen-com/hyperframes,
Apache-2.0). The motion rules draw on the Prompt Motion gallery (prompt-motion.com) and the `cinetic` and
`product-film-skill` repos credited in `references/motion.md`.

## Licence

MIT (see `LICENSE`), except `scripts/burn_transition.py`, which ports an Apache-2.0 shader (see `THIRD_PARTY.md`).

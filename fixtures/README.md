# Fixtures

This repo holds code, styles, docs and small JSON and text fixtures. Video, audio and source footage stay out of
git (see `.gitignore`). They live on this Mac in Cam's design-library checkout.

## Where the media is

The media root is `/Users/student/dev/design-library/edits`. The engine finds it through `engine/paths.py`. Set
`VIDEO_ENGINE_MEDIA` to use another folder. Relative paths in an `edl.json` (for example
`_testdata/music/house128.wav`) are relative to it.

| What | Path under the media root | Size | How to get it back |
| --- | --- | --- | --- |
| Generated test songs, clips and voices | `_testdata/` | 67 MB | Run `scripts/make_testdata.sh`. Nothing in it is third-party. The voices (`_testdata/vo/*.aiff`) come from macOS `say`. |
| Dachshunds test footage and music | `tests/dachshunds/assets/` | 54 MB | Download again from the URLs in `tests/dachshunds/sources.json` (Pexels footage, Kevin MacLeod music). |
| Green Label test footage and music | `tests/green-label/assets/` | 80 MB | Same, from `tests/green-label/sources.json`. |
| Fontainebleau test footage and music | `tests/fontainebleau/assets/` | 63 MB | Same, from `tests/fontainebleau/sources.json` (Wikimedia Commons). |
| Rendered films and contact sheets | `tests/*/*.mp4`, `tests/*/auto/*.mp4`, `styles/*/demo/*.mp4`, `*.sheet.png`, `contact*.png` | about 140 MB | Re-render with the command in each test's `README.md`. |
| Sound effect WAV files | `/Users/student/dev/design-library/sfx/` | 4.6 MB | Set `SFX_LIBRARY` to that folder. `sfx/build_from_reels.py` rebuilds them from the two source reels. Their licence is not cleared. |

The footage licences (Pexels, Wikimedia Commons, Creative Commons) do not allow republishing the files as they
are, which is why they are not committed.

## What is committed

Each `tests/<project>/` folder keeps its `edl.json`, `style.json`, `captions.txt`, `facts.md`, `sources.json`,
`credits.md` and `check.json`. Each `styles/<style>/demo/` keeps the `edl.json` and `check.json` of its demo
renders. These are the plans and the beat-alignment reports, not the films.

## Skipped tests

`tests/test_media.py` skips with a message naming the missing file and `VIDEO_ENGINE_MEDIA` when the media is
absent. Everything else runs without it.

## Regenerating the demo and test renders

```
.venv/bin/python engine/make_edit.py --style auto --mood calm \
    --clips /Users/student/dev/design-library/edits/tests/dachshunds/assets/clips \
    --music /Users/student/dev/design-library/edits/tests/dachshunds/assets/music/Raving-Energy.mp3 \
    --captions tests/dachshunds/captions.txt --duration 15 --aspect 9:16 --seed 3 --res 720 --out out/dachshunds
```

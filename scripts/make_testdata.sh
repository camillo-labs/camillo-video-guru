#!/bin/bash
# Builds the self-generated test footage and music into $VIDEO_ENGINE_MEDIA/_testdata (default: _testdata in the
# repo root, gitignored). Nothing here is third-party material.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; ENG="$ROOT/engine"; PY="$ROOT/.venv/bin/python"
OUT="${VIDEO_ENGINE_MEDIA:-$ROOT}/_testdata"
mkdir -p "$OUT/music" "$OUT/clips"
$PY "$ENG/synth.py" --bpm 128 --bars 24 --seed 1 --kind house  --out "$OUT/music/house128.wav"
$PY "$ENG/synth.py" --bpm 100 --bars 20 --seed 2 --kind hiphop --out "$OUT/music/hiphop100.wav"
$PY "$ENG/synth.py" --bpm 140 --bars 24 --seed 3 --kind house  --out "$OUT/music/house140.wav"
$PY "$ENG/synth.py" --bpm 122 --bars 20 --seed 4 --kind hiphop --out "$OUT/music/hiphop122.wav"
[ -d "$OUT/clips/A_9x16" ] || $PY "$ENG/gen_clips.py" --set A --out "$OUT/clips/A_9x16" --aspect 9:16 --height 960
[ -d "$OUT/clips/B_9x16" ] || $PY "$ENG/gen_clips.py" --set B --out "$OUT/clips/B_9x16" --aspect 9:16 --height 960
[ -d "$OUT/clips/A_16x9" ] || $PY "$ENG/gen_clips.py" --set A --out "$OUT/clips/A_16x9" --aspect 16:9 --height 540
[ -d "$OUT/clips/B_16x9" ] || $PY "$ENG/gen_clips.py" --set B --out "$OUT/clips/B_16x9" --aspect 16:9 --height 540
echo done

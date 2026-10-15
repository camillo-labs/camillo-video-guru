Reproduce: `edits/engine/make_testdata.sh`, then for demo-A-house128

    edits/.venv/bin/python edits/engine/make_edit.py --style hud-lyric-heat --clips edits/_testdata/clips/A_16x9 --music edits/_testdata/music/house128.wav --captions $'we run the night\nneon on my chest\nnever look *back*\ncity in the rain\ndrive it all night\nhold the line' --duration 16 --res 540 --seed 1 --out out

and for demo-B-hiphop100 use clips B_16x9, music hiphop100.wav, seed 2 and the lines cold air tonight, stay on the move, from zero to gold, keep it loud, back to the top, let it ring. Footage and music are self-generated. The .sheet.png files are frames of these demo renders only.

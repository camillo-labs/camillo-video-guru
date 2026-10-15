Reproduce: `edits/engine/make_testdata.sh`, then for demo-A-house140

    edits/.venv/bin/python edits/engine/make_edit.py --style hud-lyric-light --clips edits/_testdata/clips/B_16x9 --music edits/_testdata/music/house140.wav --captions $'grab the red\nkeep it moving\nnever slow down\nlights on city\nrun it back\nfeel the *bass*' --duration 16 --res 540 --seed 3 --out out

and for demo-B-hiphop122 use clips A_16x9, music hiphop122.wav, seed 4 and the lines stay in the fog, make it loud, shine through the snow, move with me, bring it home, last call. Footage and music are self-generated. The .sheet.png files are frames of these demo renders only.

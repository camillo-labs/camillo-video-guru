#!/usr/bin/env python3
"""Make a video in a learned editing style from any clips and any song.

  make_edit.py --style lyric-word-beat --clips ./footage --music song.mp3 --captions "line one\nline two" \
               --duration 18 --aspect 9:16 --out ./out

Steps: analyse the song (tempo, beat grid, downbeats, energy, drops, phrases), analyse the clips (scenes, motion,
focus), plan an edit decision list from the style's rules, render with ffmpeg and OpenCV, then measure how well the
cuts sit on the beats. Writes edit.mp4, edl.json, song.json and check.json to --out.
"""
import argparse, json, os, subprocess, sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from paths import STYLES as EDITS   # style folders: styles/<name>/style.json
LT_PY = Path(os.environ.get('VIDEO_ENGINE_WHISPER_PY', Path.home() / '.local/share/lt-voice/venv312/bin/python'))


def find_style(name):
    p = Path(name)
    if p.is_file(): return p
    for cand in (EDITS / name / 'style.json', EDITS / f'{name}.json'):
        if cand.exists(): return cand
    sys.exit(f'style {name} not found, styles: {sorted(d.name for d in EDITS.iterdir() if (d / "style.json").exists())}')


def _merge_variant(base, override):
    """Deep-merge a variant's named overrides onto a copy of the base style dict: a dict merges
    key by key, recursively; any other value (including a list) replaces the base value outright.
    This is the styles/<style>/variants/<name>.json convention (plan.md Stage 6), so a brand piece
    like fontainebleau or green-label is a handful of overridden fields, not a hand-copied
    style.json that silently drifts from the style it started as."""
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge_variant(out[k], v)
        else:
            out[k] = v
    return out


def load_style(name):
    """name is a style name/path, or 'style:variant' naming a sibling override at
    styles/<style>/variants/<variant>.json. Returns (style_dict, style_name, variant_name, style_path)."""
    style_name, _, variant_name = name.partition(':')
    sp = find_style(style_name)
    style = json.load(open(sp))
    if variant_name:
        vf = sp.parent / 'variants' / f'{variant_name}.json'
        if not vf.exists():
            have = sorted(p.stem for p in (sp.parent / 'variants').glob('*.json')) if (sp.parent / 'variants').is_dir() else []
            sys.exit(f'variant {variant_name} not found for style {style_name}, have: {have}')
        style = _merge_variant(style, json.load(open(vf)))
    return style, style_name, variant_name or None, sp


def merge_audio(style, edl):
    """edl's own audio mix settings (for example a bed-level decision choose_style.choose()
    already wrote to edl['audio']) with the style's own audio block layered on top, key by key,
    rather than the style replacing the whole dict (plan.md:228, the audio-dict fix at this
    file's old line 140)."""
    merged = dict(edl.get('audio') or {})
    merged.update(style.get('audio') or {})
    return merged


def resolve_edl_media(edl):
    """An edl written against the media folder holds paths relative to it (_testdata/..., tests/*/assets/...).
    Point them at MEDIA_ROOT (see paths.py) so --edl re-renders work from any directory."""
    import paths
    for sh in edl.get('shots', []):
        if sh.get('clip'): sh['clip'] = str(paths.media(sh['clip']))
    for k in ('music', 'voiceover'):
        if (edl.get(k) or {}).get('path'): edl[k]['path'] = str(paths.media(edl[k]['path']))
    return edl


def whisper_words(wav, tmpjson):
    r = subprocess.run([str(LT_PY), str(HERE / 'transcribe.py'), str(wav), str(tmpjson)], capture_output=True, text=True)
    if not Path(tmpjson).exists():
        print('transcription failed:', r.stderr[-300:]); return []
    return json.load(open(tmpjson))


def group_phrases(words, gap=0.45, max_words=9):
    out, ph, last = [], 0, None
    for i, w in enumerate(words):
        if last is not None and (w['t0'] - last > gap or sum(1 for x in out if x['phrase'] == ph) >= max_words or out[-1]['text'].endswith(('.', '?', '!'))):
            ph += 1
        out.append({'text': w['text'].strip(), 't0': w['t0'], 't1': w['t1'], 'phrase': ph, 'emph': False}); last = w['t1']
    return out


def snap_cuts_to_words(edl, cfg):
    """Move each internal cut to the nearest caption word start within tol seconds (phrase starts first), so cuts follow the speech
    the way they do in talking-head and explainer edits (measured: cuts sit within 0.02 to 0.05 s of a word start, not on the beat grid).
    Events that start or end on a moved cut move with it."""
    words = edl.get('words') or []; shots = edl['shots']; fps = edl['fps']
    if not words or len(shots) < 2: return 0
    tol = cfg.get('tol', 0.4); min_len = cfg.get('min_len', 0.6); moved = 0
    starts = sorted({(round(w['t0'], 3), True) for i, w in enumerate(words) if i == 0 or words[i - 1]['phrase'] != w['phrase']} |
                    {(round(w['t0'], 3), False) for w in words})
    for i in range(1, len(shots)):
        old = shots[i]['t0']
        cands = [(abs(t - old) - (0.08 if ph else 0.0), t) for t, ph in starts if abs(t - old) <= tol]
        if not cands: continue
        new = round(min(cands)[1] * fps) / fps
        if new - shots[i - 1]['t0'] < min_len or (i + 1 < len(shots) and shots[i]['t1'] - new < min_len) or abs(new - old) < 1e-6: continue
        shots[i]['t0'] = new; shots[i - 1]['t1'] = new; moved += 1
        for e in edl['events']:
            if abs(e['t0'] - old) < 1e-3: e['t0'] = new
            if abs(e['t1'] - old) < 1e-3: e['t1'] = new
            if 'tc' in e and abs(e['tc'] - old) < 1e-3: e['tc'] = new
    for sh in shots: sh['src_dur'] = round((sh['t1'] - sh['t0']) * sh.get('speed', 1.0), 3)
    return moved


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--list', action='store_true', help='list styles, effects, caption kinds, overlays and sound effects')
    ap.add_argument('--style'); ap.add_argument('--clips', help='folder of video or image clips')
    ap.add_argument('--music', help='any song or audio file'); ap.add_argument('--captions', help='text, a .txt, .srt or .json file. One line is one phrase, *word* marks emphasis')
    ap.add_argument('--voiceover', help='voiceover audio, transcribed for caption timing and mixed over ducked music')
    ap.add_argument('--vo-start-beats', type=float, default=None); ap.add_argument('--transcribe', action='store_true', help='use Whisper word timings of the music vocals as captions')
    ap.add_argument('--duration', type=float, default=None); ap.add_argument('--aspect', default=None)
    ap.add_argument('--res', type=int, default=720, help='short side in pixels'); ap.add_argument('--fps', type=int, default=30)
    ap.add_argument('--seed', type=int, default=1); ap.add_argument('--music-start', type=float, default=None)
    ap.add_argument('--out', default='edit_out'); ap.add_argument('--plan-only', action='store_true'); ap.add_argument('--edl', help='render an existing edl.json')
    ap.add_argument('--no-check', action='store_true')
    ap.add_argument('--mood', default=None, help='auto mode: edgy, dark, energetic, calm, heritage, ...')
    ap.add_argument('--audience', default=None, help='auto mode: who the edit is for')
    ap.add_argument('--caption-kind', default=None, help='auto mode: lyric, slogan, steps, tool, how-to, workflow, ...')
    ap.add_argument('--cards-dir', default=None, help='auto mode: folder of title/fact cards, if any')
    a = ap.parse_args(argv)
    import audio, clips as clipmod, plan, render, check
    if a.list:
        import fx, captions, sfx
        render.load_ext()
        print('styles   ', sorted(d.name for d in EDITS.iterdir() if (d / 'style.json').exists()))
        print('effects  ', sorted(fx.FX)); print('captions ', sorted(captions.CAPTIONS))
        print('overlays ', sorted(render.OVERLAYS)); print('sfx      ', sorted(sfx.SFX))
        return
    if not a.style: a.style = 'auto'
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    decision = None
    if a.style == 'auto':
        import brief, choose_style
        b = brief.from_footage(a.clips, mood=a.mood, audience=a.audience, caption_kind=a.caption_kind,
                                voiceover=bool(a.voiceover), duration=a.duration, aspect=a.aspect,
                                cards_dir=a.cards_dir)
        decision = choose_style.choose(b)
        json.dump({'features': b, **decision}, open(out / 'decisions.json', 'w'), indent=1)
        if not decision['style']:
            sys.exit(f"no style fit: {decision['gap']} (scores: {decision['scores']})")
        print(f"auto-selected {decision['style']} (score {decision['score']}, runner-up "
              f"{decision['runner_up']} {decision['runner_up_score']})")
        a.style = decision['style']
    style, style_name, variant_name, sp = load_style(a.style)
    dflt = style.get('defaults', {})
    aspect = a.aspect or dflt.get('aspect', '9:16')
    if a.duration is not None:
        duration = a.duration
    else:
        vo_s = None
        if a.voiceover:
            r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', a.voiceover], capture_output=True, text=True)
            try: vo_s = float(r.stdout.strip())
            except ValueError: vo_s = None
        fact_count = len(list(Path(a.cards_dir).iterdir())) if a.cards_dir and Path(a.cards_dir).is_dir() else None
        duration = plan.choose_duration(style_name, dflt.get('duration', 18.0), voiceover_s=vo_s, fact_count=fact_count)
    finish = plan.finish_block({'style': style_name, 'duration': duration, 'end_card': style.get('end_card'), 'variant': variant_name})
    if 'loop_seam_beats' not in style.get('cuts', {}):
        style.setdefault('cuts', {})['loop_seam_beats'] = finish['loop_seam_beats']
    if a.edl:
        edl = json.load(open(a.edl)); resolve_edl_media(edl); song_path = edl['music']['path']
    else:
        if a.music and a.music.endswith('.json'):
            import pick_track
            mcfg = style.get('music', {})
            picked = pick_track.pick({
                'bpm_target': mcfg.get('bpm_target', 120),
                'duration': duration,
                'drop_at': mcfg.get('drop_at', style.get('structure', {}).get('drop_at', 0.4)),
                'style_kind': mcfg.get('style_kind'),
                'mood': mcfg.get('mood'),
            }, a.music)
            if picked['path'] is None:
                sys.exit(f"no track fits {a.style}: {picked['reason']}")
            a.music = picked['path']
            if a.music_start is None:
                a.music_start = picked['start']
            if decision is not None:
                decision['music_pick'] = picked
        print('analysing music'); song = audio.analyse(a.music, out / 'song.json')
        print(f"  {song['bpm']:.1f} BPM, {len(song['beats'])} beats, drops {song['drops']}")
        print('analysing clips'); cl = clipmod.analyse_folder(a.clips, out / 'cache')
        if not cl: sys.exit('no clips found')
        text = None; given = None; vo = None
        if a.captions:
            c = Path(a.captions)
            text = c.read_text() if c.exists() and c.suffix in ('.txt', '.md') else a.captions
            if c.exists() and c.suffix == '.srt':
                from plan import parse_srt
                given = [{'text': w, 't0': t0, 't1': t1, 'phrase': i, 'emph': False} for i, (t0, t1, body) in enumerate(parse_srt(c.read_text())) for w in [body]]
                text = None
            if text and text.replace('\\n', '\n') != text: text = text.replace('\\n', '\n')
        P = song['beat_period']
        if a.voiceover:
            wav = out / 'vo.wav'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.voiceover, '-vn', '-ac', '1', '-ar', '16000', str(wav)])
            ww = whisper_words(wav, out / 'vo_words.json')
            if ww:
                first = ww[0]['t0']
                vs_b = a.vo_start_beats if a.vo_start_beats is not None else style.get('structure', {}).get('vo_start_beats', 4)
                vstart = vs_b * P - first                                    # speech begins on a beat
                g = group_phrases(ww)
                for w in g: w['t0'] += vstart; w['t1'] += vstart
                if not text: given = g
                vo = {'path': str(a.voiceover), 'start': round(vstart, 4)}
        elif a.transcribe and not text and not given:
            wav = out / 'music.wav'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.music, '-vn', '-ac', '1', '-ar', '16000', str(wav)])
            ww = whisper_words(wav, out / 'music_words.json')
            s0, _ = plan.pick_window(song, duration, style, a.music_start)
            given = [dict(w, t0=w['t0'] - s0, t1=w['t1'] - s0) for w in group_phrases(ww) if w['t0'] >= s0]
        edl = plan.build_edl(style, song, cl, duration=duration, fps=a.fps, aspect=aspect, seed=a.seed, music_start=a.music_start,
                             captions_text=text, given_words=given, voiceover=vo)
        edl['style_path'] = str(sp); song_path = a.music
        edl['finish'] = finish                                                            # hook/loop-seam/end-card decision, every style, auto-fit or not
        if decision and decision.get('audio'): edl['audio'] = dict(decision['audio'])   # the chooser's own bed-level/gain call, auto mode only
        if style.get('cuts', {}).get('snap_words'):
            print('  cuts snapped to word starts:', snap_cuts_to_words(edl, style['cuts']['snap_words']))
        if style.get('sfx_library'):                                     # opt-in: real recorded effects from design-library/sfx, synthesised ones stay as fallback
            import sfx_library, gate
            print('  library samples on sfx events:', sfx_library.apply_to_edl(edl, style['sfx_library']))
            if not gate.licence_check(edl, sfx_library.ROOT / 'index.json'):
                sys.exit('licence gate: an sfx sample is not a cleared, credited library entry')
        if style.get('audio_shape'):                                      # opt-in: intro gate, low-end duck under the voiceover, gaps before hits (audio_shape.py)
            import audio_shape
            print('  audio shaping:', audio_shape.plan(edl, style))
        if style.get('audio') or edl.get('audio'): edl['audio'] = merge_audio(style, edl)   # style-level mix settings merge over the chooser's, not replace them
        json.dump(edl, open(out / 'edl.json', 'w'), indent=1)
        print(f"planned {edl['stats']['n_shots']} shots, mean {edl['stats']['mean_shot_beats']} beats, events {edl['stats']['events_by_fx']}")
    if a.plan_only: return edl
    if edl.get('audio_shape'):
        import audio_shape
        song_path = audio_shape.shape_music(song_path, edl, out / 'music_shaped.wav')
    print('rendering'); vo_path = a.voiceover if edl.get('voiceover') else None
    video = out / 'edit.mp4'
    render.render(edl, video, song_path, vo_path, size_short=a.res)
    if not a.no_check:
        res = check.check(video, edl)
        json.dump(res, open(out / 'check.json', 'w'), indent=1)
        print(json.dumps({k: v for k, v in res.items() if k != 'cuts'}, indent=1))
    print('wrote', video)
    return edl


if __name__ == '__main__':
    main()

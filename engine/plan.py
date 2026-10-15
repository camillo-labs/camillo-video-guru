"""Edit planner: applies a style's rules to a NEW song's beat grid and NEW clips and returns an edit decision list.

Pipeline: pick the music window, lay a cut schedule on the beat grid from the style's shot-length distribution,
assign clips to shots by energy, place moves, transitions, sound effects and captions with the style's rules.
Everything is deterministic for a given --seed so an edl.json can be inspected, tweaked and re-rendered.
"""
import json, re
from pathlib import Path
import numpy as np
import clips as clipmod
import normalise


# ------------------------------------------------------------------ finish block

# Styles whose own clean intro the chooser shortens to a 2 s hook rather than pre-rolling a
# caption over it (plan.md Stage 6: "shorten hud/bw-flash-vo's clean intro to 2s, or pre-roll
# a caption"). talking-head-split and kinetic-card-explainer are voiceover-led and keep their
# own structure.vo_start_beats lead-in instead.
HOOK_SHORTEN_STYLES = {'hud-lyric-heat', 'hud-lyric-light', 'bw-flash-vo'}
# Voiceover-led styles: a finish block never adds a music loop seam under one of these, since
# there is no bed to loop back onto.
VOICEOVER_STYLES = {'kinetic-card-explainer', 'talking-head-split'}
# Explainer-shaped styles get a comment-keyword end card by default; everything else that names
# a brand variant gets a logo card instead, and a plain lyric loop gets neither (plan.md Stage 6).
EXPLAINER_STYLES = {'kinetic-card-explainer'}
LOOP_SEAM_BEATS = 2.0
HOOK_INTRO_S = 2.0


def finish_block(b):
    """The chooser's finish decision for a brief/decision dict ({'style', 'duration', 'end_card',
    'variant'}, every key read with .get() like choose_style.choose()'s own brief dict): hook,
    loop seam and end card. Always returns a block, fit or not, mirroring choose_style.choose()'s
    always-present 'audio' key, so a caller never has to special-case a missing finish decision."""
    style = b.get('style')
    duration = b.get('duration') or 18.0
    end_card = b.get('end_card')
    variant = b.get('variant')

    if style in HOOK_SHORTEN_STYLES:
        hook = {'kind': 'shorten_intro', 'intro_s': HOOK_INTRO_S}
    else:
        hook = {'kind': 'caption_preroll', 'intro_s': 0.0}

    music_led = style not in VOICEOVER_STYLES
    loop_seam_beats = LOOP_SEAM_BEATS if (music_led and duration < 30 and not end_card) else 0.0

    if end_card is not None:
        card = end_card
    elif style in EXPLAINER_STYLES:
        card = {'kind': 'comment_keyword', 'word': (variant or 'more').upper()}
    elif variant:
        card = {'kind': 'logo_card', 'variant': variant}
    else:
        card = None  # a lyric-led loop ends on the seam, not a card

    return {'hook': hook, 'loop_seam_beats': loop_seam_beats, 'end_card': card}


FACT_SECONDS = 3.5   # seconds per fact/card at a brisk explainer pace


def choose_duration(style, default_duration, voiceover_s=None, fact_count=None):
    """A duration for when --duration is omitted: a voiceover's own length (plus a short
    lead-in/out pad) wins if there is one, else a fact/card count at a fixed pace for a
    card-driven style, else the style's own style.json default (plan.md Stage 6's "voiceover
    length, fact count, style default" ladder)."""
    if voiceover_s:
        return round(voiceover_s + 2.0, 2)
    if fact_count:
        return round(fact_count * FACT_SECONDS, 2)
    return default_duration


def _choice(rng, pairs):
    vals = [p[0] for p in pairs]; w = np.array([p[1] for p in pairs], float); w /= w.sum()
    return float(rng.choice(vals, p=w))


def pick_window(song, duration, style, music_start=None):
    P = song['beat_period']; down = song['downbeats']
    st = style.get('structure', {})
    if music_start is not None:
        s0 = min(down, key=lambda d: abs(d - music_start)) if down else music_start
        if abs(s0 - music_start) > P: s0 = music_start
    else:
        s0 = down[0] if down else song['first_beat']
        drop_at = st.get('drop_at')          # fraction of the edit at which the first drop should land
        if drop_at is not None and song['drops']:
            want = drop_at * duration
            # candidates: every phrase start (8-beat boundaries plus every drop, both
            # downbeat-aligned), scored by how close the nearest drop in-window lands to
            # `want`, per the selection plan's window-search rule
            best = None
            for cand in (song.get('phrases') or down):
                if cand + duration > song['duration'] + 0.05:
                    continue
                near_drops = [dr for dr in song['drops'] if cand <= dr <= cand + duration]
                if not near_drops:
                    continue
                err = min(abs((dr - cand) - want) for dr in near_drops)
                if best is None or err < best[0]: best = (err, cand)
            if best: s0 = best[1]
            else:
                # no phrase has a drop in-window: fall back to the old near-drop search
                for dr in song['drops']:
                    cand = dr - want
                    cand = max([d for d in down if d <= cand + P * 2] or [down[0]])
                    if cand + duration <= song['duration'] + 0.05:
                        err = abs((dr - cand) - want)
                        if best is None or err < best[0]: best = (err, cand)
                if best: s0 = best[1]
        else:
            # no drops: start at the first downbeat after any silent lead-in
            s0 = down[0] if down else 0.0
    avail = song['duration'] - s0
    D = min(duration, avail)
    nb = int(D // P)
    if st.get('end_on_bar', True): nb -= nb % 4
    return s0, max(4, nb)


def beat_role(song, s0, j, P, intro_beats, outro_beats, nb, drops_j, drop_len):
    if j >= nb - outro_beats: return 'outro'
    for dj in drops_j:
        if dj <= j < dj + drop_len: return 'drop'
    if j < intro_beats: return 'intro'
    k = int(round((s0 + j * P - song['first_beat']) / P))
    k = min(max(k, 0), len(song['roles']) - 1)
    return song['roles'][k]


def match(when, c, rng):
    """Does a rule's `when` clause hold for context c? Keys: role, downbeat, phrase, drop, bar_every, first, last,
    index_mod, shot_beats_min, shot_beats_max, p."""
    w = when or {}
    if 'role' in w:
        r = w['role'] if isinstance(w['role'], list) else [w['role']]
        if c.get('role') not in r: return False
    for key in ('downbeat', 'phrase', 'drop', 'first', 'last'):
        if key in w and bool(c.get(key)) != bool(w[key]): return False
    if 'bar_every' in w and not (c.get('bar', 0) % w['bar_every'] == w.get('bar_offset', 0) and c.get('downbeat')): return False
    if 'index_mod' in w and c.get('index', 0) % w['index_mod'] != w.get('index_offset', 0): return False
    if 'shot_beats_min' in w and c.get('shot_beats', 0) < w['shot_beats_min']: return False
    if 'shot_beats_max' in w and c.get('shot_beats', 0) > w['shot_beats_max']: return False
    if 'beats_from_start_min' in w and c.get('j', 0) < w['beats_from_start_min']: return False
    if 'beats_from_start_max' in w and c.get('j', 0) > w['beats_from_start_max']: return False
    if 'frac_min' in w and c.get('frac', 0) < w['frac_min']: return False
    if 'frac_max' in w and c.get('frac', 0) > w['frac_max']: return False
    p = w.get('p', 1.0)
    return p >= 1.0 or rng.random() < p


def lerp_grade(timeline, frac):
    if not timeline: return {}
    ks = sorted(timeline, key=lambda k: k['frac'])
    if frac <= ks[0]['frac']: return dict(ks[0]['grade'])
    for a, b in zip(ks[:-1], ks[1:]):
        if a['frac'] <= frac <= b['frac']:
            if b.get('step') or a.get('step'): return dict(a['grade'])
            u = (frac - a['frac']) / max(1e-6, b['frac'] - a['frac'])
            out = dict(a['grade'])
            for key, vb in b['grade'].items():
                va = a['grade'].get(key, 1.0 if key in ('saturation', 'contrast', 'gamma') else 0.0)
                if isinstance(vb, (int, float)) and isinstance(va, (int, float)):
                    out[key] = va + (vb - va) * u
                elif isinstance(vb, list) and isinstance(va, list) and len(va) == len(vb):
                    out[key] = [x + (y - x) * u for x, y in zip(va, vb)]
                else:
                    out[key] = vb
            return out
    return dict(ks[-1]['grade'])


# ------------------------------------------------------------------ captions

def parse_words(text):
    """Text to phrases of words. One line is one phrase. *word* marks emphasis. Returns list of phrases (list of (word, emph))."""
    phrases = []
    for line in [l.strip() for l in re.split(r'[\n|]+', text) if l.strip()]:
        ws = []
        for tok in line.split():
            e = tok.startswith('*') and tok.endswith('*') and len(tok) > 2
            ws.append((tok.strip('*'), e))
        phrases.append(ws)
    return phrases


def parse_srt(text):
    out = []
    for blk in re.split(r'\n\s*\n', text.strip()):
        m = re.search(r'(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)', blk)
        if not m: continue
        g = list(map(int, m.groups()))
        t0 = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000; t1 = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        body = ' '.join(blk.splitlines()[[i for i, l in enumerate(blk.splitlines()) if '-->' in l][0] + 1:])
        out.append((t0, t1, body))
    return out


def time_words(phrases, cfg, song, s0, P, nb, D, rng, given=None):
    """Lay words on the timeline. Returns list of word dicts. given: list of {text, t0, t1} from SRT or Whisper (timeline seconds)."""
    tcfg = cfg.get('timing', {})
    mode = tcfg.get('mode', 'grid')
    words = []
    if given:
        phrase = 0
        for i, g in enumerate(given):
            words.append({'text': g['text'], 't0': g['t0'], 't1': g.get('t1', g['t0'] + 0.3), 'emph': g.get('emph', False),
                          'phrase': g.get('phrase', 0), 'line': 0})
        for i, w in enumerate(words):
            if i + 1 < len(words) and words[i + 1]['phrase'] == w['phrase']:
                w['t1'] = min(max(w['t1'], w['t0'] + 0.1), words[i + 1]['t0'] + 0.0) if tcfg.get('tight_end', True) else w['t1']
        return words
    start_b = tcfg.get('start_beat', 4)
    step = tcfg.get('step_beats', 1.0)
    steps = step if isinstance(step, list) else [step]       # a list is cycled, giving uneven word gaps
    if mode == 'grid':
        b = start_b; wn = 0
        limit = D - 0.2 - (tcfg.get('fill_tail_beats', 0) * P if tcfg.get('fill') else 0)
        reps = 12 if tcfg.get('fill') else 1                 # fill: repeat the phrase list until the edit is covered
        allp = list(phrases) * reps
        for pi, ph in enumerate(allp):
            if tcfg.get('fill') and (b * P >= limit or (tcfg.get('fill_whole') and words and (b + len(ph) * steps[0]) * P > limit)): break     # never start a phrase that cannot finish
            for wi, (w, e) in enumerate(ph):
                t = b * P
                if t >= limit: break
                stp = steps[wn % len(steps)]; wn += 1
                words.append({'text': w, 't0': t, 't1': t + stp * P, 'emph': e, 'phrase': pi, 'line': 0})
                b += stp
            b += tcfg.get('phrase_gap_beats', 0.0)
            if tcfg.get('phrase_align_bar', False): b = int(np.ceil(b / 4) * 4)
    elif mode == 'bar_phrases':
        b = start_b; bars = tcfg.get('bars_per_phrase', 1)
        for pi, ph in enumerate(phrases):
            span = bars * 4; n = len(ph)
            for wi, (w, e) in enumerate(ph):
                bb = b + round(wi * span / n * 2) / 2
                if bb * P >= D - 0.2: break
                words.append({'text': w, 't0': bb * P, 't1': (bb + span / n) * P, 'emph': e, 'phrase': pi, 'line': 0})
            b += span
    elif mode == 'onsets':
        ons = [o for o in song['onsets'] if o['s'] >= tcfg.get('min_strength', 0.25) and s0 <= o['t'] < s0 + D]
        ons = [o['t'] - s0 for o in ons if o['band'] in tcfg.get('bands', ['kick', 'snare'])]
        flat = [(pi, w, e) for pi, ph in enumerate(phrases) for (w, e) in ph]
        ons = [t for t in ons if t >= start_b * P]
        for (pi, w, e), t in zip(flat, ons):
            words.append({'text': w, 't0': t, 't1': t + 0.3, 'emph': e, 'phrase': pi, 'line': 0})
    for i, w in enumerate(words):
        nxt = words[i + 1]['t0'] if i + 1 < len(words) else D
        w['t1'] = min(w['t1'], nxt) if tcfg.get('tight_end', False) else w['t1']
    return words


# ------------------------------------------------------------------ main

def build_edl(style, song, clip_list, duration=18.0, fps=30, aspect='9:16', seed=1, music_start=None,
              captions_text=None, given_words=None, voiceover=None):
    rng = np.random.default_rng(seed)
    P = song['beat_period']
    s0, nb = pick_window(song, duration, style, music_start)
    D = nb * P
    st = style.get('structure', {})
    cuts_cfg = style.get('cuts', {})
    intro_beats = st.get('intro_beats', 4); outro_beats = st.get('outro_beats', 4)
    drops_j = [int(round((d - s0) / P)) for d in song['drops'] if s0 <= d < s0 + D]
    drop_len = st.get('drop_beats', 8)
    phrase_j = sorted({int(round((p - s0) / P)) for p in song['phrases'] if s0 - 1e-3 <= p < s0 + D})
    beat_t = lambda jj: jj * P

    # ---- cut schedule in beats
    L = cuts_cfg.get('lengths', {'default': [[1, 1]]})
    shots = []
    j = 0.0
    min_beats = max(cuts_cfg.get('min_beats', 0.25), 3 / fps / P)
    first_hold = cuts_cfg.get('first_shot_beats')
    seam = float(cuts_cfg.get('loop_seam_beats', 0) or 0)      # a short final shot that repeats the first clip so the edit loops
    nb_s = nb - seam if 0 < seam < nb - 2 else float(nb)
    while j < nb_s - 1e-6:
        jj = int(j)
        role = beat_role(song, s0, jj, P, intro_beats, outro_beats, nb, drops_j, drop_len)
        pairs = L.get(role) or L.get('default') or [[1, 1]]
        if j == 0 and first_hold: ln = float(first_hold)
        else: ln = _choice(rng, pairs)
        if cuts_cfg.get('bar_align', True) and ln >= 1:
            # keep long shots from straddling a downbeat awkwardly: land on the next beat boundary
            ln = max(1.0, round(ln))
        # snap to a phrase boundary that sits within one beat of the planned end
        end = j + ln
        for pb in phrase_j:
            if pb > j + min_beats and abs(pb - end) <= cuts_cfg.get('phrase_snap_beats', 1.0) and pb != end and pb <= nb:
                end = float(pb); break
        if nb_s - end < min_beats * 2 and nb_s - end > 1e-6: end = float(nb_s)
        end = min(end, float(nb_s))
        shots.append({'beat0': j, 'beat1': end, 'role': role})
        j = end
    if nb_s < nb: shots.append({'beat0': nb_s, 'beat1': float(nb), 'role': 'outro', 'seam': True})
    # frame-quantise cuts to the output grid and drop degenerate shots
    for sh in shots:
        sh['t0'] = round(sh['beat0'] * P * fps) / fps
        sh['t1'] = round(sh['beat1'] * P * fps) / fps
    shots[-1]['t1'] = round(D * fps) / fps

    # ---- clip assignment
    mode = style.get('clips', {}).get('select', 'energy_match')
    avoid = style.get('clips', {}).get('avoid_repeat', 3)
    be = np.array(song['beat_energy']) if song['beat_energy'] else np.ones(1)
    allm = []
    for c in clip_list:
        if c['kind'] == 'video': allm += list(c['motion'])
    mq = np.sort(np.array(allm)) if allm else np.zeros(1)
    def qm(m): return float(np.searchsorted(mq, m) / max(1, len(mq)))
    eq = np.sort(be)
    def qe(e): return float(np.searchsorted(eq, e) / max(1, len(eq)))
    recent = []; usage = {}
    seq_i = 0
    order = list(range(len(clip_list)))
    if mode == 'shuffle': rng.shuffle(order)
    for si, sh in enumerate(shots):
        dur = sh['t1'] - sh['t0']
        k0 = int(round((s0 + sh['beat0'] * P - song['first_beat']) / P)); k1 = max(k0 + 1, int(round((s0 + sh['beat1'] * P - song['first_beat']) / P)))
        k0 = min(max(k0, 0), len(be) - 1); k1 = min(max(k1, k0 + 1), len(be))
        target = qe(float(be[k0:k1].mean())) if len(be) else 0.5
        speed = 1.0
        sp = style.get('speed', {}).get('choices')
        if sp: speed = _choice(rng, sp)
        need = dur * speed
        best = None
        for ci, c in enumerate(clip_list):
            if mode == 'sequential' and ci != order[seq_i % len(order)]: continue
            if mode == 'shuffle' and ci != order[si % len(order)]: continue
            wins = clipmod.windows(c, need)
            if not wins and c['kind'] == 'video':
                # clip too short for this shot: slow down to fit what exists, never below 0.5 speed
                avail = max(0.3, (c['scenes'][0] if c['scenes'] else c['dur']) - 0.2)
                wins = [(0.0, c['mean_motion'], c['mean_bright'])]
                sp_eff = max(0.5, min(1.0, avail / dur)); need_eff = dur * sp_eff
            else:
                sp_eff, need_eff = speed, need
            for (ws, m, br) in wins:
                score = abs(qm(m) - target) if c['kind'] == 'video' else 0.35 + 0.15 * abs(target - 0.3)
                score *= style.get('clips', {}).get('energy_weight', 1.0)
                if ci in recent[-avoid:]: score += 1.5 * (1 + recent[-avoid:].count(ci) * 0.5)
                if recent and recent[-1] == ci: score += 3
                score += usage.get(ci, 0) * 0.08 + rng.random() * style.get('clips', {}).get('jitter', 0.25)
                if style.get('clips', {}).get('prefer_faces') and c.get('face'): score -= 0.15
                if best is None or score < best[0]: best = (score, ci, ws, sp_eff, need_eff)
        if best is None: raise RuntimeError('no usable clip window, give the engine more or longer clips')
        _, ci, ws, sp_eff, need_eff = best
        c = clip_list[ci]
        recent.append(ci); usage[ci] = usage.get(ci, 0) + 1; seq_i += 1
        sh.update({'clip': c['path'], 'clip_kind': c['kind'], 'src_in': ws if c['kind'] == 'video' else 0.0, 'speed': sp_eff,
                   'focus': c['focus'], 'mask': c.get('mask'), 'w': c['w'], 'h': c['h'], 'src_dur': need_eff, 'target_q': round(target, 2)})
        if c['kind'] == 'image':
            sh['kenburns'] = {'dir': float(rng.choice([0, 180, 90, 270, 45, 225])), 'scale': float(rng.uniform(1.10, 1.22)),
                              'amount': float(rng.uniform(0.05, 0.12))}

    # ---- loop seam: the final short shot repeats the opening picture
    if len(shots) > 1 and shots[-1].get('seam'):
        f0 = shots[0]
        for key in ('clip', 'clip_kind', 'src_in', 'focus', 'mask', 'w', 'h', 'kenburns', 'target_q'):
            if key in f0: shots[-1][key] = f0[key]
        shots[-1]['speed'] = f0['speed']; shots[-1]['src_dur'] = (shots[-1]['t1'] - shots[-1]['t0']) * f0['speed']

    # ---- speed ramps (time map per shot)
    for sh in shots:
        pass
    for rule in style.get('speed', {}).get('ramps', []):
        for si, sh in enumerate(shots):
            if sh['clip_kind'] != 'video': continue
            c = {'role': sh['role'], 'index': si, 'shot_beats': sh['beat1'] - sh['beat0'], 'j': sh['beat0'], 'frac': sh['beat0'] / nb,
                 'first': si == 0, 'last': si == len(shots) - 1, 'downbeat': int(sh['beat0']) % 4 == 0}
            if match(rule.get('when'), c, rng) and 'ramp' not in sh:
                r = rule['ramp']
                shot_beats = max(1e-6, c['shot_beats'])
                if 'portion_beats' in r:
                    # Stage 8: anchor the ramp to beat time, not shot fraction. portion_beats is
                    # [a, b] in beats from the shot's own start, so the ramp's absolute musical
                    # duration holds across shots of different lengths; a longer shot just carries
                    # more full-speed footage either side of the same beat-long ramp.
                    pa, pb = r['portion_beats']
                    portion = [float(np.clip(pa / shot_beats, 0.0, 1.0)), float(np.clip(pb / shot_beats, 0.0, 1.0))]
                else:
                    portion = r.get('portion', [0.0, 1.0])
                sh['ramp'] = {'s0': r.get('s0', 1.0), 's1': r.get('s1', 0.4), 'portion': portion, 'shape': r.get('shape', 'in_out')}
                # source length consumed becomes the integral of the speed curve
                u = np.linspace(0, 1, 50)
                sp = np.ones_like(u) * sh['speed']
                a, b = sh['ramp']['portion']
                from fx import ease
                for ui, uu in enumerate(u):
                    if a <= uu <= b:
                        sp[ui] = sh['speed'] * (sh['ramp']['s0'] + (sh['ramp']['s1'] - sh['ramp']['s0']) * ease(sh['ramp']['shape'], (uu - a) / max(1e-6, b - a)))
                    elif uu > b: sp[ui] = sh['speed'] * sh['ramp']['s1']
                    else: sp[ui] = sh['speed'] * sh['ramp']['s0']
                sh['src_dur'] = float((sh['t1'] - sh['t0']) * sp.mean())
                # keep inside clip
                cc = next(x for x in clip_list if x['path'] == sh['clip'])
                if sh['src_in'] + sh['src_dur'] > cc['dur']: sh['src_in'] = max(0.0, cc['dur'] - sh['src_dur'] - 0.05)

    # ---- events from rules
    events, sfx_ev = [], []
    def ctx_for_beat(jf, si=None):
        jj = int(jf)
        return {'role': beat_role(song, s0, min(jj, nb - 1), P, intro_beats, outro_beats, nb, drops_j, drop_len),
                'downbeat': jj % 4 == 0 and abs(jf - jj) < 1e-6, 'bar': jj // 4, 'j': jf, 'frac': jf / nb,
                'phrase': any(abs(jf - pj) < 1e-6 for pj in phrase_j),
                'drop': any(abs(jf - dj) < 0.5 for dj in drops_j), 'index': si if si is not None else 0}

    def place_rules(rules, out, kind):
        last_t = {}
        for ri, rule in enumerate(rules):
            at = rule.get('at', 'cut'); name = rule.get('fx') or rule.get('kind')
            key = (ri,)
            gap = rule.get('min_gap_beats', 0) * P
            def add(t_c, c, span=None, extra=None):
                if t_c - last_t.get(key, -9) < gap: return
                if not match(rule.get('when'), c, rng): return
                last_t[key] = t_c
                if kind == 'fx':
                    pre, post = rule.get('span_beats', [0.25, 0.25])
                    t0, t1 = t_c - pre * P, t_c + post * P
                    if span: t0, t1 = span
                    ev = {'fx': name, 't0': round(t0, 4), 't1': round(t1, 4), 'tc': round(t_c, 4), 'params': rule.get('params', {}),
                          'layer': rule.get('layer', 'post'), 'at': at}
                    if extra: ev.update(extra)
                    out.append(ev)
                else:
                    e = {'kind': name, 't': round(t_c, 4), 'gain': rule.get('gain', 0.5), 'at': at}
                    for kk in ('dur', 'offset', 'end_at_t'):
                        if kk == 'offset' and at == 'beat': continue      # for 'beat' rules offset is the beat position, not seconds
                        if kk in rule: e[kk] = rule[kk]
                    if 'offset_s' in rule: e['offset'] = rule['offset_s']
                    out.append(e)
            if at == 'cut':
                for si, sh in enumerate(shots):
                    if si == 0 and not rule.get('include_first'): continue
                    c = ctx_for_beat(sh['beat0'], si); c['shot_beats'] = sh['beat1'] - sh['beat0']
                    c['first'] = si == 0
                    c['last'] = si == len(shots) - 1
                    add(sh['t0'], c)
            elif at == 'shot':
                for si, sh in enumerate(shots):
                    c = ctx_for_beat(sh['beat0'], si); c['shot_beats'] = sh['beat1'] - sh['beat0']
                    c['first'] = si == 0; c['last'] = si == len(shots) - 1
                    a, b = rule.get('portion', [0, 1])
                    add(sh['t0'], c, span=(sh['t0'] + (sh['t1'] - sh['t0']) * a, sh['t0'] + (sh['t1'] - sh['t0']) * b) if kind == 'fx' else None)
            elif at == 'beat':
                ev_ = rule.get('every', 1); off = rule.get('offset', 0)
                span_b = rule.get('dur_beats', 0.5)
                jb = off
                while jb < nb:
                    si = next((i for i, s in enumerate(shots) if s['beat0'] <= jb < s['beat1']), len(shots) - 1)
                    c = ctx_for_beat(jb, si); c['shot_beats'] = shots[si]['beat1'] - shots[si]['beat0']
                    if rule.get('skip_cut_beats') and abs(jb - shots[si]['beat0']) < 1e-6: jb += ev_; continue
                    add(jb * P, c, span=(jb * P, jb * P + span_b * P))
                    jb += ev_
            elif at == 'drop':
                for dj in drops_j:
                    c = ctx_for_beat(dj); add(dj * P, c)
            elif at == 'phrase':
                for pj in phrase_j:
                    c = ctx_for_beat(pj); add(pj * P, c)
            elif at == 'onset':
                bands = rule.get('bands', ['kick']); ms = rule.get('min_strength', 0.3)
                for o in song['onsets']:
                    t = o['t'] - s0
                    if 0 <= t < D and o['band'] in bands and o['s'] >= ms:
                        jf = t / P; si = next((i for i, s in enumerate(shots) if s['t0'] <= t < s['t1']), 0)
                        c = ctx_for_beat(jf, si); c['shot_beats'] = shots[si]['beat1'] - shots[si]['beat0']
                        add(t, c)
            elif at == 'time':
                t = rule.get('frac', 0.5) * D if 'frac' in rule else rule.get('sec', 0)
                add(t, ctx_for_beat(t / P))
    place_rules(style.get('moves', []), events, 'fx')
    place_rules(style.get('sfx', []), sfx_ev, 'sfx')

    # ---- grade timeline per shot
    gcfg = style.get('grade', {})
    norm_base = normalise.from_items(clip_list)['grade_base'] if gcfg.get('normalise') else {}
    for sh in shots:
        frac = (sh['t0'] + sh['t1']) / 2 / D
        g = dict(norm_base)                      # the footage's own measured correction, layered under...
        g.update(gcfg.get('base', {}))            # ...the style's base grade, which still wins on any shared key
        if gcfg.get('timeline'): g.update(lerp_grade(gcfg['timeline'], frac))
        sh['grade'] = g

    # ---- captions
    words = []
    ccfg = style.get('captions')
    if ccfg and (captions_text or given_words):
        phrases = parse_words(captions_text) if captions_text else []
        words = time_words(phrases, ccfg, song, s0, P, nb, D, rng, given=given_words)
        if ccfg.get('auto_emph') and not any(w['emph'] for w in words):
            by_ph = {}
            for w in words: by_ph.setdefault(w['phrase'], []).append(w)
            for ph, ws in by_ph.items():
                if ccfg['auto_emph'] == 'longest': max(ws, key=lambda w: len(w['text']))['emph'] = True
                elif ccfg['auto_emph'] == 'last': ws[-1]['emph'] = True
        if ccfg.get('caption_sfx'):
            for w in words: sfx_ev.append({'kind': ccfg['caption_sfx'], 't': round(w['t0'], 4), 'gain': ccfg.get('caption_sfx_gain', 0.25), 'at': 'caption'})
    for w in words:
        w['t0'] = round(w['t0'], 4); w['t1'] = round(w['t1'], 4)

    # ---- stats
    cut_ts = [sh['t0'] for sh in shots[1:]]
    offs = [((t / P) - round(t / P * 4) / 4) * P * 1000 for t in cut_ts]      # offset to the nearest sixteenth-note grid, ms
    lens = [sh['beat1'] - sh['beat0'] for sh in shots]
    edl = {
        'style': style['name'], 'seed': seed, 'fps': fps, 'aspect': aspect, 'duration': round(D, 4), 'n_beats': nb,
        'music': {'path': song['path'], 'start': round(s0, 4), 'bpm': song['bpm'], 'beat_period': P, 'drops_in_window': [round(d - s0, 3) for d in song['drops'] if s0 <= d < s0 + D]},
        'voiceover': voiceover, 'shots': shots, 'events': sorted(events, key=lambda e: e['t0']), 'sfx': sorted(sfx_ev, key=lambda e: e['t']), 'words': words,
        'stats': {'n_shots': len(shots), 'mean_shot_beats': round(float(np.mean(lens)), 3), 'shot_beats_hist': {str(k): lens.count(k) for k in sorted(set(lens))},
                  'planned_cut_offset_ms_from_sixteenth_grid_mean_abs': round(float(np.mean(np.abs(offs))) if offs else 0.0, 2),
                  'n_events': len(events), 'events_by_fx': {n: sum(1 for e in events if e['fx'] == n) for n in sorted({e['fx'] for e in events})}},
    }
    return edl

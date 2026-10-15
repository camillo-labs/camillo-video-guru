"""Storyboard stage: a grid of the key frames of an edit, with what happens at each.

  storyboard.py out/edl.json                 frames from the plan (source frame, planned crop, grade, caption)
  storyboard.py out/edit.mp4                 exact frames from the rendered video, at the same timestamps
  storyboard.py out/edl.json --video x.mp4   the same, naming the video
  --out DIR (default: beside the input), --cap N (default 18), --decisions FILE, --no-pdf

Writes storyboard.html, storyboard.pdf (A4 landscape, 6 panels a page, headless Chrome) and storyboard.json.
make_edit.py --storyboard calls this after the plan (with --plan-only) or after the render.
"""
import argparse, html, json, os, subprocess, sys, tempfile
from pathlib import Path

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
PRIORITY = {'hook': 0, 'end': 0, 'drop': 1, 'section': 2, 'transition': 3, 'caption': 4}
MERGE_S = 0.4


def _phrases(edl):
    """Caption phrases as (t0, t1, text), grouped by the words' phrase and line numbers."""
    groups = {}
    for w in edl.get('words') or []:
        groups.setdefault((w.get('phrase', 0), w.get('line', 0)), []).append(w)
    out = [(min(w['t0'] for w in g), max(w['t1'] for w in g), ' '.join(w['text'] for w in g)) for g in groups.values()]
    return sorted(out)


def select_moments(edl, cap=18):
    """Key moments as [{t, kinds}], sorted by time, at most cap. Deterministic for a given EDL."""
    dur = float(edl.get('duration') or (edl['shots'][-1]['t1'] if edl.get('shots') else 0))
    cand = [(min(1.0, dur / 2), 'hook'), (max(0.0, dur - 0.2), 'end')]
    prev = None
    for sh in edl.get('shots', []):
        if prev is not None and sh.get('role') != prev:
            cand.append((sh['t0'] + 0.15, 'section'))
        prev = sh.get('role')
    for d in (edl.get('music') or {}).get('drops_in_window') or []:
        if 0 <= d <= dur: cand.append((d + 0.05, 'drop'))
    for ev in edl.get('events', []):
        if ev.get('at') == 'cut':
            cand.append((ev['tc'] + 0.05, 'transition'))
    for t0, t1, _ in _phrases(edl):
        cand.append((t0 + min(0.3, (t1 - t0) / 2), 'caption'))
    cand = sorted((round(min(max(t, 0.0), max(dur - 0.05, 0.0)), 3), k) for t, k in cand)
    merged = []
    for t, k in cand:                                    # moments closer than MERGE_S share one panel
        if merged and t - merged[-1]['t'] < MERGE_S:
            m = merged[-1]
            if PRIORITY[k] < min(PRIORITY[x] for x in m['kinds']): m['t'] = t
            if k not in m['kinds']: m['kinds'].append(k)
        else:
            merged.append({'t': t, 'kinds': [k]})
    if len(merged) > cap:                                # drop the least important first, later ones first on ties
        rank = sorted(range(len(merged)), key=lambda i: (min(PRIORITY[k] for k in merged[i]['kinds']), i))
        keep = set(rank[:cap])
        merged = [m for i, m in enumerate(merged) if i in keep]
    return merged


def _shot_at(edl, t):
    shots = edl.get('shots', [])
    for i, sh in enumerate(shots):
        if sh['t0'] <= t < sh['t1']: return i, sh
    return (len(shots) - 1, shots[-1]) if shots else (None, None)


def _beat_cue(edl, t):
    m = edl.get('music') or {}
    P = m.get('beat_period')
    for d in m.get('drops_in_window') or []:
        if abs(t - d) <= 0.35: return 'drop'
    if not P: return ''
    b = t / P
    nearest = round(b)
    if abs(b - nearest) * P > 0.06: return f'between beats (beat {b:.1f})'
    if nearest % 8 == 0: return f'phrase start (beat {nearest})'
    if nearest % 4 == 0: return f'downbeat (beat {nearest})'
    return f'beat {nearest}'


def _intent(edl, shot, kinds, effects, decisions):
    bits = []
    role = shot.get('role') if shot else None
    if 'hook' in kinds: bits.append('Hook: the first image has to earn the next second')
    if 'drop' in kinds: bits.append('The main beat lands here')
    if 'end' in kinds: bits.append('Closing frame')
    if 'transition' in kinds and effects: bits.append(f'{effects[0]} marks the cut on the beat')
    if 'section' in kinds and role: bits.append(f'Section change to {role}')
    if 'caption' in kinds: bits.append('Caption phrase on screen')
    why = f"{edl.get('style', 'style')} style"
    if decisions and decisions.get('style'):
        why += f" (auto-chosen, score {decisions.get('score')})"
    bits.append(why)
    if shot and shot.get('speed') not in (None, 1.0): bits.append(f"speed x{shot['speed']}")
    return '. '.join(bits[:3]) + '.'


def build_panels(edl, decisions=None, cap=18):
    fps = edl.get('fps') or 30
    phrases = _phrases(edl)
    panels = []
    for n, m in enumerate(select_moments(edl, cap), 1):
        t = m['t']; i, sh = _shot_at(edl, t)
        text = next((p for a, b, p in phrases if a - 0.05 <= t <= b + 0.05), '')
        effects = []
        for ev in edl.get('events', []):
            if ev['t0'] - 0.02 <= t <= ev['t1'] + 0.02:
                effects.append(ev['fx'] + (' (cut)' if ev.get('at') == 'cut' else ''))
        sfx = [f"{s.get('kind')} (gain {s.get('gain')})" for s in edl.get('sfx', []) if abs(s['t'] - t) <= 0.25]
        clip = Path(sh['clip']).name if sh and sh.get('clip') else ''
        src_t = round(sh['src_in'] + (t - sh['t0']) * (sh.get('speed') or 1.0), 2) if sh and sh.get('src_in') is not None else None
        panels.append({
            'n': n, 't': t, 'frame': int(round(t * fps)), 'kinds': m['kinds'],
            'section': f"{sh.get('role')} (shot {i + 1} of {len(edl['shots'])})" if sh else '',
            'source': clip + (f' @ {src_t}s' if src_t is not None else ''),
            'text': text, 'effect': ', '.join(effects) or 'none',
            'beat': _beat_cue(edl, t), 'sfx': ', '.join(sfx) or 'none',
            'intent': _intent(edl, sh, m['kinds'], effects, decisions),
            'shot_index': i,
        })
    return panels


def _size(aspect, short=480):
    a, b = (int(x) for x in aspect.split(':'))
    return (short, short * b // a) if b >= a else (short * a // b, short)


def _ffmpeg_frame(path, t, W, H):
    from PIL import Image
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f: out = f.name
    seek = ['-ss', f'{t:.3f}'] if t > 0 else []                  # -ss 0 on a still image yields no frame
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *seek, '-i', str(path), '-frames:v', '1', out], check=False)
    try: im = Image.open(out).convert('RGB'); im.load()
    except Exception: im = Image.new('RGB', (W, H), (40, 0, 40))
    os.unlink(out)
    return im


def plan_frame(edl, panel, W, H):
    """Source frame at the planned clip time, cover-cropped around the focus point, with the shot's grade
    and the caption text drawn on. An approximation: camera moves, transitions and overlays are not applied."""
    from PIL import Image, ImageDraw, ImageEnhance, ImageFont
    sh = edl['shots'][panel['shot_index']]
    import paths
    clip = paths.media(sh['clip'])
    src_t = sh['src_in'] + (panel['t'] - sh['t0']) * (sh.get('speed') or 1.0) if sh.get('clip_kind') != 'image' else 0
    im = _ffmpeg_frame(clip, src_t, W, H)
    sw, sh_ = im.size
    f = max(W / sw, H / sh_)
    Wc, Hc = int(sw * f + 0.999), int(sh_ * f + 0.999)
    im = im.resize((Wc, Hc))
    fx, fy = sh.get('focus') or (0.5, 0.5)
    cx = int(min(max(fx * Wc - W / 2, 0), Wc - W)); cy = int(min(max(fy * Hc - H / 2, 0), Hc - H))
    im = im.crop((cx, cy, cx + W, cy + H))
    g = sh.get('grade') or {}
    if g.get('bw'): im = im.convert('L').convert('RGB')
    for key, enh in (('saturation', ImageEnhance.Color), ('contrast', ImageEnhance.Contrast), ('brightness', ImageEnhance.Brightness)):
        if g.get(key) not in (None, 1.0, 0, 0.0) and not (key == 'brightness' and abs(g[key]) < 0.01):
            try: im = enh(im).enhance(float(g[key]) if key != 'brightness' or g[key] > 0.5 else 1 + g[key])
            except Exception: pass
    if panel['text']:
        d = ImageDraw.Draw(im)
        try: font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', max(14, W // 12))
        except Exception: font = ImageFont.load_default()
        words, lines, cur = panel['text'].split(), [], ''
        for w in words:
            if d.textlength((cur + ' ' + w).strip(), font=font) > W * 0.9 and cur: lines.append(cur); cur = w
            else: cur = (cur + ' ' + w).strip()
        lines.append(cur)
        y = int(H * 0.72)
        for ln in lines:
            tw = d.textlength(ln, font=font); x = (W - tw) / 2
            d.text((x + 2, y + 2), ln, font=font, fill=(0, 0, 0)); d.text((x, y), ln, font=font, fill=(255, 255, 255))
            y += int(font.size * 1.2) if hasattr(font, 'size') else 20
    return im


def _esc(s): return html.escape(str(s), quote=True)


def render_html(panels, meta):
    rows = [('Time', lambda p: f"{p['t']:.2f}s, frame {p['frame']}"), ('Moment', lambda p: ', '.join(p['kinds'])),
            ('Section', lambda p: p['section']), ('Source', lambda p: p['source']), ('On screen', lambda p: p['text'] or 'no text'),
            ('Effect', lambda p: p['effect']), ('Beat', lambda p: p['beat']), ('Sound', lambda p: p['sfx'])]
    pages = [panels[:6]] + [panels[i:i + 6] for i in range(6, len(panels), 6)]
    out = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><title>' + _esc(meta['title']) + '</title><style>',
           '@page{size:A4 landscape;margin:8mm}*{box-sizing:border-box}body{margin:0;font:8pt/1.3 -apple-system,Helvetica,Arial,sans-serif;color:#1a1a1a;background:#fff}',
           '.page{width:281mm;height:194mm;page-break-after:always;display:flex;flex-direction:column}.page:last-child{page-break-after:auto}',
           'h1{font-size:17pt;margin:0 0 1mm}.sub{color:#555;margin:0 0 3mm;font-size:8.5pt}',
           '.grid{flex:1;display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(2,1fr);gap:3mm;min-height:0}',
           '.panel{display:flex;gap:2.5mm;border:.3mm solid #ccc;border-radius:1.5mm;padding:2mm;min-height:0;overflow:hidden}',
           '.panel img{height:100%;max-width:46%;object-fit:contain;align-self:flex-start;background:#111}',
           '.meta{flex:1;min-width:0;font-size:6.6pt}.meta b{color:#555;font-weight:600}.meta .n{font-size:9pt;font-weight:700}',
           '.meta p{margin:0 0 .8mm;overflow-wrap:anywhere}.intent{font-style:italic;margin-top:1mm}',
           '</style></head><body>']
    for pi, pg in enumerate(pages):
        out.append('<section class="page">')
        if pi == 0:
            out.append(f"<h1>{_esc(meta['title'])}</h1><p class=\"sub\">{_esc(meta['subtitle'])}</p>")
        out.append('<div class="grid">')
        for p in pg:
            out.append('<div class="panel"><img src="%s" alt="Frame %d"><div class="meta"><p class="n">%d</p>' % (_esc(p['image']), p['n'], p['n']))
            for label, fn in rows: out.append(f'<p><b>{label}</b> {_esc(fn(p))}</p>')
            out.append(f"<p class=\"intent\">{_esc(p['intent'])}</p></div></div>")
        out.append('</div></section>')
    out.append('</body></html>')
    return '\n'.join(out)


def make_pdf(html_path, pdf_path):
    if not os.path.exists(CHROME): return False
    with tempfile.TemporaryDirectory() as prof:             # own profile, so a running Chrome cannot swallow the job
        try:
            subprocess.run([CHROME, '--headless=new', '--disable-gpu', f'--user-data-dir={prof}', '--no-pdf-header-footer',
                            f'--print-to-pdf={pdf_path}', Path(html_path).resolve().as_uri()], capture_output=True, timeout=60)
        except subprocess.TimeoutExpired:
            pass
    return Path(pdf_path).exists()


def storyboard(edl, out_dir, video=None, decisions=None, cap=18, pdf=True, title=None):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    frames = out_dir / 'storyboard_frames'; frames.mkdir(exist_ok=True)
    W, H = _size(edl.get('aspect', '9:16'))
    panels = build_panels(edl, decisions, cap)
    mode = 'render' if video else 'plan'
    for p in panels:
        im = _ffmpeg_frame(video, p['t'], W, H).resize((W, H)) if video else plan_frame(edl, p, W, H)
        name = f"panel_{p['n']:02d}.jpg"; im.save(frames / name, quality=88)
        p['image'] = f'storyboard_frames/{name}'
    sub = (f"{edl.get('style', '')} style, {edl.get('duration', 0):.1f}s, {edl.get('aspect', '')}, {len(panels)} key frames. "
           + ('Exact frames from the rendered video.' if video else 'Plan preview: source frames with the planned crop, grade and caption. Camera moves, transitions and overlays appear only in the render.'))
    meta = {'title': title or 'Storyboard', 'subtitle': sub, 'mode': mode}
    (out_dir / 'storyboard.html').write_text(render_html(panels, meta))
    (out_dir / 'storyboard.json').write_text(json.dumps({**meta, 'style': edl.get('style'), 'fps': edl.get('fps'),
                                                         'duration': edl.get('duration'), 'panels': panels}, indent=1))
    ok = make_pdf(out_dir / 'storyboard.html', out_dir / 'storyboard.pdf') if pdf else False
    if pdf and not ok: print('storyboard.pdf skipped: headless Chrome not found at', CHROME)
    return {'html': out_dir / 'storyboard.html', 'json': out_dir / 'storyboard.json', 'pdf': out_dir / 'storyboard.pdf' if ok else None, 'panels': panels}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('input', help='edl.json or a rendered edit.mp4 (edl.json is taken from beside it)')
    ap.add_argument('--video'); ap.add_argument('--edl'); ap.add_argument('--out'); ap.add_argument('--decisions')
    ap.add_argument('--cap', type=int, default=18); ap.add_argument('--no-pdf', action='store_true'); ap.add_argument('--title')
    a = ap.parse_args(argv)
    inp = Path(a.input)
    video = a.video or (str(inp) if inp.suffix.lower() in ('.mp4', '.mov', '.m4v') else None)
    edl_path = Path(a.edl) if a.edl else (inp if inp.suffix == '.json' else inp.with_name('edl.json'))
    edl = json.load(open(edl_path))
    dec = Path(a.decisions) if a.decisions else edl_path.with_name('decisions.json')
    decisions = json.load(open(dec)) if dec.exists() else None
    res = storyboard(edl, a.out or edl_path.parent, video, decisions, a.cap, not a.no_pdf, a.title)
    print('wrote', res['html'], res['json'], res['pdf'] or '(no pdf)')


if __name__ == '__main__':
    main()

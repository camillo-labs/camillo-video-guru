#!/usr/bin/env python3
"""Compare two renders of the same footage: sequential A-then-B playback (each with its own,
loudness-matched audio), or a split screen with one selectable audio track. Burns in a beat/cut/
SFX tick strip read from each side's edl.json when given, and can align the split screen on the
first downbeat or drop instead of each clip's own t=0. Pairs with framegrid.py (a contact sheet
of stills) for a moving comparison instead of a static one.

  engine/tools/sidebyside.py --a tests/green-label/green-label.mp4 --b /tmp/old.mp4 --out /tmp/sbs.mp4
      sequential: A plays in full, then B, each with its own audio, loudness-matched to -16 LUFS

  engine/tools/sidebyside.py --a A.mp4 --b B.mp4 --out /tmp/sbs.mp4 --mode split --audio b \\
      --a-edl tests/green-label/edl.json --b-edl /tmp/old-edl.json --align drop
      split screen, B's audio, aligned on each side's first beat-grid drop, tick strip burned
      into the bottom of each half from its own edl.json

--align start is the default for split (no shift); --align downbeat/drop needs both --a-edl and
--b-edl (skipped, with a warning on stderr, if either is missing).
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

TICK_H = 28
LOUDNESS_TARGET = -16.0


def probe_duration(path):
    out = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)],
        capture_output=True, text=True,
    ).stdout.strip()
    return float(out) if out else 0.0


def probe_size(path):
    out = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
         '-of', 'csv=p=0', str(path)],
        capture_output=True, text=True,
    ).stdout.strip()
    w, h = out.split(',')
    return int(w), int(h)


def load_edl(path):
    if not path:
        return None
    return json.load(open(path, encoding='utf-8'))


def first_downbeat(edl):
    # the engine always opens a shot list on a downbeat (shots[0].beat0 == 0), so the first
    # downbeat sits at the edit's own t=0, not at music.start (that's the offset *into the song
    # file*, not a position in the rendered video)
    return 0.0


def first_drop(edl):
    drops = (edl.get('music') or {}).get('drops_in_window')
    return drops[0] if drops else first_downbeat(edl)


def align_offset(a_edl, b_edl, how):
    if how == 'start' or not a_edl or not b_edl:
        return 0.0, 0.0
    fn = first_drop if how == 'drop' else first_downbeat
    ta, tb = fn(a_edl), fn(b_edl)
    # positive a_delay means A starts later (B is trimmed instead), and vice versa
    return max(0.0, tb - ta), max(0.0, ta - tb)


def beat_times(edl):
    music = edl.get('music') or {}
    start, period, dur = music.get('start'), music.get('beat_period'), edl.get('duration')
    if not period or dur is None:
        return []
    out, t = [], start or 0.0
    # edl time 0 is the first beat in the music's own clock (make_edit.py seeds music.start there)
    t = 0.0
    while t <= dur:
        out.append(t)
        t += period
    return out


def cut_times(edl):
    return sorted({sh['t0'] for sh in edl.get('shots', []) if sh.get('t0') is not None} | {0.0})


def sfx_times(edl):
    return [s['t'] for s in edl.get('sfx', []) if 't' in s]


def build_tick_strip(edl, width, height=TICK_H):
    dur = edl.get('duration') or 1.0
    im = Image.new('RGB', (width, height), (18, 18, 18))
    d = ImageDraw.Draw(im)

    def x_of(t):
        return max(0, min(width - 1, int(t / dur * width)))

    for t in beat_times(edl):
        x = x_of(t)
        d.line([(x, height - 6), (x, height - 1)], fill=(110, 110, 110), width=1)
    for t in cut_times(edl):
        x = x_of(t)
        d.line([(x, 2), (x, height - 1)], fill=(255, 180, 40), width=2)
    for t in sfx_times(edl):
        x = x_of(t)
        d.line([(x, 0), (x, height - 1)], fill=(230, 40, 40), width=1)
    return im


def write_tick_strip(edl, width, out_path):
    build_tick_strip(edl, width).save(out_path)
    return out_path


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f'ffmpeg failed: {" ".join(cmd)}\n{r.stderr[-4000:]}')


def sequential(a, b, out, w, h, a_tick=None, b_tick=None):
    inputs = ['-i', str(a), '-i', str(b)]
    extra_inputs = []
    overlay_a = overlay_b = ''
    vidx = 2
    if a_tick:
        extra_inputs += ['-i', str(a_tick)]
        overlay_a = f';[v0][{vidx}:v]overlay=0:H-{TICK_H}[v0]'
        vidx += 1
    if b_tick:
        extra_inputs += ['-i', str(b_tick)]
        overlay_b = f';[v1][{vidx}:v]overlay=0:H-{TICK_H}[v1]'

    base = (
        f"[0:v]scale={w}:{h}:force_original_aspect_ratio=decrease,"
        f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1[v0];"
        f"[1:v]scale={w}:{h}:force_original_aspect_ratio=decrease,"
        f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1[v1];"
        f"[0:a]loudnorm=I={LOUDNESS_TARGET}:TP=-1.5:LRA=11[a0];"
        f"[1:a]loudnorm=I={LOUDNESS_TARGET}:TP=-1.5:LRA=11[a1]"
    )
    fc = base + overlay_a + overlay_b + ';[v0][a0][v1][a1]concat=n=2:v=1:a=1[outv][outa]'
    cmd = ['ffmpeg', '-v', 'error', '-y', *inputs, *extra_inputs, '-filter_complex', fc,
           '-map', '[outv]', '-map', '[outa]', '-c:v', 'libx264', '-c:a', 'aac', str(out)]
    run(cmd)


def split(a, b, out, w, h, audio, a_delay, b_delay, a_tick=None, b_tick=None):
    half = w // 2
    inputs = ['-i', str(a), '-i', str(b)]
    extra_inputs, vidx = [], 2
    tick_a = tick_b = ''
    if a_tick:
        extra_inputs += ['-i', str(a_tick)]
        tick_a = f';[v0][{vidx}:v]overlay=0:H-{TICK_H}[v0]'
        vidx += 1
    if b_tick:
        extra_inputs += ['-i', str(b_tick)]
        tick_b = f';[v1][{vidx}:v]overlay=0:H-{TICK_H}[v1]'

    delay_a = f'tpad=start_duration={a_delay:.3f}:color=black,' if a_delay > 0 else ''
    delay_b = f'tpad=start_duration={b_delay:.3f}:color=black,' if b_delay > 0 else ''

    fc = (
        f"[0:v]{delay_a}scale={half}:{h}:force_original_aspect_ratio=decrease,"
        f"pad={half}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1[v0];"
        f"[1:v]{delay_b}scale={half}:{h}:force_original_aspect_ratio=decrease,"
        f"pad={half}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1[v1]"
        f"{tick_a}{tick_b};[v0][v1]hstack=inputs=2[outv]"
    )
    a_idx = '0' if audio != 'b' else '1'
    delay_audio = f'adelay=delays={int(a_delay * 1000)}|{int(a_delay * 1000)},' if audio != 'b' and a_delay > 0 else (
        f'adelay=delays={int(b_delay * 1000)}|{int(b_delay * 1000)},' if audio == 'b' and b_delay > 0 else '')
    fc += f';[{a_idx}:a]{delay_audio}loudnorm=I={LOUDNESS_TARGET}:TP=-1.5:LRA=11[outa]'

    cmd = ['ffmpeg', '-v', 'error', '-y', *inputs, *extra_inputs, '-filter_complex', fc,
           '-map', '[outv]', '-map', '[outa]', '-c:v', 'libx264', '-c:a', 'aac', str(out)]
    run(cmd)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--a', required=True)
    p.add_argument('--b', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--mode', choices=['sequential', 'split'], default='sequential')
    p.add_argument('--audio', choices=['a', 'b'], default='a', help='split mode only: which side\'s audio to keep')
    p.add_argument('--align', choices=['start', 'downbeat', 'drop'], default='start', help='split mode only')
    p.add_argument('--a-edl')
    p.add_argument('--b-edl')
    p.add_argument('--h', type=int, default=720)
    a = p.parse_args()

    wa, ha = probe_size(a.a)
    out_h = a.h
    out_w = int(round(out_h * wa / ha / 2)) * 2  # each side's own width, kept at full aspect either way
    full_w = out_w * 2 if a.mode == 'split' else out_w

    a_edl, b_edl = load_edl(a.a_edl), load_edl(a.b_edl)
    if a.align != 'start' and not (a_edl and b_edl):
        print(f'--align {a.align} needs both --a-edl and --b-edl, aligning on start instead', file=sys.stderr)
        a.align = 'start'
    a_delay, b_delay = align_offset(a_edl, b_edl, a.align) if a.mode == 'split' else (0.0, 0.0)

    with tempfile.TemporaryDirectory() as td:
        a_tick = write_tick_strip(a_edl, full_w if a.mode == 'sequential' else out_w, Path(td) / 'a_tick.png') if a_edl else None
        b_tick = write_tick_strip(b_edl, full_w if a.mode == 'sequential' else out_w, Path(td) / 'b_tick.png') if b_edl else None

        if a.mode == 'sequential':
            sequential(a.a, a.b, a.out, out_w, out_h, a_tick, b_tick)
        else:
            split(a.a, a.b, a.out, full_w, out_h, a.audio, a_delay, b_delay, a_tick, b_tick)
    print(f'wrote {a.out}')


if __name__ == '__main__':
    main()

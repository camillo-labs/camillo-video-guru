"""Builds the video engine explainer: animated pipeline scenes drawn with Pillow, real captures of the engine's own
outputs, word-timed captions, synthesised sound from engine/sfx.py, then the 1920x1080 film and a 1080x1920 cut.

  python build.py still 3.5 12.0      writes work/still-<t>.png (no audio)
  python build.py render [name]       writes out/<name>.mp4 and out/<name>-vertical.mp4 (default name video-engine-explainer)
Run with edits/.venv/bin/python.
"""
import sys, json, subprocess, difflib, re, wave, math, pathlib
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = pathlib.Path(__file__).resolve().parent; WK = HERE / "work"; OUT = HERE / "out"; ED = HERE.parent
sys.path.insert(0, str(ED / "engine"))
import sfx as SFX
W, H, FPS = 1920, 1080, 30
FONTS = ED / "engine/assets/fonts"
DARK, LIGHT, BEIGE, TERRA, BLUE, INK = (15, 15, 20), (245, 242, 235), (233, 223, 202), (204, 98, 64), (62, 104, 255), (22, 22, 28)
MUTE = (120, 118, 112)

_fc = {}
def F(name, size, var=None):
    k = (name, size, var)
    if k not in _fc:
        f = ImageFont.truetype(str(FONTS / name), size)
        if var:
            try: f.set_variation_by_name(var)
            except Exception: pass
        _fc[k] = f
    return _fc[k]
ANTON = lambda s: F("Anton-Regular.ttf", s)
SERIF = lambda s: F("InstrumentSerif-Italic.ttf", s)
SANS = lambda s: F("InterTight-Variable.ttf", s, "Bold")
SANSR = lambda s: F("InterTight-Variable.ttf", s, "Medium")
GROT = lambda s: F("SpaceGrotesk-Variable.ttf", s, "Bold")

def cl(x): return max(0.0, min(1.0, x))
def E(x): x = cl(x); return 1 - (1 - x) ** 3
def ph(t, a, d=0.5): return E((t - a) / d)
def mix(a, b, u): return tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3))
def rr(d, box, r=14, fill=None, outline=None, w=2): d.rounded_rectangle(box, r, fill=fill, outline=outline, width=w)
def tx(d, xy, s, f, fill, anchor="la"): d.text(xy, s, font=f, fill=fill, anchor=anchor)
def arrow(d, a, b, col, w=5, u=1.0):
    x0, y0 = a; x1, y1 = b; x1 = x0 + (x1 - x0) * u; y1 = y0 + (y1 - y0) * u
    d.line([(x0, y0), (x1, y1)], fill=col, width=w)
    if u > 0.95:
        ang = math.atan2(y1 - y0, x1 - x0)
        for s in (-0.5, 0.5): d.line([(x1, y1), (x1 - 18 * math.cos(ang + s), y1 - 18 * math.sin(ang + s))], fill=col, width=w)

# ---------- data ----------
LINES = json.load(open(WK / "lines.json")); STARTS = json.load(open(WK / "starts.json")); WORDS = json.load(open(WK / "words.json"))
TOTAL = 64.85
nar = wave.open(str(WK / "narration.wav")); NARR = np.frombuffer(nar.readframes(nar.getnframes()), "<i2").astype(np.float32) / 32768; NSR = nar.getframerate()
ENV = np.array([np.abs(NARR[i:i + NSR // 100]).max() for i in range(0, len(NARR) - NSR // 100, NSR // 100)])  # 100 per second

def norm(s): return re.sub(r"[^a-z0-9]", "", s.lower())
def caption_words():
    """Script tokens with times: Whisper word times inside each line window, matched to the script text."""
    out = []
    for (a, b), line in zip(STARTS, LINES):
        toks = line.split(); ww = [w for w in WORDS if a - 0.15 <= w["s"] < b + 0.1]
        A = [norm(t) for t in toks]; B = [norm(w["w"]) for w in ww]
        sm = difflib.SequenceMatcher(None, A, B, autojunk=False); st = [None] * len(toks)
        for blk in sm.get_matching_blocks():
            for k in range(blk.size): st[blk.a + k] = ww[blk.b + k]["s"]
        st[0] = a if st[0] is None or st[0] > a + 0.3 else st[0]
        # interpolate unmatched by character length
        i = 0
        while i < len(toks):
            if st[i] is None:
                j = i
                while j < len(toks) and st[j] is None: j += 1
                lo = st[i - 1]; hi = st[j] if j < len(toks) else b
                lens = [len(t) + 1 for t in toks[i - 1:j]]; tot = sum(lens)
                acc = lens[0]
                for k in range(i, j): st[k] = lo + (hi - lo) * acc / tot; acc += lens[k - i + 1]
                i = j
            else: i += 1
        for k, t in enumerate(toks): out.append((t, st[k], st[k + 1] if k + 1 < len(toks) else b))
    return out
CW = caption_words()
def chunks():
    ch, cur = [], []
    for w in CW:
        cur.append(w)
        if re.search(r"[,.:;]$", w[0]) or len(cur) >= 4 or sum(len(x[0]) + 1 for x in cur) > 26: ch.append(cur); cur = []
    if cur: ch.append(cur)
    return ch
CH = chunks()
def active_chunk(t):
    for i, c in enumerate(CH):
        end = CH[i + 1][0][1] if i + 1 < len(CH) else c[-1][2] + 0.5
        if c[0][1] - 0.05 <= t < min(end, c[-1][2] + 0.45): return c
    return None

def draw_caption(d, t, cx, y, size, maxw, plate=True):
    c = active_chunk(t)
    if not c: return
    f = SANS(size); gap = size * 0.28
    widths = [d.textlength(w[0], font=f) for w in c]; total = sum(widths) + gap * (len(c) - 1)
    pad = size * 0.5; x0 = cx - total / 2
    if plate: rr(d, (x0 - pad, y - size * 0.35, x0 + total + pad, y + size * 1.15), 18, fill=(10, 10, 14, 215))
    x = x0
    for (word, s, e), wd in zip(c, widths):
        on = s <= t < e + 0.02; past = t >= e
        tx(d, (x, y), word, f, (255, 255, 255) if past else (TERRA if on else (200, 200, 205)))
        x += wd + gap

# ---------- real media ----------
class Vid:
    def __init__(s, path, loop=True):
        s.cap = cv2.VideoCapture(str(path)); s.n = int(s.cap.get(cv2.CAP_PROP_FRAME_COUNT)); s.fps = s.cap.get(cv2.CAP_PROP_FPS) or 30
        s.pos = 0; s.loop = loop; s.last = None
    def at(s, t):
        i = int(t * s.fps); i = i % s.n if s.loop else min(i, s.n - 1)
        if i != s.pos:
            if i != s.pos + 1 or s.last is None: s.cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            s.pos = i
        else: s.pos = i
        ok, fr = s.cap.read()
        if ok: s.last = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)); s.pos = i
        return s.last
    def cover(s, t, w, h):
        im = s.at(t)
        if im is None: return Image.new("RGB", (w, h), (30, 30, 30))
        sc = max(w / im.width, h / im.height); im = im.resize((int(im.width * sc) + 1, int(im.height * sc) + 1))
        l, tp = (im.width - w) // 2, (im.height - h) // 2; return im.crop((l, tp, l + w, tp + h))
_vc = {}
def V(name, path, loop=True):
    if name not in _vc: _vc[name] = Vid(path, loop)
    return _vc[name]
def paste_round(img, im, xy, r=18):
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255); img.paste(im, xy, m)

# ---------- stages strip ----------
STAGES = ["Sources", "Script", "Voice", "Word timing", "Styles", "Beat edit", "Captions", "Sound", "Export", "Review"]
LINE_STAGE = {1: [], 2: [0], 3: [1, 2], 4: [3], 5: [4], 6: [5], 7: [6], 8: [7], 9: [5], 10: [8], 11: [9], 12: list(range(10))}
def strip(d, line, fg, accent):
    x = 100; act = LINE_STAGE.get(line, [])
    for i, s in enumerate(STAGES):
        f = SANS(21); w = d.textlength(s, font=f) + 34; on = i in act
        rr(d, (x, 38, x + w, 78), 20, fill=accent if on else None, outline=accent if on else mix(fg, (128, 128, 128), 0.55), w=2)
        tx(d, (x + w / 2, 58), s, f, (255, 255, 255) if on else mix(fg, (128, 128, 128), 0.3), "mm"); x += w + 12

# ---------- scenes ----------
def line_of(t):
    for i, (a, b) in enumerate(STARTS):
        nxt = STARTS[i + 1][0] - 0.15 if i + 1 < len(STARTS) else TOTAL
        if t < nxt: return i + 1, (0 if i == 0 else a - 0.15), nxt
    return 12, STARTS[-1][0], TOTAL

LEDGER = json.load(open(ED.parent.parent / "green-label-content/data/fact_ledger.json"))["rows"]
SCRIPT_TXT = open(ED.parent.parent / "green-label-content/output/2026-w42/video-script.txt").read().strip().splitlines()
CHECK = json.load(open(ED / "tests/green-label/check.json"))
CUTS = [0, 3.5, 7.00, 8.43, 9.77, 10.87, 12.20, 13.80, 15.13, 16.47, 17.77, 19.13, 20.47, 21.80, 23.20, 24.53, 25.77, 27.17, 28.33, 29.90, 31.20, 32.63, 33.80, 35.00, 36.50, 37.90, 39.20, 40.53, 41.90, 43.07, 44.43, 47.57, 50.50]

def s1(img, d, t, p, L):
    d.rectangle((0, 0, W, H), fill=DARK)
    u = ph(t, 0.2, 0.7); tx(d, (100, 170 + (1 - u) * 40), "How Cam's video engine", ANTON(124), mix(DARK, (245, 242, 235), u))
    u = ph(t, 0.6, 0.7); tx(d, (100, 310 + (1 - u) * 40), "builds a video by itself", SERIF(112), mix(DARK, BLUE, u) if False else mix(DARK, (120, 150, 255), u))
    nodes = ["sources", "script", "voice", "timing", "edit", "export"]; x0, y0, bw, gap = 100, 560, 235, 60
    for i, n in enumerate(nodes):
        a = 1.4 + i * 0.55; u = ph(t, a, 0.4)
        if u <= 0: continue
        x = x0 + i * (bw + gap)
        if i: arrow(d, (x - gap + 8, y0 + 55), (x - 8, y0 + 55), (170, 170, 180), 4, ph(t, a - 0.25, 0.25))
        rr(d, (x, y0 + (1 - u) * 24, x + bw, y0 + 110 + (1 - u) * 24), 18, fill=mix(DARK, (38, 38, 52), u), outline=mix(DARK, (120, 150, 255), u), w=3)
        tx(d, (x + bw / 2, y0 + 55 + (1 - u) * 24), n, SANS(40), mix(DARK, (245, 242, 235), u), "mm")
    u = ph(t, 4.8, 0.6)
    if u > 0:
        vid = V("engine", WK / "engine_run/edit.mp4").cover(t - 4.8, 520, 292)
        paste_round(img, vid, (1300, 700 + int((1 - u) * 30)), 14)
        tx(d, (1300, 1005 - 5), "", SANSR(20), MUTE)
        tx(d, (100, 760), "Rendered by make_edit.py,", SANS(34), (245, 242, 235)); tx(d, (100, 806), "kinetic-card-explainer style, from this narration", SANSR(30), (180, 180, 190))

def s2(img, d, t, p, L):
    d.rectangle((0, 0, W, H), fill=LIGHT)
    srcs = [("feedparser", "RSS and Atom feeds"), ("trafilatura", "text from web pages")]
    for i, (a, b) in enumerate(srcs):
        u = ph(t, 0.2 + i * 0.4, 0.5); y = 200 + i * 230
        rr(d, (100 - (1 - u) * 60, y, 640 - (1 - u) * 60, y + 170), 20, fill=INK if i == 0 else TERRA)
        tx(d, (140 - (1 - u) * 60, y + 30), a, ANTON(64), (245, 242, 235)); tx(d, (140 - (1 - u) * 60, y + 122), b, SANSR(32), (225, 225, 230))
        arrow(d, (650, y + 85), (800, 540), MUTE, 5, ph(t, 0.9 + i * 0.3, 0.5))
    u = ph(t, 1.2, 0.5); rr(d, (820, 190, 1820, 800), 22, fill=(255, 255, 255), outline=INK, w=3)
    tx(d, (860, 215), "fact ledger", SERIF(64), INK)
    for i, r in enumerate(LEDGER[:4]):
        a = 1.6 + i * 0.5; uu = ph(t, a, 0.4)
        if uu <= 0: continue
        y = 320 + i * 118; claim = r["claim"]; claim = (claim[:62] + "...") if len(claim) > 64 else claim
        rr(d, (850, y, 1790, y + 100), 12, fill=mix((255, 255, 255), BEIGE, uu))
        tx(d, (870, y + 14), r["id"], GROT(34), TERRA); tx(d, (950, y + 14), claim, SANSR(27), INK)
        tx(d, (950, y + 56), "quote and source kept, checked " + r["checked_on"], SANSR(23), MUTE)

def s3(img, d, t, p, L):
    d.rectangle((0, 0, W, H), fill=BEIGE)
    rr(d, (100, 190, 1020, 800), 22, fill=(255, 255, 255)); tx(d, (140, 220), "script from the ledger", SERIF(58), INK)
    full = "\n".join(SCRIPT_TXT[:3]); n = int(cl((t - 0.3) / 2.6) * len(full)); shown = full[:n]
    y = 320
    for ln in shown.split("\n"):
        words = ln.split(); line = ""
        for w_ in words:
            if d.textlength(line + w_, font=SANSR(28)) > 830: tx(d, (140, y), line, SANSR(28), INK); y += 40; line = ""
            line += w_ + " "
        tx(d, (140, y), line, SANSR(28), INK); y += 52
    u = ph(t, 1.3, 0.5); arrow(d, (1040, 495), (1150, 495), MUTE, 5, u)
    u = ph(t, 1.6, 0.5); rr(d, (1170, 300, 1820, 700), 22, fill=INK)
    tx(d, (1210, 340), "Kokoro-82M", ANTON(78), (245, 242, 235)); tx(d, (1210, 440), "narration, runs on my own machine", SANSR(32), (200, 200, 208))
    for i in range(34):
        hgt = 20 + 90 * abs(math.sin(i * 0.7 + t * 9)) * (0.4 + 0.6 * abs(math.sin(i * 0.31 + t * 3))) * u
        x = 1210 + i * 17; d.rounded_rectangle((x, 600 - hgt / 2, x + 9, 600 + hgt / 2), 4, fill=TERRA)

def s4(img, d, t, p, L, gt=0):
    d.rectangle((0, 0, W, H), fill=DARK)
    tx(d, (100, 150), "faster-whisper", ANTON(90), (245, 242, 235)); tx(d, (100, 255), "every word gets a start and an end", SERIF(60), (120, 150, 255))
    win = 3.0; t0 = gt - win / 2; x0, x1, yc = 100, 1820, 560
    d.line((x0, yc + 150, x1, yc + 150), fill=(60, 60, 75), width=2)
    for i in range(int(x1 - x0)):
        tt = t0 + i / (x1 - x0) * win; k = int(tt * 100)
        if 0 <= k < len(ENV):
            hgt = max(3, ENV[k] * 300); col = TERRA if abs(tt - gt) < 0.015 else (150, 160, 185)
            d.line((x0 + i, yc - hgt / 2, x0 + i, yc + hgt / 2), fill=col, width=1)
    for w in WORDS:
        if t0 - 0.2 < w["s"] < t0 + win:
            xa = x0 + (w["s"] - t0) / win * (x1 - x0); xb = x0 + (w["e"] - t0) / win * (x1 - x0)
            if xa < x0 - 5 or xb > x1 + 5: continue
            on = w["s"] <= gt < w["e"]
            rr(d, (xa, yc + 170, max(xb, xa + 40), yc + 232), 10, fill=TERRA if on else (44, 44, 62))
            tx(d, (xa + 8, yc + 177), w["w"], SANS(28), (255, 255, 255)); tx(d, (xa + 4, yc + 240), f"{w['s']:.2f}s", GROT(20), (150, 150, 170))
    xp = x0 + (gt - t0) / win * (x1 - x0); d.line((xp, yc - 160, xp, yc + 160), fill=(255, 255, 255), width=2)

def s5(img, d, t, p, L):
    d.rectangle((0, 0, W, H), fill=LIGHT)
    tiles = [("bw-flash-vo", "flash cuts, mono to colour", "bw-flash-vo/demo/demo-A-house128-16x9.mp4"), ("lyric-word-beat", "one heavy word per beat", "lyric-word-beat/demo/demo-A-house128.mp4"),
             ("talking-head-split", "reframes on word starts", "talking-head-split/demo/demo-house128.mp4"), ("kinetic-card-explainer", "one idea per card", "kinetic-card-explainer/demo/demo-house128.mp4")]
    tw, th, gap = 410, 480, 26
    for i, (n, sub, path) in enumerate(tiles):
        u = ph(t, 0.2 + i * 0.35, 0.5)
        if u <= 0: continue
        x = 100 + i * (tw + gap); y = 190 + int((1 - u) * 50)
        rr(d, (x, y, x + tw, y + th + 120), 20, fill=INK)
        vid = V("st%d" % i, ED / path).cover(t + i * 1.7, tw - 24, th - 20); paste_round(img, vid, (x + 12, y + 12), 12)
        tx(d, (x + 20, y + th + 6), n, GROT(29), (245, 242, 235)); tx(d, (x + 20, y + th + 52), sub, SANSR(25), (200, 200, 208))
    u = ph(t, 2.2, 0.6)
    if u > 0:
        tx(d, (100, 855), "style.json: shot lengths, grade, moves, sound and captions, measured from a reference", SERIF(44), mix(LIGHT, INK, u))

def s6(img, d, t, p, L):
    d.rectangle((0, 0, W, H), fill=DARK)
    gx0, gx1 = 100, 1280; bpm = 128.0; beat = 60 / bpm; span = 6 * beat
    tx(d, (100, 135), "beat grid", ANTON(76), (245, 242, 235))
    for i in range(0, 6 * 4 + 1):
        x = gx0 + i / 24 * (gx1 - gx0); big = i % 4 == 0
        d.line((x, 300 if big else 330, x, 400), fill=(150, 160, 190) if big else (70, 72, 92), width=3 if big else 1)
    tx(d, (gx0, 255), "music beats and sixteenths", SANSR(26), (150, 150, 170))
    tx(d, (gx0, 425), "cuts snap to the grid", SANSR(26), (150, 150, 170)); tx(d, (gx0, 570), "or to word starts when a voice leads", SANSR(26), (150, 150, 170))
    raw = [x * 0.6 for x in (0.31, 0.92, 1.48, 2.24, 2.69, 3.4, 4.13, 4.52)]
    for i, rt in enumerate(raw):
        a = 0.5 + i * 0.35; u = ph(t, a, 0.5)
        if u <= 0: continue
        snap = round(rt / (beat / 4)) * (beat / 4); x_raw = gx0 + rt / span * (gx1 - gx0); x_sn = gx0 + snap / span * (gx1 - gx0)
        x = x_raw + (x_sn - x_raw) * ph(t, a + 0.35, 0.3); y = 462 + (1 - u) * -60
        d.rounded_rectangle((x - 5, y, x + 5, y + 90), 3, fill=TERRA)
    ws = [(0.45, "talk"), (1.2, "head"), (1.9, "split"), (3.0, "cards"), (3.7, "voice")]
    for i, (wt, w) in enumerate(ws):
        u = ph(t, 1.6 + i * 0.3, 0.4)
        if u <= 0: continue
        x = gx0 + wt / span * (gx1 - gx0); d.rounded_rectangle((x - 5, 600 + (1 - u) * -40, x + 5, 720), 3, fill=(120, 150, 255)); tx(d, (x + 10, 730), w, SANSR(24), (170, 170, 190))
    tx(d, (100, 840), f"{CHECK['share_of_cuts_within_one_frame_of_a_sixteenth'] * 100:.0f}% of cuts in a real render land within one frame of a sixteenth", SERIF(46), (120, 150, 255))
    u = ph(t, 0.4, 0.6)
    vid = V("gl", ED / "tests/green-label/green-label.mp4").cover(t, 300, 533)
    px, py = 1420 + (1 - u) * 80, 170; rr(d, (px - 12, py - 12, px + 312, py + 545), 30, fill=(40, 40, 52)); paste_round(img, vid, (int(px), py), 22)
    tx(d, (px + 150, py + 590), "tests/green-label, bw-flash-vo", SANSR(23), (150, 150, 170), "ma")

def s7(img, d, t, p, L):
    d.rectangle((0, 0, W, H), fill=BEIGE)
    v = V("gl2", ED / "tests/green-label/green-label.mp4")
    for i, ts in enumerate([6.0, 11.0, 15.5]):
        u = ph(t, 0.2 + i * 0.35, 0.5)
        if u <= 0: continue
        im = v.cover(ts + t * 0.05, 330, 586) if False else v.cover(ts, 330, 586)
        x = 100 + i * 360; paste_round(img, im, (x, 170 + int((1 - u) * 50)), 16)
    steps = [("Pillow draws a PNG", "one per word or phrase"), ("ffmpeg overlay", "enable=between(t,a,b)")]
    for i, (a, b) in enumerate(steps):
        u = ph(t, 1.2 + i * 0.5, 0.5); x = 1200; y = 190 + i * 190
        rr(d, (x, y + (1 - u) * 30, 1820, y + 150 + (1 - u) * 30), 18, fill=INK if i == 0 else TERRA)
        tx(d, (x + 30, y + 24 + (1 - u) * 30), a, ANTON(56), (245, 242, 235)); tx(d, (x + 30, y + 92 + (1 - u) * 30), b, GROT(30), (225, 225, 230))
    u = ph(t, 2.4, 0.5)
    if u > 0:
        tx(d, (1200, 600), "drawtext", GROT(46), mix(BEIGE, INK, u)); w_ = d.textlength("drawtext", font=GROT(46)); d.line((1200, 626, 1200 + w_ * u, 626), fill=TERRA, width=5)
        tx(d, (1200, 668), "not built into this ffmpeg", SANSR(32), mix(BEIGE, MUTE, u))

_sf = {}
def sfx_arr(n):
    if n not in _sf: _sf[n] = SFX.SFX[n]()
    return _sf[n]
def s8(img, d, t, p, L):
    d.rectangle((0, 0, W, H), fill=DARK)
    tx(d, (100, 135), "all synthesised, no samples", SERIF(70), (120, 150, 255))
    rows = [("whoosh", 1.3), ("impact", 1.5), ("riser", 1.8), ("click", 1.2)]
    for i, (n, ln) in enumerate(rows):
        y = 260 + i * 165; u = ph(t, 0.3 + i * 0.5, 0.4)
        a = sfx_arr(n)
        rr(d, (100, y, 1820, y + 140), 16, fill=(30, 30, 42))
        tx(d, (130, y + 70), n, GROT(38), (245, 242, 235), "lm")
        N = 1300; seg = np.array_split(a if len(a) else np.zeros(2), N); env = np.array([np.abs(s).max() for s in seg]); env = env / (env.max() + 1e-9)
        reveal = int(N * cl((t - 0.5 - i * 0.5) / 1.2))
        for k in range(reveal):
            h_ = max(2, env[k] * 110); d.line((420 + k, y + 70 - h_ / 2, 420 + k, y + 70 + h_ / 2), fill=TERRA if k > reveal - 25 else (150, 160, 190), width=1)

def s9(img, d, t, p, L):
    d.rectangle((0, 0, W, H), fill=LIGHT)
    tx(d, (100, 135), "a reference clip sets the cuts", ANTON(80), INK)
    x0, x1 = 100, 1820; tot = 50.5; lane = lambda s: x0 + s / tot * (x1 - x0)
    tx(d, (x0, 290), "scene changes found in the reference", SANSR(28), MUTE)
    for i, c in enumerate(CUTS):
        if t * 22 > i: d.rounded_rectangle((lane(c) - 3, 330, lane(c) + 3, 430), 3, fill=INK)
    tx(d, (x0, 510), "fire inserts on the off beat, midway between cuts", SANSR(28), MUTE)
    for i in range(10, 19):
        mid = (CUTS[i] + CUTS[i + 1]) / 2
        if t * 9 > (i - 10) + 4: d.rounded_rectangle((lane(mid) - 14, 550, lane(mid) + 14, 650), 6, fill=TERRA)
    tx(d, (x0, 730), "captions on their own timeline", SANSR(28), MUTE)
    for i in range(14):
        a = 3 + i * 3.4
        if t * 12 > i + 8: rr(d, (lane(a), 770, lane(a + 2.3), 820), 10, fill=(120, 150, 255))

def count(u, v): return int(round(v * E(u)))
def s10(img, d, t, p, L):
    d.rectangle((0, 0, W, H), fill=DARK)
    tx(d, (100, 150), "H.264 + AAC", ANTON(120), (245, 242, 235)); tx(d, (100, 295), "1920 x 1080, 30 fps", SERIF(70), (120, 150, 255))
    u = ph(t, 0.9, 0.6)
    if u > 0:
        vid = V("engine2", WK / "engine_run/edit.mp4").cover(t + 8, 640, 360); paste_round(img, vid, (100, 450 + int((1 - u) * 30)), 16)
        tx(d, (100, 830), "an engine render", SANSR(28), (170, 170, 190))
    stats = [(CHECK["n_planned_cuts"], "cuts planned", ""), (CHECK["n_cuts_detected_in_video"], "cuts found in the video", ""), (CHECK["share_of_cuts_within_one_frame_of_a_sixteenth"] * 100, "% within one frame of the grid", "%")]
    tx(d, (900, 440), "check.py compares the render with the grid", SANSR(34), (200, 200, 208))
    for i, (v, lab, suf) in enumerate(stats):
        u = ph(t, 1.4 + i * 0.4, 0.8); y = 520 + i * 130
        tx(d, (900, y), f"{count(u, v)}" if not suf else f"{v * E(u):.1f}", ANTON(86), TERRA); tx(d, (1180, y + 28), lab if not suf else "of cuts within one frame of the grid", SANSR(32), (245, 242, 235))

def s11(img, d, t, p, L):
    d.rectangle((0, 0, W, H), fill=LIGHT)
    steps = ["render", "score vs reference", "list differences", "change engine"]; cx, cy, r = 500, 530, 250
    for i, s_ in enumerate(steps):
        ang = -math.pi / 2 + i * math.pi / 2; x = cx + r * math.cos(ang) * 1.18; y = cy + r * math.sin(ang)
        on = (t * 0.7) % 4; lit = int(on) == i; u = ph(t, 0.2 + i * 0.35, 0.4)
        if u <= 0: continue
        w_ = d.textlength(s_, font=SANS(28)) + 44
        rr(d, (x - w_ / 2, y - 34, x + w_ / 2, y + 34), 34, fill=TERRA if lit else INK); tx(d, (x, y), s_, SANS(28), (255, 255, 255), "mm")
    for i in range(4):
        a0 = -math.pi / 2 + i * math.pi / 2 + 0.55; a1 = a0 + math.pi / 2 - 1.1
        pts = [(cx + r * 1.18 * math.cos(a0 + (a1 - a0) * k / 12), cy + r * math.sin(a0 + (a1 - a0) * k / 12)) for k in range(13)]
        if t > 1.2 + i * 0.3: d.line(pts, fill=MUTE, width=4)
    tx(d, (cx, cy), "review loop", SERIF(60), INK, "mm")
    # chart: majors per round
    rounds = [("round 1", 8), ("round 2", 3), ("round 3", 0)]
    tx(d, (1000, 170), "bw-flash-vo, major differences", ANTON(52), INK)
    for i, (n, v) in enumerate(rounds):
        a = 3.2 + i * 1.6 if True else 0; u = ph(t, a, 0.8); y = 270 + i * 165
        tx(d, (1000, y + 40), n, SANSR(32), MUTE, "lm"); w_ = 520 * v / 8 * u
        if v: d.rounded_rectangle((1180, y, 1180 + max(w_, 8), y + 80), 10, fill=TERRA)
        tx(d, (1200 + 520 * v / 8 * u + 14, y + 40), str(count(u, v)), ANTON(70), INK, "lm")
    u = ph(t, 8.2, 0.8)
    if u > 0:
        im = Image.open(ED / "bw-flash-vo/review-round-3/01-overview-0-5.4s.png").convert("RGB"); im.thumbnail((640, 240)); paste_round(img, im, (1180, 715), 12)
        tx(d, (1000, 1010 - 18), "", SANSR(20), MUTE)

TOOLS = [("PhotoCraft", "photo"), ("VectorCraft", "vector"), ("DesignCraft", "layout"), ("FilmCraft", "video"), ("EffectCraft", "motion")]
def icon(d, kind, x, y, col):
    if kind == "photo": d.ellipse((x - 30, y - 30, x + 30, y + 30), outline=col, width=5); d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=col)
    elif kind == "vector": d.line((x - 32, y + 28, x - 10, y - 24, x + 14, y + 10, x + 34, y - 28), fill=col, width=5); [d.rectangle((a - 7, b - 7, a + 7, b + 7), fill=col) for a, b in ((x - 32, y + 28), (x - 10, y - 24), (x + 14, y + 10), (x + 34, y - 28))]
    elif kind == "layout": d.rectangle((x - 32, y - 32, x + 32, y + 32), outline=col, width=5); d.line((x - 32, y - 8, x + 32, y - 8), fill=col, width=4); d.line((x, y - 8, x, y + 32), fill=col, width=4)
    elif kind == "video": d.rounded_rectangle((x - 34, y - 24, x + 34, y + 24), 8, outline=col, width=5); d.polygon([(x - 8, y - 12), (x - 8, y + 12), (x + 14, y)], fill=col)
    else: d.arc((x - 32, y - 32, x + 32, y + 32), 20, 340, fill=col, width=5); d.polygon([(x + 20, y - 38), (x + 40, y - 20), (x + 14, y - 14)], fill=col)
def s12(img, d, t, p, L):
    d.rectangle((0, 0, W, H), fill=DARK)
    if t < 3.2:
        tx(d, (100, 150), "creative apps feed the engine", SERIF(70), (120, 150, 255))
        for i, (n, k) in enumerate(TOOLS):
            u = ph(t, 0.3 + i * 0.35, 0.5)
            if u <= 0: continue
            x = 100 + i * 350; y = 300 + int((1 - u) * 40)
            rr(d, (x, y, x + 320, y + 260), 22, fill=(32, 32, 46), outline=(80, 90, 130), w=2); icon(d, k, x + 160, y + 85, (245, 242, 235))
            tx(d, (x + 160, y + 170), n, GROT(32), (245, 242, 235), "mm"); tx(d, (x + 160, y + 214), k, SANSR(28), TERRA, "mm")
            arrow(d, (x + 160, y + 270), (x + 160, 640), (120, 130, 170), 4, ph(t, 0.9 + i * 0.3, 0.4))
        u = ph(t, 2.0, 0.5); rr(d, (100, 650, 1820, 770), 22, fill=TERRA); tx(d, (960, 710), "make_edit.py  +  styles  +  voice  +  review loop", ANTON(60), (255, 255, 255), "mm")
    else:
        u = ph(t, 3.3, 0.7)
        tx(d, (960, 440 + (1 - u) * 30), "Digital media system", ANTON(150), mix(DARK, (245, 242, 235), u), "mm")
        tx(d, (960, 580 + (1 - u) * 30), "Cam's video engine", SERIF(84), mix(DARK, (120, 150, 255), u), "mm")

SCENES = {1: s1, 2: s2, 3: s3, 4: s4, 5: s5, 6: s6, 7: s7, 8: s8, 9: s9, 10: s10, 11: s11, 12: s12}
THEME = {1: (DARK, TERRA), 2: (LIGHT, TERRA), 3: (BEIGE, TERRA), 4: (DARK, TERRA), 5: (LIGHT, TERRA), 6: (DARK, TERRA), 7: (BEIGE, TERRA), 8: (DARK, TERRA), 9: (LIGHT, TERRA), 10: (DARK, TERRA), 11: (LIGHT, TERRA), 12: (DARK, TERRA)}
NOCAP_END = TOTAL - 1.7

def scene_frame(t):
    img = Image.new("RGB", (W, H), DARK); d = ImageDraw.Draw(img)
    ln, a, b = line_of(t); lt = t - a; L = b - a; fn = SCENES[ln]
    if ln == 4: fn(img, d, lt, lt / L, L, gt=t)
    else: fn(img, d, lt, lt / L, L)
    bg, acc = THEME[ln]; strip(d, ln, (245, 242, 235) if bg == DARK else INK, acc)
    return img

def full_frame(t):
    img = scene_frame(t); ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    if t < NOCAP_END: draw_caption(d, t, W // 2, 925, 62, 1500)
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"); return img

def vertical_frame(t, scene=None):
    scene = scene or scene_frame(t); v = Image.new("RGB", (1080, 1920), (12, 12, 17)); d = ImageDraw.Draw(v)
    small = scene.resize((1080, 607), Image.LANCZOS); v.paste(small, (0, 520))
    d.text((60, 190), "Cam's video engine", font=ANTON(96), fill=(245, 242, 235)); d.text((60, 320), "built by itself", font=SERIF(76), fill=(120, 150, 255))
    ov = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    if t < NOCAP_END: draw_caption(od, t, 540, 1290, 70, 960, plate=False)
    return Image.alpha_composite(v.convert("RGBA"), ov).convert("RGB")

# ---------- audio ----------
def make_audio(path):
    SR = 44100; y = np.zeros(int((TOTAL + 0.5) * SR)); y[:len(NARR)] += NARR[:len(y)]
    def put(t, a, g):
        i = int(t * SR); a = a[: len(y) - i] * g; y[i:i + len(a)] += a
    for ln, (a, b) in enumerate(STARTS, 1):
        put(max(a - 0.35, 0.05), sfx_arr("whoosh"), 0.07)
    put(STARTS[0][0] + 5.0, sfx_arr("tick"), 0.06); put(STARTS[8][0] + 0.4, sfx_arr("click"), 0.08); put(STARTS[8][0] + 1.5, sfx_arr("click"), 0.08)
    put(TOTAL - 1.8, sfx_arr("impact"), 0.10)
    y = np.clip(y, -1, 1)
    with wave.open(str(path), "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype("<i2").tobytes())

def encode(path, size, wav):
    return subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{size[0]}x{size[1]}", "-r", str(FPS), "-i", "-", "-i", str(wav),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=9", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(path)], stdin=subprocess.PIPE)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "still":
        for a in sys.argv[2:]:
            t = float(a); full_frame(t).save(WK / f"still-{t:05.1f}.png"); vertical_frame(t).save(WK / f"vstill-{t:05.1f}.png")
    else:
        name = sys.argv[2] if len(sys.argv) > 2 else "video-engine-explainer"; OUT.mkdir(exist_ok=True)
        wav = WK / "mix.wav"; make_audio(wav)
        p1 = encode(OUT / f"{name}.mp4", (W, H), wav); p2 = encode(OUT / f"{name}-vertical.mp4", (1080, 1920), wav)
        n = int(TOTAL * FPS)
        for i in range(n):
            t = i / FPS; sc = scene_frame(t)
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            if t < NOCAP_END: draw_caption(ImageDraw.Draw(ov), t, W // 2, 925, 62, 1500)
            f = Image.alpha_composite(sc.convert("RGBA"), ov).convert("RGB")
            p1.stdin.write(f.tobytes()); p2.stdin.write(vertical_frame(t, sc).tobytes())
            if i % 300 == 0: print(i, n, flush=True)
        p1.stdin.close(); p2.stdin.close(); p1.wait(); p2.wait()
        full_frame(1.0).save(OUT / "poster.png") if False else None
        full_frame(63.6).save(OUT / "poster.png")

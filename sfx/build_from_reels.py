"""Cut the named effects out of the sound-effect reels into the sfx library.

Run with the edits venv:  edits/.venv/bin/python -I sfx/build_from_reels.py
The effect table (name, start, end in the source reel, category, tags) was read
by hand from the on-screen names of the reels and aligned to the audio, see README.md.
Each clip: 5 ms padding, 5 ms fades, gain to about -16 LUFS integrated (never above
-1 dBFS sample peak, so a click that would clip is left quieter and flagged), 48 kHz 24-bit WAV.
"""
import json, os, re, subprocess, sys, tempfile
import numpy as np, soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "..", "edits", "work", "reels-2026-10-13")
PRIMARY = {"reel": "2b7b86e46eaf4886a19f5c5a342a7d92.MP4", "dir": "2b7b86", "downloaded": "2026-10-13 22:12"}
DUPLICATE = {"reel": "aad7a9353ad8440f88e31cd76b65f48c.MP4", "downloaded": "2026-10-13 22:29"}
TARGET_LUFS, PEAK_CEIL_DB, PAD, FADE = -16.0, -1.0, 0.005, 0.005

# name, start, end, category dir, tags
EFFECTS = [
    ("8 Bit Talking", 0.00, 2.37, "ui", ["8-bit", "voice", "retro", "game", "chiptune"]),
    ("Old Flash", 2.57, 3.41, "other", ["flash", "camera-flash", "retro", "pop"]),
    ("Cinematic Woosh", 4.04, 6.36, "transitions/whoosh", ["whoosh", "cinematic", "transition", "swoosh", "tail"]),
    ("Night Vision", 6.60, 8.11, "other", ["night-vision", "power-up", "goggles", "scan"]),
    ("Nextel", 8.45, 8.86, "ui", ["nextel", "walkie-talkie", "chirp", "beep", "radio"]),
    ("Digital Text", 8.93, 9.50, "ui", ["digital", "text", "typing", "data", "chatter"]),
    ("Riser", 9.50, 13.25, "risers", ["riser", "build-up", "tension", "swell"]),
    ("Counter", 13.94, 14.79, "clicks-and-switches", ["counter", "ticker", "ticks", "count"]),
    ("Bicycle Chain", 14.96, 15.54, "other", ["bicycle", "chain", "mechanical", "foley"]),
    ("Camera Click", 16.18, 16.83, "clicks-and-switches", ["camera", "shutter", "click", "photo"]),
    ("Shine", 17.21, 17.83, "ui", ["shine", "sparkle", "glint", "highlight"]),
    ("Woosh", 18.49, 19.21, "transitions/whoosh", ["whoosh", "swoosh", "transition", "short"]),
    ("Outro Hit", 19.97, 21.23, "impacts", ["impact", "hit", "outro", "sting", "sub-boom", "end-card-sting", "unlabelled-in-reel"],
     "Not in the on-screen list. It is the end-card sting the reel wrapper adds (waveform correlation 0.9997 with the boom after the end card of the walkthrough reel 537fad), kept because it is a clean sub boom."),
]

def kebab(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def lufs(x, sr):
    n = int(np.ceil(4.0 * sr / len(x))) + 1
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "m.wav")
        sf.write(p, np.tile(x, (n, 1)), sr)
        r = subprocess.run(["ffmpeg", "-nostats", "-i", p, "-af", "ebur128", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r)
    return float(m[-1])

def main():
    src = os.path.join(WORK, PRIMARY["dir"], "audio.wav")
    if not os.path.exists(src):                      # copy the reel into WORK/<dir>/src.mp4 first (the raw reels are not in git)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(WORK, PRIMARY["dir"], "src.mp4"), "-vn", "-ar", "48000", src], check=True)
    x, sr = sf.read(src, always_2d=True)
    assert sr == 48000
    index = []
    for name, a, b, cat, tags, *note in EFFECTS:
        s0, s1 = max(0, int((a - PAD) * sr)), min(len(x), int((b + PAD) * sr))
        c = x[s0:s1].copy()
        f = int(FADE * sr)
        ramp = np.linspace(0, 1, f)[:, None]
        c[:f] *= ramp
        c[-f:] *= ramp[::-1]
        l0 = lufs(c, sr)
        gain_db = TARGET_LUFS - l0
        pk0 = 20 * np.log10(np.abs(c).max() + 1e-12)
        limited = pk0 + gain_db > PEAK_CEIL_DB
        if limited:
            gain_db = PEAK_CEIL_DB - pk0
        c *= 10 ** (gain_db / 20)
        l1, pk = lufs(c, sr), 20 * np.log10(np.abs(c).max() + 1e-12)
        fn = kebab(name) + ".wav"
        d = os.path.join(HERE, cat)
        os.makedirs(d, exist_ok=True)
        sf.write(os.path.join(d, fn), c, sr, subtype="PCM_24")
        index.append({
            "name": name, "id": kebab(name), "file": f"{cat}/{fn}", "category": cat,
            "duration": round(len(c) / sr, 3), "peak_dbfs": round(float(pk), 2), "lufs": round(l1, 2),
            "loudness_limited_by_peak": bool(limited), "sample_rate": sr, "channels": c.shape[1],
            "source_reel": PRIMARY["reel"], "source_duplicate_reel": DUPLICATE["reel"],
            "timestamp_in_source": [a, b], "tags": tags,
            "licence": "unknown, personal and internal use only until cleared",
            **({"note": note[0]} if note else {}),
        })
        print(f"{name:16s} {cat:20s} {len(c)/sr:5.2f}s peak {pk:6.2f} lufs {l1:6.2f} {'(peak-limited)' if limited else ''}")
    with open(os.path.join(HERE, "index.json"), "w") as fh:
        json.dump({"version": 1, "licence": "unknown, personal and internal use only until cleared",
                   "effects": index}, fh, indent=2)

if __name__ == "__main__":
    main()

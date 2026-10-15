"""Measure a reference reel instead of eyeballing it: frame sheets, scene cuts, Demucs stems, a word-timed transcript,
an audio map (loudness per stem + spectrograms with the cuts) and sound-effect events.

Usage:  python -I analyse_reference.py <ref.mp4> <outdir> [--lang en] [--skip-stems] [--skip-transcript]
Needs:  ffmpeg, numpy, matplotlib; demucs (pip install demucs, uses torch); faster-whisper.
Outputs in <outdir>: sheets/sheet_XX_YY.png (10 fps, 15x4 tiles = 6 s each), cuts.txt, stems/*.wav,
transcript.json, audio_map.png, fx_events.json. Read the sheets in order and write rules (see reference-study.md)."""
import argparse
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("outdir")
ap.add_argument("--lang", default="en")
ap.add_argument("--skip-stems", action="store_true")
ap.add_argument("--skip-transcript", action="store_true")
a = ap.parse_args()
V, O = Path(a.video), Path(a.outdir)
(O / "frames").mkdir(parents=True, exist_ok=True)
(O / "sheets").mkdir(exist_ok=True)


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


# frames + sheets (10 fps, 144x256 tiles; one sheet = 60 frames = 6 s)
run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(V), "-vf", "fps=10,scale=144:256", str(O / "frames" / "%04d.png")])
n = len(list((O / "frames").glob("*.png")))
for s in range(0, n, 60):
    run(["ffmpeg", "-y", "-loglevel", "error", "-start_number", "1", "-i", str(O / "frames" / "%04d.png"),
         "-vf", f"select='between(n\\,{s}\\,{s + 59})',tile=15x4", "-frames:v", "1",
         str(O / "sheets" / f"sheet_{s // 10:02d}_{(s + 60) // 10:02d}.png")])

# scene cuts
info = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(V), "-vf", "select='gt(scene,0.25)',showinfo", "-an", "-f", "null", "-"],
                      capture_output=True, text=True).stderr
cuts = [float(x.split(":")[1]) for x in info.split() if x.startswith("pts_time:")]
(O / "cuts.txt").write_text("\n".join(f"{c:.3f}" for c in cuts))

# audio
run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(V), "-vn", "-ac", "2", "-ar", "44100", str(O / "audio.wav")])
run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(V), "-vn", "-ac", "1", "-ar", "16000", str(O / "audio16k.wav")])

if not a.skip_transcript:
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(str(O / "audio16k.wav"), word_timestamps=True, language=a.lang)
    tr = [{"t0": round(s.start, 2), "t1": round(s.end, 2), "text": s.text.strip(),
           "words": [[round(w.start, 2), round(w.end, 2), w.word] for w in (s.words or [])]} for s in segs]
    (O / "transcript.json").write_text(json.dumps(tr, ensure_ascii=False, indent=1), encoding="utf-8")

stem_dir = O / "stems" / "htdemucs" / "audio"
if not a.skip_stems:
    run([sys.executable, "-m", "demucs", "-n", "htdemucs", "-o", str(O / "stems"), str(O / "audio.wav")])


def load(p):
    with wave.open(str(p)) as w:
        sr, sw, ch = w.getframerate(), w.getsampwidth(), w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2" if sw == 2 else "<i4").astype(float)
    return x.reshape(-1, ch).mean(1) / (32768 if sw == 2 else 2 ** 31), sr


if stem_dir.exists():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    stems = {k: load(stem_dir / f"{k}.wav") for k in ("vocals", "drums", "bass", "other")}
    sr = stems["vocals"][1]
    hop = sr // 100

    def rms(x):
        m = len(x) // hop
        return np.sqrt((x[: m * hop].reshape(m, hop) ** 2).mean(1) + 1e-12)

    env = {k: 20 * np.log10(rms(v[0])) for k, v in stems.items()}
    t = np.arange(len(env["vocals"])) / 100
    fx = stems["drums"][0] + stems["other"][0]
    e = rms(fx)
    de = np.diff(20 * np.log10(e + 1e-9), prepend=-120)
    events, i = [], 0
    while i < len(e):
        if de[i] > 9 and 20 * np.log10(e[i]) > -38:
            j, peak = i, e[i]
            while j < len(e) - 1 and 20 * np.log10(e[j] + 1e-9) > 20 * np.log10(peak) - 18:
                peak = max(peak, e[j]); j += 1
            seg = fx[i * hop: max(j, i + 5) * hop]
            nfft = 2048
            frames = [seg[k:k + nfft] for k in range(0, max(1, len(seg) - nfft), nfft // 2)] or [np.pad(seg, (0, nfft - len(seg)))]
            cents = []
            for fr in frames:
                sp = np.abs(np.fft.rfft(fr * np.hanning(len(fr)), nfft))
                cents.append(float((sp * np.fft.rfftfreq(nfft, 1 / sr)).sum() / (sp.sum() + 1e-9)))
            kind = "rising" if cents[-1] > cents[0] * 1.4 else "falling" if cents[-1] < cents[0] / 1.4 else "flat"
            events.append({"t": round(i / 100, 2), "dur": round((j - i) / 100, 2), "peak_db": round(20 * np.log10(peak), 1), "pitch": kind})
            i = j + 5
        else:
            i += 1
    (O / "fx_events.json").write_text(json.dumps(events, indent=1))
    fig, ax = plt.subplots(3, 1, figsize=(26, 12), sharex=True)
    for k, c in (("vocals", "tab:blue"), ("drums", "tab:red"), ("bass", "tab:green"), ("other", "tab:orange")):
        ax[0].plot(t, env[k], lw=0.8, label=k, color=c)
    ax[0].set_ylim(-70, 0); ax[0].legend(loc="upper right"); ax[0].set_ylabel("dB")
    ax[1].specgram(fx, NFFT=1024, Fs=sr, noverlap=768, cmap="magma", vmin=-120); ax[1].set_ylim(0, 12000); ax[1].set_ylabel("drums+other Hz")
    ax[2].specgram(stems["vocals"][0], NFFT=1024, Fs=sr, noverlap=768, cmap="viridis", vmin=-120); ax[2].set_ylim(0, 6000); ax[2].set_ylabel("vocals Hz")
    for axx in ax:
        for c in cuts:
            axx.axvline(c, color="k" if axx is ax[0] else "white", lw=0.5, alpha=0.6)
    ax[2].set_xticks(np.arange(0, t[-1] + 1, 1))
    plt.tight_layout(); plt.savefig(O / "audio_map.png", dpi=60)
print(f"{n} frames, {len(cuts)} cuts -> {O}")

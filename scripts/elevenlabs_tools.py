"""ElevenLabs helpers for video work: voiceover with word timings, music from a composition plan, sound effects.
The key comes from ELEVENLABS_API_KEY (env, or the Windows user variable) and is never printed.

  tts   <script.json> <out.mp3> <out_words.json> --voice "<your voice name>" [--speed 1.12] [--model eleven_v4]
        script.json: [{"id": "hook", "text": "First sentence of your script."}, ...]  (one call, whole script)
        out_words.json: {"total": s, "segments": [{"id", "text", "t0", "t1", "words": [[word, t0, t1], ...]}]}
  music <plan.json> <out.mp3>
        plan.json: {"positive_global_styles": [...], "negative_global_styles": [...],
                    "sections": [{"section_name", "positive_local_styles", "negative_local_styles", "duration_ms" (>=3000), "lines": []}]}
        or {"prompt": "...", "music_length_ms": 6500} for a short cue.
  sfx   <out.mp3> "<prompt>" <seconds> [--influence 0.6]

Account limit: 2-4 concurrent requests (HTTP 429 otherwise). The music model ignores "silent" sections (make the
hush in the mix) and rejects prompts naming real studios/artists."""
import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.elevenlabs.io/v1"


def key():
    k = os.environ.get("ELEVENLABS_API_KEY")
    if not k and os.name == "nt":
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as h:
            k = winreg.QueryValueEx(h, "ELEVENLABS_API_KEY")[0]
    if not k:
        sys.exit("ELEVENLABS_API_KEY is not set")
    return k.strip()


def call(path, payload=None, raw=False):
    req = urllib.request.Request(API + path, data=None if payload is None else json.dumps(payload).encode("utf-8"),
                                 headers={"xi-api-key": key(), "Content-Type": "application/json"},
                                 method="GET" if payload is None else "POST")
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            body = r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:400]}")
    return body if raw else json.loads(body)


def tts(a):
    script = json.loads(Path(a.script).read_text(encoding="utf-8"))
    voices = call("/voices")["voices"]
    hit = [v for v in voices if v["name"].lower() == a.voice.lower()]
    if not hit:
        sys.exit(f"voice {a.voice!r} not found")
    vid = hit[0]["voice_id"]
    settings = call(f"/voices/{vid}/settings")
    settings["speed"] = a.speed
    text = " ".join(s["text"] for s in script)
    res = call(f"/text-to-speech/{vid}/with-timestamps?output_format=mp3_44100_128", {"text": text, "model_id": a.model, "voice_settings": settings})
    Path(a.out_mp3).write_bytes(base64.b64decode(res["audio_base64"]))
    al = res.get("alignment") or res.get("normalized_alignment")
    chars, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    words = [{"w": m.group(), "t0": round(st[m.start()], 3), "t1": round(en[m.end() - 1], 3), "c": m.start()} for m in re.finditer(r"\S+", "".join(chars))]
    segs, pos = [], 0
    for s in script:
        b = pos + len(s["text"])
        ws = [w for w in words if pos <= w["c"] < b]
        segs.append({"id": s["id"], "text": s["text"], "t0": ws[0]["t0"], "t1": ws[-1]["t1"], "words": [[w["w"], w["t0"], w["t1"]] for w in ws]})
        pos = b + 1
    Path(a.out_words).write_text(json.dumps({"model": a.model, "total": round(en[-1], 3), "segments": segs}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{round(en[-1], 1)} s, {len(words)} words")


def music(a):
    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    body = {"model_id": "music_v1", **({"composition_plan": plan} if "sections" in plan else plan)}
    Path(a.out).write_bytes(call("/music?output_format=mp3_44100_192", body, raw=True))
    print("wrote", a.out)


def sfx(a):
    body = {"text": a.prompt, "duration_seconds": float(a.seconds), "prompt_influence": a.influence}
    Path(a.out).write_bytes(call("/sound-generation?output_format=mp3_44100_192", body, raw=True))
    print("wrote", a.out)


ap = argparse.ArgumentParser()
sub = ap.add_subparsers(dest="cmd", required=True)
p = sub.add_parser("tts"); p.add_argument("script"); p.add_argument("out_mp3"); p.add_argument("out_words")
p.add_argument("--voice", required=True, help="voice name as shown in your ElevenLabs library"); p.add_argument("--speed", type=float, default=1.12); p.add_argument("--model", default="eleven_v4")
p = sub.add_parser("music"); p.add_argument("plan"); p.add_argument("out")
p = sub.add_parser("sfx"); p.add_argument("out"); p.add_argument("prompt"); p.add_argument("seconds"); p.add_argument("--influence", type=float, default=0.6)
a = ap.parse_args()
{"tts": tts, "music": music, "sfx": sfx}[a.cmd](a)

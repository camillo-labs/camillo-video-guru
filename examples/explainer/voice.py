"""One ElevenLabs take per script line, Cam's clone Cameron (cloned), eleven_multilingual_v2. Key from the env file, never printed."""
import os, re, json, subprocess, requests, pathlib
env = pathlib.Path("/Users/student/life tracker/_meta/secrets.elevenlabs.env").read_text()
key = re.search(r"ELEVENLABS_API_KEY=(\S+)", env).group(1).strip("'\"")
H = pathlib.Path(__file__).parent / "work"
VOICE = "p9vxMEBtGJYCWqpHpTwy"
lines = [re.sub(r"^\d+\.\s*", "", l).strip() for l in open(H.parent / "script.md") if re.match(r"^\d+\.", l)]
json.dump(lines, open(H / "lines.json", "w"), indent=1)
for i, t in enumerate(lines, 1):
    mp3 = H / f"line{i:02d}.mp3"
    if mp3.exists(): continue
    r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128",
        headers={"xi-api-key": key}, json={"text": t, "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}, timeout=120)
    r.raise_for_status(); mp3.write_bytes(r.content); print(i, len(r.content))

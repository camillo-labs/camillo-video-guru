"""Word timestamps with the local Whisper model. Run with the lt-voice venv:
~/.local/share/lt-voice/venv312/bin/python transcribe.py in.wav out.json
Writes [{"text","t0","t1"}]. make_edit.py calls this for --transcribe and --voiceover when no captions are given."""
import json, sys
from mlx_audio.stt.utils import load_model
m = load_model("mlx-community/whisper-large-v3-turbo-asr-4bit")
r = m.generate(sys.argv[1], word_timestamps=True)
words = []
for s in getattr(r, 'segments', []):
    for w in s.get('words', []) or []:
        words.append({'text': w.get('word', '').strip(), 't0': float(w.get('start', 0)), 't1': float(w.get('end', 0)), 'segment_start': float(s.get('start', 0))})
json.dump(words, open(sys.argv[2], 'w'))
print(len(words), 'words')

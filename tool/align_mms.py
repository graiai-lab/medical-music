"""Forced alignment of OUR lyric words to a vocal recording with torchaudio MMS_FA.

    venv/bin/python tool/align_mms.py audio/cardiac_vocals.wav lyrics/cardiac.md align/cardiac_mms.json

Why this aligner: we already know the words, so this is forced alignment,
not transcription. MMS_FA is a character-level CTC aligner (wav2vec2, MMS)
with no pronunciation dictionary, so drug names and phonetic respellings
like "blee-oh-MY-sin" are aligned as spelled instead of failing as
out-of-vocabulary. Read whole from the torchaudio 2.8.0 tutorial
"Forced alignment for multilingual data" on 2026-09-17: bundle.get_model /
get_tokenizer / get_aligner; token_spans = aligner(emission[0],
tokenizer(words)); seconds = frame * waveform.size(1) / emission.size(1) /
sample_rate; audio must be at bundle.sample_rate (16 kHz). The bundle's
dictionary, printed from the venv, is a-z, apostrophe, '-' as blank and
'*' as the unknown token, so words are lowered and stripped to a-z and
apostrophe before tokenising.

Output shape is what video/scenes/verse_annotate.py reads:
{"words": [{"word", "start", "end", "line", "score"}]}. Written per word
with flush. "score" is the span's mean CTC confidence; low scores mark the
words Suno mangled or the aligner could not place.
"""
import json
import re
import sys
from pathlib import Path

import torch
import torchaudio
from torchaudio.pipelines import MMS_FA as bundle

audio_path, lyric_path, out_path = map(Path, sys.argv[1:4])
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"device={device}", flush=True)

# lyric lines: non-blank lines after a "[Verse N]" tag up to the next blank
lines, verse_idx, in_verse = [], -1, False
for raw in lyric_path.read_text().splitlines():
    s = raw.strip()
    if s.startswith("[Verse"):
        verse_idx += 1; in_verse = True; continue
    if not s:
        in_verse = False; continue
    if in_verse:
        lines.append(s)
words = [{"word": w, "line": li} for li, l in enumerate(lines) for w in l.split()]
print(f"{len(lines)} lines, {len(words)} words, {verse_idx + 1} verses", flush=True)


def norm(w):
    """Lower-case and keep only the bundle's characters (prose: case-insensitive)."""
    t = re.sub(r"[^a-z']", "", w.lower())
    return t or "*"  # a word with no alignable characters becomes the unknown token


transcript = [norm(w["word"]) for w in words]

waveform, sr = torchaudio.load(str(audio_path))
if waveform.size(0) > 1:
    waveform = waveform.mean(0, keepdim=True)
if sr != bundle.sample_rate:
    waveform = torchaudio.functional.resample(waveform, sr, bundle.sample_rate)
    sr = bundle.sample_rate
print(f"audio {waveform.size(1) / sr:.1f}s at {sr} Hz", flush=True)

model = bundle.get_model().to(device)
tokenizer = bundle.get_tokenizer()
aligner = bundle.get_aligner()
with torch.inference_mode():
    emission, _ = model(waveform.to(device))
    token_spans = aligner(emission[0], tokenizer(transcript))
ratio = waveform.size(1) / emission.size(1) / sr
print(f"{emission.size(1)} frames, {ratio * 1000:.1f} ms per frame", flush=True)

out_path.parent.mkdir(parents=True, exist_ok=True)
fh = open(out_path, "w")
fh.write('{"source": "torchaudio MMS_FA forced alignment of %s to %s", "words": [\n'
         % (lyric_path.name, audio_path.name))
n = len(words)
for i, (w, spans) in enumerate(zip(words, token_spans)):
    score = sum(s.score * len(s) for s in spans) / sum(len(s) for s in spans)
    rec = {"word": w["word"], "line": w["line"], "start": round(spans[0].start * ratio, 3),
           "end": round(spans[-1].end * ratio, 3), "score": round(float(score), 3)}
    fh.write(json.dumps(rec) + (",\n" if i < n - 1 else "\n")); fh.flush()
    if score < 0.5:
        print(f"  low confidence line {w['line']}: {w['word']!r} score {score:.2f}", flush=True)
fh.write("]}\n"); fh.close()
print(f"wrote {out_path}", flush=True)

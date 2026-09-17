"""Word-level forced alignment of a Suno vocal against the lyrics we wrote.

    venv/bin/python tool/align.py audio/cardiac_vocals.mp3 lyrics/cardiac.md align/cardiac.json

Transcribes with WhisperX, then aligns. The lyric file is the ground truth we
compare against, so the output records BOTH what Whisper heard and which
lyric word it was matched to; mismatches are the Suno mispronunciations
worth fixing (see SUNO-NOTES.md). Output is the shape verse_annotate.py
reads: {"words": [{"word", "start", "end", "line"}]}, where "word" is OUR
lyric word and "heard" is Whisper's.

Writes incrementally: the transcript segment list lands on disk before the
alignment starts, and each verse's matched words are flushed as matched.
"""
import difflib
import json
import re
import sys
from pathlib import Path

import whisperx

audio_path, lyric_path, out_path = map(Path, sys.argv[1:4])
device = "cuda" if whisperx.torch.cuda.is_available() else "cpu"  # type: ignore[attr-defined]
compute = "float16" if device == "cuda" else "int8"
print(f"device={device}", flush=True)

# 1. lyric lines: the non-blank lines that follow a "[Verse N]" tag up to
#    the next blank line. Everything else in the file is notes.
lines, verse_idx, in_verse = [], -1, False
for raw in lyric_path.read_text().splitlines():
    s = raw.strip()
    if s.startswith("[Verse"):
        verse_idx += 1; in_verse = True; continue
    if not s:
        in_verse = False; continue
    if in_verse:
        lines.append({"verse": verse_idx, "text": s})
print(f"{len(lines)} lyric lines across {verse_idx + 1} verses", flush=True)

# 2. transcribe + align
model = whisperx.load_model("large-v3", device, compute_type=compute, language="en")
audio = whisperx.load_audio(str(audio_path))
result = model.transcribe(audio, batch_size=8)
out_path.parent.mkdir(parents=True, exist_ok=True)
raw_path = out_path.with_suffix(".whisperx_raw.json")
raw_path.write_text(json.dumps(result, indent=1))
print(f"transcript saved: {raw_path}", flush=True)
align_model, meta = whisperx.load_align_model(language_code="en", device=device)
result = whisperx.align(result["segments"], align_model, meta, audio, device, return_char_alignments=False)
raw_path.write_text(json.dumps(result, indent=1))
heard = [w for seg in result["segments"] for w in seg.get("words", []) if "start" in w]
print(f"{len(heard)} timed words heard", flush=True)

# 3. match our lyric words to heard words in order (SequenceMatcher on
#    normalised tokens), so every lyric word gets a time even where Suno
#    mangled it. Case-insensitive normalisation on purpose: prose.
def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())
ours = [{"word": w, "line": li} for li, l in enumerate(lines) for w in l["text"].split()]
sm = difflib.SequenceMatcher(None, [norm(w["word"]) for w in ours], [norm(h["word"]) for h in heard], autojunk=False)
matched = {}
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        for k in range(i2 - i1):
            matched[i1 + k] = heard[j1 + k]
    elif tag == "replace" and (i2 - i1) == (j2 - j1):
        for k in range(i2 - i1):  # same count: positional, flagged as mismatch
            matched[i1 + k] = dict(heard[j1 + k], mismatch=True)
# unmatched lyric words: spread evenly across the gap between the nearest
# matched neighbours, so every word has a time and the scene never stalls.
n = len(ours)
times = [None] * n
for i in range(n):
    if i in matched:
        times[i] = (matched[i]["start"], matched[i]["end"])
i = 0
while i < n:
    if times[i] is not None:
        i += 1; continue
    j = i
    while j < n and times[j] is None:
        j += 1
    lo = times[i - 1][1] if i > 0 else 0.0
    hi = times[j][0] if j < n else lo + 0.4 * (j - i)
    step = (hi - lo) / (j - i)
    for k in range(i, j):
        times[k] = (lo + (k - i) * step, lo + (k - i + 1) * step)
    i = j
words, fh = [], open(out_path, "w")
fh.write('{"source": "whisperx large-v3 on %s", "words": [\n' % audio_path.name)
for i, w in enumerate(ours):
    h = matched.get(i, {})
    rec = {"word": w["word"], "line": w["line"], "start": round(times[i][0], 3),
           "end": round(times[i][1], 3), "heard": h.get("word")}
    if h.get("mismatch"): rec["mismatch"] = True
    if not h: rec["interpolated"] = True
    words.append(rec)
    fh.write(json.dumps(rec) + (",\n" if i < n - 1 else "\n")); fh.flush()
fh.write("]}\n"); fh.close()
mm = [w for w in words if w.get("mismatch") or w.get("interpolated")]
print(f"wrote {out_path}: {len(words)} words, {len(mm)} not heard as written:", flush=True)
for w in mm:
    print(f"  line {w['line']}: wrote {w['word']!r}, heard {w['heard']!r}", flush=True)

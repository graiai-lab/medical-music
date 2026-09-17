"""Compare word-level alignments of the same lyric: scores and onset deltas.

    venv/bin/python tool/compare_alignments.py align/lungs_mix_mms.json align/lungs_vocals_mms.json [align/lungs_vocals_whisperx.json]

Prints per-file score summaries and, for each pair, the median/mean/max
absolute onset difference and the words that differ by more than 150 ms.
Word lists must come from the same lyric file (same length, same order).
"""
import json
import statistics as st
import sys


def load(p):
    return json.load(open(p))["words"]


def summary(name, words):
    sc = [w.get("score") for w in words if w.get("score") is not None]
    line = f"{name}: n={len(words)} span={words[0]['start']:.1f}-{words[-1]['end']:.1f}s"
    if sc:
        line += f" score mean={st.mean(sc):.3f} median={st.median(sc):.3f} frac<0.5={sum(x < 0.5 for x in sc) / len(sc):.2f}"
    mono = all(words[i]["start"] <= words[i + 1]["start"] for i in range(len(words) - 1))
    print(line + f" monotonic={mono}", flush=True)


files = sys.argv[1:]
sets = [(f, load(f)) for f in files]
for f, w in sets:
    summary(f, w)
for i in range(len(sets)):
    for j in range(i + 1, len(sets)):
        fa, a = sets[i]; fb, b = sets[j]
        n = min(len(a), len(b))
        if len(a) != len(b):
            print(f"  word count differs: {len(a)} vs {len(b)}", flush=True)
        pairs = [(a[k], b[k]) for k in range(n) if not b[k].get("interpolated") and not a[k].get("interpolated")]
        d = [abs(x["start"] - y["start"]) for x, y in pairs]
        print(f"{fa} vs {fb}: n={len(d)} median|d|={st.median(d) * 1000:.0f} ms mean={st.mean(d) * 1000:.0f} ms max={max(d) * 1000:.0f} ms", flush=True)
        big = [(x["line"], x["word"], round(x["start"], 2), round(y["start"], 2)) for x, y in pairs if abs(x["start"] - y["start"]) > 0.15]
        print(f"  >150 ms apart: {len(big)}", big[:15], "..." if len(big) > 15 else "", flush=True)

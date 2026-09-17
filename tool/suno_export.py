"""Write paste-ready Suno inputs from each lyrics/*.md.

    python3 tool/suno_export.py

For every lyrics/<song>.md this writes:
  lyrics/suno/<song>.lyrics.txt  the [Verse N] blocks and [End], nothing else
  lyrics/suno/<song>.style.txt   the indented style paragraph, one line
Paste the first into Suno's Lyrics box and the second into Style. The md
stays the record (title, status, OE state); these two files are the input.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "lyrics" / "suno"
OUT.mkdir(exist_ok=True)

for md in sorted((ROOT / "lyrics").glob("*.md")):
    text = md.read_text().splitlines()
    verses, style, in_verse, in_style = [], [], False, False
    for raw in text:
        s = raw.rstrip()
        if s.startswith("Style:"):
            in_style = True; continue
        if in_style:
            if s.startswith("    "):
                style.append(s.strip()); continue
            if s.strip() == "" and not style:
                continue
            in_style = False
        if s.startswith("[Verse") or s.startswith("[Chorus"):
            in_verse = True; verses.append(s.strip()); continue
        if in_verse:
            if s.strip() == "":
                in_verse = False; verses.append("")
            else:
                verses.append(s.strip())
    if not verses:
        continue
    while verses and verses[-1] == "":
        verses.pop()
    verses.append(""); verses.append("[End]")
    (OUT / f"{md.stem}.lyrics.txt").write_text("\n".join(verses) + "\n")
    (OUT / f"{md.stem}.style.txt").write_text(" ".join(style) + "\n")
    print(f"{md.stem}: {sum(1 for v in verses if v.startswith('[Verse'))} verses, style {len(' '.join(style))} chars", flush=True)

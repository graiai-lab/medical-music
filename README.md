# medical-music

Songs to remember medicine by. Lyrics are written here, rendered with Suno,
then cut into annotated videos.

## Layout

| dir | holds |
|---|---|
| `lyrics/` | one markdown file per song: lyrics, the facts each line encodes, OpenEvidence check status |
| `audio/` | Suno renders (`<song>.mp3`) |
| `align/` | word-level timestamps from forced alignment of each render |
| `video/` | Manim scenes and rendered clips; `video/cutaways/` for sourced images with licence noted |

## Lyric rules

Strophic (same melody every verse). Tight end-rhyme. Fixed syllable count per
line. Word stress on the downbeat. Core list in the chorus, elaboration in the
verses. Slow tempo, no melisma, no syncopation. Concrete, imageable words.

## Pipeline

lyrics → Suno → forced alignment (word timestamps) → Manim lyric annotation +
sourced cutaways → composite (ffmpeg / DaVinci Resolve)

## Video: lyric annotation scene

```
source venv/bin/activate.fish
ALIGN=align/cardiac_v1_synthetic.json ANNOT=video/scenes/cardiac_v1.json \
  manim -ql video/scenes/verse_annotate.py VerseAnnotate      # -qh for 1080p
```

`ALIGN` is word-level timestamps (WhisperX shape). `align/*_synthetic.json`
is a 140 BPM one-syllable-per-beat grid used only until the Suno vocal is
aligned; it is not a measurement of the recording. `ANNOT` lists what to
draw on which word: `circle`, `underline`, or `note` with text.
Renders land in `media/` (gitignored); keep any you want in `video/renders/`
(also gitignored, they are regenerable).

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

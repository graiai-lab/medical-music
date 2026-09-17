"""Manim scene: lyric annotation for one verse, driven by word timestamps.

Usage:
    ALIGN=align/cardiac_v1_synthetic.json ANNOT=video/scenes/cardiac_v1.json \
        manim -ql video/scenes/verse_annotate.py VerseAnnotate

ALIGN: {"words": [{"word", "start", "end", "line"}, ...]} — word-level
timestamps from forced alignment (WhisperX shape) of the Suno vocal.
ANNOT: [{"at": "<word>", "do": "circle|underline|note", "text": "..."}]
— what to draw when that word is sung. Words matched case-insensitively,
first unconsumed occurrence.

Each line is ONE Text mobject (so the baseline is shared) and words are
revealed as slices of its glyphs. Notes go in a right-hand margin column
with an arrow to the word, so they never collide with the lyric lines.
"""
import json
import os

from manim import (BLUE, DOWN, LEFT, RIGHT, UP, WHITE, YELLOW, Arrow, Create,
                   Ellipse, FadeIn, Scene, Text, Underline, VGroup, Write,
                   config)

config.background_color = "#101418"
LYRIC_SIZE = 40
NOTE_SIZE = 26


def load(path, default):
    return json.load(open(path)) if path and os.path.exists(path) else default


def word_slices(text_mob, words):
    """Map each word to the VGroup of its glyphs inside a single Text.

    Measured 2026-09-17 (manim 0.21): with disable_ligatures=True a Text has
    one submobject per CHARACTER, spaces included (37 for a 37-char line);
    with ligatures on it drops spaces and merges "fi"/"fl". We render with
    ligatures off, so advance by len(word) + 1 for the space.
    """
    out, i = [], 0
    for w in words:
        n = len(w["word"])
        out.append(VGroup(*text_mob[i:i + n]))
        i += n + 1
    return out


class VerseAnnotate(Scene):
    def construct(self):
        align = load(os.environ.get("ALIGN"), {"words": []})
        annots = load(os.environ.get("ANNOT"), [])
        lines = {}
        for w in align["words"]:
            lines.setdefault(w["line"], []).append(w)

        rows = VGroup()
        sung = []  # (word dict, glyph group)
        for li in sorted(lines):
            row = Text(" ".join(w["word"] for w in lines[li]), font_size=LYRIC_SIZE, color=WHITE,
                       disable_ligatures=True)  # "fi"/"fl" ligatures break glyph indexing
            rows.add(row)
            sung.extend(zip(lines[li], word_slices(row, lines[li])))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.55).to_edge(LEFT, buff=0.7).to_edge(UP, buff=0.8)

        margin_x = config.frame_width / 2 - 0.6   # right edge for notes
        used_note_ys = []

        pending = list(annots)
        clock = 0.0
        for w, glyphs in sung:
            gap = w["start"] - clock
            if gap > 0:
                self.wait(gap)
                clock = w["start"]
            t = min(max(0.15, w["end"] - w["start"]), 0.3)
            self.play(FadeIn(glyphs, shift=UP * 0.08), run_time=t)
            clock += t
            key = w["word"].lower().strip(",.—")
            hit = next((a for a in pending if a["at"].lower().strip(",.—") == key), None)
            if hit:
                pending.remove(hit)
                dt = self._annotate(hit, glyphs, margin_x, used_note_ys)
                clock += dt
        if pending:
            print("UNMATCHED ANNOTATIONS:", [a["at"] for a in pending], flush=True)
        self.wait(1.5)

    def _annotate(self, a, glyphs, margin_x, used_ys):
        kind = a["do"]
        if kind == "circle":
            ring = Ellipse(width=glyphs.width + 0.35, height=glyphs.height + 0.45,
                           color=YELLOW, stroke_width=3).move_to(glyphs)
            self.play(Create(ring), run_time=0.5)
            return 0.5
        if kind == "underline":
            self.play(Create(Underline(glyphs, color=YELLOW, buff=0.08)), run_time=0.4)
            return 0.4
        if kind == "note":
            # Note sits in the right margin in the GAP above the word's line,
            # so the arrow runs through the gap and lands on the word's top
            # right corner without striking through the rest of the line.
            y = glyphs.get_top()[1] + 0.3
            while any(abs(y - u) < 0.4 for u in used_ys):
                y -= 0.4
            used_ys.append(y)
            note = Text(a["text"], font_size=NOTE_SIZE, color=BLUE)
            note.move_to([margin_x - note.width / 2, y, 0])
            tip = glyphs.get_corner(UP + RIGHT) + [0.05, 0.02, 0]
            arr = Arrow(note.get_left(), tip, buff=0.1, color=BLUE, stroke_width=3,
                        max_tip_length_to_length_ratio=0.1)
            self.play(Write(note), Create(arr), run_time=0.7)
            return 0.7
        return 0.0

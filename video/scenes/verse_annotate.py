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

from manim import (BLUE, DOWN, LEFT, RIGHT, UP, WHITE, YELLOW, AnimationGroup, Arrow, Create,
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
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.55)
        # Fit the verse in the frame: eight common-meter lines at 40pt with
        # note gaps overflow 480p/1080p alike, so scale to leave 0.6 margins.
        max_h = config.frame_height - 1.2
        if rows.height > max_h:
            rows.scale(max_h / rows.height)
        rows.to_edge(LEFT, buff=0.7).to_edge(UP, buff=0.6)

        margin_x = config.frame_width / 2 - 0.6   # right edge for notes
        used_note_ys = []

        # Time-locked schedule: every word's reveal STARTS at its aligned
        # start, and the reveal plus any annotation on it fits inside the
        # gap before the next word, so the scene can never drift behind the
        # audio. (The first version ran annotations serially and drifted
        # about a second per verse; caught by frame-checking "echo".)
        # Measured 2026-09-17: Manim rounds every play() and wait() UP to
        # whole frames, so a private clock drifted 1.58 s behind the audio
        # over 44 words at 15 fps. The clock is therefore the renderer's own
        # time, re-read before every word, so rounding never accumulates.
        pending = list(annots)
        frame = 1 / config.frame_rate
        starts = [w["start"] for w, _ in sung]
        for idx, (w, glyphs) in enumerate(sung):
            clock = self.renderer.time
            gap = w["start"] - clock
            if gap >= frame:
                self.wait(gap)
                clock = self.renderer.time
            nxt = starts[idx + 1] if idx + 1 < len(starts) else w["end"] + 0.6
            budget = max(frame, min(0.35, nxt - clock))
            anims = [FadeIn(glyphs, shift=UP * 0.08)]
            key = w["word"].lower().strip(",.—")
            hit = next((a for a in pending if a["at"].lower().strip(",.—") == key), None)
            if hit:
                pending.remove(hit)
                anims.append(self._annotation(hit, glyphs, margin_x, used_note_ys))
            if os.environ.get("TIMING_LOG"):
                with open(os.environ["TIMING_LOG"], "a") as fh:
                    fh.write(f'{w["word"]}\t{w["start"]:.3f}\t{clock:.3f}\t{self.renderer.time:.3f}\t{budget:.3f}\n'); fh.flush()
            self.play(*anims, run_time=budget)
        if pending:
            print("UNMATCHED ANNOTATIONS:", [a["at"] for a in pending], flush=True)
        self.wait(1.5)

    def _annotation(self, a, glyphs, margin_x, used_ys):
        """Build the annotation animation for one word (played with its reveal)."""
        kind = a["do"]
        if kind == "circle":
            ring = Ellipse(width=glyphs.width + 0.35, height=glyphs.height + 0.45,
                           color=YELLOW, stroke_width=3).move_to(glyphs)
            return Create(ring)
        if kind == "underline":
            return Create(Underline(glyphs, color=YELLOW, buff=0.08))
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
            return AnimationGroup(Write(note), Create(arr))
        raise ValueError(f"unknown annotation kind {kind!r}")

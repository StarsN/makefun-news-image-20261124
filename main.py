#!/usr/bin/env python3
"""THE OTTER TIMES - Tuesday, 24 November 2026.

A one-page newspaper front page, drawn entirely at runtime with the
Python 3 standard library.  No images, no network access, no files read
at runtime.  The program builds a 1024x1024 RGB picture in memory --
paper, rules, a hand-drawn masthead, headlines, small hand-drawn
pictures for each story -- and writes it out as a PNG.

Everything here is written from scratch for this page: the bitmap font
below is my own 5-wide, 8-tall design, and the PNG writer is my own
minimal encoder (signature, IHDR, one IDAT, IEND).

Output: $MAKEFUN_OUTPUT_DIR/entry.png (default: out/entry.png).
The output is deterministic: the same input always produces the same
bytes, so two runs give byte-identical files.
"""

import hashlib
import math
import os
import struct
import sys
import zlib

WIDTH = 1024
HEIGHT = 1024

# Palette: (red, green, blue).
PAPER = (248, 244, 233)       # warm newsprint
INK = (22, 22, 22)            # near-black text and rules
GREY = (112, 110, 102)        # captions and secondary text
LIGHT = (232, 228, 218)       # light panel background
SKY = (178, 208, 224)         # light blue sky in pictures
RED = (168, 44, 36)           # accent red
BLUE = (38, 84, 138)          # deep blue
DARK_BLUE = (30, 60, 96)      # chip body
GREEN = (34, 120, 62)         # rising market green
ORANGE = (204, 110, 28)       # flame and sun
WHITE = (255, 255, 255)
MID_GREY = (150, 148, 138)

# ---------------------------------------------------------------------------
# Bitmap font.
#
# My own design: every glyph is 5 pixels wide and 8 rows tall, drawn on a
# grid where "#" is ink and "." is empty.  Capitals and digits use rows
# 0-6; lower-case letters sit on rows 2-6, with descenders (g, j, p, q,
# y and the comma) dropping into row 7.  Characters advance 6 pixels
# (5 for the glyph plus 1 of space) times the scale factor.
# ---------------------------------------------------------------------------

FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#", "....."),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####.", "....."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####", "....."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####.", "....."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####", "....."),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#....", "....."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###.", "....."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#", "....."),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####", "....."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##..", "....."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#", "....."),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####", "....."),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#", "....."),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#", "....."),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###.", "....."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#....", "....."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#", "....."),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#", "....."),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####.", "....."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "....."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###.", "....."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#..", "....."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#", "....."),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#", "....."),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#..", "....."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####", "....."),
    "a": (".....", ".....", ".###.", "....#", ".####", "#...#", ".####", "....."),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####.", "....."),
    "c": (".....", ".....", ".####", "#....", "#....", "#....", ".####", "....."),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####", "....."),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###.", "....."),
    "f": ("..##.", ".#...", ".#...", "####.", ".#...", ".#...", ".#...", "....."),
    "g": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#", "....."),
    "i": ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###.", "....."),
    "j": ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", "...#.", ".##.."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "....."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###.", "....."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#", "....."),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#", "....."),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###.", "....."),
    "p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#....", "#...."),
    "q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#....", "....."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####.", "....."),
    "t": (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##.", "....."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#...#", ".####", "....."),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#..", "....."),
    "w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "##.##", "#...#", "....."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "....."),
    "y": (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#", ".###."),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####", "....."),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###.", "....."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###.", "....."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####", "....."),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####.", "....."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#.", "....."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###.", "....."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###.", "....."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#..", "....."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###.", "....."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###.", "....."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".....", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#...", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#..", "....."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#..", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#.", "....."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#...", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#....", "....."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#..", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#", "....."),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", ".....", "....."),
    "=": (".....", ".....", ".###.", ".....", ".###.", ".....", ".....", "....."),
    "*": (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", ".....", "....."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#.", "....."),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###.", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####", "....."),
    "|": ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "....."),
}

# Characters the text asked for that the font does not have, collected
# while drawing so a missing glyph is reported instead of silently lost.
MISSING = set()

# The font table must be exactly 8 rows of 5 cells each; fail loudly
# here rather than drawing a broken page.
for _ch, _rows in FONT.items():
    assert len(_rows) == 8, _ch
    for _row in _rows:
        assert len(_row) == 5 and set(_row) <= {"#", "."}, (_ch, _row)


# ---------------------------------------------------------------------------
# Canvas: an RGB image held as one flat bytearray, plus the drawing
# primitives the page needs.  All coordinates are clipped to the page.
# ---------------------------------------------------------------------------

class Page:
    def __init__(self):
        self.buf = bytearray(PAPER * (WIDTH * HEIGHT))

    def px(self, x, y, color):
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            i = (y * WIDTH + x) * 3
            self.buf[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0 = max(x, 0)
        y0 = max(y, 0)
        x1 = min(x + w, WIDTH)
        y1 = min(y + h, HEIGHT)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * WIDTH + x0) * 3
            self.buf[i:i + 3 * (x1 - x0)] = row

    def frame(self, x, y, w, h, color, t=2):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        """Bresenham line; t>1 draws a square brush of that size."""
        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            if t == 1:
                self.px(x0, y0, color)
            else:
                self.rect(x0 - t // 2, y0 - t // 2, t, t, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def polyline(self, points, color, t=1):
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            self.line(x0, y0, x1, y1, color, t)

    def circle(self, cx, cy, r, color, filled=True):
        if filled:
            for dy in range(-r, r + 1):
                dx = int((r * r - dy * dy) ** 0.5)
                self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)
        else:
            steps = max(12, int(2 * math.pi * r))
            for i in range(steps):
                a = 2 * math.pi * i / steps
                self.rect(cx + int(r * math.cos(a)) - 1,
                          cy + int(r * math.sin(a)) - 1, 2, 2, color)

    def triangle(self, p1, p2, p3, color):
        """Filled triangle, scanline by scanline."""
        (x0, y0), (x1, y1), (x2, y2) = sorted(
            (p1, p2, p3), key=lambda p: p[1])

        def edge_x(xa, ya, xb, yb, y):
            if yb == ya:
                return float(xa)
            return xa + (xb - xa) * (y - ya) / (yb - ya)

        for y in range(y0, y2 + 1):
            if y < y1:
                xa = edge_x(x0, y0, x1, y1, y)
            else:
                xa = edge_x(x1, y1, x2, y2, y)
            xb = edge_x(x0, y0, x2, y2, y)
            xs, xe = int(min(xa, xb)), int(max(xa, xb))
            self.rect(xs, y, xe - xs + 1, 1, color)

    # -- text ---------------------------------------------------------------

    def text_w(self, s, scale):
        return max(0, len(s) * 6 * scale - scale)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                MISSING.add(ch)
                cx += 6 * scale
                continue
            for r, row in enumerate(glyph):
                for col, bit in enumerate(row):
                    if bit == "#":
                        self.rect(cx + col * scale, y + r * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, s, scale, color):
        self.text(cx - self.text_w(s, scale) // 2, y, s, scale, color)

    def wrap(self, s, max_w, scale):
        """Greedy word wrap; returns a list of lines that fit max_w."""
        lines = []
        for chunk in s.split("\n"):
            words = chunk.split(" ")
            cur = ""
            for w in words:
                trial = (cur + " " + w).strip()
                if self.text_w(trial, scale) <= max_w or not cur:
                    cur = trial
                else:
                    lines.append(cur)
                    cur = w
            if cur:
                lines.append(cur)
        return lines

    def para(self, x, y, s, scale, max_w, color, lh=None):
        """Draw a wrapped paragraph; returns the y just below it."""
        if lh is None:
            lh = 8 * scale + 3
        for line in self.wrap(s, max_w, scale):
            self.text(x, y, line, scale, color)
            y += lh
        return y


# ---------------------------------------------------------------------------
# PNG writer: my own minimal encoder.  8-bit RGB, colour type 2, no
# interlace, one IDAT chunk holding zlib-compressed scanlines, each
# prefixed with filter byte 0.  zlib output is deterministic, so the
# whole file is byte-identical on every run.
# ---------------------------------------------------------------------------

def _chunk(kind, data):
    return (struct.pack(">I", len(data)) + kind + data +
            struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))


def encode_png(buf, width, height):
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = bytearray()
    row_len = width * 3
    for y in range(height):
        raw.append(0)
        raw += buf[y * row_len:(y + 1) * row_len]
    idat = zlib.compress(bytes(raw), 9)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) +
            _chunk(b"IDAT", idat) + _chunk(b"IEND", b""))


# ---------------------------------------------------------------------------
# Small hand-drawn pictures.  Each takes the top-left corner of its box
# and draws inside it with the primitives above.  Nothing is traced or
# copied: every picture is a few rectangles, triangles and circles.
# ---------------------------------------------------------------------------

def pic_chip(p, x, y, w, h):
    """Headline picture: a chip with pins and a rising market arrow."""
    p.rect(x, y, w, h, LIGHT)
    p.text(x + 14, y + 10, "+31%", 4, GREEN)
    # Arrow climbing from lower left to upper right.
    p.polyline([(x + 18, y + 222), (x + 150, y + 150), (x + 300, y + 76)],
               GREEN, t=4)
    p.line(x + 300, y + 76, x + 276, y + 82, GREEN, t=4)
    p.line(x + 300, y + 76, x + 292, y + 100, GREEN, t=4)
    # Chip body with pins on all four sides.
    cx, cy, s = x + 150, y + 96, 100
    for i in range(5):
        off = 8 + i * 20
        p.rect(cx + off, cy - 14, 10, 14, DARK_BLUE)
        p.rect(cx + off, cy + s, 10, 14, DARK_BLUE)
        p.rect(cx - 14, cy + off, 14, 10, DARK_BLUE)
        p.rect(cx + s, cy + off, 14, 10, DARK_BLUE)
    p.rect(cx, cy, s, s, DARK_BLUE)
    p.rect(cx + 18, cy + 18, s - 36, s - 36, BLUE)
    p.rect(cx + 34, cy + 34, s - 68, s - 68, DARK_BLUE)
    p.text(cx + s // 2 - p.text_w("GPU", 3) // 2, cy + s // 2 - 12,
           "GPU", 3, WHITE)
    p.text(x + 14, y + h - 22, "THE CHIPMAKER'S COMEBACK", 1, GREY)


def pic_drone(p, x, y, w, h):
    """Mexico: a surveillance drone over mountain ridges."""
    p.rect(x, y, w, h, SKY)
    p.circle(x + 104, y + 18, 10, ORANGE)
    p.triangle((x - 4, y + h), (x + 52, y + 52), (x + 108, y + h), MID_GREY)
    p.triangle((x + 56, y + h), (x + 96, y + 66), (x + 132, y + h), GREY)
    # Drone body, arms, spinning rotors and legs.
    p.rect(x + 46, y + 30, 36, 10, INK)
    p.line(x + 50, y + 35, x + 34, y + 26, INK, t=2)
    p.line(x + 78, y + 35, x + 94, y + 26, INK, t=2)
    p.rect(x + 22, y + 24, 26, 3, INK)
    p.rect(x + 80, y + 24, 26, 3, INK)
    p.line(x + 54, y + 40, x + 54, y + 48, INK, t=2)
    p.line(x + 74, y + 40, x + 74, y + 48, INK, t=2)
    p.circle(x + 64, y + 35, 3, RED)


def pic_capitol(p, x, y, w, h):
    """USA: a domed capitol building with a flag."""
    p.rect(x, y, w, h, LIGHT)
    p.line(x + 64, y + 16, x + 64, y + 34, INK, t=2)
    p.rect(x + 64, y + 16, 16, 10, RED)
    p.circle(x + 64, y + 58, 24, INK)
    p.rect(x + 38, y + 58, 52, 26, LIGHT)  # keep only the dome cap
    p.rect(x + 20, y + 58, 88, 44, GREY)
    for col in range(5):
        p.rect(x + 28 + col * 17, y + 62, 6, 34, WHITE)
    p.rect(x + 14, y + 102, 100, 6, INK)


def pic_document(p, x, y, w, h):
    """China: a sealed document."""
    p.rect(x, y, w, h, LIGHT)
    p.rect(x + 32, y + 12, 62, 86, WHITE)
    p.frame(x + 32, y + 12, 62, 86, INK, t=2)
    for i in range(4):
        p.rect(x + 40, y + 24 + i * 12, 46, 3, MID_GREY)
    # Red seal stamped over the corner of the page.
    p.circle(x + 88, y + 82, 13, RED)
    p.circle(x + 88, y + 82, 8, WHITE)
    p.circle(x + 88, y + 82, 3, RED)


def pic_sudan(p, x, y, w, h):
    """Sudan: buildings in Khartoum with smoke rising."""
    p.rect(x, y, w, h, SKY)
    p.circle(x + 30, y + 36, 8, MID_GREY)
    p.circle(x + 40, y + 24, 10, MID_GREY)
    p.circle(x + 28, y + 12, 7, MID_GREY)
    p.rect(x + 12, y + 50, 34, 62, INK)
    p.rect(x + 58, y + 66, 42, 46, GREY)
    for r in range(3):
        for c in range(2):
            p.rect(x + 18 + c * 14, y + 58 + r * 14, 6, 6, PAPER)
    for r in range(2):
        for c in range(2):
            p.rect(x + 64 + c * 16, y + 74 + r * 14, 6, 6, PAPER)
    p.line(x + 92, y + 66, x + 92, y + 48, INK, t=2)
    p.rect(x + 92, y + 48, 14, 9, BLUE)


def pic_factory_fire(p, x, y, w, h):
    """Indonesia: a factory with a chimney, flames and smoke."""
    p.rect(x, y, w, h, LIGHT)
    p.circle(x + 100, y + 16, 8, MID_GREY)
    p.circle(x + 92, y + 28, 6, MID_GREY)
    p.rect(x + 88, y + 34, 14, 78, INK)
    p.rect(x + 12, y + 64, 72, 48, INK)
    for i in range(3):
        p.triangle((x + 12 + i * 24, y + 64), (x + 24 + i * 24, y + 48),
                   (x + 36 + i * 24, y + 64), INK)
    p.triangle((x + 26, y + 52), (x + 42, y + 24), (x + 58, y + 52), ORANGE)
    p.triangle((x + 34, y + 52), (x + 42, y + 34), (x + 50, y + 52), RED)
    for c in range(3):
        p.rect(x + 20 + c * 22, y + 74, 10, 10, PAPER)


def pic_japan(p, x, y, w, h):
    """Japan: factory output bars climbing, with the PMI reading."""
    p.rect(x, y, w, h, LIGHT)
    p.text(x + 12, y + 10, "PMI 53.7", 2, INK)
    p.rect(x + 18, y + 82, 18, 30, BLUE)
    p.rect(x + 46, y + 66, 18, 46, BLUE)
    p.rect(x + 74, y + 50, 18, 62, BLUE)
    p.polyline([(x + 14, y + 96), (x + 46, y + 74), (x + 84, y + 54),
                (x + 116, y + 34)], GREEN, t=3)
    p.line(x + 116, y + 34, x + 100, y + 38, GREEN, t=3)
    p.line(x + 116, y + 34, x + 110, y + 50, GREEN, t=3)


# ---------------------------------------------------------------------------
# The front page itself.
# ---------------------------------------------------------------------------

STORIES = [
    # (tag, headline, body, picture)
    ("MEXICO",
     "US DRONE HELPED TRACK EL CHAPO ISIDRO",
     "A US surveillance drone helped Mexican forces track the cartel "
     "leader known as El Chapo Isidro in Sinaloa, officials said. His "
     "capture set off clashes that left 20 people dead.",
     pic_drone),
    ("WASHINGTON",
     "CONGRESSMAN QUITS OVER ETHICS REPORT",
     "Rep. Jimmy Gomez will resign effective Dec. 1 after a House Ethics "
     "Committee report found substantial evidence of sexual misconduct "
     "toward a staffer, the panel said.",
     pic_capitol),
    ("BEIJING",
     "DEATH SENTENCE FOR LEAKING SECRETS",
     "A Chinese official surnamed Ma was sentenced to death for leaking "
     "35 state secrets to a foreign agency for more than $150,000, state "
     "media reported.",
     pic_document),
    ("KHARTOUM",
     "DRONE STRIKES HIT KHARTOUM",
     "Drone strikes hit homes and the United Nations building in "
     "Khartoum early on Tuesday, witnesses said, as fighting in the "
     "capital continued.",
     pic_sudan),
    ("JAKARTA",
     "MORE BODIES FOUND AFTER FACTORY FIRE",
     "More remains were recovered from the Cikande candy factory fire, "
     "officials said, as the search continues for 34 missing workers.",
     pic_factory_fire),
    ("TOKYO",
     "JAPAN FACTORIES GROW FASTER",
     "Japanese factory activity grew faster in November, with the flash "
     "PMI at 53.7, helped by demand for chips, a business survey showed.",
     pic_japan),
]

ALSO_TODAY = (
    "FIFA confirms the US will co-host the 2031 Women's World Cup, with "
    "the UK hosting in 2035. | The WFP warns wars threaten food aid for "
    "7.3m more people. | Trump orders executions to be expedited. | "
    "Virginia and Oregon sue SpaceX over Grok deepfakes."
)

SOURCES = ("Sources: Reuters, AFP, Associated Press, CNN, The Manila "
           "Times. Drawn and typeset by a program; no photographs "
           "were used.")


def draw_front_page(p):
    # Masthead.
    p.rect(28, 16, 968, 3, INK)
    p.text_center(512, 28, "THE OTTER TIMES", 8, INK)
    p.text(28, 96, "EST. 2026", 1, GREY)
    p.text(996 - p.text_w("FREE", 1), 96, "FREE", 1, GREY)
    p.text_center(512, 92, "Tuesday, 24 November 2026", 2, INK)
    p.rect(28, 116, 968, 3, INK)
    p.rect(28, 122, 968, 1, INK)

    # Headline story: Nvidia.
    p.rect(28, 134, 12, 12, RED)
    p.text(46, 135, "TOP STORY", 1, RED)
    p.text(28, 150, "HUANG RETURNS", 5, INK)
    p.text(28, 196, "AS NVIDIA CEO", 5, INK)
    p.para(28, 248,
           "Shares jump 31% as the founder takes back the top job 11 days "
           "after quitting. The Nasdaq climbs 6.5%.",
           2, 600, INK, lh=20)
    p.para(28, 318,
           "Jensen Huang is chief executive of Nvidia again, 11 days "
           "after he stepped down, the company said on Monday. Investors "
           "welcomed the return, and the Nasdaq rose 6.5% on the day. "
           "The brief handover ends after a turbulent spell at the "
           "chipmaker, whose processors power much of the AI boom.",
           1, 600, INK, lh=11)
    p.rect(28, 366, 600, 1, GREY)
    p.text(28, 378, "NVIDIA +31%   NASDAQ +6.5%   11 DAYS OUT", 2, INK)
    p.frame(648, 134, 348, 250, INK, t=2)
    pic_chip(p, 650, 136, 344, 246)

    # Rule, then the six stories in a 2 x 3 grid.
    p.rect(28, 396, 968, 2, INK)
    cell_w, cell_h = 474, 164
    for i, (tag, headline, body, pic) in enumerate(STORIES):
        cx = 28 + (i % 2) * (cell_w + 20)
        cy = 408 + (i // 2) * (cell_h + 10)
        p.frame(cx, cy, 128, 112, INK, t=2)
        pic(p, cx + 2, cy + 2, 124, 108)
        p.text(cx + 140, cy, tag, 1, RED)
        p.para(cx + 140, cy + 12, headline, 2, 334, INK, lh=20)
        p.para(cx, cy + 120, body, 1, 474, INK, lh=11)

    # Also today, then the sources line.
    p.rect(28, 922, 968, 2, INK)
    p.rect(28, 932, 12, 12, RED)
    p.text(46, 933, "ALSO TODAY", 2, INK)
    p.para(28, 954, ALSO_TODAY, 1, 968, INK, lh=11)
    p.text(28, 984, SOURCES, 1, GREY)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "out"
    os.makedirs(out_dir, exist_ok=True)
    page = Page()
    draw_front_page(page)
    data = encode_png(page.buf, WIDTH, HEIGHT)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    if MISSING:
        print("warning: no glyph for:", sorted(MISSING), file=sys.stderr)
    print("wrote %s (%d bytes)" % (path, len(data)))
    print("sha256:", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()

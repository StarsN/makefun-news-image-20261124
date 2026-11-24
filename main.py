#!/usr/bin/env python3
"""Draw the front page of THE WORLD TODAY for Tuesday 24 November 2026.

Pure Python 3 standard library only. No network access, no files read at
runtime. Renders a 1024x1024 newspaper front page using a hand-built 5x7
bitmap font and a hand-rolled PNG encoder, so two runs produce exactly
the same bytes.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py   (writes out/entry.png)
"""

import math
import os
import struct
import zlib

WIDTH, HEIGHT = 1024, 1024

# ------------------------------------------------------------------ colours
PAPER = (248, 244, 236)
INK = (24, 24, 24)
GREY = (80, 76, 68)
RED = (178, 40, 44)
NAVY = (22, 40, 70)
TEAL = (14, 106, 90)
SKYBLUE = (30, 80, 124)
PURPLE = (94, 46, 140)
BROWN = (140, 92, 44)
ORANGE = (182, 88, 30)
GREEN = (34, 120, 58)
WHITE = (255, 255, 255)
GOLD = (200, 154, 54)
LIGHT = (236, 232, 220)
CHIPGREEN = (22, 140, 70)
DARKGREEN = (16, 90, 48)
SAND = (214, 190, 150)

# -------------------------------------------------------------------- font
# 5x7 pixel font. '#' is a set pixel. Anything lowercase prints as uppercase.
GLYPHS = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "##  #", "# # #", "#  ##", "#  ##", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    "3": ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "   # ", "  #  ", "  #  ", "  #  "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", " ##  ", " ##  ", "     "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", " ##  ", " #   "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    ";": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", " #   "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    "-": ("     ", "     ", "     ", " ### ", "     ", "     ", "     "),
    "(": ("   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "),
    ")": (" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "),
    "/": ("    #", "    #", "   # ", "   # ", "  #  ", " #   ", "#    "),
    "%": ("#   #", "#  # ", "   # ", "  #  ", " #   ", "#  # ", "#   #"),
    "+": ("     ", "  #  ", "  #  ", " ### ", "  #  ", "  #  ", "     "),
    "=": ("     ", "     ", " ### ", "     ", " ### ", "     ", "     "),
    "$": ("  #  ", " ####", "# #  ", " ### ", "  # #", "#### ", "  #  "),
    "*": ("     ", "#   #", " # # ", " ### ", " # # ", "#   #", "     "),
    '"': (" # # ", " # # ", " # # ", "     ", "     ", "     ", "     "),
    "'": ("  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "),
    "·": ("     ", "     ", "     ", " ##  ", " ##  ", "     ", "     "),
    "•": ("     ", "     ", "     ", " ##  ", " ##  ", "     ", "     "),
    "—": ("     ", "     ", "     ", "#####", "     ", "     ", "     "),
}
for _glyph in GLYPHS.values():
    assert len(_glyph) == 7 and all(len(row) == 5 for row in _glyph)

_FOLD = {
    "’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "‐": "-",
    "é": "e", "è": "e", "ê": "e", "á": "a", "í": "i", "ó": "o",
    "ú": "u", "ñ": "n", "ü": "u", "ç": "c",
}


def normalise(text):
    """Upper-case the text and map unsupported characters to ASCII."""
    out = []
    for ch in text:
        ch = _FOLD.get(ch, ch)
        out.append(ch.upper() if ch.isalpha() else ch)
    return "".join(out)


def measure(text, size):
    return len(normalise(text)) * 6 * size


def wrap_text(text, width_px, size):
    """Split cleaned text into lines no wider than width_px."""
    per_line = max(1, width_px // (6 * size))
    words = normalise(text).split(" ")
    lines, current = [], ""
    for word in words:
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= per_line:
            current += " " + word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ------------------------------------------------------------------ canvas
class Page:
    """A flat RGB canvas with tiny drawing helpers."""

    def __init__(self, w, h, background):
        self.w, self.h = w, h
        self.pixels = bytearray(bytes(background) * (w * h))

    def put(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.pixels[i:i + 3] = bytes(colour)

    def hbar(self, x0, x1, y, colour):
        if y < 0 or y >= self.h:
            return
        x0, x1 = max(0, x0), min(self.w - 1, x1)
        if x1 < x0:
            return
        span = bytes(colour) * (x1 - x0 + 1)
        i = (y * self.w + x0) * 3
        self.pixels[i:i + len(span)] = span

    def vbar(self, x, y0, y1, colour):
        if x < 0 or x >= self.w:
            return
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            self.put(x, y, colour)

    def box(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            self.hbar(x, x + w - 1, yy, colour)

    def frame(self, x, y, w, h, colour, thick=1):
        for t in range(thick):
            self.hbar(x, x + w - 1, y + t, colour)
            self.hbar(x, x + w - 1, y + h - 1 - t, colour)
            self.vbar(x + t, y, y + h - 1, colour)
            self.vbar(x + w - 1 - t, y, y + h - 1, colour)

    def segment(self, x0, y0, x1, y1, colour, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        step_x = 1 if x0 < x1 else -1
        step_y = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for t in range(thick):
                self.put(x0 + t, y0, colour)
                self.put(x0, y0 + t, colour)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += step_x
            if e2 < dx:
                err += dx
                y0 += step_y

    def blob(self, cx, cy, r, colour):
        for dy in range(-r, r + 1):
            half = int(math.sqrt(max(0, r * r - dy * dy)))
            self.hbar(cx - half, cx + half, cy + dy, colour)

    def polygon(self, points, colour):
        top = min(y for _, y in points)
        bottom = max(y for _, y in points)
        count = len(points)
        for y in range(top, bottom + 1):
            hits = []
            for i in range(count):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % count]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    hits.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            hits.sort()
            for i in range(0, len(hits) - 1, 2):
                self.hbar(int(hits[i]), int(hits[i + 1]), y, colour)

    def starburst(self, cx, cy, outer, inner, points, colour):
        pts = []
        for i in range(points * 2):
            r = outer if i % 2 == 0 else inner
            angle = math.pi * i / points - math.pi / 2
            pts.append((int(cx + r * math.cos(angle)),
                        int(cy + r * math.sin(angle))))
        self.polygon(pts, colour)

    def curve(self, cx, cy, r, a0, a1, colour, thick=2):
        steps = max(8, int(abs(a1 - a0) * r / 4))
        prev = None
        for i in range(steps + 1):
            a = a0 + (a1 - a0) * i / steps
            p = (int(cx + r * math.cos(a)), int(cy + r * math.sin(a)))
            if prev is not None:
                self.segment(prev[0], prev[1], p[0], p[1], colour, thick)
            prev = p

    # --------------------------------------------------------------- text
    def print_text(self, x, y, text, size, colour):
        text = normalise(text)
        cursor = x
        for ch in text:
            glyph = GLYPHS.get(ch, GLYPHS["?"])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "#":
                        self.box(cursor + col * size, y + row * size,
                                 size, size, colour)
            cursor += 6 * size
        return cursor - x

    def centred(self, y, text, size, colour):
        w = measure(text, size)
        self.print_text((WIDTH - w) // 2, y, text, size, colour)

    def block(self, x, y, lines, size, colour, gap=17):
        for line in lines:
            self.print_text(x, y, line, size, colour)
            y += gap
        return y


# --------------------------------------------------------------------- png
def _png_chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def write_png(page):
    raw = bytearray()
    stride = page.w * 3
    for y in range(page.h):
        raw.append(0)  # filter type: none
        raw += page.pixels[y * stride:(y + 1) * stride]
    header = struct.pack(">IIBBBBB", page.w, page.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _png_chunk(b"IHDR", header) +
            _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            _png_chunk(b"IEND", b""))


# ------------------------------------------------------------------ layout
MARGIN = 28
RIGHT = WIDTH - MARGIN


def masthead(pg):
    pg.centred(30, "THE WORLD TODAY", 6, INK)
    pg.hbar(MARGIN, RIGHT - 1, 84, INK)
    pg.centred(92, "TUESDAY, 24 NOVEMBER 2026", 2, RED)
    pg.hbar(MARGIN, RIGHT - 1, 116, INK)
    pg.hbar(MARGIN, RIGHT - 1, 120, INK)


def headline_art(pg):
    """Nvidia: a chip on a dark board, a green arrow climbing past it."""
    x0, y0, x1, y1 = 652, 140, RIGHT, 420
    pg.box(x0, y0, x1 - x0, y1 - y0, NAVY)
    pg.print_text(x0 + 16, y0 + 14, "SANTA CLARA, CALIFORNIA", 2, GOLD)
    # circuit traces
    for ty in (y0 + 60, y0 + 96, y0 + 132, y0 + 168):
        pg.hbar(x0 + 12, x0 + 120, ty, (44, 66, 104))
    pg.vbar(x0 + 120, y0 + 60, y0 + 168, (44, 66, 104))
    # the chip
    cx, cy = 780, 268
    pg.box(cx - 58, cy - 58, 116, 116, CHIPGREEN)
    pg.frame(cx - 58, cy - 58, 116, 116, DARKGREEN, 3)
    for pin in range(-2, 3):
        pg.box(cx + pin * 24 - 3, cy - 72, 6, 14, GOLD)
        pg.box(cx + pin * 24 - 3, cy + 58, 6, 14, GOLD)
        pg.box(cx - 72, cy + pin * 24 - 3, 14, 6, GOLD)
        pg.box(cx + 58, cy + pin * 24 - 3, 14, 6, GOLD)
    pg.box(cx - 34, cy - 34, 68, 68, DARKGREEN)
    pg.print_text(cx - 22, cy - 12, "NVDA", 2, WHITE)
    # climbing arrow
    pts = [(848, 340), (878, 300), (906, 316), (936, 244), (952, 258),
           (952, 236), (936, 224), (912, 288), (884, 274), (856, 312)]
    pg.polygon(pts, (64, 220, 110))
    pg.print_text(x0 + 16, y1 - 52, "SHARES +31% IN A DAY", 2, (64, 220, 110))
    pg.hbar(x0, x1 - 1, y1 - 1, GOLD)
    pg.print_text(x0 + 16, y1 - 26, "NASDAQ +6.5% - S&P +4.7%", 2, WHITE)


def headline(pg):
    pg.print_text(MARGIN, 140, "TECH - NVIDIA", 2, RED)
    pg.print_text(MARGIN, 166, "HUANG IS", 5, INK)
    pg.print_text(MARGIN, 208, "BACK AT", 5, INK)
    pg.print_text(MARGIN, 250, "NVIDIA", 5, INK)
    deck = wrap_text(
        "Eleven days after he quit as chief executive, Jensen Huang is "
        "back running the chipmaker he co-founded. Shares jump 31% and "
        "lift the Nasdaq 6.5%.", 600, 2)
    y = pg.block(MARGIN, 306, deck, 2, GREY)
    deck2 = wrap_text(
        "Trump pressed for his return. US lawmakers vowed to keep "
        "probing Nvidia.", 600, 2)
    y = pg.block(MARGIN, y + 8, deck2, 2, GREY)
    y += 12
    pg.hbar(MARGIN, 620, y, RED)
    pg.print_text(MARGIN, y + 8, "BOARD: RETURN POSED NO RISK", 2, RED)


# --------------------------------------------------------- story pictures
def art_drone(pg, x, y):
    """Surveillance drone over a desert ridge."""
    pg.box(x, y, 72, 72, SAND)
    pg.box(x, y + 48, 72, 24, (150, 104, 60))
    pg.polygon([(x + 8, y + 52), (x + 30, y + 42), (x + 52, y + 50),
                (x + 64, y + 58), (x + 40, y + 62), (x + 16, y + 60)],
               (120, 82, 46))
    pg.box(x + 28, y + 26, 16, 10, INK)
    pg.segment(x + 16, y + 22, x + 28, y + 28, INK, 2)
    pg.segment(x + 56, y + 22, x + 44, y + 28, INK, 2)
    pg.segment(x + 10, y + 18, x + 24, y + 22, INK, 2)
    pg.segment(x + 62, y + 18, x + 48, y + 22, INK, 2)
    pg.segment(x + 24, y + 32, x + 34, y + 40, RED, 2)
    pg.segment(x + 48, y + 32, x + 38, y + 40, RED, 2)


def art_capitol(pg, x, y):
    """US Capitol dome and columns."""
    pg.box(x, y, 72, 72, NAVY)
    pg.blob(x + 36, y + 30, 15, WHITE)
    pg.box(x + 22, y + 30, 28, 6, WHITE)
    for cx in (x + 25, x + 33, x + 41):
        pg.box(cx, y + 36, 4, 18, WHITE)
    pg.box(x + 18, y + 54, 36, 4, WHITE)
    pg.box(x + 34, y + 10, 4, 8, GOLD)
    pg.box(x + 12, y + 60, 48, 4, GOLD)


def art_seal(pg, x, y):
    """A sealed document."""
    pg.box(x, y, 72, 72, (238, 234, 222))
    pg.box(x + 18, y + 10, 36, 50, WHITE)
    pg.frame(x + 18, y + 10, 36, 50, INK, 1)
    pg.hbar(x + 22, x + 50, y + 18, INK)
    pg.hbar(x + 22, x + 50, y + 26, INK)
    pg.hbar(x + 22, x + 50, y + 34, INK)
    pg.blob(x + 36, y + 48, 9, RED)
    pg.starburst(x + 36, y + 48, 6, 3, 5, GOLD)


def art_un(pg, x, y):
    """A blue UN-style building under a dark sky."""
    pg.box(x, y, 72, 72, (30, 40, 60))
    pg.box(x + 16, y + 18, 40, 44, SKYBLUE)
    for row in range(5):
        for col in range(4):
            pg.box(x + 20 + col * 9, y + 22 + row * 8, 5, 4, WHITE)
    pg.blob(x + 36, y + 10, 6, WHITE)
    pg.segment(x + 30, y + 12, x + 42, y + 8, WHITE, 2)
    pg.segment(x + 30, y + 8, x + 42, y + 12, WHITE, 2)
    pg.starburst(x + 58, y + 14, 8, 3, 8, ORANGE)
    pg.blob(x + 58, y + 14, 3, GOLD)


def art_factory(pg, x, y):
    """Factory chimneys with smoke and a flame."""
    pg.box(x, y, 72, 72, (64, 62, 58))
    pg.box(x + 10, y + 40, 52, 24, (42, 40, 38))
    pg.box(x + 14, y + 16, 8, 26, (42, 40, 38))
    pg.box(x + 26, y + 24, 8, 18, (42, 40, 38))
    pg.blob(x + 18, y + 10, 7, (205, 205, 205))
    pg.blob(x + 30, y + 6, 6, (205, 205, 205))
    pg.starburst(x + 48, y + 34, 12, 5, 8, ORANGE)
    pg.blob(x + 48, y + 34, 4, GOLD)


def art_bars(pg, x, y):
    """A rising bar chart."""
    pg.box(x, y, 72, 72, LIGHT)
    pg.hbar(x + 8, x + 64, y + 60, INK)
    pg.vbar(x + 8, y + 12, y + 60, INK)
    heights = [14, 20, 18, 28, 36]
    for i, h in enumerate(heights):
        pg.box(x + 14 + i * 10, y + 60 - h, 7, h, GREEN if i < 4 else RED)
    pg.segment(x + 12, y + 44, x + 62, y + 16, RED, 3)
    pg.polygon([(x + 62, y + 16), (x + 56, y + 16), (x + 62, y + 22)],
               RED)


STORIES = [
    dict(kicker="MEXICO", colour=TEAL, art=art_drone,
         title="US DRONE HELPED CATCH DRUG LORD",
         body="Mexico says a US surveillance drone helped track 'El "
              "Chapo Isidro' in Sinaloa. His capture set off clashes "
              "that left 20 people dead."),
    dict(kicker="USA", colour=NAVY, art=art_capitol,
         title="CONGRESSMAN GOMEZ TO RESIGN",
         body="Rep. Jimmy Gomez quits from Dec 1 after a House Ethics "
              "report found substantial evidence of sexual misconduct "
              "toward a staffer."),
    dict(kicker="CHINA", colour=RED, art=art_seal,
         title="DEATH SENTENCE FOR SPYING",
         body="An official surnamed Ma is sentenced to death for "
              "leaking 35 state secrets to a foreign agency for over "
              "$150,000, state media say."),
    dict(kicker="SUDAN", colour=SKYBLUE, art=art_un,
         title="DRONES HIT UN BUILDING",
         body="Drone strikes hit homes and the UN building in "
              "Khartoum, the capital, early on Tuesday, reports say."),
    dict(kicker="INDONESIA", colour=ORANGE, art=art_factory,
         title="MORE BODIES FOUND AT FACTORY",
         body="Rescuers recover more remains from the candy factory "
              "fire in Cikande. The search goes on for 34 missing "
              "workers."),
    dict(kicker="JAPAN", colour=GREEN, art=art_bars,
         title="JAPAN FACTORIES PICK UP",
         body="Factory activity grows faster in November, flash PMI "
              "53.7, as output and export orders rise on chip "
              "demand."),
]


def story_block(pg, x, y, w, story):
    pg.hbar(x, x + w - 1, y, story["colour"])
    pg.hbar(x, x + w - 1, y + 2, story["colour"])
    story["art"](pg, x, y + 12)
    tx = x + 84
    tw = w - 84
    pg.print_text(tx, y + 12, story["kicker"], 2, story["colour"])
    yy = pg.block(tx, y + 34, wrap_text(story["title"], tw, 2), 2, INK)
    pg.block(tx, yy + 4, wrap_text(story["body"], tw, 2), 2, GREY)


def story_grid(pg):
    col_w = 472
    xs = [MARGIN, 524]
    ys = [452, 616, 780]
    for i, story in enumerate(STORIES):
        story_block(pg, xs[i % 2], ys[i // 2], col_w, story)


def footer(pg):
    y = 940
    pg.print_text(MARGIN, y, "ALSO TODAY:", 2, RED)
    items = ("FIFA confirms the US will co-host the 2031 Women's World "
             "Cup, UK gets 2035 - WFP warns wars threaten food aid for "
             "7.3m more people - Trump orders executions to be "
             "expedited - Virginia and Oregon sue SpaceX over Grok "
             "deepfakes")
    lead = MARGIN + measure("ALSO TODAY: ", 2)
    first_w = WIDTH - 2 * MARGIN - measure("ALSO TODAY: ", 2)
    first_line = wrap_text(items, first_w, 2)[0]
    pg.print_text(lead, y, first_line, 2, INK)
    rest = items[len(first_line):].strip()
    yy = y + 17
    for line in wrap_text(rest, WIDTH - 2 * MARGIN, 2):
        pg.print_text(MARGIN, yy, line, 2, INK)
        yy += 17
    pg.hbar(MARGIN, RIGHT - 1, 990, INK)
    pg.centred(998, "SOURCES: AP - REUTERS - AFP - CNN - THE MANILA "
                     "TIMES - THE JAPAN TIMES", 2, GREY)


def render():
    pg = Page(WIDTH, HEIGHT, PAPER)
    masthead(pg)
    headline_art(pg)
    headline(pg)
    pg.hbar(MARGIN, RIGHT - 1, 436, INK)
    story_grid(pg)
    footer(pg)
    return pg


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(outdir, exist_ok=True)
    data = write_png(render())
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path} ({len(data)} bytes)")


if __name__ == "__main__":
    main()

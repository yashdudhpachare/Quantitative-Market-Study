#!/usr/bin/env python3
"""Generate a 1200x630 social/OG cover for the Quantitative Market Study page.

Re-uses the hero's K-means-style scatter on a warm charcoal field, then bakes in
the title, eyebrow, and a metadata line so link previews read on their own.
Pure-Pillow, no numpy.
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont

random.seed(11)

W, H = 1200, 630
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "og-cover.jpg")

# Palette (site tokens)
CHAR_TOP = (44, 40, 37)
CHAR_BOT = (16, 14, 11)
CREAM = (250, 247, 240)
GOLD = (200, 184, 154)
GOLD_DEEP = (176, 158, 126)
CLUSTERS = [
    (200, 184, 154), (196, 122, 98), (120, 158, 148),
    (140, 130, 170), (216, 200, 172),
]

FONT_DIR = "/System/Library/Fonts/Supplemental"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# --- base vertical gradient ---
base = Image.new("RGB", (W, H), CHAR_BOT)
bd = ImageDraw.Draw(base)
for y in range(H):
    bd.line([(0, y), (W, y)], fill=lerp(CHAR_TOP, CHAR_BOT, (y / H) ** 0.85))

# --- faint chart grid ---
grid = Image.new("RGB", (W, H), (0, 0, 0))
gd = ImageDraw.Draw(grid)
step = 60
for x in range(0, W, step):
    gd.line([(x, 0), (x, H)], fill=(26, 24, 20), width=1)
for y in range(0, H, step):
    gd.line([(0, y), (W, y)], fill=(26, 24, 20), width=1)
base = ImageChops.screen(base, grid)

# --- clustered glow scatter (weighted to the right so the left stays clear for text) ---
acc = Image.new("RGB", (W, H), (0, 0, 0))
centres = [
    (0.70, 0.66, 0.085, 620),
    (0.82, 0.45, 0.060, 260),
    (0.62, 0.40, 0.058, 240),
    (0.88, 0.70, 0.055, 200),
    (0.74, 0.30, 0.045, 150),
]
for ci, (cxr, cyr, spread, n) in enumerate(centres):
    color = CLUSTERS[ci % len(CLUSTERS)]
    cx0, cy0 = cxr * W, cyr * H
    for _ in range(n):
        ang = random.random() * 2 * math.pi
        rad = abs(random.gauss(0, spread)) * max(W, H)
        px = cx0 + math.cos(ang) * rad * random.uniform(0.6, 1.4)
        py = cy0 + math.sin(ang) * rad * 0.7 * random.uniform(0.6, 1.4)
        if not (0 < px < W and 0 < py < H):
            continue
        r = random.uniform(1.6, 4.2)
        a = random.uniform(0.45, 1.0)
        dot = Image.new("RGB", (W, H), (0, 0, 0))
        ImageDraw.Draw(dot).ellipse(
            [px - r, py - r, px + r, py + r],
            fill=tuple(int(c * a) for c in color))
        acc = ImageChops.lighter(acc, dot)

acc_soft = acc.filter(ImageFilter.GaussianBlur(1.1))
acc_glow = Image.eval(acc.filter(ImageFilter.GaussianBlur(7)), lambda v: int(v * 0.55))
out = ImageChops.screen(base, ImageChops.lighter(acc_soft, acc_glow))

# --- left-side darkening so the title sits on a calm field ---
shade = Image.new("L", (W, H), 0)
sd = ImageDraw.Draw(shade)
for x in range(W):
    sd.line([(x, 0), (x, H)], fill=int(150 * max(0, 1 - x / (W * 0.72))))
dark = Image.new("RGB", (W, H), (12, 11, 9))
out = Image.composite(dark, out, shade)

# bottom gradient for the meta line
bshade = Image.new("L", (W, H), 0)
bsd = ImageDraw.Draw(bshade)
for y in range(H):
    bsd.line([(0, y), (W, y)], fill=int(150 * max(0, (y - H * 0.62) / (H * 0.38))))
out = Image.composite(dark, out, bshade)

# soft vignette
vig = Image.new("L", (W, H), 0)
ImageDraw.Draw(vig).ellipse([-W * 0.18, -H * 0.18, W * 1.18, H * 1.18], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(170))
out = Image.composite(out, Image.new("RGB", (W, H), (8, 7, 5)), vig)

# ---------------------------------------------------------------- text
draw = ImageDraw.Draw(out)
MARGIN = 70

# tracked (letter-spaced) text helper
def tracked(draw, xy, text, fnt, fill, tracking):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x

# wrap helper
def wrap(text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

eyebrow_f = font("Courier New Bold.ttf", 19)
title_f = font("Georgia Italic.ttf", 70)
meta_f = font("Courier New.ttf", 17)

# top rule + eyebrow
draw.line([(MARGIN, 92), (MARGIN + 46, 92)], fill=GOLD_DEEP, width=2)
tracked(draw, (MARGIN + 62, 82), "QUANTITATIVE MARKET STUDY", eyebrow_f, GOLD, 3)

# title (display italic, cream)
title = "Five customers hiding in one dataset."
lines = wrap(title, title_f, W - MARGIN - 360)
ty = 250 - (len(lines) - 1) * 44
for ln in lines:
    draw.text((MARGIN, ty), ln, font=title_f, fill=CREAM)
    ty += 84

# bottom meta
tracked(draw, (MARGIN, H - 78),
        "7,665 PURCHASES  ·  STATISTICS  ·  K-MEANS  ·  5 SEGMENTS",
        meta_f, (216, 200, 172), 2)

out = out.filter(ImageFilter.GaussianBlur(0.3))
out.save(OUT, quality=90)
print("og-cover ->", OUT, out.size)

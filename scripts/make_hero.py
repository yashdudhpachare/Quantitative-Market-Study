#!/usr/bin/env python3
"""Generate an on-brand hero image for the Quantitative Market Study page.

A soft K-means-style clustered scatter (the study's centrepiece) rendered on a
warm charcoal field in the site palette. Pure-Pillow, no numpy.
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

random.seed(7)

W, H = 2200, 1375
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "hero.jpg")

CHAR_TOP = (44, 40, 37)
CHAR_BOT = (18, 16, 13)
CLUSTERS = [
    (200, 184, 154),  # gold
    (196, 122, 98),   # terracotta
    (120, 158, 148),  # sage
    (140, 130, 170),  # plum
    (216, 200, 172),  # pale gold
]


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# --- base vertical gradient ---
base = Image.new("RGB", (W, H), CHAR_BOT)
bd = ImageDraw.Draw(base)
for y in range(H):
    bd.line([(0, y), (W, y)], fill=lerp(CHAR_TOP, CHAR_BOT, (y / H) ** 0.85))

# --- faint chart grid, screened in subtly ---
grid = Image.new("RGB", (W, H), (0, 0, 0))
gd = ImageDraw.Draw(grid)
step = 100
for x in range(0, W, step):
    gd.line([(x, 0), (x, H)], fill=(26, 24, 20), width=1)
for y in range(0, H, step):
    gd.line([(0, y), (W, y)], fill=(26, 24, 20), width=1)
base = ImageChops.screen(base, grid)

# --- clustered glow scatter (additive via lighter) ---
acc = Image.new("RGB", (W, H), (0, 0, 0))
centres = [
    (0.30, 0.74, 0.090, 1200),  # dominant low-spend corner
    (0.46, 0.56, 0.060, 430),
    (0.62, 0.63, 0.078, 540),
    (0.55, 0.40, 0.052, 300),
    (0.34, 0.52, 0.046, 250),
]
for ci, (cxr, cyr, spread, n) in enumerate(centres):
    color = CLUSTERS[ci % len(CLUSTERS)]
    cx0, cy0 = cxr * W, cyr * H
    for _ in range(n):
        ang = random.random() * 2 * math.pi
        rad = abs(random.gauss(0, spread)) * max(W, H)
        px = cx0 + math.cos(ang) * rad * random.uniform(0.6, 1.4)
        py = cy0 + math.sin(ang) * rad * 0.55 * random.uniform(0.6, 1.4)
        if not (0 < px < W and 0 < py < H):
            continue
        r = random.uniform(2.0, 5.5)
        a = random.uniform(0.45, 1.0)
        dot = Image.new("RGB", (W, H), (0, 0, 0))
        ImageDraw.Draw(dot).ellipse(
            [px - r, py - r, px + r, py + r],
            fill=tuple(int(c * a) for c in color))
        acc = ImageChops.lighter(acc, dot)

acc_soft = acc.filter(ImageFilter.GaussianBlur(1.3))
acc_glow = Image.eval(acc.filter(ImageFilter.GaussianBlur(8)), lambda v: int(v * 0.55))
acc_final = ImageChops.lighter(acc_soft, acc_glow)

out = ImageChops.screen(base, acc_final)

# --- warm lower-left lift + soft vignette ---
warm = Image.new("RGB", (W, H), (0, 0, 0))
ImageDraw.Draw(warm).ellipse([-W * 0.25, H * 0.35, W * 0.75, H * 1.5], fill=(46, 36, 28))
warm = warm.filter(ImageFilter.GaussianBlur(240))
out = ImageChops.screen(out, warm)

vig = Image.new("L", (W, H), 0)
ImageDraw.Draw(vig).ellipse([-W * 0.15, -H * 0.15, W * 1.15, H * 1.15], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(260))
dark = Image.new("RGB", (W, H), (10, 9, 7))
out = Image.composite(out, dark, vig)

out = out.filter(ImageFilter.GaussianBlur(0.4))
out.save(OUT, quality=88)
print("hero ->", OUT, out.size)

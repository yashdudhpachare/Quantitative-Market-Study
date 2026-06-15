#!/usr/bin/env python3
"""Rasterize the Quantitative Market Study slide deck into per-slide JPGs.

Output layout:
  public/decks/quant-market-study/001.jpg ... 034.jpg
  public/decks/manifest.json
"""
import os, json, sys
import fitz  # PyMuPDF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "public", "decks")

# (source-filename, slug) — order matters
DECKS = [
    ("Quantitative Market Study.pdf", "quant-market-study"),
]

# Render at a width target of ~1600px (good for HD thumbs + 2x).
TARGET_WIDTH = 1600
JPG_QUALITY  = 82


def render_pdf(pdf_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    pages = []
    for i in range(len(doc)):
        page = doc.load_page(i)
        rect = page.rect
        scale = TARGET_WIDTH / rect.width
        mtx = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mtx, alpha=False)
        fname = f"{i+1:03d}.jpg"
        pix.save(os.path.join(out_dir, fname), jpg_quality=JPG_QUALITY)
        pages.append(fname)
    doc.close()
    return pages


def main():
    manifest = {}
    for pdf_name, slug in DECKS:
        pdf_path = os.path.join(ROOT, pdf_name)
        out_dir  = os.path.join(OUT, slug)
        if not os.path.exists(pdf_path):
            print(f"MISSING: {pdf_path}", file=sys.stderr)
            continue
        pages = render_pdf(pdf_path, out_dir)
        manifest[slug] = {"source": pdf_name, "count": len(pages), "files": pages}
        print(f"{slug:24s}  {len(pages):3d} slides -> {out_dir}")
    man_path = os.path.join(OUT, "manifest.json")
    with open(man_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest -> {man_path}")


if __name__ == "__main__":
    main()

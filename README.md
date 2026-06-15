# Quantitative Market Study — Customer Segmentation from Purchase Data

A single-file, editorial case-study page that turns the original 34-slide
deck into a scrollable narrative for the portfolio. From **7,665 cleaned
purchases** to **five customer segments** and a marketing strategy for each —
told in six chapters: Premise · The Data · Patterns · Evidence · Segments ·
Strategy.

## Structure

```
index.html                          # the whole site (HTML + CSS + JS, no build step)
hero.jpg                            # generated hero (K-means-style scatter)
og-cover.jpg                        # 1200x630 social / link-preview cover
public/decks/
  quant-market-study/001–034.jpg    # rendered slides
  manifest.json                     # deck manifest
scripts/
  extract_deck.py                   # PDF → per-slide JPGs + manifest
  make_hero.py                      # generates hero.jpg
  make_og.py                        # generates og-cover.jpg (title baked in)
Quantitative Market Study.pdf       # source deck
```

## Viewing

It's a static page — open `index.html`, or serve the folder:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

## Regenerating assets

```bash
python3 scripts/extract_deck.py     # re-render slides if the PDF changes
python3 scripts/make_hero.py        # re-render the hero image
python3 scripts/make_og.py          # re-render the social cover (og-cover.jpg)
```

Requires `PyMuPDF` (slides) and `Pillow` (hero + cover).

## Interactions

- **Chapter rail** in the nav tracks your scroll position.
- **Click any slide** to open it in a lightbox with a filmstrip of the whole chapter.
- **"View … slides"** links open a per-chapter drawer.
- **"View Full Deck"** opens every slide in original order.

## Credits

Team · Awart Katiyar · Paarth S Barkur · Shuvadeep Ghosh · Yash Dudhpachare

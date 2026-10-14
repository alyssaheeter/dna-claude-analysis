# Proposed CLAUDE.md changes (not applied; needs user approval)

## 1. Project Overview (replace the last sentence)

Personal genome analysis toolkit. Scripts analyze raw DNA data and output markdown reports. The final step is generating a single-page HTML summary in the Nocturne Hothouse brand look (see `webpage/brand.css`).

## 2. Replace the whole "Webpage Generation" section

## Webpage Generation

Reference `webpage/STYLE_GUIDE.md` for exact styling. Key points:

- **Single HTML file** with inline CSS/JS (`scripts/generate_webpage.py` inlines `webpage/brand.css` and `webpage/assets/*.svg`)
- **Brand aesthetic**: Nocturne Hothouse (see `webpage/brand.css`): dark night-fern ground, antique gold line work, one garnet accent; Cormorant Garamond headlines, Jost text, Pinyon Script for the name only
- **Fixed header** with brand mark, wordmark and navigation
- **Sections** for each analysis category
- **Colour coding**: sage = typical, gold = moderate, rose text on dark for elevated; garnet is a fill only, never text on dark; status always has an icon and a word
- **Checks**: `NODE_PATH=/opt/node22/lib/node_modules PLAYWRIGHT_CHROMIUM=/path/to/chromium node scripts/check_webpage.js` (72 checks)

### Section IDs
(unchanged: keep the existing table of 17 section IDs, status through carrier)

### Data Flow
```
reports/*.md → Parse findings → HTML sections → webpage/dna_terminal.html
```

## 3. File Locations table (add two rows)

| Path | Purpose |
|------|---------|
| `data/` | Raw DNA files (gitignored) |
| `scripts/` | Python analysis scripts |
| `reports/` | Generated markdown reports |
| `webpage/` | Style guide + generated HTML |
| `webpage/brand.css` | Nocturne Hothouse stylesheet (single source of CSS for the page) |
| `webpage/assets/` | Brand SVGs (mark, leaf, heart) inlined into the page |

## 4. Important Rules (rule 3 wording, optional)

3. **Single HTML output** — No external dependencies except Google Fonts (unchanged)

All other rules (privacy, not medical advice, English, highlight risks) stay as they are. Rule 5 still holds: critical findings use the risk badge (garnet fill) and rose status text.

# Genome Notes: Style and Structure Guide

## Overview

A single-page, single-file HTML summary of the genome reports, styled in the **Nocturne Hothouse** brand kit (Kit 01: dark hothouse, gilded line, garnet bloom). All CSS lives in `webpage/brand.css`; `scripts/generate_webpage.py` inlines it, the SVG assets and a tiny script into `webpage/dna_terminal.html` (git-ignored output). The only external request is Google Fonts.

`webpage/example.html` is the legacy terminal-style demo. It is kept for history only and is no longer read by the generator.

---

## Document structure

```
<!DOCTYPE html>
<html lang="en">
  <head>  meta, title, Google Fonts link, <style> (brand.css inlined)
  <body>
    hidden SVG sprite (symbols: sword, heart)
    a.skip
    <header>  .header-top (.logo: mark + .wordmark, .timestamp) + <nav aria-label>
    <main>
      #hero            kicker, h1, one sentence, two buttons, botanical art
      #status          .status-box: summary, takeaways tiers, toolbar, legend
      <section id> x16 inside <details class="sec">, a .divider between each pair
    <footer>
    <script>  search, flagged-only, expand/collapse, nav highlight
```

---

## Brand tokens

Defined on `:root` in `brand.css`. Change colours there only.

| Token | Hex | Role |
|-------|-----|------|
| `--ground` | `#121D17` | Page background ("Night fern") |
| `--panel` | `#1E2E25` | Panels, cards, table headers ("Moss shadow") |
| `--ivory` | `#F1E9D6` | Body and data text |
| `--gold` | `#C9A66B` | Mark, rules, links, headings, section titles, active states ("Antique gold") |
| `--garnet` | `#8F2638` | The bloom: buttons, risk badge fill, flagged-row rail. Fill only |
| `--blush` | `#E8C3BC` | Small accents: emphasis in the h1, genotype values, focus ring, ask lines |
| `--sage` | `#A9C4A2` | Derived: "typical" and good-news text and icons |
| `--rose` | `#E58C98` | Derived: "elevated" status text (garnet cannot be text on dark) |
| `--muted` | `#B9B2A0` | Derived: secondary text, labels, timestamps, nav links |
| `--control` | `rgba(201,166,107,.6)` | Derived: borders of the search box and toolbar buttons (>= 3:1) |

The first six are the kit's colours and are fixed. `--sage`, `--rose`, `--muted` and `--control` are **derived extensions** of the kit, added so status can be told apart in text; each text token is at least 4.5:1 on both `--ground` and `--panel`. `--line` and `--line-soft` are ivory at 28% and 12% alpha for hairlines.

### Colour rules

- **Garnet is a fill, never text on dark.** It is used for button and badge backgrounds and a left rail. Risk text uses `--rose`. The checks scan every text element for garnet.
- Status colours always travel with an icon and a word, never colour alone.
- Gold is for structure (rules, headings, links); ivory carries the data.
- Print swaps the tokens to dark ink on white (see Print).

---

## Typography

```html
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Jost:wght@400;500&family=Pinyon+Script&display=swap" rel="stylesheet">
```

| Face | Use | Fallback stack |
|------|-----|----------------|
| Cormorant Garamond 500 (and italic) | Headlines, section titles, subsection titles, hero h1 | `Georgia, "Times New Roman", serif` |
| Jost 400 and 500 | Reading text, labels, tables, buttons, spaced capitals | `system-ui, "Segoe UI", sans-serif` |
| Pinyon Script | The wordmark name only | `"Snell Roundhand", cursive` |

Rules:

- **Pinyon Script for the name only.** It appears in `.wordmark .script` and nowhere else, never in sentences. A check counts the elements that use it.
- **Jost weights 400 and 500 only.** Weight 500 is the emphasis weight (flagged rows, buttons, badges); there is no bold 700.
- Cormorant has a 600 for `.profile-value`; everything else is 500.
- Body is 15px / 1.6; table body 13px; **no text under 12px**. Small caps-style labels (nav, tier titles, table headers) are 12px uppercase with letter spacing.
- Hero h1 is 32px; section titles 26px.

---

## Components (as implemented in `brand.css`)

| Component | Notes |
|-----------|-------|
| Header and wordmark | Fixed, `--ground` with a 1px gold bottom rule. Brand mark (`assets/mark.svg`, "Three of Swords mark", `role="img"`), wordmark = Pinyon name + spaced Cormorant capitals (default "Genome notes", set with `OWNER_NAME`), timestamp. Nav is uppercase 12px, gold underline on hover, `aria-current="true"` on the section in view |
| Hero (`#hero`) | Bordered panel before the summary. Kicker in spaced gold capitals, Cormorant h1 with an italic blush second line, one derived sentence, buttons `.btn-primary` (garnet fill, ivory text, pill, 44px) and `.btn-secondary` (gold outline). Both link to anchors on the page. At most 240px tall at 1280px |
| Botanical art | `.botanical`, `aria-hidden`, absolute at the right of the hero: two leaves (`assets/leaf.svg`) and two hearts (`assets/heart.svg`). A scaled-down version of the kit art (no sword sprays). Narrows under 900px, removed under 640px |
| Status box | `.status-box`: panel with gold border, summary grid and progress strip |
| Takeaway tiers | `.tier` cards (panel, soft gold border, 14px radius): Ask about / act on (3px gold left rule, <= 7 items, each with an ask line in blush), Worth knowing, Good news, Not tested; plus the clinician questions list. Tier titles are 12px spaced Jost capitals |
| Toolbar | Search box and buttons for flagged-only, expand all, collapse all. Gold-alpha borders (`--control`), 44px buttons, `aria-pressed` buttons fill gold |
| Legend | `details.legend`: defines each status word |
| Section panels | `section` in `--panel` with a 40% gold border inside `details.sec`; header on `--ground`, 26px gold Cormorant title with a +/minus marker, evidence pill, section badge. Flagged sections open, clean ones collapsed |
| Tables | Columns Status, What it means, Your result, Marker. Flagged rows are weight 500 with an icon. Under 640px each row becomes a stacked card with `data-label` captions and a garnet left rail on flagged rows |
| Badges | `.section-badge` good (sage on tinted sage), moderate (gold on tinted gold), risk (ivory text on garnet fill); `.ev` evidence pills: Established (sage), Moderate (muted), Weak (gold) |
| Dividers | `.divider` between sections: a gilded 1px line with a small centred sword glyph, a heart on every third; `aria-hidden`; both glyphs come from the one sprite |
| Findings, profile boxes, disclaimers | `.finding` cards with a 3px left rail by level, `.profile-box`, and at most three `.disclaimer` boxes (general in gold; pharma and carrier are `.disclaimer.critical`: 2px garnet border, garnet-tint fill, rose heading). `.profile-value` takes a tone class: `tone-good` sage, `tone-info` blush, `tone-moderate` gold, `tone-high` rose. Inline `style` attributes carry no colour tokens |
| Footer | Panel with gold top rule: provenance and limits |

Motion: transitions on nav, buttons and summaries only when `prefers-reduced-motion: no-preference`; a blanket rule disables animation and transition when reduced motion is requested.

---

## Responsive behaviour

| Width | Behaviour |
|-------|-----------|
| over 900px | Full hero with botanical art, wrapped nav |
| 641 to 900px | Hero right padding 200px, smaller art |
| up to 768px | Tighter gutters, single-column grids, one-row horizontally scrolling nav |
| up to 640px | Hero reduced to the kicker (h1 stays for screen readers, art, sentence and buttons hidden), tables become stacked cards, smaller wordmark that wraps instead of clipping a long `OWNER_NAME` |
| 320px | No horizontal scroll; the longest section title wraps (`overflow-wrap: anywhere`) |

Fixed header height is the `--hh` variable, used for `scroll-padding-top` and the top padding of `main`.

## Accessibility and special modes

- Skip link is the first Tab stop; `:focus-visible` ring in blush; landmarks and `aria-label` on nav.
- Forced colours: panel, pill, badge and button borders switch to `CanvasText`; status text keeps its words and icons.
- If Google Fonts is blocked, the fallback stacks apply and nothing overflows.

## Print

`@media print` swaps the tokens to dark ink on a white page and hides the header, toolbar, skip link, hero (art, text and buttons) and dividers, so page 1 starts with the key takeaways. Rows, tiers and findings do not split across pages; the status box and sections may, because they are taller than a page. Section badges print as a 1px outlined pill in dark ink (the risk badge in `#a00`, about 7.7:1 on white), never as a fill, because browsers drop backgrounds by default. The open-section +/- marker is not printed.

Remaining print caveats: see the "Honest limits" and "Deferred minors" lists in `webpage/DESIGN_REVIEW.md` section 6.

---

## Generating the page and running the checks

```bash
cd scripts && python3 generate_webpage.py          # writes webpage/dna_terminal.html
```

Environment variables: `GENOME_FILE` (input genome), `OUT_FILE` (output path), `OWNER_NAME` (wordmark and title; default "Genome notes").

```bash
NODE_PATH=/opt/node22/lib/node_modules PLAYWRIGHT_CHROMIUM=/path/to/chromium node scripts/check_webpage.js
```

The script needs Playwright and a Chromium binary, is dev-only, and exits non-zero if any check fails. B1 to B5 are the brand checks and R1 to R8 the usability checks; both are described in `webpage/DESIGN_REVIEW.md`.

---

## Sections List (standard set)

| ID | Name | Description |
|----|------|-------------|
| status | STATUS | General info, alerts |
| ancestry | ANCESTRY | Origin, haplogroups |
| health | HEALTH | Disease risks |
| nutrition | NUTRITION | Metabolism, food intolerances |
| sports | SPORTS | Athletic potential |
| psychology | PSYCH | Psychological traits |
| cognitive | COGNITIVE | Cognitive abilities |
| longevity | LONGEVITY | Longevity markers |
| sleep | SLEEP | Sleep, circadian rhythms |
| immunity | IMMUNITY | Immune system |
| pain | PAIN | Pain sensitivity |
| detox | DETOX | Detoxification |
| skin | SKIN | Skin |
| vision | VISION | Vision and hearing |
| traits | TRAITS | Physical traits |
| pharma | PHARMA | Pharmacogenomics |
| carrier | CARRIER | Carrier status |

---

## Design principles

1. **Answer first**: takeaways with a next step before any table.
2. **Quiet luxury, not decoration**: gold line work, one garnet accent, ornament only in the hero and dividers.
3. **Status is never colour alone**: icon, word and weight.
4. **Readable everywhere**: 4.5:1 text, 12px minimum, 320px wide, print and forced colours.
5. **Single file**: no external dependencies except Google Fonts.
6. **Not medical advice**: disclaimers stay on the page.

## Pre-publish checklist

- [ ] `python3 generate_webpage.py` runs without errors
- [ ] `node scripts/check_webpage.js` reports all checks PASS
- [ ] No DNA data or personal name committed (`OWNER_NAME` is optional)
- [ ] Disclaimers present (general, pharma, carrier, footer)
- [ ] Critical findings highlighted: pharma and carrier disclaimers (`.disclaimer.critical`) have a garnet border and rose heading, and high-risk values use rose (`--rose` text, garnet only as a fill or border)
- [ ] Fonts look right on your own machine (Jost, Cormorant Garamond, Pinyon Script)

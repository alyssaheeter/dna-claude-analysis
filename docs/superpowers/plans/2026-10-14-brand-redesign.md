# Brand Redesign of the DNA Page: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle the generated genome page from the green-on-black terminal look to the "Nocturne Hothouse" brand kit (dark hothouse, gilded line, garnet bloom) without losing any of the usability work already shipped.

**Architecture:** Move all CSS out of `scripts/generate_webpage.py` and `webpage/example.html` into one canonical `webpage/brand.css` built on CSS custom properties (the brand tokens). The generator keeps its HTML structure and class names, inlines `brand.css` plus two small SVG assets (mark, leaf), and adds a compact hero. `scripts/check_webpage.js` gains brand-fidelity and resilience checks written before each change; its existing 31 checks must keep passing untouched.

**Tech Stack:** Python 3 (generator), plain CSS/SVG, Google Fonts (Cormorant Garamond, Jost, Pinyon Script), Node + Playwright (checks).

**Spec:** the user request ("aesthetically pleasing, using the attached brand kit as inspo"), the brand kit `Alyssa_Consiglia_brand_kits.pdf` (Kit 01 board, page 2 of 6), and the rubric in `webpage/DESIGN_REVIEW.md` (R1 to R8, still binding).

## Global Constraints

- Kit choice: **01 Nocturne Hothouse** (recommended: the page is dense data, and a dark ground with ivory text keeps long tables comfortable; the other four kits are light). Switching kit later means replacing the token block and the font link only.
- Palette, verbatim from the kit: ground `#121D17`, panels `#1E2E25`, ivory `#F1E9D6`, antique gold `#C9A66B`, garnet `#8F2638`, blush `#E8C3BC`.
- Extra tokens the kit does not define (flagged here as my extension, user to confirm): `--sage #A9C4A2` (typical result), `--rose #E58C98` (high flag), `--muted #B9B2A0` (secondary text). Each must reach 4.5:1 on both `--ground` and `--panel`.
- Type, verbatim from the kit: Cormorant Garamond 500 and italic for headlines and titles; **Pinyon Script for the name only, never sentences**; Jost 400 and 500 for reading text, labels in spaced capitals.
- Garnet is a fill (buttons, the bloom), never a text colour on a dark ground (contrast is about 1.4:1).
- Single HTML file; the only external request allowed is Google Fonts (`fonts.googleapis.com`, `fonts.gstatic.com`) (CLAUDE.md rule 3).
- Webpage text is English (CLAUDE.md rule 4); disclaimers stay (rule 2); red-equivalent for critical findings stays distinct (rule 5).
- Section IDs from CLAUDE.md stay unchanged. The existing checks R1 to R8 (31 checks) pass unchanged, which includes: at 1280×900 at least 3 takeaways, and at 390×844 at least 2, are visible on the first screen. The hero must therefore stay compact.
- CLAUDE.md and `webpage/STYLE_GUIDE.md` currently mandate the terminal look. This plan supersedes that at the user's request; Task 6 updates both, and the user confirms that edit at plan review.
- Decorative art is `aria-hidden`, carries no animation, and never overlaps text.
- Commands run from the repo root; the check command is:
  `NODE_PATH=/opt/node22/lib/node_modules PLAYWRIGHT_CHROMIUM=/opt/pw-browsers/chromium node scripts/check_webpage.js`

## Review Focus

Most likely first. Each line gets a test in the task named.

1. **Google Fonts unreachable or blocked** (offline, privacy extension, this sandbox): the page must stay readable, un-overflowed, and keep the first-screen takeaways, with serif/sans fallbacks. (Task 5)
2. **A different genome** (23andMe format, male, few markers, zero flagged): generation must not crash, the hero and tiers must show sensible empty states, not "0 of 0" or blank boxes. (Task 5)
3. **320px wide with long gene names and serif type**: no horizontal scroll, hero art hidden or clipped without covering text. (Task 2, Task 5)
4. **Print and forced-colors/high-contrast modes**: print stays white and ink-saving; forced colors keeps every status word visible. (Task 5)
5. **Reduced motion**: nothing animates; decorative blinking or drifting art would break the existing guarantee. (Task 4)

## File Structure

| File | Responsibility |
|---|---|
| `webpage/brand.css` (create) | The only stylesheet: tokens, base, components, responsive, print, forced-colors |
| `webpage/assets/mark.svg` (create) | Simplified Three-of-Swords heart mark, `currentColor`-free, brand colours inline |
| `webpage/assets/leaf.svg` (create) | Single monstera-style leaf used for the hero botanical and dividers |
| `scripts/generate_webpage.py` (modify) | Load `brand.css` and SVG assets; hero and wordmark markup; remove the CSS borrowed from `example.html` and the inline `EXTRA_CSS`; env overrides for testing |
| `scripts/check_webpage.js` (modify) | Brand-fidelity checks (B1 to B5) and resilience cases |
| `tests/fixtures/minimal_23andme.txt` (create) | Eight-line 23andMe-format genome for the "different genome" case |
| `CLAUDE.md`, `webpage/STYLE_GUIDE.md`, `webpage/DESIGN_REVIEW.md` (modify) | Document the new look and the brand rubric |
| `webpage/example.html` (leave) | Legacy terminal demo; the generator stops depending on it |

---

### Task 1: Brand tokens, fonts and the single stylesheet

**Files:**
- Create: `webpage/brand.css`
- Modify: `scripts/generate_webpage.py:15-17` (paths), `scripts/generate_webpage.py:557-565` (CSS assembly), `scripts/check_webpage.js`

**Interfaces:**
- Produces: `load_css() -> str` in the generator (returns the contents of `webpage/brand.css`); env overrides `GENOME_FILE`, `OUT_FILE` read at import (defaults unchanged); CSS custom properties `--ground --panel --ivory --gold --garnet --blush --sage --rose --muted`; class names currently emitted by the generator keep working.

- [ ] **Step 1: Write the failing checks** in `scripts/check_webpage.js`, new block `B1`:

```js
// B1 tokens and fonts
const tok = await page.evaluate(() => {
  const s = getComputedStyle(document.documentElement), g = n => s.getPropertyValue(n).trim().toLowerCase();
  return { ground: g('--ground'), panel: g('--panel'), ivory: g('--ivory'), gold: g('--gold'), garnet: g('--garnet'), blush: g('--blush'),
           body: getComputedStyle(document.body).fontFamily, title: getComputedStyle(document.querySelector('.section-title')).fontFamily };
});
check('B1', 'kit 01 palette tokens are exact', tok.ground === '#121d17' && tok.panel === '#1e2e25' && tok.ivory === '#f1e9d6'
  && tok.gold === '#c9a66b' && tok.garnet === '#8f2638' && tok.blush === '#e8c3bc', JSON.stringify(tok));
check('B1', 'body is Jost, titles are Cormorant Garamond', /^"?Jost/.test(tok.body) && /^"?Cormorant Garamond/.test(tok.title), `${tok.body} | ${tok.title}`);
check('B1', 'ground colour is the page background', await page.evaluate(() => getComputedStyle(document.body).backgroundColor) === 'rgb(18, 29, 23)', '');
```
plus a request audit registered before `page.goto`: collect `new URL(req.url()).hostname` for every request and assert each is `''` (file), `fonts.googleapis.com` or `fonts.gstatic.com`.

- [ ] **Step 2: Run the checks to verify B1 fails**
Run: the check command. Expected: the new B1 lines FAIL (tokens empty, body font monospace); the 31 existing checks still PASS.

- [ ] **Step 3: Create `webpage/brand.css` and wire it.** Move every rule now in `EXTRA_CSS` (generator) and every rule the generator takes from `example.html` that a generated class needs, into `brand.css`, expressed through the tokens (`--bg` becomes `--ground`, `--bg-light`/`--bg-section` become `--panel`, `--green` becomes `--gold` for accents and `--ivory` for text, `--amber` becomes `--gold`, `--red` becomes `--rose`, `--cyan` becomes `--blush`, `--gray-light` becomes `--muted`). Set `html{background:var(--ground)}`, `body{font:400 15px/1.6 "Jost", system-ui, "Segoe UI", sans-serif; color:var(--ivory)}`, headings `"Cormorant Garamond", Georgia, "Times New Roman", serif` weight 500. In the generator: add `load_css()`, delete the `STYLE_SRC` read, the font-size regex and `EXTRA_CSS`, replace the font link with `family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Jost:wght@400;500&family=Pinyon+Script&display=swap`, and read `GENOME_FILE`/`OUT_FILE` from `os.environ.get(..., default)`.

- [ ] **Step 4: Regenerate and run all checks**
Run: `cd scripts && python3 generate_webpage.py && cd .. && ` the check command.
Expected: B1 PASS and all 31 existing checks PASS (watch R7 contrast: any failing pair means adjust the token, not the check).

- [ ] **Step 5: Commit**
```bash
git add webpage/brand.css scripts/generate_webpage.py scripts/check_webpage.js
git commit -m "Move styling to brand.css with Nocturne Hothouse tokens and fonts"
```

---

### Task 2: Header, wordmark, hero and brand mark

**Files:**
- Create: `webpage/assets/mark.svg`, `webpage/assets/leaf.svg`
- Modify: `scripts/generate_webpage.py` (header and body assembly), `webpage/brand.css`, `scripts/check_webpage.js`

**Interfaces:**
- Consumes: `load_css()` (Task 1).
- Produces: `inline_svg(name: str) -> str` (reads `webpage/assets/<name>.svg`, strips any XML prolog); `hero(owner: str, flagged: int, ask: int, found: int) -> str`; env `OWNER_NAME` (default `"Genome notes"`; first word renders in script, the rest in spaced capitals). Elements: `#hero`, `svg[data-brand="mark"]` (`role="img"`, `aria-label="Three of Swords mark"`), `.wordmark .script`, `.btn-primary`, `.btn-secondary`, `.botanical`.

- [ ] **Step 1: Write the failing checks**, block `B2`:

```js
check('B2', 'hero precedes the summary and stays compact', h.heroBeforeStatus && h.heroHeight <= 240, `${h.heroHeight}px`);        // 1280px viewport
check('B2', 'brand mark is an accessible image', h.mark === 'img' && h.markLabel === 'Three of Swords mark', '');
check('B2', 'Pinyon Script is used only by the wordmark name', h.pinyonCount === h.scriptCount && h.scriptCount >= 1, `${h.pinyonCount}/${h.scriptCount}`);
check('B2', 'primary button is garnet with ivory text, 44px tall', h.btnBg === 'rgb(143, 38, 56)' && h.btnColor === 'rgb(241, 233, 214)' && h.btnH >= 44, JSON.stringify(h));
check('B2', 'botanical art hidden and aria-hidden at 390px', m.botanicalDisplay === 'none' && h.botanicalAria === 'true', '');
check('B2', 'no horizontal scroll at 320px with the hero', m320.sw <= m320.iw, '');
```
Counting rule: `pinyonCount` = elements whose computed `font-family` starts with `"Pinyon Script"`, `scriptCount` = elements matching `.wordmark .script`.

- [ ] **Step 2: Run the checks to verify B2 fails**
Run: the check command. Expected: B2 FAIL (`#hero` missing); everything else PASS.

- [ ] **Step 3: Implement.** Author `mark.svg` (viewBox 0 0 120 140: three crossed swords in `--gold` strokes over a garnet heart, as in kit 01; no raster, no text) and `leaf.svg` (moss `--panel` leaf with ground-colour veins). Implement `inline_svg(name)` and `hero(owner, flagged, ask, found)`: kicker in gold spaced capitals (`GENOME NOTES · THE SHORT VERSION`), headline in Cormorant 500 with the second line italic in `--blush` (`What your DNA can, and can't, tell you.`), one Jost sentence built from the counts with zero-safe wording (when `found == 0` it says no markers were readable), buttons `See key takeaways` (`#status`, garnet fill) and `Questions for my clinician` (`#questions`, gold outline). Header: inline mark (28px) + wordmark; nav in Jost spaced capitals with a gold underline for `aria-current`. At `max-width: 640px` the hero drops the sentence, the buttons and the botanical so the takeaways keep the first screen.

- [ ] **Step 4: Regenerate and run all checks**
Expected: B1, B2 and the 31 existing checks PASS. Open screenshots at 1280, 390 and 320px and compare with the hero in the kit board.

- [ ] **Step 5: Commit**
```bash
git add webpage/assets scripts/generate_webpage.py webpage/brand.css scripts/check_webpage.js
git commit -m "Add brand header, wordmark, hero and mark"
```

---

### Task 3: Takeaways, tables, badges and status colours

**Files:** Modify `webpage/brand.css`, `scripts/check_webpage.js` (generator markup unchanged unless a class is missing).

**Interfaces:**
- Consumes: tokens (Task 1). Produces: status classes `.status-normal` (sage), `.status-info` (blush), `.status-moderate` (gold), `.status-risk` (rose), `.status-na` (muted).

- [ ] **Step 1: Write the failing checks**, block `B3`:

```js
check('B3', 'status tokens meet 4.5:1 on ground and panel', ['--sage','--rose','--muted','--gold','--blush'].every(t => ratio(tokenRGB(t), GROUND) >= 4.5 && ratio(tokenRGB(t), PANEL) >= 4.5), '');
check('B3', 'garnet is never used as text on a dark ground', garnetTextOnDark.length === 0, garnetTextOnDark.join(', '));
check('B3', 'top tier has a gold rule and ivory headings', h.askBorder === 'rgb(201, 166, 107)' && h.askTitleFont.startsWith('"Cormorant'), '');
check('B3', 'flagged rows keep weight 700 and an icon (R6 still holds)', h.flagBold >= 700 && h.flagIcon, '');
```
where `ratio`, `tokenRGB`, `GROUND`, `PANEL` are small helpers added to the script (WCAG relative luminance, the same formula the R7 check already uses).

- [ ] **Step 2: Run the checks to verify B3 fails**
Expected: B3 FAIL on the status colours and the ask-tier rule; others PASS.

- [ ] **Step 3: Implement** in `brand.css`: tiers as panels (`--panel`, 1px gold border at 35% alpha, 14px radius), tier titles Jost spaced capitals in gold, tier-ask left rule 3px gold, follow-up lines (`.tk-act`) in `--blush`, tables on `--panel` with hairline `--gold`-alpha row rules, headers Jost 12px spaced capitals in `--muted`, markers in `--muted`, genotype in `--blush` weight 500, evidence badges as outlined pills (established sage, moderate muted, weak gold), section badges as filled pills (good sage-on-dark, moderate gold-on-dark, risk rose-on-dark) with visible text colour not colour alone. Define `--sage`, `--rose`, `--muted` here.

- [ ] **Step 4: Run all checks**
Expected: B1 to B3 and the 31 existing PASS. Contrast failures are fixed by adjusting the derived tokens only.

- [ ] **Step 5: Commit**
```bash
git add webpage/brand.css scripts/check_webpage.js
git commit -m "Style takeaways, tables and badges with the brand palette"
```

---

### Task 4: Section panels, dividers, pattern and motion

**Files:** Modify `scripts/generate_webpage.py` (divider markup between sections, SVG sprite once in `<body>`), `webpage/brand.css`, `scripts/check_webpage.js`.

**Interfaces:** Produces `.divider` (decorative, `aria-hidden="true"`) and one `<svg style="display:none">` sprite defining `#sword` and `#heart`.

- [ ] **Step 1: Write the failing checks**, block `B4` (test names and assertions):

```js
check('B4', 'one divider between each pair of sections, all aria-hidden', d.dividers === d.secs - 1 && d.dividersHidden, `${d.dividers}`);
check('B4', 'sprite symbols defined exactly once', d.swordDefs === 1 && d.heartDefs === 1, '');
await page.emulateMedia({ reducedMotion: 'reduce' });
check('B4', 'reduced motion: no element has an animation', await page.evaluate(() => [...document.querySelectorAll('*')].every(e => getComputedStyle(e).animationName === 'none')), '');
check('B4', 'section panels use panel colour with a gold-alpha border', d.secBg === 'rgb(30, 46, 37)' && /rgba\(201, 166, 107/.test(d.secBorder), JSON.stringify(d));
```

- [ ] **Step 2: Run to verify B4 fails**
Expected: B4 FAIL; earlier blocks PASS.

- [ ] **Step 3: Implement.** Divider = thin gold rule with a small centred sword/heart from the sprite (the kit's pattern, used sparingly: dividers only, no full-page tiling). Section headings Cormorant 500 at 26px, summary bar keeps its `+`/`−` marker in gold. Footer in `--panel` with a gold top rule. All motion off: remove the logo blink; hover transitions colour-only, wrapped in `prefers-reduced-motion: no-preference`.

- [ ] **Step 4: Run all checks and regenerate screenshots**
Expected: B1 to B4 and all 31 existing PASS.

- [ ] **Step 5: Commit**
```bash
git add scripts/generate_webpage.py webpage/brand.css scripts/check_webpage.js
git commit -m "Add section panels, gilded dividers and motion rules"
```

---

### Task 5: Resilience (fonts blocked, different genome, forced colours, print)

**Files:**
- Create: `tests/fixtures/minimal_23andme.txt`
- Modify: `scripts/check_webpage.js`, `webpage/brand.css`, `scripts/generate_webpage.py` (empty-state wording only)

**Interfaces:** Consumes the generator env overrides `GENOME_FILE`, `OUT_FILE` (Task 1). The check script gains `generateWith(genome, out)` which runs `python3 scripts/generate_webpage.py` with those env vars and returns the output path.

- [ ] **Step 1: Write the fixture and the failing checks**, block `B5`. Fixture (tab-separated, 23andMe format, a male, one common marker):

```
# 23andMe raw data
# rsid	chromosome	position	genotype
rs1815739	11	66560624	CC
rs12913832	15	28365618	AA
rs4680	22	19963748	AA
rs3094315	24	1	A
rs3131972	24	2	G
```
Checks:

```js
// fonts blocked
await ctx.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
check('B5', 'fonts blocked: no horizontal scroll at 320px and takeaways still on the first screen', sw <= iw && visibleTop >= 1, '');
check('B5', 'fonts blocked: body falls back to a sans stack and titles to a serif stack', /sans-serif$/.test(body) && /serif$/.test(title), '');
// different genome
const out = generateWith('tests/fixtures/minimal_23andme.txt', '/tmp/brand_fixture.html');
check('B5', 'minimal 23andMe genome generates a page', fs.existsSync(out), '');
check('B5', 'fixture page: no "0 of 0", hero and tiers show empty-state wording', !/\b0 of 0\b/.test(text) && /no flagged markers|No other flagged markers|none of the displayed markers/i.test(text), '');
// forced colours and print
await page.emulateMedia({ forcedColors: 'active' });
check('B5', 'forced colours: every status keeps visible text', statusTexts.every(t => t.length > 3), '');
await page.emulateMedia({ media: 'print' });
check('B5', 'print: white page, dark ink', bg === 'rgb(255, 255, 255)' && inkLum < 0.2, '');
```

- [ ] **Step 2: Run to verify B5 fails**
Expected: at least the fixture and print checks FAIL (print currently inherits dark tokens, empty-state copy unverified).

- [ ] **Step 3: Implement** fixes the failures name: in `brand.css` set the print block to override the tokens to ink on white (`--ground`, `--panel` white; `--ivory`, `--gold`, `--sage`, `--rose`, `--muted` dark equivalents that keep 4.5:1 on white); add `@media (forced-colors: active)` with `border-color: CanvasText` on panels and pills; set explicit fallback stacks. In the generator, ensure the hero sentence and the tier empty states read sensibly when `found == 0` or `n_flag_rows == 0` (e.g. "None of the displayed markers differ from the typical result.").

- [ ] **Step 4: Run all checks**
Expected: B1 to B5 and the 31 existing PASS.

- [ ] **Step 5: Commit**
```bash
git add tests/fixtures scripts webpage/brand.css
git commit -m "Harden brand styling: font fallback, other genomes, forced colours, print"
```

---

### Task 6: Documentation, visual review and PR

**Files:** Modify `CLAUDE.md` ("Webpage Generation" section and the Overview line), `webpage/STYLE_GUIDE.md`, `webpage/DESIGN_REVIEW.md`.

- [ ] **Step 1: Update docs.** CLAUDE.md: replace "terminal aesthetic: JetBrains Mono, green-on-black" with "brand aesthetic: Nocturne Hothouse (see `webpage/brand.css`)", keep the section-ID table, rules and file locations, add `webpage/brand.css` and `webpage/assets/` to the file table. STYLE_GUIDE.md: replace the palette, typography and component sections with the token table, type pairing, component list from `brand.css`, and the "Pinyon for the name only" and "garnet is never text on dark" rules. DESIGN_REVIEW.md: add section 6, the brand rubric B1 to B5 (what each measures) and the final results.

- [ ] **Step 2: Visual review.** Run `cd scripts && python3 generate_webpage.py`, take screenshots at 1280×900, 390×844 and 320×844 plus a print PDF page, and compare with the kit board for palette, type pairing and the hero. Record in DESIGN_REVIEW.md that real-font rendering could not be verified in the sandbox if the fonts were blocked there; the user confirms it on their own machine.

- [ ] **Step 3: Full verification**
Run: the check command, and `cd scripts && for f in *_analysis.py; do python3 "$f" >/dev/null || echo FAIL $f; done`.
Expected: every check PASS, no FAIL lines, exit 0.

- [ ] **Step 4: Commit and push**
```bash
git add CLAUDE.md webpage docs
git commit -m "Document the brand redesign and record results"
git push -u origin claude/upbeat-sagan-l9s9vb
```

- [ ] **Step 5: Open or update the draft PR** with a summary of the look, the derived tokens (`--sage`, `--rose`, `--muted`) and the unverified-fonts note.

---

## Self-Review

- **Spec coverage:** brand kit palette and type pairing (Task 1), mark, wordmark, hero with botanical and buttons as in the kit's website board (Task 2), pattern and gilded line (Task 4), colour-use rules (Task 3), all existing usability guarantees preserved (Global Constraints, checks re-run each task), docs (Task 6). Gap noted, not planned: the kit's business cards, social avatar and envelope pattern are out of scope for a web page.
- **Step scan:** each test step names its assertions; each implement step names files, selectors, tokens and values; no step is "style it nicely".
- **Type consistency:** `load_css`, `inline_svg`, `hero`, env names `GENOME_FILE`, `OUT_FILE`, `OWNER_NAME` and the class names (`#hero`, `.wordmark .script`, `.btn-primary`, `.btn-secondary`, `.botanical`, `.divider`) are used identically in Tasks 1 to 6.
- **Review Focus:** all five items have a test (fonts blocked, fixture genome, 320px, print and forced colours, reduced motion).
- **Proportion:** the plan is a set of decisions and tests; CSS bodies are described by token mapping and values, not written out.

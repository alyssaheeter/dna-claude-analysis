#!/usr/bin/env node
/* Measures webpage/dna_terminal.html against the rubric in webpage/DESIGN_REVIEW.md.
 * Dev-only check. Requires Playwright (npm i -g playwright) and a Chromium binary:
 *   PLAYWRIGHT_CHROMIUM=/path/to/chromium node scripts/check_webpage.js
 * Exits non-zero if any check fails.
 */
const path = require('path');
const fs = require('fs');
const { execFileSync } = require('child_process');
let chromium;
try { ({ chromium } = require('playwright')); }
catch (e) { ({ chromium } = require(path.join(process.env.NODE_PATH || '/opt/node22/lib/node_modules', 'playwright'))); }

const FILE = 'file://' + path.resolve(__dirname, '../webpage/dna_terminal.html');
const ROOT = path.resolve(__dirname, '..');
function generateWith(genome, out) {
  execFileSync('python3', ['scripts/generate_webpage.py'], { cwd: ROOT, stdio: 'pipe',
    env: Object.assign({}, process.env, { GENOME_FILE: path.resolve(ROOT, genome), OUT_FILE: out }) });
  return out;
}
const results = [];
const check = (id, name, ok, detail) => results.push({ id, name, ok, detail });

async function main() {
  const browser = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_CHROMIUM || undefined, args: ['--no-sandbox'] });

  // ---------- B1 request audit: only file:// and Google Fonts hosts
  const hosts = new Set();
  const auditPage = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  auditPage.on('request', req => { try { hosts.add(new URL(req.url()).hostname); } catch (e) { hosts.add(req.url()); } });
  await auditPage.goto(FILE);
  await auditPage.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
  const badHosts = [...hosts].filter(h => !['', 'fonts.googleapis.com', 'fonts.gstatic.com'].includes(h));
  check('B1', 'requests only go to file or Google Fonts hosts', badHosts.length === 0, badHosts.join(', ') || [...hosts].join(','));
  await auditPage.close();

  // ---------- R8 responsive: no horizontal scroll, header never covers content
  for (const w of [1280, 390, 320]) {
    const page = await browser.newPage({ viewport: { width: w, height: 844 } });
    await page.goto(FILE); await page.waitForTimeout(400);
    const m = await page.evaluate(() => {
      const hdr = document.querySelector('header').getBoundingClientRect();
      const first = document.querySelector('.status-box').getBoundingClientRect();
      const wide = [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > innerWidth + 1 && !e.closest('nav'))
        .slice(0, 3).map(e => e.tagName + '.' + e.className);
      return { sw: document.documentElement.scrollWidth, iw: innerWidth, hdrBottom: hdr.bottom, firstTop: first.top + scrollY, wide,
               hdrH: hdr.height };
    });
    check('R8', `no horizontal scroll at ${w}px`, m.sw <= m.iw, `scrollWidth ${m.sw} vs ${m.iw} ${m.wide.join(',')}`);
    check('R8', `fixed header (${Math.round(m.hdrH)}px) does not cover first content at ${w}px`, m.firstTop >= m.hdrBottom, `content top ${Math.round(m.firstTop)} vs header bottom ${Math.round(m.hdrBottom)}`);
    if (w === 390) {
      const fits = await page.evaluate(() => {
        const t = document.querySelector('.tier-ask'); const r = t.getBoundingClientRect();
        const items = [...t.querySelectorAll('li.tk')].filter(l => l.getBoundingClientRect().bottom <= innerHeight);
        return items.length;
      });
      check('R1', 'at 390x844 at least 2 top-tier takeaways are visible on the first screen', fits >= 2, `${fits} visible`);
      const tbl = await page.evaluate(() => { const tr = document.querySelector('tr.r'); return getComputedStyle(tr).display; });
      check('R8', 'tables become stacked cards on mobile', tbl === 'block', `tr display=${tbl}`);
    }
    if (w === 1280) {
      const fits = await page.evaluate(() => [...document.querySelectorAll('.tier-ask li.tk')].filter(l => l.getBoundingClientRect().bottom <= innerHeight).length);
      check('R1', 'at 1280x900 at least 3 top-tier takeaways are visible on the first screen', fits >= 3, `${fits} visible`);
    }
    await page.close();
  }

  // ---------- desktop page checks
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await page.goto(FILE); await page.waitForTimeout(400);
  await page.evaluate(() => document.querySelectorAll('details').forEach(d => d.open = true));

  const d = await page.evaluate(() => {
    const lum = ([r, g, b]) => { const f = c => { c /= 255; return c <= .03928 ? c / 12.92 : Math.pow((c + .055) / 1.055, 2.4); }; return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); };
    const parse = s => { const m = s.match(/[\d.]+/g).map(Number); return { r: m[0], g: m[1], b: m[2], a: m[3] === undefined ? 1 : m[3] }; };
    const bgOf = el => {
      const layers = [];
      for (let e = el; e; e = e.parentElement) { const c = parse(getComputedStyle(e).backgroundColor); if (c.a > 0) { layers.push(c); if (c.a >= .99) break; } }
      let base = { r: 10, g: 10, b: 10 };
      layers.reverse().forEach(c => { base = { r: c.r * c.a + base.r * (1 - c.a), g: c.g * c.a + base.g * (1 - c.a), b: c.b * c.a + base.b * (1 - c.a) }; });
      return [base.r, base.g, base.b];
    };
    const fails = [], small = []; const seen = new Set();
    document.querySelectorAll('body *').forEach(el => {
      if (el.closest('thead') && getComputedStyle(el).position === 'absolute') return;
      const txt = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
      if (!txt) return;
      const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') return;
      if (el.closest('.sr, .skip') ) return;
      const fs = parseFloat(cs.fontSize);
      if (fs < 12) small.push(el.tagName + '.' + el.className + ' ' + fs);
      const c = parse(cs.color);
      const bg = bgOf(el); const L1 = lum([c.r, c.g, c.b]), L2 = lum(bg);
      const ratio = (Math.max(L1, L2) + .05) / (Math.min(L1, L2) + .05);
      const key = el.tagName + '.' + el.className + cs.color;
      if (ratio < 4.5 && !seen.has(key)) { seen.add(key); fails.push(`${key} ${ratio.toFixed(2)}`); }
    });
    const bodyFs = parseFloat(getComputedStyle(document.querySelector('td.c-mean')).fontSize);
    const ask = [...document.querySelectorAll('.tier-ask li.tk')];
    const genes = ask.map(l => l.querySelector('strong').textContent);
    const secs = [...document.querySelectorAll('section[id]')];
    const rows = [...document.querySelectorAll('tr.r')];
    return {
      fails, small, bodyFs,
      askN: ask.length, askGenes: genes, askAllAct: ask.every(l => l.querySelector('.tk-act')),
      secs: secs.length, dividers: document.querySelectorAll('.divider').length,
      dividersHidden: [...document.querySelectorAll('.divider')].every(x => x.getAttribute('aria-hidden') === 'true'),
      swordDefs: document.querySelectorAll('symbol#sword').length, heartDefs: document.querySelectorAll('symbol#heart').length,
      secBg: getComputedStyle(secs[0]).backgroundColor, secBorder: getComputedStyle(secs[0]).borderTopColor,
      titleFs: getComputedStyle(document.querySelector('.section-title')).fontSize,
      evs: document.querySelectorAll('section[id] .ev').length,
      disclaimers: document.querySelectorAll('.disclaimer').length,
      legend: !!document.querySelector('details.legend'),
      rowsWithIcon: rows.filter(r => r.querySelector('.st [aria-hidden="true"]') && r.querySelector('.st').textContent.trim().length > 3).length,
      rows: rows.length,
      skip: !!document.querySelector('a.skip'), navLabel: !!document.querySelector('nav[aria-label]'), main: !!document.querySelector('main'),
      h1h2: document.querySelectorAll('h2').length,
      firstMean: [...document.querySelectorAll('tr.r')][0].children[1].className,
      headers: [...document.querySelectorAll('thead th')].slice(0, 4).map(t => t.textContent),
      printCss: [...document.styleSheets].filter(s => !s.href).some(s => [...s.cssRules].some(r => r.media && r.media.mediaText.includes('print'))),
      reduceCss: [...document.styleSheets].filter(s => !s.href).some(s => [...s.cssRules].some(r => r.media && r.media.mediaText.includes('reduced-motion'))),
      focusCss: [...document.styleSheets].filter(s => !s.href).some(s => [...s.cssRules].some(r => r.selectorText && r.selectorText.includes(':focus-visible'))),
      flaggedBold: getComputedStyle(document.querySelector('tr.flag td.c-mean')).fontWeight,
      typicalBold: getComputedStyle(document.querySelector('tr.r:not(.flag) td.c-mean')).fontWeight,
      flaggedIcon: !!document.querySelector('tr.flag .st [aria-hidden]'),
    };
  });

  check('R1', 'top tier has 1-7 items', d.askN >= 1 && d.askN <= 7, `${d.askN} items`);
  check('R1', 'no gene repeated in the top tier', new Set(d.askGenes).size === d.askGenes.length, d.askGenes.join(', '));
  check('R2', 'every top-tier item has an ask/do line', d.askAllAct, '');
  const acts = await page.evaluate(() => [...document.querySelectorAll('.tk-act, .questions li')].map(e => e.textContent));
  const forbidden = acts.filter(a => /\b(mg|diagnos\w*|stop taking|start taking|you (have|are) (a |an )?[a-z ]*(disease|disorder|syndrome|diabetic))\b/i.test(a));
  check('R2', 'no diagnosis or dose phrasing in follow-up text; clinician question list present', forbidden.length === 0 && acts.length >= 2 * d.askN, forbidden.join(' | ') || `${acts.length} lines`);
  check('R3', 'table leads with the plain-English meaning column', d.headers[0] === 'Status' && d.headers[1] === 'What it means' && d.headers[3] === 'Marker', d.headers.join(' | '));
  check('R3', 'status legend present', d.legend, '');
  check('R3', 'every row has status icon + word', d.rowsWithIcon === d.rows, `${d.rowsWithIcon}/${d.rows}`);
  check('R4', 'one evidence badge per section', d.evs === d.secs && d.secs >= 16, `${d.evs} badges / ${d.secs} sections`);
  check('R4', 'at most 3 disclaimer boxes (1 general + pharma + carrier)', d.disclaimers <= 3, `${d.disclaimers}`);
  check('R6', 'flagged rows are emphasised by weight and an icon (not colour alone)', Number(d.flaggedBold) >= 500 && Number(d.flaggedBold) > Number(d.typicalBold) && d.flaggedIcon, `flagged ${d.flaggedBold} vs typical ${d.typicalBold}`);
  check('R7', 'all visible text meets 4.5:1 contrast', d.fails.length === 0, d.fails.slice(0, 6).join('; '));
  check('R7', 'no text under 12px', d.small.length === 0, d.small.slice(0, 4).join('; '));
  check('R7', 'table body text >= 13px', d.bodyFs >= 13, `${d.bodyFs}px`);
  check('R7', 'skip link, nav label, main landmark', d.skip && d.navLabel && d.main, '');
  check('R7', ':focus-visible and reduced-motion rules present', d.focusCss && d.reduceCss, '');
  check('R8', 'print stylesheet present', d.printCss, '');

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

  // B1 derived-token and control contrast
  const cc = await page.evaluate(() => {
    const lum = ([r, g, b]) => { const f = c => { c /= 255; return c <= .03928 ? c / 12.92 : Math.pow((c + .055) / 1.055, 2.4); }; return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); };
    const ratio = (a, b) => (Math.max(lum(a), lum(b)) + .05) / (Math.min(lum(a), lum(b)) + .05);
    const hex = h => { h = h.trim().replace('#', ''); return [0, 2, 4].map(i => parseInt(h.substr(i, 2), 16)); };
    const root = getComputedStyle(document.documentElement), tk = n => hex(root.getPropertyValue(n));
    const rgba = s => s.match(/[\d.]+/g).map(Number);
    const ground = tk('--ground'), out = {};
    for (const t of ['--sage', '--rose', '--muted']) out[t] = [ratio(tk(t), ground), ratio(tk(t), tk('--panel'))];
    const ctl = {};
    for (const sel of ['.toolbar input', '.toolbar button']) {
      const c = rgba(getComputedStyle(document.querySelector(sel)).borderTopColor), a = c[3] === undefined ? 1 : c[3];
      ctl[sel] = ratio([0, 1, 2].map(i => c[i] * a + ground[i] * (1 - a)), ground);
    }
    return { out, ctl };
  });
  const tokBad = Object.entries(cc.out).filter(([, v]) => v[0] < 4.5 || v[1] < 4.5).map(([k, v]) => `${k} ${v.map(x => x.toFixed(2))}`);
  check('B1', '--sage, --rose, --muted reach 4.5:1 on --ground and --panel', tokBad.length === 0, tokBad.join('; ') || JSON.stringify(cc.out));
  const ctlBad = Object.entries(cc.ctl).filter(([, v]) => v < 3);
  check('B1', 'toolbar input and button borders reach 3:1 against --ground', ctlBad.length === 0, JSON.stringify(cc.ctl));

  // B2 header, hero and brand mark
  const h = await page.evaluate(() => {
    const hero = document.querySelector('#hero'), st = document.querySelector('#status');
    const mark = document.querySelector('svg[data-brand="mark"][role="img"]');
    const btn = document.querySelector('.btn-primary');
    const bcs = btn && getComputedStyle(btn);
    const all = [...document.querySelectorAll('body *')];
    return {
      heroBeforeStatus: !!hero && !!st && !!(hero.compareDocumentPosition(st) & Node.DOCUMENT_POSITION_FOLLOWING),
      heroHeight: hero ? Math.round(hero.getBoundingClientRect().height) : 9999,
      mark: mark ? mark.getAttribute('role') : null, markLabel: mark ? mark.getAttribute('aria-label') : null,
      pinyonCount: all.filter(e => getComputedStyle(e).fontFamily.startsWith('"Pinyon Script"')).length,
      scriptCount: document.querySelectorAll('.wordmark .script').length,
      btnBg: bcs ? bcs.backgroundColor : null, btnColor: bcs ? bcs.color : null, btnH: btn ? btn.getBoundingClientRect().height : 0,
      botanicalAria: document.querySelector('.botanical') ? document.querySelector('.botanical').getAttribute('aria-hidden') : null,
    };
  });
  check('B2', 'hero precedes the summary and stays compact', h.heroBeforeStatus && h.heroHeight <= 240, `${h.heroHeight}px`);
  check('B2', 'brand mark is an accessible image', h.mark === 'img' && h.markLabel === 'Three of Swords mark', '');
  check('B2', 'Pinyon Script is used only by the wordmark name', h.pinyonCount === h.scriptCount && h.scriptCount >= 1, `${h.pinyonCount}/${h.scriptCount}`);
  check('B2', 'primary button is garnet with ivory text, 44px tall', h.btnBg === 'rgb(143, 38, 56)' && h.btnColor === 'rgb(241, 233, 214)' && h.btnH >= 44, JSON.stringify(h));
  const hb = await page.evaluate(() => [...document.querySelectorAll('#hero a[href^="#"]')].map(a => ({ href: a.getAttribute('href'), ok: !!document.querySelector(a.getAttribute('href')) })));
  check('B2', 'hero links all resolve to an element', hb.length >= 1 && hb.every(x => x.ok), JSON.stringify(hb));
  const mob = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await mob.goto(FILE); await mob.waitForTimeout(300);
  const m = await mob.evaluate(() => { const b = document.querySelector('.botanical'); return { botanicalDisplay: b ? getComputedStyle(b).display : null }; });
  await mob.close();
  check('B2', 'botanical art hidden and aria-hidden at 390px', m.botanicalDisplay === 'none' && h.botanicalAria === 'true', '');
  const p320 = await browser.newPage({ viewport: { width: 320, height: 844 } });
  await p320.goto(FILE); await p320.waitForTimeout(300);
  const m320 = await p320.evaluate(() => ({ sw: document.documentElement.scrollWidth, iw: innerWidth }));
  await p320.close();
  check('B2', 'no horizontal scroll at 320px with the hero', m320.sw <= m320.iw, '');

  // ---------- B3 takeaways, tables, badges and status colours
  const lumN = ([r, g, b]) => { const f = c => { c /= 255; return c <= .03928 ? c / 12.92 : Math.pow((c + .055) / 1.055, 2.4); }; return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); };
  const ratio = (a, b) => (Math.max(lumN(a), lumN(b)) + .05) / (Math.min(lumN(a), lumN(b)) + .05);
  const tokVals = await page.evaluate(() => { const s = getComputedStyle(document.documentElement); const o = {}; for (const t of ['--ground', '--panel', '--sage', '--rose', '--muted', '--gold', '--blush']) o[t] = s.getPropertyValue(t).trim(); return o; });
  const tokenRGB = t => { const h = tokVals[t].replace('#', ''); return [0, 2, 4].map(i => parseInt(h.substr(i, 2), 16)); };
  const GROUND = tokenRGB('--ground'), PANEL = tokenRGB('--panel');
  const b3 = await page.evaluate(() => {
    const parse = s => { const m = s.match(/[\d.]+/g).map(Number); return { r: m[0], g: m[1], b: m[2], a: m[3] === undefined ? 1 : m[3] }; };
    const lum = ([r, g, b]) => { const f = c => { c /= 255; return c <= .03928 ? c / 12.92 : Math.pow((c + .055) / 1.055, 2.4); }; return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); };
    const bgOf = el => {
      const layers = [];
      for (let e = el; e; e = e.parentElement) { const c = parse(getComputedStyle(e).backgroundColor); if (c.a > 0) { layers.push(c); if (c.a >= .99) break; } }
      let base = { r: 18, g: 29, b: 23 };
      layers.reverse().forEach(c => { base = { r: c.r * c.a + base.r * (1 - c.a), g: c.g * c.a + base.g * (1 - c.a), b: c.b * c.a + base.b * (1 - c.a) }; });
      return [base.r, base.g, base.b];
    };
    const garnetText = []; let scanned = 0;
    document.querySelectorAll('body *').forEach(el => {
      if (![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) return;
      const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') return;
      scanned++;
      const c = parse(cs.color);
      if (c.r === 143 && c.g === 38 && c.b === 56 && lum(bgOf(el)) < 0.2) garnetText.push(el.tagName + '.' + el.className);
    });
    const ask = document.querySelector('.tier-ask'), at = document.querySelector('.tier-ask .tier-title');
    return {
      garnetText, scanned, askBorder: getComputedStyle(ask).borderLeftColor, askBorderW: getComputedStyle(ask).borderLeftWidth,
      askTitleFont: getComputedStyle(at).fontFamily, askTitleLs: parseFloat(getComputedStyle(at).letterSpacing) || 0,
    };
  });
  check('B3', 'status tokens meet 4.5:1 on ground and panel', ['--sage', '--rose', '--muted', '--gold', '--blush'].every(t => ratio(tokenRGB(t), GROUND) >= 4.5 && ratio(tokenRGB(t), PANEL) >= 4.5), '');
  check('B3', 'garnet is never used as text on a dark ground', b3.scanned > 50 && b3.garnetText.length === 0, b3.garnetText.join(', ') || `${b3.scanned} text elements scanned`);
  check('B3', 'top tier has a 3px gold rule and spaced Jost capitals title', b3.askBorder === 'rgb(201, 166, 107)' && b3.askBorderW === '3px' && /^"?Jost/.test(b3.askTitleFont) && b3.askTitleLs > 0, `${b3.askBorder} ${b3.askBorderW} ${b3.askTitleFont} ls=${b3.askTitleLs}`);
  check('B3', 'flagged rows keep weight 500 over typical 400 and an icon (R6 still holds)', Number(d.flaggedBold) === 500 && Number(d.typicalBold) === 400 && d.flaggedIcon, `${d.flaggedBold}/${d.typicalBold}`);

  // ---------- B4 section panels, dividers, motion
  check('B4', 'one divider between each pair of sections, all aria-hidden', d.dividers === d.secs - 1 && d.dividersHidden, `${d.dividers}`);
  check('B4', 'sprite symbols defined exactly once', d.swordDefs === 1 && d.heartDefs === 1, `${d.swordDefs}/${d.heartDefs}`);
  check('B4', 'section panels use panel colour with a gold-alpha border', d.secBg === 'rgb(30, 46, 37)' && /rgba\(201, 166, 107/.test(d.secBorder), JSON.stringify({ bg: d.secBg, border: d.secBorder }));
  check('B4', 'section headings are 26px', d.titleFs === '26px', d.titleFs);
  const rm = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await rm.emulateMedia({ reducedMotion: 'reduce' });
  await rm.goto(FILE); await rm.waitForTimeout(300);
  check('B4', 'reduced motion: no element has an animation', await rm.evaluate(() => [...document.querySelectorAll('*')].every(e => getComputedStyle(e).animationName === 'none')), '');
  await rm.close();

  // keyboard: first Tab reaches the skip link
  await page.keyboard.press('Tab');
  const tabbed = await page.evaluate(() => document.activeElement.className);
  check('R7', 'first Tab stop is the skip link', tabbed === 'skip', tabbed);

  // ---------- R5 interaction
  const total = d.rows;
  await page.fill('#q', 'cyp2c19'); await page.waitForTimeout(100);
  const s1 = await page.evaluate(() => document.querySelectorAll('tr.r:not([hidden])').length);
  check('R5', 'search narrows the rows', s1 > 0 && s1 < total, `${s1} of ${total}`);
  await page.fill('#q', ''); await page.click('#flagonly'); await page.waitForTimeout(100);
  const s2 = await page.evaluate(() => ({ shown: [...document.querySelectorAll('tr.r:not([hidden])')], pressed: document.getElementById('flagonly').getAttribute('aria-pressed') }));
  const nonFlag = await page.evaluate(() => [...document.querySelectorAll('tr.r:not([hidden])')].filter(r => !r.classList.contains('flag')).length);
  check('R5', 'flagged-only hides every non-flagged row', nonFlag === 0 && s2.pressed === 'true', `${nonFlag} non-flagged visible`);
  await page.click('#flagonly'); await page.click('#collapseall');
  const openN = await page.evaluate(() => document.querySelectorAll('details.sec[open]').length);
  check('R5', 'collapse all works', openN === 0, `${openN} open`);
  await page.click('nav a[href="#pharma"]'); await page.waitForTimeout(700);
  const ph = await page.evaluate(() => ({ open: document.querySelector('#pharma details').open, cur: document.querySelector('nav a[aria-current="true"]')?.textContent, top: document.querySelector('#pharma').getBoundingClientRect().top, hdr: document.querySelector('header').getBoundingClientRect().bottom }));
  check('R5', 'nav jump opens the section, marks it current, and lands below the header', ph.open && ph.cur === 'PHARMA' && ph.top >= ph.hdr - 2, JSON.stringify(ph));
  const xref = await page.evaluate(() => document.querySelectorAll('.xref').length);
  check('R5', 'repeated markers carry an "also in" cross-reference', xref > 0, `${xref}`);

  // ---------- B5 resilience
  const lumB = ([r, g, b]) => { const f = c => { c /= 255; return c <= .03928 ? c / 12.92 : Math.pow((c + .055) / 1.055, 2.4); }; return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); };
  // fonts blocked
  {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
    let aborted = 0;
    await ctx.route(/fonts\.(googleapis|gstatic)\.com/, r => { aborted++; return r.abort(); });
    const pg = await ctx.newPage();
    await pg.goto(FILE); await pg.waitForTimeout(400);
    const f = await pg.evaluate(() => ({
      visibleTop: [...document.querySelectorAll('.tier-ask li.tk')].filter(l => { const r = l.getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight; }).length,
      body: getComputedStyle(document.body).fontFamily, title: getComputedStyle(document.querySelector('.section-title')).fontFamily }));
    await pg.setViewportSize({ width: 320, height: 844 }); await pg.waitForTimeout(200);
    const sw = await pg.evaluate(() => ({ sw: document.documentElement.scrollWidth, iw: innerWidth }));
    check('B5', 'fonts blocked: no horizontal scroll at 320px and takeaways still on the first screen', sw.sw <= sw.iw && f.visibleTop >= 2, `${f.visibleTop} visible, scrollWidth ${sw.sw} vs ${sw.iw}, ${aborted} font requests aborted`);
    check('B5', 'fonts blocked: body falls back to a sans stack and titles to a serif stack', /sans-serif$/.test(f.body) && /[^-]serif$/.test(f.title), `${f.body} | ${f.title}`);
    await ctx.close();
  }
  // different genome
  {
    const out = generateWith('tests/fixtures/minimal_23andme.txt', '/tmp/brand_fixture.html');
    check('B5', 'minimal 23andMe genome generates a page', fs.existsSync(out), out);
    const pg = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    await pg.goto('file://' + out); await pg.waitForTimeout(300);
    const x = await pg.evaluate(() => ({ text: document.body.innerText, secs: document.querySelectorAll('section[id]').length,
      hero: document.querySelector('#hero .hero-sentence').textContent, sw: document.documentElement.scrollWidth, iw: innerWidth,
      tiers: [...document.querySelectorAll('.tier')].map(t => t.textContent) }));
    check('B5', 'fixture page: no "0 of 0", hero and tiers show empty-state wording', !/\b0 of 0\b/.test(x.text) && x.secs === 16
      && /none of the displayed markers/i.test(x.hero) && /no flagged markers|No other flagged markers/i.test(x.text), `${x.secs} sections; ${x.hero}`);
    check('B5', 'fixture page: no horizontal scroll', x.sw <= x.iw, '');
    await pg.close();
    try { fs.unlinkSync(out); } catch (e) {}
  }
  // forced colours
  {
    const pg = await browser.newPage({ viewport: { width: 390, height: 844 } });
    await pg.emulateMedia({ forcedColors: 'active' });
    await pg.goto(FILE); await pg.waitForTimeout(300);
    await pg.evaluate(() => document.querySelectorAll('details').forEach(d => d.open = true));
    const fc = await pg.evaluate(() => {
      const sts = [...document.querySelectorAll('.st')];
      const bad = sts.filter(e => { const cs = getComputedStyle(e), r = e.getBoundingClientRect(); return e.textContent.trim().length <= 3 || cs.display === 'none' || cs.visibility === 'hidden' || r.width <= 0 || r.height <= 0; });
      const sec = getComputedStyle(document.querySelector('section[id]')).borderTopColor, pill = getComputedStyle(document.querySelector('.ev')).borderTopColor;
      const probe = document.createElement('i'); probe.style.color = 'CanvasText'; document.body.appendChild(probe);
      const ct = getComputedStyle(probe).color; probe.remove();
      return { n: sts.length, bad: bad.length, sw: document.documentElement.scrollWidth, iw: innerWidth, forced: matchMedia('(forced-colors: active)').matches, sec, pill, ct };
    });
    check('B5', 'forced colours: every status keeps visible text', fc.forced && fc.n > 0 && fc.bad === 0, `${fc.n} statuses, ${fc.bad} bad, forced=${fc.forced}`);
    check('B5', 'forced colours: no horizontal scroll at 390px', fc.sw <= fc.iw, `${fc.sw} vs ${fc.iw}`);
    check('B5', 'forced colours: panels and pills use CanvasText borders', fc.sec === fc.ct && fc.pill === fc.ct, `${fc.sec} | ${fc.pill} vs ${fc.ct}`);
    await pg.close();
  }
  // print
  {
    const pg = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    await pg.goto(FILE); await pg.waitForTimeout(300);
    await pg.emulateMedia({ media: 'print' });
    await pg.evaluate(() => document.querySelectorAll('details').forEach(d => d.open = true));
    const pr = await pg.evaluate(() => {
      const num = s => s.match(/[\d.]+/g).map(Number);
      const rows = [...document.querySelectorAll('.section-badge, .st')].filter(e => getComputedStyle(e).display !== 'none').map(e => {
        const cs = getComputedStyle(e); let bg = num(cs.backgroundColor); const a = bg.length === 4 ? bg[3] : 1; bg = bg.slice(0, 3).map(c => c * a + 255 * (1 - a));
        return { cls: e.className, fg: num(cs.color).slice(0, 3), bg: bg.slice(0, 3) };
      });
      const bot = document.querySelector('.botanical');
      return { bg: getComputedStyle(document.body).backgroundColor, ink: num(getComputedStyle(document.body).color).slice(0, 3), rows,
        art: bot ? getComputedStyle(bot).display : 'missing', hdr: getComputedStyle(document.querySelector('header')).display };
    });
    const worst = pr.rows.map(r => ({ cls: r.cls, c: (Math.max(lumB(r.fg), lumB(r.bg)) + .05) / (Math.min(lumB(r.fg), lumB(r.bg)) + .05) })).sort((a, b) => a.c - b.c)[0];
    check('B5', 'print: white page, dark ink', pr.bg === 'rgb(255, 255, 255)' && lumB(pr.ink) < 0.2, `${pr.bg} ink ${pr.ink}`);
    check('B5', 'print: badges and statuses reach 4.5:1 on white', pr.rows.length > 0 && worst.c >= 4.5, `${pr.rows.length} measured, worst ${worst && worst.cls} ${worst && worst.c.toFixed(2)}`);
    check('B5', 'print: hero art and header are not displayed', pr.art === 'none' && pr.hdr === 'none', `${pr.art}/${pr.hdr}`);
    await pg.close();
  }

  // ---------- B5 carried-in: hero art never overlaps hero text
  for (const w of [701, 800, 900, 1000, 1100, 1280]) {
    const pg = await browser.newPage({ viewport: { width: w, height: 900 } });
    await pg.goto(FILE); await pg.waitForTimeout(250);
    const o = await pg.evaluate(() => {
      const art = document.querySelector('.botanical').getBoundingClientRect();
      const walker = document.createTreeWalker(document.querySelector('#hero .hero-body'), NodeFilter.SHOW_TEXT);
      let n, count = 0; const hits = [];
      while ((n = walker.nextNode())) {
        if (!n.textContent.trim()) continue;
        const rg = document.createRange(); rg.selectNodeContents(n);
        for (const r of rg.getClientRects()) {
          if (r.width === 0) continue; count++;
          if (r.left < art.right && r.right > art.left && r.top < art.bottom && r.bottom > art.top) hits.push(`${n.textContent.trim().slice(0, 20)}@${Math.round(r.right)}`);
        }
      }
      return { count, hits, artLeft: Math.round(art.left), hero: Math.round(document.querySelector('#hero').getBoundingClientRect().height), sw: document.documentElement.scrollWidth, iw: innerWidth };
    });
    check('B5', `hero art does not overlap hero text at ${w}px`, o.count > 0 && o.hits.length === 0 && o.sw <= o.iw && (w !== 1280 || o.hero <= 240), `${o.count} line boxes, art at x=${o.artLeft}, hero ${o.hero}px ${o.hits.join(',')}`);
    await pg.close();
  }

  // ---------- B5 carried-in: longest section title at 320px, divider glyphs render
  {
    const pg = await browser.newPage({ viewport: { width: 320, height: 844 } });
    await pg.goto(FILE); await pg.waitForTimeout(250);
    const t = await pg.evaluate(() => {
      const titles = [...document.querySelectorAll('.section-title')];
      const over = titles.filter(e => { const h = e.closest('.section-header').getBoundingClientRect(), r = e.getBoundingClientRect(); return r.right > h.right + 0.5 || e.scrollWidth > e.clientWidth + 1; });
      const longest = titles.reduce((a, b) => (b.textContent.length > a.textContent.length ? b : a));
      return { n: titles.length, over: over.map(e => e.textContent.trim()), longest: longest.textContent.trim(), fs: getComputedStyle(longest).fontSize, ofw: getComputedStyle(longest).overflowWrap, sw: document.documentElement.scrollWidth, iw: innerWidth };
    });
    check('B5', 'section titles fit at 320px, longest included', t.n >= 16 && t.over.length === 0 && t.sw <= t.iw && t.ofw === 'anywhere' && t.fs === '26px', `${t.n} titles, longest "${t.longest}" at ${t.fs}, overflowing: ${t.over.join(',')}`);
    await pg.close();
    const dp = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    await dp.goto(FILE); await dp.waitForTimeout(250);
    const dv = await dp.evaluate(() => { const us = [...document.querySelectorAll('.divider svg use')]; return { n: us.length, zero: us.filter(u => { const r = u.getBoundingClientRect(); return r.width <= 0 || r.height <= 0; }).length, kinds: new Set(us.map(u => u.getAttribute('href'))).size }; });
    check('B5', 'every divider glyph (sword and heart) renders with a non-zero box', dv.n > 0 && dv.kinds === 2 && dv.zero === 0, `${dv.n} glyphs, ${dv.kinds} kinds, ${dv.zero} empty`);
    await dp.close();
  }

  await browser.close();

  let bad = 0;
  for (const r of results) { if (!r.ok) bad++; console.log(`${r.ok ? 'PASS' : 'FAIL'} ${r.id}  ${r.name}${r.detail ? '  [' + r.detail + ']' : ''}`); }
  const byCat = {};
  results.forEach(r => { (byCat[r.id] = byCat[r.id] || { p: 0, t: 0 }); byCat[r.id].t++; if (r.ok) byCat[r.id].p++; });
  console.log('\n' + Object.keys(byCat).sort().map(k => `${k}: ${byCat[k].p}/${byCat[k].t}`).join('   '));
  process.exit(bad ? 1 : 0);
}
main().catch(e => { console.error(e); process.exit(2); });

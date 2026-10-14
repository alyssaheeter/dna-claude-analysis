#!/usr/bin/env node
/* Measures webpage/dna_terminal.html against the rubric in webpage/DESIGN_REVIEW.md.
 * Dev-only check. Requires Playwright (npm i -g playwright) and a Chromium binary:
 *   PLAYWRIGHT_CHROMIUM=/path/to/chromium node scripts/check_webpage.js
 * Exits non-zero if any check fails.
 */
const path = require('path');
let chromium;
try { ({ chromium } = require('playwright')); }
catch (e) { ({ chromium } = require(path.join(process.env.NODE_PATH || '/opt/node22/lib/node_modules', 'playwright'))); }

const FILE = 'file://' + path.resolve(__dirname, '../webpage/dna_terminal.html');
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
      secs: secs.length, evs: document.querySelectorAll('section[id] .ev').length,
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

  await browser.close();

  let bad = 0;
  for (const r of results) { if (!r.ok) bad++; console.log(`${r.ok ? 'PASS' : 'FAIL'} ${r.id}  ${r.name}${r.detail ? '  [' + r.detail + ']' : ''}`); }
  const byCat = {};
  results.forEach(r => { (byCat[r.id] = byCat[r.id] || { p: 0, t: 0 }); byCat[r.id].t++; if (r.ok) byCat[r.id].p++; });
  console.log('\n' + Object.keys(byCat).sort().map(k => `${k}: ${byCat[k].p}/${byCat[k].t}`).join('   '));
  process.exit(bad ? 1 : 0);
}
main().catch(e => { console.error(e); process.exit(2); });

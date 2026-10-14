#!/usr/bin/env python3
"""Generate webpage/dna_terminal.html (single file, inline CSS/JS).

Genotypes are read live from the genome file; English interpretations come from
the INTERP tables below, which were curated from the reports/ output. A genotype
with no entry in a table is shown as "no interpretation" rather than guessed.
CSS lives in webpage/brand.css (Nocturne Hothouse tokens) and is inlined.
"""
import os
import re
from datetime import datetime
from html import escape

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENOME_FILE = os.environ.get('GENOME_FILE', f"{BASE_PATH}/data/my_dna_file.txt")
OUT_FILE = os.environ.get('OUT_FILE', f"{BASE_PATH}/webpage/dna_terminal.html")
CSS_FILE = f"{BASE_PATH}/webpage/brand.css"
ASSET_DIR = f"{BASE_PATH}/webpage/assets"
OWNER_NAME = os.environ.get('OWNER_NAME', '').strip() or 'Genome notes'


def load_css():
    with open(CSS_FILE, encoding='utf-8') as f:
        return f.read()


def inline_svg(name):
    """Return webpage/assets/<name>.svg as an inline fragment (XML prolog and comments stripped)."""
    with open(f"{ASSET_DIR}/{name}.svg", encoding='utf-8') as f:
        svg = f.read()
    svg = re.sub(r'<\?xml[^>]*\?>|<!--.*?-->|<!DOCTYPE[^>]*>', '', svg, flags=re.S)
    return svg.strip()


def wordmark(owner):
    first, _, rest = owner.partition(' ')
    caps = f'<span class="caps">{escape(rest.strip().upper())}</span>' if rest.strip() else ''
    return f'<span class="wordmark"><span class="script">{escape(first)}</span>{caps}</span>'


HEART = ('<svg viewBox="0 0 60 56" aria-hidden="true" focusable="false"><path d="M30 54C8 38 2 20 14 10C22 4 29 9 30 16'
         'C31 9 38 4 46 10C58 20 52 38 30 54Z" fill="#8F2638" stroke="#C9A66B" stroke-width="1.5" stroke-linejoin="round"/></svg>')


def hero(owner, flagged, ask, found, has_questions=None):
    """Compact introduction above the summary. Counts only; zero-safe when no markers were readable."""
    if has_questions is None:
        has_questions = ask > 0
    if found == 0:
        sentence = 'No markers were readable in this file, so there is nothing to report.'
    else:
        sentence = (f'{found} marker{"s" if found != 1 else ""} could be read on this chip, {flagged} differ'
                    f'{"s" if flagged == 1 else ""} from the typical result, and {ask} {"has" if ask == 1 else "have"} '
                    f'a sensible follow-up.')
    secondary = '<a class="btn btn-secondary" href="#questions">Questions for my clinician</a>' if has_questions else ''
    botanical = (f'<div class="botanical" aria-hidden="true"><span class="leaf l1">{inline_svg("leaf")}</span>'
                 f'<span class="leaf l2">{inline_svg("leaf")}</span><span class="heart h1">{HEART}</span>'
                 f'<span class="heart h2">{HEART}</span></div>')
    return (f'<div id="hero" class="hero" role="region" aria-labelledby="hero-title"><div class="hero-body">'
            f'<p class="kicker">{escape(owner.upper())} &middot; THE SHORT VERSION</p>'
            f'<h1 id="hero-title">What your DNA can, and can\'t,<br><em>tell you.</em></h1>'
            f'<p class="hero-sentence">{escape(sentence)}</p>'
            f'<p class="hero-actions"><a class="btn btn-primary" href="#status">See key takeaways</a>{secondary}</p>'
            f"</div>{botanical}</div>")


META = {'source': 'Unknown', 'chip': 'Unknown', 'y_calls': 0, 'x_calls': 0}


def load_genome():
    genome = {}
    with open(GENOME_FILE) as f:
        for line in f:
            if line.startswith('#'):
                low = line.lower()
                if 'ancestrydna' in low:
                    META['source'] = 'AncestryDNA'
                elif '23andme' in low:
                    META['source'] = '23andMe'
                m = re.search(r'array version:\s*(\S+)', line, re.I)
                if m:
                    META['chip'] = f"array v{m.group(1).lstrip('Vv')}"
                continue
            if line.startswith('rsid'):
                continue
            p = line.rstrip('\n').split('\t')
            if len(p) >= 5:
                gt = p[3] + p[4]
            elif len(p) == 4:
                gt = p[3]
            else:
                continue
            called = gt not in ('00', '--', '0')
            genome[p[0]] = gt if called else None
            if called and p[1] in ('24', 'Y'):
                META['y_calls'] += 1
            if called and p[1] in ('23', 'X'):
                META['x_calls'] += 1
    return genome


GENOME = load_genome()
RESULTS = []
STATS = {'found': 0, 'total': 0}


def geno(rsid):
    g = GENOME.get(rsid)
    return g if g else None


def norm(g):
    return ''.join(sorted(g))


# Follow-up suggestions for flagged markers, keyed by rsID: (priority, text).
# Wording is deliberately "ask about", never a diagnosis or a dose instruction.
ACT = {
    'rs4244285': (1, "Tell your pharmacist or prescriber you may be an intermediate CYP2C19 metabolizer before starting clopidogrel, some acid reducers or some antidepressants. Clinical-grade testing can confirm.", "Does a likely intermediate CYP2C19 metabolizer status matter for any medicine I take or might be prescribed?"),
    'rs10757274': (2, "Standard cardiovascular screening applies (blood pressure, lipids). Family history matters more than this one marker.", "Given my family history, are my blood pressure and cholesterol screening intervals right?"),
    'rs7903146': (3, "Standard diabetes screening applies (fasting glucose or HbA1c). Activity, weight and diet matter far more than this one marker.", "Should I have fasting glucose or HbA1c checked, and how often?"),
    'rs3923809': (4, "If you have restless-legs symptoms, ask about a ferritin (iron stores) blood test.", "If I have restless-legs symptoms, should my ferritin (iron stores) be checked?"),
    'rs2282679': (5, "Ask whether a 25(OH)D (vitamin D) blood test makes sense; supplementation should follow the blood level, not this genotype.", "Would a 25(OH)D (vitamin D) blood test be useful for me?"),
    'rs7041': (5, "Ask whether a 25(OH)D (vitamin D) blood test makes sense; supplementation should follow the blood level, not this genotype.", "Would a 25(OH)D (vitamin D) blood test be useful for me?"),
    'rs9923231': (6, "If warfarin is ever prescribed, mention this result; dosing is guided by clinical testing and INR monitoring.", "If I am ever prescribed warfarin, should dosing use genetic testing or INR monitoring alone?"),
}

# Strength of the evidence behind each section's markers (judgement, shown as a badge).
EVIDENCE = {
    'ancestry': ('weak', 'A few single markers cannot estimate ancestry'),
    'health': ('moderate', 'Mixed: Factor V/HFE are well established, most others are modest risk shifts'),
    'nutrition': ('moderate', 'Some markers are well studied; effects on real diets are small'),
    'sports': ('weak', 'Single-marker athletic prediction is weak'),
    'psychology': ('weak', 'Psychological genetics has very small effect sizes'),
    'cognitive': ('weak', 'Cognition is highly polygenic; single markers explain little'),
    'longevity': ('weak', 'Longevity associations are inconsistent across studies'),
    'sleep': ('weak', 'Chronotype markers are weak; restless-legs markers are moderate'),
    'immunity': ('moderate', 'Autoimmune and allergy associations are real but modest'),
    'pain': ('weak', 'Pain-sensitivity markers are weak predictors'),
    'detox': ('moderate', 'Drug-metabolism genes are well studied; the rest is modest'),
    'skin': ('weak', 'Skin and acne associations are weak'),
    'vision': ('moderate', 'Eye-disease associations are real but modest'),
    'traits': ('moderate', 'Eye colour is a strong predictor; hair traits are not'),
    'pharma': ('established', 'CYP2C19, VKORC1, SLCO1B1 and TPMT have clinical guidelines'),
    'carrier': ('established', 'Carrier variants are well characterised, but this chip tests very few'),
}

ST = {
    'normal': ('✓', 'TYPICAL'),
    'info': ('○', 'INFO'),
    'moderate': ('▲', 'FLAGGED · MODERATE'),
    'risk': ('▲▲', 'FLAGGED · HIGH'),
    'na': ('–', 'NO READING'),
    'none': ('–', 'NOT TESTED'),
}


def row(rsid, gene, table):
    """One marker row. table maps sorted genotype -> (status, plain-English meaning)."""
    STATS['total'] += 1
    g = geno(rsid)
    idx = len(RESULTS)
    if g is None:
        st, text = 'none', 'This chip does not test this marker'
        RESULTS.append({'section': None, 'rsid': rsid, 'gene': gene, 'g': None, 'st': 'na', 'text': ''})
    else:
        STATS['found'] += 1
        st, text = table.get(norm(g), ('na', 'No interpretation available for this genotype'))
        act = ACT.get(rsid) if st in ('moderate', 'risk') else None
        RESULTS.append({'section': None, 'rsid': rsid, 'gene': gene, 'g': g, 'st': st, 'text': text,
                        'act': act[1] if act else None, 'pri': act[0] if act else None, 'q': act[2] if act else None})
    icon, label = ST[st]
    flag = ' flag' if st in ('moderate', 'risk') else ''
    q = escape(f'{gene} {rsid} {text} {label}'.lower(), quote=True)
    return (f'<tr class="r{flag}" data-q="{q}"><td data-label="Status"><span class="st status-{"na" if st == "none" else st}">'
            f'<span aria-hidden="true">{icon}</span> {label}</span></td>'
            f'<td class="c-mean" data-label="What it means"><span class="mt">{escape(text)}<!--X{idx}--></span></td>'
            f'<td class="geno" data-label="Your result">{g or "--"}</td>'
            f'<td class="c-mark" data-label="Marker">{escape(gene)} · {rsid}</td></tr>')


def table(rows):
    body = '\n'.join(rows)
    return ('<table><thead><tr><th scope="col">Status</th><th scope="col">What it means</th>'
            '<th scope="col">Your result</th><th scope="col">Marker</th></tr></thead>\n'
            f'<tbody>{body}</tbody></table>')


def sub(title, rows):
    return f'<div class="subsection"><h3 class="subsection-title">{escape(title)}</h3>{table(rows)}</div>'


def finding(kind, icon, gene, desc):
    return (f'<div class="finding {kind}"><div class="finding-icon" aria-hidden="true">{icon}</div><div class="finding-content">'
            f'<div class="finding-gene">{escape(gene)}</div><div class="finding-desc">{escape(desc)}</div></div></div>')


def profile(title, value, desc, color='var(--cyan)'):
    return (f'<div class="profile-box"><div class="profile-title">{escape(title)}</div>'
            f'<div class="profile-value" style="color: {color};">{escape(value)}</div>'
            f'<div class="profile-desc">{escape(desc)}</div></div>')


def disclaimer(text, critical=False):
    style = ' style="background: rgba(255, 51, 51, 0.1); border-color: var(--red); color: var(--red);"' if critical else ''
    return f'<div class="disclaimer" role="note"{style}><strong>! Important</strong> {escape(text)}</div>'


def note(text):
    return f'<p class="note">{escape(text)}</p>'


SEC_TITLE = {}


def section(sid, title, badge_cls, badge, content):
    mine = [r for r in RESULTS if r['section'] is None]
    for r in mine:
        r['section'] = sid
    SEC_TITLE[sid] = title
    found_rows = [r for r in mine if r['g']]
    n_risk = sum(r['st'] == 'risk' for r in found_rows)
    n_mod = sum(r['st'] == 'moderate' for r in found_rows)
    if mine and not found_rows:
        badge_cls, badge = 'moderate', 'NO DATA ON THIS CHIP'
    elif n_risk:
        badge_cls, badge = 'risk', f'{n_risk} HIGH, {n_mod} MODERATE'
    elif n_mod:
        badge_cls, badge = 'moderate', f'{n_mod} MODERATE FLAG{"S" if n_mod > 1 else ""}'
    elif mine:
        badge_cls, badge = 'good', 'NO FLAGS'
    ev, ev_text = EVIDENCE[sid]
    opened = ' open' if (n_risk or n_mod) else ''
    return (f'<section id="{sid}" aria-labelledby="h-{sid}"><details class="sec"{opened}>'
            f'<summary class="section-header"><h2 class="section-title" id="h-{sid}">// {escape(title)}</h2>'
            f'<span class="badges"><span class="ev ev-{ev}" title="{escape(ev_text, quote=True)}">EVIDENCE: {ev.upper()}</span>'
            f'<span class="section-badge {badge_cls}">{escape(badge)}</span></span></summary>'
            f'<div class="section-content"><p class="ev-note">{escape(ev_text)}.</p>{content}</div></details></section>')


MED = ("Genes indicate predisposition, not destiny. This page is informational only and is not medical advice; "
       "consumer-array results are not clinical-grade. Discuss anything important with a clinician or genetic counselor.")

# ---------------------------------------------------------------- sections
sections = []

# ANCESTRY
anc = note("Only a handful of ancestry-informative markers are tested here; this is NOT an ethnicity estimate. "
                 "Use your AncestryDNA ethnicity results (or GEDmatch / DNA.Land) for real ancestry.")
anc += sub('Ancestry-informative markers', [
    row('rs1426654', 'SLC24A5', {'AA': ('info', 'European-type light-skin variant')}),
    row('rs12913832', 'HERC2/OCA2', {'GG': ('info', 'Blue/light eye variant; common in Northern Europe'), 'AA': ('info', 'Brown eye variant'), 'AG': ('info', 'Intermediate (green/hazel)')}),
    row('rs4988235', 'LCT (MCM6)', {'AA': ('info', 'Lactase persistence variant; common in Europeans')}),
    row('rs2814778', 'DARC (Duffy)', {'TT': ('info', 'Duffy-positive (the African-prevalent null variant is absent)')}),
    row('rs3827760', 'EDAR', {'AA': ('info', 'Ancestral variant; East Asian-type variant not present')}),
    row('rs17822931', 'ABCC11', {'CT': ('info', 'Heterozygous: dry-type/wet-type earwax mix')}),
])
sections.append(section('ancestry', 'ANCESTRY', 'moderate', 'LIMITED DATA', anc))

# HEALTH
h = ''
h += sub('Cardiovascular', [
    row('rs10757274', '9p21 locus', {'AG': ('moderate', 'Slightly increased coronary artery disease risk (heterozygous)')}),
    row('rs6025', 'Factor V Leiden', {'CC': ('normal', 'No Factor V Leiden mutation')}),
    row('rs1800562', 'HFE C282Y', {'GG': ('normal', 'No C282Y hemochromatosis mutation')}),
    row('rs1801131', 'MTHFR A1298C', {'GT': ('normal', 'Normal activity (heterozygous)')}),
    row('rs1801133', 'MTHFR C677T', {'GG': ('normal', 'No C677T variant (reference)')}),
])
h += sub('Metabolic, cancer and autoimmune', [
    row('rs7903146', 'TCF7L2', {'CT': ('moderate', 'Moderately increased type 2 diabetes risk (heterozygous)')}),
    row('rs17782313', 'MC4R', {'TT': ('normal', 'Normal appetite regulation')}),
    row('rs1042522', 'TP53 Arg72Pro', {'GG': ('normal', 'Arg/Arg, the common variant')}),
    row('rs1695', 'GSTP1', {'AA': ('normal', 'Normal detoxification activity')}),
    row('rs2476601', 'PTPN22', {'AG': ('moderate', 'Modestly increased autoimmune risk (RA, T1D, thyroiditis); common variant')}),
    row('rs3087243', 'CTLA4', {'GG': ('moderate', 'Slightly increased autoimmune risk')}),
    row('rs6457617', 'HLA-DRB1', {'CC': ('normal', 'Normal rheumatoid arthritis risk')}),
])
h += sub('Inflammation and allergy', [
    row('rs1800795', 'IL-6 -174', {'CC': ('moderate', 'Higher IL-6 production; more inflammation, slower healing')}),
    row('rs1800629', 'TNF-alpha -308', {'GG': ('normal', 'Standard TNF-alpha production')}),
    row('rs1143634', 'IL-1B', {'AG': ('moderate', 'Slightly higher IL-1B production')}),
    row('rs1801275', 'IL4R', {'AA': ('moderate', 'Increased IL-4 sensitivity; some atopy predisposition')}),
    row('rs7216389', 'ORMDL3', {'CC': ('normal', 'Normal asthma risk')}),
])
sections.append(section('health', 'HEALTH RISKS', 'moderate', 'MODERATE MARKERS', h))

# NUTRITION
n = sub('Diet and nutrients', [
    row('rs4988235', 'LCT', {'AA': ('normal', 'Lactose tolerant')}),
    row('rs7454108', 'HLA-DQ8', {'TT': ('normal', 'Low celiac risk via DQ8 (DQ2.5 marker not on chip)')}),
    row('rs671', 'ALDH2', {'GG': ('normal', 'Normal alcohol metabolism')}),
    row('rs2282679', 'GC (VDBP)', {'GT': ('moderate', 'Somewhat lower vitamin D binding; check 25(OH)D')}),
    row('rs7041', 'GC (VDBP)', {'AC': ('moderate', 'Somewhat lower vitamin D binding; check 25(OH)D')}),
    row('rs602662', 'FUT2', {'AG': ('moderate', 'Mildly reduced; may relate to B12 absorption')}),
    row('rs7501331', 'BCMO1', {'CC': ('normal', 'Normal beta-carotene conversion')}),
    row('rs174546', 'FADS1', {'CT': ('moderate', 'Moderate omega-3 conversion')}),
    row('rs4961', 'ADD1', {'GG': ('normal', 'Normal salt sensitivity')}),
    row('rs713598', 'TAS2R38', {'CG': ('info', 'Medium bitter taste sensitivity')}),
    row('rs855791', 'TMPRSS6', {'GG': ('normal', 'Normal iron status')}),
])
sections.append(section('nutrition', 'NUTRITION', 'good', 'MOSTLY NORMAL', n))

# SPORTS
_actn3 = geno('rs1815739')
s = ''
if _actn3:
    _prof = {'CC': ('POWER-LEANING (RR)', 'Two functional ACTN3 copies'), 'CT': ('ALL-ROUNDER (RX)', 'One functional ACTN3 copy; versatile fiber mix'), 'TT': ('ENDURANCE-LEANING (XX)', 'No functional ACTN3; slow-twitch bias')}.get(norm(_actn3), (_actn3, 'ACTN3 rs1815739'))
    s += '<div class="two-cols">' + profile('Athlete profile (ACTN3)', _prof[0], _prof[1], 'var(--green)') + '</div>'
s += sub('Performance markers', [
    row('rs1815739', 'ACTN3', {'CT': ('info', 'RX: one functional copy; versatile fiber mix')}),
    row('rs8192678', 'PPARGC1A', {'CT': ('normal', 'Gly/Ser; moderate endurance potential')}),
    row('rs1049434', 'MCT1', {'AA': ('normal', 'Efficient lactate clearance; good for intervals')}),
    row('rs1800629', 'TNF-alpha', {'GG': ('normal', 'Lower inflammation after training')}),
    row('rs1800795', 'IL-6', {'CC': ('moderate', 'More inflammation; may recover slower')}),
    row('rs6265', 'BDNF', {'TT': ('moderate', 'Met/Met; may need more repetitions to learn new skills')}),
    row('rs4880', 'SOD2', {'AG': ('normal', 'Average antioxidant activity')}),
])
sections.append(section('sports', 'SPORTS / FITNESS', 'good', 'BALANCED', s))

# PSYCHOLOGY
p = note("Psychological genetics has small effect sizes. Do not read these as personality or diagnosis.")
_comt, _bdnf = geno('rs4680'), geno('rs6265')
_boxes = []
if _comt:
    _boxes.append(profile('COMT type', {'AG': 'VAL/MET (AG)', 'GG': 'VAL/VAL (GG)', 'AA': 'MET/MET (AA)'}[norm(_comt)] if norm(_comt) in ('AG', 'GG', 'AA') else _comt, 'rs4680: dopamine clearance in prefrontal cortex'))
if _bdnf:
    _boxes.append(profile('BDNF', {'CC': 'VAL/VAL (CC)', 'CT': 'VAL/MET (CT)', 'TT': 'MET/MET (TT)'}.get(norm(_bdnf), _bdnf), 'rs6265: activity-dependent BDNF release; exercise helps', 'var(--amber)' if norm(_bdnf) == 'TT' else 'var(--cyan)'))
if _boxes:
    p += '<div class="two-cols">' + ''.join(_boxes) + '</div>'
p += sub('Markers', [
    row('rs4680', 'COMT Val158Met', {'AG': ('info', 'Balanced warrior/worrier profile')}),
    row('rs6265', 'BDNF Val66Met', {'TT': ('moderate', 'Reduced BDNF secretion; small increased stress-linked mood risk')}),
    row('rs16969968', 'CHRNA5', {'GG': ('normal', 'Standard nicotine dependence risk')}),
])
_missing = [g for r, g in (('rs25531', '5-HTTLPR'), ('rs1800497', 'DRD2'), ('rs53576', 'OXTR'), ('rs1799971', 'OPRM1'), ('rs1360780', 'FKBP5')) if geno(r) is None]
if _missing:
    p += finding('info', 'i', 'Not covered', ', '.join(_missing) + ' markers are not on this array.')
sections.append(section('psychology', 'PSYCHOLOGY', 'moderate', 'MIXED', p))

# COGNITIVE
c = note("Cognition is highly polygenic; single variants explain very little.")
c += sub('Cognitive markers', [
    row('rs4680', 'COMT', {'AG': ('info', 'Balanced cognitive flexibility')}),
    row('rs6265', 'BDNF', {'TT': ('moderate', 'Met/Met; regular aerobic exercise is the best-supported offset')}),
    row('rs9536314', 'KLOTHO (KL-VS)', {'GT': ('normal', 'Heterozygous KL-VS; linked to better cognitive aging')}),
    row('rs759178', 'FOXP2', {'AA': ('info', 'Speech-gene variant, no known effect')}),
    row('rs1800795', 'IL-6', {'CC': ('moderate', 'Higher inflammatory tone')}),
])
if geno('rs429358') is None or geno('rs7412') is None:
    c += finding('info', 'i', 'APOE', 'APOE (rs429358 / rs7412) is NOT on this array, so APOE status is unknown here.')
sections.append(section('cognitive', 'COGNITIVE', 'good', 'NO MAJOR FLAGS', c))

# LONGEVITY
lg = sub('Longevity markers', [
    row('rs9536314', 'KLOTHO', {'GT': ('normal', 'Favorable heterozygote')}),
    row('rs5882', 'CETP', {'GG': ('normal', 'Longevity variant; higher HDL')}),
    row('rs10936599', 'TERC', {'CC': ('normal', 'Associated with longer telomeres')}),
    row('rs2736100', 'TERT', {'CC': ('normal', 'Associated with telomerase activity')}),
    row('rs1001179', 'CAT', {'CT': ('info', 'Average catalase activity')}),
])
lg += finding('info', 'i', 'Note', 'Longevity genetics is weakly predictive; any overall score from a few SNPs has no real population basis.')
if geno('rs2802292') is None:
    lg += finding('info', 'i', 'Not covered', 'FOXO3 (rs2802292) is not on this array.')
sections.append(section('longevity', 'LONGEVITY', 'good', 'FAVORABLE MARKERS', lg))

# SLEEP
sl = ''
_boxes = []
if geno('rs4753426'):
    _boxes.append(profile('Chronotype', {'CC': 'EVENING-LEANING', 'TT': 'MORNING-LEANING'}.get(norm(geno('rs4753426')), 'INTERMEDIATE'), 'From MTNR1B rs4753426 (one marker; weak evidence)', 'var(--amber)'))
if geno('rs3923809'):
    _boxes.append(profile('Restless legs (BTBD9)', {'AA': 'ELEVATED RISK', 'GG': 'NOT ELEVATED'}.get(norm(geno('rs3923809')), 'INTERMEDIATE'), 'From rs3923809; if symptomatic, check iron (ferritin) with a clinician', 'var(--amber)'))
if _boxes:
    sl += '<div class="two-cols">' + ''.join(_boxes) + '</div>'
sl += sub('Sleep markers', [
    row('rs4753426', 'MTNR1B', {'CC': ('moderate', 'Delayed melatonin onset; later natural sleep time')}),
    row('rs10830963', 'MTNR1B', {'CG': ('moderate', 'Slightly reduced melatonin sensitivity')}),
    row('rs3923809', 'BTBD9', {'AA': ('risk', 'Elevated risk of restless legs / periodic limb movements')}),
    row('rs2300478', 'MEIS1', {'GT': ('na', 'No interpretation available for this genotype')}),
    row('rs1801260', 'CLOCK', {'AG': ('na', 'No interpretation available for this genotype')}),
    row('rs1823125', 'PAX8', {'AG': ('normal', 'Average sleep need (~7-8h)')}),
])
if geno('rs762551') is None or geno('rs5751876') is None:
    sl += finding('info', 'i', 'Caffeine', 'CYP1A2 and/or ADORA2A are not on this array, so caffeine sensitivity is unknown.')
sections.append(section('sleep', 'SLEEP', 'moderate', 'EVENING TYPE', sl))

# IMMUNITY
im = sub('Immune markers', [
    row('rs2476601', 'PTPN22', {'AG': ('moderate', 'Modestly increased autoimmune tendency')}),
    row('rs3087243', 'CTLA4', {'GG': ('moderate', 'Slightly increased autoimmune tendency')}),
    row('rs1801275', 'IL4R', {'AA': ('moderate', 'Atopy predisposition')}),
    row('rs1800795', 'IL-6', {'CC': ('moderate', 'Higher inflammatory tone')}),
    row('rs1800629', 'TNF-alpha', {'GG': ('normal', 'Standard')}),
    row('rs7454108', 'HLA-DQ8', {'TT': ('normal', 'Low celiac risk via DQ8')}),
])
if any(r['st'] in ('moderate', 'risk') and r['section'] is None for r in RESULTS):
    im += finding('warning', '!', 'Overall', 'One or more inflammation/autoimmune markers are flagged. Generic advice: sleep, Mediterranean diet, omega-3.')
sections.append(section('immunity', 'IMMUNITY', 'moderate', 'MODERATE INFLAMMATION', im))

# PAIN
pn = sub('Pain markers', [
    row('rs4680', 'COMT', {'AG': ('info', 'Average pain sensitivity')}),
    row('rs3783641', 'GCH1', {'AT': ('normal', 'Carries protective allele')}),
    row('rs10483639', 'GCH1', {'GG': ('normal', 'Protective: lower chronic-pain risk')}),
    row('rs1835740', 'MTDH', {'CC': ('moderate', 'Increased migraine risk')}),
    row('rs11172113', 'LRP1', {'CT': ('moderate', 'Moderate migraine risk')}),
    row('rs1800795', 'IL-6', {'CC': ('moderate', 'Tendency toward inflammatory pain')}),
])
sections.append(section('pain', 'PAIN SENSITIVITY', 'moderate', 'AVERAGE / MIGRAINE-PRONE', pn))

# DETOX
dt = sub('Detox and drug-processing markers', [
    row('rs4244285', 'CYP2C19*2', {'AG': ('moderate', 'Intermediate metabolizer')}),
    row('rs1799930', 'NAT2', {'AG': ('moderate', 'Intermediate acetylator')}),
    row('rs4880', 'SOD2', {'AG': ('normal', 'Average')}),
    row('rs1001179', 'CAT', {'CT': ('moderate', 'Slightly reduced catalase')}),
    row('rs1801394', 'MTRR', {'AG': ('moderate', 'Slightly reduced B12 regeneration')}),
    row('rs11191439', 'AS3MT', {'CT': ('moderate', 'Somewhat reduced arsenic clearance')}),
    row('rs1695', 'GSTP1', {'AA': ('normal', 'Good detox capacity')}),
])
sections.append(section('detox', 'DETOXIFICATION', 'moderate', 'INTERMEDIATE', dt))

# SKIN
sk = sub('Skin markers', [
    row('rs4133274', 'DDB2', {'AA': ('risk', 'Increased acne risk')}),
    row('rs1800795', 'IL-6', {'CC': ('moderate', 'More inflammation; slower healing')}),
    row('rs1805007', 'MC1R R151C', {'CC': ('normal', 'Reference genotype')}),
    row('rs1805005', 'MC1R V60L', {'GG': ('normal', 'Reference genotype')}),
    row('rs2070600', 'AGER', {'CC': ('normal', 'Protective against glycation aging')}),
    row('rs1695', 'GSTP1', {'AA': ('normal', 'Good antioxidant capacity')}),
    row('rs4880', 'SOD2', {'AG': ('normal', 'Average')}),
])
if geno('rs1805009') == 'CC':
    sk += finding('warning', '!', 'MC1R D294H (rs1805009)', 'See TRAITS: this genotype may carry a red-hair-associated variant, which also matters for UV sensitivity. Use sun protection regardless.')
sections.append(section('skin', 'SKIN', 'moderate', 'ACNE / INFLAMMATION TENDENCY', sk))

# VISION
vs = sub('Vision and hearing', [
    row('rs10490924', 'ARMS2', {'GG': ('normal', 'Normal macular degeneration risk')}),
    row('rs10483727', 'SIX6', {'CT': ('moderate', 'Moderate glaucoma risk')}),
    row('rs4656461', 'TMCO1', {'AA': ('normal', 'Normal glaucoma risk')}),
    row('rs2165241', 'EPHA2', {'CT': ('moderate', 'Moderate cataract risk')}),
    row('rs634990', 'RASGRF1', {'TT': ('normal', 'Normal myopia risk')}),
    row('rs7598759', 'GRM7', {'CC': ('na', 'No interpretation available for this genotype')}),
])
sections.append(section('vision', 'VISION / HEARING', 'good', 'MOSTLY NORMAL', vs))

# TRAITS
tr = sub('Physical traits', [
    row('rs12913832', 'HERC2', {'GG': ('info', 'Blue/gray eyes (strong predictor)')}),
    row('rs1426654', 'SLC24A5', {'AA': ('info', 'Light skin (European variant)')}),
    row('rs1805009', 'MC1R D294H', {'CC': ('moderate', 'Possible red-hair-associated genotype. VERIFY against actual hair color / strand orientation')}),
    row('rs12821256', 'KITLG', {'TT': ('info', 'Not the blond-associated variant')}),
    row('rs3827760', 'EDAR', {'AA': ('info', 'Thinner hair (European-type)')}),
    row('rs2180439', 'HDAC9', {'CT': ('moderate', 'Moderate hair-loss association')}),
    row('rs17822931', 'ABCC11', {'CT': ('info', 'Intermediate earwax type')}),
])
if geno('rs1805009') == 'CC':
    tr += finding('warning', '?', 'Hair color not reliable', 'Single-variant MC1R hair-color guesses are unconfirmed; compare with your actual hair color.')
sections.append(section('traits', 'PHYSICAL TRAITS', 'good', 'INFORMATIONAL', tr))

# PHARMA
ph = disclaimer("Never change medication based on this page. Discuss pharmacogenomics with a prescriber or pharmacist (ideally clinical-grade testing).", True)
ph += sub('Drug-response markers', [
    row('rs4244285', 'CYP2C19*2', {'AG': ('moderate', 'Intermediate metabolizer (affects clopidogrel, some PPIs/antidepressants)')}),
    row('rs9923231', 'VKORC1', {'CT': ('moderate', 'Intermediate warfarin sensitivity')}),
    row('rs4149056', 'SLCO1B1', {'TT': ('normal', 'Normal statin transport (myopathy risk not elevated)')}),
    row('rs1800460', 'TPMT', {'CC': ('normal', 'Normal thiopurine metabolism')}),
])
sections.append(section('pharma', 'PHARMACOGENOMICS', 'moderate', 'INTERMEDIATE METABOLIZER', ph))

# CARRIER
cr = disclaimer("The AncestryDNA array covers very few carrier variants. A clean result here is NOT a negative carrier screen.", True)
cr += sub('Tested carrier variants', [
    row('rs1800562', 'HFE C282Y', {'GG': ('normal', 'Not a C282Y carrier')}),
    row('rs28929474', 'SERPINA1 Z', {'CC': ('normal', 'MM genotype; normal A1AT')}),
    row('rs113993960', 'CFTR F508del', {}),
    row('rs76763715', 'GBA N370S', {}),
    row('rs334', 'HBB (sickle)', {}),
])
sections.append(section('carrier', 'CARRIER STATUS', 'good', 'NO CARRIER VARIANTS FOUND', cr))

# ---------------------------------------------------------------- summary
total = len({r['rsid'] for r in RESULTS})
found = len({r['rsid'] for r in RESULTS if r['g']})
snps = len(GENOME)
FLAGGED = [r for r in RESULTS if r['g'] and r['st'] in ('moderate', 'risk')]


def by_gene(rows):
    """Keep the first row per gene so a repeated marker is listed once."""
    seen, out = set(), []
    for r in rows:
        if r['gene'] not in seen:
            seen.add(r['gene'])
            out.append(r)
    return out


ask = by_gene(sorted([r for r in FLAGGED if r['act']], key=lambda r: r['pri']))[:7]
ask_genes = {r['gene'] for r in ask}
know = by_gene([r for r in FLAGGED if r['gene'] not in ask_genes])
good = by_gene([r for r in RESULTS if r['g'] and r['st'] == 'normal' and r['section'] in ('health', 'pharma', 'longevity', 'carrier')])[:6]

not_tested = [r['gene'] for r in by_gene([r for r in RESULTS if r['g'] is None])]
for rs, name in (('rs429358', 'APOE'), ('rs762551', 'CYP1A2'), ('rs2802292', 'FOXO3')):
    if geno(rs) is None and name not in not_tested:
        not_tested.append(name)

if META['y_calls'] > 100:
    _sex = 'Male (XY)'
elif META['x_calls'] > 1000:
    _sex = 'Female (XX)'
else:
    _sex = 'Unknown'


def li(icon, cls, head, body=''):
    b = f'<div class="tk-act">→ {escape(body)}</div>' if body else ''
    return f'<li class="tk {cls}"><span class="tk-icon" aria-hidden="true">{icon}</span><div><div class="tk-head">{head}</div>{b}</div></li>'


def tier(title, cls, items, empty):
    inner = ''.join(items) or f'<li class="tk">{escape(empty)}</li>'
    return f'<div class="tier {cls}"><h3 class="tier-title">{escape(title)}</h3><ul>{inner}</ul></div>'


ask_items = [li('▲', 'amber', f"<strong>{escape(r['gene'])}</strong> ({r['g']}): {escape(r['text'])}", r['act']) for r in ask]
know_items = [li('▲', 'amber', f"<strong>{escape(r['gene'])}</strong> ({r['g']}): {escape(r['text'])}") for r in know[:6]]
if len(know) > 6:
    know_items.append(f'<li class="tk more">+ {len(know) - 6} more flagged markers in the sections below</li>')
good_items = [li('✓', 'green', f"<strong>{escape(r['gene'])}</strong>: {escape(r['text'])}") for r in good]
nt_items = [li('–', 'gray', escape(', '.join(not_tested)) + ' are not on this chip, so their results are unknown. '
               'A consumer SNP array also misses most clinically important variants (for example most BRCA1/BRCA2 and CFTR variants); '
               'ask a clinician about clinical testing if it matters to you.')] if not_tested else []

questions = ''.join(f'<li>{escape(r["q"])}</li>' for r in by_gene(ask) if r['q'])
questions_html = (f'<div class="tier questions" id="questions"><h3 class="tier-title">Questions to bring to a clinician or pharmacist</h3>'
                  f'<ol>{questions}</ol></div>') if questions else ''

n_flag_rows = len({r['rsid'] for r in FLAGGED})
lede = (f'<p class="lede"><strong>{n_flag_rows} of {found}</strong> distinct markers read on this chip differ from the typical result, and '
        f'<strong>{len(ask)}</strong> of them have a sensible follow-up. Each marker has a small effect on its own. '
        f'Informational only, not medical advice.</p>')

legend = '''<details class="legend"><summary>How to read the statuses</summary><dl>
<dt><span class="st status-normal">✓ TYPICAL</span></dt><dd>The common or reference result. Nothing to act on.</dd>
<dt><span class="st status-info">○ INFO</span></dt><dd>A trait or characteristic. No risk is implied.</dd>
<dt><span class="st status-moderate">▲ FLAGGED · MODERATE</span></dt><dd>Differs from typical with a small to moderate effect. Usually worth awareness, not worry.</dd>
<dt><span class="st status-risk">▲▲ FLAGGED · HIGH</span></dt><dd>A larger effect. Worth discussing with a clinician.</dd>
<dt><span class="st status-na">– NO READING / NOT TESTED</span></dt><dd>No interpretation for this result, or the chip does not test the marker.</dd>
</dl><p>Evidence badges: <strong>ESTABLISHED</strong> = clinical guidelines exist; <strong>MODERATE</strong> = real but modest; <strong>WEAK</strong> = inconsistent or very small effects.</p></details>'''

toolbar = '''<div class="toolbar" role="search"><label class="sr" for="q">Search markers by gene, rsID or keyword</label>
<input id="q" type="search" placeholder="Search gene, rsID or keyword" autocomplete="off">
<button type="button" id="flagonly" aria-pressed="false">Flagged only</button>
<button type="button" id="expandall">Expand all</button><button type="button" id="collapseall">Collapse all</button>
<span id="count" role="status" aria-live="polite"></span></div>'''

hero_html = hero(OWNER_NAME, n_flag_rows, len(ask), found, has_questions=bool(questions))

status = f'''
<div class="status-box" id="status" tabindex="-1">
  <h2 class="status-header">// KEY TAKEAWAYS</h2>
  {lede}
  {tier('Ask about / act on', 'tier-ask', ask_items, 'No flagged markers have a standard follow-up.')}
  {tier('Worth knowing', 'tier-know', know_items, 'No other flagged markers.')}
  {tier('Good news', 'tier-good', good_items, 'No highlighted markers.')}
  {tier('Not tested on this chip', 'tier-nt', nt_items, 'All displayed markers were on the chip.')}
  {questions_html}
  <div class="status-grid">
    <div class="status-item"><span class="status-label">GENOME:</span><span class="status-value">{escape(META['source'])}</span></div>
    <div class="status-item"><span class="status-label">SEX:</span><span class="status-value">{_sex}</span></div>
    <div class="status-item"><span class="status-label">SNPs:</span><span class="status-value">{snps:,}</span></div>
    <div class="status-item"><span class="status-label">CHIP:</span><span class="status-value">{escape(META['chip'])}</span></div>
  </div>
  <div class="progress-bar"><div class="progress-track">
    <div class="progress-fill" style="flex: {found};"></div><div class="progress-empty" style="flex: {total - found};"></div></div>
    <div class="progress-label">{found}/{total} displayed markers present on this chip</div></div>
  {disclaimer(MED)}
  {legend}
  {toolbar}
</div>'''

# ---------------------------------------------------------------- assembly
NAV = [('status', 'SUMMARY'), ('ancestry', 'ANCESTRY'), ('health', 'HEALTH'), ('nutrition', 'NUTRITION'), ('sports', 'SPORTS'),
       ('psychology', 'PSYCH'), ('cognitive', 'COGNITIVE'), ('longevity', 'LONGEVITY'), ('sleep', 'SLEEP'),
       ('immunity', 'IMMUNITY'), ('pain', 'PAIN'), ('detox', 'DETOX'), ('skin', 'SKIN'), ('vision', 'VISION'),
       ('traits', 'TRAITS'), ('pharma', 'PHARMA'), ('carrier', 'CARRIER')]
nav = '\n'.join(f'<a href="#{i}">{t}</a>' for i, t in NAV)

body = '\n'.join(sections)
# cross-references: a marker that also appears in other sections says where
for idx, r in enumerate(RESULTS):
    others = [SEC_TITLE[x['section']] for j, x in enumerate(RESULTS)
              if j != idx and x['rsid'] == r['rsid'] and x['g'] and x['section'] != r['section']]
    others = list(dict.fromkeys(others))
    tag = f' <span class="xref">↺ also in {escape(", ".join(others))}</span>' if (r['g'] and others) else ''
    body = body.replace(f'<!--X{idx}-->', tag)

footer = (f'<footer><h2 class="status-header">// ABOUT THIS DATA</h2><p>Source: {escape(META["source"])} raw data ({snps:,} SNPs, {escape(META["chip"])}). '
          f'Generated {datetime.now():%Y-%m-%d %H:%M} by scripts/generate_webpage.py. A consumer array reads selected positions, not your whole genome, '
          f'and is not clinical-grade; confirm anything that matters in an accredited clinical lab before acting. '
          f'Interpretations are general population associations, not a diagnosis.</p></footer>')

EXTRA_JS = r'''
(function () {
  var hdr = document.querySelector('header');
  function setH() { document.documentElement.style.setProperty('--hh', hdr.offsetHeight + 'px'); }
  setH(); addEventListener('resize', setH);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(setH);
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var links = Array.prototype.slice.call(document.querySelectorAll('nav a'));
  var secs = links.map(function (a) { return document.querySelector(a.getAttribute('href')); });

  function go(id) {
    var t = document.querySelector(id); if (!t) return;
    var d = t.querySelector('details'); if (d) d.open = true;
    t.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    t.setAttribute('tabindex', '-1'); t.focus({ preventScroll: true });
    history.replaceState(null, '', id);
  }
  links.forEach(function (a) { a.addEventListener('click', function (e) { e.preventDefault(); go(a.getAttribute('href')); }); });
  if (location.hash) go(location.hash);

  function active() {
    var y = hdr.offsetHeight + 40, cur = 0;
    secs.forEach(function (s, i) { if (s && s.getBoundingClientRect().top <= y) cur = i; });
    links.forEach(function (a, i) {
      if (i === cur) { a.setAttribute('aria-current', 'true'); } else { a.removeAttribute('aria-current'); }
    });
    var c = links[cur]; if (c && c.scrollIntoView && innerWidth <= 768) { nav_center(c); }
  }
  function nav_center(c) { var n = c.parentNode; n.scrollLeft = c.offsetLeft - n.clientWidth / 2 + c.clientWidth / 2; }
  addEventListener('scroll', active, { passive: true }); active();

  var q = document.getElementById('q'), flag = document.getElementById('flagonly'), count = document.getElementById('count');
  var rows = Array.prototype.slice.call(document.querySelectorAll('tr.r'));
  var sections = Array.prototype.slice.call(document.querySelectorAll('section[id]'));
  function filter() {
    var term = q.value.trim().toLowerCase(), only = flag.getAttribute('aria-pressed') === 'true', shown = 0;
    rows.forEach(function (r) {
      var ok = (!only || r.classList.contains('flag')) && (!term || r.dataset.q.indexOf(term) > -1);
      r.hidden = !ok; if (ok) shown++;
    });
    var active_filter = term || only;
    document.querySelectorAll('.subsection').forEach(function (s) {
      s.hidden = !!active_filter && !s.querySelector('tr.r:not([hidden])');
    });
    sections.forEach(function (s) {
      var any = !!s.querySelector('tr.r:not([hidden])');
      s.hidden = !!active_filter && !any;
      if (active_filter && any) s.querySelector('details').open = true;
    });
    count.textContent = active_filter ? (shown ? shown + ' of ' + rows.length + ' markers shown' : 'No markers match') : '';
  }
  q.addEventListener('input', filter);
  flag.addEventListener('click', function () {
    flag.setAttribute('aria-pressed', flag.getAttribute('aria-pressed') === 'true' ? 'false' : 'true'); filter();
  });
  function setAll(v) { document.querySelectorAll('details.sec').forEach(function (d) { d.open = v; }); }
  document.getElementById('expandall').addEventListener('click', function () { setAll(true); });
  document.getElementById('collapseall').addEventListener('click', function () { setAll(false); });
  var saved = [];
  addEventListener('beforeprint', function () {
    saved = Array.prototype.map.call(document.querySelectorAll('details'), function (d) { return d.open; });
    document.querySelectorAll('details').forEach(function (d) { d.open = true; });
  });
  addEventListener('afterprint', function () {
    document.querySelectorAll('details').forEach(function (d, i) { d.open = saved[i]; });
  });
})();
'''

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(OWNER_NAME)} | genome summary</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Jost:wght@400;500&family=Pinyon+Script&display=swap" rel="stylesheet">
<style>{load_css()}</style>
</head>
<body>
<a class="skip" href="#status">Skip to summary</a>
<header>
  <div class="header-top"><div class="logo">{inline_svg("mark").replace("<svg ", '<svg data-brand="mark" role="img" aria-label="Three of Swords mark" ', 1)}{wordmark(OWNER_NAME)}</div>
  <div class="timestamp">{datetime.now():%Y-%m-%d %H:%M}</div></div>
  <nav aria-label="Sections">{nav}</nav>
</header>
<main id="main">
{hero_html}
{status}
{body}
{footer}
</main>
<script>{EXTRA_JS}</script>
</body>
</html>'''

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Wrote {OUT_FILE}: {found}/{total} markers present, {n_flag_rows} flagged, {len(ask)} follow-ups")

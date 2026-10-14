#!/usr/bin/env python3
"""Generate webpage/dna_terminal.html (single file, inline CSS/JS).

Genotypes are read live from the genome file; English interpretations come from
the INTERP tables below, which were curated from the reports/ output. A genotype
with no entry in a table is shown as "no interpretation" rather than guessed.
CSS is reused from webpage/example.html so styling follows STYLE_GUIDE.md.
"""
import os
import re
from datetime import datetime
from html import escape

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENOME_FILE = f"{BASE_PATH}/data/my_dna_file.txt"
OUT_FILE = f"{BASE_PATH}/webpage/dna_terminal.html"
STYLE_SRC = f"{BASE_PATH}/webpage/example.html"


def load_genome():
    genome = {}
    with open(GENOME_FILE) as f:
        for line in f:
            if line.startswith('#') or line.startswith('rsid'):
                continue
            p = line.rstrip('\n').split('\t')
            if len(p) >= 5:
                gt = p[3] + p[4]
            elif len(p) == 4:
                gt = p[3]
            else:
                continue
            genome[p[0]] = None if gt in ('00', '--') else gt
    return genome


GENOME = load_genome()
STATS = {'found': 0, 'total': 0}


def geno(rsid):
    g = GENOME.get(rsid)
    return g if g else None


def norm(g):
    return ''.join(sorted(g))


# rsid -> (gene, label, {sorted genotype: (status, text)})
# status: normal | moderate | risk | info | na
def row(rsid, gene, table):
    STATS['total'] += 1
    g = geno(rsid)
    if g is None:
        return f'<tr><td>{rsid}</td><td>{escape(gene)}</td><td class="geno">--</td><td class="status-na">NOT ON CHIP</td><td>Not covered by this array</td></tr>'
    STATS['found'] += 1
    st, text = table.get(norm(g), ('na', 'No interpretation available for this genotype'))
    return (f'<tr><td>{rsid}</td><td>{escape(gene)}</td><td class="geno">{g}</td>'
            f'<td class="status-{st}">{ {"normal":"NORMAL","moderate":"MODERATE","risk":"HIGH","info":"INFO","na":"N/A"}[st] }</td>'
            f'<td>{escape(text)}</td></tr>')


def table(rows):
    body = '\n'.join(rows)
    return ('<table><tr><th>SNP</th><th>Gene</th><th>Genotype</th><th>Status</th><th>Interpretation</th></tr>\n'
            f'{body}\n</table>')


def sub(title, rows):
    return f'<div class="subsection"><div class="subsection-title">{escape(title)}</div>{table(rows)}</div>'


def finding(kind, icon, gene, desc):
    return (f'<div class="finding {kind}"><div class="finding-icon">{icon}</div><div class="finding-content">'
            f'<div class="finding-gene">{escape(gene)}</div><div class="finding-desc">{escape(desc)}</div></div></div>')


def profile(title, value, desc, color='var(--cyan)'):
    return (f'<div class="profile-box"><div class="profile-title">{escape(title)}</div>'
            f'<div class="profile-value" style="color: {color};">{escape(value)}</div>'
            f'<div class="profile-desc">{escape(desc)}</div></div>')


def disclaimer(text, critical=False):
    style = ' style="background: rgba(255, 51, 51, 0.1); border-color: var(--red); color: var(--red);"' if critical else ''
    return f'<div class="disclaimer"{style}><strong>! Important</strong> {escape(text)}</div>'


def section(sid, title, badge_cls, badge, content):
    return (f'<section id="{sid}"><div class="section-header"><span class="section-title">// {escape(title)}</span>'
            f'<span class="section-badge {badge_cls}">{escape(badge)}</span></div>'
            f'<div class="section-content">{content}</div></section>')


MED = ("Genes indicate predisposition, not destiny. This page is informational only and is not medical advice; "
       "consumer-array results are not clinical-grade. Discuss anything important with a clinician or genetic counselor.")

# ---------------------------------------------------------------- sections
sections = []

# ANCESTRY
anc = disclaimer("Only a handful of ancestry-informative markers are tested here; this is NOT an ethnicity estimate. "
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
h = disclaimer(MED)
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
s = '<div class="two-cols">' + profile('Athlete profile', 'ALL-ROUNDER', 'Balanced strength / endurance (strength 42%, endurance 50%)', 'var(--green)') \
    + profile('VO2max potential', 'GOOD', 'Estimated 67% from available markers (rough heuristic)', 'var(--green)') + '</div>'
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
p = disclaimer("Psychological genetics has small effect sizes. Do not read these as personality or diagnosis.")
p += '<div class="two-cols">' + profile('COMT type', 'VAL/MET (AG)', 'Balanced dopamine clearance; flexible under varying conditions') \
     + profile('BDNF', 'MET/MET (TT)', 'Lower activity-dependent BDNF release; exercise helps', 'var(--amber)') + '</div>'
p += sub('Markers', [
    row('rs4680', 'COMT Val158Met', {'AG': ('info', 'Balanced warrior/worrier profile')}),
    row('rs6265', 'BDNF Val66Met', {'TT': ('moderate', 'Reduced BDNF secretion; small increased stress-linked mood risk')}),
    row('rs16969968', 'CHRNA5', {'GG': ('normal', 'Standard nicotine dependence risk')}),
])
p += finding('info', 'i', 'Not covered', '5-HTTLPR, DRD2, OXTR, OPRM1 and FKBP5 markers are not on this array.')
sections.append(section('psychology', 'PSYCHOLOGY', 'moderate', 'MIXED', p))

# COGNITIVE
c = disclaimer("Cognition is highly polygenic; single variants explain very little.")
c += sub('Cognitive markers', [
    row('rs4680', 'COMT', {'AG': ('info', 'Balanced cognitive flexibility')}),
    row('rs6265', 'BDNF', {'TT': ('moderate', 'Met/Met; regular aerobic exercise is the best-supported offset')}),
    row('rs9536314', 'KLOTHO (KL-VS)', {'GT': ('normal', 'Heterozygous KL-VS; linked to better cognitive aging')}),
    row('rs759178', 'FOXP2', {'AA': ('info', 'Speech-gene variant, no known effect')}),
    row('rs1800795', 'IL-6', {'CC': ('moderate', 'Higher inflammatory tone')}),
])
c += finding('info', 'i', 'APOE', 'APOE (rs429358 / rs7412) is NOT on this array, so Alzheimer-risk APOE status is unknown here.')
sections.append(section('cognitive', 'COGNITIVE', 'good', 'NO MAJOR FLAGS', c))

# LONGEVITY
lg = sub('Longevity markers', [
    row('rs9536314', 'KLOTHO', {'GT': ('normal', 'Favorable heterozygote')}),
    row('rs5882', 'CETP', {'GG': ('normal', 'Longevity variant; higher HDL')}),
    row('rs10936599', 'TERC', {'CC': ('normal', 'Associated with longer telomeres')}),
    row('rs2736100', 'TERT', {'CC': ('normal', 'Associated with telomerase activity')}),
    row('rs1001179', 'CAT', {'CT': ('info', 'Average catalase activity')}),
])
lg += finding('info', 'i', 'Note', 'The generated report scores this 8.2/10 ("95th percentile"); that rests on a few SNPs and has no real population basis. Not shown here. FOXO3 and APOE are not on this array.')
sections.append(section('longevity', 'LONGEVITY', 'good', 'FAVORABLE MARKERS', lg))

# SLEEP
sl = '<div class="two-cols">' + profile('Chronotype', 'EVENING-LEANING', 'Moderate evening preference (delayed melatonin onset)', 'var(--amber)') \
    + profile('Restless legs', 'ELEVATED RISK', 'BTBD9 risk genotype; keep iron (ferritin) adequate', 'var(--amber)') + '</div>'
sl += sub('Sleep markers', [
    row('rs4753426', 'MTNR1B', {'CC': ('moderate', 'Delayed melatonin onset; later natural sleep time')}),
    row('rs10830963', 'MTNR1B', {'CG': ('moderate', 'Slightly reduced melatonin sensitivity')}),
    row('rs3923809', 'BTBD9', {'AA': ('risk', 'Elevated risk of restless legs / periodic limb movements')}),
    row('rs2300478', 'MEIS1', {'GT': ('na', 'No interpretation available for this genotype')}),
    row('rs1801260', 'CLOCK', {'AG': ('na', 'No interpretation available for this genotype')}),
    row('rs1823125', 'PAX8', {'AG': ('normal', 'Average sleep need (~7-8h)')}),
])
sl += finding('info', 'i', 'Caffeine', 'CYP1A2 and ADORA2A are not on this array, so caffeine sensitivity is unknown.')
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
im += finding('warning', '!', 'Overall', 'Moderate-inflammation profile. Anti-inflammatory habits (sleep, Mediterranean diet, omega-3) are the generic advice.')
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
tr += finding('warning', '?', 'Hair color not reliable', 'The generated report predicts red hair with "high" confidence from one MC1R marker. That is a single-variant guess; treat it as unconfirmed.')
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

# ---------------------------------------------------------------- status
total = STATS['total']
found = STATS['found']
snps = len(GENOME)
status = f'''
<div class="status-box" id="status">
  <div class="status-header">// SYSTEM STATUS</div>
  <div class="status-grid">
    <div class="status-item"><span class="status-label">GENOME:</span><span class="status-value">AncestryDNA</span></div>
    <div class="status-item"><span class="status-label">SEX:</span><span class="status-value">Female (XX)</span></div>
    <div class="status-item"><span class="status-label">SNPs:</span><span class="status-value">{snps:,}</span></div>
    <div class="status-item"><span class="status-label">CHIP:</span><span class="status-value">AncestryDNA array v2.0</span></div>
  </div>
  <div class="alerts-grid">
    <div class="alerts-column warnings"><h3>// ALERTS</h3>
      <div class="alert-item warning"><span class="alert-icon">!</span><span>BTBD9 AA: elevated restless-legs risk</span></div>
      <div class="alert-item warning"><span class="alert-icon">!</span><span>9p21 AG: mildly increased coronary risk</span></div>
      <div class="alert-item warning"><span class="alert-icon">!</span><span>TCF7L2 CT: moderately increased type 2 diabetes risk</span></div>
      <div class="alert-item warning"><span class="alert-icon">!</span><span>CYP2C19*2 AG: intermediate drug metabolizer</span></div>
      <div class="alert-item warning"><span class="alert-icon">!</span><span>IL-6 CC: higher inflammatory tone</span></div>
      <div class="alert-item warning"><span class="alert-icon">!</span><span>Migraine-associated variants (MTDH CC)</span></div>
      <div class="alert-item warning"><span class="alert-icon">!</span><span>APOE, CYP1A2 not on chip: unknown</span></div>
    </div>
    <div class="alerts-column highlights"><h3>// HIGHLIGHTS</h3>
      <div class="alert-item success"><span class="alert-icon">+</span><span>KLOTHO heterozygote, CETP and telomere-length variants favorable</span></div>
      <div class="alert-item success"><span class="alert-icon">+</span><span>No Factor V Leiden, no HFE C282Y</span></div>
      <div class="alert-item success"><span class="alert-icon">+</span><span>Lactose tolerant; low celiac risk (DQ8)</span></div>
      <div class="alert-item success"><span class="alert-icon">+</span><span>Efficient lactate clearance (MCT1 AA)</span></div>
      <div class="alert-item success"><span class="alert-icon">+</span><span>Protective GCH1 pain variants</span></div>
    </div>
  </div>
  <div class="progress-bar"><div class="progress-track">
    <div class="progress-fill" style="flex: {found};"></div><div class="progress-empty" style="flex: {total - found};"></div></div>
    <div class="progress-label">{found}/{total} displayed markers present on this chip</div></div>
  {disclaimer(MED)}
</div>'''

NAV = [('status', 'STATUS'), ('ancestry', 'ANCESTRY'), ('health', 'HEALTH'), ('nutrition', 'NUTRITION'), ('sports', 'SPORTS'),
       ('psychology', 'PSYCH'), ('cognitive', 'COGNITIVE'), ('longevity', 'LONGEVITY'), ('sleep', 'SLEEP'),
       ('immunity', 'IMMUNITY'), ('pain', 'PAIN'), ('detox', 'DETOX'), ('skin', 'SKIN'), ('vision', 'VISION'),
       ('traits', 'TRAITS'), ('pharma', 'PHARMA'), ('carrier', 'CARRIER')]
nav = '\n'.join(f'<a href="#{i}">{t}</a>' for i, t in NAV)

with open(STYLE_SRC, encoding='utf-8') as f:
    src = f.read()
css = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
js = re.search(r'<script>(.*?)</script>', src, re.S).group(1)

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DNA TERMINAL v1.0</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<header>
  <div class="header-top"><div class="logo">DNA TERMINAL v1.0</div>
  <div class="timestamp">{datetime.now():%Y-%m-%d %H:%M}</div></div>
  <nav>{nav}</nav>
</header>
<main>
{status}
{chr(10).join(sections)}
</main>
<script>{js}</script>
</body>
</html>'''

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Wrote {OUT_FILE}: {found}/{total} markers present")

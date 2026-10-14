#!/usr/bin/env python3
"""
Reproductive SNP Analysis Script
Analyzes reproductive health genetic markers from 23andMe data
"""

import os
from collections import defaultdict
from datetime import datetime

# Paths
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENOME_FILE = f"{BASE_PATH}/data/my_dna_file.txt"
REPORTS_PATH = f"{BASE_PATH}/reports"

# =============================================================================
# SNP DATABASE - Organized by reproductive health category
# =============================================================================

REPRODUCTIVE_SNPS = {
    "female_ovarian": {
        "name": "Ovarian reserve (women)",
        "snps": {
            "rs16991615": {
                "gene": "MCM8",
                "description": "Timing of menopause",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Early menopause - significantly earlier than average"),
                    "AG": ("moderate", "Menopause slightly earlier than average (~1 year)"),
                    "GA": ("moderate", "Menopause slightly earlier than average (~1 year)"),
                    "GG": ("normal", "Normal timing of menopause"),
                }
            },
            "rs244715": {
                "gene": "BRSK1",
                "description": "Ovarian reserve",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("moderate", "Possibly reduced ovarian reserve"),
                    "CT": ("low", "Minor effect on reserve"),
                    "TC": ("low", "Minor effect on reserve"),
                    "TT": ("normal", "Normal ovarian reserve"),
                }
            },
            "rs2303369": {
                "gene": "FNDC4",
                "description": "Ovarian function",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("moderate", "Possible early decline in ovarian function"),
                    "CT": ("low", "Minor effect"),
                    "TC": ("low", "Minor effect"),
                    "CC": ("normal", "Normal ovarian function"),
                }
            },
        }
    },

    "pcos": {
        "name": "Polycystic ovary syndrome (PCOS)",
        "snps": {
            "rs13405728": {
                "gene": "LHCGR",
                "description": "LH/hCG receptor - PCOS risk",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Increased PCOS risk"),
                    "AG": ("moderate", "Moderately increased PCOS risk"),
                    "GA": ("moderate", "Moderately increased PCOS risk"),
                    "GG": ("normal", "Average risk"),
                }
            },
            "rs13429458": {
                "gene": "LHCGR",
                "description": "LH/hCG receptor - sensitivity",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Increased PCOS risk"),
                    "AG": ("moderate", "Moderately increased risk"),
                    "GA": ("moderate", "Moderately increased risk"),
                    "GG": ("normal", "Average risk"),
                }
            },
            "rs2479106": {
                "gene": "DENND1A",
                "description": "Key PCOS gene",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Significantly increased PCOS risk"),
                    "AG": ("moderate", "Increased PCOS risk"),
                    "GA": ("moderate", "Increased PCOS risk"),
                    "GG": ("normal", "Average risk"),
                }
            },
            "rs10818854": {
                "gene": "DENND1A",
                "description": "Hyperandrogenism in PCOS",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Increased risk of hyperandrogenism"),
                    "AG": ("moderate", "Moderate risk of hyperandrogenism"),
                    "GA": ("moderate", "Moderate risk of hyperandrogenism"),
                    "GG": ("normal", "Average androgen levels"),
                }
            },
            "rs1801282": {
                "gene": "PPARG",
                "description": "Insulin resistance in PCOS",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("info", "Pro/Pro - standard variant"),
                    "CG": ("protective", "Pro/Ala - protection against insulin resistance"),
                    "GC": ("protective", "Pro/Ala - protection against insulin resistance"),
                    "GG": ("protective", "Ala/Ala - protective effect"),
                }
            },
        }
    },

    "pregnancy_risks": {
        "name": "Pregnancy risks",
        "snps": {
            "rs6025": {
                "gene": "F5 Leiden",
                "description": "Thrombophilia (risk of thrombosis during pregnancy)",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Factor V Leiden homozygous - 50x thrombosis risk! Anticoagulation required"),
                    "AG": ("high", "Factor V Leiden heterozygous - 5x thrombosis risk, monitoring is essential"),
                    "GA": ("high", "Factor V Leiden heterozygous - 5x thrombosis risk, monitoring is essential"),
                    "AC": ("high", "Factor V Leiden carrier - increased thrombosis risk"),
                    "CA": ("high", "Factor V Leiden carrier - increased thrombosis risk"),
                    "GG": ("normal", "No Factor V Leiden mutation"),
                    "CC": ("normal", "No Factor V Leiden mutation"),
                    "CG": ("normal", "No Factor V Leiden mutation"),
                    "GC": ("normal", "No Factor V Leiden mutation"),
                }
            },
            "rs1799963": {
                "gene": "F2 Prothrombin",
                "description": "Prothrombin G20210A - venous thrombosis risk",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Homozygous - very high risk of thrombosis during pregnancy"),
                    "AG": ("high", "Carrier - increased thrombosis risk, monitoring required"),
                    "GA": ("high", "Carrier - increased thrombosis risk, monitoring required"),
                    "GG": ("normal", "No prothrombin mutation"),
                }
            },
            "rs1801133": {
                "gene": "MTHFR C677T",
                "description": "Folate metabolism - neural tube defect risk",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("high", "Reduced MTHFR activity (~30%) - methylfolate required"),
                    "CT": ("moderate", "Moderately reduced activity (~65%) - methylfolate recommended"),
                    "TC": ("moderate", "Moderately reduced activity (~65%) - methylfolate recommended"),
                    "AG": ("moderate", "Heterozygous - moderately reduced activity"),
                    "GA": ("moderate", "Heterozygous - moderately reduced activity"),
                    "CC": ("normal", "Normal MTHFR activity"),
                    "AA": ("normal", "Normal MTHFR activity"),
                }
            },
            "rs1799889": {
                "gene": "SERPINE1 (PAI-1)",
                "description": "Risk of preeclampsia and pregnancy loss",
                "risk_allele": "G",
                "interpretation": {
                    "GG": ("high", "4G/4G - increased risk of preeclampsia and thrombosis"),
                    "AG": ("moderate", "4G/5G - moderate risk"),
                    "GA": ("moderate", "4G/5G - moderate risk"),
                    "AA": ("normal", "5G/5G - normal risk"),
                }
            },
        }
    },

    "gestational_diabetes": {
        "name": "Gestational diabetes",
        "snps": {
            "rs7903146": {
                "gene": "TCF7L2",
                "description": "Main risk gene for type 2 diabetes and gestational diabetes",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("high", "Significantly increased GDM risk (~80% higher)"),
                    "CT": ("moderate", "Moderately increased GDM risk (~40% higher)"),
                    "TC": ("moderate", "Moderately increased GDM risk (~40% higher)"),
                    "CC": ("normal", "Average GDM risk"),
                }
            },
            "rs10830963": {
                "gene": "MTNR1B",
                "description": "Melatonin receptor - insulin response",
                "risk_allele": "G",
                "interpretation": {
                    "GG": ("high", "Increased GDM risk, impaired insulin secretion"),
                    "CG": ("moderate", "Moderate GDM risk"),
                    "GC": ("moderate", "Moderate GDM risk"),
                    "CC": ("normal", "Average risk"),
                }
            },
        }
    },

    "estrogen_metabolism": {
        "name": "Estrogen metabolism",
        "snps": {
            "rs10046": {
                "gene": "CYP19A1",
                "description": "Aromatase - estrogen synthesis",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("info", "Increased aromatase activity, higher estrogen levels"),
                    "CT": ("info", "Intermediate aromatase activity"),
                    "TC": ("info", "Intermediate aromatase activity"),
                    "CC": ("info", "Reduced aromatase activity, lower estrogen"),
                }
            },
            "rs1056836": {
                "gene": "CYP1B1",
                "description": "4-OH estrogens (potentially genotoxic)",
                "risk_allele": "G",
                "interpretation": {
                    "GG": ("moderate", "Val/Val - increased formation of 4-OH estrogens, higher risk"),
                    "CG": ("low", "Leu/Val - moderate formation"),
                    "GC": ("low", "Leu/Val - moderate formation"),
                    "CC": ("normal", "Leu/Leu - normal estrogen metabolism"),
                }
            },
            "rs4680": {
                "gene": "COMT",
                "description": "Estrogen methylation - detoxification",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("moderate", "Met/Met - slow estrogen methylation, stays longer in the body"),
                    "AG": ("info", "Val/Met - intermediate methylation"),
                    "GA": ("info", "Val/Met - intermediate methylation"),
                    "GG": ("info", "Val/Val - fast estrogen methylation"),
                }
            },
        }
    },

    "male_testosterone": {
        "name": "Testosterone (men)",
        "snps": {
            "rs6258": {
                "gene": "SHBG",
                "description": "Binding globulin - free testosterone level",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("info", "Reduced SHBG - higher free testosterone"),
                    "CT": ("info", "Intermediate SHBG level"),
                    "TC": ("info", "Intermediate SHBG level"),
                    "CC": ("info", "Normal SHBG"),
                }
            },
            "rs12150660": {
                "gene": "SHBG",
                "description": "SHBG and testosterone levels",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("info", "Low SHBG - higher bioavailable testosterone"),
                    "GT": ("info", "Intermediate SHBG"),
                    "TG": ("info", "Intermediate SHBG"),
                    "GG": ("info", "High SHBG - lower free testosterone"),
                }
            },
            "rs727428": {
                "gene": "SHBG",
                "description": "Binding globulin level",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("info", "Low SHBG"),
                    "AG": ("info", "Intermediate SHBG"),
                    "GA": ("info", "Intermediate SHBG"),
                    "GG": ("info", "High SHBG"),
                }
            },
            "rs10046": {
                "gene": "CYP19A1",
                "description": "Aromatase - conversion of testosterone to estrogens",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("moderate", "High aromatase - greater conversion to estrogens"),
                    "CT": ("info", "Intermediate aromatase activity"),
                    "TC": ("info", "Intermediate aromatase activity"),
                    "CC": ("info", "Low aromatase - less conversion"),
                }
            },
        }
    },

    "fertility_male": {
        "name": "Male fertility",
        "snps": {
            "rs5934505": {
                "gene": "FSHB",
                "description": "Follicle-stimulating hormone - spermatogenesis",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("moderate", "Reduced FSH production - possible effect on spermatogenesis"),
                    "CT": ("low", "Minor reduction in FSH"),
                    "TC": ("low", "Minor reduction in FSH"),
                    "CC": ("normal", "Normal FSH production"),
                }
            },
            "rs1801133": {
                "gene": "MTHFR C677T",
                "description": "Sperm quality and DNA fragmentation",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("moderate", "Reduced sperm quality, increased DNA fragmentation"),
                    "CT": ("low", "Minor effect on quality"),
                    "TC": ("low", "Minor effect on quality"),
                    "AG": ("low", "Minor effect on sperm quality"),
                    "GA": ("low", "Minor effect on sperm quality"),
                    "CC": ("normal", "Normal sperm quality"),
                    "AA": ("normal", "Normal sperm quality"),
                }
            },
            "rs4880": {
                "gene": "SOD2",
                "description": "Antioxidant - protects sperm from oxidative stress",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("moderate", "Ala/Ala - reduced protection against oxidative stress"),
                    "CT": ("low", "Val/Ala - intermediate protection"),
                    "TC": ("low", "Val/Ala - intermediate protection"),
                    "CC": ("normal", "Val/Val - normal antioxidant protection"),
                }
            },
        }
    },

    "brca": {
        "name": "BRCA cancer risks (reproductive organs)",
        "snps": {
            "rs80357906": {
                "gene": "BRCA1 (5382insC)",
                "description": "BRCA1 mutation - breast and ovarian cancer",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("high", "Carrier of pathogenic BRCA1 mutation - genetic counseling required!"),
                    "CT": ("high", "Carrier of pathogenic BRCA1 mutation - genetic counseling required!"),
                    "TC": ("high", "Carrier of pathogenic BRCA1 mutation - genetic counseling required!"),
                    "TT": ("normal", "No 5382insC mutation"),
                    "--": ("normal", "No mutation"),
                }
            },
            "rs28897672": {
                "gene": "BRCA1 (C61G)",
                "description": "BRCA1 mutation - high penetrance",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("high", "Carrier of pathogenic BRCA1 mutation!"),
                    "GT": ("high", "Carrier of pathogenic BRCA1 mutation!"),
                    "TG": ("high", "Carrier of pathogenic BRCA1 mutation!"),
                    "GG": ("normal", "No C61G mutation"),
                    "--": ("normal", "No mutation"),
                }
            },
            "rs80359550": {
                "gene": "BRCA2 (6174delT)",
                "description": "BRCA2 mutation - breast, ovarian and prostate cancer",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("high", "Carrier of pathogenic BRCA2 mutation!"),
                    "AT": ("high", "Carrier of pathogenic BRCA2 mutation!"),
                    "TA": ("high", "Carrier of pathogenic BRCA2 mutation!"),
                    "AA": ("normal", "No 6174delT mutation"),
                    "--": ("normal", "No mutation"),
                }
            },
        }
    },
}


def load_genome():
    """Load genome data into a dictionary"""
    genome = {}
    with open(GENOME_FILE, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                rsid, chrom, pos, genotype = parts[0], parts[1], parts[2], parts[3]
                if len(parts) >= 5:  # AncestryDNA format: separate allele columns
                    if parts[3] + parts[4] == '00':
                        continue  # Ancestry no-call: skip so it is not mistaken for a deletion ('--')
                    genotype = parts[3] + parts[4]
                genome[rsid] = {
                    'chromosome': chrom,
                    'position': pos,
                    'genotype': genotype
                }
    return genome


def normalize_genotype(genotype):
    """Normalize genotype for comparison (sort alleles)"""
    if len(genotype) == 2:
        return ''.join(sorted(genotype))
    return genotype


def analyze_snp(snp_id, snp_info, genome_data):
    """Analyze a single SNP"""
    result = {
        'snp_id': snp_id,
        'gene': snp_info['gene'],
        'description': snp_info['description'],
        'risk_allele': snp_info['risk_allele'],
        'found': False,
        'genotype': None,
        'risk_level': None,
        'interpretation': None
    }

    if snp_id in genome_data:
        result['found'] = True
        raw_genotype = genome_data[snp_id]['genotype']
        result['genotype'] = raw_genotype
        result['chromosome'] = genome_data[snp_id]['chromosome']
        result['position'] = genome_data[snp_id]['position']

        # Try to find interpretation
        normalized = normalize_genotype(raw_genotype)
        interpretations = snp_info.get('interpretation', {})

        # Try both original and normalized genotype
        for gt in [raw_genotype, normalized]:
            if gt in interpretations:
                result['risk_level'], result['interpretation'] = interpretations[gt]
                break

        # If still not found, try reverse
        if result['interpretation'] is None and len(raw_genotype) == 2:
            reversed_gt = raw_genotype[::-1]
            if reversed_gt in interpretations:
                result['risk_level'], result['interpretation'] = interpretations[reversed_gt]

    return result


def determine_thrombophilia_status(results):
    """Determine combined thrombophilia risk from Factor V and Prothrombin"""
    factor_v = None
    prothrombin = None

    for r in results:
        if r['snp_id'] == 'rs6025':
            factor_v = r
        elif r['snp_id'] == 'rs1799963':
            prothrombin = r

    if not factor_v or not prothrombin:
        return None

    fv_risk = factor_v.get('risk_level', 'normal')
    pt_risk = prothrombin.get('risk_level', 'normal')

    # Combined risk assessment
    if fv_risk == 'high' and pt_risk == 'high':
        status = ('very_high', 'Combined thrombophilia - VERY high risk! Anticoagulation is mandatory during pregnancy')
    elif fv_risk == 'high' or pt_risk == 'high':
        if factor_v.get('genotype', '') in ['AA']:
            status = ('very_high', 'Factor V Leiden homozygous - 50x thrombosis risk')
        else:
            status = ('high', 'Thrombophilia carrier - hematologist monitoring required during pregnancy')
    else:
        status = ('normal', 'No hereditary thrombophilia')

    return {
        'factor_v': factor_v.get('genotype', 'N/A'),
        'prothrombin': prothrombin.get('genotype', 'N/A'),
        'status': status[0],
        'interpretation': status[1]
    }


def determine_estrogen_risk(results):
    """Determine estrogen metabolism risk profile"""
    cyp1b1 = None
    comt = None

    for r in results:
        if r['snp_id'] == 'rs1056836':
            cyp1b1 = r
        elif r['snp_id'] == 'rs4680':
            comt = r

    if not cyp1b1 or not comt:
        return None

    # CYP1B1 GG = high 4-OH, COMT AA = slow methylation = worst combination
    cyp1b1_high = cyp1b1.get('genotype', '') in ['GG', 'CG', 'GC']
    comt_slow = comt.get('genotype', '') in ['AA', 'AG', 'GA']

    if cyp1b1.get('genotype', '') == 'GG' and comt.get('genotype', '') == 'AA':
        status = ('high', 'Unfavorable profile: high 4-OH estrogens + slow clearance')
    elif cyp1b1_high and comt_slow:
        status = ('moderate', 'Moderate risk: elevated 4-OH estrogens, slowed methylation')
    elif cyp1b1_high or comt_slow:
        status = ('low', 'One unfavorable factor - monitor estrogen levels')
    else:
        status = ('normal', 'Favorable estrogen metabolism profile')

    return {
        'cyp1b1': cyp1b1.get('genotype', 'N/A'),
        'comt': comt.get('genotype', 'N/A'),
        'status': status[0],
        'interpretation': status[1]
    }


def generate_category_report(category, results, genome):
    """Generate report for a category"""
    cat_info = REPRODUCTIVE_SNPS[category]

    report = []
    report.append(f"# {cat_info['name']}")
    report.append(f"\nAnalysis date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("\n## Results\n")

    # Statistics
    found = sum(1 for r in results if r['found'])
    report.append(f"Markers found: {found}/{len(results)}\n")

    # Risk summary
    risk_counts = defaultdict(int)
    for r in results:
        if r['risk_level']:
            risk_counts[r['risk_level']] += 1

    if risk_counts:
        report.append("### Risk summary\n")
        risk_emoji = {
            'high': '🔴',
            'very_high': '🔴🔴',
            'moderate': '🟡',
            'low': '🟢',
            'normal': '✅',
            'protective': '🛡️',
            'info': 'ℹ️'
        }
        for risk, count in sorted(risk_counts.items()):
            emoji = risk_emoji.get(risk, '•')
            report.append(f"- {emoji} {risk}: {count}")

    report.append("\n### Detailed results\n")
    report.append("| SNP | Gene | Genotype | Risk | Interpretation |")
    report.append("|-----|-----|---------|------|---------------|")

    for r in results:
        if r['found']:
            risk_label = r['risk_level'] or 'n/a'
            interp = r['interpretation'] or 'No data'
            report.append(f"| {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {risk_label} | {interp} |")
        else:
            report.append(f"| {r['snp_id']} | {r['gene']} | - | - | Not found in genome |")

    # Special sections based on category
    if category == 'pregnancy_risks':
        report.append("\n### Thrombophilia status\n")
        thrombo = determine_thrombophilia_status(results)
        if thrombo:
            report.append(f"- Factor V Leiden (rs6025): {thrombo['factor_v']}")
            report.append(f"- Prothrombin G20210A (rs1799963): {thrombo['prothrombin']}")
            report.append(f"- **Status: {thrombo['status']}**")
            report.append(f"- {thrombo['interpretation']}")

    if category == 'estrogen_metabolism':
        report.append("\n### Estrogen metabolism profile\n")
        estrogen = determine_estrogen_risk(results)
        if estrogen:
            report.append(f"- CYP1B1 (rs1056836): {estrogen['cyp1b1']} - 4-OH estrogen formation")
            report.append(f"- COMT (rs4680): {estrogen['comt']} - methylation/clearance")
            report.append(f"- **Profile: {estrogen['status']}**")
            report.append(f"- {estrogen['interpretation']}")

    return '\n'.join(report)


def generate_summary_report(all_results, genome):
    """Generate overall reproductive health summary report"""
    report = []
    report.append("# Reproductive Health Summary Report")
    report.append(f"\nAnalysis date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("\n---\n")

    report.append("## Important disclaimers\n")
    report.append("1. **This is NOT a medical diagnosis** - informational analysis only")
    report.append("2. **Genetics determines predisposition**, not destiny")
    report.append("3. **Many SNPs have different significance** for men and women")
    report.append("4. **When planning a pregnancy** - genetic counseling is essential")
    report.append("5. **BRCA mutations** require confirmation by clinical testing\n")

    report.append("---\n")

    # Collect findings by risk level
    high_risk = []
    moderate_risk = []
    protective = []

    for category, results in all_results.items():
        for r in results:
            if r['risk_level'] in ['high', 'very_high']:
                high_risk.append((category, r))
            elif r['risk_level'] == 'moderate':
                moderate_risk.append((category, r))
            elif r['risk_level'] == 'protective':
                protective.append((category, r))

    if high_risk:
        report.append("## 🔴 High-risk markers\n")
        report.append("| Category | SNP | Gene | Genotype | Description |")
        report.append("|-----------|-----|-----|---------|----------|")
        for cat, r in high_risk:
            cat_name = REPRODUCTIVE_SNPS[cat]['name']
            report.append(f"| {cat_name} | {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {r['interpretation']} |")
        report.append("")

    if moderate_risk:
        report.append("## 🟡 Moderate-risk markers\n")
        report.append("| Category | SNP | Gene | Genotype | Description |")
        report.append("|-----------|-----|-----|---------|----------|")
        for cat, r in moderate_risk:
            cat_name = REPRODUCTIVE_SNPS[cat]['name']
            report.append(f"| {cat_name} | {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {r['interpretation']} |")
        report.append("")

    if protective:
        report.append("## 🛡️ Protective variants\n")
        report.append("| Category | SNP | Gene | Genotype | Description |")
        report.append("|-----------|-----|-----|---------|----------|")
        for cat, r in protective:
            cat_name = REPRODUCTIVE_SNPS[cat]['name']
            report.append(f"| {cat_name} | {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {r['interpretation']} |")
        report.append("")

    # Special analyses
    report.append("---\n")
    report.append("## Special analyses\n")

    # Thrombophilia status
    pregnancy_results = all_results.get('pregnancy_risks', [])
    thrombo = determine_thrombophilia_status(pregnancy_results)
    if thrombo:
        report.append("### Thrombophilia (pregnancy risk)\n")
        report.append(f"- Factor V Leiden: {thrombo['factor_v']}")
        report.append(f"- Prothrombin: {thrombo['prothrombin']}")
        report.append(f"- **Status: {thrombo['status']}**")
        report.append(f"- {thrombo['interpretation']}\n")

    # Estrogen metabolism
    estrogen_results = all_results.get('estrogen_metabolism', [])
    estrogen = determine_estrogen_risk(estrogen_results)
    if estrogen:
        report.append("### Estrogen metabolism\n")
        report.append(f"- CYP1B1 (4-OH estrogens): {estrogen['cyp1b1']}")
        report.append(f"- COMT (methylation): {estrogen['comt']}")
        report.append(f"- **Profile: {estrogen['status']}**")
        report.append(f"- {estrogen['interpretation']}\n")

    # BRCA summary
    report.append("### BRCA oncogenes\n")
    brca_results = all_results.get('brca', [])
    brca_risk = False
    for r in brca_results:
        if r['found'] and r['risk_level'] == 'high':
            brca_risk = True
            report.append(f"- **WARNING:** {r['gene']} ({r['genotype']}) - {r['interpretation']}")

    if not brca_risk:
        found_brca = [r for r in brca_results if r['found']]
        if found_brca:
            report.append("- No pathogenic BRCA1/BRCA2 mutations detected")
        else:
            report.append("- BRCA markers not found in genome (extended testing required)")

    report.append("\n---\n")
    report.append("## Analysis statistics\n")

    total_snps = 0
    found_snps = 0
    for cat, results in all_results.items():
        total_snps += len(results)
        found_snps += sum(1 for r in results if r['found'])

    report.append(f"- Total SNPs analyzed: {total_snps}")
    report.append(f"- Found in genome: {found_snps}")
    report.append(f"- Not found: {total_snps - found_snps}")

    return '\n'.join(report)


def main():
    print("=" * 60)
    print("REPRODUCTIVE HEALTH ANALYSIS FROM 23andMe GENOME")
    print("=" * 60)

    print("\n[1/4] Loading genome...")
    genome = load_genome()
    print(f"      Loaded {len(genome)} SNP")

    print("\n[2/4] Analyzing markers by category...")
    all_results = {}

    for category, cat_info in REPRODUCTIVE_SNPS.items():
        print(f"      -> {cat_info['name']}...")
        results = []
        for snp_id, snp_info in cat_info['snps'].items():
            result = analyze_snp(snp_id, snp_info, genome)
            results.append(result)
        all_results[category] = results

        # Count found
        found = sum(1 for r in results if r['found'])
        print(f"        Found: {found}/{len(results)}")

    print("\n[3/4] Generating category reports...")
    for category, results in all_results.items():
        report = generate_category_report(category, results, genome)
        category_dir = f"{REPORTS_PATH}/{category}"
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)
        report_path = f"{category_dir}/report.md"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"      -> {report_path}")

    print("\n[4/4] Generating summary report...")
    summary = generate_summary_report(all_results, genome)
    # Ensure reproductive directory exists
    repro_dir = f"{REPORTS_PATH}/reproductive"
    if not os.path.exists(repro_dir):
        os.makedirs(repro_dir)
    summary_path = f"{repro_dir}/report.md"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"      -> {summary_path}")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

    # Print key findings to console
    print("\nKEY FINDINGS:\n")

    for category, results in all_results.items():
        high_risk = [r for r in results if r['risk_level'] in ['high', 'very_high']]
        if high_risk:
            print(f"  {REPRODUCTIVE_SNPS[category]['name']}:")
            for r in high_risk:
                print(f"    * {r['gene']} ({r['genotype']}): {r['interpretation']}")
            print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Health SNP Analysis Script
Analyzes health-related genetic markers from 23andMe data
"""

import os
from collections import defaultdict
from datetime import datetime

# Paths
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENOME_FILE = f"{BASE_PATH}/data/my_dna_file.txt"
REPORTS_PATH = f"{BASE_PATH}/reports"

# =============================================================================
# SNP DATABASE - Organized by health category
# =============================================================================

HEALTH_SNPS = {
    "cardiovascular": {
        "name": "Cardiovascular Disease",
        "snps": {
            "rs10757274": {
                "gene": "9p21",
                "description": "Coronary artery disease, myocardial infarction",
                "risk_allele": "G",
                "interpretation": {
                    "GG": ("high", "Increased CAD risk (homozygous)"),
                    "AG": ("moderate", "Moderately increased CAD risk (heterozygous)"),
                    "AA": ("normal", "Normal risk"),
                }
            },
            "rs1333049": {
                "gene": "9p21",
                "description": "CAD, coronary heart disease",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("high", "Increased CAD risk"),
                    "CG": ("moderate", "Moderately increased risk"),
                    "GG": ("normal", "Normal risk"),
                }
            },
            "rs1801133": {
                "gene": "MTHFR C677T",
                "description": "Homocysteine, clotting risk",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("high", "Reduced MTHFR activity (~30%), elevated homocysteine"),
                    "CT": ("moderate", "Moderately reduced activity (~65%)"),
                    "AG": ("moderate", "C677T heterozygous - moderately reduced activity (~65%)"),
                    "CC": ("normal", "Normal MTHFR activity"),
                    "AA": ("normal", "Normal MTHFR activity"),
                }
            },
            "rs1801131": {
                "gene": "MTHFR A1298C",
                "description": "Folate metabolism",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("moderate", "Reduced MTHFR activity"),
                    "AC": ("low", "Slight reduction"),
                    "GT": ("normal", "Normal A1298C activity"),
                    "TT": ("normal", "Normal activity"),
                    "AA": ("normal", "Normal activity"),
                }
            },
            "rs6025": {
                "gene": "Factor V Leiden",
                "description": "Thrombophilia",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Factor V Leiden - high thrombosis risk!"),
                    "AG": ("high", "Factor V Leiden carrier - increased thrombosis risk"),
                    "AC": ("high", "Factor V Leiden carrier - increased thrombosis risk"),
                    "GG": ("normal", "No Factor V Leiden mutation"),
                    "CC": ("normal", "No Factor V Leiden mutation"),
                    "CG": ("normal", "No Factor V Leiden mutation"),
                }
            },
            "rs1799963": {
                "gene": "Prothrombin G20210A",
                "description": "Venous thrombosis",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Homozygous - high thrombosis risk"),
                    "AG": ("high", "Carrier - increased thrombosis risk"),
                    "GG": ("normal", "No prothrombin mutation"),
                }
            },
            "rs1800562": {
                "gene": "HFE C282Y",
                "description": "Hemochromatosis (iron accumulation)",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "C282Y homozygous - high hemochromatosis risk"),
                    "AG": ("moderate", "C282Y carrier"),
                    "GG": ("normal", "No C282Y mutation"),
                }
            },
        }
    },

    "oncology": {
        "name": "Oncology Markers",
        "snps": {
            "rs1042522": {
                "gene": "TP53 Arg72Pro",
                "description": "General cancer risk",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("moderate", "Pro/Pro - slightly increased risk of some cancers"),
                    "CG": ("normal", "Arg/Pro - heterozygous"),
                    "GG": ("normal", "Arg/Arg - standard variant"),
                }
            },
            "rs1800566": {
                "gene": "NQO1",
                "description": "Carcinogen detoxification",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("high", "No NQO1 activity - reduced detoxification"),
                    "CT": ("moderate", "Reduced NQO1 activity"),
                    "CC": ("normal", "Normal detoxification"),
                }
            },
            "rs1695": {
                "gene": "GSTP1",
                "description": "Detoxification",
                "risk_allele": "G",
                "interpretation": {
                    "GG": ("moderate", "Reduced detoxification via GSTP1"),
                    "AG": ("low", "Slightly reduced activity"),
                    "AA": ("normal", "Normal GSTP1 activity"),
                }
            },
            "rs1048943": {
                "gene": "CYP1A1",
                "description": "Carcinogen metabolism",
                "risk_allele": "G",
                "interpretation": {
                    "GG": ("moderate", "Increased carcinogen activation"),
                    "AG": ("low", "Slightly increased"),
                    "AA": ("normal", "Normal metabolism"),
                }
            },
        }
    },

    "neurology": {
        "name": "Neurology and Mental Health",
        "snps": {
            "rs429358": {
                "gene": "APOE (ε4 marker 1)",
                "description": "Alzheimer's disease",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("high", "Probably ε4/ε4 - significantly increased risk"),
                    "CT": ("moderate", "Probably ε4 carrier"),
                    "TT": ("normal", "No ε4 allele"),
                }
            },
            "rs7412": {
                "gene": "APOE (ε marker 2)",
                "description": "Alzheimer's disease",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("info", "Used to determine APOE genotype"),
                    "CT": ("info", "Used to determine APOE genotype"),
                    "TT": ("info", "Used to determine APOE genotype"),
                }
            },
            "rs6265": {
                "gene": "BDNF Val66Met",
                "description": "Memory, neuroplasticity, depression",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("moderate", "Met/Met - reduced BDNF secretion, depression risk"),
                    "TT": ("moderate", "Met/Met - reduced BDNF secretion, depression risk"),
                    "AG": ("low", "Val/Met - slightly reduced secretion"),
                    "CT": ("low", "Val/Met - slightly reduced secretion"),
                    "GG": ("normal", "Val/Val - normal BDNF secretion"),
                    "CC": ("normal", "Val/Val - normal BDNF secretion"),
                }
            },
            "rs4680": {
                "gene": "COMT Val158Met",
                "description": "Stress, anxiety, cognitive function",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("info", "Met/Met - 'Worrier' - better cognition, but higher anxiety"),
                    "AG": ("info", "Val/Met - balanced type"),
                    "GG": ("info", "Val/Val - 'Warrior' - stress-resistant, poorer memory"),
                }
            },
            "rs1800497": {
                "gene": "DRD2/ANKK1 Taq1A",
                "description": "Dopamine, addictions",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("moderate", "A1/A1 - fewer D2 receptors, addiction risk"),
                    "AG": ("low", "A1/A2 - moderately reduced D2 receptors"),
                    "GG": ("normal", "A2/A2 - normal number of D2 receptors"),
                }
            },
            "rs53576": {
                "gene": "OXTR",
                "description": "Oxytocin, empathy, sociability",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("info", "Lower empathy and social sensitivity"),
                    "AG": ("info", "Average level"),
                    "GG": ("info", "Higher empathy and social sensitivity"),
                }
            },
        }
    },

    "diabetes": {
        "name": "Diabetes and Metabolism",
        "snps": {
            "rs7903146": {
                "gene": "TCF7L2",
                "description": "Type 2 diabetes (main marker)",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("high", "Significantly increased T2D risk (~80%)"),
                    "CT": ("moderate", "Increased T2D risk (~40%)"),
                    "CC": ("normal", "Normal risk"),
                }
            },
            "rs1801282": {
                "gene": "PPARG Pro12Ala",
                "description": "Insulin, obesity",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("normal", "Pro/Pro - standard variant"),
                    "CG": ("protective", "Pro/Ala - protective effect against T2D"),
                    "GG": ("protective", "Ala/Ala - protective effect"),
                }
            },
            "rs5219": {
                "gene": "KCNJ11",
                "description": "Type 2 diabetes",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("moderate", "Increased T2D risk"),
                    "CT": ("low", "Slightly increased risk"),
                    "CC": ("normal", "Normal risk"),
                }
            },
            "rs9939609": {
                "gene": "FTO",
                "description": "Obesity (main marker)",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Increased obesity risk (+3 kg on average)"),
                    "AT": ("moderate", "Moderately increased risk (+1.5 kg)"),
                    "TT": ("normal", "Normal risk"),
                }
            },
            "rs17782313": {
                "gene": "MC4R",
                "description": "Appetite, obesity",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("moderate", "Increased appetite and obesity risk"),
                    "CT": ("low", "Slightly increased risk"),
                    "TT": ("normal", "Normal appetite control"),
                }
            },
        }
    },

    "autoimmune": {
        "name": "Autoimmune Diseases",
        "snps": {
            "rs2187668": {
                "gene": "HLA-DQ2.5",
                "description": "Celiac disease",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("high", "HLA-DQ2.5 - high celiac disease risk"),
                    "CT": ("moderate", "HLA-DQ2.5 carrier"),
                    "CC": ("normal", "Low celiac disease risk"),
                }
            },
            "rs7454108": {
                "gene": "HLA-DQ8",
                "description": "Celiac disease, type 1 diabetes",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("moderate", "HLA-DQ8 - celiac disease and T1D risk"),
                    "CT": ("low", "Carrier"),
                    "TT": ("normal", "Low risk"),
                }
            },
            "rs2476601": {
                "gene": "PTPN22",
                "description": "Autoimmune (RA, SLE, T1D)",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "High risk of autoimmune diseases"),
                    "AG": ("moderate", "Increased autoimmune risk"),
                    "GG": ("normal", "Normal risk"),
                }
            },
            "rs3135388": {
                "gene": "HLA-DRB1",
                "description": "Multiple sclerosis",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("moderate", "Increased multiple sclerosis risk"),
                    "AG": ("low", "Slightly increased risk"),
                    "GG": ("normal", "Normal risk"),
                }
            },
        }
    },

    "pharmacogenomics": {
        "name": "Pharmacogenomics",
        "snps": {
            "rs4244285": {
                "gene": "CYP2C19*2",
                "description": "Metabolism: Clopidogrel, omeprazole, antidepressants",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Poor metabolizer - clopidogrel NOT effective!"),
                    "AG": ("moderate", "Intermediate metabolizer"),
                    "GG": ("normal", "Normal metabolizer"),
                }
            },
            "rs4986893": {
                "gene": "CYP2C19*3",
                "description": "Antidepressant metabolism",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Poor metabolizer"),
                    "AG": ("moderate", "Intermediate"),
                    "GG": ("normal", "Normal metabolizer"),
                }
            },
            "rs1065852": {
                "gene": "CYP2D6",
                "description": "Metabolism: Codeine, tamoxifen, antidepressants",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Poor metabolizer - codeine does not work"),
                    "AG": ("moderate", "Intermediate metabolizer"),
                    "GG": ("normal", "Normal metabolizer"),
                }
            },
            "rs9923231": {
                "gene": "VKORC1",
                "description": "Warfarin sensitivity",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("high", "High sensitivity - low warfarin dose needed"),
                    "CT": ("moderate", "Moderate sensitivity"),
                    "CC": ("normal", "Standard warfarin dose"),
                }
            },
            "rs1799853": {
                "gene": "CYP2C9*2",
                "description": "Metabolism: Warfarin, NSAIDs",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("high", "Poor metabolizer - reduce warfarin dose"),
                    "CT": ("moderate", "Intermediate metabolizer"),
                    "CC": ("normal", "Normal metabolizer"),
                }
            },
            "rs1057910": {
                "gene": "CYP2C9*3",
                "description": "Warfarin metabolism",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("high", "Poor metabolizer"),
                    "AC": ("moderate", "Intermediate"),
                    "AA": ("normal", "Normal metabolizer"),
                }
            },
            "rs4149056": {
                "gene": "SLCO1B1",
                "description": "Statin transport (myopathy risk)",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("high", "High risk of statin-induced myopathy!"),
                    "CT": ("moderate", "Increased myopathy risk"),
                    "TT": ("normal", "Normal risk"),
                }
            },
            "rs1800460": {
                "gene": "TPMT",
                "description": "Azathioprine metabolism",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Poor metabolizer - azathioprine toxicity!"),
                    "TT": ("high", "Poor metabolizer - azathioprine toxicity!"),
                    "AG": ("moderate", "Intermediate - reduce dose"),
                    "CT": ("moderate", "Intermediate - reduce dose"),
                    "GG": ("normal", "Normal metabolizer"),
                    "CC": ("normal", "Normal metabolizer"),
                }
            },
        }
    },

    "other": {
        "name": "Other Important Markers",
        "snps": {
            "rs1800629": {
                "gene": "TNF-α",
                "description": "Inflammation",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("moderate", "Increased TNF-α production, chronic inflammation"),
                    "AG": ("low", "Slightly increased"),
                    "GG": ("normal", "Normal level"),
                }
            },
            "rs1143634": {
                "gene": "IL-1β",
                "description": "Inflammation",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("moderate", "Increased inflammation"),
                    "CT": ("low", "Slightly increased"),
                    "AG": ("low", "Slightly increased IL-1β production"),
                    "CC": ("normal", "Normal level"),
                    "AA": ("normal", "Normal level"),
                }
            },
            "rs1800795": {
                "gene": "IL-6",
                "description": "Inflammation, immunity",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("moderate", "Increased IL-6 production"),
                    "CG": ("low", "Moderately increased"),
                    "GG": ("normal", "Normal level"),
                }
            },
            "rs7041": {
                "gene": "GC (VDBP)",
                "description": "Vitamin D metabolism",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("moderate", "Gc1F/1F - reduced vitamin D level"),
                    "GT": ("low", "Slightly reduced"),
                    "AC": ("low", "Gc1S/1F - slightly reduced vitamin D"),
                    "GG": ("normal", "Gc1S/1S - normal level"),
                    "AA": ("normal", "Normal level"),
                    "CC": ("normal", "Normal level"),
                }
            },
            "rs2282679": {
                "gene": "GC",
                "description": "Vitamin D level",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("moderate", "Reduced vitamin D"),
                    "AC": ("low", "Slightly reduced"),
                    "GT": ("low", "Slightly reduced vitamin D level"),
                    "GG": ("normal", "Normal level"),
                    "TT": ("normal", "Normal level"),
                    "AA": ("normal", "Normal level"),
                }
            },
            "rs855791": {
                "gene": "TMPRSS6",
                "description": "Iron level",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("moderate", "Reduced iron level"),
                    "CT": ("low", "Slightly reduced"),
                    "AG": ("low", "Slightly reduced iron level"),
                    "GG": ("normal", "Normal iron level"),
                    "AA": ("normal", "Normal level"),
                    "CC": ("normal", "Normal level"),
                }
            },
            "rs1799945": {
                "gene": "HFE H63D",
                "description": "Hemochromatosis (mild form)",
                "risk_allele": "G",
                "interpretation": {
                    "GG": ("moderate", "H63D homozygous - mild risk of iron accumulation"),
                    "CG": ("low", "H63D carrier"),
                    "CC": ("normal", "No H63D mutation"),
                }
            },
        }
    }
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


def determine_apoe_genotype(genome):
    """Determine APOE genotype from rs429358 and rs7412"""
    rs429358 = genome.get('rs429358', {}).get('genotype', '')
    rs7412 = genome.get('rs7412', {}).get('genotype', '')

    # APOE determination table
    # rs429358 (C=ε4), rs7412 (T=ε2)
    apoe_table = {
        ('TT', 'CC'): ('ε2/ε2', 'protective', 'Protective genotype - reduced Alzheimer risk'),
        ('TT', 'CT'): ('ε2/ε3', 'protective', 'Slightly reduced risk'),
        ('CT', 'CC'): ('ε2/ε4', 'moderate', 'Mixed - one protective, one risk allele'),
        ('TT', 'TT'): ('ε3/ε3', 'normal', 'Most common genotype - average risk'),
        ('CT', 'CT'): ('ε3/ε4', 'high', 'Increased Alzheimer risk (~3x)'),
        ('CC', 'TT'): ('ε4/ε4', 'very_high', 'Significantly increased Alzheimer risk (~12x)'),
        ('CT', 'TT'): ('ε3/ε4', 'high', 'Increased Alzheimer risk (~3x)'),
        ('CC', 'CT'): ('ε4/ε4 or ε3/ε4', 'high', 'Increased risk'),
    }

    # Normalize genotypes
    n429 = normalize_genotype(rs429358)
    n7412 = normalize_genotype(rs7412)

    for (g1, g2), (apoe, risk, desc) in apoe_table.items():
        if normalize_genotype(g1) == n429 and normalize_genotype(g2) == n7412:
            return {
                'rs429358': rs429358,
                'rs7412': rs7412,
                'apoe_genotype': apoe,
                'risk_level': risk,
                'interpretation': desc
            }

    return {
        'rs429358': rs429358,
        'rs7412': rs7412,
        'apoe_genotype': 'Undetermined',
        'risk_level': 'unknown',
        'interpretation': f'Combination {rs429358}/{rs7412} not in lookup table'
    }


def determine_mthfr_status(results):
    """Determine combined MTHFR status"""
    c677t = None
    a1298c = None

    for r in results:
        if r['snp_id'] == 'rs1801133':
            c677t = r['genotype']
        elif r['snp_id'] == 'rs1801131':
            a1298c = r['genotype']

    if not c677t or not a1298c:
        return None

    # Normalize genotypes - C677T: C>T mutation, A1298C: A>C mutation
    # Count risk alleles
    c677t_risk = c677t.count('T') if c677t else 0  # T is risk
    # For A1298C, the genotype might be reported as G/T (complement strand)
    # A>C on forward = T>G on reverse, so G is risk on reverse
    a1298c_risk = a1298c.count('C') + a1298c.count('G') if a1298c else 0

    # Check for homozygous risk
    is_c677t_homo = c677t in ['TT', 'AA']  # TT on forward, AA could be different strand
    is_c677t_hetero = 'T' in c677t and 'C' in c677t or 'A' in c677t and 'G' in c677t
    is_a1298c_homo = a1298c in ['CC', 'GG']
    is_a1298c_hetero = len(set(a1298c)) == 2 if a1298c else False

    # More lenient detection: AG for C677T = heterozygote (strand complement)
    if c677t == 'AG':
        is_c677t_hetero = True
    if a1298c == 'GT':
        is_a1298c_hetero = False  # GT likely means normal/normal on this assay

    if is_c677t_homo and is_a1298c_homo:
        status = ('severe', 'Significant reduction in MTHFR activity (~10-20%)')
    elif is_c677t_homo and is_a1298c_hetero:
        status = ('severe', 'Significant reduction in MTHFR activity')
    elif is_c677t_homo:
        status = ('moderate', 'C677T homozygous - reduced MTHFR activity (~30%)')
    elif is_c677t_hetero and is_a1298c_homo:
        status = ('moderate', 'Compound - moderate reduction in activity')
    elif is_c677t_hetero and is_a1298c_hetero:
        status = ('moderate', 'Compound heterozygous - moderate reduction')
    elif is_c677t_hetero:
        status = ('mild', 'C677T heterozygous - slight reduction (~65%)')
    elif is_a1298c_homo:
        status = ('mild', 'A1298C homozygous - slight reduction')
    else:
        status = ('normal', 'Normal MTHFR activity')

    return {
        'c677t': c677t,
        'a1298c': a1298c,
        'status': status[0],
        'interpretation': status[1]
    }


def generate_category_report(category, results, genome):
    """Generate report for a category"""
    cat_info = HEALTH_SNPS[category]

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

    # Special sections
    if category == 'neurology':
        report.append("\n### APOE genotype (Alzheimer's risk)\n")
        apoe = determine_apoe_genotype(genome)
        report.append(f"- rs429358: {apoe['rs429358']}")
        report.append(f"- rs7412: {apoe['rs7412']}")
        report.append(f"- **APOE genotype: {apoe['apoe_genotype']}**")
        report.append(f"- Risk: {apoe['risk_level']}")
        report.append(f"- {apoe['interpretation']}")

    if category == 'cardiovascular':
        mthfr = determine_mthfr_status(results)
        if mthfr:
            report.append("\n### MTHFR status\n")
            report.append(f"- C677T (rs1801133): {mthfr['c677t']}")
            report.append(f"- A1298C (rs1801131): {mthfr['a1298c']}")
            report.append(f"- **Status: {mthfr['status']}**")
            report.append(f"- {mthfr['interpretation']}")

    return '\n'.join(report)


def generate_summary_report(all_results, genome):
    """Generate overall summary report"""
    report = []
    report.append("# 📊 Health Summary Report")
    report.append(f"\nAnalysis date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("\n---\n")

    report.append("## ⚠️ Important Disclaimers\n")
    report.append("1. **This is NOT a medical diagnosis** — informational analysis only (not medical advice)")
    report.append("2. **Having a risk allele ≠ disease** — penetrance varies")
    report.append("3. **Most diseases are polygenic** — they depend on many genes + environment")
    report.append("4. **For medical decisions** — consulting a geneticist is mandatory\n")

    report.append("---\n")

    # Collect high-risk findings
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
        report.append("## 🔴 High-Risk Markers\n")
        report.append("| Category | SNP | Gene | Genotype | Description |")
        report.append("|-----------|-----|-----|---------|----------|")
        for cat, r in high_risk:
            cat_name = HEALTH_SNPS[cat]['name']
            report.append(f"| {cat_name} | {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {r['interpretation']} |")
        report.append("")

    if moderate_risk:
        report.append("## 🟡 Moderate-Risk Markers\n")
        report.append("| Category | SNP | Gene | Genotype | Description |")
        report.append("|-----------|-----|-----|---------|----------|")
        for cat, r in moderate_risk:
            cat_name = HEALTH_SNPS[cat]['name']
            report.append(f"| {cat_name} | {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {r['interpretation']} |")
        report.append("")

    if protective:
        report.append("## 🛡️ Protective Variants\n")
        report.append("| Category | SNP | Gene | Genotype | Description |")
        report.append("|-----------|-----|-----|---------|----------|")
        for cat, r in protective:
            cat_name = HEALTH_SNPS[cat]['name']
            report.append(f"| {cat_name} | {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {r['interpretation']} |")
        report.append("")

    # Special analyses
    report.append("---\n")
    report.append("## 🧬 Special Analyses\n")

    # APOE
    apoe = determine_apoe_genotype(genome)
    report.append("### APOE (Alzheimer's Disease)\n")
    report.append(f"- **Genotype: {apoe['apoe_genotype']}**")
    report.append(f"- {apoe['interpretation']}\n")

    # MTHFR
    cardio_results = all_results.get('cardiovascular', [])
    mthfr = determine_mthfr_status(cardio_results)
    if mthfr:
        report.append("### MTHFR (Folate Metabolism)\n")
        report.append(f"- C677T: {mthfr['c677t']}, A1298C: {mthfr['a1298c']}")
        report.append(f"- **Status: {mthfr['status']}**")
        report.append(f"- {mthfr['interpretation']}\n")

    # Pharmacogenomics summary
    report.append("### 💊 Pharmacogenomics - key findings\n")
    pharma = all_results.get('pharmacogenomics', [])
    important_drugs = []
    for r in pharma:
        if r['found'] and r['risk_level'] in ['high', 'moderate']:
            important_drugs.append(f"- **{r['gene']}** ({r['genotype']}): {r['interpretation']}")

    if important_drugs:
        report.extend(important_drugs)
    else:
        report.append("- No critical pharmacogenetic findings")

    report.append("\n---\n")
    report.append("## 📈 Analysis Statistics\n")

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
    print("23andMe GENOME HEALTH ANALYSIS")
    print("=" * 60)

    print("\n[1/4] Loading genome...")
    genome = load_genome()
    print(f"      Loaded {len(genome)} SNP")

    print("\n[2/4] Analyzing markers by category...")
    all_results = {}

    for category, cat_info in HEALTH_SNPS.items():
        print(f"      → {cat_info['name']}...")
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
        report_path = f"{REPORTS_PATH}/{category}/report.md"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"      → {report_path}")

    print("\n[4/4] Generating summary report...")
    summary = generate_summary_report(all_results, genome)
    summary_path = f"{REPORTS_PATH}/health_summary.md"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"      → {summary_path}")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

    # Print key findings to console
    print("\n🔑 KEY FINDINGS:\n")

    for category, results in all_results.items():
        high_risk = [r for r in results if r['risk_level'] in ['high', 'very_high']]
        if high_risk:
            print(f"⚠️  {HEALTH_SNPS[category]['name']}:")
            for r in high_risk:
                print(f"    • {r['gene']} ({r['genotype']}): {r['interpretation']}")
            print()


if __name__ == "__main__":
    main()

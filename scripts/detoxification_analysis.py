#!/usr/bin/env python3
"""
Detoxification SNP Analysis Script
Analyzes detoxification-related genetic markers from 23andMe data
"""

import os
from collections import defaultdict
from datetime import datetime

# Paths
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENOME_FILE = f"{BASE_PATH}/data/my_dna_file.txt"
REPORTS_PATH = f"{BASE_PATH}/reports"

# =============================================================================
# SNP DATABASE - Organized by detoxification category
# =============================================================================

DETOX_SNPS = {
    "phase1_cyp450": {
        "name": "Phase I detoxification (CYP450)",
        "snps": {
            "rs762551": {
                "gene": "CYP1A2",
                "description": "Caffeine metabolism",
                "risk_allele": "C",
                "interpretation": {
                    "AA": ("fast", "Fast caffeine metabolizer - caffeine is cleared quickly"),
                    "AC": ("intermediate", "Intermediate caffeine metabolizer"),
                    "CA": ("intermediate", "Intermediate caffeine metabolizer"),
                    "CC": ("slow", "Slow caffeine metabolizer - caffeine lingers longer"),
                }
            },
            "rs1056836": {
                "gene": "CYP1B1",
                "description": "Estrogen metabolism",
                "risk_allele": "G",
                "interpretation": {
                    "GG": ("high", "Increased formation of 4-OH estrogens (more carcinogenic)"),
                    "CG": ("moderate", "Moderately increased formation of 4-OH estrogens"),
                    "GC": ("moderate", "Moderately increased formation of 4-OH estrogens"),
                    "CC": ("normal", "Normal estrogen metabolism (more 2-OH)"),
                }
            },
            "rs1799853": {
                "gene": "CYP2C9*2",
                "description": "Metabolism of NSAIDs, warfarin",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("slow", "Slow metabolizer - reduce NSAID/warfarin dose"),
                    "CT": ("intermediate", "Intermediate metabolizer"),
                    "TC": ("intermediate", "Intermediate metabolizer"),
                    "CC": ("normal", "Normal CYP2C9 metabolizer"),
                }
            },
            "rs1057910": {
                "gene": "CYP2C9*3",
                "description": "Metabolism of NSAIDs, warfarin",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("slow", "Slow metabolizer - significantly reduce dose"),
                    "AC": ("intermediate", "Intermediate metabolizer"),
                    "CA": ("intermediate", "Intermediate metabolizer"),
                    "AA": ("normal", "Normal CYP2C9*3 metabolizer"),
                }
            },
            "rs4244285": {
                "gene": "CYP2C19*2",
                "description": "Metabolism: clopidogrel, omeprazole, antidepressants",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("slow", "Poor metabolizer - clopidogrel is NOT effective!"),
                    "AG": ("intermediate", "Intermediate metabolizer"),
                    "GA": ("intermediate", "Intermediate metabolizer"),
                    "GG": ("normal", "Normal CYP2C19 metabolizer"),
                }
            },
            "rs12248560": {
                "gene": "CYP2C19*17",
                "description": "Ultrarapid metabolism",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("ultrafast", "Ultrarapid metabolizer - a dose increase may be needed"),
                    "CT": ("fast", "Fast metabolizer"),
                    "TC": ("fast", "Fast metabolizer"),
                    "CC": ("normal", "Normal CYP2C19 metabolizer"),
                }
            },
        }
    },

    "phase2_conjugation": {
        "name": "Phase II conjugation",
        "snps": {
            "rs1695": {
                "gene": "GSTP1",
                "description": "Glutathione S-transferase - detoxification via glutathione",
                "risk_allele": "G",
                "interpretation": {
                    "AA": ("normal", "Normal GSTP1 activity - efficient detoxification"),
                    "AG": ("moderate", "Slightly reduced GSTP1 activity"),
                    "GA": ("moderate", "Slightly reduced GSTP1 activity"),
                    "GG": ("low", "Reduced GSTP1 activity - less efficient detoxification"),
                }
            },
            "rs1801280": {
                "gene": "NAT2",
                "description": "N-acetyltransferase 2 - acetylation",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("slow", "Slow acetylator - increased risk of isoniazid toxicity"),
                    "AG": ("intermediate", "Intermediate acetylator"),
                    "GA": ("intermediate", "Intermediate acetylator"),
                    "GG": ("fast", "Fast acetylator"),
                }
            },
            "rs1799930": {
                "gene": "NAT2",
                "description": "N-acetyltransferase 2 - second variant",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("slow", "Slow acetylator"),
                    "AG": ("intermediate", "Intermediate acetylator"),
                    "GA": ("intermediate", "Intermediate acetylator"),
                    "GG": ("fast", "Fast acetylator"),
                }
            },
            "rs8175347": {
                "gene": "UGT1A1*28",
                "description": "Gilbert syndrome - bilirubin conjugation",
                "risk_allele": "TA7",
                "interpretation": {
                    "6/6": ("normal", "Normal UGT1A1 activity"),
                    "6/7": ("moderate", "Carrier - moderately reduced bilirubin conjugation"),
                    "7/7": ("low", "Gilbert syndrome - jaundice during stress/fasting"),
                    "AA": ("normal", "Likely normal UGT1A1 activity"),
                    "AT": ("moderate", "Likely UGT1A1*28 carrier"),
                    "TA": ("moderate", "Likely UGT1A1*28 carrier"),
                    "TT": ("low", "Likely Gilbert syndrome"),
                }
            },
        }
    },

    "antioxidants": {
        "name": "Antioxidant defense",
        "snps": {
            "rs4880": {
                "gene": "SOD2 (MnSOD)",
                "description": "Superoxide dismutase - mitochondrial protection",
                "risk_allele": "T",
                "interpretation": {
                    "CC": ("high", "High SOD2 activity - effective mitochondrial protection"),
                    "CT": ("moderate", "Intermediate SOD2 activity"),
                    "TC": ("moderate", "Intermediate SOD2 activity"),
                    "TT": ("low", "Low SOD2 activity - antioxidants needed"),
                    "AA": ("low", "Low SOD2 activity (Ala/Ala) - antioxidants needed"),
                    "AG": ("moderate", "Intermediate SOD2 activity"),
                    "GA": ("moderate", "Intermediate SOD2 activity"),
                    "GG": ("high", "High SOD2 activity"),
                }
            },
            "rs1050450": {
                "gene": "GPX1",
                "description": "Glutathione peroxidase - protection against peroxides",
                "risk_allele": "T",
                "interpretation": {
                    "CC": ("normal", "Normal GPX1 activity"),
                    "CT": ("moderate", "Slightly reduced GPX1 activity"),
                    "TC": ("moderate", "Slightly reduced GPX1 activity"),
                    "TT": ("low", "Reduced GPX1 activity - selenium needed"),
                }
            },
            "rs1001179": {
                "gene": "CAT",
                "description": "Catalase - hydrogen peroxide breakdown",
                "risk_allele": "T",
                "interpretation": {
                    "CC": ("normal", "Normal catalase activity"),
                    "CT": ("moderate", "Slightly reduced catalase activity"),
                    "TC": ("moderate", "Slightly reduced catalase activity"),
                    "TT": ("low", "Reduced catalase activity"),
                }
            },
        }
    },

    "methylation": {
        "name": "Methylation",
        "snps": {
            "rs1801133": {
                "gene": "MTHFR C677T",
                "description": "Methylenetetrahydrofolate reductase - key enzyme",
                "risk_allele": "T",
                "interpretation": {
                    "CC": ("normal", "100% MTHFR activity - normal methylation"),
                    "CT": ("moderate", "~65% MTHFR activity - slightly reduced methylation"),
                    "TC": ("moderate", "~65% MTHFR activity - slightly reduced methylation"),
                    "TT": ("low", "~30% MTHFR activity - significantly reduced methylation"),
                    "AA": ("normal", "Normal MTHFR activity"),
                    "AG": ("moderate", "C677T heterozygote - moderately reduced activity (~65%)"),
                    "GA": ("moderate", "C677T heterozygote - moderately reduced activity (~65%)"),
                    "GG": ("normal", "Normal MTHFR activity"),
                }
            },
            "rs1801131": {
                "gene": "MTHFR A1298C",
                "description": "Second MTHFR variant",
                "risk_allele": "C",
                "interpretation": {
                    "AA": ("normal", "Normal A1298C activity"),
                    "AC": ("low", "Slightly reduced activity"),
                    "CA": ("low", "Slightly reduced activity"),
                    "CC": ("moderate", "Reduced MTHFR activity"),
                    "TT": ("normal", "Normal activity"),
                    "GT": ("normal", "Normal A1298C activity"),
                    "TG": ("normal", "Normal A1298C activity"),
                    "GG": ("moderate", "Reduced A1298C activity"),
                }
            },
            "rs1805087": {
                "gene": "MTR (MS)",
                "description": "Methionine synthase - B12-dependent methylation",
                "risk_allele": "G",
                "interpretation": {
                    "AA": ("normal", "Normal MTR activity"),
                    "AG": ("moderate", "Slightly reduced MTR activity - B12 needed"),
                    "GA": ("moderate", "Slightly reduced MTR activity - B12 needed"),
                    "GG": ("low", "Reduced MTR activity - B12 needed"),
                }
            },
            "rs1801394": {
                "gene": "MTRR",
                "description": "Methionine synthase reductase - B12 regeneration",
                "risk_allele": "G",
                "interpretation": {
                    "AA": ("normal", "Normal MTRR activity"),
                    "AG": ("moderate", "Slightly reduced B12 regeneration"),
                    "GA": ("moderate", "Slightly reduced B12 regeneration"),
                    "GG": ("low", "Reduced B12 regeneration - methyl-B12 needed"),
                }
            },
        }
    },

    "heavy_metals": {
        "name": "Heavy metals",
        "snps": {
            "rs662": {
                "gene": "PON1 Q192R",
                "description": "Paraoxonase - detoxification of pesticides and mercury",
                "risk_allele": "A",
                "interpretation": {
                    "GG": ("normal", "Normal PON1 activity - good protection against pesticides"),
                    "AG": ("moderate", "Moderately reduced PON1 activity"),
                    "GA": ("moderate", "Moderately reduced PON1 activity"),
                    "AA": ("low", "Reduced PON1 activity - vulnerability to pesticides/mercury"),
                }
            },
            "rs11191439": {
                "gene": "AS3MT",
                "description": "Arsenite methyltransferase - arsenic metabolism",
                "risk_allele": "T",
                "interpretation": {
                    "CC": ("normal", "Efficient arsenic elimination"),
                    "CT": ("moderate", "Moderately reduced arsenic elimination"),
                    "TC": ("moderate", "Moderately reduced arsenic elimination"),
                    "TT": ("low", "Reduced arsenic elimination - avoid exposure"),
                }
            },
        }
    },

    "transporters": {
        "name": "Transporters",
        "snps": {
            "rs1045642": {
                "gene": "ABCB1 (MDR1/P-glycoprotein)",
                "description": "Efflux of toxins and drugs from cells",
                "risk_allele": "T",
                "interpretation": {
                    "CC": ("high", "High P-glycoprotein activity - rapid efflux"),
                    "CT": ("normal", "Normal P-glycoprotein activity"),
                    "TC": ("normal", "Normal P-glycoprotein activity"),
                    "TT": ("low", "Reduced P-glycoprotein activity - toxin accumulation"),
                }
            },
            "rs4149056": {
                "gene": "SLCO1B1",
                "description": "Statin transport into the liver",
                "risk_allele": "C",
                "interpretation": {
                    "TT": ("normal", "Normal statin transport"),
                    "TC": ("moderate", "Increased risk of statin myopathy (~4x)"),
                    "CT": ("moderate", "Increased risk of statin myopathy (~4x)"),
                    "CC": ("high", "High risk of statin myopathy (~17x) - avoid high doses!"),
                }
            },
        }
    },

    "alcohol": {
        "name": "Alcohol",
        "snps": {
            "rs1229984": {
                "gene": "ADH1B",
                "description": "Alcohol dehydrogenase - alcohol oxidation",
                "risk_allele": "A",
                "interpretation": {
                    "GG": ("slow", "Slow alcohol oxidation - longer intoxication"),
                    "AG": ("fast", "Fast alcohol oxidation - faster sobering up"),
                    "GA": ("fast", "Fast alcohol oxidation - faster sobering up"),
                    "AA": ("fast", "Very fast alcohol oxidation"),
                }
            },
            "rs671": {
                "gene": "ALDH2",
                "description": "Aldehyde dehydrogenase - acetaldehyde breakdown",
                "risk_allele": "A",
                "interpretation": {
                    "GG": ("normal", "Normal ALDH2 activity - good alcohol tolerance"),
                    "AG": ("low", "Reduced ALDH2 activity - flushing, nausea from alcohol"),
                    "GA": ("low", "Reduced ALDH2 activity - flushing, nausea from alcohol"),
                    "AA": ("very_low", "No ALDH2 activity - severe flushing, alcohol intolerance"),
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
                    genotype = '--' if parts[3] + parts[4] == '00' else parts[3] + parts[4]
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


def determine_mthfr_status(results):
    """Determine combined MTHFR status from methylation results"""
    c677t = None
    a1298c = None

    for r in results:
        if r['snp_id'] == 'rs1801133':
            c677t = r['genotype']
        elif r['snp_id'] == 'rs1801131':
            a1298c = r['genotype']

    if not c677t or not a1298c:
        return None

    # Count risk alleles
    c677t_risk = c677t.count('T') if c677t else 0
    a1298c_risk = a1298c.count('C') + a1298c.count('G') if a1298c else 0

    # Check for homozygous risk
    is_c677t_homo = c677t in ['TT', 'AA']
    is_c677t_hetero = 'T' in c677t and 'C' in c677t or 'A' in c677t and 'G' in c677t
    is_a1298c_homo = a1298c in ['CC', 'GG']
    is_a1298c_hetero = len(set(a1298c)) == 2 if a1298c else False

    if c677t == 'AG':
        is_c677t_hetero = True
    if a1298c == 'GT':
        is_a1298c_hetero = False

    if is_c677t_homo and is_a1298c_homo:
        status = ('severe', 'Significantly reduced MTHFR activity (~10-20%)')
    elif is_c677t_homo and is_a1298c_hetero:
        status = ('severe', 'Significantly reduced MTHFR activity')
    elif is_c677t_homo:
        status = ('moderate', 'C677T homozygote - reduced MTHFR activity (~30%)')
    elif is_c677t_hetero and is_a1298c_homo:
        status = ('moderate', 'Compound - moderately reduced activity')
    elif is_c677t_hetero and is_a1298c_hetero:
        status = ('moderate', 'Compound heterozygote - moderate reduction')
    elif is_c677t_hetero:
        status = ('mild', 'C677T heterozygote - slight reduction (~65%)')
    elif is_a1298c_homo:
        status = ('mild', 'A1298C homozygote - slight reduction')
    else:
        status = ('normal', 'Normal MTHFR activity')

    return {
        'c677t': c677t,
        'a1298c': a1298c,
        'status': status[0],
        'interpretation': status[1]
    }


def determine_nat2_status(results):
    """Determine NAT2 acetylator status"""
    rs1801280 = None
    rs1799930 = None

    for r in results:
        if r['snp_id'] == 'rs1801280':
            rs1801280 = r
        elif r['snp_id'] == 'rs1799930':
            rs1799930 = r

    if not rs1801280 or not rs1799930:
        return None

    slow_count = 0
    if rs1801280['risk_level'] == 'slow':
        slow_count += 2
    elif rs1801280['risk_level'] == 'intermediate':
        slow_count += 1

    if rs1799930['risk_level'] == 'slow':
        slow_count += 2
    elif rs1799930['risk_level'] == 'intermediate':
        slow_count += 1

    if slow_count >= 3:
        status = ('slow', 'Slow acetylator - increased risk of isoniazid and sulfonamide toxicity')
    elif slow_count >= 1:
        status = ('intermediate', 'Intermediate acetylator')
    else:
        status = ('fast', 'Fast acetylator')

    return {
        'rs1801280': rs1801280['genotype'] if rs1801280['found'] else 'n/a',
        'rs1799930': rs1799930['genotype'] if rs1799930['found'] else 'n/a',
        'status': status[0],
        'interpretation': status[1]
    }


def determine_cyp2c19_status(results):
    """Determine CYP2C19 metabolizer status"""
    rs4244285 = None  # *2
    rs12248560 = None  # *17

    for r in results:
        if r['snp_id'] == 'rs4244285':
            rs4244285 = r
        elif r['snp_id'] == 'rs12248560':
            rs12248560 = r

    if not rs4244285 or not rs12248560:
        return None

    is_slow = rs4244285['risk_level'] == 'slow'
    is_intermediate_slow = rs4244285['risk_level'] == 'intermediate'
    is_ultrafast = rs12248560['risk_level'] == 'ultrafast'
    is_fast = rs12248560['risk_level'] == 'fast'

    if is_slow:
        status = ('poor', 'CYP2C19 poor metabolizer - clopidogrel is ineffective!')
    elif is_intermediate_slow and is_ultrafast:
        status = ('normal', 'Normal metabolizer (compensated)')
    elif is_intermediate_slow:
        status = ('intermediate', 'CYP2C19 intermediate metabolizer')
    elif is_ultrafast:
        status = ('ultrarapid', 'CYP2C19 ultrarapid metabolizer - a dose increase may be needed')
    elif is_fast:
        status = ('rapid', 'CYP2C19 fast metabolizer')
    else:
        status = ('normal', 'Normal CYP2C19 metabolizer')

    return {
        'rs4244285': rs4244285['genotype'] if rs4244285['found'] else 'n/a',
        'rs12248560': rs12248560['genotype'] if rs12248560['found'] else 'n/a',
        'status': status[0],
        'interpretation': status[1]
    }


def determine_alcohol_tolerance(results):
    """Determine alcohol tolerance based on ADH1B and ALDH2"""
    adh1b = None
    aldh2 = None

    for r in results:
        if r['snp_id'] == 'rs1229984':
            adh1b = r
        elif r['snp_id'] == 'rs671':
            aldh2 = r

    if not adh1b and not aldh2:
        return None

    adh_fast = adh1b and adh1b['risk_level'] in ['fast', 'ultrafast'] if adh1b else False
    aldh_low = aldh2 and aldh2['risk_level'] in ['low', 'very_low'] if aldh2 else False

    if aldh_low:
        status = ('intolerant', 'Alcohol intolerance - flushing, nausea')
    elif adh_fast and not aldh_low:
        status = ('sensitive', 'Rapid intoxication, but good acetaldehyde breakdown')
    elif not adh_fast and not aldh_low:
        status = ('normal', 'Standard alcohol tolerance')
    else:
        status = ('unknown', 'Could not be determined')

    return {
        'adh1b': adh1b['genotype'] if adh1b and adh1b['found'] else 'n/a',
        'aldh2': aldh2['genotype'] if aldh2 and aldh2['found'] else 'n/a',
        'status': status[0],
        'interpretation': status[1]
    }


def generate_category_report(category, results, genome):
    """Generate report for a category"""
    cat_info = DETOX_SNPS[category]

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
        report.append("### Status summary\n")
        status_emoji = {
            'high': '🔴',
            'very_high': '🔴🔴',
            'moderate': '🟡',
            'low': '🟠',
            'very_low': '🔴',
            'normal': '✅',
            'fast': '⚡',
            'slow': '🐢',
            'ultrafast': '⚡⚡',
            'intermediate': '🟡',
            'info': 'ℹ️'
        }
        for risk, count in sorted(risk_counts.items()):
            emoji = status_emoji.get(risk, '•')
            report.append(f"- {emoji} {risk}: {count}")

    report.append("\n### Detailed results\n")
    report.append("| SNP | Gene | Genotype | Status | Interpretation |")
    report.append("|-----|-----|---------|--------|---------------|")

    for r in results:
        if r['found']:
            risk_label = r['risk_level'] or 'n/a'
            interp = r['interpretation'] or 'No data'
            report.append(f"| {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {risk_label} | {interp} |")
        else:
            report.append(f"| {r['snp_id']} | {r['gene']} | - | - | Not found in genome |")

    # Special sections
    if category == 'methylation':
        mthfr = determine_mthfr_status(results)
        if mthfr:
            report.append("\n### MTHFR status (combined)\n")
            report.append(f"- C677T (rs1801133): {mthfr['c677t']}")
            report.append(f"- A1298C (rs1801131): {mthfr['a1298c']}")
            report.append(f"- **Status: {mthfr['status']}**")
            report.append(f"- {mthfr['interpretation']}")

    if category == 'phase2_conjugation':
        nat2 = determine_nat2_status(results)
        if nat2:
            report.append("\n### NAT2 acetylator status\n")
            report.append(f"- rs1801280: {nat2['rs1801280']}")
            report.append(f"- rs1799930: {nat2['rs1799930']}")
            report.append(f"- **Status: {nat2['status']}**")
            report.append(f"- {nat2['interpretation']}")

    if category == 'phase1_cyp450':
        cyp2c19 = determine_cyp2c19_status(results)
        if cyp2c19:
            report.append("\n### CYP2C19 metabolizer status\n")
            report.append(f"- *2 (rs4244285): {cyp2c19['rs4244285']}")
            report.append(f"- *17 (rs12248560): {cyp2c19['rs12248560']}")
            report.append(f"- **Status: {cyp2c19['status']}**")
            report.append(f"- {cyp2c19['interpretation']}")

    if category == 'alcohol':
        alcohol = determine_alcohol_tolerance(results)
        if alcohol:
            report.append("\n### Alcohol tolerance\n")
            report.append(f"- ADH1B (rs1229984): {alcohol['adh1b']}")
            report.append(f"- ALDH2 (rs671): {alcohol['aldh2']}")
            report.append(f"- **Status: {alcohol['status']}**")
            report.append(f"- {alcohol['interpretation']}")

    return '\n'.join(report)


def generate_summary_report(all_results, genome):
    """Generate overall summary report"""
    report = []
    report.append("# Detoxification summary report")
    report.append(f"\nAnalysis date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("\n---\n")

    report.append("## Important warnings\n")
    report.append("1. **This is NOT a medical diagnosis** - informational analysis only")
    report.append("2. **Genetics is not destiny** - lifestyle and environment matter more")
    report.append("3. **For medical decisions** - consulting a physician is required")
    report.append("4. **Medication dosages** - are determined by a physician only\n")

    report.append("---\n")

    # Collect findings by status
    critical = []
    attention = []
    optimal = []

    for category, results in all_results.items():
        for r in results:
            if r['risk_level'] in ['slow', 'low', 'very_low', 'high']:
                critical.append((category, r))
            elif r['risk_level'] in ['moderate', 'intermediate']:
                attention.append((category, r))
            elif r['risk_level'] in ['normal', 'fast', 'high'] and r['risk_level'] == 'normal':
                optimal.append((category, r))

    if critical:
        report.append("## Needs attention\n")
        report.append("| Category | SNP | Gene | Genotype | Description |")
        report.append("|-----------|-----|-----|---------|----------|")
        for cat, r in critical:
            cat_name = DETOX_SNPS[cat]['name']
            report.append(f"| {cat_name} | {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {r['interpretation']} |")
        report.append("")

    if attention:
        report.append("## Moderate deviations\n")
        report.append("| Category | SNP | Gene | Genotype | Description |")
        report.append("|-----------|-----|-----|---------|----------|")
        for cat, r in attention:
            cat_name = DETOX_SNPS[cat]['name']
            report.append(f"| {cat_name} | {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {r['interpretation']} |")
        report.append("")

    # Special analyses
    report.append("---\n")
    report.append("## Special analyses\n")

    # MTHFR
    methylation_results = all_results.get('methylation', [])
    mthfr = determine_mthfr_status(methylation_results)
    if mthfr:
        report.append("### MTHFR (Methylation)\n")
        report.append(f"- C677T: {mthfr['c677t']}, A1298C: {mthfr['a1298c']}")
        report.append(f"- **Status: {mthfr['status']}**")
        report.append(f"- {mthfr['interpretation']}")
        if mthfr['status'] in ['moderate', 'severe', 'mild']:
            report.append("- **Recommendations:** methylfolate, methyl-B12, avoid folic acid\n")
        else:
            report.append("")

    # NAT2
    phase2_results = all_results.get('phase2_conjugation', [])
    nat2 = determine_nat2_status(phase2_results)
    if nat2:
        report.append("### NAT2 (Acetylation)\n")
        report.append(f"- **Status: {nat2['status']}**")
        report.append(f"- {nat2['interpretation']}")
        if nat2['status'] == 'slow':
            report.append("- **Recommendations:** use caution with isoniazid and sulfonamides\n")
        else:
            report.append("")

    # CYP2C19
    phase1_results = all_results.get('phase1_cyp450', [])
    cyp2c19 = determine_cyp2c19_status(phase1_results)
    if cyp2c19:
        report.append("### CYP2C19 (Drug metabolism)\n")
        report.append(f"- **Status: {cyp2c19['status']}**")
        report.append(f"- {cyp2c19['interpretation']}")
        if cyp2c19['status'] == 'poor':
            report.append("- **IMPORTANT:** Clopidogrel is ineffective - an alternative is required!\n")
        else:
            report.append("")

    # Alcohol
    alcohol_results = all_results.get('alcohol', [])
    alcohol = determine_alcohol_tolerance(alcohol_results)
    if alcohol:
        report.append("### Alcohol\n")
        report.append(f"- **Status: {alcohol['status']}**")
        report.append(f"- {alcohol['interpretation']}\n")

    # SLCO1B1 Statin warning
    transporter_results = all_results.get('transporters', [])
    for r in transporter_results:
        if r['snp_id'] == 'rs4149056' and r['found']:
            if r['risk_level'] in ['moderate', 'high']:
                report.append("### SLCO1B1 (Statins)\n")
                report.append(f"- Genotype: {r['genotype']}")
                report.append(f"- **{r['interpretation']}**")
                if r['risk_level'] == 'high':
                    report.append("- **IMPORTANT:** Avoid high doses of simvastatin and atorvastatin!\n")
                else:
                    report.append("")

    report.append("---\n")
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
    print("DETOXIFICATION ANALYSIS FROM 23andMe GENOME")
    print("=" * 60)

    print("\n[1/4] Loading genome...")
    genome = load_genome()
    print(f"      Loaded {len(genome)} SNP")

    print("\n[2/4] Analyzing markers by category...")
    all_results = {}

    for category, cat_info in DETOX_SNPS.items():
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
        report_dir = f"{REPORTS_PATH}/detox"
        os.makedirs(report_dir, exist_ok=True)
        report_path = f"{report_dir}/{category}.md"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"      -> {report_path}")

    print("\n[4/4] Generating summary report...")
    summary = generate_summary_report(all_results, genome)
    summary_path = f"{REPORTS_PATH}/detox/report.md"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"      -> {summary_path}")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

    # Print key findings to console
    print("\nKEY FINDINGS:\n")

    for category, results in all_results.items():
        important = [r for r in results if r['risk_level'] in ['slow', 'low', 'very_low', 'high']]
        if important:
            print(f"  {DETOX_SNPS[category]['name']}:")
            for r in important:
                print(f"    - {r['gene']} ({r['genotype']}): {r['interpretation']}")
            print()


if __name__ == "__main__":
    main()

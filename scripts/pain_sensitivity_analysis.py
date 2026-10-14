#!/usr/bin/env python3
"""
Pain Sensitivity SNP Analysis Script
Analyzes pain-related genetic markers from 23andMe data
"""

import os
from collections import defaultdict
from datetime import datetime

# Paths
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENOME_FILE = f"{BASE_PATH}/data/my_dna_file.txt"
REPORTS_PATH = f"{BASE_PATH}/reports"

# =============================================================================
# SNP DATABASE - Pain Sensitivity Categories
# =============================================================================

PAIN_SNPS = {
    "pain_threshold": {
        "name": "Baseline pain sensitivity",
        "snps": {
            "rs4680": {
                "gene": "COMT Val158Met",
                "description": "Catechol-O-methyltransferase - dopamine and catecholamine metabolism",
                "risk_allele": "A",
                "interpretation": {
                    "GG": ("low_pain", "Val/Val - low pain sensitivity, fast catecholamine metabolism"),
                    "AG": ("moderate", "Val/Met - moderate pain sensitivity"),
                    "AA": ("high_pain", "Met/Met - high pain sensitivity, slow catecholamine metabolism"),
                }
            },
            "rs6746030": {
                "gene": "SCN9A",
                "description": "Sodium channel Nav1.7 - pain signal conduction",
                "risk_allele": "A",
                "interpretation": {
                    "GG": ("low_pain", "Higher pain threshold"),
                    "AG": ("moderate", "Average pain threshold"),
                    "AA": ("high_pain", "Lower pain threshold, increased sensitivity"),
                }
            },
            "rs8007267": {
                "gene": "GCH1",
                "description": "GTP cyclohydrolase 1 - part of the protective haplotype",
                "risk_allele": "A",
                "interpretation": {
                    "GG": ("normal", "Standard variant"),
                    "AG": ("protective", "Protective allele carrier - reduced pain sensitivity"),
                    "AA": ("protective", "Protective genotype - reduced pain sensitivity"),
                }
            },
            "rs3783641": {
                "gene": "GCH1",
                "description": "GTP cyclohydrolase 1 - protective haplotype against chronic pain",
                "risk_allele": "A",
                "interpretation": {
                    "TT": ("normal", "Standard variant"),
                    "AT": ("protective", "Protective allele carrier"),
                    "AA": ("protective", "Protective genotype against chronic pain"),
                }
            },
            "rs10483639": {
                "gene": "GCH1",
                "description": "GTP cyclohydrolase 1 - component of the pain-protective haplotype",
                "risk_allele": "G",
                "interpretation": {
                    "CC": ("normal", "Standard variant"),
                    "CG": ("protective", "Protective allele carrier"),
                    "GG": ("protective", "Protective genotype - lower risk of chronic pain"),
                }
            },
        }
    },

    "opioid_response": {
        "name": "Response to opioid analgesics",
        "snps": {
            "rs1799971": {
                "gene": "OPRM1 A118G",
                "description": "Mu-opioid receptor - main target of opioids",
                "risk_allele": "G",
                "interpretation": {
                    "AA": ("normal", "Normal opioid response, standard doses"),
                    "AG": ("moderate", "Reduced response - higher doses may be needed"),
                    "GG": ("high", "Markedly reduced response - substantially higher opioid doses needed"),
                }
            },
            "rs1045642": {
                "gene": "ABCB1 C3435T",
                "description": "P-glycoprotein - opioid transport across the blood-brain barrier",
                "risk_allele": "T",
                "interpretation": {
                    "CC": ("good", "Good opioid response, better CNS penetration"),
                    "CT": ("moderate", "Average opioid response"),
                    "TT": ("poor", "Reduced opioid response, poorer penetration"),
                }
            },
        }
    },

    "inflammatory_pain": {
        "name": "Inflammatory pain",
        "snps": {
            "rs1800629": {
                "gene": "TNF-α -308G>A",
                "description": "Tumor necrosis factor alpha - key inflammation mediator",
                "risk_allele": "A",
                "interpretation": {
                    "GG": ("normal", "Normal TNF-α production"),
                    "AG": ("moderate", "Increased TNF-α production, tendency toward inflammatory pain"),
                    "AA": ("high", "High TNF-α production, increased risk of chronic inflammation and pain"),
                }
            },
            "rs1800795": {
                "gene": "IL-6 -174G>C",
                "description": "Interleukin-6 - pro-inflammatory cytokine",
                "risk_allele": "C",
                "interpretation": {
                    "GG": ("normal", "Normal IL-6 level"),
                    "GC": ("moderate", "Moderately elevated IL-6"),
                    "CG": ("moderate", "Moderately elevated IL-6"),
                    "CC": ("high", "Increased IL-6 production, tendency toward inflammatory pain"),
                }
            },
            "rs1800896": {
                "gene": "IL-10 -1082A>G",
                "description": "Interleukin-10 - anti-inflammatory cytokine",
                "risk_allele": "A",
                "interpretation": {
                    "GG": ("protective", "High IL-10 production, good anti-inflammatory protection"),
                    "AG": ("normal", "Average IL-10 production"),
                    "GA": ("normal", "Average IL-10 production"),
                    "AA": ("high", "Low IL-10 production, reduced anti-inflammatory protection"),
                }
            },
        }
    },

    "migraine": {
        "name": "Migraine",
        "snps": {
            "rs1835740": {
                "gene": "MTDH/AEG-1",
                "description": "Metadherin - glutamate regulation, first GWAS marker for migraine",
                "risk_allele": "C",
                "interpretation": {
                    "TT": ("normal", "Normal migraine risk"),
                    "CT": ("moderate", "Moderately increased migraine risk (~20%)"),
                    "TC": ("moderate", "Moderately increased migraine risk (~20%)"),
                    "CC": ("high", "Increased migraine risk (~40%)"),
                }
            },
            "rs2651899": {
                "gene": "PRDM16",
                "description": "Transcription factor - nervous system development",
                "risk_allele": "C",
                "interpretation": {
                    "TT": ("normal", "Normal migraine risk"),
                    "CT": ("moderate", "Slightly increased migraine risk"),
                    "TC": ("moderate", "Slightly increased migraine risk"),
                    "CC": ("high", "Increased migraine risk"),
                }
            },
            "rs10166942": {
                "gene": "TRPM8",
                "description": "Cold receptor - sensory sensitivity",
                "risk_allele": "T",
                "interpretation": {
                    "CC": ("normal", "Normal migraine risk"),
                    "CT": ("moderate", "Slightly increased migraine risk"),
                    "TC": ("moderate", "Slightly increased migraine risk"),
                    "TT": ("high", "Increased risk of migraine with aura"),
                }
            },
            "rs11172113": {
                "gene": "LRP1",
                "description": "Low-density lipoprotein receptor - neuroprotection",
                "risk_allele": "T",
                "interpretation": {
                    "CC": ("normal", "Normal migraine risk"),
                    "CT": ("moderate", "Slightly increased risk"),
                    "TC": ("moderate", "Slightly increased risk"),
                    "TT": ("high", "Increased migraine risk"),
                }
            },
        }
    },

    "anesthetics": {
        "name": "Local anesthetics",
        "snps": {
            "rs12532": {
                "gene": "SCN5A",
                "description": "Sodium channel - target of local anesthetics",
                "risk_allele": "T",
                "interpretation": {
                    "CC": ("normal", "Normal response to local anesthetics"),
                    "CT": ("moderate", "Slightly reduced anesthetic efficacy"),
                    "TC": ("moderate", "Slightly reduced anesthetic efficacy"),
                    "TT": ("high", "May need more anesthetic"),
                }
            },
            "rs1805007": {
                "gene": "MC1R R151C",
                "description": "Melanocortin receptor 1 - associated with red hair",
                "risk_allele": "T",
                "interpretation": {
                    "CC": ("normal", "Normal response to anesthesia"),
                    "CT": ("high", "MC1R variant carrier - may need 19% more anesthetic"),
                    "TC": ("high", "MC1R variant carrier - may need 19% more anesthetic"),
                    "TT": ("high", "MC1R variant - significantly more local anesthetic needed"),
                }
            },
        }
    },

    "nsaids": {
        "name": "Response to NSAIDs (nonsteroidal anti-inflammatory drugs)",
        "snps": {
            "rs1799853": {
                "gene": "CYP2C9*2",
                "description": "Cytochrome P450 2C9 - NSAID metabolism",
                "risk_allele": "T",
                "interpretation": {
                    "CC": ("normal", "Normal metabolizer - standard NSAID doses"),
                    "CT": ("moderate", "Intermediate metabolizer - use caution with dosing"),
                    "TC": ("moderate", "Intermediate metabolizer - use caution with dosing"),
                    "TT": ("high", "Poor metabolizer - increased risk of NSAID side effects, reduce dose"),
                }
            },
            "rs1057910": {
                "gene": "CYP2C9*3",
                "description": "Cytochrome P450 2C9 - key NSAID-metabolizing enzyme",
                "risk_allele": "C",
                "interpretation": {
                    "AA": ("normal", "Normal metabolizer - standard doses"),
                    "AC": ("moderate", "Intermediate metabolizer - risk of NSAID accumulation"),
                    "CA": ("moderate", "Intermediate metabolizer - risk of NSAID accumulation"),
                    "CC": ("high", "Poor metabolizer - high risk of side effects, reduce dose by 50%"),
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


def analyze_gch1_haplotype(genome):
    """Analyze GCH1 protective haplotype"""
    rs8007267 = genome.get('rs8007267', {}).get('genotype', '')
    rs3783641 = genome.get('rs3783641', {}).get('genotype', '')
    rs10483639 = genome.get('rs10483639', {}).get('genotype', '')

    protective_count = 0
    details = []

    if 'A' in rs8007267:
        protective_count += rs8007267.count('A')
        details.append(f"rs8007267: {rs8007267}")
    if 'A' in rs3783641:
        protective_count += rs3783641.count('A')
        details.append(f"rs3783641: {rs3783641}")
    if 'G' in rs10483639:
        protective_count += rs10483639.count('G')
        details.append(f"rs10483639: {rs10483639}")

    if protective_count >= 4:
        status = ('strong_protective', 'Strong protective GCH1 haplotype - markedly reduced pain sensitivity')
    elif protective_count >= 2:
        status = ('protective', 'Partial protective GCH1 haplotype - moderately reduced pain sensitivity')
    elif protective_count >= 1:
        status = ('mild_protective', 'Carrier of protective GCH1 alleles')
    else:
        status = ('normal', 'No protective GCH1 haplotype')

    return {
        'rs8007267': rs8007267,
        'rs3783641': rs3783641,
        'rs10483639': rs10483639,
        'protective_alleles': protective_count,
        'status': status[0],
        'interpretation': status[1],
        'details': details
    }


def analyze_cyp2c9_status(results):
    """Determine combined CYP2C9 metabolizer status for NSAIDs"""
    cyp2c9_2 = None
    cyp2c9_3 = None

    for r in results:
        if r['snp_id'] == 'rs1799853':
            cyp2c9_2 = r['genotype']
        elif r['snp_id'] == 'rs1057910':
            cyp2c9_3 = r['genotype']

    if not cyp2c9_2 and not cyp2c9_3:
        return None

    # Count variant alleles
    variant_count = 0
    if cyp2c9_2:
        variant_count += cyp2c9_2.count('T')
    if cyp2c9_3:
        variant_count += cyp2c9_3.count('C')

    if variant_count >= 3:
        status = ('poor', 'Poor CYP2C9 metabolizer - reduce NSAID dose by 50-75%')
    elif variant_count == 2:
        status = ('intermediate', 'Intermediate CYP2C9 metabolizer - reduce NSAID dose by 25-50%')
    elif variant_count == 1:
        status = ('intermediate', 'Intermediate CYP2C9 metabolizer - use caution with dosing')
    else:
        status = ('normal', 'Normal CYP2C9 metabolizer - standard NSAID doses')

    return {
        'cyp2c9_2': cyp2c9_2,
        'cyp2c9_3': cyp2c9_3,
        'variant_alleles': variant_count,
        'status': status[0],
        'interpretation': status[1]
    }


def analyze_comt_pain_profile(genome):
    """Analyze COMT Val158Met for pain sensitivity profile"""
    rs4680 = genome.get('rs4680', {}).get('genotype', '')

    if rs4680 == 'GG':
        profile = {
            'type': 'Warrior (Val/Val)',
            'pain_sensitivity': 'Low',
            'stress_tolerance': 'High',
            'dopamine_metabolism': 'Fast',
            'clinical': 'Needs less pain medication, handles stress better'
        }
    elif rs4680 == 'AA':
        profile = {
            'type': 'Worrier (Met/Met)',
            'pain_sensitivity': 'High',
            'stress_tolerance': 'Low',
            'dopamine_metabolism': 'Slow',
            'clinical': 'May need more pain medication, higher cognitive function'
        }
    elif rs4680 in ['AG', 'GA']:
        profile = {
            'type': 'Mixed (Val/Met)',
            'pain_sensitivity': 'Average',
            'stress_tolerance': 'Average',
            'dopamine_metabolism': 'Average',
            'clinical': 'Balanced pain and stress profile'
        }
    else:
        profile = {
            'type': 'Undetermined',
            'pain_sensitivity': 'N/A',
            'stress_tolerance': 'N/A',
            'dopamine_metabolism': 'N/A',
            'clinical': 'Genotype not found'
        }

    profile['genotype'] = rs4680
    return profile


def generate_category_report(category, results, genome):
    """Generate report for a category"""
    cat_info = PAIN_SNPS[category]

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
        report.append("### Results summary\n")
        risk_emoji = {
            'high': '🔴',
            'high_pain': '🔴',
            'moderate': '🟡',
            'low': '🟢',
            'low_pain': '🟢',
            'normal': '✅',
            'protective': '🛡️',
            'strong_protective': '🛡️🛡️',
            'mild_protective': '🛡️',
            'good': '✅',
            'poor': '🔴',
            'info': 'ℹ️'
        }
        for risk, count in sorted(risk_counts.items()):
            emoji = risk_emoji.get(risk, '•')
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

    # Special sections for specific categories
    if category == 'pain_threshold':
        report.append("\n### GCH1 protective haplotype\n")
        gch1 = analyze_gch1_haplotype(genome)
        report.append(f"- rs8007267: {gch1['rs8007267'] or 'not found'}")
        report.append(f"- rs3783641: {gch1['rs3783641'] or 'not found'}")
        report.append(f"- rs10483639: {gch1['rs10483639'] or 'not found'}")
        report.append(f"- Protective alleles: {gch1['protective_alleles']}")
        report.append(f"- **Status: {gch1['status']}**")
        report.append(f"- {gch1['interpretation']}")

        report.append("\n### COMT pain profile\n")
        comt = analyze_comt_pain_profile(genome)
        report.append(f"- rs4680 genotype: **{comt['genotype']}**")
        report.append(f"- Type: **{comt['type']}**")
        report.append(f"- Pain sensitivity: {comt['pain_sensitivity']}")
        report.append(f"- Stress tolerance: {comt['stress_tolerance']}")
        report.append(f"- Dopamine metabolism: {comt['dopamine_metabolism']}")
        report.append(f"- Clinical significance: {comt['clinical']}")

    if category == 'nsaids':
        cyp2c9 = analyze_cyp2c9_status(results)
        if cyp2c9:
            report.append("\n### CYP2C9 metabolizer status\n")
            report.append(f"- CYP2C9*2 (rs1799853): {cyp2c9['cyp2c9_2'] or 'not found'}")
            report.append(f"- CYP2C9*3 (rs1057910): {cyp2c9['cyp2c9_3'] or 'not found'}")
            report.append(f"- Variant alleles: {cyp2c9['variant_alleles']}")
            report.append(f"- **Status: {cyp2c9['status']}**")
            report.append(f"- {cyp2c9['interpretation']}")

    return '\n'.join(report)


def generate_summary_report(all_results, genome):
    """Generate overall summary report"""
    report = []
    report.append("# Pain Sensitivity Analysis")
    report.append(f"\nAnalysis date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("\n---\n")

    report.append("## Important disclaimers\n")
    report.append("1. **This is NOT a medical diagnosis** - informational genetic analysis only")
    report.append("2. **Pain sensitivity depends on many factors** - genetics is only one part")
    report.append("3. **Individual response may differ** - genotype does not guarantee phenotype")
    report.append("4. **For prescribing medication** - consulting a physician is required\n")

    report.append("---\n")

    # COMT Pain Profile - Main highlight
    report.append("## Primary pain profile (COMT)\n")
    comt = analyze_comt_pain_profile(genome)
    report.append(f"| Parameter | Value |")
    report.append(f"|----------|----------|")
    report.append(f"| Genotype | **{comt['genotype']}** |")
    report.append(f"| Type | **{comt['type']}** |")
    report.append(f"| Pain sensitivity | {comt['pain_sensitivity']} |")
    report.append(f"| Stress tolerance | {comt['stress_tolerance']} |")
    report.append(f"| Dopamine metabolism | {comt['dopamine_metabolism']} |")
    report.append(f"\n**Clinical significance:** {comt['clinical']}\n")

    # GCH1 Haplotype
    report.append("## GCH1 protective haplotype\n")
    gch1 = analyze_gch1_haplotype(genome)
    if gch1['protective_alleles'] > 0:
        report.append(f"- Status: **{gch1['status']}**")
        report.append(f"- {gch1['interpretation']}")
        report.append(f"- Protective alleles: {gch1['protective_alleles']}/6")
    else:
        report.append("- No protective haplotype detected")
    report.append("")

    report.append("---\n")

    # Collect findings by importance
    high_pain = []
    low_pain = []
    medication_warnings = []
    protective = []

    for category, results in all_results.items():
        cat_name = PAIN_SNPS[category]['name']
        for r in results:
            if r['risk_level'] in ['high', 'high_pain', 'poor']:
                if category in ['opioid_response', 'nsaids', 'anesthetics']:
                    medication_warnings.append((cat_name, r))
                else:
                    high_pain.append((cat_name, r))
            elif r['risk_level'] in ['low_pain', 'good']:
                low_pain.append((cat_name, r))
            elif r['risk_level'] in ['protective', 'strong_protective', 'mild_protective']:
                protective.append((cat_name, r))

    if medication_warnings:
        report.append("## Important for medication use\n")
        report.append("| Category | SNP | Gene | Genotype | Significance |")
        report.append("|-----------|-----|-----|---------|----------|")
        for cat, r in medication_warnings:
            report.append(f"| {cat} | {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {r['interpretation']} |")
        report.append("")

    if high_pain:
        report.append("## Increased pain sensitivity\n")
        report.append("| Category | SNP | Gene | Genotype | Description |")
        report.append("|-----------|-----|-----|---------|----------|")
        for cat, r in high_pain:
            report.append(f"| {cat} | {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {r['interpretation']} |")
        report.append("")

    if low_pain:
        report.append("## Reduced pain sensitivity\n")
        report.append("| Category | SNP | Gene | Genotype | Description |")
        report.append("|-----------|-----|-----|---------|----------|")
        for cat, r in low_pain:
            report.append(f"| {cat} | {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {r['interpretation']} |")
        report.append("")

    if protective:
        report.append("## Protective variants\n")
        report.append("| Category | SNP | Gene | Genotype | Description |")
        report.append("|-----------|-----|-----|---------|----------|")
        for cat, r in protective:
            report.append(f"| {cat} | {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {r['interpretation']} |")
        report.append("")

    # CYP2C9 Status for NSAIDs
    nsaid_results = all_results.get('nsaids', [])
    cyp2c9 = analyze_cyp2c9_status(nsaid_results)
    if cyp2c9:
        report.append("## NSAID metabolism (CYP2C9)\n")
        report.append(f"- CYP2C9*2: {cyp2c9['cyp2c9_2'] or 'not found'}")
        report.append(f"- CYP2C9*3: {cyp2c9['cyp2c9_3'] or 'not found'}")
        report.append(f"- **Metabolizer status: {cyp2c9['status']}**")
        report.append(f"- Recommendation: {cyp2c9['interpretation']}\n")

    # Migraine risk
    report.append("## Migraine risk\n")
    migraine_results = all_results.get('migraine', [])
    migraine_risk_count = sum(1 for r in migraine_results if r['risk_level'] in ['high', 'moderate'])
    if migraine_risk_count >= 3:
        report.append("- **Increased genetic migraine risk**")
    elif migraine_risk_count >= 1:
        report.append("- Moderate genetic migraine risk")
    else:
        report.append("- No increased genetic migraine risk")

    migraine_found = [r for r in migraine_results if r['found']]
    if migraine_found:
        report.append("\nRelevant markers:")
        for r in migraine_found:
            status = r['risk_level'] or 'n/a'
            report.append(f"- {r['snp_id']} ({r['gene']}): {r['genotype']} - {status}")
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

    report.append("\n---\n")
    report.append("## Practical recommendations\n")

    # Generate personalized recommendations
    recommendations = []

    if comt['pain_sensitivity'] == 'High':
        recommendations.append("- **Pain sensitivity:** You may be more sensitive to pain. Discuss an individualized approach to pain relief with your doctor.")

    if comt['pain_sensitivity'] == 'Low':
        recommendations.append("- **Pain sensitivity:** You likely have a high pain threshold. Remember that pain is an important signal from your body.")

    opioid_results = all_results.get('opioid_response', [])
    for r in opioid_results:
        if r['snp_id'] == 'rs1799971' and r['risk_level'] in ['moderate', 'high']:
            recommendations.append("- **Opioids:** Possibly reduced response to opioid analgesics. Inform your anesthesiologist.")
            break

    if cyp2c9 and cyp2c9['status'] != 'normal':
        recommendations.append(f"- **NSAIDs:** {cyp2c9['interpretation']}")

    anesthetic_results = all_results.get('anesthetics', [])
    for r in anesthetic_results:
        if r['snp_id'] == 'rs1805007' and r['risk_level'] == 'high':
            recommendations.append("- **Local anesthesia:** A higher dose of local anesthetics may be needed. Inform your dentist/surgeon.")
            break

    if migraine_risk_count >= 2:
        recommendations.append("- **Migraine:** Increased genetic predisposition. Avoid known triggers and keep a headache diary.")

    if recommendations:
        report.extend(recommendations)
    else:
        report.append("- No specific recommendations based on the analysis results.")

    return '\n'.join(report)


def main():
    print("=" * 60)
    print("GENOME-WIDE PAIN SENSITIVITY ANALYSIS")
    print("=" * 60)

    print("\n[1/4] Loading genome...")
    genome = load_genome()
    print(f"      Loaded {len(genome)} SNP")

    print("\n[2/4] Analyzing markers by category...")
    all_results = {}

    for category, cat_info in PAIN_SNPS.items():
        print(f"      -> {cat_info['name']}...")
        results = []
        for snp_id, snp_info in cat_info['snps'].items():
            result = analyze_snp(snp_id, snp_info, genome)
            results.append(result)
        all_results[category] = results

        # Count found
        found = sum(1 for r in results if r['found'])
        print(f"        Found: {found}/{len(results)}")

    print("\n[3/4] Generating detailed reports...")
    for category, results in all_results.items():
        report = generate_category_report(category, results, genome)
        report_dir = f"{REPORTS_PATH}/pain/{category}"
        os.makedirs(report_dir, exist_ok=True)
        report_path = f"{report_dir}/report.md"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"      -> {report_path}")

    print("\n[4/4] Generating summary report...")
    summary = generate_summary_report(all_results, genome)
    summary_path = f"{REPORTS_PATH}/pain/report.md"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"      -> {summary_path}")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

    # Print key findings to console
    print("\nKEY FINDINGS:\n")

    # COMT Profile
    comt = analyze_comt_pain_profile(genome)
    print(f"COMT profile: {comt['type']}")
    print(f"  - Pain sensitivity: {comt['pain_sensitivity']}")
    print(f"  - {comt['clinical']}")
    print()

    # Medication warnings
    for category, results in all_results.items():
        warnings = [r for r in results if r['risk_level'] in ['high', 'poor']]
        if warnings and category in ['opioid_response', 'nsaids', 'anesthetics']:
            print(f"WARNING - {PAIN_SNPS[category]['name']}:")
            for r in warnings:
                print(f"    * {r['gene']} ({r['genotype']}): {r['interpretation']}")
            print()


if __name__ == "__main__":
    main()

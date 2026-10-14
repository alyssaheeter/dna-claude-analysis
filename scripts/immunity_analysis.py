#!/usr/bin/env python3
"""
Immunity SNP Analysis Script
Analyzes immunity-related genetic markers from 23andMe data
"""

import os
from collections import defaultdict
from datetime import datetime

# Paths
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENOME_FILE = f"{BASE_PATH}/data/my_dna_file.txt"
REPORTS_PATH = f"{BASE_PATH}/reports"

# =============================================================================
# SNP DATABASE - Organized by immunity category
# =============================================================================

IMMUNITY_SNPS = {
    "hla_system": {
        "name": "HLA system (HLA-B27, celiac DQ2/DQ8)",
        "snps": {
            "rs4349859": {
                "gene": "HLA-B27",
                "description": "Ankylosing spondylitis, reactive arthritis",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "HLA-B27 positive - high risk of ankylosing spondylitis"),
                    "AG": ("moderate", "HLA-B27 carrier - increased risk of spondyloarthropathies"),
                    "GG": ("normal", "HLA-B27 negative - normal risk"),
                }
            },
            "rs2187668": {
                "gene": "HLA-DQ2.5",
                "description": "Celiac disease (main marker)",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("high", "HLA-DQ2.5 homozygous - very high risk of celiac disease"),
                    "CT": ("moderate", "HLA-DQ2.5 carrier - increased risk of celiac disease"),
                    "TC": ("moderate", "HLA-DQ2.5 carrier - increased risk of celiac disease"),
                    "CC": ("normal", "Low celiac disease risk by DQ2.5"),
                }
            },
            "rs7454108": {
                "gene": "HLA-DQ8",
                "description": "Celiac disease, type 1 diabetes",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("moderate", "HLA-DQ8 positive - risk of celiac disease and T1D"),
                    "CT": ("low", "HLA-DQ8 carrier"),
                    "TC": ("low", "HLA-DQ8 carrier"),
                    "TT": ("normal", "Low risk by HLA-DQ8"),
                }
            },
        }
    },

    "autoimmune": {
        "name": "Autoimmune risks",
        "snps": {
            "rs2476601": {
                "gene": "PTPN22",
                "description": "Rheumatoid arthritis, T1D, SLE, thyroiditis",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Risk homozygote - very high risk of autoimmune diseases"),
                    "AG": ("moderate", "Heterozygote - increased risk of RA, T1D, SLE, thyroiditis"),
                    "GA": ("moderate", "Heterozygote - increased risk of RA, T1D, SLE, thyroiditis"),
                    "GG": ("normal", "Normal risk of autoimmune diseases"),
                }
            },
            "rs6457617": {
                "gene": "HLA-DRB1",
                "description": "Rheumatoid arthritis (shared epitope)",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("high", "High risk of rheumatoid arthritis"),
                    "CT": ("moderate", "Increased risk of rheumatoid arthritis"),
                    "TC": ("moderate", "Increased risk of rheumatoid arthritis"),
                    "CC": ("normal", "Normal risk of rheumatoid arthritis"),
                }
            },
            "rs3135388": {
                "gene": "HLA-DRB1 (MS)",
                "description": "Multiple sclerosis",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "High risk of multiple sclerosis"),
                    "AG": ("moderate", "Increased risk of multiple sclerosis"),
                    "GA": ("moderate", "Increased risk of multiple sclerosis"),
                    "GG": ("normal", "Normal risk of multiple sclerosis"),
                }
            },
            "rs2066847": {
                "gene": "NOD2",
                "description": "Crohn's disease",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("high", "High risk of Crohn's disease"),
                    "CG": ("moderate", "Increased risk of Crohn's disease (2-4x)"),
                    "GC": ("moderate", "Increased risk of Crohn's disease (2-4x)"),
                    "--": ("normal", "No insertion - normal risk"),
                    "GG": ("normal", "Normal risk of Crohn's disease"),
                }
            },
            "rs3087243": {
                "gene": "CTLA4",
                "description": "Autoimmune thyroiditis, T1D, RA",
                "risk_allele": "G",
                "interpretation": {
                    "GG": ("moderate", "Increased risk of autoimmune diseases"),
                    "AG": ("low", "Slightly increased risk"),
                    "GA": ("low", "Slightly increased risk"),
                    "AA": ("normal", "Normal risk"),
                }
            },
        }
    },

    "cytokines": {
        "name": "Cytokines (inflammatory response)",
        "snps": {
            "rs1800629": {
                "gene": "TNF-alpha",
                "description": "Tumor necrosis factor, inflammation",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "High TNF-alpha production - tendency toward chronic inflammation"),
                    "AG": ("moderate", "Increased TNF-alpha production"),
                    "GA": ("moderate", "Increased TNF-alpha production"),
                    "GG": ("normal", "Normal TNF-alpha production"),
                }
            },
            "rs1800795": {
                "gene": "IL-6",
                "description": "Interleukin-6, inflammation and immunity",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("high", "High IL-6 production - pro-inflammatory profile"),
                    "CG": ("moderate", "Moderately increased IL-6 production"),
                    "GC": ("moderate", "Moderately increased IL-6 production"),
                    "GG": ("normal", "Normal IL-6 production"),
                }
            },
            "rs1800896": {
                "gene": "IL-10",
                "description": "Interleukin-10, anti-inflammatory",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("low", "Low IL-10 production - reduced anti-inflammatory response"),
                    "AG": ("moderate", "Moderate IL-10 production"),
                    "GA": ("moderate", "Moderate IL-10 production"),
                    "GG": ("normal", "High IL-10 production - good anti-inflammatory response"),
                }
            },
            "rs16944": {
                "gene": "IL-1beta",
                "description": "Interleukin-1beta, inflammation",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "High IL-1beta production - pro-inflammatory profile"),
                    "AG": ("moderate", "Moderately increased IL-1beta production"),
                    "GA": ("moderate", "Moderately increased IL-1beta production"),
                    "GG": ("normal", "Normal IL-1beta production"),
                }
            },
            "rs20541": {
                "gene": "IL-13",
                "description": "Interleukin-13, allergy and asthma",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "High IL-13 production - risk of asthma and allergy"),
                    "AG": ("moderate", "Increased IL-13 production"),
                    "GA": ("moderate", "Increased IL-13 production"),
                    "GG": ("normal", "Normal IL-13 production"),
                }
            },
        }
    },

    "innate_immunity": {
        "name": "Innate immunity (TLR, complement)",
        "snps": {
            "rs5743708": {
                "gene": "TLR2",
                "description": "Toll-like receptor 2, bacterial infections",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Impaired TLR2 function - reduced protection against bacteria"),
                    "AG": ("moderate", "Reduced TLR2 function"),
                    "GA": ("moderate", "Reduced TLR2 function"),
                    "GG": ("normal", "Normal TLR2 function"),
                }
            },
            "rs4986790": {
                "gene": "TLR4",
                "description": "Toll-like receptor 4, gram-negative bacteria",
                "risk_allele": "G",
                "interpretation": {
                    "GG": ("high", "Impaired TLR4 function - reduced response to LPS"),
                    "AG": ("moderate", "Reduced TLR4 function"),
                    "GA": ("moderate", "Reduced TLR4 function"),
                    "AA": ("normal", "Normal TLR4 function"),
                }
            },
            "rs2230199": {
                "gene": "C3",
                "description": "Complement component C3",
                "risk_allele": "G",
                "interpretation": {
                    "GG": ("moderate", "C3F/F - increased complement activation, AMD risk"),
                    "CG": ("low", "C3S/F - moderate activation"),
                    "GC": ("low", "C3S/F - moderate activation"),
                    "CC": ("normal", "C3S/S - normal complement activation"),
                }
            },
        }
    },

    "infections": {
        "name": "Infectious diseases",
        "snps": {
            "rs333": {
                "gene": "CCR5-delta32",
                "description": "HIV resistance",
                "risk_allele": "D",
                "interpretation": {
                    "DD": ("protective", "CCR5-delta32 homozygous - high resistance to HIV-1"),
                    "DI": ("protective", "CCR5-delta32 heterozygous - partial protection against HIV"),
                    "ID": ("protective", "CCR5-delta32 heterozygous - partial protection against HIV"),
                    "--": ("protective", "Deletion - HIV resistance"),
                    "II": ("normal", "No CCR5 deletion - standard susceptibility"),
                }
            },
            "rs12979860": {
                "gene": "IL28B (IFNL3)",
                "description": "Hepatitis C - spontaneous clearance and response to therapy",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("protective", "Good response to hepatitis C therapy, high chance of clearance"),
                    "CT": ("moderate", "Intermediate response to hepatitis C therapy"),
                    "TC": ("moderate", "Intermediate response to hepatitis C therapy"),
                    "TT": ("low", "Poor response to hepatitis C therapy"),
                }
            },
            "rs601338": {
                "gene": "FUT2",
                "description": "Norovirus, rotavirus - secretor status",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("protective", "Non-secretor - resistance to norovirus and rotavirus"),
                    "AG": ("normal", "Secretor - standard susceptibility"),
                    "GA": ("normal", "Secretor - standard susceptibility"),
                    "GG": ("normal", "Secretor - standard susceptibility to norovirus"),
                }
            },
            "rs2814778": {
                "gene": "DARC (Duffy)",
                "description": "Plasmodium vivax malaria",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("protective", "Duffy-negative - resistance to P. vivax malaria"),
                    "CT": ("moderate", "Partial protection against P. vivax"),
                    "TC": ("moderate", "Partial protection against P. vivax"),
                    "TT": ("normal", "Duffy-positive - susceptibility to P. vivax"),
                }
            },
        }
    },

    "allergy": {
        "name": "Allergy and atopy",
        "snps": {
            "rs7216389": {
                "gene": "ORMDL3",
                "description": "Childhood asthma",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("high", "High risk of childhood asthma"),
                    "CT": ("moderate", "Increased risk of asthma"),
                    "TC": ("moderate", "Increased risk of asthma"),
                    "CC": ("normal", "Normal risk of asthma"),
                }
            },
            "rs61816761": {
                "gene": "FLG (filaggrin)",
                "description": "Atopic dermatitis, eczema",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Impaired skin barrier function - high risk of eczema"),
                    "AG": ("moderate", "Carrier - increased risk of atopic dermatitis"),
                    "GA": ("moderate", "Carrier - increased risk of atopic dermatitis"),
                    "GG": ("normal", "Normal filaggrin function"),
                }
            },
            "rs1801275": {
                "gene": "IL4RA",
                "description": "IL-4 receptor, atopy and allergy",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Increased IL-4 sensitivity - risk of atopy"),
                    "AG": ("moderate", "Moderately increased risk of allergy"),
                    "GA": ("moderate", "Moderately increased risk of allergy"),
                    "GG": ("normal", "Normal IL-4 sensitivity"),
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


def determine_celiac_risk(results):
    """Determine combined celiac disease risk from HLA-DQ2.5 and HLA-DQ8"""
    dq2 = None
    dq8 = None

    for r in results:
        if r['snp_id'] == 'rs2187668':
            dq2 = r
        elif r['snp_id'] == 'rs7454108':
            dq8 = r

    if not dq2 or not dq8:
        return None

    dq2_gt = dq2.get('genotype', '')
    dq8_gt = dq8.get('genotype', '')

    # Risk assessment
    dq2_risk = 'T' in dq2_gt if dq2_gt else False
    dq8_risk = 'C' in dq8_gt if dq8_gt else False

    if dq2_gt == 'TT':
        status = ('very_high', 'HLA-DQ2.5 homozygous - very high risk of celiac disease (>50%)')
    elif dq2_risk and dq8_risk:
        status = ('high', 'DQ2.5 + DQ8 - high risk of celiac disease')
    elif dq2_risk:
        status = ('moderate', 'HLA-DQ2.5 carrier - increased risk of celiac disease (~5-10%)')
    elif dq8_risk:
        status = ('low', 'HLA-DQ8 - small risk of celiac disease (~2%)')
    else:
        status = ('normal', 'Low risk of celiac disease (<1%)')

    return {
        'dq2_genotype': dq2_gt,
        'dq8_genotype': dq8_gt,
        'status': status[0],
        'interpretation': status[1]
    }


def determine_inflammation_profile(results):
    """Determine overall inflammation profile from cytokine SNPs"""
    proinflammatory = 0
    antiinflammatory = 0
    total = 0

    cytokine_info = []

    for r in results:
        if not r['found']:
            continue
        total += 1

        if r['snp_id'] == 'rs1800629':  # TNF-alpha
            if 'A' in r['genotype']:
                proinflammatory += 1
                cytokine_info.append(f"TNF-alpha ({r['genotype']}): elevated")
            else:
                cytokine_info.append(f"TNF-alpha ({r['genotype']}): normal")

        elif r['snp_id'] == 'rs1800795':  # IL-6
            if 'C' in r['genotype']:
                proinflammatory += 1
                cytokine_info.append(f"IL-6 ({r['genotype']}): elevated")
            else:
                cytokine_info.append(f"IL-6 ({r['genotype']}): normal")

        elif r['snp_id'] == 'rs1800896':  # IL-10 (anti-inflammatory)
            if r['genotype'] == 'GG':
                antiinflammatory += 1
                cytokine_info.append(f"IL-10 ({r['genotype']}): high (protective)")
            elif 'A' in r['genotype']:
                cytokine_info.append(f"IL-10 ({r['genotype']}): reduced")

        elif r['snp_id'] == 'rs16944':  # IL-1beta
            if 'A' in r['genotype']:
                proinflammatory += 1
                cytokine_info.append(f"IL-1beta ({r['genotype']}): elevated")
            else:
                cytokine_info.append(f"IL-1beta ({r['genotype']}): normal")

        elif r['snp_id'] == 'rs20541':  # IL-13
            if 'A' in r['genotype']:
                proinflammatory += 1
                cytokine_info.append(f"IL-13 ({r['genotype']}): elevated (allergy)")
            else:
                cytokine_info.append(f"IL-13 ({r['genotype']}): normal")

    if total == 0:
        return None

    if proinflammatory >= 3:
        profile = ('high_inflammation', 'Pro-inflammatory profile - anti-inflammatory diet recommended')
    elif proinflammatory >= 2:
        profile = ('moderate_inflammation', 'Moderately pro-inflammatory profile')
    elif antiinflammatory >= 1 and proinflammatory <= 1:
        profile = ('balanced', 'Balanced inflammatory profile')
    else:
        profile = ('normal', 'Normal inflammatory profile')

    return {
        'proinflammatory_count': proinflammatory,
        'antiinflammatory_count': antiinflammatory,
        'total_analyzed': total,
        'profile': profile[0],
        'interpretation': profile[1],
        'details': cytokine_info
    }


def generate_category_report(category, results, genome):
    """Generate report for a category"""
    cat_info = IMMUNITY_SNPS[category]

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

    return '\n'.join(report)


def generate_summary_report(all_results, genome):
    """Generate overall immunity summary report"""
    report = []
    report.append("# Immunity Analysis")
    report.append(f"\nAnalysis date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("\n---\n")

    report.append("## Important Warnings\n")
    report.append("1. **This is NOT a medical diagnosis** - informational analysis only")
    report.append("2. **Carrying a risk allele does NOT equal disease** - penetrance varies")
    report.append("3. **Immunity depends on many factors** - genes + lifestyle + environment")
    report.append("4. **For medical decisions** - consultation with an immunologist/allergist is required\n")

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
        report.append("## Increased Risk Markers\n")
        report.append("| Category | SNP | Gene | Genotype | Description |")
        report.append("|-----------|-----|-----|---------|----------|")
        for cat, r in high_risk:
            cat_name = IMMUNITY_SNPS[cat]['name']
            report.append(f"| {cat_name} | {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {r['interpretation']} |")
        report.append("")

    if moderate_risk:
        report.append("## Moderate Risk Markers\n")
        report.append("| Category | SNP | Gene | Genotype | Description |")
        report.append("|-----------|-----|-----|---------|----------|")
        for cat, r in moderate_risk:
            cat_name = IMMUNITY_SNPS[cat]['name']
            report.append(f"| {cat_name} | {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {r['interpretation']} |")
        report.append("")

    if protective:
        report.append("## Protective Variants\n")
        report.append("| Category | SNP | Gene | Genotype | Description |")
        report.append("|-----------|-----|-----|---------|----------|")
        for cat, r in protective:
            cat_name = IMMUNITY_SNPS[cat]['name']
            report.append(f"| {cat_name} | {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {r['interpretation']} |")
        report.append("")

    # Special analyses
    report.append("---\n")
    report.append("## Special Analyses\n")

    # Celiac disease risk
    hla_results = all_results.get('hla_system', [])
    celiac = determine_celiac_risk(hla_results)
    if celiac:
        report.append("### Celiac Disease Risk (HLA-DQ2.5/DQ8)\n")
        report.append(f"- HLA-DQ2.5 (rs2187668): {celiac['dq2_genotype']}")
        report.append(f"- HLA-DQ8 (rs7454108): {celiac['dq8_genotype']}")
        report.append(f"- **Status: {celiac['status']}**")
        report.append(f"- {celiac['interpretation']}\n")

    # Inflammation profile
    cytokine_results = all_results.get('cytokines', [])
    inflammation = determine_inflammation_profile(cytokine_results)
    if inflammation:
        report.append("### Inflammatory Profile (cytokines)\n")
        report.append(f"- Pro-inflammatory markers: {inflammation['proinflammatory_count']}")
        report.append(f"- Anti-inflammatory: {inflammation['antiinflammatory_count']}")
        report.append(f"- **Profile: {inflammation['profile']}**")
        report.append(f"- {inflammation['interpretation']}")
        report.append("\nDetails:")
        for detail in inflammation['details']:
            report.append(f"  - {detail}")
        report.append("")

    # Infection resistance summary
    report.append("### Infection Resistance\n")
    infection_results = all_results.get('infections', [])
    for r in infection_results:
        if r['found']:
            status = "protective" if r['risk_level'] == 'protective' else r['risk_level'] or 'n/a'
            report.append(f"- **{r['gene']}** ({r['genotype']}): {r['interpretation']}")

    report.append("\n---\n")
    report.append("## Analysis Statistics\n")

    total_snps = 0
    found_snps = 0
    for cat, results in all_results.items():
        total_snps += len(results)
        found_snps += sum(1 for r in results if r['found'])

    report.append(f"- Total SNPs analyzed: {total_snps}")
    report.append(f"- Found in genome: {found_snps}")
    report.append(f"- Not found: {total_snps - found_snps}")

    report.append("\n---\n")
    report.append("## Recommendations\n")
    report.append("### If pro-inflammatory markers are elevated:")
    report.append("- Anti-inflammatory diet (omega-3, turmeric, ginger)")
    report.append("- Monitor vitamin D levels")
    report.append("- Regular physical activity")
    report.append("- Stress management\n")
    report.append("### If at risk of autoimmune diseases:")
    report.append("- Regular autoantibody monitoring")
    report.append("- Avoid triggers (stress, infections)")
    report.append("- Consultation with a rheumatologist/immunologist\n")
    report.append("### If at risk of allergy/atopy:")
    report.append("- Strengthen the skin barrier (emollients)")
    report.append("- Identify and avoid allergens")
    report.append("- Probiotics for immune modulation")

    return '\n'.join(report)


def main():
    print("=" * 60)
    print("IMMUNITY ANALYSIS FROM 23andMe GENOME")
    print("=" * 60)

    print("\n[1/4] Loading genome...")
    genome = load_genome()
    print(f"      Loaded {len(genome)} SNP")

    print("\n[2/4] Analyzing markers by category...")
    all_results = {}

    for category, cat_info in IMMUNITY_SNPS.items():
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
        report_dir = f"{REPORTS_PATH}/{category}"
        os.makedirs(report_dir, exist_ok=True)
        report_path = f"{report_dir}/report.md"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"      -> {report_path}")

    print("\n[4/4] Generating summary report...")
    summary = generate_summary_report(all_results, genome)
    summary_dir = f"{REPORTS_PATH}/immunity"
    os.makedirs(summary_dir, exist_ok=True)
    summary_path = f"{summary_dir}/report.md"
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
        protective_found = [r for r in results if r['risk_level'] == 'protective']

        if high_risk:
            print(f"  {IMMUNITY_SNPS[category]['name']}:")
            for r in high_risk:
                print(f"    * {r['gene']} ({r['genotype']}): {r['interpretation']}")
            print()

        if protective_found:
            print(f"  {IMMUNITY_SNPS[category]['name']} (protective):")
            for r in protective_found:
                print(f"    + {r['gene']} ({r['genotype']}): {r['interpretation']}")
            print()


if __name__ == "__main__":
    main()

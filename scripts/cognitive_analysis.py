#!/usr/bin/env python3
"""
Cognitive SNP Analysis Script
Analyzes cognitive-related genetic markers from 23andMe data
"""

import os
from collections import defaultdict
from datetime import datetime

# Paths
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENOME_FILE = f"{BASE_PATH}/data/my_dna_file.txt"
REPORTS_PATH = f"{BASE_PATH}/reports"

# =============================================================================
# SNP DATABASE - Organized by cognitive category
# =============================================================================

COGNITIVE_SNPS = {
    "memory": {
        "name": "Memory",
        "snps": {
            "rs17070145": {
                "gene": "KIBRA (WWC1)",
                "description": "Episodic memory, memory consolidation",
                "risk_allele": "C",
                "interpretation": {
                    "TT": ("excellent", "Best episodic memory - homozygous for the favorable allele"),
                    "CT": ("good", "Good episodic memory - heterozygous"),
                    "CC": ("normal", "Typical episodic memory"),
                }
            },
            "rs4680": {
                "gene": "COMT Val158Met",
                "description": "Working memory, cognitive flexibility, stress resilience",
                "risk_allele": "-",
                "interpretation": {
                    "AA": ("info", "Met/Met ('Worrier') - better working memory at rest, higher anxiety under stress"),
                    "AG": ("info", "Val/Met - balanced type, adaptive cognitive flexibility"),
                    "GA": ("info", "Val/Met - balanced type, adaptive cognitive flexibility"),
                    "GG": ("info", "Val/Val ('Warrior') - better cognition under stress, worse at rest"),
                }
            },
            "rs6265": {
                "gene": "BDNF Val66Met",
                "description": "Neuroplasticity, learning, memory",
                "risk_allele": "A",
                "interpretation": {
                    "GG": ("normal", "Val/Val - normal BDNF secretion, good neuroplasticity"),
                    "CC": ("normal", "Val/Val - normal BDNF secretion, good neuroplasticity"),
                    "AG": ("moderate", "Val/Met - slightly reduced BDNF secretion"),
                    "CT": ("moderate", "Val/Met - slightly reduced BDNF secretion"),
                    "AA": ("reduced", "Met/Met - reduced neuroplasticity, but can be compensated by exercise"),
                    "TT": ("reduced", "Met/Met - reduced neuroplasticity, but can be compensated by exercise"),
                }
            },
        }
    },

    "cognitive_aging": {
        "name": "Cognitive Aging",
        "snps": {
            "rs429358": {
                "gene": "APOE (e4 marker)",
                "description": "Alzheimer's disease, cognitive aging",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("high", "Probably e4/e4 - significantly increased risk of cognitive decline"),
                    "CT": ("moderate", "Probably an e4 carrier - moderately increased risk"),
                    "TC": ("moderate", "Probably an e4 carrier - moderately increased risk"),
                    "TT": ("normal", "No e4 allele - typical risk of cognitive aging"),
                }
            },
            "rs7412": {
                "gene": "APOE (e2 marker)",
                "description": "Protective allele against Alzheimer's",
                "risk_allele": "T",
                "interpretation": {
                    "CC": ("info", "Used together with rs429358 to determine APOE genotype"),
                    "CT": ("protective", "Possibly an e2 carrier - protective effect"),
                    "TC": ("protective", "Possibly an e2 carrier - protective effect"),
                    "TT": ("info", "Used together with rs429358 to determine APOE genotype"),
                }
            },
            "rs9536314": {
                "gene": "KLOTHO",
                "description": "Longevity gene, brain protection against aging",
                "risk_allele": "-",
                "interpretation": {
                    "GT": ("excellent", "KL-VS heterozygote - optimal variant, best cognitive aging"),
                    "TG": ("excellent", "KL-VS heterozygote - optimal variant, best cognitive aging"),
                    "GG": ("normal", "Wild type - typical cognitive aging"),
                    "TT": ("reduced", "KL-VS homozygote - possibly reduced function (rare)"),
                }
            },
            "rs2802292": {
                "gene": "FOXO3",
                "description": "Longevity gene, neuron protection, cellular stress",
                "risk_allele": "T",
                "interpretation": {
                    "GG": ("excellent", "Associated with longevity and better cognitive health"),
                    "GT": ("good", "Heterozygous - moderately protective effect"),
                    "TG": ("good", "Heterozygous - moderately protective effect"),
                    "TT": ("normal", "Typical variant"),
                }
            },
        }
    },

    "attention": {
        "name": "Attention and Dopamine",
        "snps": {
            "rs1800955": {
                "gene": "DRD4 -521 C/T",
                "description": "Dopamine receptor D4, attention, ADHD",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("info", "Reduced DRD4 expression - may affect attention"),
                    "CT": ("info", "Heterozygous - intermediate DRD4 expression"),
                    "TC": ("info", "Heterozygous - intermediate DRD4 expression"),
                    "CC": ("normal", "Normal D4 receptor expression"),
                }
            },
            "rs1800497": {
                "gene": "DRD2/ANKK1 Taq1A",
                "description": "D2 dopamine receptors, attention, reinforcement learning",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("moderate", "A1/A1 - fewer D2 receptors, may affect learning and motivation"),
                    "AG": ("low", "A1/A2 - moderately reduced D2 receptors"),
                    "GA": ("low", "A1/A2 - moderately reduced D2 receptors"),
                    "GG": ("normal", "A2/A2 - normal number of D2 receptors"),
                }
            },
            "rs27072": {
                "gene": "DAT1 (SLC6A3)",
                "description": "Dopamine transporter, information processing speed",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("info", "May affect dopaminergic transmission"),
                    "AG": ("info", "Heterozygous"),
                    "GA": ("info", "Heterozygous"),
                    "GG": ("normal", "Typical dopamine transport"),
                }
            },
        }
    },

    "verbal": {
        "name": "Verbal Abilities",
        "snps": {
            "rs7794745": {
                "gene": "CNTNAP2",
                "description": "Speech development, language abilities",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("moderate", "Associated with reduced language abilities"),
                    "AT": ("low", "Heterozygous - small effect"),
                    "TA": ("low", "Heterozygous - small effect"),
                    "AA": ("normal", "Normal language abilities"),
                }
            },
            "rs17236239": {
                "gene": "CNTNAP2",
                "description": "Contactin-associated protein, neurodevelopment",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("moderate", "May affect language development"),
                    "AG": ("low", "Heterozygous"),
                    "GA": ("low", "Heterozygous"),
                    "GG": ("normal", "Normal variant"),
                }
            },
            "rs759178": {
                "gene": "FOXP2",
                "description": "Speech and language gene, articulation, grammar",
                "risk_allele": "-",
                "interpretation": {
                    "AA": ("info", "FOXP2 speech gene variant"),
                    "AG": ("info", "FOXP2 heterozygote"),
                    "GA": ("info", "FOXP2 heterozygote"),
                    "GG": ("info", "FOXP2 speech gene variant"),
                }
            },
        }
    },

    "neuroprotection": {
        "name": "Neuroprotection",
        "snps": {
            "rs1800629": {
                "gene": "TNF-a -308",
                "description": "Neuroinflammation, inflammatory response in the brain",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "High TNF-a production - increased neuroinflammation"),
                    "AG": ("moderate", "Moderately increased TNF-a production"),
                    "GA": ("moderate", "Moderately increased TNF-a production"),
                    "GG": ("normal", "Normal TNF-a level"),
                }
            },
            "rs1800795": {
                "gene": "IL-6 -174",
                "description": "Interleukin-6, neuroinflammation, cognitive aging",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("moderate", "Increased IL-6 production - more inflammation"),
                    "CG": ("low", "Moderately increased IL-6 level"),
                    "GC": ("low", "Moderately increased IL-6 level"),
                    "GG": ("normal", "Normal IL-6 level - less neuroinflammation"),
                }
            },
            "rs1800896": {
                "gene": "IL-10 -1082",
                "description": "Anti-inflammatory cytokine, brain protection",
                "risk_allele": "A",
                "interpretation": {
                    "GG": ("protective", "High IL-10 production - good anti-inflammatory protection"),
                    "AG": ("normal", "Intermediate IL-10 production"),
                    "GA": ("normal", "Intermediate IL-10 production"),
                    "CT": ("normal", "Intermediate IL-10 production"),
                    "TC": ("normal", "Intermediate IL-10 production"),
                    "AA": ("reduced", "Low IL-10 production - reduced anti-inflammatory protection"),
                    "TT": ("reduced", "Low IL-10 production - reduced anti-inflammatory protection"),
                    "CC": ("protective", "High IL-10 production - good anti-inflammatory protection"),
                }
            },
        }
    },

    "caffeine_cognition": {
        "name": "Caffeine and Cognition",
        "snps": {
            "rs762551": {
                "gene": "CYP1A2",
                "description": "Caffeine metabolism, cognitive effects of coffee",
                "risk_allele": "C",
                "interpretation": {
                    "AA": ("excellent", "Fast metabolizer - caffeine improves cognition, low risk of side effects"),
                    "AC": ("good", "Intermediate metabolizer - moderate benefit from caffeine"),
                    "CA": ("good", "Intermediate metabolizer - moderate benefit from caffeine"),
                    "CC": ("reduced", "Slow metabolizer - caffeine may cause anxiety and insomnia"),
                }
            },
            "rs5751876": {
                "gene": "ADORA2A",
                "description": "Adenosine receptor, caffeine-induced anxiety",
                "risk_allele": "C",
                "interpretation": {
                    "TT": ("excellent", "Less anxiety from coffee, better cognitive effect"),
                    "CT": ("good", "Moderate sensitivity to caffeine-induced anxiety"),
                    "TC": ("good", "Moderate sensitivity to caffeine-induced anxiety"),
                    "CC": ("sensitive", "High caffeine-induced anxiety - limiting intake is recommended"),
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


def determine_apoe_genotype(genome):
    """Determine APOE genotype from rs429358 and rs7412"""
    rs429358 = genome.get('rs429358', {}).get('genotype', '')
    rs7412 = genome.get('rs7412', {}).get('genotype', '')

    # APOE determination table
    # rs429358 (C=e4), rs7412 (T=e2)
    apoe_table = {
        ('TT', 'CC'): ('e2/e2', 'protective', 'Protective genotype - reduced risk of cognitive decline'),
        ('TT', 'CT'): ('e2/e3', 'protective', 'Slightly reduced risk'),
        ('CT', 'CC'): ('e2/e4', 'moderate', 'Mixed - one protective allele, one risk allele'),
        ('TT', 'TT'): ('e3/e3', 'normal', 'Most common genotype - typical risk'),
        ('CT', 'CT'): ('e3/e4', 'high', 'Increased risk of cognitive decline (~3x)'),
        ('CC', 'TT'): ('e4/e4', 'very_high', 'Significantly increased risk (~12x)'),
        ('CT', 'TT'): ('e3/e4', 'high', 'Increased risk of cognitive decline (~3x)'),
        ('CC', 'CT'): ('e4/e4 or e3/e4', 'high', 'Increased risk'),
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
        'apoe_genotype': 'Not determined',
        'risk_level': 'unknown',
        'interpretation': f'Combination {rs429358}/{rs7412} not in table'
    }


def determine_comt_profile(genome):
    """Determine COMT cognitive profile from rs4680"""
    rs4680 = genome.get('rs4680', {}).get('genotype', '')

    profiles = {
        'AA': ('Worrier (Met/Met)', 'cognitive',
               'Better working memory and executive function in a calm state. '
               'May experience reduced cognition under stress. Recommended: '
               'meditation, stress management, avoiding excess caffeine.'),
        'AG': ('Intermediate (Val/Met)', 'balanced',
               'Balanced profile. Adaptive cognitive flexibility - '
               'works well both at rest and under moderate stress.'),
        'GA': ('Intermediate (Val/Met)', 'balanced',
               'Balanced profile. Adaptive cognitive flexibility - '
               'works well both at rest and under moderate stress.'),
        'GG': ('Warrior (Val/Val)', 'stress_resilient',
               'Better cognitive function under stress and pressure. '
               'May perform worse in routine, calm conditions. '
               'Recommended: moderate stress for optimal performance, deadlines.')
    }

    if rs4680 in profiles:
        name, profile_type, desc = profiles[rs4680]
        return {
            'genotype': rs4680,
            'profile_name': name,
            'profile_type': profile_type,
            'description': desc
        }

    return {
        'genotype': rs4680,
        'profile_name': 'Not determined',
        'profile_type': 'unknown',
        'description': 'Genotype not recognized'
    }


def determine_caffeine_response(genome):
    """Determine cognitive response to caffeine"""
    rs762551 = genome.get('rs762551', {}).get('genotype', '')
    rs5751876 = genome.get('rs5751876', {}).get('genotype', '')

    # Metabolism speed
    metabolism = 'unknown'
    if rs762551 == 'AA':
        metabolism = 'fast'
    elif rs762551 in ['AC', 'CA']:
        metabolism = 'intermediate'
    elif rs762551 == 'CC':
        metabolism = 'slow'

    # Anxiety sensitivity
    anxiety = 'unknown'
    if rs5751876 == 'TT':
        anxiety = 'low'
    elif rs5751876 in ['CT', 'TC']:
        anxiety = 'moderate'
    elif rs5751876 == 'CC':
        anxiety = 'high'

    # Combined recommendation
    recommendations = {
        ('fast', 'low'): ('excellent', 'Excellent caffeine responder. 2-4 cups of coffee will improve cognition without side effects.'),
        ('fast', 'moderate'): ('good', 'Good responder. 2-3 cups of coffee, avoid after lunch.'),
        ('fast', 'high'): ('moderate', 'Fast metabolism but high anxiety. Limit to 1-2 cups in the morning.'),
        ('intermediate', 'low'): ('good', 'Moderate responder. 1-2 cups of coffee, no later than 14:00.'),
        ('intermediate', 'moderate'): ('moderate', 'Intermediate sensitivity. 1-2 cups in the morning.'),
        ('intermediate', 'high'): ('limited', 'Intermediate metabolism + high anxiety. Consider green tea.'),
        ('slow', 'low'): ('moderate', 'Slow metabolism. 1 cup in the morning, avoid after noon.'),
        ('slow', 'moderate'): ('limited', 'Slow metabolism + anxiety. Maximum 1 cup in the morning.'),
        ('slow', 'high'): ('avoid', 'Slow metabolism + high anxiety. Avoiding caffeine is recommended.'),
    }

    key = (metabolism, anxiety)
    if key in recommendations:
        response, rec = recommendations[key]
    else:
        response, rec = ('unknown', 'Insufficient data for a recommendation')

    return {
        'cyp1a2_genotype': rs762551,
        'adora2a_genotype': rs5751876,
        'metabolism': metabolism,
        'anxiety_sensitivity': anxiety,
        'response_type': response,
        'recommendation': rec
    }


def generate_cognitive_report(all_results, genome):
    """Generate comprehensive cognitive report"""
    report = []
    report.append("# Cognitive Genetic Profile")
    report.append(f"\nAnalysis date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("\n---\n")

    report.append("## Important Disclaimers\n")
    report.append("1. **This is NOT a medical diagnosis** - informational analysis only")
    report.append("2. **Genetics is not destiny** - environment and lifestyle matter more")
    report.append("3. **Cognitive abilities are multifactorial** - a single gene does not determine intelligence")
    report.append("4. **For medical decisions** - consulting a specialist is mandatory\n")

    report.append("---\n")

    # Statistics
    total_found = 0
    total_snps = 0
    for cat, results in all_results.items():
        total_snps += len(results)
        total_found += sum(1 for r in results if r['found'])

    report.append(f"## Analysis Statistics\n")
    report.append(f"- SNPs analyzed: {total_snps}")
    report.append(f"- Found in genome: {total_found}")
    report.append(f"- Not found: {total_snps - total_found}\n")

    report.append("---\n")

    # COMT Profile
    report.append("## COMT Cognitive Profile\n")
    comt = determine_comt_profile(genome)
    report.append(f"- **rs4680 genotype:** {comt['genotype']}")
    report.append(f"- **Profile:** {comt['profile_name']}")
    report.append(f"- **Description:** {comt['description']}\n")

    # APOE for cognitive aging
    report.append("## APOE Genotype (Cognitive Aging)\n")
    apoe = determine_apoe_genotype(genome)
    report.append(f"- rs429358: {apoe['rs429358']}")
    report.append(f"- rs7412: {apoe['rs7412']}")
    report.append(f"- **APOE genotype:** {apoe['apoe_genotype']}")
    report.append(f"- **Risk level:** {apoe['risk_level']}")
    report.append(f"- {apoe['interpretation']}\n")

    # Caffeine response
    report.append("## Caffeine Response\n")
    caffeine = determine_caffeine_response(genome)
    report.append(f"- **CYP1A2 (rs762551):** {caffeine['cyp1a2_genotype']} - metabolism: {caffeine['metabolism']}")
    report.append(f"- **ADORA2A (rs5751876):** {caffeine['adora2a_genotype']} - anxiety: {caffeine['anxiety_sensitivity']}")
    report.append(f"- **Response type:** {caffeine['response_type']}")
    report.append(f"- **Recommendation:** {caffeine['recommendation']}\n")

    report.append("---\n")

    # Detailed results by category
    for category, results in all_results.items():
        cat_info = COGNITIVE_SNPS[category]
        report.append(f"## {cat_info['name']}\n")

        # Table
        report.append("| SNP | Gene | Genotype | Status | Interpretation |")
        report.append("|-----|-----|---------|--------|---------------|")

        for r in results:
            if r['found']:
                status = r['risk_level'] or 'n/a'
                interp = r['interpretation'] or 'No data'
                report.append(f"| {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {status} | {interp} |")
            else:
                report.append(f"| {r['snp_id']} | {r['gene']} | - | - | Not found in genome |")

        report.append("")

    report.append("---\n")

    # Key findings summary
    report.append("## Key Findings\n")

    # Collect notable findings
    excellent = []
    protective = []
    moderate_concerns = []
    high_concerns = []

    for category, results in all_results.items():
        for r in results:
            if r['risk_level'] == 'excellent':
                excellent.append((category, r))
            elif r['risk_level'] == 'protective':
                protective.append((category, r))
            elif r['risk_level'] in ['moderate', 'reduced']:
                moderate_concerns.append((category, r))
            elif r['risk_level'] in ['high', 'very_high']:
                high_concerns.append((category, r))

    if excellent:
        report.append("### Strengths\n")
        for cat, r in excellent:
            report.append(f"- **{r['gene']}** ({r['genotype']}): {r['interpretation']}")
        report.append("")

    if protective:
        report.append("### Protective Factors\n")
        for cat, r in protective:
            report.append(f"- **{r['gene']}** ({r['genotype']}): {r['interpretation']}")
        report.append("")

    if high_concerns:
        report.append("### Needs Attention\n")
        for cat, r in high_concerns:
            report.append(f"- **{r['gene']}** ({r['genotype']}): {r['interpretation']}")
        report.append("")

    if moderate_concerns:
        report.append("### Moderate Traits\n")
        for cat, r in moderate_concerns:
            report.append(f"- **{r['gene']}** ({r['genotype']}): {r['interpretation']}")
        report.append("")

    report.append("---\n")

    # Recommendations
    report.append("## Recommendations for Optimizing Cognitive Function\n")

    report.append("### Based on your profile:\n")

    # COMT-based recommendations
    if comt['profile_type'] == 'cognitive':
        report.append("**COMT (Worrier):**")
        report.append("- Practice meditation and breathing techniques")
        report.append("- Limit caffeine during stressful periods")
        report.append("- Magnesium and L-theanine may help\n")
    elif comt['profile_type'] == 'stress_resilient':
        report.append("**COMT (Warrior):**")
        report.append("- Use moderate stress for motivation")
        report.append("- Deadlines and competition will improve productivity")
        report.append("- Avoid overly calm routines\n")

    # BDNF-based recommendations
    bdnf_result = None
    for r in all_results.get('memory', []):
        if r['snp_id'] == 'rs6265':
            bdnf_result = r
            break

    if bdnf_result and bdnf_result['risk_level'] in ['moderate', 'reduced']:
        report.append("**BDNF (reduced neuroplasticity):**")
        report.append("- Regular aerobic exercise is CRITICALLY important")
        report.append("- Learning new things (languages, music) stimulates BDNF")
        report.append("- Omega-3 and curcumin support neuroplasticity\n")

    # Inflammation-based recommendations
    inflammation_concern = False
    for r in all_results.get('neuroprotection', []):
        if r['risk_level'] in ['high', 'moderate']:
            inflammation_concern = True
            break

    if inflammation_concern:
        report.append("**Neuroinflammation:**")
        report.append("- Anti-inflammatory diet (Mediterranean)")
        report.append("- Omega-3 fatty acids")
        report.append("- Adequate sleep (7-9 hours)")
        report.append("- Control of chronic stress\n")

    report.append("### General recommendations:\n")
    report.append("- Regular physical exercise (150+ min/week)")
    report.append("- Quality sleep of 7-9 hours")
    report.append("- Continuous learning and intellectual challenges")
    report.append("- Social activity")
    report.append("- Stress management")
    report.append("- Mediterranean or MIND diet\n")

    return '\n'.join(report)


def main():
    print("=" * 60)
    print("COGNITIVE GENETIC ANALYSIS")
    print("=" * 60)

    print("\n[1/3] Loading genome...")
    genome = load_genome()
    print(f"      Loaded {len(genome)} SNPs")

    print("\n[2/3] Analyzing cognitive markers...")
    all_results = {}

    for category, cat_info in COGNITIVE_SNPS.items():
        print(f"      -> {cat_info['name']}...")
        results = []
        for snp_id, snp_info in cat_info['snps'].items():
            result = analyze_snp(snp_id, snp_info, genome)
            results.append(result)
        all_results[category] = results

        # Count found
        found = sum(1 for r in results if r['found'])
        print(f"         Found: {found}/{len(results)}")

    print("\n[3/3] Generating report...")
    report = generate_cognitive_report(all_results, genome)

    # Ensure directory exists
    report_dir = f"{REPORTS_PATH}/cognitive"
    os.makedirs(report_dir, exist_ok=True)

    report_path = f"{report_dir}/report.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"      -> {report_path}")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

    # Print key findings to console
    print("\nKEY FINDINGS:\n")

    # COMT profile
    comt = determine_comt_profile(genome)
    print(f"COMT profile: {comt['profile_name']}")
    print(f"   {comt['description'][:80]}...\n")

    # APOE
    apoe = determine_apoe_genotype(genome)
    print(f"APOE genotype: {apoe['apoe_genotype']}")
    print(f"   {apoe['interpretation']}\n")

    # Caffeine
    caffeine = determine_caffeine_response(genome)
    print(f"Caffeine: {caffeine['response_type']}")
    print(f"   {caffeine['recommendation']}\n")

    # Notable findings
    for category, results in all_results.items():
        notable = [r for r in results if r['risk_level'] in ['excellent', 'high', 'very_high', 'protective']]
        if notable:
            print(f"{COGNITIVE_SNPS[category]['name']}:")
            for r in notable:
                print(f"   * {r['gene']} ({r['genotype']}): {r['interpretation']}")
            print()


if __name__ == "__main__":
    main()

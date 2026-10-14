#!/usr/bin/env python3
"""
Sports and Fitness Genetic Analysis Script
Analyzes athletic performance markers from 23andMe data
"""

import os
from collections import defaultdict
from datetime import datetime

# Paths
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENOME_FILE = f"{BASE_PATH}/data/my_dna_file.txt"
REPORTS_PATH = f"{BASE_PATH}/reports"

# =============================================================================
# SNP DATABASE - Sports and Fitness Markers
# =============================================================================

SPORTS_SNPS = {
    "muscle_fiber_type": {
        "name": "Muscle fiber type",
        "description": "Determines the ratio of fast-twitch to slow-twitch muscle fibers",
        "snps": {
            "rs1815739": {
                "gene": "ACTN3",
                "description": "Alpha-actinin-3 - key protein of fast-twitch muscle fibers",
                "interpretation": {
                    "CC": ("power", "RR - Fully functional ACTN3. Fast-twitch muscle fibers (type II). Predisposition to sprint and power sports"),
                    "CT": ("mixed", "RX - Mixed type. One functional allele. Versatile abilities"),
                    "TT": ("endurance", "XX - ACTN3 deficiency. Slow-twitch fibers (type I). Predisposition to endurance"),
                }
            },
        }
    },

    "endurance": {
        "name": "Endurance",
        "description": "Markers of aerobic endurance and fat metabolism",
        "snps": {
            "rs4253778": {
                "gene": "PPARA",
                "description": "Regulator of fatty acid metabolism and energy exchange",
                "interpretation": {
                    "GG": ("high", "G/G - High PPARA expression. Efficient fat oxidation. Good endurance"),
                    "GC": ("moderate", "G/C - Intermediate activity. Moderate endurance capacity"),
                    "CC": ("low", "C/C - Reduced PPARA activity. Less efficient fat utilization"),
                }
            },
            "rs8192678": {
                "gene": "PPARGC1A (PGC-1α)",
                "description": "Master regulator of mitochondrial biogenesis",
                "interpretation": {
                    "CC": ("high", "Gly/Gly - High PGC-1α activity. Excellent mitochondrial biogenesis"),
                    "CT": ("moderate", "Gly/Ser - Moderate activity. Good endurance potential"),
                    "TT": ("low", "Ser/Ser - Reduced activity. Smaller adaptive response to endurance training"),
                }
            },
            "rs2010963": {
                "gene": "VEGFA",
                "description": "Vascular endothelial growth factor - angiogenesis and muscle blood supply",
                "interpretation": {
                    "GG": ("high", "G/G - High VEGF expression. Excellent angiogenesis and muscle capillarization"),
                    "GC": ("moderate", "G/C - Moderate expression. Good blood supply"),
                    "CC": ("low", "C/C - Reduced VEGF expression. Smaller angiogenic response to training"),
                }
            },
        }
    },

    "strength": {
        "name": "Strength and muscle mass",
        "description": "Markers of strength capacity and hypertrophy",
        "snps": {
            "rs1800795": {
                "gene": "IL-6",
                "description": "Interleukin-6 - regulator of inflammation and muscle adaptation",
                "interpretation": {
                    "GG": ("high", "G/G - Low IL-6 production. Better recovery. Good strength potential"),
                    "GC": ("moderate", "G/C - Moderate production. Balanced response"),
                    "CG": ("moderate", "C/G - Moderate production. Balanced response"),
                    "CC": ("low", "C/C - High IL-6 production. More inflammation. Slower recovery"),
                }
            },
            "rs35767": {
                "gene": "IGF1",
                "description": "Insulin-like growth factor 1 - key anabolic hormone",
                "interpretation": {
                    "CC": ("high", "C/C - High IGF-1 level. Good potential for gaining muscle mass"),
                    "CT": ("moderate", "C/T - Intermediate IGF-1 level. Moderate anabolic potential"),
                    "TT": ("low", "T/T - Reduced IGF-1. Harder to gain muscle mass"),
                }
            },
        }
    },

    "lactate_clearance": {
        "name": "Lactate metabolism",
        "description": "Ability to clear lactic acid",
        "snps": {
            "rs1049434": {
                "gene": "MCT1 (SLC16A1)",
                "description": "Monocarboxylate transporter - lactate efflux from muscles",
                "interpretation": {
                    "AA": ("high", "A/A - High MCT1 activity. Fast lactate clearance. Excellent for interval training"),
                    "AT": ("moderate", "A/T - Intermediate activity. Moderate lactate clearance"),
                    "TT": ("low", "T/T - Reduced MCT1 activity. Slower lactate clearance. Longer recovery between sets"),
                }
            },
        }
    },

    "recovery": {
        "name": "Recovery",
        "description": "Markers of regeneration and anti-inflammatory response",
        "snps": {
            "rs1800629": {
                "gene": "TNF-α",
                "description": "Tumor necrosis factor alpha - inflammation and catabolism",
                "interpretation": {
                    "GG": ("fast", "G/G - Low TNF-α production. Fast recovery. Less inflammation after workouts"),
                    "GA": ("moderate", "G/A - Moderate production. Average recovery"),
                    "AG": ("moderate", "A/G - Moderate production. Average recovery"),
                    "AA": ("slow", "A/A - High TNF-α production. Slow recovery. More muscle soreness"),
                }
            },
            "rs4880": {
                "gene": "SOD2 (MnSOD)",
                "description": "Superoxide dismutase 2 - antioxidant defense of mitochondria",
                "interpretation": {
                    "TT": ("high", "Val/Val - High SOD2 activity. Excellent protection against oxidative stress"),
                    "CT": ("moderate", "Val/Ala - Intermediate activity. Good antioxidant defense"),
                    "TC": ("moderate", "Val/Ala - Intermediate activity. Good antioxidant defense"),
                    "CC": ("low", "Ala/Ala - Reduced mitochondrial SOD2 activity. More oxidative stress"),
                    "AA": ("high", "Val/Val - High SOD2 activity. Excellent protection against oxidative stress"),
                    "AG": ("moderate", "Val/Ala - Intermediate activity. Good antioxidant defense"),
                    "GG": ("low", "Ala/Ala - Reduced SOD2 activity. More oxidative stress"),
                }
            },
        }
    },

    "injury_risk": {
        "name": "Injury risk",
        "description": "Markers of connective tissue strength",
        "snps": {
            "rs12722": {
                "gene": "COL5A1",
                "description": "Type V collagen - tendon structure",
                "interpretation": {
                    "CC": ("low_risk", "C/C - Strong tendons. Low risk of tendinopathy"),
                    "CT": ("moderate_risk", "C/T - Intermediate tendon strength"),
                    "TT": ("high_risk", "T/T - Increased collagen elasticity. Higher risk of tendon injuries (Achilles, patellar)"),
                }
            },
            "rs1800012": {
                "gene": "COL1A1",
                "description": "Type I collagen - structure of ligaments and bones",
                "interpretation": {
                    "GG": ("low_risk", "G/G - Dense collagen. Low risk of ligament tears"),
                    "GT": ("moderate_risk", "G/T - Intermediate ligament strength. Moderate risk"),
                    "TG": ("moderate_risk", "T/G - Intermediate ligament strength. Moderate risk"),
                    "TT": ("high_risk", "T/T - Reduced collagen density. Increased risk of ACL and other ligament injuries"),
                    "CC": ("low_risk", "C/C - Dense collagen. Low risk of ligament tears"),
                    "CT": ("moderate_risk", "C/T - Intermediate ligament strength. Moderate risk"),
                    "AA": ("high_risk", "A/A - Reduced collagen density. Increased risk of ligament injuries"),
                }
            },
            "rs2228570": {
                "gene": "VDR (FokI)",
                "description": "Vitamin D receptor - bone health",
                "interpretation": {
                    "CC": ("low_risk", "F/F (C/C) - Active VDR receptor. Good calcium absorption. Strong bones"),
                    "CT": ("moderate_risk", "F/f (C/T) - Intermediate VDR activity"),
                    "TC": ("moderate_risk", "F/f (T/C) - Intermediate VDR activity"),
                    "TT": ("high_risk", "f/f (T/T) - Reduced VDR activity. Risk of low bone density. Vitamin D is important"),
                }
            },
        }
    },

    "vo2max_potential": {
        "name": "VO2max potential",
        "description": "Composite assessment of aerobic power (based on PPARGC1A, PPARA, VEGFA)",
        "snps": {}  # Calculated from endurance markers
    },

    "motor_learning": {
        "name": "Motor learning",
        "description": "Ability to acquire new motor skills",
        "snps": {
            "rs6265": {
                "gene": "BDNF",
                "description": "Brain-derived neurotrophic factor - neuroplasticity and motor memory",
                "interpretation": {
                    "CC": ("high", "Val/Val - High BDNF secretion. Fast technique acquisition. Excellent motor memory"),
                    "CT": ("moderate", "Val/Met - Moderate secretion. Good motor learning"),
                    "TC": ("moderate", "Val/Met - Moderate secretion. Good motor learning"),
                    "TT": ("low", "Met/Met - Reduced BDNF secretion. Slower acquisition of new skills. Needs more repetitions"),
                    "GG": ("high", "Val/Val - High BDNF secretion. Fast technique acquisition"),
                    "AG": ("moderate", "Val/Met - Moderate BDNF secretion"),
                    "GA": ("moderate", "Val/Met - Moderate BDNF secretion"),
                    "AA": ("low", "Met/Met - Reduced BDNF secretion. More practice required"),
                }
            },
        }
    },

    "stress_response": {
        "name": "Stress resilience",
        "description": "Psychological resilience to competitive stress",
        "snps": {
            "rs4680": {
                "gene": "COMT",
                "description": "Catechol-O-methyltransferase - dopamine metabolism",
                "interpretation": {
                    "GG": ("warrior", "Val/Val - 'Warrior'. Fast dopamine metabolism. Stress-resistant. Performs better in high-pressure competition"),
                    "AG": ("mixed", "Val/Met - Mixed type. Balance between stress resilience and cognitive precision"),
                    "GA": ("mixed", "Val/Met - Mixed type. Balance between stress resilience and cognitive precision"),
                    "AA": ("worrier", "Met/Met - 'Worrier'. Slow metabolism. Higher anxiety under pressure, but better precision and planning"),
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
        'found': False,
        'genotype': None,
        'phenotype': None,
        'interpretation': None
    }

    if snp_id in genome_data:
        result['found'] = True
        raw_genotype = genome_data[snp_id]['genotype']
        result['genotype'] = raw_genotype
        result['chromosome'] = genome_data[snp_id]['chromosome']
        result['position'] = genome_data[snp_id]['position']

        # Try to find interpretation
        interpretations = snp_info.get('interpretation', {})

        # Try original, normalized, and reversed genotype
        for gt in [raw_genotype, normalize_genotype(raw_genotype), raw_genotype[::-1] if len(raw_genotype) == 2 else raw_genotype]:
            if gt in interpretations:
                result['phenotype'], result['interpretation'] = interpretations[gt]
                break

    return result


def analyze_sports(genome):
    """Analyze all sports-related SNPs"""
    all_results = {}

    for category, cat_info in SPORTS_SNPS.items():
        if not cat_info['snps']:  # Skip calculated categories
            continue

        results = []
        for snp_id, snp_info in cat_info['snps'].items():
            result = analyze_snp(snp_id, snp_info, genome)
            results.append(result)
        all_results[category] = results

    return all_results


def calculate_vo2max_potential(results):
    """Calculate VO2max potential based on endurance markers"""
    endurance_results = results.get('endurance', [])

    score = 0
    max_score = 0
    markers_found = 0

    scoring = {
        'high': 3,
        'moderate': 2,
        'low': 1
    }

    for r in endurance_results:
        if r['found'] and r['phenotype']:
            markers_found += 1
            max_score += 3
            score += scoring.get(r['phenotype'], 0)

    if markers_found == 0:
        return None

    percentage = (score / max_score) * 100

    if percentage >= 80:
        level = "Excellent"
        description = "High genetic potential for developing VO2max. You respond well to aerobic training."
    elif percentage >= 60:
        level = "Good"
        description = "Good VO2max potential. With proper training, high performance can be achieved."
    elif percentage >= 40:
        level = "Average"
        description = "Average potential. Progress is possible, but it may take more time."
    else:
        level = "Below average"
        description = "Genetically less predisposed to high aerobic performance. A focus on strength-based sports is recommended."

    return {
        'score': score,
        'max_score': max_score,
        'percentage': percentage,
        'level': level,
        'description': description,
        'markers_found': markers_found
    }


def determine_athlete_profile(results):
    """Determine overall athlete profile (endurance/power/mixed)"""
    profile = {
        'power_score': 0,
        'endurance_score': 0,
        'max_power': 0,
        'max_endurance': 0
    }

    # ACTN3 - most important marker
    muscle_fiber = results.get('muscle_fiber_type', [])
    for r in muscle_fiber:
        if r['snp_id'] == 'rs1815739' and r['found']:
            profile['max_power'] += 3
            profile['max_endurance'] += 3
            if r['phenotype'] == 'power':
                profile['power_score'] += 3
            elif r['phenotype'] == 'endurance':
                profile['endurance_score'] += 3
            elif r['phenotype'] == 'mixed':
                profile['power_score'] += 1.5
                profile['endurance_score'] += 1.5

    # Endurance markers
    endurance_results = results.get('endurance', [])
    for r in endurance_results:
        if r['found'] and r['phenotype']:
            profile['max_endurance'] += 2
            if r['phenotype'] == 'high':
                profile['endurance_score'] += 2
            elif r['phenotype'] == 'moderate':
                profile['endurance_score'] += 1

    # Strength markers
    strength_results = results.get('strength', [])
    for r in strength_results:
        if r['found'] and r['phenotype']:
            profile['max_power'] += 2
            if r['phenotype'] == 'high':
                profile['power_score'] += 2
            elif r['phenotype'] == 'moderate':
                profile['power_score'] += 1

    # Lactate clearance - benefits both but more for power/interval
    lactate = results.get('lactate_clearance', [])
    for r in lactate:
        if r['found'] and r['phenotype']:
            profile['max_power'] += 1
            profile['max_endurance'] += 1
            if r['phenotype'] == 'high':
                profile['power_score'] += 1
                profile['endurance_score'] += 0.5
            elif r['phenotype'] == 'moderate':
                profile['power_score'] += 0.5
                profile['endurance_score'] += 0.25

    # Calculate percentages
    if profile['max_power'] > 0:
        profile['power_percentage'] = (profile['power_score'] / profile['max_power']) * 100
    else:
        profile['power_percentage'] = 50

    if profile['max_endurance'] > 0:
        profile['endurance_percentage'] = (profile['endurance_score'] / profile['max_endurance']) * 100
    else:
        profile['endurance_percentage'] = 50

    # Determine type
    power_pct = profile['power_percentage']
    endurance_pct = profile['endurance_percentage']

    diff = abs(power_pct - endurance_pct)

    if diff < 15:
        profile['type'] = 'mixed'
        profile['type_name'] = 'Versatile athlete'
        profile['type_description'] = 'Balanced profile. Both strength and cyclic sports are a good fit.'
    elif power_pct > endurance_pct:
        if diff > 30:
            profile['type'] = 'power'
            profile['type_name'] = 'Power/Sprinter'
            profile['type_description'] = 'Pronounced predisposition to strength and speed-strength sports.'
        else:
            profile['type'] = 'power_mixed'
            profile['type_name'] = 'Power-oriented with versatile elements'
            profile['type_description'] = 'Strength qualities predominate, with a good base for other disciplines.'
    else:
        if diff > 30:
            profile['type'] = 'endurance'
            profile['type_name'] = 'Endurance-oriented'
            profile['type_description'] = 'Pronounced predisposition to cyclic endurance sports.'
        else:
            profile['type'] = 'endurance_mixed'
            profile['type_name'] = 'Endurance-oriented with versatile elements'
            profile['type_description'] = 'Endurance predominates, with a good base for strength loads.'

    return profile


def get_training_recommendations(profile, results):
    """Generate personalized training recommendations"""
    recommendations = []

    # Based on athlete type
    if profile['type'] in ['power', 'power_mixed']:
        recommendations.append({
            'category': 'Main focus',
            'items': [
                'Strength training 3-4 times per week',
                'Sprint work and plyometrics',
                'Explosive strength and power',
                'Short intense intervals (10-30 sec)',
            ]
        })
        recommendations.append({
            'category': 'Recommended sports',
            'items': [
                'Weightlifting, powerlifting',
                'Sprinting (100-400m), jumping',
                'Combat sports, wrestling',
                'Team sports (soccer, basketball)',
                'CrossFit',
            ]
        })
    elif profile['type'] in ['endurance', 'endurance_mixed']:
        recommendations.append({
            'category': 'Main focus',
            'items': [
                'Long aerobic workouts',
                'Building base endurance (zone 2)',
                'Tempo workouts at the lactate threshold',
                'Long intervals (3-8 min)',
            ]
        })
        recommendations.append({
            'category': 'Recommended sports',
            'items': [
                'Long-distance running (5km - marathon)',
                'Triathlon, cycling',
                'Long-distance swimming',
                'Cross-country skiing, biathlon',
                'Rowing',
            ]
        })
    else:  # mixed
        recommendations.append({
            'category': 'Main focus',
            'items': [
                'Combination of strength and aerobic training',
                'Periodization: strength blocks alternate with endurance',
                'Medium intervals (1-3 min)',
                'Functional training',
            ]
        })
        recommendations.append({
            'category': 'Recommended sports',
            'items': [
                'CrossFit and functional fitness',
                'Middle distances (800m - 5km)',
                'Team and ball sports',
                'Swimming',
                'Mixed martial arts (MMA)',
            ]
        })

    # Recovery recommendations
    recovery = results.get('recovery', [])
    slow_recovery = False
    for r in recovery:
        if r['found'] and r['phenotype'] in ['slow', 'low']:
            slow_recovery = True
            break

    if slow_recovery:
        recommendations.append({
            'category': 'Recovery (important!)',
            'items': [
                'Increase the time between heavy workouts (48-72h)',
                'Prioritize sleep (8+ hours)',
                'Anti-inflammatory nutrition (omega-3, turmeric)',
                'Regular massage and myofascial release',
                'Contrast showers and sauna',
            ]
        })
    else:
        recommendations.append({
            'category': 'Recovery',
            'items': [
                'Standard recovery time (24-48h)',
                'You can train more often when feeling well',
                'Watch for signs of overtraining',
            ]
        })

    # Injury prevention
    injury = results.get('injury_risk', [])
    high_injury_risk = False
    for r in injury:
        if r['found'] and r['phenotype'] == 'high_risk':
            high_injury_risk = True
            break

    if high_injury_risk:
        recommendations.append({
            'category': 'Injury prevention (priority!)',
            'items': [
                'Mandatory 15-20 minute warm-up',
                'Eccentric exercises for tendons',
                'Collagen support (vitamin C + gelatin/collagen)',
                'Adequate vitamin D (check your level)',
                'Avoid sudden increases in training load',
                'Work on proprioception and balance',
            ]
        })

    # Stress response
    stress = results.get('stress_response', [])
    for r in stress:
        if r['snp_id'] == 'rs4680' and r['found']:
            if r['phenotype'] == 'worrier':
                recommendations.append({
                    'category': 'Psychological preparation',
                    'items': [
                        'Practice relaxation techniques before competitions',
                        'Use success visualization',
                        'Develop routines and rituals to reduce anxiety',
                        'Your advantage is precision and strategic thinking',
                    ]
                })
            elif r['phenotype'] == 'warrior':
                recommendations.append({
                    'category': 'Psychological preparation',
                    'items': [
                        'Your advantage is resilience under pressure',
                        'Use the adrenaline of competition',
                        'You can rely on intuition in stressful situations',
                    ]
                })

    # Motor learning
    motor = results.get('motor_learning', [])
    for r in motor:
        if r['found'] and r['phenotype'] == 'low':
            recommendations.append({
                'category': 'Technique acquisition',
                'items': [
                    'More time for technique practice',
                    'Break complex movements into parts',
                    'Use video for analysis',
                    'Regular practice matters more than intensity',
                ]
            })

    return recommendations


def generate_report(results, genome):
    """Generate comprehensive sports fitness report"""
    report = []

    # Header
    report.append("# Sports Genetics Analysis")
    report.append(f"\nAnalysis date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("\n---\n")

    # Disclaimer
    report.append("## Important Disclaimer\n")
    report.append("- Genetics determines potential but does not guarantee results")
    report.append("- Training, nutrition and recovery matter more than genes")
    report.append("- Anyone can improve their performance")
    report.append("- Use this information for optimization, not limitation\n")

    report.append("---\n")

    # Athlete profile
    profile = determine_athlete_profile(results)
    report.append("## Athlete Profile\n")
    report.append(f"### {profile['type_name']}\n")
    report.append(f"{profile['type_description']}\n")
    report.append(f"- Strength potential: **{profile['power_percentage']:.0f}%**")
    report.append(f"- Endurance potential: **{profile['endurance_percentage']:.0f}%**\n")

    # VO2max potential
    vo2max = calculate_vo2max_potential(results)
    if vo2max:
        report.append("### VO2max potential\n")
        report.append(f"- Level: **{vo2max['level']}** ({vo2max['percentage']:.0f}%)")
        report.append(f"- {vo2max['description']}\n")

    report.append("---\n")

    # Detailed results by category
    report.append("## Detailed Analysis by Category\n")

    for category, cat_info in SPORTS_SNPS.items():
        if not cat_info['snps']:
            continue

        cat_results = results.get(category, [])
        if not cat_results:
            continue

        report.append(f"### {cat_info['name']}\n")
        report.append(f"*{cat_info['description']}*\n")

        report.append("| SNP | Gene | Genotype | Result |")
        report.append("|-----|-----|---------|-----------|")

        for r in cat_results:
            if r['found']:
                interp = r['interpretation'] or 'No data'
                report.append(f"| {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {interp} |")
            else:
                report.append(f"| {r['snp_id']} | {r['gene']} | - | Not found in genome |")

        report.append("")

    report.append("---\n")

    # Training recommendations
    recommendations = get_training_recommendations(profile, results)
    report.append("## Training Recommendations\n")

    for rec in recommendations:
        report.append(f"### {rec['category']}\n")
        for item in rec['items']:
            report.append(f"- {item}")
        report.append("")

    report.append("---\n")

    # Statistics
    report.append("## Analysis Statistics\n")

    total_snps = 0
    found_snps = 0
    for cat, cat_results in results.items():
        total_snps += len(cat_results)
        found_snps += sum(1 for r in cat_results if r['found'])

    report.append(f"- SNPs analyzed: {total_snps}")
    report.append(f"- Found in genome: {found_snps}")
    report.append(f"- Not found: {total_snps - found_snps}\n")

    # Key findings summary
    report.append("## Key Findings\n")

    # ACTN3
    muscle = results.get('muscle_fiber_type', [])
    for r in muscle:
        if r['snp_id'] == 'rs1815739' and r['found']:
            report.append(f"**ACTN3 (rs1815739):** {r['genotype']} - {r['interpretation']}\n")

    # COMT
    stress = results.get('stress_response', [])
    for r in stress:
        if r['snp_id'] == 'rs4680' and r['found']:
            report.append(f"**COMT (rs4680):** {r['genotype']} - {r['interpretation']}\n")

    # Injury risks
    injury = results.get('injury_risk', [])
    injury_issues = [r for r in injury if r['found'] and r['phenotype'] == 'high_risk']
    if injury_issues:
        report.append("**Elevated injury risk:**")
        for r in injury_issues:
            report.append(f"- {r['gene']}: {r['interpretation']}")
        report.append("")

    return '\n'.join(report)


def main():
    print("=" * 60)
    print("SPORTS GENETICS ANALYSIS")
    print("=" * 60)

    print("\n[1/4] Loading genome...")
    genome = load_genome()
    print(f"      Loaded {len(genome)} SNP")

    print("\n[2/4] Analyzing sports markers...")
    results = analyze_sports(genome)

    for category, cat_results in results.items():
        found = sum(1 for r in cat_results if r['found'])
        print(f"      -> {SPORTS_SNPS[category]['name']}: {found}/{len(cat_results)}")

    print("\n[3/4] Determining athlete profile...")
    profile = determine_athlete_profile(results)
    print(f"      Type: {profile['type_name']}")
    print(f"      Strength potential: {profile['power_percentage']:.0f}%")
    print(f"      Endurance potential: {profile['endurance_percentage']:.0f}%")

    print("\n[4/4] Generating report...")
    report = generate_report(results, genome)

    # Ensure directory exists
    output_dir = f"{REPORTS_PATH}/sports_fitness"
    os.makedirs(output_dir, exist_ok=True)

    report_path = f"{output_dir}/report.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"      -> {report_path}")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

    # Print key findings to console
    print("\nKEY FINDINGS:\n")

    # ACTN3
    muscle = results.get('muscle_fiber_type', [])
    for r in muscle:
        if r['snp_id'] == 'rs1815739' and r['found']:
            print(f"  ACTN3: {r['genotype']} - {r['interpretation']}")

    # COMT
    stress = results.get('stress_response', [])
    for r in stress:
        if r['snp_id'] == 'rs4680' and r['found']:
            print(f"  COMT: {r['genotype']} - {r['interpretation']}")

    print(f"\n  Profile: {profile['type_name']}")
    print(f"  {profile['type_description']}")


if __name__ == "__main__":
    main()

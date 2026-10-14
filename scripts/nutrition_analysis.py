#!/usr/bin/env python3
"""
Nutrition & Metabolism Analysis Script
Analyzes nutrition-related genetic markers from 23andMe data
"""

import os
from datetime import datetime
from collections import defaultdict

# Paths
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENOME_FILE = f"{BASE_PATH}/data/my_dna_file.txt"
REPORTS_PATH = f"{BASE_PATH}/reports"

# =============================================================================
# SNP DATABASE - Nutrition markers
# =============================================================================

NUTRITION_SNPS = {
    "lactose": {
        "name": "Lactose",
        "snps": {
            "rs4988235": {
                "gene": "LCT (MCM6)",
                "description": "Lactose tolerance",
                "interpretation": {
                    "TT": ("tolerant", "Tolerates lactose (lactase persistence)"),
                    "CT": ("partial", "Partial tolerance"),
                    "CC": ("intolerant", "Lactose intolerance"),
                    "AA": ("tolerant", "Tolerates lactose"),
                    "AG": ("partial", "Partial tolerance"),
                    "GG": ("intolerant", "Lactose intolerance"),
                }
            },
        }
    },

    "gluten": {
        "name": "Gluten (celiac disease)",
        "snps": {
            "rs2187668": {
                "gene": "HLA-DQ2.5",
                "description": "Celiac disease risk",
                "interpretation": {
                    "TT": ("high_risk", "HLA-DQ2.5 - high genetic risk of celiac disease"),
                    "CT": ("moderate_risk", "HLA-DQ2.5 carrier - moderate risk"),
                    "CC": ("low_risk", "Low genetic risk of celiac disease"),
                }
            },
            "rs7454108": {
                "gene": "HLA-DQ8",
                "description": "Celiac disease risk",
                "interpretation": {
                    "CC": ("moderate_risk", "HLA-DQ8 - moderate risk of celiac disease"),
                    "CT": ("low_risk", "Carrier"),
                    "TT": ("low_risk", "Low risk"),
                }
            },
        }
    },

    "caffeine": {
        "name": "Caffeine",
        "snps": {
            "rs762551": {
                "gene": "CYP1A2",
                "description": "Caffeine metabolism",
                "interpretation": {
                    "AA": ("fast", "Fast metabolizer - caffeine is safe up to 400mg/day"),
                    "AC": ("medium", "Average metabolizer - moderate intake"),
                    "CC": ("slow", "Slow metabolizer - heart risk at >200mg/day"),
                }
            },
            "rs5751876": {
                "gene": "ADORA2A",
                "description": "Caffeine-induced anxiety",
                "interpretation": {
                    "TT": ("low_anxiety", "Less caffeine-induced anxiety"),
                    "CT": ("moderate_anxiety", "Moderate sensitivity"),
                    "CC": ("high_anxiety", "More caffeine-induced anxiety"),
                }
            },
        }
    },

    "alcohol": {
        "name": "Alcohol",
        "snps": {
            "rs671": {
                "gene": "ALDH2",
                "description": "Alcohol metabolism (Asian flush)",
                "interpretation": {
                    "GG": ("normal", "Normal metabolism"),
                    "AG": ("flush", "Asian flush - intolerance, cancer risk with consumption"),
                    "AA": ("severe", "Severe alcohol intolerance"),
                }
            },
            "rs1229984": {
                "gene": "ADH1B",
                "description": "Ethanol metabolism rate",
                "interpretation": {
                    "CC": ("slow", "Slow metabolism - higher risk of alcoholism"),
                    "CT": ("fast", "Fast metabolism - protection against alcoholism"),
                    "TT": ("fast", "Very fast metabolism - protective"),
                }
            },
        }
    },

    "vitamin_d": {
        "name": "Vitamin D",
        "snps": {
            "rs2282679": {
                "gene": "GC (VDBP)",
                "description": "Blood vitamin D level",
                "interpretation": {
                    "CC": ("low", "Reduced vitamin D level - supplement needed"),
                    "AC": ("moderate", "Moderately reduced - monitor levels"),
                    "GT": ("moderate", "Moderately reduced"),
                    "AA": ("normal", "Normal level"),
                    "TT": ("normal", "Normal level"),
                    "GG": ("normal", "Normal level"),
                }
            },
            "rs7041": {
                "gene": "GC",
                "description": "Vitamin D binding protein",
                "interpretation": {
                    "TT": ("low", "Gc1F - reduced vitamin D"),
                    "GT": ("moderate", "Moderately reduced"),
                    "AC": ("moderate", "Moderately reduced"),
                    "GG": ("normal", "Gc1S - normal level"),
                    "AA": ("normal", "Normal level"),
                    "CC": ("normal", "Normal"),
                }
            },
            "rs12785878": {
                "gene": "DHCR7",
                "description": "Sun-driven vitamin D synthesis",
                "interpretation": {
                    "TT": ("low", "Reduced synthesis from sunlight"),
                    "GT": ("moderate", "Moderately reduced synthesis"),
                    "GG": ("normal", "Normal synthesis"),
                }
            },
        }
    },

    "vitamin_b": {
        "name": "B vitamins",
        "snps": {
            "rs1801133": {
                "gene": "MTHFR C677T",
                "description": "Folate (B9) metabolism",
                "interpretation": {
                    "TT": ("impaired", "~30% activity - methylfolate needed"),
                    "CT": ("moderate", "~65% activity - methylfolate preferred"),
                    "AG": ("moderate", "~65% activity"),
                    "CC": ("normal", "Normal activity - folic acid OK"),
                    "AA": ("normal", "Normal activity"),
                }
            },
            "rs1801131": {
                "gene": "MTHFR A1298C",
                "description": "Folate metabolism",
                "interpretation": {
                    "CC": ("impaired", "Reduced activity"),
                    "AC": ("moderate", "Slightly reduced"),
                    "GT": ("normal", "Normal activity"),
                    "AA": ("normal", "Normal activity"),
                    "TT": ("normal", "Normal"),
                }
            },
            "rs602662": {
                "gene": "FUT2",
                "description": "Vitamin B12 absorption",
                "interpretation": {
                    "AA": ("impaired", "Reduced B12 absorption - supplement needed"),
                    "AG": ("moderate", "Moderately reduced"),
                    "GG": ("normal", "Normal absorption"),
                }
            },
        }
    },

    "vitamin_a": {
        "name": "Vitamin A",
        "snps": {
            "rs12934922": {
                "gene": "BCMO1",
                "description": "Beta-carotene to vitamin A conversion",
                "interpretation": {
                    "TT": ("impaired", "Poor conversion - preformed vitamin A (retinol) needed"),
                    "AT": ("moderate", "Moderate conversion"),
                    "AA": ("normal", "Good beta-carotene conversion"),
                }
            },
            "rs7501331": {
                "gene": "BCMO1",
                "description": "Beta-carotene conversion",
                "interpretation": {
                    "TT": ("impaired", "Poor conversion"),
                    "CT": ("moderate", "Moderate"),
                    "CC": ("normal", "Normal conversion"),
                }
            },
        }
    },

    "omega3": {
        "name": "Omega-3 fatty acids",
        "snps": {
            "rs174546": {
                "gene": "FADS1",
                "description": "ALA to EPA/DHA conversion",
                "interpretation": {
                    "TT": ("impaired", "Poor conversion - preformed EPA/DHA needed (fish, supplements)"),
                    "CT": ("moderate", "Moderate conversion"),
                    "CC": ("normal", "Good conversion from plant sources"),
                }
            },
            "rs174547": {
                "gene": "FADS1",
                "description": "Omega-3 metabolism",
                "interpretation": {
                    "TT": ("impaired", "Reduced conversion"),
                    "CT": ("moderate", "Moderate"),
                    "CC": ("normal", "Good conversion"),
                }
            },
        }
    },

    "salt": {
        "name": "Salt and blood pressure",
        "snps": {
            "rs4961": {
                "gene": "ADD1",
                "description": "Salt sensitivity",
                "interpretation": {
                    "TT": ("sensitive", "Salt-sensitive hypertension - limit salt"),
                    "GT": ("moderate", "Moderate sensitivity"),
                    "GG": ("normal", "Normal salt sensitivity"),
                }
            },
            "rs699": {
                "gene": "AGT",
                "description": "Angiotensinogen",
                "interpretation": {
                    "CC": ("sensitive", "Elevated blood pressure from salt"),
                    "CT": ("moderate", "Moderate sensitivity"),
                    "TT": ("normal", "Normal response to salt"),
                }
            },
        }
    },

    "taste": {
        "name": "Taste traits",
        "snps": {
            "rs713598": {
                "gene": "TAS2R38",
                "description": "Bitter taste sensitivity",
                "interpretation": {
                    "GG": ("supertaster", "Supertaster - strongly perceives bitterness (broccoli, coffee)"),
                    "CG": ("medium", "Average bitter taste sensitivity"),
                    "CC": ("non_taster", "Cannot taste PROP/PTC bitterness"),
                }
            },
            "rs72921001": {
                "gene": "OR6A2",
                "description": "Cilantro perception",
                "interpretation": {
                    "AA": ("soap", "Cilantro smells like soap"),
                    "AC": ("mild", "Mild perception of soapy taste"),
                    "CC": ("normal", "Normal cilantro perception"),
                }
            },
        }
    },

    "iron": {
        "name": "Iron",
        "snps": {
            "rs1800562": {
                "gene": "HFE C282Y",
                "description": "Hemochromatosis (iron overload)",
                "interpretation": {
                    "AA": ("high_risk", "Hemochromatosis - avoid iron supplements!"),
                    "AG": ("carrier", "Carrier - monitor ferritin levels"),
                    "GG": ("normal", "Normal iron metabolism"),
                }
            },
            "rs855791": {
                "gene": "TMPRSS6",
                "description": "Iron level",
                "interpretation": {
                    "TT": ("low", "Tendency toward low iron"),
                    "CT": ("moderate", "Moderately reduced"),
                    "AG": ("moderate", "Moderately reduced level"),
                    "CC": ("normal", "Normal level"),
                    "AA": ("normal", "Normal"),
                    "GG": ("normal", "Normal"),
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


def analyze_nutrition(genome):
    """Analyze nutrition markers"""
    results = {}

    for category, cat_info in NUTRITION_SNPS.items():
        cat_results = []
        for snp_id, snp_info in cat_info['snps'].items():
            result = {
                'snp_id': snp_id,
                'gene': snp_info['gene'],
                'description': snp_info['description'],
                'found': False,
                'genotype': None,
                'status': None,
                'interpretation': None
            }

            if snp_id in genome:
                result['found'] = True
                genotype = genome[snp_id]['genotype']
                result['genotype'] = genotype

                interp = snp_info.get('interpretation', {})
                for gt in [genotype, genotype[::-1] if len(genotype) == 2 else genotype]:
                    if gt in interp:
                        result['status'], result['interpretation'] = interp[gt]
                        break

            cat_results.append(result)
        results[category] = cat_results

    return results


def generate_report(results):
    """Generate nutrition report"""
    report = []
    report.append("# 🥗 Nutrition & Metabolism Analysis")
    report.append(f"\nAnalysis date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("\n---\n")

    # Summary of key findings
    report.append("## 📋 Key Findings\n")

    recommendations = []
    warnings = []

    for category, cat_results in results.items():
        for r in cat_results:
            if r['status'] in ['impaired', 'intolerant', 'slow', 'low', 'sensitive', 'high_risk', 'flush', 'severe']:
                warnings.append(f"⚠️ **{r['gene']}**: {r['interpretation']}")
            elif r['status'] in ['tolerant', 'fast', 'normal', 'low_risk']:
                pass  # Normal findings

    if warnings:
        report.append("### Needs Attention\n")
        for w in warnings:
            report.append(f"- {w}")
        report.append("")

    report.append("---\n")

    # Detailed results by category
    for category, cat_results in results.items():
        cat_name = NUTRITION_SNPS[category]['name']
        report.append(f"## {cat_name}\n")
        report.append("| SNP | Gene | Genotype | Status | Interpretation |")
        report.append("|-----|-----|---------|--------|---------------|")

        for r in cat_results:
            if r['found']:
                status_emoji = {
                    'normal': '✅',
                    'tolerant': '✅',
                    'fast': '✅',
                    'low_risk': '✅',
                    'moderate': '🟡',
                    'partial': '🟡',
                    'medium': '🟡',
                    'carrier': '🟡',
                    'impaired': '🔴',
                    'intolerant': '🔴',
                    'slow': '🔴',
                    'low': '🔴',
                    'sensitive': '🔴',
                    'high_risk': '🔴',
                    'flush': '🔴',
                    'severe': '🔴',
                    'supertaster': 'ℹ️',
                    'non_taster': 'ℹ️',
                    'soap': 'ℹ️',
                }.get(r['status'], '•')
                interp = r['interpretation'] or 'No data'
                status = r['status'] or 'n/a'
                report.append(f"| {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {status_emoji} {status} | {interp} |")
            else:
                report.append(f"| {r['snp_id']} | {r['gene']} | - | - | Not found |")
        report.append("")

    # Recommendations section
    report.append("---\n")
    report.append("## 💡 Personalized Recommendations\n")

    # Generate recommendations based on findings
    rec_map = {
        'lactose': {
            'intolerant': "**Lactose**: Avoid dairy products or use lactose-free alternatives",
            'partial': "**Lactose**: Consume dairy in moderation; lactase supplements can help"
        },
        'caffeine': {
            'slow': "**Caffeine**: Limit to 1-2 cups of coffee per day, avoid after lunch",
            'high_anxiety': "**Caffeine**: If coffee makes you anxious, reduce your intake"
        },
        'vitamin_d': {
            'low': "**Vitamin D**: A supplement of 2000-4000 IU/day is recommended, especially in winter",
            'moderate': "**Vitamin D**: Monitor 25(OH)D levels; a supplement may be needed"
        },
        'vitamin_b': {
            'impaired': "**Folate**: Use methylfolate instead of folic acid (400-800 mcg/day)"
        },
        'vitamin_a': {
            'impaired': "**Vitamin A**: Get it from animal sources (liver, eggs) or retinol supplements"
        },
        'omega3': {
            'impaired': "**Omega-3**: Eat fatty fish 2-3 times per week or take EPA/DHA supplements"
        },
        'iron': {
            'high_risk': "**Iron**: AVOID iron supplements! Monitor ferritin regularly",
            'low': "**Iron**: Possible tendency toward anemia - monitor hemoglobin and ferritin"
        },
        'salt': {
            'sensitive': "**Salt**: Limit to 5g/day, avoid processed foods"
        },
        'alcohol': {
            'flush': "**Alcohol**: Complete abstinence recommended - increased risk of esophageal cancer",
            'severe': "**Alcohol**: Complete abstinence from alcohol"
        }
    }

    has_recommendations = False
    for category, cat_results in results.items():
        if category in rec_map:
            for r in cat_results:
                if r['status'] in rec_map[category]:
                    report.append(f"- {rec_map[category][r['status']]}")
                    has_recommendations = True

    if not has_recommendations:
        report.append("- No critical findings; stick to a balanced diet")

    report.append("\n---\n")
    report.append("## ⚠️ Important\n")
    report.append("- Genetics is a predisposition, not a diagnosis")
    report.append("- Consult a doctor before taking supplements")
    report.append("- Blood tests are recommended for vitamin D and iron")

    return '\n'.join(report)


def main():
    print("=" * 60)
    print("NUTRITION & METABOLISM ANALYSIS")
    print("=" * 60)

    print("\n[1/3] Loading genome...")
    genome = load_genome()
    print(f"      Loaded {len(genome)} SNP")

    print("\n[2/3] Analyzing markers...")
    results = analyze_nutrition(genome)

    total = sum(len(r) for r in results.values())
    found = sum(sum(1 for x in r if x['found']) for r in results.values())
    print(f"      Found: {found}/{total} markers")

    print("\n[3/3] Generating report...")
    report = generate_report(results)

    report_path = f"{REPORTS_PATH}/nutrition/report.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"      → {report_path}")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()

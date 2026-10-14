#!/usr/bin/env python3
"""
Skin Analysis Script
Analyzes skin-related genetic markers from 23andMe data
"""

import os
from datetime import datetime
from collections import defaultdict

# Paths
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENOME_FILE = f"{BASE_PATH}/data/my_dna_file.txt"
REPORTS_PATH = f"{BASE_PATH}/reports"

# =============================================================================
# SNP DATABASE - Skin markers
# =============================================================================

SKIN_SNPS = {
    "collagen": {
        "name": "Collagen and skin structure",
        "snps": {
            "rs1800012": {
                "gene": "COL1A1",
                "description": "Type I collagen structure, tendency to wrinkles",
                "interpretation": {
                    "GG": ("normal", "Normal collagen structure"),
                    "GT": ("moderate", "Moderately reduced collagen density"),
                    "TT": ("impaired", "Reduced collagen density, tendency to wrinkles"),
                    "CC": ("normal", "Normal collagen structure"),
                    "CT": ("moderate", "Moderately reduced collagen density"),
                }
            },
        }
    },

    "mmp1": {
        "name": "Collagen degradation (MMP1)",
        "snps": {
            "rs1799750": {
                "gene": "MMP1",
                "description": "Collagenase - collagen breakdown",
                "interpretation": {
                    # 2G/2G variant - insertion/deletion polymorphism
                    # In 23andMe: usually reported as G/G, GG, or deletion status
                    "GG": ("fast_aging", "2G/2G - Rapid collagen breakdown, early wrinkles"),
                    "DG": ("moderate", "1G/2G - Moderate collagen degradation"),
                    "GD": ("moderate", "1G/2G - Moderate collagen degradation"),
                    "DD": ("normal", "1G/1G - Best collagen preservation"),
                    # Alternative representations
                    "II": ("fast_aging", "2G/2G - Rapid collagen breakdown"),
                    "DI": ("moderate", "1G/2G - Moderate degradation"),
                    "ID": ("moderate", "1G/2G - Moderate degradation"),
                    # Some chips report as T/C
                    "TT": ("normal", "1G/1G - Best collagen preservation"),
                    "CT": ("moderate", "1G/2G - Moderate degradation"),
                    "TC": ("moderate", "1G/2G - Moderate degradation"),
                    "CC": ("fast_aging", "2G/2G - Rapid collagen breakdown"),
                }
            },
        }
    },

    "antioxidants": {
        "name": "Antioxidant defense",
        "snps": {
            "rs4880": {
                "gene": "SOD2",
                "description": "Superoxide dismutase - protection from oxidative stress",
                "interpretation": {
                    "CC": ("good", "High antioxidant defense (Ala/Ala)"),
                    "CT": ("moderate", "Moderate protection (Ala/Val)"),
                    "TC": ("moderate", "Moderate protection (Ala/Val)"),
                    "TT": ("low", "Reduced antioxidant defense (Val/Val)"),
                    "AA": ("good", "High antioxidant defense"),
                    "AG": ("moderate", "Moderate protection"),
                    "GA": ("moderate", "Moderate protection"),
                    "GG": ("low", "Reduced antioxidant defense"),
                }
            },
            "rs1695": {
                "gene": "GSTP1",
                "description": "Glutathione S-transferase - detoxification",
                "interpretation": {
                    "AA": ("good", "High detoxification capacity (Ile/Ile)"),
                    "AG": ("moderate", "Moderate detoxification (Ile/Val)"),
                    "GA": ("moderate", "Moderate detoxification (Ile/Val)"),
                    "GG": ("low", "Reduced detoxification (Val/Val)"),
                }
            },
        }
    },

    "uv_sensitivity": {
        "name": "UV radiation sensitivity",
        "snps": {
            "rs1805007": {
                "gene": "MC1R (R151C)",
                "description": "Melanocortin receptor - red hair, freckles",
                "interpretation": {
                    "CC": ("normal", "Normal UV sensitivity"),
                    "CT": ("sensitive", "Carrier - increased sun sensitivity"),
                    "TC": ("sensitive", "Carrier - increased sun sensitivity"),
                    "TT": ("high_risk", "High UV sensitivity, risk of sunburn"),
                }
            },
            "rs1805008": {
                "gene": "MC1R (R160W)",
                "description": "Melanocortin receptor - photosensitivity",
                "interpretation": {
                    "CC": ("normal", "Normal UV sensitivity"),
                    "CT": ("sensitive", "Carrier - increased sensitivity"),
                    "TC": ("sensitive", "Carrier - increased sensitivity"),
                    "TT": ("high_risk", "High sensitivity, burns easily"),
                }
            },
            "rs12913832": {
                "gene": "HERC2/OCA2",
                "description": "Eye color, skin pigmentation",
                "interpretation": {
                    "AA": ("light", "Light eyes, fair skin - higher UV sensitivity"),
                    "AG": ("medium", "Medium pigmentation"),
                    "GA": ("medium", "Medium pigmentation"),
                    "GG": ("dark", "Dark eyes, better UV protection"),
                }
            },
        }
    },

    "photoaging": {
        "name": "Photoaging",
        "snps": {
            "rs1805005": {
                "gene": "MC1R (V60L)",
                "description": "Melanocortin receptor - photoaging",
                "interpretation": {
                    "GG": ("normal", "Normal photoaging risk"),
                    "GT": ("elevated", "Elevated photoaging risk"),
                    "TG": ("elevated", "Elevated photoaging risk"),
                    "TT": ("high", "High photoaging risk"),
                    "AA": ("normal", "Normal photoaging risk"),
                    "AG": ("elevated", "Elevated photoaging risk"),
                    "GA": ("elevated", "Elevated photoaging risk"),
                }
            },
            "rs1805009": {
                "gene": "MC1R (D294H)",
                "description": "Melanocortin receptor - pigment spots",
                "interpretation": {
                    "GG": ("normal", "Normal pigmentation risk"),
                    "GA": ("elevated", "Elevated risk of pigment spots"),
                    "AG": ("elevated", "Elevated risk of pigment spots"),
                    "AA": ("high", "High risk of hyperpigmentation"),
                    "CC": ("normal", "Normal pigmentation risk"),
                    "CA": ("elevated", "Elevated risk of pigment spots"),
                    "AC": ("elevated", "Elevated risk of pigment spots"),
                }
            },
        }
    },

    "acne": {
        "name": "Acne and skin inflammation",
        "snps": {
            "rs4133274": {
                "gene": "DDB2",
                "description": "DNA repair, acne tendency",
                "interpretation": {
                    "TT": ("normal", "Normal acne risk"),
                    "TG": ("elevated", "Moderately elevated acne risk"),
                    "GT": ("elevated", "Moderately elevated acne risk"),
                    "GG": ("high", "Elevated acne risk"),
                    "CC": ("normal", "Normal acne risk"),
                    "CA": ("elevated", "Moderately elevated risk"),
                    "AC": ("elevated", "Moderately elevated risk"),
                    "AA": ("high", "Elevated acne risk"),
                }
            },
            "rs1800629": {
                "gene": "TNF-alpha",
                "description": "Tumor necrosis factor - inflammation",
                "interpretation": {
                    "GG": ("normal", "Normal inflammation level"),
                    "GA": ("elevated", "Elevated tendency to inflammation"),
                    "AG": ("elevated", "Elevated tendency to inflammation"),
                    "AA": ("high", "High tendency to skin inflammation"),
                }
            },
        }
    },

    "psoriasis": {
        "name": "Psoriasis",
        "snps": {
            "rs10484554": {
                "gene": "HLA-C",
                "description": "Major genetic risk factor for psoriasis",
                "interpretation": {
                    "CC": ("normal", "Low genetic risk of psoriasis"),
                    "CT": ("elevated", "Moderate genetic risk of psoriasis"),
                    "TC": ("elevated", "Moderate genetic risk of psoriasis"),
                    "TT": ("high", "High genetic risk of psoriasis"),
                }
            },
        }
    },

    "eczema": {
        "name": "Eczema (atopic dermatitis)",
        "snps": {
            "rs61816761": {
                "gene": "FLG (Filaggrin)",
                "description": "Filaggrin - skin barrier function",
                "interpretation": {
                    "GG": ("normal", "Normal skin barrier"),
                    "GA": ("impaired", "Impaired skin barrier, eczema risk"),
                    "AG": ("impaired", "Impaired skin barrier, eczema risk"),
                    "AA": ("high_risk", "High risk of atopic dermatitis"),
                    "CC": ("normal", "Normal skin barrier"),
                    "CT": ("impaired", "Impaired skin barrier"),
                    "TC": ("impaired", "Impaired skin barrier"),
                    "TT": ("high_risk", "High eczema risk"),
                }
            },
        }
    },

    "wound_healing": {
        "name": "Wound healing",
        "snps": {
            "rs1800629_wound": {
                "gene": "TNF-alpha",
                "snp_id_actual": "rs1800629",
                "description": "Healing speed, scarring",
                "interpretation": {
                    "GG": ("normal", "Normal healing"),
                    "GA": ("slow", "Slowed healing, keloid risk"),
                    "AG": ("slow", "Slowed healing, keloid risk"),
                    "AA": ("impaired", "Tendency to poor healing"),
                }
            },
            "rs1800795": {
                "gene": "IL-6",
                "description": "Interleukin-6 - inflammation and healing",
                "interpretation": {
                    "GG": ("normal", "Normal inflammatory response"),
                    "GC": ("elevated", "Elevated inflammation, slower healing"),
                    "CG": ("elevated", "Elevated inflammation, slower healing"),
                    "CC": ("high", "High inflammation, slowed healing"),
                }
            },
        }
    },

    "cellulite": {
        "name": "Cellulite",
        "snps": {
            "rs1799750_cellulite": {
                "gene": "MMP1",
                "snp_id_actual": "rs1799750",
                "description": "Connective tissue structure",
                "interpretation": {
                    "GG": ("high_risk", "2G/2G - Elevated cellulite risk"),
                    "DG": ("moderate", "1G/2G - Moderate risk"),
                    "GD": ("moderate", "1G/2G - Moderate risk"),
                    "DD": ("normal", "1G/1G - Reduced cellulite risk"),
                    "TT": ("normal", "Reduced cellulite risk"),
                    "CT": ("moderate", "Moderate risk"),
                    "TC": ("moderate", "Moderate risk"),
                    "CC": ("high_risk", "Elevated cellulite risk"),
                }
            },
            "rs1800012_cellulite": {
                "gene": "COL1A1",
                "snp_id_actual": "rs1800012",
                "description": "Collagen density, skin elasticity",
                "interpretation": {
                    "GG": ("normal", "Normal collagen density"),
                    "GT": ("moderate", "Moderately reduced density"),
                    "TT": ("high_risk", "Reduced density, cellulite risk"),
                    "CC": ("normal", "Normal collagen density"),
                    "CT": ("moderate", "Moderately reduced density"),
                }
            },
        }
    },

    "elasticity": {
        "name": "Skin elasticity",
        "snps": {
            "rs7539120": {
                "gene": "ELN (Elastin)",
                "description": "Elastin - skin firmness",
                "interpretation": {
                    "CC": ("good", "Good skin elasticity"),
                    "CT": ("moderate", "Moderate elasticity"),
                    "TC": ("moderate", "Moderate elasticity"),
                    "TT": ("reduced", "Reduced elasticity, early wrinkles"),
                    "GG": ("good", "Good skin elasticity"),
                    "GA": ("moderate", "Moderate elasticity"),
                    "AG": ("moderate", "Moderate elasticity"),
                    "AA": ("reduced", "Reduced elasticity"),
                }
            },
        }
    },

    "hydration": {
        "name": "Skin hydration",
        "snps": {
            "rs12212041": {
                "gene": "AQP3",
                "description": "Aquaporin-3 - skin water balance",
                "interpretation": {
                    "TT": ("good", "Good moisture retention"),
                    "TC": ("moderate", "Moderate hydration"),
                    "CT": ("moderate", "Moderate hydration"),
                    "CC": ("dry", "Tendency to dry skin"),
                    "AA": ("good", "Good moisture retention"),
                    "AG": ("moderate", "Moderate hydration"),
                    "GA": ("moderate", "Moderate hydration"),
                    "GG": ("dry", "Tendency to dry skin"),
                }
            },
        }
    },

    "glycation": {
        "name": "Glycation (sugar damage)",
        "snps": {
            "rs2070600": {
                "gene": "AGER (RAGE)",
                "description": "Receptor for advanced glycation end products",
                "interpretation": {
                    "CC": ("protective", "Protection from glycation aging"),
                    "CT": ("moderate", "Moderate glycation risk"),
                    "TC": ("moderate", "Moderate glycation risk"),
                    "TT": ("elevated", "Elevated risk of glycation aging"),
                    "GG": ("protective", "Glycation protection"),
                    "GA": ("moderate", "Moderate risk"),
                    "AG": ("moderate", "Moderate risk"),
                    "AA": ("elevated", "Elevated risk"),
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


def analyze_skin(genome):
    """Analyze skin markers"""
    results = {}

    for category, cat_info in SKIN_SNPS.items():
        cat_results = []
        for snp_id, snp_info in cat_info['snps'].items():
            # Handle duplicate SNPs with different interpretations
            actual_snp_id = snp_info.get('snp_id_actual', snp_id)

            result = {
                'snp_id': actual_snp_id,
                'gene': snp_info['gene'],
                'description': snp_info['description'],
                'found': False,
                'genotype': None,
                'status': None,
                'interpretation': None
            }

            if actual_snp_id in genome:
                result['found'] = True
                genotype = genome[actual_snp_id]['genotype']
                result['genotype'] = genotype

                interp = snp_info.get('interpretation', {})
                for gt in [genotype, genotype[::-1] if len(genotype) == 2 else genotype]:
                    if gt in interp:
                        result['status'], result['interpretation'] = interp[gt]
                        break

            cat_results.append(result)
        results[category] = cat_results

    return results


def determine_skin_profile(results):
    """Determine overall skin profile based on genetic results"""

    scores = {
        'aging_prone': 0,
        'sensitive': 0,
        'resilient': 0,
        'inflammation_prone': 0,
        'photoaging_risk': 0,
    }

    profile_factors = []

    # Analyze collagen and aging markers
    for category in ['collagen', 'mmp1', 'elasticity']:
        if category in results:
            for r in results[category]:
                if r['status'] in ['impaired', 'fast_aging', 'reduced']:
                    scores['aging_prone'] += 2
                    profile_factors.append(f"Rapid aging ({r['gene']})")
                elif r['status'] in ['moderate']:
                    scores['aging_prone'] += 1
                elif r['status'] in ['normal', 'good']:
                    scores['resilient'] += 1

    # Analyze UV sensitivity and photoaging
    for category in ['uv_sensitivity', 'photoaging']:
        if category in results:
            for r in results[category]:
                if r['status'] in ['high_risk', 'high', 'sensitive', 'light']:
                    scores['sensitive'] += 2
                    scores['photoaging_risk'] += 2
                    profile_factors.append(f"UV sensitivity ({r['gene']})")
                elif r['status'] in ['elevated', 'medium']:
                    scores['sensitive'] += 1
                    scores['photoaging_risk'] += 1
                elif r['status'] in ['normal', 'dark']:
                    scores['resilient'] += 1

    # Analyze inflammation and skin conditions
    for category in ['acne', 'psoriasis', 'eczema', 'wound_healing']:
        if category in results:
            for r in results[category]:
                if r['status'] in ['high', 'high_risk', 'impaired']:
                    scores['inflammation_prone'] += 2
                    profile_factors.append(f"Tendency to inflammation ({r['gene']})")
                elif r['status'] in ['elevated', 'slow']:
                    scores['inflammation_prone'] += 1
                elif r['status'] in ['normal']:
                    scores['resilient'] += 1

    # Analyze antioxidant protection
    if 'antioxidants' in results:
        for r in results['antioxidants']:
            if r['status'] in ['low']:
                scores['aging_prone'] += 1
                scores['sensitive'] += 1
            elif r['status'] in ['good']:
                scores['resilient'] += 2

    # Determine primary profile
    profiles = []

    if scores['aging_prone'] >= 3:
        profiles.append("Prone to early aging")
    if scores['sensitive'] >= 3 or scores['photoaging_risk'] >= 3:
        profiles.append("Sensitive skin")
    if scores['inflammation_prone'] >= 3:
        profiles.append("Prone to inflammation")
    if scores['resilient'] >= 5 and not profiles:
        profiles.append("Resilient skin")

    if not profiles:
        profiles.append("Average resilience")

    return {
        'profiles': profiles,
        'scores': scores,
        'factors': profile_factors
    }


def generate_report(results, profile):
    """Generate skin analysis report"""
    report = []
    report.append("# Skin Genetic Analysis")
    report.append(f"\nAnalysis date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("\n---\n")

    # Skin profile summary
    report.append("## Your genetic skin profile\n")

    profile_emoji = {
        'Prone to early aging': '⏳',
        'Sensitive skin': '🌡️',
        'Prone to inflammation': '🔥',
        'Resilient skin': '💪',
        'Average resilience': '⚖️',
    }

    for p in profile['profiles']:
        emoji = profile_emoji.get(p, '•')
        report.append(f"### {emoji} {p}\n")

    if profile['factors']:
        report.append("**Key genetic factors:**\n")
        for f in profile['factors'][:5]:  # Top 5 factors
            report.append(f"- {f}")
        report.append("")

    report.append("---\n")

    # Summary of key findings
    report.append("## Key findings\n")

    warnings = []
    positive = []

    for category, cat_results in results.items():
        for r in cat_results:
            if r['found'] and r['status']:
                if r['status'] in ['impaired', 'fast_aging', 'high_risk', 'high', 'low', 'reduced', 'dry', 'elevated']:
                    warnings.append(f"⚠️ **{r['gene']}**: {r['interpretation']}")
                elif r['status'] in ['good', 'protective', 'normal', 'dark']:
                    if r['status'] in ['good', 'protective']:
                        positive.append(f"✅ **{r['gene']}**: {r['interpretation']}")

    if warnings:
        report.append("### Needs attention\n")
        for w in warnings:
            report.append(f"- {w}")
        report.append("")

    if positive:
        report.append("### Genetic advantages\n")
        for p in positive:
            report.append(f"- {p}")
        report.append("")

    report.append("---\n")

    # Detailed results by category
    category_order = [
        'collagen', 'mmp1', 'elasticity', 'antioxidants',
        'uv_sensitivity', 'photoaging', 'hydration', 'glycation',
        'acne', 'psoriasis', 'eczema', 'wound_healing', 'cellulite'
    ]

    for category in category_order:
        if category not in results:
            continue
        cat_results = results[category]
        cat_name = SKIN_SNPS[category]['name']
        report.append(f"## {cat_name}\n")
        report.append("| SNP | Gene | Genotype | Status | Interpretation |")
        report.append("|-----|-----|---------|--------|---------------|")

        for r in cat_results:
            if r['found']:
                status_emoji = {
                    'normal': '✅',
                    'good': '✅',
                    'protective': '✅',
                    'dark': '✅',
                    'moderate': '🟡',
                    'medium': '🟡',
                    'slow': '🟡',
                    'elevated': '🟠',
                    'impaired': '🔴',
                    'fast_aging': '🔴',
                    'high_risk': '🔴',
                    'high': '🔴',
                    'low': '🔴',
                    'reduced': '🔴',
                    'dry': '🔴',
                    'sensitive': '🟠',
                    'light': 'ℹ️',
                }.get(r['status'], '•')
                interp = r['interpretation'] or 'No data'
                status = r['status'] or 'n/a'
                report.append(f"| {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {status_emoji} {status} | {interp} |")
            else:
                report.append(f"| {r['snp_id']} | {r['gene']} | - | - | Not found |")
        report.append("")

    # Recommendations section
    report.append("---\n")
    report.append("## Personalized skin care recommendations\n")

    # Generate recommendations based on profile
    recommendations = []

    # Aging-prone skin recommendations
    if profile['scores']['aging_prone'] >= 2:
        recommendations.append("""### Anti-aging care

- **Retinoids**: Start with 0.025-0.05% retinol 2-3 times a week
- **Peptides**: Look for Matrixyl, Argireline to stimulate collagen
- **Vitamin C**: 10-20% L-ascorbic acid in the morning
- **Collagen supplements**: 5-10g hydrolyzed collagen per day
- **Prevention**: Avoid smoking and sugar (glycation)""")

    # UV-sensitive skin recommendations
    if profile['scores']['sensitive'] >= 2 or profile['scores']['photoaging_risk'] >= 2:
        recommendations.append("""### Sun protection

- **SPF 50+**: Daily, even in cloudy weather
- **Physical filters**: Zinc oxide, titanium dioxide (less irritating)
- **Reapplication**: Every 2 hours while in the sun
- **Clothing**: UPF clothing, wide-brimmed hats, sunglasses
- **Timing**: Avoid direct sun from 10:00 to 16:00
- **Antioxidants**: Vitamin C, E, niacinamide to protect against photodamage""")

    # Inflammation-prone skin recommendations
    if profile['scores']['inflammation_prone'] >= 2:
        recommendations.append("""### Soothing care

- **Barrier products**: Ceramides, cholesterol, fatty acids
- **Soothing ingredients**: Niacinamide (B3), centella asiatica, allantoin
- **Avoid**: Harsh surfactants, alcohol, fragrances
- **Omega-3**: 2-3g EPA/DHA daily (anti-inflammatory effect)
- **Probiotics**: For skin microbiome health
- **Diet**: Limit dairy and sugar if prone to acne""")

    # Antioxidant support
    low_antioxidants = False
    if 'antioxidants' in results:
        for r in results['antioxidants']:
            if r['status'] in ['low', 'moderate']:
                low_antioxidants = True
                break

    if low_antioxidants:
        recommendations.append("""### Antioxidant support

- **Vitamin C**: 15-20% serum in the morning
- **Vitamin E**: In combination with vitamin C
- **Niacinamide**: 5-10% for protection and repair
- **Resveratrol**: Antioxidant from grapes
- **Supplements**: Astaxanthin 4-12mg, CoQ10 100-200mg
- **Nutrition**: More berries, dark leafy greens, nuts""")

    # Hydration support
    if 'hydration' in results:
        for r in results['hydration']:
            if r['status'] in ['dry', 'moderate']:
                recommendations.append("""### Hydration

- **Hyaluronic acid**: Various molecular weights
- **Ceramides**: Barrier repair
- **Glycerin, urea**: Humectants
- **Occlusives**: Squalane, jojoba oil at night
- **Humidifier**: Especially in winter
- **Water**: 2-2.5L per day""")
                break

    # Glycation protection
    if 'glycation' in results:
        for r in results['glycation']:
            if r['status'] in ['elevated', 'moderate']:
                recommendations.append("""### Glycation protection

- **Diet**: Limit sugar and fast carbohydrates
- **Carnosine**: Supplement 500-1000mg per day
- **Alpha-lipoic acid**: 100-300mg per day
- **Avoid**: Fried foods with a crust (AGEs)
- **Green tea**: Polyphenols against glycation""")
                break

    if not recommendations:
        recommendations.append("""### Basic care

Your genes show good skin resilience. Stick to basic care:
- Gentle cleansing
- Hydration
- SPF 30+ daily
- Antioxidant serum""")

    for rec in recommendations:
        report.append(rec)
        report.append("")

    report.append("---\n")
    report.append("## Important\n")
    report.append("- Genetics is a predisposition, not a diagnosis")
    report.append("- Lifestyle, diet and care affect skin condition as much as genes do")
    report.append("- See a dermatologist for skin conditions")
    report.append("- Introduce new active ingredients gradually")

    return '\n'.join(report)


def main():
    print("=" * 60)
    print("SKIN GENETIC ANALYSIS")
    print("=" * 60)

    print("\n[1/4] Loading genome...")
    genome = load_genome()
    print(f"      Loaded {len(genome)} SNP")

    print("\n[2/4] Analyzing skin markers...")
    results = analyze_skin(genome)

    total = sum(len(r) for r in results.values())
    found = sum(sum(1 for x in r if x['found']) for r in results.values())
    print(f"      Found: {found}/{total} markers")

    print("\n[3/4] Determining skin profile...")
    profile = determine_skin_profile(results)
    print(f"      Profile: {', '.join(profile['profiles'])}")

    print("\n[4/4] Generating report...")
    report = generate_report(results, profile)

    # Ensure directory exists
    report_dir = f"{REPORTS_PATH}/skin"
    os.makedirs(report_dir, exist_ok=True)

    report_path = f"{report_dir}/report.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"      -> {report_path}")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()

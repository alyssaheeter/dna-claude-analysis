#!/usr/bin/env python3
"""
Physical Traits Analysis Script
Analyzes physical traits markers from 23andMe data
"""

import os
from datetime import datetime
from collections import defaultdict

# Paths
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENOME_FILE = f"{BASE_PATH}/data/my_dna_file.txt"
REPORTS_PATH = f"{BASE_PATH}/reports"

# =============================================================================
# SNP DATABASE - Physical traits markers
# =============================================================================

PHYSICAL_SNPS = {
    "eye_color": {
        "name": "Eye color",
        "snps": {
            "rs12913832": {
                "gene": "HERC2",
                "description": "Main determinant of eye color",
                "interpretation": {
                    "GG": ("blue", "Blue/gray eyes (primary genotype)"),
                    "AG": ("mixed", "Green or light brown eyes"),
                    "AA": ("brown", "Brown eyes"),
                }
            },
            "rs1800407": {
                "gene": "OCA2",
                "description": "Eye color modifier",
                "interpretation": {
                    "GG": ("standard", "Standard variant"),
                    "AG": ("modifier", "May lighten brown color"),
                    "AA": ("green_modifier", "Often associated with green eyes"),
                    "CT": ("modifier", "May modify color"),
                    "TT": ("green_modifier", "Often associated with green eyes"),
                }
            },
            "rs12896399": {
                "gene": "SLC24A4",
                "description": "Eye color modifier",
                "interpretation": {
                    "GG": ("darker", "Tendency toward darker color"),
                    "GT": ("intermediate", "Intermediate effect"),
                    "TT": ("lighter", "Tendency toward lighter color"),
                }
            },
            "rs16891982": {
                "gene": "SLC45A2",
                "description": "Eye and skin pigmentation",
                "interpretation": {
                    "GG": ("dark", "Dark pigmentation (typical for Africans/Asians)"),
                    "CG": ("mixed", "Mixed pigmentation"),
                    "CC": ("light", "Light pigmentation (typical for Europeans)"),
                }
            },
            "rs1393350": {
                "gene": "TYR",
                "description": "Tyrosinase - pigmentation",
                "interpretation": {
                    "GG": ("standard", "Standard variant"),
                    "AG": ("lighter", "Slightly lighter pigmentation"),
                    "AA": ("lighter", "Tendency toward lighter eyes"),
                }
            },
        }
    },

    "hair_color": {
        "name": "Hair color",
        "snps": {
            "rs12913832": {
                "gene": "HERC2",
                "description": "Affects hair color",
                "interpretation": {
                    "GG": ("light", "Tendency toward light hair"),
                    "AG": ("mixed", "Medium hair color"),
                    "AA": ("dark", "Tendency toward dark hair"),
                }
            },
            "rs1805007": {
                "gene": "MC1R R151C",
                "description": "Red hair (variant 1)",
                "interpretation": {
                    "CC": ("normal", "No effect on red hair"),
                    "CT": ("carrier", "Red hair carrier - may have a reddish tint"),
                    "TT": ("red", "High probability of red hair"),
                }
            },
            "rs1805008": {
                "gene": "MC1R R160W",
                "description": "Red hair (variant 2)",
                "interpretation": {
                    "CC": ("normal", "No effect on red hair"),
                    "CT": ("carrier", "Red hair carrier"),
                    "TT": ("red", "High probability of red hair"),
                }
            },
            "rs1805009": {
                "gene": "MC1R D294H",
                "description": "Red hair (variant 3)",
                "interpretation": {
                    "GG": ("normal", "No effect on red hair"),
                    "CG": ("carrier", "Red hair carrier"),
                    "CC": ("red", "High probability of red hair"),
                }
            },
            "rs12821256": {
                "gene": "KITLG",
                "description": "Blondism",
                "interpretation": {
                    "TT": ("dark", "Dark hair"),
                    "CT": ("light_carrier", "May lighten hair color"),
                    "CC": ("blonde", "Tendency toward light/blond hair"),
                }
            },
        }
    },

    "hair_structure": {
        "name": "Hair structure",
        "snps": {
            "rs11803731": {
                "gene": "TCHH",
                "description": "Hair curliness",
                "interpretation": {
                    "AA": ("straight", "Straight hair"),
                    "AT": ("wavy", "Wavy hair"),
                    "TT": ("curly", "Curly hair"),
                }
            },
            "rs3827760": {
                "gene": "EDAR",
                "description": "Hair thickness (Asian variant)",
                "interpretation": {
                    "AA": ("thin", "Thin hair (European variant)"),
                    "AG": ("intermediate", "Medium thickness"),
                    "GG": ("thick", "Thick, coarse hair (Asian variant)"),
                    "CC": ("thin", "Thin hair"),
                    "CT": ("intermediate", "Medium thickness"),
                    "TT": ("thick", "Thick hair"),
                }
            },
        }
    },

    "baldness": {
        "name": "Baldness (male)",
        "snps": {
            "rs2180439": {
                "gene": "HDAC9",
                "description": "Androgenetic alopecia",
                "interpretation": {
                    "CC": ("high_risk", "Increased risk of early baldness"),
                    "CT": ("moderate_risk", "Moderate risk of baldness"),
                    "TT": ("low_risk", "Low risk of early baldness"),
                }
            },
            "rs6625163": {
                "gene": "AR",
                "description": "Androgenetic alopecia (X chromosome)",
                "interpretation": {
                    "AA": ("high_risk", "Increased risk of baldness"),
                    "AC": ("moderate_risk", "Moderate risk"),
                    "CC": ("low_risk", "Low risk of baldness"),
                }
            },
        }
    },

    "skin": {
        "name": "Skin pigmentation",
        "snps": {
            "rs1426654": {
                "gene": "SLC24A5",
                "description": "Main light skin gene in Europeans",
                "interpretation": {
                    "AA": ("light", "Light skin (European variant)"),
                    "AG": ("intermediate", "Intermediate pigmentation"),
                    "GG": ("dark", "Dark skin (African/Asian variant)"),
                }
            },
            "rs16891982": {
                "gene": "SLC45A2",
                "description": "Skin pigmentation",
                "interpretation": {
                    "GG": ("dark", "Dark pigmentation"),
                    "CG": ("intermediate", "Intermediate"),
                    "CC": ("light", "Light skin"),
                }
            },
        }
    },

    "freckles": {
        "name": "Freckles",
        "snps": {
            "rs1805007": {
                "gene": "MC1R",
                "description": "Freckles and sun sensitivity",
                "interpretation": {
                    "CC": ("no_freckles", "Fewer freckles, tans better"),
                    "CT": ("some_freckles", "Prone to freckles, be careful in the sun"),
                    "TT": ("many_freckles", "Many freckles, high sun sensitivity"),
                }
            },
        }
    },

    "earwax": {
        "name": "Earwax type",
        "snps": {
            "rs17822931": {
                "gene": "ABCC11",
                "description": "Earwax type and body odor",
                "interpretation": {
                    "CC": ("dry", "Dry earwax (Asian type), less body odor"),
                    "CT": ("intermediate", "Intermediate type"),
                    "TT": ("wet", "Wet earwax (European type), typical body odor"),
                }
            },
        }
    },

    "light_sneeze": {
        "name": "Photic sneeze reflex (ACHOO)",
        "snps": {
            "rs10427255": {
                "gene": "Near ZEB2",
                "description": "Sneezing from bright light",
                "interpretation": {
                    "CC": ("no_achoo", "No photic sneeze reflex"),
                    "CT": ("mild_achoo", "Mild photic sneeze reflex"),
                    "TT": ("achoo", "Sneezing when looking at bright light"),
                }
            },
        }
    },

    "taste": {
        "name": "Taste perception",
        "snps": {
            "rs713598": {
                "gene": "TAS2R38",
                "description": "Bitter sensitivity (PROP/PTC)",
                "interpretation": {
                    "GG": ("supertaster", "Supertaster - strongly perceives bitterness (broccoli, coffee)"),
                    "CG": ("medium", "Medium bitter sensitivity"),
                    "CC": ("non_taster", "Cannot taste PROP/PTC bitterness"),
                }
            },
            "rs72921001": {
                "gene": "OR6A2",
                "description": "Cilantro (coriander) perception",
                "interpretation": {
                    "AA": ("soap", "Cilantro tastes like soap"),
                    "AC": ("mild_soap", "Mild perception of soapy taste"),
                    "CC": ("normal", "Normal cilantro perception - herbal aroma"),
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


def analyze_traits(genome):
    """Analyze physical traits markers"""
    results = {}

    for category, cat_info in PHYSICAL_SNPS.items():
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
                # Try original, reversed, and sorted genotypes
                for gt in [genotype, genotype[::-1] if len(genotype) == 2 else genotype]:
                    if gt in interp:
                        result['status'], result['interpretation'] = interp[gt]
                        break

            cat_results.append(result)
        results[category] = cat_results

    return results


def predict_eye_color(results):
    """
    IrisPlex-like eye color prediction based on multiple SNPs
    Uses rs12913832 (HERC2) as main predictor with modifications from other SNPs
    """
    eye_results = {r['snp_id']: r for r in results.get('eye_color', [])}

    # Main predictor: rs12913832 (HERC2)
    herc2 = eye_results.get('rs12913832', {})
    herc2_gt = herc2.get('genotype', '')

    # Base prediction from HERC2
    if herc2_gt == 'GG':
        blue_prob = 0.85
        green_prob = 0.10
        brown_prob = 0.05
    elif herc2_gt in ['AG', 'GA']:
        blue_prob = 0.25
        green_prob = 0.35
        brown_prob = 0.40
    elif herc2_gt == 'AA':
        blue_prob = 0.02
        green_prob = 0.15
        brown_prob = 0.83
    else:
        return None

    # Modify with OCA2 rs1800407
    oca2 = eye_results.get('rs1800407', {})
    oca2_gt = oca2.get('genotype', '')
    if oca2_gt in ['AA', 'TT']:
        green_prob += 0.15
        brown_prob -= 0.10
        blue_prob -= 0.05
    elif oca2_gt in ['AG', 'CT']:
        green_prob += 0.05

    # Modify with SLC24A4 rs12896399
    slc24a4 = eye_results.get('rs12896399', {})
    slc24a4_gt = slc24a4.get('genotype', '')
    if slc24a4_gt == 'TT':
        blue_prob += 0.05
        brown_prob -= 0.05
    elif slc24a4_gt == 'GG':
        brown_prob += 0.05
        blue_prob -= 0.05

    # Modify with SLC45A2 rs16891982
    slc45a2 = eye_results.get('rs16891982', {})
    slc45a2_gt = slc45a2.get('genotype', '')
    if slc45a2_gt == 'CC':
        blue_prob += 0.05
        green_prob += 0.02
    elif slc45a2_gt == 'GG':
        brown_prob += 0.15
        blue_prob -= 0.10

    # Normalize probabilities
    total = blue_prob + green_prob + brown_prob
    blue_prob = max(0, min(1, blue_prob / total))
    green_prob = max(0, min(1, green_prob / total))
    brown_prob = max(0, min(1, brown_prob / total))

    # Determine most likely color
    if blue_prob >= green_prob and blue_prob >= brown_prob:
        prediction = "Blue/gray"
    elif green_prob >= blue_prob and green_prob >= brown_prob:
        prediction = "Green"
    else:
        prediction = "Brown"

    return {
        'prediction': prediction,
        'blue_probability': round(blue_prob * 100, 1),
        'green_probability': round(green_prob * 100, 1),
        'brown_probability': round(brown_prob * 100, 1),
    }


def predict_hair_color(results):
    """
    Predict hair color based on MC1R variants and other genes
    Checks for red hair (MC1R) and blonde tendency (KITLG)
    """
    hair_results = {r['snp_id']: r for r in results.get('hair_color', [])}

    # Count MC1R red hair variants
    mc1r_variants = ['rs1805007', 'rs1805008', 'rs1805009']
    red_alleles = 0
    carrier_alleles = 0

    for snp_id in mc1r_variants:
        snp = hair_results.get(snp_id, {})
        status = snp.get('status', '')
        if status == 'red':
            red_alleles += 2
        elif status == 'carrier':
            carrier_alleles += 1

    # Check HERC2 for light/dark
    herc2 = hair_results.get('rs12913832', {})
    herc2_status = herc2.get('status', '')

    # Check KITLG for blonde
    kitlg = hair_results.get('rs12821256', {})
    kitlg_status = kitlg.get('status', '')

    # Determine prediction
    is_red = red_alleles >= 2 or (carrier_alleles >= 2)
    red_carrier = carrier_alleles >= 1

    if is_red:
        prediction = "Red hair"
        confidence = "high" if red_alleles >= 2 else "moderate"
    elif kitlg_status == 'blonde' and herc2_status == 'light':
        prediction = "Light/blond hair"
        confidence = "high"
    elif kitlg_status in ['blonde', 'light_carrier'] or herc2_status == 'light':
        prediction = "Light hair"
        confidence = "moderate"
    elif herc2_status == 'dark':
        prediction = "Dark hair"
        confidence = "high"
    else:
        prediction = "Medium hair color"
        confidence = "low"

    return {
        'prediction': prediction,
        'confidence': confidence,
        'red_carrier': red_carrier,
        'red_alleles': red_alleles + carrier_alleles,
        'mc1r_note': "MC1R carrier - children may have a reddish tint" if red_carrier else None
    }


def generate_report(results):
    """Generate physical traits markdown report"""
    report = []
    report.append("# Physical Traits Analysis")
    report.append(f"\nAnalysis date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("\n---\n")

    # Predictions section
    report.append("## Predictions\n")

    # Eye color prediction
    eye_pred = predict_eye_color(results)
    if eye_pred:
        report.append("### Eye Color (IrisPlex-like analysis)\n")
        report.append(f"**Prediction: {eye_pred['prediction']}**\n")
        report.append("| Color | Probability |")
        report.append("|------|-------------|")
        report.append(f"| Blue/gray | {eye_pred['blue_probability']}% |")
        report.append(f"| Green | {eye_pred['green_probability']}% |")
        report.append(f"| Brown | {eye_pred['brown_probability']}% |")
        report.append("")

    # Hair color prediction
    hair_pred = predict_hair_color(results)
    if hair_pred:
        report.append("### Hair Color\n")
        report.append(f"**Prediction: {hair_pred['prediction']}** (confidence: {hair_pred['confidence']})\n")
        if hair_pred['red_carrier']:
            report.append(f"- MC1R alleles: {hair_pred['red_alleles']}")
            report.append(f"- {hair_pred['mc1r_note']}")
        report.append("")

    report.append("---\n")

    # Key physical traits summary
    report.append("## Key Traits\n")

    trait_highlights = []

    # Hair structure
    for r in results.get('hair_structure', []):
        if r['found'] and r['status']:
            if r['snp_id'] == 'rs11803731':
                trait_highlights.append(f"**Hair**: {r['interpretation']}")
            elif r['snp_id'] == 'rs3827760':
                trait_highlights.append(f"**Hair thickness**: {r['interpretation']}")

    # Baldness risk
    for r in results.get('baldness', []):
        if r['found'] and r['status'] == 'high_risk':
            trait_highlights.append(f"**Baldness**: {r['interpretation']}")

    # Skin
    for r in results.get('skin', []):
        if r['found'] and r['snp_id'] == 'rs1426654':
            trait_highlights.append(f"**Skin**: {r['interpretation']}")

    # Freckles
    for r in results.get('freckles', []):
        if r['found'] and r['status'] in ['some_freckles', 'many_freckles']:
            trait_highlights.append(f"**Freckles**: {r['interpretation']}")

    # Earwax
    for r in results.get('earwax', []):
        if r['found']:
            trait_highlights.append(f"**Earwax**: {r['interpretation']}")

    # Light sneeze
    for r in results.get('light_sneeze', []):
        if r['found'] and r['status'] in ['mild_achoo', 'achoo']:
            trait_highlights.append(f"**ACHOO syndrome**: {r['interpretation']}")

    # Taste
    for r in results.get('taste', []):
        if r['found']:
            if r['snp_id'] == 'rs713598':
                trait_highlights.append(f"**Bitterness**: {r['interpretation']}")
            elif r['snp_id'] == 'rs72921001' and r['status'] in ['soap', 'mild_soap']:
                trait_highlights.append(f"**Cilantro**: {r['interpretation']}")

    if trait_highlights:
        for h in trait_highlights:
            report.append(f"- {h}")
    else:
        report.append("- No notable findings")

    report.append("\n---\n")

    # Detailed results by category
    report.append("## Detailed Results by Category\n")

    for category, cat_results in results.items():
        cat_name = PHYSICAL_SNPS[category]['name']
        report.append(f"### {cat_name}\n")
        report.append("| SNP | Gene | Genotype | Status | Interpretation |")
        report.append("|-----|-----|---------|--------|---------------|")

        for r in cat_results:
            if r['found']:
                status_emoji = {
                    # Eye/hair color
                    'blue': '&#128309;',
                    'green': '&#128994;',
                    'brown': '&#129424;',
                    'light': '&#11036;',
                    'dark': '&#11035;',
                    'mixed': '&#128993;',
                    # Hair
                    'straight': '|',
                    'wavy': '~',
                    'curly': '@',
                    'red': '&#128308;',
                    'blonde': '&#128993;',
                    'carrier': '(c)',
                    # Risk
                    'high_risk': '&#128308;',
                    'moderate_risk': '&#128993;',
                    'low_risk': '&#128994;',
                    # Other
                    'normal': '&#9989;',
                    'standard': '&#9989;',
                    'dry': '&#128167;',
                    'wet': '&#128166;',
                    'achoo': '&#129319;',
                    'supertaster': '&#128293;',
                    'non_taster': '-',
                    'soap': '&#129532;',
                }.get(r['status'], '')

                interp = r['interpretation'] or 'No data'
                status = r['status'] or 'n/a'
                report.append(f"| {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {status_emoji} {status} | {interp} |")
            else:
                report.append(f"| {r['snp_id']} | {r['gene']} | - | - | Not found |")
        report.append("")

    report.append("---\n")

    # Statistics
    report.append("## Analysis Statistics\n")
    total = sum(len(r) for r in results.values())
    found = sum(sum(1 for x in r if x['found']) for r in results.values())
    report.append(f"- Total SNPs analyzed: {total}")
    report.append(f"- Found in genome: {found}")
    report.append(f"- Not found: {total - found}")

    report.append("\n---\n")
    report.append("## Notes\n")
    report.append("- Physical traits are determined by many genes and environmental factors")
    report.append("- Predictions are probabilistic")
    report.append("- Eye and hair color may change with age")
    report.append("- MC1R variants are also associated with increased sun sensitivity")

    return '\n'.join(report)


def main():
    print("=" * 60)
    print("PHYSICAL TRAITS ANALYSIS")
    print("=" * 60)

    print("\n[1/4] Loading genome...")
    genome = load_genome()
    print(f"      Loaded {len(genome)} SNP")

    print("\n[2/4] Analyzing markers...")
    results = analyze_traits(genome)

    total = sum(len(r) for r in results.values())
    found = sum(sum(1 for x in r if x['found']) for r in results.values())
    print(f"      Found: {found}/{total} markers")

    print("\n[3/4] Predictions...")

    # Eye color prediction
    eye_pred = predict_eye_color(results)
    if eye_pred:
        print(f"      Eyes: {eye_pred['prediction']} "
              f"(blue {eye_pred['blue_probability']}%, "
              f"green {eye_pred['green_probability']}%, "
              f"brown {eye_pred['brown_probability']}%)")

    # Hair color prediction
    hair_pred = predict_hair_color(results)
    if hair_pred:
        print(f"      Hair: {hair_pred['prediction']} ({hair_pred['confidence']})")

    print("\n[4/4] Generating report...")
    report = generate_report(results)

    report_path = f"{REPORTS_PATH}/physical_traits/report.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"      -> {report_path}")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

    # Print key findings to console
    print("\nKEY FINDINGS:\n")

    for category, cat_results in results.items():
        cat_name = PHYSICAL_SNPS[category]['name']
        found_items = [r for r in cat_results if r['found'] and r['interpretation']]
        if found_items:
            print(f"{cat_name}:")
            for r in found_items:
                print(f"    {r['gene']} ({r['genotype']}): {r['interpretation']}")
            print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Vision and Hearing SNP Analysis Script
Analyzes vision and hearing-related genetic markers from 23andMe data
"""

import os
from collections import defaultdict
from datetime import datetime

# Paths
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENOME_FILE = f"{BASE_PATH}/data/my_dna_file.txt"
REPORTS_PATH = f"{BASE_PATH}/reports"

# =============================================================================
# SNP DATABASE - Vision and Hearing
# =============================================================================

VISION_SNPS = {
    "myopia": {
        "name": "Myopia (Nearsightedness)",
        "name_ru": "Myopia (nearsightedness)",
        "snps": {
            "rs524952": {
                "gene": "GJD2",
                "description": "Myopia susceptibility",
                "description_ru": "Myopia susceptibility",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Increased myopia risk (homozygous)", "Increased myopia risk (homozygous)"),
                    "AG": ("moderate", "Moderate myopia risk", "Moderate myopia risk"),
                    "AC": ("moderate", "Moderate myopia risk", "Moderate myopia risk"),
                    "GG": ("normal", "Normal myopia risk", "Normal myopia risk"),
                    "CC": ("normal", "Normal myopia risk", "Normal myopia risk"),
                }
            },
            "rs634990": {
                "gene": "RASGRF1",
                "description": "Myopia development",
                "description_ru": "Myopia development",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("high", "Increased myopia risk", "Increased myopia risk"),
                    "CT": ("moderate", "Moderate myopia risk", "Moderate myopia risk"),
                    "TT": ("normal", "Normal myopia risk", "Normal myopia risk"),
                }
            },
            "rs17412774": {
                "gene": "ZNF644",
                "description": "High myopia susceptibility",
                "description_ru": "High myopia susceptibility",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "High risk of severe myopia", "High risk of severe myopia"),
                    "AG": ("moderate", "Moderate risk of high myopia", "Moderate risk of high myopia"),
                    "GG": ("normal", "Normal risk", "Normal risk"),
                }
            },
        }
    },
    "amd": {
        "name": "Age-related Macular Degeneration (AMD)",
        "name_ru": "Age-related macular degeneration (AMD)",
        "snps": {
            "rs1061170": {
                "gene": "CFH (Y402H)",
                "description": "Major AMD risk factor - Complement Factor H",
                "description_ru": "Main AMD risk factor - complement factor H",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("high", "7x increased AMD risk (homozygous risk)", "7x increased AMD risk (homozygous risk)"),
                    "TC": ("moderate", "2.5x increased AMD risk (heterozygous)", "2.5x increased AMD risk (heterozygous)"),
                    "CT": ("moderate", "2.5x increased AMD risk (heterozygous)", "2.5x increased AMD risk (heterozygous)"),
                    "TT": ("normal", "Normal AMD risk", "Normal AMD risk"),
                }
            },
            "rs10490924": {
                "gene": "ARMS2 (A69S)",
                "description": "AMD susceptibility - ARMS2 gene",
                "description_ru": "AMD susceptibility - ARMS2 gene",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("high", "Significantly increased AMD risk", "Significantly increased AMD risk"),
                    "GT": ("moderate", "Moderate AMD risk increase", "Moderate AMD risk increase"),
                    "GG": ("normal", "Normal AMD risk", "Normal AMD risk"),
                }
            },
        }
    },
    "glaucoma": {
        "name": "Glaucoma",
        "name_ru": "Glaucoma",
        "snps": {
            "rs10483727": {
                "gene": "SIX6",
                "description": "Primary open-angle glaucoma risk",
                "description_ru": "Risk of primary open-angle glaucoma",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("high", "Increased glaucoma risk", "Increased glaucoma risk"),
                    "CT": ("moderate", "Moderate glaucoma risk", "Moderate glaucoma risk"),
                    "TC": ("moderate", "Moderate glaucoma risk", "Moderate glaucoma risk"),
                    "TT": ("normal", "Normal glaucoma risk", "Normal glaucoma risk"),
                }
            },
            "rs4656461": {
                "gene": "TMCO1",
                "description": "Intraocular pressure regulation",
                "description_ru": "Regulation of intraocular pressure",
                "risk_allele": "G",
                "interpretation": {
                    "GG": ("high", "Increased glaucoma risk", "Increased glaucoma risk"),
                    "AG": ("moderate", "Moderate glaucoma risk", "Moderate glaucoma risk"),
                    "GA": ("moderate", "Moderate glaucoma risk", "Moderate glaucoma risk"),
                    "AA": ("normal", "Normal glaucoma risk", "Normal glaucoma risk"),
                }
            },
        }
    },
    "cataracts": {
        "name": "Cataracts",
        "name_ru": "Cataract",
        "snps": {
            "rs2165241": {
                "gene": "EPHA2",
                "description": "Age-related cataract susceptibility",
                "description_ru": "Susceptibility to age-related cataract",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("high", "Increased cataract risk", "Increased cataract risk"),
                    "CT": ("moderate", "Moderate cataract risk", "Moderate cataract risk"),
                    "TC": ("moderate", "Moderate cataract risk", "Moderate cataract risk"),
                    "CC": ("normal", "Normal cataract risk", "Normal cataract risk"),
                }
            },
            "rs1048661": {
                "gene": "LOXL1",
                "description": "Exfoliation syndrome and secondary glaucoma",
                "description_ru": "Exfoliation syndrome and secondary glaucoma",
                "risk_allele": "G",
                "interpretation": {
                    "GG": ("high", "Increased risk of exfoliation syndrome", "Increased risk of exfoliation syndrome"),
                    "GT": ("moderate", "Moderate risk", "Moderate risk"),
                    "TG": ("moderate", "Moderate risk", "Moderate risk"),
                    "TT": ("normal", "Lower risk", "Lower risk"),
                }
            },
        }
    },
}

HEARING_SNPS = {
    "age_related_hearing_loss": {
        "name": "Age-Related Hearing Loss (Presbycusis)",
        "name_ru": "Age-related hearing loss (presbycusis)",
        "snps": {
            "rs7598759": {
                "gene": "GRM7",
                "description": "Glutamate receptor - hearing sensitivity",
                "description_ru": "Glutamate receptor - hearing sensitivity",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Increased risk of age-related hearing loss", "Increased risk of age-related hearing loss"),
                    "AG": ("moderate", "Moderate risk", "Moderate risk"),
                    "GA": ("moderate", "Moderate risk", "Moderate risk"),
                    "GG": ("normal", "Normal risk", "Normal risk"),
                }
            },
            "rs11928865": {
                "gene": "GRHL2",
                "description": "Cochlear hair cell function",
                "description_ru": "Cochlear hair cell function",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Increased hearing loss risk", "Increased hearing loss risk"),
                    "AG": ("moderate", "Moderate risk", "Moderate risk"),
                    "GA": ("moderate", "Moderate risk", "Moderate risk"),
                    "GG": ("normal", "Normal risk", "Normal risk"),
                }
            },
        }
    },
    "hereditary_deafness": {
        "name": "Hereditary Deafness",
        "name_ru": "Hereditary deafness",
        "snps": {
            "rs80338939": {
                "gene": "GJB2 (35delG)",
                "description": "Most common cause of hereditary deafness",
                "description_ru": "Most common cause of hereditary deafness",
                "risk_allele": "delG",
                "interpretation": {
                    "--": ("high", "Homozygous 35delG - congenital deafness", "Homozygous 35delG - congenital deafness"),
                    "D": ("high", "Carrier of 35delG mutation - hearing loss risk", "Carrier of 35delG mutation - hearing loss risk"),
                    "DI": ("moderate", "Heterozygous carrier of 35delG", "Heterozygous carrier of 35delG"),
                    "II": ("normal", "Not a carrier of 35delG", "Not a carrier of 35delG"),
                    "GG": ("normal", "Not a carrier of 35delG", "Not a carrier of 35delG"),
                    "CC": ("normal", "Not a carrier of 35delG", "Not a carrier of 35delG"),
                    "CG": ("normal", "Not a carrier of 35delG", "Not a carrier of 35delG"),
                }
            },
        }
    },
    "noise_induced_hearing_loss": {
        "name": "Noise-Induced Hearing Loss (NIHL)",
        "name_ru": "Noise-induced hearing loss",
        "snps": {
            "rs7598759": {
                "gene": "GRM7",
                "description": "Susceptibility to noise damage",
                "description_ru": "Susceptibility to noise damage",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("high", "Increased NIHL susceptibility", "Increased NIHL susceptibility"),
                    "AG": ("moderate", "Moderate NIHL susceptibility", "Moderate NIHL susceptibility"),
                    "GA": ("moderate", "Moderate NIHL susceptibility", "Moderate NIHL susceptibility"),
                    "GG": ("normal", "Normal susceptibility", "Normal susceptibility"),
                }
            },
            "rs4880": {
                "gene": "SOD2 (Ala16Val)",
                "description": "Oxidative stress protection in cochlea",
                "description_ru": "Protection against oxidative stress in the cochlea",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("high", "Reduced antioxidant protection - NIHL risk", "Reduced antioxidant protection - NIHL risk"),
                    "CT": ("moderate", "Moderate antioxidant protection", "Moderate antioxidant protection"),
                    "TC": ("moderate", "Moderate antioxidant protection", "Moderate antioxidant protection"),
                    "AT": ("moderate", "Moderate antioxidant protection", "Moderate antioxidant protection"),
                    "TA": ("moderate", "Moderate antioxidant protection", "Moderate antioxidant protection"),
                    "CC": ("normal", "Good antioxidant protection", "Good antioxidant protection"),
                    "AA": ("normal", "Good antioxidant protection (Ala/Ala)", "Good antioxidant protection (Ala/Ala)"),
                }
            },
        }
    },
    "otosclerosis": {
        "name": "Otosclerosis",
        "name_ru": "Otosclerosis",
        "snps": {
            "rs39399": {
                "gene": "TGFB1",
                "description": "Abnormal bone remodeling in middle ear",
                "description_ru": "Abnormal middle ear bone remodeling",
                "risk_allele": "C",
                "interpretation": {
                    "CC": ("high", "Increased otosclerosis risk", "Increased otosclerosis risk"),
                    "CT": ("moderate", "Moderate otosclerosis risk", "Moderate otosclerosis risk"),
                    "TC": ("moderate", "Moderate otosclerosis risk", "Moderate otosclerosis risk"),
                    "TT": ("normal", "Normal risk", "Normal risk"),
                }
            },
        }
    },
    "menieres_disease": {
        "name": "Meniere's Disease",
        "name_ru": "Meniere's disease",
        "snps": {
            "rs4947296": {
                "gene": "NFKB1",
                "description": "Inflammatory response in inner ear",
                "description_ru": "Inflammatory response in the inner ear",
                "risk_allele": "T",
                "interpretation": {
                    "TT": ("high", "Increased Meniere's disease risk", "Increased Meniere's disease risk"),
                    "CT": ("moderate", "Moderate risk", "Moderate risk"),
                    "TC": ("moderate", "Moderate risk", "Moderate risk"),
                    "CC": ("normal", "Normal risk", "Normal risk"),
                }
            },
        }
    },
}


def load_genome():
    """Load genome data from 23andMe file"""
    genome = {}
    with open(GENOME_FILE, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                rsid = parts[0]
                if len(parts) >= 5:  # AncestryDNA format: separate allele columns
                    if parts[3] + parts[4] == '00':
                        continue  # no-call
                    genotype = parts[3] + parts[4]
                else:
                    genotype = parts[3]
                genome[rsid] = genotype
    return genome


def analyze_vision(genome):
    """Analyze vision-related SNPs"""
    results = {
        "category": "Vision",
        "category_ru": "Vision",
        "subcategories": {},
        "summary": {
            "high_risk": [],
            "moderate_risk": [],
            "normal": [],
            "not_found": []
        }
    }

    for subcat_key, subcat_data in VISION_SNPS.items():
        subcat_results = {
            "name": subcat_data["name"],
            "name_ru": subcat_data["name_ru"],
            "snps": {}
        }

        for rsid, snp_info in subcat_data["snps"].items():
            genotype = genome.get(rsid)

            if genotype and genotype != "--":
                # Normalize genotype (sort alleles for matching)
                sorted_genotype = "".join(sorted(genotype))
                original_genotype = genotype

                # Try to find interpretation
                interpretation = None
                for gt_key, interp in snp_info["interpretation"].items():
                    if gt_key == genotype or gt_key == sorted_genotype:
                        interpretation = interp
                        break

                if interpretation:
                    risk_level, desc_en, desc_ru = interpretation
                    snp_result = {
                        "gene": snp_info["gene"],
                        "genotype": original_genotype,
                        "risk_level": risk_level,
                        "description": snp_info["description"],
                        "description_ru": snp_info["description_ru"],
                        "interpretation": desc_en,
                        "interpretation_ru": desc_ru,
                    }
                    subcat_results["snps"][rsid] = snp_result

                    if risk_level == "high":
                        results["summary"]["high_risk"].append((rsid, snp_info["gene"], desc_en))
                    elif risk_level == "moderate":
                        results["summary"]["moderate_risk"].append((rsid, snp_info["gene"], desc_en))
                    else:
                        results["summary"]["normal"].append((rsid, snp_info["gene"]))
                else:
                    # Genotype found but no interpretation available
                    snp_result = {
                        "gene": snp_info["gene"],
                        "genotype": original_genotype,
                        "risk_level": "unknown",
                        "description": snp_info["description"],
                        "interpretation": f"Genotype {original_genotype} - no interpretation available",
                    }
                    subcat_results["snps"][rsid] = snp_result
            else:
                results["summary"]["not_found"].append((rsid, snp_info["gene"]))

        results["subcategories"][subcat_key] = subcat_results

    return results


def analyze_hearing(genome):
    """Analyze hearing-related SNPs"""
    results = {
        "category": "Hearing",
        "category_ru": "Hearing",
        "subcategories": {},
        "summary": {
            "high_risk": [],
            "moderate_risk": [],
            "normal": [],
            "not_found": []
        }
    }

    for subcat_key, subcat_data in HEARING_SNPS.items():
        subcat_results = {
            "name": subcat_data["name"],
            "name_ru": subcat_data["name_ru"],
            "snps": {}
        }

        for rsid, snp_info in subcat_data["snps"].items():
            genotype = genome.get(rsid)

            if genotype and genotype != "--":
                # Normalize genotype
                sorted_genotype = "".join(sorted(genotype))
                original_genotype = genotype

                # Try to find interpretation
                interpretation = None
                for gt_key, interp in snp_info["interpretation"].items():
                    if gt_key == genotype or gt_key == sorted_genotype:
                        interpretation = interp
                        break

                if interpretation:
                    risk_level, desc_en, desc_ru = interpretation
                    snp_result = {
                        "gene": snp_info["gene"],
                        "genotype": original_genotype,
                        "risk_level": risk_level,
                        "description": snp_info["description"],
                        "description_ru": snp_info["description_ru"],
                        "interpretation": desc_en,
                        "interpretation_ru": desc_ru,
                    }
                    subcat_results["snps"][rsid] = snp_result

                    if risk_level == "high":
                        results["summary"]["high_risk"].append((rsid, snp_info["gene"], desc_en))
                    elif risk_level == "moderate":
                        results["summary"]["moderate_risk"].append((rsid, snp_info["gene"], desc_en))
                    else:
                        results["summary"]["normal"].append((rsid, snp_info["gene"]))
                else:
                    snp_result = {
                        "gene": snp_info["gene"],
                        "genotype": original_genotype,
                        "risk_level": "unknown",
                        "description": snp_info["description"],
                        "interpretation": f"Genotype {original_genotype} - no interpretation available",
                    }
                    subcat_results["snps"][rsid] = snp_result
            else:
                results["summary"]["not_found"].append((rsid, snp_info["gene"]))

        results["subcategories"][subcat_key] = subcat_results

    return results


def calculate_amd_risk(vision_results):
    """Calculate combined AMD risk from CFH and ARMS2 variants"""
    amd_data = vision_results["subcategories"].get("amd", {})
    snps = amd_data.get("snps", {})

    cfh_result = snps.get("rs1061170", {})
    arms2_result = snps.get("rs10490924", {})

    cfh_genotype = cfh_result.get("genotype", "")
    arms2_genotype = arms2_result.get("genotype", "")

    # Calculate risk multiplier
    cfh_risk = 1.0
    if cfh_genotype == "CC":
        cfh_risk = 7.0
    elif cfh_genotype in ["TC", "CT"]:
        cfh_risk = 2.5

    arms2_risk = 1.0
    if arms2_genotype == "TT":
        arms2_risk = 8.0
    elif arms2_genotype in ["GT", "TG"]:
        arms2_risk = 2.5

    combined_risk = cfh_risk * arms2_risk

    risk_assessment = {
        "cfh_genotype": cfh_genotype if cfh_genotype else "Not found",
        "cfh_risk_multiplier": cfh_risk,
        "arms2_genotype": arms2_genotype if arms2_genotype else "Not found",
        "arms2_risk_multiplier": arms2_risk,
        "combined_risk_multiplier": combined_risk,
        "risk_category": "Unknown"
    }

    if combined_risk >= 10:
        risk_assessment["risk_category"] = "Very High"
        risk_assessment["risk_category_ru"] = "Very high"
        risk_assessment["recommendation"] = "Regular ophthalmologic screening strongly recommended"
        risk_assessment["recommendation_ru"] = "Regular ophthalmologist examination is strongly recommended"
    elif combined_risk >= 5:
        risk_assessment["risk_category"] = "High"
        risk_assessment["risk_category_ru"] = "High"
        risk_assessment["recommendation"] = "Regular eye exams recommended, consider AREDS supplements"
        risk_assessment["recommendation_ru"] = "Regular eye exams recommended; consider AREDS supplements"
    elif combined_risk >= 2:
        risk_assessment["risk_category"] = "Moderate"
        risk_assessment["risk_category_ru"] = "Moderate"
        risk_assessment["recommendation"] = "Annual eye exams, healthy lifestyle"
        risk_assessment["recommendation_ru"] = "Annual eye exams, healthy lifestyle"
    else:
        risk_assessment["risk_category"] = "Normal"
        risk_assessment["risk_category_ru"] = "Normal"
        risk_assessment["recommendation"] = "Standard eye care"
        risk_assessment["recommendation_ru"] = "Standard eye care"

    return risk_assessment


def generate_report(vision_results, hearing_results, amd_risk):
    """Generate markdown report"""
    report = []

    # Header
    report.append("# Vision and Hearing Genetic Analysis Report")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("---\n")

    # Executive Summary
    report.append("## Executive Summary\n")

    # Vision summary
    vision_high = len(vision_results["summary"]["high_risk"])
    vision_moderate = len(vision_results["summary"]["moderate_risk"])
    vision_normal = len(vision_results["summary"]["normal"])

    report.append(f"### Vision")
    report.append(f"- **High risk markers:** {vision_high}")
    report.append(f"- **Moderate risk markers:** {vision_moderate}")
    report.append(f"- **Normal markers:** {vision_normal}\n")

    # Hearing summary
    hearing_high = len(hearing_results["summary"]["high_risk"])
    hearing_moderate = len(hearing_results["summary"]["moderate_risk"])
    hearing_normal = len(hearing_results["summary"]["normal"])

    report.append(f"### Hearing")
    report.append(f"- **High risk markers:** {hearing_high}")
    report.append(f"- **Moderate risk markers:** {hearing_moderate}")
    report.append(f"- **Normal markers:** {hearing_normal}\n")

    report.append("---\n")

    # ==========================================================================
    # VISION SECTION
    # ==========================================================================
    report.append("# VISION ANALYSIS\n")

    # AMD Risk Assessment
    report.append("## AMD Risk Assessment\n")
    report.append(f"**CFH rs1061170:** {amd_risk['cfh_genotype']} (Risk: {amd_risk['cfh_risk_multiplier']}x)")
    report.append(f"**ARMS2 rs10490924:** {amd_risk['arms2_genotype']} (Risk: {amd_risk['arms2_risk_multiplier']}x)")
    report.append(f"**Combined Risk Multiplier:** {amd_risk['combined_risk_multiplier']}x")
    report.append(f"**Risk Category:** {amd_risk['risk_category']} / {amd_risk.get('risk_category_ru', '')}")
    report.append(f"**Recommendation:** {amd_risk['recommendation']}")
    report.append(f"*{amd_risk.get('recommendation_ru', '')}*\n")

    # Detailed vision results by subcategory
    for subcat_key, subcat_data in vision_results["subcategories"].items():
        report.append(f"## {subcat_data['name']}")
        report.append(f"### {subcat_data['name_ru']}\n")

        if not subcat_data["snps"]:
            report.append("*No data available*\n")
            continue

        report.append("| SNP | Gene | Genotype | Risk | Interpretation |")
        report.append("|-----|------|----------|------|----------------|")

        for rsid, snp_data in subcat_data["snps"].items():
            risk_emoji = ""
            if snp_data["risk_level"] == "high":
                risk_emoji = "HIGH"
            elif snp_data["risk_level"] == "moderate":
                risk_emoji = "MODERATE"
            elif snp_data["risk_level"] == "normal":
                risk_emoji = "Normal"
            else:
                risk_emoji = "?"

            interpretation = snp_data.get("interpretation", "N/A")
            interpretation_ru = snp_data.get("interpretation_ru", "")

            report.append(f"| {rsid} | {snp_data['gene']} | {snp_data['genotype']} | {risk_emoji} | {interpretation} |")

        report.append("")

    report.append("---\n")

    # ==========================================================================
    # HEARING SECTION
    # ==========================================================================
    report.append("# HEARING ANALYSIS\n")

    # Detailed hearing results by subcategory
    for subcat_key, subcat_data in hearing_results["subcategories"].items():
        report.append(f"## {subcat_data['name']}")
        report.append(f"### {subcat_data['name_ru']}\n")

        if not subcat_data["snps"]:
            report.append("*No data available*\n")
            continue

        report.append("| SNP | Gene | Genotype | Risk | Interpretation |")
        report.append("|-----|------|----------|------|----------------|")

        for rsid, snp_data in subcat_data["snps"].items():
            risk_emoji = ""
            if snp_data["risk_level"] == "high":
                risk_emoji = "HIGH"
            elif snp_data["risk_level"] == "moderate":
                risk_emoji = "MODERATE"
            elif snp_data["risk_level"] == "normal":
                risk_emoji = "Normal"
            else:
                risk_emoji = "?"

            interpretation = snp_data.get("interpretation", "N/A")

            report.append(f"| {rsid} | {snp_data['gene']} | {snp_data['genotype']} | {risk_emoji} | {interpretation} |")

        report.append("")

    report.append("---\n")

    # ==========================================================================
    # RECOMMENDATIONS
    # ==========================================================================
    report.append("# Recommendations\n")

    report.append("## Vision Recommendations\n")

    if vision_high > 0:
        report.append("### High Risk Findings:\n")
        for rsid, gene, desc in vision_results["summary"]["high_risk"]:
            report.append(f"- **{gene} ({rsid}):** {desc}")
        report.append("")

    report.append("### General Vision Care:")
    report.append("- Regular comprehensive eye exams")
    report.append("- Protect eyes from UV radiation")
    report.append("- Maintain healthy diet rich in antioxidants")
    report.append("- Avoid smoking")
    report.append("- Monitor blood pressure and cholesterol\n")

    report.append("## Hearing Recommendations\n")

    if hearing_high > 0:
        report.append("### High Risk Findings:\n")
        for rsid, gene, desc in hearing_results["summary"]["high_risk"]:
            report.append(f"- **{gene} ({rsid}):** {desc}")
        report.append("")

    report.append("### General Hearing Care:")
    report.append("- Use hearing protection in loud environments")
    report.append("- Limit exposure to loud music")
    report.append("- Regular hearing tests after age 50")
    report.append("- Avoid ototoxic medications when possible")
    report.append("- Maintain cardiovascular health\n")

    report.append("---\n")

    # Disclaimer
    report.append("## Disclaimer\n")
    report.append("*This report is for educational and informational purposes only. It should not be used for medical diagnosis or treatment decisions. Consult with healthcare professionals for personalized medical advice.*\n")

    return "\n".join(report)


def main():
    """Main function"""
    print("=" * 60)
    print("Vision and Hearing Genetic Analysis")
    print("=" * 60)

    # Load genome data
    print("\nLoading genome data...")
    genome = load_genome()
    print(f"Loaded {len(genome)} SNPs")

    # Analyze vision
    print("\nAnalyzing vision-related SNPs...")
    vision_results = analyze_vision(genome)

    # Analyze hearing
    print("Analyzing hearing-related SNPs...")
    hearing_results = analyze_hearing(genome)

    # Calculate AMD risk
    print("Calculating AMD risk...")
    amd_risk = calculate_amd_risk(vision_results)

    # Generate report
    print("\nGenerating report...")
    report = generate_report(vision_results, hearing_results, amd_risk)

    # Create output directory if needed
    output_dir = f"{REPORTS_PATH}/vision_hearing"
    os.makedirs(output_dir, exist_ok=True)

    # Save report
    output_file = f"{output_dir}/report.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nReport saved to: {output_file}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print("\n--- VISION ---")
    print(f"High risk: {len(vision_results['summary']['high_risk'])}")
    print(f"Moderate risk: {len(vision_results['summary']['moderate_risk'])}")
    print(f"Normal: {len(vision_results['summary']['normal'])}")
    print(f"Not found: {len(vision_results['summary']['not_found'])}")

    print(f"\nAMD Combined Risk: {amd_risk['combined_risk_multiplier']}x ({amd_risk['risk_category']})")

    print("\n--- HEARING ---")
    print(f"High risk: {len(hearing_results['summary']['high_risk'])}")
    print(f"Moderate risk: {len(hearing_results['summary']['moderate_risk'])}")
    print(f"Normal: {len(hearing_results['summary']['normal'])}")
    print(f"Not found: {len(hearing_results['summary']['not_found'])}")

    if vision_results['summary']['high_risk']:
        print("\n!!! HIGH RISK VISION MARKERS !!!")
        for rsid, gene, desc in vision_results['summary']['high_risk']:
            print(f"  - {gene} ({rsid}): {desc}")

    if hearing_results['summary']['high_risk']:
        print("\n!!! HIGH RISK HEARING MARKERS !!!")
        for rsid, gene, desc in hearing_results['summary']['high_risk']:
            print(f"  - {gene} ({rsid}): {desc}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Longevity and Aging Analysis Script
Analyzes genetic markers associated with lifespan, aging, and anti-aging pathways from 23andMe data
"""

import os
from datetime import datetime
from collections import defaultdict

# Paths
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENOME_FILE = f"{BASE_PATH}/data/my_dna_file.txt"
REPORTS_PATH = f"{BASE_PATH}/reports"

# =============================================================================
# SNP DATABASE - Longevity and Aging Markers
# =============================================================================

LONGEVITY_SNPS = {
    "longevity_genes": {
        "name": "Longevity Genes",
        "name_ru": "Longevity Genes",
        "snps": {
            "rs2802292": {
                "gene": "FOXO3",
                "description": "Forkhead box O3 - Master longevity regulator",
                "description_ru": "Master longevity regulator, controls stress resistance",
                "protective_allele": "T",
                "interpretation": {
                    "TT": ("beneficial", "Longevity variant (+2.7 years)", "Longevity variant (+2.7 years)", 2.7),
                    "GT": ("moderate", "Partial longevity benefit (+1.5 years)", "Partial longevity benefit (+1.5 years)", 1.5),
                    "GG": ("baseline", "Baseline lifespan", "Baseline lifespan", 0),
                }
            },
            "rs5882": {
                "gene": "CETP",
                "description": "Cholesteryl ester transfer protein - HDL metabolism",
                "description_ru": "Cholesteryl ester transfer protein, linked to Ashkenazi longevity",
                "protective_allele": "G",
                "interpretation": {
                    "GG": ("beneficial", "Longevity variant - higher HDL", "Longevity variant - higher HDL", 1.5),
                    "AG": ("moderate", "Partial HDL benefit", "Partial HDL benefit", 0.7),
                    "AA": ("baseline", "Standard HDL metabolism", "Standard HDL metabolism", 0),
                }
            },
            "rs9536314": {
                "gene": "KLOTHO (KL)",
                "description": "Klotho - Anti-aging hormone, longevity factor",
                "description_ru": "Anti-aging hormone, protects against age-related diseases",
                "protective_allele": "T",
                "interpretation": {
                    "TT": ("beneficial", "KL-VS variant - cognitive and longevity benefit", "KL-VS variant - cognitive and longevity benefit", 1.8),
                    "GT": ("beneficial", "Heterozygote - optimal Klotho levels", "Heterozygote - optimal Klotho levels", 2.0),
                    "GG": ("baseline", "Standard Klotho", "Standard Klotho", 0),
                }
            },
        }
    },

    "apoe": {
        "name": "APOE Genotype",
        "name_ru": "APOE Genotype",
        "snps": {
            "rs429358": {
                "gene": "APOE",
                "description": "APOE C112R - determines ε4 status",
                "description_ru": "APOE C112R - determines ε4 status",
                "note": "C=ε4 allele component, T=ε2/ε3 component",
                "interpretation": {
                    "CC": ("risk", "Two ε4 components", "Two ε4 components", -3.0),
                    "CT": ("moderate", "One ε4 component", "One ε4 component", -1.5),
                    "TT": ("baseline", "No ε4 component", "No ε4 component", 0),
                }
            },
            "rs7412": {
                "gene": "APOE",
                "description": "APOE R158C - determines ε2 status",
                "description_ru": "APOE R158C - determines ε2 status",
                "note": "T=ε2 allele (protective), C=ε3/ε4 component",
                "interpretation": {
                    "TT": ("beneficial", "Two ε2 components", "Two ε2 components", 2.5),
                    "CT": ("beneficial", "One ε2 component", "One ε2 component", 1.2),
                    "CC": ("baseline", "No ε2 component", "No ε2 component", 0),
                }
            },
        }
    },

    "telomeres": {
        "name": "Telomere Length",
        "name_ru": "Telomere Length",
        "snps": {
            "rs10936599": {
                "gene": "TERC",
                "description": "Telomerase RNA component - telomere maintenance",
                "description_ru": "Telomerase RNA component - telomere maintenance",
                "protective_allele": "C",
                "interpretation": {
                    "CC": ("beneficial", "Longer telomeres", "Longer telomeres", 1.0),
                    "CT": ("moderate", "Average telomere length", "Average telomere length", 0.5),
                    "TT": ("risk", "Shorter telomeres", "Shorter telomeres", -0.5),
                }
            },
            "rs2736100": {
                "gene": "TERT",
                "description": "Telomerase reverse transcriptase - telomere extension",
                "description_ru": "Telomerase reverse transcriptase - telomere elongation",
                "protective_allele": "C",
                "interpretation": {
                    "CC": ("beneficial", "Enhanced telomerase activity", "Enhanced telomerase activity", 1.0),
                    "AC": ("moderate", "Average telomerase", "Average telomerase", 0.5),
                    "AA": ("baseline", "Standard telomerase", "Standard telomerase", 0),
                }
            },
        }
    },

    "oxidative_stress": {
        "name": "Oxidative Stress Defense",
        "name_ru": "Oxidative Stress Protection",
        "snps": {
            "rs4880": {
                "gene": "SOD2 (MnSOD)",
                "description": "Superoxide dismutase 2 - mitochondrial antioxidant",
                "description_ru": "Superoxide dismutase 2 - mitochondrial antioxidant",
                "protective_allele": "C",
                "interpretation": {
                    "CC": ("beneficial", "Better antioxidant protection (Ala/Ala)", "Better antioxidant protection (Ala/Ala)", 1.0),
                    "CT": ("moderate", "Moderate protection (Ala/Val)", "Moderate protection (Ala/Val)", 0.5),
                    "AC": ("moderate", "Moderate protection (Ala/Val)", "Moderate protection (Ala/Val)", 0.5),
                    "TT": ("risk", "Lower mitochondrial protection (Val/Val)", "Lower mitochondrial protection (Val/Val)", -0.5),
                    "AA": ("risk", "Lower mitochondrial protection (Val/Val)", "Lower mitochondrial protection (Val/Val)", -0.5),
                    "AT": ("moderate", "Moderate protection (Ala/Val)", "Moderate protection (Ala/Val)", 0.5),
                }
            },
            "rs1050450": {
                "gene": "GPX1",
                "description": "Glutathione peroxidase 1 - selenium-dependent antioxidant",
                "description_ru": "Glutathione peroxidase 1 - selenium-dependent antioxidant",
                "protective_allele": "C",
                "interpretation": {
                    "CC": ("beneficial", "Pro/Pro - optimal GPX1 activity", "Pro/Pro - optimal GPX1 activity", 0.8),
                    "CT": ("moderate", "Pro/Leu - moderate activity", "Pro/Leu - moderate activity", 0.4),
                    "TT": ("risk", "Leu/Leu - reduced GPX1 activity", "Leu/Leu - reduced GPX1 activity", -0.4),
                }
            },
            "rs1001179": {
                "gene": "CAT",
                "description": "Catalase - hydrogen peroxide neutralization",
                "description_ru": "Catalase - hydrogen peroxide neutralization",
                "protective_allele": "C",
                "interpretation": {
                    "CC": ("beneficial", "Higher catalase activity", "Higher catalase activity", 0.6),
                    "CT": ("moderate", "Average catalase", "Average catalase", 0.3),
                    "TT": ("baseline", "Standard catalase", "Standard catalase", 0),
                }
            },
        }
    },

    "inflammation": {
        "name": "Inflammaging Markers",
        "name_ru": "Inflammaging Markers",
        "snps": {
            "rs1800795": {
                "gene": "IL-6",
                "description": "Interleukin-6 - pro-inflammatory cytokine",
                "description_ru": "Interleukin-6 - pro-inflammatory cytokine",
                "protective_allele": "C",
                "interpretation": {
                    "CC": ("beneficial", "Lower IL-6 production - reduced inflammaging", "Lower IL-6 production - reduced inflammaging", 1.2),
                    "CG": ("moderate", "Moderate IL-6 levels", "Moderate IL-6 levels", 0.6),
                    "GG": ("risk", "Higher IL-6 - increased inflammaging", "Higher IL-6 - increased inflammaging", -0.8),
                }
            },
            "rs1800629": {
                "gene": "TNF-alpha",
                "description": "Tumor necrosis factor alpha - master inflammatory regulator",
                "description_ru": "Tumor necrosis factor alpha - master inflammation regulator",
                "protective_allele": "G",
                "interpretation": {
                    "GG": ("beneficial", "Standard TNF-alpha production", "Standard TNF-alpha production", 0.5),
                    "GA": ("moderate", "Slightly elevated TNF-alpha", "Slightly elevated TNF-alpha", 0),
                    "AG": ("moderate", "Slightly elevated TNF-alpha", "Slightly elevated TNF-alpha", 0),
                    "AA": ("risk", "High TNF-alpha - chronic inflammation risk", "High TNF-alpha - chronic inflammation risk", -1.0),
                }
            },
            "rs1205": {
                "gene": "CRP",
                "description": "C-reactive protein - inflammatory biomarker",
                "description_ru": "C-reactive protein - inflammation biomarker",
                "protective_allele": "T",
                "interpretation": {
                    "TT": ("beneficial", "Lower baseline CRP", "Lower baseline CRP", 0.8),
                    "CT": ("moderate", "Average CRP levels", "Average CRP levels", 0.4),
                    "CC": ("baseline", "Standard CRP", "Standard CRP", 0),
                }
            },
        }
    },

    "dna_repair": {
        "name": "DNA Repair",
        "name_ru": "DNA Repair",
        "snps": {
            "rs25487": {
                "gene": "XRCC1",
                "description": "X-ray repair cross-complementing 1 - base excision repair",
                "description_ru": "XRCC1 - base excision repair",
                "protective_allele": "G",
                "interpretation": {
                    "GG": ("beneficial", "Arg/Arg - optimal DNA repair", "Arg/Arg - optimal DNA repair", 0.8),
                    "CC": ("beneficial", "Arg/Arg - optimal DNA repair", "Arg/Arg - optimal DNA repair", 0.8),
                    "AG": ("moderate", "Arg/Gln - moderate repair capacity", "Arg/Gln - moderate repair capacity", 0.4),
                    "GA": ("moderate", "Arg/Gln - moderate repair capacity", "Arg/Gln - moderate repair capacity", 0.4),
                    "CT": ("moderate", "Arg/Gln - moderate repair capacity", "Arg/Gln - moderate repair capacity", 0.4),
                    "TC": ("moderate", "Arg/Gln - moderate repair capacity", "Arg/Gln - moderate repair capacity", 0.4),
                    "AA": ("risk", "Gln/Gln - reduced DNA repair", "Gln/Gln - reduced DNA repair", -0.6),
                    "TT": ("risk", "Gln/Gln - reduced DNA repair", "Gln/Gln - reduced DNA repair", -0.6),
                }
            },
            "rs1052133": {
                "gene": "OGG1",
                "description": "8-oxoguanine DNA glycosylase - oxidative DNA damage repair",
                "description_ru": "OGG1 - repair of oxidative DNA damage",
                "protective_allele": "C",
                "interpretation": {
                    "CC": ("beneficial", "Ser/Ser - efficient repair of oxidative damage", "Ser/Ser - efficient repair of oxidative damage", 0.7),
                    "CG": ("moderate", "Ser/Cys - moderate repair", "Ser/Cys - moderate repair", 0.3),
                    "GG": ("risk", "Cys/Cys - reduced oxidative damage repair", "Cys/Cys - reduced oxidative damage repair", -0.5),
                }
            },
        }
    },

    "sirtuin": {
        "name": "Sirtuin Pathway",
        "name_ru": "Sirtuin Pathway",
        "snps": {
            "rs3758391": {
                "gene": "SIRT1",
                "description": "Sirtuin 1 - NAD+-dependent deacetylase, caloric restriction mimic",
                "description_ru": "Sirtuin 1 - NAD+-dependent deacetylase, caloric restriction mimetic",
                "protective_allele": "T",
                "interpretation": {
                    "TT": ("beneficial", "Enhanced SIRT1 activity - better aging response", "Enhanced SIRT1 activity - better aging response", 1.5),
                    "CT": ("moderate", "Moderate SIRT1 activity", "Moderate SIRT1 activity", 0.7),
                    "CC": ("baseline", "Standard SIRT1", "Standard SIRT1", 0),
                }
            },
        }
    },

    "igf1_pathway": {
        "name": "IGF-1/Insulin Pathway",
        "name_ru": "IGF-1/Insulin Pathway",
        "snps": {
            "rs2229765": {
                "gene": "IGF1R",
                "description": "Insulin-like growth factor 1 receptor - growth/longevity trade-off",
                "description_ru": "Insulin-like growth factor 1 receptor - growth/longevity trade-off",
                "protective_allele": "A",
                "interpretation": {
                    "AA": ("beneficial", "Reduced IGF-1R signaling - longevity pattern", "Reduced IGF-1R signaling - longevity pattern", 1.3),
                    "AG": ("moderate", "Moderate IGF-1R signaling", "Moderate IGF-1R signaling", 0.6),
                    "GA": ("moderate", "Moderate IGF-1R signaling", "Moderate IGF-1R signaling", 0.6),
                    "GG": ("baseline", "Standard IGF-1R signaling", "Standard IGF-1R signaling", 0),
                }
            },
        }
    },
}

# APOE Genotype determination table
# rs429358: T=ancestral, C=derived (ε4)
# rs7412: C=ancestral, T=derived (ε2)
APOE_GENOTYPES = {
    ("TT", "CC"): ("ε3/ε3", "Most common genotype - baseline risk", "Most common genotype - baseline risk"),
    ("TT", "CT"): ("ε2/ε3", "Protective - lower cardiovascular and Alzheimer's risk", "Protective - lower cardiovascular and Alzheimer's risk"),
    ("TT", "TT"): ("ε2/ε2", "Highly protective - lowest Alzheimer's risk, but increased triglycerides", "Highly protective - lowest Alzheimer's risk, but increased triglycerides"),
    ("CT", "CC"): ("ε3/ε4", "One ε4 allele - moderately increased Alzheimer's risk", "One ε4 allele - moderately increased Alzheimer's risk"),
    ("CT", "CT"): ("ε2/ε4", "Mixed - ε2 partially compensates for ε4", "Mixed - ε2 partially compensates for ε4"),
    ("CC", "CC"): ("ε4/ε4", "Two ε4 alleles - significantly increased Alzheimer's risk", "Two ε4 alleles - significantly increased Alzheimer's risk"),
}

# Anti-aging recommendations based on genotype patterns
RECOMMENDATIONS = {
    "oxidative_stress": {
        "risk": [
            "Increase antioxidant intake: Vitamin C (500-1000mg), Vitamin E (400 IU), CoQ10 (100-200mg)",
            "Consider NAC (N-Acetyl Cysteine) 600-1200mg/day for glutathione support",
            "Eat colorful vegetables rich in polyphenols",
            "Avoid excessive iron supplementation",
            "Consider astaxanthin supplementation (4-12mg/day)",
        ],
        "risk_ru": [
            "Increase antioxidant intake: Vitamin C (500-1000mg), Vitamin E (400 IU), CoQ10 (100-200mg)",
            "Consider NAC (N-Acetyl Cysteine) 600-1200mg/day for glutathione support",
            "Eat colorful vegetables rich in polyphenols",
            "Avoid excessive iron supplementation",
            "Consider astaxanthin supplementation (4-12mg/day)",
        ],
    },
    "inflammation": {
        "risk": [
            "Follow anti-inflammatory diet (Mediterranean, low glycemic)",
            "Consider omega-3 fatty acids (EPA/DHA 2-4g/day)",
            "Curcumin with piperine (500-1000mg/day)",
            "Reduce refined carbohydrates and processed foods",
            "Regular moderate exercise (avoid overtraining)",
            "Optimize sleep (7-9 hours)",
        ],
        "risk_ru": [
            "Follow anti-inflammatory diet (Mediterranean, low glycemic)",
            "Consider omega-3 fatty acids (EPA/DHA 2-4g/day)",
            "Curcumin with piperine (500-1000mg/day)",
            "Reduce refined carbohydrates and processed foods",
            "Regular moderate exercise (avoid overtraining)",
            "Optimize sleep (7-9 hours)",
        ],
    },
    "telomeres": {
        "risk": [
            "Prioritize stress management (meditation, yoga)",
            "Ensure adequate sleep for telomere maintenance",
            "Consider TA-65 or astragalus root extract",
            "Regular moderate exercise",
            "Avoid excessive endurance training",
            "Optimize vitamin D levels (40-60 ng/mL)",
        ],
        "risk_ru": [
            "Prioritize stress management (meditation, yoga)",
            "Ensure adequate sleep for telomere maintenance",
            "Consider TA-65 or astragalus root extract",
            "Regular moderate exercise",
            "Avoid excessive endurance training",
            "Optimize vitamin D levels (40-60 ng/mL)",
        ],
    },
    "dna_repair": {
        "risk": [
            "Ensure adequate B vitamins (especially B12, folate)",
            "Consider NMN or NR for NAD+ support (250-500mg/day)",
            "Minimize UV and radiation exposure",
            "Avoid DNA-damaging substances (tobacco, excessive alcohol)",
            "Consider sulforaphane from broccoli sprouts",
        ],
        "risk_ru": [
            "Ensure adequate B vitamins (especially B12, folate)",
            "Consider NMN or NR for NAD+ support (250-500mg/day)",
            "Minimize UV and radiation exposure",
            "Avoid DNA-damaging substances (tobacco, excessive alcohol)",
            "Consider sulforaphane from broccoli sprouts",
        ],
    },
    "sirtuin": {
        "baseline": [
            "Practice intermittent fasting or time-restricted eating",
            "Consider resveratrol (250-500mg/day) or pterostilbene",
            "NMN or NR supplementation for NAD+ boost",
            "Regular exercise activates sirtuins",
            "Cold exposure (cold showers, cryotherapy)",
        ],
        "baseline_ru": [
            "Practice intermittent fasting or time-restricted eating",
            "Consider resveratrol (250-500mg/day) or pterostilbene",
            "NMN or NR supplementation for NAD+ boost",
            "Regular exercise activates sirtuins",
            "Cold exposure (cold showers, cryotherapy)",
        ],
    },
    "apoe_e4": {
        "risk": [
            "CRITICAL: Prioritize cardiovascular and brain health",
            "Follow strict Mediterranean or MIND diet",
            "Regular aerobic exercise (150+ min/week)",
            "Optimize sleep and treat sleep apnea",
            "Monitor and control blood pressure, glucose, cholesterol",
            "Consider DHA supplementation (1-2g/day)",
            "Avoid head injuries",
            "Engage in cognitive activities and social connections",
            "Regular cardiovascular screening",
        ],
        "risk_ru": [
            "CRITICAL: Prioritize cardiovascular and brain health",
            "Follow strict Mediterranean or MIND diet",
            "Regular aerobic exercise (150+ min/week)",
            "Optimize sleep and treat sleep apnea",
            "Monitor and control blood pressure, glucose, cholesterol",
            "Consider DHA supplementation (1-2g/day)",
            "Avoid head injuries",
            "Engage in cognitive activities and social connections",
            "Regular cardiovascular screening",
        ],
    },
    "general_longevity": [
        "Caloric restriction or intermittent fasting",
        "Regular exercise combining cardio and resistance training",
        "Optimize sleep quality and circadian rhythm",
        "Stress management and social connections",
        "Regular health screenings",
        "Consider metformin or rapamycin (consult physician)",
        "Maintain healthy body weight",
        "Avoid smoking and limit alcohol",
    ],
    "general_longevity_ru": [
        "Caloric restriction or intermittent fasting",
        "Regular exercise combining cardio and resistance training",
        "Optimize sleep quality and circadian rhythm",
        "Stress management and social connections",
        "Regular health screenings",
        "Consider metformin or rapamycin (consult physician)",
        "Maintain healthy body weight",
        "Avoid smoking and limit alcohol",
    ],
}


def load_genome():
    """Load and parse 23andMe genome file"""
    genome = {}
    with open(GENOME_FILE, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                rsid = parts[0]
                genotype = parts[3] + parts[4] if len(parts) >= 5 else parts[3]
                if genotype == '00':
                    continue  # Ancestry no-call: skip so it is not mistaken for a deletion
                genome[rsid] = genotype
    return genome


def determine_apoe_genotype(genome):
    """
    Determine APOE genotype (ε2/ε2, ε2/ε3, ε3/ε3, ε2/ε4, ε3/ε4, ε4/ε4)
    Based on rs429358 and rs7412
    """
    rs429358 = genome.get("rs429358", "")
    rs7412 = genome.get("rs7412", "")

    # Normalize genotypes (sort alleles)
    def normalize(gt):
        if len(gt) == 2:
            return "".join(sorted(gt))
        return gt

    rs429358 = normalize(rs429358)
    rs7412 = normalize(rs7412)

    # Look up in table
    key = (rs429358, rs7412)

    if key in APOE_GENOTYPES:
        return {
            "genotype": APOE_GENOTYPES[key][0],
            "interpretation": APOE_GENOTYPES[key][1],
            "interpretation_ru": APOE_GENOTYPES[key][2],
            "rs429358": rs429358,
            "rs7412": rs7412,
        }
    else:
        # Manual determination based on individual SNPs
        # rs429358: C=ε4, T=not ε4
        # rs7412: T=ε2, C=not ε2
        if len(rs429358) != 2 or len(rs7412) != 2:
            e4_count = e2_count = None
        else:
            e4_count = rs429358.count('C')
            e2_count = rs7412.count('T')

        if e4_count is None:
            genotype = "Unknown"
        elif e4_count == 0 and e2_count == 0:
            genotype = "ε3/ε3"
        elif e4_count == 0 and e2_count == 1:
            genotype = "ε2/ε3"
        elif e4_count == 0 and e2_count == 2:
            genotype = "ε2/ε2"
        elif e4_count == 1 and e2_count == 0:
            genotype = "ε3/ε4"
        elif e4_count == 1 and e2_count == 1:
            genotype = "ε2/ε4"
        elif e4_count == 2:
            genotype = "ε4/ε4"
        else:
            genotype = "Unknown"

        return {
            "genotype": genotype,
            "interpretation": f"Determined from rs429358={rs429358}, rs7412={rs7412}",
            "interpretation_ru": f"Determined from rs429358={rs429358}, rs7412={rs7412}",
            "rs429358": rs429358,
            "rs7412": rs7412,
        }


def analyze_longevity(genome):
    """Analyze all longevity-related SNPs"""
    results = {}

    for category, category_data in LONGEVITY_SNPS.items():
        category_results = {
            "name": category_data["name"],
            "name_ru": category_data["name_ru"],
            "snps": {},
            "summary": {
                "beneficial": 0,
                "moderate": 0,
                "baseline": 0,
                "risk": 0,
            }
        }

        for rsid, snp_data in category_data["snps"].items():
            genotype = genome.get(rsid, "")

            if not genotype or genotype == "--":
                interpretation = {
                    "status": "not_tested",
                    "description": "Not tested in this chip",
                    "description_ru": "Not tested in this chip",
                    "score": 0,
                }
            else:
                # Normalize genotype
                normalized = "".join(sorted(genotype)) if len(genotype) == 2 else genotype

                # Try both original and normalized
                if genotype in snp_data["interpretation"]:
                    interp = snp_data["interpretation"][genotype]
                elif normalized in snp_data["interpretation"]:
                    interp = snp_data["interpretation"][normalized]
                else:
                    interp = ("unknown", f"Genotype {genotype} not in database", f"Genotype {genotype} not in database", 0)

                interpretation = {
                    "status": interp[0],
                    "description": interp[1],
                    "description_ru": interp[2],
                    "score": interp[3] if len(interp) > 3 else 0,
                }

                if interp[0] in category_results["summary"]:
                    category_results["summary"][interp[0]] += 1

            category_results["snps"][rsid] = {
                "gene": snp_data["gene"],
                "description": snp_data["description"],
                "description_ru": snp_data["description_ru"],
                "genotype": genotype,
                "interpretation": interpretation,
            }

        results[category] = category_results

    # Add APOE genotype determination
    results["apoe_determination"] = determine_apoe_genotype(genome)

    return results


def calculate_longevity_score(results):
    """Calculate aggregate longevity score based on all analyzed SNPs"""
    total_score = 0
    scores_by_category = {}

    for category, data in results.items():
        if category == "apoe_determination":
            # Add APOE-specific scoring
            apoe = data["genotype"]
            if "ε2/ε2" in apoe:
                apoe_score = 2.5
            elif "ε2/ε3" in apoe:
                apoe_score = 1.5
            elif "ε3/ε3" in apoe:
                apoe_score = 0
            elif "ε2/ε4" in apoe:
                apoe_score = -0.5
            elif "ε3/ε4" in apoe:
                apoe_score = -2.0
            elif "ε4/ε4" in apoe:
                apoe_score = -4.0
            else:
                apoe_score = 0
            scores_by_category["apoe"] = apoe_score
            total_score += apoe_score
            continue

        if "snps" not in data:
            continue

        category_score = 0
        snp_count = 0

        for rsid, snp_data in data["snps"].items():
            if snp_data["interpretation"]["status"] != "not_tested":
                category_score += snp_data["interpretation"]["score"]
                snp_count += 1

        scores_by_category[category] = category_score
        total_score += category_score

    # Calculate percentile (rough estimate based on normal distribution)
    # Assuming average score is 0, std dev ~5
    import math

    def normal_cdf(x, mean=0, std=5):
        return 0.5 * (1 + math.erf((x - mean) / (std * math.sqrt(2))))

    percentile = normal_cdf(total_score) * 100

    return {
        "total_score": total_score,
        "category_scores": scores_by_category,
        "percentile": percentile,
        "interpretation": get_score_interpretation(total_score, percentile),
    }


def get_score_interpretation(score, percentile):
    """Get interpretation of longevity score"""
    if score >= 8:
        return {
            "level": "exceptional",
            "description": "Exceptional longevity genetics - top tier",
            "description_ru": "Exceptional longevity genetics - top tier",
        }
    elif score >= 4:
        return {
            "level": "favorable",
            "description": "Favorable longevity profile",
            "description_ru": "Favorable longevity profile",
        }
    elif score >= 0:
        return {
            "level": "average",
            "description": "Average longevity genetics",
            "description_ru": "Average longevity genetics",
        }
    elif score >= -4:
        return {
            "level": "below_average",
            "description": "Below average - lifestyle interventions important",
            "description_ru": "Below average - lifestyle interventions important",
        }
    else:
        return {
            "level": "challenging",
            "description": "Challenging profile - proactive health management essential",
            "description_ru": "Challenging profile - proactive health management essential",
        }


def get_recommendations(results, score_data):
    """Generate personalized anti-aging recommendations"""
    recommendations = []

    # Check each category for risk factors
    for category, data in results.items():
        if category == "apoe_determination":
            # APOE-specific recommendations
            if "ε4" in data["genotype"]:
                recommendations.append({
                    "category": "APOE ε4 Carrier",
                    "category_ru": "APOE ε4 Carrier",
                    "priority": "high",
                    "items": RECOMMENDATIONS["apoe_e4"]["risk"],
                    "items_ru": RECOMMENDATIONS["apoe_e4"]["risk_ru"],
                })
            continue

        if "snps" not in data:
            continue

        # Count risks in category
        risk_count = data["summary"].get("risk", 0)

        if risk_count > 0 and category in RECOMMENDATIONS:
            cat_recs = RECOMMENDATIONS[category]
            if "risk" in cat_recs:
                recommendations.append({
                    "category": data["name"],
                    "category_ru": data["name_ru"],
                    "priority": "high" if risk_count > 1 else "moderate",
                    "items": cat_recs["risk"],
                    "items_ru": cat_recs["risk_ru"],
                })
        elif category in RECOMMENDATIONS and "baseline" in RECOMMENDATIONS[category]:
            # Add baseline recommendations for categories without risk
            recommendations.append({
                "category": data["name"],
                "category_ru": data["name_ru"],
                "priority": "low",
                "items": RECOMMENDATIONS[category]["baseline"],
                "items_ru": RECOMMENDATIONS[category]["baseline_ru"],
            })

    # Always add general longevity recommendations
    recommendations.append({
        "category": "General Longevity",
        "category_ru": "General Longevity",
        "priority": "moderate",
        "items": RECOMMENDATIONS["general_longevity"],
        "items_ru": RECOMMENDATIONS["general_longevity_ru"],
    })

    # Sort by priority
    priority_order = {"high": 0, "moderate": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

    return recommendations


def generate_report(results, score_data, recommendations):
    """Generate markdown report"""
    report = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report.append("# Longevity & Aging Genetics Report")
    report.append("")
    report.append(f"**Generated:** {timestamp}\n")
    report.append("---\n")

    # Executive Summary
    report.append("## Executive Summary\n")
    report.append(f"**Longevity Score:** {score_data['total_score']:.1f}")
    report.append(f"**Percentile:** {score_data['percentile']:.0f}%")
    report.append(f"**Assessment:** {score_data['interpretation']['description']}")
    report.append("")

    # Score breakdown
    report.append("### Score by Category\n")
    report.append("| Category | Score |")
    report.append("|----------|-------|")
    for cat, cat_score in score_data["category_scores"].items():
        cat_name = cat.replace("_", " ").title()
        score_str = f"+{cat_score:.1f}" if cat_score > 0 else f"{cat_score:.1f}"
        report.append(f"| {cat_name} | {score_str} |")
    report.append("")

    # APOE Genotype
    report.append("## APOE Genotype\n")
    apoe = results["apoe_determination"]
    report.append(f"**Genotype:** {apoe['genotype']}")
    report.append(f"**Status:** {apoe['interpretation']}")
    report.append(f"- rs429358: {apoe['rs429358']}")
    report.append(f"- rs7412: {apoe['rs7412']}\n")

    if "ε4" in apoe["genotype"]:
        report.append("⚠️ **WARNING:** APOE ε4 carrier detected. See recommendations section.\n")
    elif "ε2" in apoe["genotype"]:
        report.append("✅ **FAVORABLE:** APOE ε2 allele detected - protective against Alzheimer's.\n")

    # Detailed Results by Category
    report.append("---\n")
    report.append("## Detailed Analysis\n")

    for category, data in results.items():
        if category == "apoe_determination":
            continue
        if "snps" not in data:
            continue

        report.append(f"### {data['name']}\n")

        # Summary counts
        summary = data["summary"]
        status_icons = {"beneficial": "✅", "moderate": "➖", "baseline": "⚪", "risk": "⚠️"}
        summary_parts = []
        for status, count in summary.items():
            if count > 0:
                icon = status_icons.get(status, "")
                summary_parts.append(f"{icon} {status.title()}: {count}")
        if summary_parts:
            report.append(f"**Summary:** {' | '.join(summary_parts)}\n")

        # SNP table
        report.append("| SNP | Gene | Genotype | Status | Interpretation |")
        report.append("|-----|------|----------|--------|----------------|")

        for rsid, snp_data in data["snps"].items():
            gene = snp_data["gene"]
            genotype = snp_data["genotype"] or "N/A"
            status = snp_data["interpretation"]["status"]
            desc = snp_data["interpretation"]["description"]

            status_icon = status_icons.get(status, "")
            report.append(f"| {rsid} | {gene} | {genotype} | {status_icon} {status} | {desc} |")

        report.append("")

    # Recommendations
    report.append("---\n")
    report.append("## Anti-Aging Recommendations\n")

    priority_labels = {
        "high": "🔴 HIGH PRIORITY",
        "moderate": "🟡 MODERATE",
        "low": "🟢 GENERAL",
    }

    for rec in recommendations:
        priority = priority_labels.get(rec["priority"], rec["priority"])
        report.append(f"### {rec['category']}")
        report.append(f"**Priority:** {priority}\n")

        for item in rec["items"]:
            report.append(f"- {item}")
        report.append("")

    # Disclaimer
    report.append("---\n")
    report.append("## Disclaimer\n")
    report.append("""
This report is for educational and informational purposes only. It is NOT medical advice.
Genetic factors are only part of the longevity equation. Lifestyle, environment, and other
factors play significant roles. Consult healthcare professionals before making health decisions.
""")

    return "\n".join(report)


def main():
    """Main execution function"""
    print("=" * 60)
    print("LONGEVITY & AGING GENETICS ANALYSIS")
    print("=" * 60)
    print()

    # Load genome
    print("Loading genome data...")
    genome = load_genome()
    print(f"Loaded {len(genome):,} SNPs from genome file.\n")

    # Analyze longevity SNPs
    print("Analyzing longevity markers...")
    results = analyze_longevity(genome)

    # Calculate longevity score
    print("Calculating longevity score...")
    score_data = calculate_longevity_score(results)

    # Get recommendations
    print("Generating personalized recommendations...")
    recommendations = get_recommendations(results, score_data)

    # Generate report
    print("Generating report...")
    report = generate_report(results, score_data, recommendations)

    # Save report
    report_dir = f"{REPORTS_PATH}/longevity"
    os.makedirs(report_dir, exist_ok=True)
    report_file = f"{report_dir}/report.md"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nReport saved to: {report_file}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"\nLongevity Score: {score_data['total_score']:.1f}")
    print(f"Percentile: {score_data['percentile']:.0f}%")
    print(f"Assessment: {score_data['interpretation']['description']}")

    print(f"\nAPOE Genotype: {results['apoe_determination']['genotype']}")
    print(f"Status: {results['apoe_determination']['interpretation']}")

    print("\n" + "-" * 60)
    print("Category Scores:")
    for cat, cat_score in score_data["category_scores"].items():
        score_str = f"+{cat_score:.1f}" if cat_score > 0 else f"{cat_score:.1f}"
        print(f"  {cat.replace('_', ' ').title()}: {score_str}")

    print("\n" + "=" * 60)
    print("Analysis complete. See report for detailed recommendations.")
    print("=" * 60)


if __name__ == "__main__":
    main()

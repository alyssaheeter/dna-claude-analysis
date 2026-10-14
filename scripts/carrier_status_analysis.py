#!/usr/bin/env python3
"""
Carrier Status Analysis Script
Analyzes genetic carrier status for hereditary diseases from 23andMe data
Includes family planning implications and recommendations
"""

import os
from collections import defaultdict
from datetime import datetime

# Paths
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENOME_FILE = f"{BASE_PATH}/data/my_dna_file.txt"
REPORTS_PATH = f"{BASE_PATH}/reports"

# =============================================================================
# CARRIER STATUS SNP DATABASE
# Organized by disease category with carrier interpretations
# =============================================================================

CARRIER_SNPS = {
    "cystic_fibrosis": {
        "name": "Cystic Fibrosis",
        "inheritance": "Autosomal recessive",
        "frequency": "1 in 25 carriers among Europeans",
        "snps": {
            "rs113993960": {
                "gene": "CFTR",
                "mutation": "F508del (p.Phe508del)",
                "description": "Most common cystic fibrosis mutation (70% of cases)",
                "risk_allele": "del",
                "interpretation": {
                    "--": ("carrier", "F508del carrier - deletion detected"),
                    "CTT": ("normal", "Normal - no deletion"),
                    "CT": ("carrier", "Possible carrier (heterozygous)"),
                    "II": ("normal", "Insertion - normal"),
                    "DI": ("carrier", "Deletion carrier"),
                    "DD": ("affected", "Homozygous for the deletion - cystic fibrosis possible"),
                }
            },
            "rs121909005": {
                "gene": "CFTR",
                "mutation": "G542X (p.Gly542Ter)",
                "description": "Nonsense (stop) mutation, 2-3% of cystic fibrosis cases",
                "risk_allele": "A",
                "interpretation": {
                    "AA": ("affected", "G542X homozygous - cystic fibrosis"),
                    "AG": ("carrier", "G542X carrier"),
                    "GA": ("carrier", "G542X carrier"),
                    "GG": ("normal", "Normal - no G542X mutation"),
                }
            },
        }
    },

    "sickle_cell": {
        "name": "Sickle Cell Anemia",
        "inheritance": "Autosomal recessive",
        "frequency": "1 in 12 carriers among African Americans, rare in Europeans",
        "snps": {
            "rs334": {
                "gene": "HBB",
                "mutation": "HbS (p.Glu6Val)",
                "description": "Sickle cell anemia mutation",
                "risk_allele": "T",
                "interpretation": {
                    "AA": ("normal", "Normal - normal hemoglobin HbA"),
                    "AT": ("carrier", "HbS carrier - sickle cell trait (protection against malaria)"),
                    "TA": ("carrier", "HbS carrier - sickle cell trait (protection against malaria)"),
                    "TT": ("affected", "Sickle cell anemia (HbSS) - medical follow-up required"),
                }
            },
        }
    },

    "tay_sachs": {
        "name": "Tay-Sachs Disease",
        "inheritance": "Autosomal recessive",
        "frequency": "1 in 30 carriers among Ashkenazi Jews",
        "snps": {
            "rs80338939": {
                "gene": "HEXA",
                "mutation": "IVS12+1G>C / 1278insTATC",
                "description": "Tay-Sachs disease mutation",
                "risk_allele": "T",
                "interpretation": {
                    "CC": ("normal", "Normal - no mutation"),
                    "CT": ("carrier", "Tay-Sachs mutation carrier"),
                    "TC": ("carrier", "Tay-Sachs mutation carrier"),
                    "TT": ("affected", "Homozygous - Tay-Sachs disease"),
                    "GG": ("normal", "Normal"),
                    "AG": ("carrier", "Possible carrier"),
                    "GA": ("carrier", "Possible carrier"),
                    "AA": ("affected", "Tay-Sachs disease possible"),
                }
            },
        }
    },

    "gaucher": {
        "name": "Gaucher Disease",
        "inheritance": "Autosomal recessive",
        "frequency": "1 in 15 carriers among Ashkenazi Jews",
        "snps": {
            "rs76763715": {
                "gene": "GBA",
                "mutation": "N370S (p.Asn409Ser)",
                "description": "Most common mutation in Gaucher disease type 1",
                "risk_allele": "A",
                "interpretation": {
                    "GG": ("normal", "Normal - no N370S mutation"),
                    "AG": ("carrier", "N370S carrier - Gaucher disease type 1"),
                    "GA": ("carrier", "N370S carrier - Gaucher disease type 1"),
                    "AA": ("affected", "N370S homozygous - Gaucher disease type 1"),
                    "CC": ("normal", "Normal"),
                    "CT": ("carrier", "Possible carrier"),
                    "TC": ("carrier", "Possible carrier"),
                    "TT": ("affected", "Gaucher disease possible"),
                }
            },
        }
    },

    "hearing_loss": {
        "name": "Hereditary Deafness (GJB2)",
        "inheritance": "Autosomal recessive",
        "frequency": "1 in 30-50 carriers in the general population",
        "snps": {
            "rs80338939": {
                "gene": "GJB2",
                "mutation": "35delG (c.35delG)",
                "description": "Most common cause of hereditary deafness in Europeans",
                "risk_allele": "del",
                "interpretation": {
                    "--": ("carrier", "35delG carrier"),
                    "GG": ("normal", "Normal - no 35delG deletion"),
                    "G-": ("carrier", "35delG deletion carrier"),
                    "-G": ("carrier", "35delG deletion carrier"),
                    "CC": ("normal", "Normal"),
                    "CT": ("carrier", "Possible carrier"),
                    "TT": ("affected", "Deafness possible"),
                }
            },
        }
    },

    "hemochromatosis": {
        "name": "Hemochromatosis",
        "inheritance": "Autosomal recessive with incomplete penetrance",
        "frequency": "1 in 8-10 carriers among Europeans",
        "snps": {
            "rs1800562": {
                "gene": "HFE",
                "mutation": "C282Y (p.Cys282Tyr)",
                "description": "Main mutation in hereditary hemochromatosis",
                "risk_allele": "A",
                "interpretation": {
                    "GG": ("normal", "Normal - no C282Y mutation"),
                    "AG": ("carrier", "C282Y carrier - ferritin monitoring recommended"),
                    "GA": ("carrier", "C282Y carrier - ferritin monitoring recommended"),
                    "AA": ("affected", "C282Y homozygous - high risk of hemochromatosis, iron monitoring is essential"),
                }
            },
            "rs1799945": {
                "gene": "HFE",
                "mutation": "H63D (p.His63Asp)",
                "description": "Second most common HFE mutation (mild effect)",
                "risk_allele": "G",
                "interpretation": {
                    "CC": ("normal", "Normal - no H63D mutation"),
                    "CG": ("carrier", "H63D carrier - usually clinically insignificant"),
                    "GC": ("carrier", "H63D carrier - usually clinically insignificant"),
                    "GG": ("mild_risk", "H63D homozygous - slight risk of iron accumulation"),
                }
            },
        }
    },

    "alpha1_antitrypsin": {
        "name": "Alpha-1 Antitrypsin Deficiency",
        "inheritance": "Autosomal codominant",
        "frequency": "1 in 25 carriers of the Z allele among Europeans",
        "snps": {
            "rs28929474": {
                "gene": "SERPINA1",
                "mutation": "Z (p.Glu342Lys)",
                "description": "Severe deficiency - risk of emphysema and cirrhosis",
                "risk_allele": "T",
                "interpretation": {
                    "CC": ("normal", "MM genotype - normal (100% A1AT activity)"),
                    "CT": ("carrier", "MZ genotype - carrier (~60% activity, avoid smoking!)"),
                    "TC": ("carrier", "MZ genotype - carrier (~60% activity, avoid smoking!)"),
                    "TT": ("affected", "ZZ genotype - severe deficiency (~15% activity), risk of emphysema/cirrhosis"),
                    "GG": ("normal", "Normal"),
                    "AG": ("carrier", "Z allele carrier"),
                    "GA": ("carrier", "Z allele carrier"),
                    "AA": ("affected", "ZZ genotype"),
                }
            },
            "rs17580": {
                "gene": "SERPINA1",
                "mutation": "S (p.Glu264Val)",
                "description": "Moderate A1AT deficiency",
                "risk_allele": "T",
                "interpretation": {
                    "AA": ("normal", "Normal - no S allele"),
                    "AT": ("carrier", "MS genotype - S carrier (~80% activity)"),
                    "TA": ("carrier", "MS genotype - S carrier (~80% activity)"),
                    "TT": ("mild_risk", "SS genotype - moderate deficiency (~60% activity)"),
                    "GG": ("normal", "Normal"),
                    "GT": ("carrier", "S allele carrier"),
                    "TG": ("carrier", "S allele carrier"),
                }
            },
        }
    },

    "phenylketonuria": {
        "name": "Phenylketonuria (PKU)",
        "inheritance": "Autosomal recessive",
        "frequency": "1 in 50 carriers among Europeans",
        "snps": {
            "rs5030858": {
                "gene": "PAH",
                "mutation": "R408W (p.Arg408Trp)",
                "description": "Common phenylketonuria mutation in Eastern Europe",
                "risk_allele": "A",
                "interpretation": {
                    "GG": ("normal", "Normal - no R408W mutation"),
                    "AG": ("carrier", "R408W carrier - PKU"),
                    "GA": ("carrier", "R408W carrier - PKU"),
                    "AA": ("affected", "R408W homozygous - phenylketonuria"),
                    "CC": ("normal", "Normal"),
                    "CT": ("carrier", "PAH mutation carrier"),
                    "TC": ("carrier", "PAH mutation carrier"),
                    "TT": ("affected", "Phenylketonuria"),
                }
            },
        }
    },

    "brca_hereditary_cancer": {
        "name": "Hereditary Cancer (BRCA1/BRCA2)",
        "inheritance": "Autosomal dominant (one copy is enough to confer risk)",
        "frequency": "1 in 40 among Ashkenazi Jews, 1 in 400-500 in the general population",
        "snps": {
            "rs80357906": {
                "gene": "BRCA1",
                "mutation": "185delAG (c.68_69delAG)",
                "description": "BRCA1 founder mutation - high risk of breast/ovarian cancer",
                "risk_allele": "del",
                "interpretation": {
                    "--": ("high_risk", "185delAG carrier - high risk of breast cancer (up to 80%) and ovarian cancer (up to 40%)"),
                    "AG": ("normal", "Normal - no 185delAG mutation"),
                    "GA": ("normal", "Normal"),
                    "AA": ("normal", "Normal"),
                    "GG": ("normal", "Normal"),
                    "A-": ("high_risk", "BRCA1 deletion carrier"),
                    "-A": ("high_risk", "BRCA1 deletion carrier"),
                    "G-": ("high_risk", "BRCA1 deletion carrier"),
                    "-G": ("high_risk", "BRCA1 deletion carrier"),
                    "II": ("normal", "Normal - insertion"),
                    "DI": ("high_risk", "Deletion carrier"),
                    "ID": ("high_risk", "Deletion carrier"),
                    "DD": ("high_risk", "Homozygous - genetic counseling required"),
                }
            },
            "rs80359550": {
                "gene": "BRCA2",
                "mutation": "6174delT (c.5946delT)",
                "description": "BRCA2 founder mutation - high risk of breast cancer",
                "risk_allele": "del",
                "interpretation": {
                    "--": ("high_risk", "6174delT carrier - high risk of breast and prostate cancer"),
                    "TT": ("normal", "Normal - no 6174delT deletion"),
                    "T-": ("high_risk", "BRCA2 deletion carrier"),
                    "-T": ("high_risk", "BRCA2 deletion carrier"),
                    "AA": ("normal", "Normal"),
                    "CC": ("normal", "Normal"),
                    "GG": ("normal", "Normal"),
                    "II": ("normal", "Normal"),
                    "DI": ("high_risk", "Deletion carrier"),
                    "ID": ("high_risk", "Deletion carrier"),
                    "DD": ("high_risk", "Homozygous for the deletion"),
                }
            },
        }
    },
}

# Family planning notes for each condition
FAMILY_PLANNING_NOTES = {
    "cystic_fibrosis": """
    **Family planning for cystic fibrosis carriers:**
    - If both partners are carriers: 25% risk of having a child with cystic fibrosis
    - Partner testing before pregnancy is recommended
    - PGD (preimplantation genetic diagnosis) and prenatal diagnosis are available
    - The disease is serious, but treatment has improved significantly
    """,

    "sickle_cell": """
    **Family planning for sickle cell anemia carriers:**
    - Carrier status (AT) protects against malaria without disease symptoms
    - If both partners are carriers: 25% risk of sickle cell anemia in the child
    - Partner testing is strongly recommended
    - Newborn screening detects the disease at birth
    """,

    "tay_sachs": """
    **Family planning for Tay-Sachs disease carriers:**
    - Especially important for couples of Ashkenazi descent
    - If both are carriers: 25% risk of Tay-Sachs disease (fatal in childhood)
    - Partner testing is essential
    - PGD can prevent the birth of an affected child
    """,

    "gaucher": """
    **Family planning for Gaucher disease carriers:**
    - Type 1 (N370S) is the mildest and is compatible with a normal life
    - If both are carriers: 25% risk of Gaucher disease
    - Effective enzyme replacement therapy is available
    - Partner testing is recommended, especially for Ashkenazi Jews
    """,

    "hearing_loss": """
    **Family planning for hereditary deafness carriers:**
    - If both partners carry 35delG: 25% risk of deafness in the child
    - Partner testing is recommended
    - Deafness does not affect life expectancy
    - Cochlear implants are effective when detected early
    """,

    "hemochromatosis": """
    **Family planning for hemochromatosis carriers/affected individuals:**
    - C282Y homozygotes should monitor ferritin regularly
    - Carriers usually have no clinical manifestations
    - The disease responds well to treatment (phlebotomy)
    - Low priority for PGD, since the disease is manageable
    """,

    "alpha1_antitrypsin": """
    **Family planning for alpha-1 antitrypsin deficiency:**
    - MZ carriers: avoid smoking and occupational hazards!
    - ZZ genotype: high risk of emphysema, especially with smoking
    - Partner testing is recommended
    - The disease manifests in adulthood; treatment is available
    """,

    "phenylketonuria": """
    **Family planning for phenylketonuria carriers:**
    - If both are carriers: 25% risk of PKU in the child
    - Newborn screening is mandatory in all countries
    - With early diagnosis and diet, development is normal
    - Women with PKU must follow the diet BEFORE and during pregnancy
    """,

    "brca_hereditary_cancer": """
    **Family planning for BRCA1/BRCA2 mutations:**
    - IMPORTANT: BRCA mutations are dominant - one copy is enough to confer risk
    - 50% risk of passing the mutation to each child
    - PGD is available to prevent transmission of the mutation
    - Genetic counseling is necessary
    - For carriers: enhanced screening, preventive options
    """,
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


def analyze_carriers(genome):
    """Analyze carrier status for all conditions"""
    all_results = {}

    for condition_id, condition_info in CARRIER_SNPS.items():
        results = []

        for snp_id, snp_info in condition_info['snps'].items():
            result = {
                'snp_id': snp_id,
                'gene': snp_info['gene'],
                'mutation': snp_info['mutation'],
                'description': snp_info['description'],
                'risk_allele': snp_info['risk_allele'],
                'found': False,
                'genotype': None,
                'carrier_status': None,
                'interpretation': None
            }

            if snp_id in genome:
                result['found'] = True
                raw_genotype = genome[snp_id]['genotype']
                result['genotype'] = raw_genotype
                result['chromosome'] = genome[snp_id]['chromosome']
                result['position'] = genome[snp_id]['position']

                # Try to find interpretation
                interpretations = snp_info.get('interpretation', {})

                # Try original genotype
                if raw_genotype in interpretations:
                    result['carrier_status'], result['interpretation'] = interpretations[raw_genotype]
                else:
                    # Try normalized
                    normalized = normalize_genotype(raw_genotype)
                    if normalized in interpretations:
                        result['carrier_status'], result['interpretation'] = interpretations[normalized]
                    else:
                        # Try reversed
                        reversed_gt = raw_genotype[::-1] if len(raw_genotype) == 2 else raw_genotype
                        if reversed_gt in interpretations:
                            result['carrier_status'], result['interpretation'] = interpretations[reversed_gt]
                        else:
                            # Default interpretation based on risk allele presence
                            risk = snp_info['risk_allele']
                            if raw_genotype == '--' or 'del' in raw_genotype.lower():
                                result['carrier_status'] = 'possible_carrier'
                                result['interpretation'] = 'Deletion detected - confirmation required'
                            elif risk in raw_genotype:
                                risk_count = raw_genotype.count(risk)
                                if risk_count == 2:
                                    result['carrier_status'] = 'affected'
                                    result['interpretation'] = f'Homozygous for risk allele {risk}'
                                else:
                                    result['carrier_status'] = 'carrier'
                                    result['interpretation'] = f'Heterozygous - carrier of allele {risk}'
                            else:
                                result['carrier_status'] = 'normal'
                                result['interpretation'] = 'Risk allele not detected'

            results.append(result)

        all_results[condition_id] = {
            'info': condition_info,
            'results': results
        }

    return all_results


def get_status_emoji(status):
    """Get emoji for carrier status"""
    status_map = {
        'normal': '[ OK ]',
        'carrier': '[CARR]',
        'affected': '[!!!!]',
        'high_risk': '[!!!!]',
        'mild_risk': '[MILD]',
        'possible_carrier': '[ ?? ]',
    }
    return status_map.get(status, '[----]')


def get_status_icon_md(status):
    """Get markdown status indicator"""
    status_map = {
        'normal': 'Normal',
        'carrier': 'CARRIER',
        'affected': 'AFFECTED',
        'high_risk': 'HIGH RISK',
        'mild_risk': 'Mild Risk',
        'possible_carrier': 'Possible Carrier',
    }
    return status_map.get(status, 'Unknown')


def generate_report(results):
    """Generate comprehensive carrier status report with family planning notes"""
    report = []

    report.append("# Carrier Status Analysis Report")
    report.append("# Genetic Disease Carrier Status Report")
    report.append("")
    report.append(f"**Analysis date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("")
    report.append("---")
    report.append("")

    # Important warnings
    report.append("## IMPORTANT WARNINGS")
    report.append("")
    report.append("1. **This is NOT a medical diagnosis** - informational analysis only")
    report.append("2. **Carrier status =/= disease** - carriers are usually healthy")
    report.append("3. **For recessive diseases** - the child is at risk only if BOTH parents are carriers")
    report.append("4. **BRCA mutations are DOMINANT** - one copy creates cancer risk")
    report.append("5. **23andMe tests a limited set of mutations** - a negative result does not guarantee the absence of carrier status")
    report.append("6. **For family planning** - consultation with a geneticist is ESSENTIAL")
    report.append("")
    report.append("---")
    report.append("")

    # Summary section
    report.append("## CARRIER STATUS SUMMARY")
    report.append("")

    carriers_found = []
    affected_found = []
    high_risk_found = []
    normal_count = 0
    not_found_count = 0

    for condition_id, data in results.items():
        for r in data['results']:
            if not r['found']:
                not_found_count += 1
            elif r['carrier_status'] == 'carrier':
                carriers_found.append((condition_id, r))
            elif r['carrier_status'] == 'affected':
                affected_found.append((condition_id, r))
            elif r['carrier_status'] == 'high_risk':
                high_risk_found.append((condition_id, r))
            elif r['carrier_status'] in ['normal', 'mild_risk']:
                normal_count += 1

    # Alert section for significant findings
    if affected_found or high_risk_found:
        report.append("### !!! CRITICAL FINDINGS !!!")
        report.append("")
        for condition_id, r in affected_found + high_risk_found:
            condition_name = results[condition_id]['info']['name']
            report.append(f"- **{condition_name}**: {r['gene']} {r['mutation']}")
            report.append(f"  - Genotype: **{r['genotype']}**")
            report.append(f"  - Status: **{get_status_icon_md(r['carrier_status'])}**")
            report.append(f"  - {r['interpretation']}")
            report.append("")
        report.append("**GENETIC COUNSELING IS NEEDED!**")
        report.append("")

    if carriers_found:
        report.append("### Carrier status detected")
        report.append("")
        for condition_id, r in carriers_found:
            condition_name = results[condition_id]['info']['name']
            report.append(f"- **{condition_name}**: {r['gene']} {r['mutation']}")
            report.append(f"  - Genotype: **{r['genotype']}**")
            report.append(f"  - {r['interpretation']}")
        report.append("")

    # Statistics
    report.append("### Statistics")
    report.append("")
    report.append(f"- Total conditions analyzed: {len(results)}")
    report.append(f"- Normal results: {normal_count}")
    report.append(f"- Carrier status detected: {len(carriers_found)}")
    report.append(f"- Elevated risk/disease: {len(affected_found) + len(high_risk_found)}")
    report.append(f"- SNPs not found in genome: {not_found_count}")
    report.append("")
    report.append("---")
    report.append("")

    # Detailed results by condition
    report.append("## DETAILED RESULTS BY CONDITION")
    report.append("")

    for condition_id, data in results.items():
        info = data['info']
        condition_results = data['results']

        report.append(f"### {info['name']}")
        report.append("")
        report.append(f"- **Inheritance type:** {info['inheritance']}")
        report.append(f"- **Carrier frequency:** {info['frequency']}")
        report.append("")

        report.append("| SNP | Gene | Mutation | Genotype | Status | Interpretation |")
        report.append("|-----|-----|----------|---------|--------|----------------|")

        for r in condition_results:
            if r['found']:
                status = get_status_icon_md(r['carrier_status'])
                report.append(f"| {r['snp_id']} | {r['gene']} | {r['mutation']} | **{r['genotype']}** | {status} | {r['interpretation']} |")
            else:
                report.append(f"| {r['snp_id']} | {r['gene']} | {r['mutation']} | - | - | Not found in genome |")

        report.append("")

        # Add family planning notes if carrier or affected
        has_findings = any(r['carrier_status'] in ['carrier', 'affected', 'high_risk']
                         for r in condition_results if r['found'])

        if has_findings and condition_id in FAMILY_PLANNING_NOTES:
            report.append("#### Family Planning")
            # Convert notes to Latin transliteration
            notes = FAMILY_PLANNING_NOTES[condition_id]
            report.append(notes.replace("**", "**"))
            report.append("")

        report.append("---")
        report.append("")

    # General family planning section
    report.append("## GENERAL FAMILY PLANNING RECOMMENDATIONS")
    report.append("")
    report.append("### If you are a carrier of a recessive condition:")
    report.append("")
    report.append("1. **Partner testing** - the most important step")
    report.append("   - If the partner is NOT a carrier - risk to children is minimal")
    report.append("   - If the partner is also a carrier - 25% risk for each child")
    report.append("")
    report.append("2. **Options available for two carriers:**")
    report.append("   - PGD (preimplantation genetic diagnosis) with IVF")
    report.append("   - Prenatal diagnosis (CVS, amniocentesis)")
    report.append("   - Donor gametes")
    report.append("   - Adoption")
    report.append("")
    report.append("3. **Genetic counseling:**")
    report.append("   - Recommended for all carriers")
    report.append("   - Essential when planning a pregnancy")
    report.append("   - Helps clarify real risks and options")
    report.append("")

    report.append("### If you have a BRCA mutation:")
    report.append("")
    report.append("1. **BRCA is a dominant mutation:**")
    report.append("   - 50% risk of passing it to each child")
    report.append("   - One copy is enough for increased cancer risk")
    report.append("")
    report.append("2. **Recommendations for carriers:**")
    report.append("   - Enhanced screening (MRI, mammography)")
    report.append("   - Discussion of preventive surgery")
    report.append("   - Genetic counseling for the family")
    report.append("")
    report.append("3. **Family planning options:**")
    report.append("   - PGD allows selection of embryos without the mutation")
    report.append("   - Testing of children is possible in adulthood")
    report.append("")

    report.append("---")
    report.append("")
    report.append("## LIMITATIONS OF THIS ANALYSIS")
    report.append("")
    report.append("1. **23andMe tests only specific mutations:**")
    report.append("   - Not all mutations of a given gene")
    report.append("   - A negative result does not guarantee the absence of carrier status")
    report.append("")
    report.append("2. **For a complete carrier analysis:**")
    report.append("   - An expanded carrier panel (100+ conditions) is recommended")
    report.append("   - Clinical laboratories (Invitae, Natera, GeneDx)")
    report.append("")
    report.append("3. **This report:**")
    report.append("   - For informational purposes only")
    report.append("   - Does not replace clinical testing")
    report.append("   - Requires interpretation by a geneticist")
    report.append("")

    report.append("---")
    report.append("")
    report.append("*Report generated automatically*")
    report.append(f"*Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    return '\n'.join(report)


def main():
    print("=" * 60)
    print("CARRIER STATUS ANALYSIS")
    print("Genetic disease carrier status analysis")
    print("=" * 60)

    print("\n[1/3] Loading genome...")
    genome = load_genome()
    print(f"      Loaded {len(genome)} SNPs")

    print("\n[2/3] Analyzing carrier status...")
    results = analyze_carriers(genome)

    # Print summary to console
    print("\n" + "-" * 60)
    print("ANALYSIS RESULTS:")
    print("-" * 60)

    for condition_id, data in results.items():
        info = data['info']
        condition_results = data['results']

        print(f"\n{info['name']}:")

        for r in condition_results:
            if r['found']:
                status = get_status_emoji(r['carrier_status'])
                print(f"  {status} {r['snp_id']} ({r['gene']}): {r['genotype']}")
                print(f"           {r['interpretation']}")
            else:
                print(f"  [----] {r['snp_id']} ({r['gene']}): Not found")

    print("\n[3/3] Generating report...")

    # Ensure directory exists
    report_dir = f"{REPORTS_PATH}/carrier_status"
    os.makedirs(report_dir, exist_ok=True)

    report = generate_report(results)
    report_path = f"{report_dir}/report.md"

    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"      -> {report_path}")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

    # Print key findings
    carriers = []
    affected = []

    for condition_id, data in results.items():
        for r in data['results']:
            if r['found']:
                if r['carrier_status'] == 'carrier':
                    carriers.append((data['info']['name'], r))
                elif r['carrier_status'] in ['affected', 'high_risk']:
                    affected.append((data['info']['name'], r))

    if affected:
        print("\n!!! CRITICAL FINDINGS !!!\n")
        for name, r in affected:
            print(f"  {name}: {r['gene']} {r['genotype']}")
            print(f"  -> {r['interpretation']}")
            print()

    if carriers:
        print("\nCARRIER STATUS DETECTED:\n")
        for name, r in carriers:
            print(f"  {name}: {r['gene']} {r['genotype']}")
            print(f"  -> {r['interpretation']}")
            print()

    if not carriers and not affected:
        print("\nNo carrier status detected in the SNPs checked.")
        print("WARNING: 23andMe tests only a limited set of mutations.")


if __name__ == "__main__":
    main()

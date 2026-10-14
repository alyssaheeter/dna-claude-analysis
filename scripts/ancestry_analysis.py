#!/usr/bin/env python3
"""
Ancestry Analysis Script
Analyzes ancestry-related genetic markers from 23andMe data
"""

import os
from datetime import datetime

# Paths
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENOME_FILE = f"{BASE_PATH}/data/my_dna_file.txt"
REPORTS_PATH = f"{BASE_PATH}/reports"

# =============================================================================
# SNP DATABASE - Ancestry markers
# =============================================================================

ANCESTRY_SNPS = {
    "pigmentation": {
        "name": "Pigmentation (ancestry)",
        "snps": {
            "rs1426654": {
                "gene": "SLC24A5",
                "description": "Light skin (Europe)",
                "interpretation": {
                    "AA": ("european", "European variant - light skin"),
                    "AG": ("mixed", "Mixed"),
                    "GG": ("ancestral", "Ancestral variant - dark skin"),
                }
            },
            "rs16891982": {
                "gene": "SLC45A2",
                "description": "Light skin (Europe)",
                "interpretation": {
                    "GG": ("european", "European variant - light skin"),
                    "CG": ("mixed", "Mixed"),
                    "CC": ("ancestral", "Ancestral variant"),
                }
            },
            "rs12913832": {
                "gene": "HERC2/OCA2",
                "description": "Eye color, Northern Europe",
                "interpretation": {
                    "AA": ("other", "Brown eyes"),
                    "AG": ("mixed", "Green/hazel eyes"),
                    "GG": ("northern_european", "Blue eyes - Northern Europe"),
                }
            },
            "rs1800407": {
                "gene": "OCA2",
                "description": "Light eyes (Europe)",
                "interpretation": {
                    "TT": ("european", "Light eyes"),
                    "GT": ("mixed", "Mixed"),
                    "GG": ("other", "Dark eyes"),
                }
            },
        }
    },

    "east_asian": {
        "name": "East Asian markers",
        "snps": {
            "rs3827760": {
                "gene": "EDAR",
                "description": "Thick hair, shovel-shaped incisors",
                "interpretation": {
                    "CC": ("east_asian", "East Asian variant - thick hair"),
                    "CT": ("mixed", "Mixed"),
                    "TT": ("other", "Non-Asian variant"),
                }
            },
            "rs17822931": {
                "gene": "ABCC11",
                "description": "Earwax type",
                "interpretation": {
                    "CC": ("east_asian", "Dry earwax (East Asia)"),
                    "CT": ("mixed", "Mixed"),
                    "TT": ("other", "Wet earwax (Europe/Africa)"),
                }
            },
        }
    },

    "african": {
        "name": "African markers",
        "snps": {
            "rs2814778": {
                "gene": "DARC (Duffy)",
                "description": "Duffy null - malaria resistance",
                "interpretation": {
                    "CC": ("african", "Duffy null - African ancestry, protection from P.vivax"),
                    "CT": ("mixed", "Carrier"),
                    "TT": ("other", "Duffy positive"),
                }
            },
        }
    },

    "lactase": {
        "name": "Lactase persistence (geography)",
        "snps": {
            "rs4988235": {
                "gene": "LCT (MCM6)",
                "description": "Lactose tolerance",
                "interpretation": {
                    "TT": ("european_pastoral", "European pastoral variant - tolerates lactose"),
                    "CT": ("mixed", "Partial tolerance"),
                    "CC": ("ancestral", "Ancestral variant - lactose intolerance"),
                    "AA": ("european_pastoral", "Tolerates lactose"),
                    "AG": ("mixed", "Partial tolerance"),
                    "GG": ("ancestral", "Lactose intolerance"),
                }
            },
            "rs182549": {
                "gene": "LCT",
                "description": "Lactase persistence (Arab/African)",
                "interpretation": {
                    "CC": ("arabic_african", "Tolerates lactose (Arab/African variant)"),
                    "CT": ("mixed", "Partial"),
                    "TT": ("ancestral", "Ancestral variant"),
                }
            },
        }
    },

    "neanderthal": {
        "name": "Neanderthal heritage",
        "snps": {
            "rs2298813": {
                "gene": "Neanderthal",
                "description": "Hair growth direction",
                "interpretation": {
                    "AA": ("neanderthal", "Neanderthal variant"),
                    "AG": ("mixed", "Mixed"),
                    "GG": ("modern", "Modern human"),
                }
            },
            "rs3917862": {
                "gene": "Neanderthal",
                "description": "Blood clotting",
                "interpretation": {
                    "TT": ("neanderthal", "Neanderthal variant"),
                    "CT": ("mixed", "Mixed"),
                    "CC": ("modern", "Modern"),
                }
            },
        }
    },
}

# Y-chromosome haplogroups (males only)
Y_HAPLOGROUPS = {
    "rs9786184": ("R1b", "M269 - Western Europe"),
    "rs17250804": ("R1a", "M17/M198 - Eastern Europe, Asia"),
    "rs9341296": ("I1", "M253 - Scandinavia"),
    "rs2032597": ("I2", "M438 - Balkans, Eastern Europe"),
    "rs34126399": ("J1", "M267 - Middle East"),
    "rs34305635": ("J2", "M172 - Mediterranean"),
    "rs2032604": ("E1b1b", "M35 - Africa, Mediterranean"),
    "rs2032636": ("G", "M201 - Caucasus, Europe"),
    "rs9341301": ("N", "M231 - Finno-Ugric peoples, Siberia"),
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


def analyze_ancestry(genome):
    """Analyze ancestry markers"""
    results = {}

    for category, cat_info in ANCESTRY_SNPS.items():
        cat_results = []
        for snp_id, snp_info in cat_info['snps'].items():
            result = {
                'snp_id': snp_id,
                'gene': snp_info['gene'],
                'description': snp_info['description'],
                'found': False,
                'genotype': None,
                'origin': None,
                'interpretation': None
            }

            if snp_id in genome:
                result['found'] = True
                genotype = genome[snp_id]['genotype']
                result['genotype'] = genotype

                # Try to find interpretation
                interp = snp_info.get('interpretation', {})
                for gt in [genotype, genotype[::-1] if len(genotype) == 2 else genotype]:
                    if gt in interp:
                        result['origin'], result['interpretation'] = interp[gt]
                        break

            cat_results.append(result)
        results[category] = cat_results

    return results


def analyze_y_haplogroup(genome):
    """Analyze Y-chromosome haplogroup markers"""
    results = []

    for snp_id, (haplogroup, description) in Y_HAPLOGROUPS.items():
        if snp_id in genome:
            genotype = genome[snp_id]['genotype']
            # Check if derived allele present (simplified)
            results.append({
                'snp_id': snp_id,
                'haplogroup': haplogroup,
                'description': description,
                'genotype': genotype,
                'found': True
            })

    return results


def determine_sex(genome):
    """Determine genetic sex from Y-chromosome markers"""
    # Check for Y chromosome SNPs
    y_snps = [snp for snp, data in genome.items() if data['chromosome'] == 'Y']
    return 'male' if len(y_snps) > 10 else 'female'


def generate_report(results, y_results, sex, genome):
    """Generate ancestry report"""
    report = []
    report.append("# 🌍 Ancestry Analysis")
    report.append(f"\nAnalysis date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"\nGenetic sex: **{'Male' if sex == 'male' else 'Female'}**")
    report.append("\n---\n")

    report.append("## ⚠️ Important\n")
    report.append("- This is a simplified analysis based on individual SNPs")
    report.append("- Accurate ancestry determination requires analysis of thousands of markers")
    report.append("- We recommend uploading your data to GEDmatch or DNA.Land for detailed analysis\n")
    report.append("---\n")

    # Ancestry Informative Markers
    report.append("## 🧬 Ancestry Informative Markers (AIMs)\n")

    for category, cat_results in results.items():
        cat_name = ANCESTRY_SNPS[category]['name']
        report.append(f"### {cat_name}\n")
        report.append("| SNP | Gene | Genotype | Interpretation |")
        report.append("|-----|-----|---------|---------------|")

        for r in cat_results:
            if r['found']:
                interp = r['interpretation'] or 'No data'
                report.append(f"| {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {interp} |")
            else:
                report.append(f"| {r['snp_id']} | {r['gene']} | - | Not found |")
        report.append("")

    # Y-haplogroup (if male)
    if sex == 'male' and y_results:
        report.append("## 👨 Y-chromosome haplogroup (paternal line)\n")
        report.append("| SNP | Haplogroup | Genotype | Description |")
        report.append("|-----|-------------|---------|----------|")

        for r in y_results:
            report.append(f"| {r['snp_id']} | {r['haplogroup']} | {r['genotype']} | {r['description']} |")

        report.append("\n**Note**: For accurate Y-haplogroup determination, YFull or FTDNA is recommended")
        report.append("")

    # Summary
    report.append("\n---\n")
    report.append("## 📊 Summary\n")

    # Count origins
    origin_counts = {}
    for cat_results in results.values():
        for r in cat_results:
            if r['origin']:
                origin_counts[r['origin']] = origin_counts.get(r['origin'], 0) + 1

    origin_labels = {
        'european': '🇪🇺 European',
        'northern_european': '🇸🇪 Northern European',
        'european_pastoral': '🐄 European pastoral',
        'east_asian': '🇯🇵 East Asian',
        'african': '🌍 African',
        'arabic_african': '🏜️ Arab/African',
        'neanderthal': '🦴 Neanderthal',
        'ancestral': '🌿 Ancestral',
        'mixed': '🔀 Mixed',
        'modern': '👤 Modern human',
        'other': '• Other'
    }

    if origin_counts:
        for origin, count in sorted(origin_counts.items(), key=lambda x: -x[1]):
            label = origin_labels.get(origin, origin)
            report.append(f"- {label}: {count} markers")

    report.append("\n---\n")
    report.append("## 🔗 Recommended Resources\n")
    report.append("- **GEDmatch**: gedmatch.com - free comparison against databases")
    report.append("- **DNA.Land**: dna.land - free ancestry analysis")
    report.append("- **YFull**: yfull.com - detailed Y-chromosome analysis")
    report.append("- **FTDNA**: familytreedna.com - transfer for haplogroups")

    return '\n'.join(report)


def main():
    print("=" * 60)
    print("ANCESTRY ANALYSIS FROM 23andMe GENOME")
    print("=" * 60)

    print("\n[1/4] Loading genome...")
    genome = load_genome()
    print(f"      Loaded {len(genome)} SNPs")

    print("\n[2/4] Determining sex...")
    sex = determine_sex(genome)
    print(f"      Genetic sex: {'male' if sex == 'male' else 'female'}")

    print("\n[3/4] Analyzing ancestry markers...")
    results = analyze_ancestry(genome)

    y_results = []
    if sex == 'male':
        print("      Analyzing Y chromosome...")
        y_results = analyze_y_haplogroup(genome)

    print("\n[4/4] Generating report...")
    report = generate_report(results, y_results, sex, genome)

    report_path = f"{REPORTS_PATH}/ancestry/report.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"      → {report_path}")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()

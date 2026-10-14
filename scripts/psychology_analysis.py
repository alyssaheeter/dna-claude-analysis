#!/usr/bin/env python3
"""
Psychology and Behavior Analysis Script
Analyzes psychological and behavioral genetic markers from 23andMe data
"""

import os
from collections import defaultdict
from datetime import datetime

# Paths
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENOME_FILE = f"{BASE_PATH}/data/my_dna_file.txt"
REPORTS_PATH = f"{BASE_PATH}/reports"

# =============================================================================
# DISCLAIMER
# =============================================================================

DISCLAIMER = """
**IMPORTANT DISCLAIMER**

Genes are a predisposition, NOT destiny.

1. Genetic variants influence tendencies, but do NOT determine behavior
2. Environment, upbringing and personal choice play a huge role
3. Neuroplasticity allows the brain to change throughout life
4. A single SNP rarely determines a complex trait - it is always an interaction of many genes
5. The effect of most variants is very small (usually <1% of influence)
6. This analysis is for INFORMATIONAL purposes ONLY
7. For psychological help, consult a qualified professional

Remember: you are NOT a slave to your genes. Awareness of predispositions can help
you develop more effective strategies for coping and growth.
"""

# =============================================================================
# SNP DATABASE - Psychology and Behavior
# =============================================================================

PSYCHOLOGY_SNPS = {
    "serotonin": {
        "name": "Serotonin system",
        "description": "Regulates mood, anxiety, sleep and impulsivity",
        "snps": {
            "rs25531": {
                "gene": "SLC6A4 (5-HTTLPR)",
                "description": "Serotonin transporter - stress sensitivity",
                "interpretation": {
                    "AA": ("high_sensitivity", "L/L - High transporter expression, more resilient to stress"),
                    "AG": ("moderate_sensitivity", "L/S - Moderate stress sensitivity"),
                    "GG": ("low_sensitivity", "S/S - Reduced expression, increased sensitivity to stress and negative events"),
                },
                "impact": "Affects emotional reactivity and susceptibility to the environment"
            },
            "rs6295": {
                "gene": "HTR1A",
                "description": "Serotonin 1A receptor - anxiety and depression",
                "interpretation": {
                    "CC": ("higher_risk", "Increased risk of anxiety and depression"),
                    "CG": ("moderate", "Moderate risk"),
                    "GG": ("lower_risk", "Reduced risk of anxiety"),
                },
                "impact": "Affects baseline anxiety level"
            },
        }
    },

    "dopamine": {
        "name": "Dopamine system",
        "description": "Regulates motivation, reward, attention and executive function",
        "snps": {
            "rs4680": {
                "gene": "COMT Val158Met",
                "description": "Catechol-O-methyltransferase - dopamine breakdown in the prefrontal cortex",
                "interpretation": {
                    "GG": ("warrior", "Val/Val - 'Warrior': fast dopamine breakdown, stress-resistant, but lower baseline dopamine, more impulsive"),
                    "AG": ("balanced", "Val/Met - Balanced type: intermediate speed, adaptable to different situations"),
                    "AA": ("worrier", "Met/Met - 'Worrier': slow breakdown, higher dopamine, better cognition, but higher anxiety"),
                },
                "impact": "Key marker of cognitive style and stress resilience"
            },
            "rs1800497": {
                "gene": "DRD2/ANKK1 Taq1A",
                "description": "Dopamine D2 receptor density",
                "interpretation": {
                    "AA": ("low_d2", "A1/A1 - Fewer D2 receptors: novelty seeking, addiction risk"),
                    "AG": ("moderate_d2", "A1/A2 - Moderately reduced D2 receptors"),
                    "GG": ("normal_d2", "A2/A2 - Normal number of D2 receptors"),
                },
                "impact": "Affects reward sensitivity"
            },
            "rs1800955": {
                "gene": "DRD4 -521C/T",
                "description": "Dopamine D4 receptor - novelty and ADHD",
                "interpretation": {
                    "TT": ("high_novelty", "Increased novelty and stimulation seeking"),
                    "CT": ("moderate_novelty", "Moderate novelty seeking"),
                    "CC": ("normal_novelty", "Standard level of novelty seeking"),
                },
                "impact": "Affects the need for stimulation and new experiences"
            },
        }
    },

    "neuroplasticity": {
        "name": "Neuroplasticity",
        "description": "The brain's capacity for change, learning and recovery",
        "snps": {
            "rs6265": {
                "gene": "BDNF Val66Met",
                "description": "Brain-derived neurotrophic factor - learning and memory",
                "interpretation": {
                    "CC": ("val_val", "Val/Val - Normal BDNF secretion, good neuroplasticity"),
                    "GG": ("val_val", "Val/Val - Normal BDNF secretion, good neuroplasticity"),
                    "CT": ("val_met", "Val/Met - Slightly reduced secretion, moderate effect on memory"),
                    "AG": ("val_met", "Val/Met - Slightly reduced secretion, moderate effect on memory"),
                    "TT": ("met_met", "Met/Met - Reduced BDNF secretion, poorer episodic memory, higher risk of depression under stress"),
                    "AA": ("met_met", "Met/Met - Reduced BDNF secretion, poorer episodic memory, higher risk of depression under stress"),
                },
                "impact": "Key factor in learning, memory and recovery from stress"
            },
        }
    },

    "oxytocin": {
        "name": "Oxytocin system",
        "description": "Regulates social behavior, trust and empathy",
        "snps": {
            "rs53576": {
                "gene": "OXTR",
                "description": "Oxytocin receptor - sociability and empathy",
                "interpretation": {
                    "GG": ("high_empathy", "High empathy: better at recognizing emotions, more social, more responsive to social support"),
                    "AG": ("moderate_empathy", "Moderate empathy: average level of social sensitivity"),
                    "AA": ("lower_empathy", "Lower empathy: less sensitive to social cues, but more independent"),
                },
                "impact": "Affects the quality of social bonds and emotional intelligence"
            },
            "rs2254298": {
                "gene": "OXTR",
                "description": "Oxytocin receptor - attachment",
                "interpretation": {
                    "AA": ("secure", "More secure attachment style"),
                    "AG": ("mixed", "Mixed style"),
                    "GG": ("anxious", "May have a tendency toward anxious attachment"),
                },
                "impact": "Affects attachment patterns in relationships"
            },
        }
    },

    "addiction_risk": {
        "name": "Addiction risk",
        "description": "Genetic factors of predisposition to addictive behavior",
        "snps": {
            "rs1799971": {
                "gene": "OPRM1 A118G",
                "description": "Mu-opioid receptor - response to opioids and alcohol",
                "interpretation": {
                    "AA": ("normal", "Standard sensitivity to opioids and alcohol"),
                    "AG": ("altered", "Altered response: may need a larger dose of painkillers, different reaction to alcohol"),
                    "GG": ("high_risk", "Increased risk of alcohol dependence, reduced sensitivity to opioids"),
                },
                "impact": "Affects the endorphin reward system"
            },
            "rs16969968": {
                "gene": "CHRNA5",
                "description": "Nicotinic receptor - risk of nicotine dependence",
                "interpretation": {
                    "AA": ("high_risk", "Increased risk of nicotine dependence and heavy smoking"),
                    "AG": ("moderate_risk", "Moderately increased risk"),
                    "GG": ("normal_risk", "Standard risk of nicotine dependence"),
                },
                "impact": "Affects sensitivity to nicotine"
            },
            "rs1800497": {
                "gene": "DRD2/ANKK1",
                "description": "D2 receptors - overall addiction risk",
                "interpretation": {
                    "AA": ("high_risk", "Increased risk of various addictions (alcohol, gambling)"),
                    "AG": ("moderate_risk", "Moderately increased risk"),
                    "GG": ("normal_risk", "Standard risk"),
                },
                "impact": "Key marker of addiction vulnerability"
            },
        }
    },

    "depression_anxiety": {
        "name": "Depression and anxiety risk",
        "description": "Genetic factors of mental health",
        "snps": {
            "rs25531": {
                "gene": "SLC6A4",
                "description": "Serotonin transporter - depression under stress",
                "interpretation": {
                    "GG": ("higher_risk", "S/S - Increased risk of depression under life stress"),
                    "AG": ("moderate_risk", "L/S - Moderate risk"),
                    "AA": ("lower_risk", "L/L - More resilient to depression"),
                },
                "impact": "Gene-environment interaction in the development of depression"
            },
            "rs6265": {
                "gene": "BDNF",
                "description": "Neuroplasticity - depression",
                "interpretation": {
                    "TT": ("higher_risk", "Met/Met - Increased risk of depression, especially under stress"),
                    "AA": ("higher_risk", "Met/Met - Increased risk of depression, especially under stress"),
                    "CT": ("moderate_risk", "Val/Met - Moderately increased risk"),
                    "AG": ("moderate_risk", "Val/Met - Moderately increased risk"),
                    "CC": ("lower_risk", "Val/Val - Standard risk"),
                    "GG": ("lower_risk", "Val/Val - Standard risk"),
                },
                "impact": "Affects recovery from stress"
            },
            "rs4680": {
                "gene": "COMT",
                "description": "Anxiety and rumination",
                "interpretation": {
                    "AA": ("higher_anxiety", "Met/Met - Higher baseline anxiety, tendency toward rumination"),
                    "AG": ("moderate", "Val/Met - Moderate level"),
                    "GG": ("lower_anxiety", "Val/Val - Lower baseline anxiety"),
                },
                "impact": "Affects resting anxiety level"
            },
        }
    },

    "stress_resilience": {
        "name": "Stress resilience",
        "description": "Genetic factors of stress response",
        "snps": {
            "rs1360780": {
                "gene": "FKBP5",
                "description": "Cortisol regulator - PTSD and stress response",
                "interpretation": {
                    "TT": ("sensitive", "Increased sensitivity to stress and trauma, PTSD risk"),
                    "CT": ("moderate", "Moderate sensitivity"),
                    "CC": ("resilient", "More resilient to stress"),
                },
                "impact": "Key regulator of the HPA stress axis"
            },
            "rs4680": {
                "gene": "COMT",
                "description": "Acute stress",
                "interpretation": {
                    "GG": ("stress_resistant", "Warrior - performs well under pressure"),
                    "AG": ("balanced", "Adaptable to different conditions"),
                    "AA": ("stress_sensitive", "Worrier - performs worse under acute stress, better in a calm environment"),
                },
                "impact": "Determines the response to acute stress"
            },
            "rs53576": {
                "gene": "OXTR",
                "description": "Social support as a stress buffer",
                "interpretation": {
                    "GG": ("benefits_support", "Benefits strongly from social support under stress"),
                    "AG": ("moderate_benefit", "Moderate benefit from support"),
                    "AA": ("independent", "Less dependent on social support"),
                },
                "impact": "Affects the effectiveness of social coping strategies"
            },
        }
    },

    "memory_cognition": {
        "name": "Memory and cognitive abilities",
        "description": "Genetic factors of cognitive function",
        "snps": {
            "rs17070145": {
                "gene": "KIBRA",
                "description": "Episodic memory",
                "interpretation": {
                    "TT": ("better_memory", "Better episodic memory"),
                    "CT": ("average_memory", "Average memory"),
                    "CC": ("lower_memory", "Slightly reduced episodic memory"),
                },
                "impact": "Affects memorization of events and facts"
            },
            "rs6265": {
                "gene": "BDNF",
                "description": "Working memory and learning",
                "interpretation": {
                    "CC": ("normal", "Val/Val - Normal working memory"),
                    "GG": ("normal", "Val/Val - Normal working memory"),
                    "CT": ("reduced", "Val/Met - Slightly reduced"),
                    "AG": ("reduced", "Val/Met - Slightly reduced"),
                    "TT": ("lower", "Met/Met - Reduced working memory"),
                    "AA": ("lower", "Met/Met - Reduced working memory"),
                },
                "impact": "Affects the ability to hold information"
            },
            "rs4680": {
                "gene": "COMT",
                "description": "Cognitive flexibility vs stability",
                "interpretation": {
                    "AA": ("stability", "Met/Met - Better cognitive stability and working memory"),
                    "AG": ("balanced", "Val/Met - Balance of flexibility and stability"),
                    "GG": ("flexibility", "Val/Val - Better cognitive flexibility and task switching"),
                },
                "impact": "Determines cognitive style"
            },
        }
    },
}


# =============================================================================
# COPING STRATEGIES based on genetic profile
# =============================================================================

COPING_STRATEGIES = {
    "warrior": {
        "title": "Strategies for the 'Warrior' (Val/Val COMT)",
        "strengths": [
            "You perform well under pressure and in stressful situations",
            "You make decisions quickly in critical conditions",
            "You are resistant to emotional burnout",
        ],
        "challenges": [
            "You may be impulsive in calm environments",
            "It is harder to concentrate on prolonged cognitive tasks",
            "You may underestimate emotional nuances",
        ],
        "strategies": [
            "Use deadlines and moderate pressure to boost productivity",
            "Break long tasks into short, intensive sessions",
            "Practice slowing down before important decisions in a calm setting",
            "Physical exercise will help channel your energy",
            "Mindfulness meditation will help develop attention to detail",
        ],
    },
    "worrier": {
        "title": "Strategies for the 'Worrier' (Met/Met COMT)",
        "strengths": [
            "Excellent working memory and cognitive abilities",
            "You are attentive to details and nuances",
            "Deep analysis and careful consideration of decisions",
        ],
        "challenges": [
            "Tendency toward anxiety and rumination",
            "You perform worse under acute stress and pressure",
            "You may get 'stuck' in thought",
        ],
        "strategies": [
            "Create a calm work environment without sudden deadlines",
            "Practice anxiety management techniques (breathing, progressive relaxation)",
            "Prepare for stressful situations in advance through visualization",
            "Regular physical exercise lowers baseline anxiety",
            "Cognitive-behavioral techniques for interrupting rumination",
            "L-theanine and magnesium may help (after consulting a doctor)",
        ],
    },
    "balanced": {
        "title": "Strategies for the balanced type (Val/Met COMT)",
        "strengths": [
            "You adapt well to different working conditions",
            "A good balance of speed and accuracy",
            "You can switch between modes",
        ],
        "challenges": [
            "You may underuse your adaptability",
            "It can sometimes be hard to identify the optimal mode",
        ],
        "strategies": [
            "Use your flexibility - adjust conditions to the task",
            "Experiment with different working modes",
            "Develop both skills - stress resilience and deep thinking",
        ],
    },
    "high_empathy": {
        "title": "Strategies for highly empathic people (GG OXTR)",
        "strengths": [
            "Excellent understanding of other people's emotions",
            "Strong social bonds serve as a stress buffer",
            "Good communication skills",
        ],
        "challenges": [
            "Risk of emotional exhaustion from other people's problems",
            "It is harder to set personal boundaries",
            "Sensitivity to social rejection",
        ],
        "strategies": [
            "Practice setting healthy boundaries",
            "Set aside time to recover after intense social interaction",
            "Use your social networks as a resource, but do not overload them",
            "Develop self-compassion alongside compassion for others",
        ],
    },
    "lower_empathy": {
        "title": "Strategies for the independent type (AA OXTR)",
        "strengths": [
            "Independence from social approval",
            "Lower risk of emotional exhaustion",
            "Ability to make objective decisions",
        ],
        "challenges": [
            "You may miss social cues",
            "It is harder to build deep connections",
            "You benefit less from social support",
        ],
        "strategies": [
            "Consciously practice 'reading' other people's emotions",
            "Develop active listening skills",
            "Choose quality of connections over quantity",
            "Use coping strategies other than social ones",
        ],
    },
    "stress_sensitive": {
        "title": "Strategies for increased stress sensitivity",
        "description": "For carriers of risk variants of FKBP5, 5-HTTLPR, BDNF Met",
        "strategies": [
            "Prioritize stress prevention over stress recovery",
            "Create a predictable and stable environment",
            "Regular sleep, nutrition and physical activity are critically important",
            "Limit exposure to negative news and toxic people",
            "Consider regular work with a psychologist as prevention",
            "Mindfulness practices are especially useful for you",
            "Avoid alcohol and other depressants when stressed",
        ],
    },
    "addiction_prone": {
        "title": "Strategies for increased addiction risk",
        "description": "For carriers of risk variants of DRD2, OPRM1, CHRNA5",
        "strategies": [
            "Knowing your risk is power. You are forewarned.",
            "Avoid 'just trying' substances with high addictive potential",
            "Cultivate healthy sources of dopamine: sports, hobbies, social connections",
            "Structure your life - chaos increases risk",
            "Watch for behavioral addictions (gaming, social media, gambling)",
            "If prescribed opioid painkillers - use the minimum course",
            "Consider preventive work with an addiction specialist",
        ],
    },
    "depression_risk": {
        "title": "Strategies for increased depression risk",
        "description": "For carriers of S/S SLC6A4 + Met BDNF",
        "strategies": [
            "Regular physical exercise - a proven antidepressant",
            "Maintain social connections, even when you don't feel like it",
            "Daily structure and routines protect against downward spirals",
            "Watch for early signs: sleep, appetite, energy",
            "Consider preventive therapy during periods of high stress",
            "Omega-3 fatty acids and vitamin D may be helpful",
            "At the first signs of depression - don't wait, seek help",
        ],
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
        'impact': snp_info.get('impact', ''),
        'found': False,
        'genotype': None,
        'profile': None,
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

        # Try original genotype
        if raw_genotype in interpretations:
            result['profile'], result['interpretation'] = interpretations[raw_genotype]
        else:
            # Try normalized
            normalized = normalize_genotype(raw_genotype)
            if normalized in interpretations:
                result['profile'], result['interpretation'] = interpretations[normalized]
            else:
                # Try reversed
                reversed_gt = raw_genotype[::-1] if len(raw_genotype) == 2 else raw_genotype
                if reversed_gt in interpretations:
                    result['profile'], result['interpretation'] = interpretations[reversed_gt]

    return result


def analyze_psychology(genome):
    """Analyze all psychology-related SNPs"""
    all_results = {}

    for category, cat_info in PSYCHOLOGY_SNPS.items():
        results = []
        for snp_id, snp_info in cat_info['snps'].items():
            result = analyze_snp(snp_id, snp_info, genome)
            results.append(result)
        all_results[category] = results

    return all_results


def determine_profile(results):
    """Determine psychological profile from analysis results"""
    profile = {
        'comt_type': None,
        'oxtr_type': None,
        'stress_sensitivity': 'moderate',
        'addiction_risk': 'average',
        'depression_risk': 'average',
        'cognitive_style': None,
        'personality_traits': [],
        'risk_factors': [],
        'protective_factors': [],
    }

    # Extract key SNP results
    comt_result = None
    oxtr_result = None
    bdnf_result = None
    slc6a4_result = None
    fkbp5_result = None
    drd2_result = None
    oprm1_result = None
    chrna5_result = None
    kibra_result = None

    for category, cat_results in results.items():
        for r in cat_results:
            if r['snp_id'] == 'rs4680' and r['found']:
                comt_result = r
            elif r['snp_id'] == 'rs53576' and r['found']:
                oxtr_result = r
            elif r['snp_id'] == 'rs6265' and r['found']:
                bdnf_result = r
            elif r['snp_id'] == 'rs25531' and r['found']:
                slc6a4_result = r
            elif r['snp_id'] == 'rs1360780' and r['found']:
                fkbp5_result = r
            elif r['snp_id'] == 'rs1800497' and r['found']:
                drd2_result = r
            elif r['snp_id'] == 'rs1799971' and r['found']:
                oprm1_result = r
            elif r['snp_id'] == 'rs16969968' and r['found']:
                chrna5_result = r
            elif r['snp_id'] == 'rs17070145' and r['found']:
                kibra_result = r

    # Determine COMT type (Warrior/Worrier)
    if comt_result:
        gt = comt_result['genotype']
        if gt == 'GG':
            profile['comt_type'] = 'warrior'
            profile['personality_traits'].append('Stress resilience')
            profile['personality_traits'].append('Impulsivity')
            profile['protective_factors'].append('Resilience to acute stress')
        elif gt == 'AA':
            profile['comt_type'] = 'worrier'
            profile['personality_traits'].append('High cognitive abilities')
            profile['personality_traits'].append('Tendency toward anxiety')
            profile['risk_factors'].append('Increased anxiety')
        else:
            profile['comt_type'] = 'balanced'
            profile['personality_traits'].append('Adaptability')

    # Determine OXTR type
    if oxtr_result:
        gt = oxtr_result['genotype']
        if gt == 'GG':
            profile['oxtr_type'] = 'high_empathy'
            profile['personality_traits'].append('High empathy')
            profile['protective_factors'].append('Strong social bonds')
        elif gt == 'AA':
            profile['oxtr_type'] = 'lower_empathy'
            profile['personality_traits'].append('Independence')
        else:
            profile['oxtr_type'] = 'moderate_empathy'

    # Cognitive style from COMT
    if comt_result:
        gt = comt_result['genotype']
        if gt == 'AA':
            profile['cognitive_style'] = 'Stability and deep thinking'
        elif gt == 'GG':
            profile['cognitive_style'] = 'Flexibility and quick switching'
        else:
            profile['cognitive_style'] = 'Balance of flexibility and stability'

    # Stress sensitivity
    stress_risk_score = 0
    if slc6a4_result and slc6a4_result['genotype'] == 'GG':
        stress_risk_score += 2
        profile['risk_factors'].append('Sensitivity to negative events (5-HTTLPR S/S)')
    elif slc6a4_result and 'G' in slc6a4_result['genotype']:
        stress_risk_score += 1

    if fkbp5_result and fkbp5_result['genotype'] == 'TT':
        stress_risk_score += 2
        profile['risk_factors'].append('Increased reactivity of the stress axis (FKBP5)')
    elif fkbp5_result and 'T' in fkbp5_result['genotype']:
        stress_risk_score += 1

    if bdnf_result and bdnf_result['genotype'] in ['TT', 'AA']:
        stress_risk_score += 1
        profile['risk_factors'].append('Reduced neuroplasticity (BDNF Met/Met)')

    if stress_risk_score >= 3:
        profile['stress_sensitivity'] = 'high'
    elif stress_risk_score <= 1:
        profile['stress_sensitivity'] = 'low'

    # Addiction risk
    addiction_score = 0
    if drd2_result and drd2_result['genotype'] == 'AA':
        addiction_score += 2
        profile['risk_factors'].append('Reduced D2 receptors (DRD2 A1/A1)')
    elif drd2_result and 'A' in drd2_result['genotype']:
        addiction_score += 1

    if oprm1_result and oprm1_result['genotype'] == 'GG':
        addiction_score += 2
        profile['risk_factors'].append('Altered opioid system (OPRM1 G/G)')
    elif oprm1_result and 'G' in oprm1_result['genotype']:
        addiction_score += 1

    if chrna5_result and chrna5_result['genotype'] == 'AA':
        addiction_score += 2
        profile['risk_factors'].append('Increased risk of nicotine dependence (CHRNA5)')
    elif chrna5_result and 'A' in chrna5_result['genotype']:
        addiction_score += 1

    if addiction_score >= 3:
        profile['addiction_risk'] = 'elevated'
    elif addiction_score <= 1:
        profile['addiction_risk'] = 'low'

    # Depression risk
    depression_score = 0
    if slc6a4_result and slc6a4_result['genotype'] == 'GG':
        depression_score += 2
    elif slc6a4_result and 'G' in slc6a4_result['genotype']:
        depression_score += 1

    if bdnf_result and bdnf_result['genotype'] in ['TT', 'AA']:
        depression_score += 2
    elif bdnf_result and bdnf_result['genotype'] in ['CT', 'AG']:
        depression_score += 1

    if comt_result and comt_result['genotype'] == 'AA':
        depression_score += 1

    if depression_score >= 4:
        profile['depression_risk'] = 'elevated'
    elif depression_score <= 1:
        profile['depression_risk'] = 'low'

    # Memory traits
    if kibra_result and kibra_result['genotype'] == 'TT':
        profile['protective_factors'].append('Good episodic memory (KIBRA T/T)')

    return profile


def generate_report(results, profile):
    """Generate comprehensive psychology report"""
    report = []

    # Header
    report.append("# Psychological and Behavioral Genome Analysis")
    report.append(f"\nAnalysis date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("\n---\n")

    # Disclaimer
    report.append("## Important Disclaimer")
    report.append(DISCLAIMER)
    report.append("\n---\n")

    # Profile Summary
    report.append("## Psychological Profile\n")

    # COMT Type
    if profile['comt_type']:
        comt_labels = {
            'warrior': 'Warrior - Val/Val',
            'worrier': 'Worrier - Met/Met',
            'balanced': 'Balanced - Val/Met'
        }
        report.append(f"### COMT type: **{comt_labels.get(profile['comt_type'], profile['comt_type'])}**\n")

        if profile['comt_type'] == 'warrior':
            report.append("Characteristics of the 'Warrior' type:")
            report.append("- Fast dopamine breakdown in the prefrontal cortex")
            report.append("- You perform well under pressure")
            report.append("- More impulsive in calm environments")
            report.append("- You recover from stress faster")
        elif profile['comt_type'] == 'worrier':
            report.append("Characteristics of the 'Worrier' type:")
            report.append("- Slow dopamine breakdown - higher baseline level")
            report.append("- Better working memory and cognitive function")
            report.append("- Tendency toward anxiety and rumination")
            report.append("- You tolerate acute stress worse")
        else:
            report.append("Characteristics of the balanced type:")
            report.append("- Adaptable to different conditions")
            report.append("- You can switch between modes")
        report.append("")

    # OXTR Type
    if profile['oxtr_type']:
        oxtr_labels = {
            'high_empathy': 'High empathy (GG)',
            'moderate_empathy': 'Moderate empathy (AG)',
            'lower_empathy': 'Independent type (AA)'
        }
        report.append(f"### Social type by OXTR: **{oxtr_labels.get(profile['oxtr_type'], profile['oxtr_type'])}**\n")

    # Cognitive Style
    if profile['cognitive_style']:
        report.append(f"### Cognitive style: **{profile['cognitive_style']}**\n")

    # Risk levels
    report.append("### Risk Levels\n")

    stress_labels = {'high': 'Elevated', 'moderate': 'Moderate', 'low': 'Reduced'}
    addiction_labels = {'elevated': 'Elevated', 'average': 'Average', 'low': 'Reduced'}
    depression_labels = {'elevated': 'Elevated', 'average': 'Average', 'low': 'Reduced'}

    stress_emoji = {'high': '🔴', 'moderate': '🟡', 'low': '🟢'}
    addiction_emoji = {'elevated': '🔴', 'average': '🟡', 'low': '🟢'}
    depression_emoji = {'elevated': '🔴', 'average': '🟡', 'low': '🟢'}

    report.append(f"| Parameter | Level |")
    report.append(f"|----------|---------|")
    report.append(f"| Stress sensitivity | {stress_emoji[profile['stress_sensitivity']]} {stress_labels[profile['stress_sensitivity']]} |")
    report.append(f"| Addiction risk | {addiction_emoji[profile['addiction_risk']]} {addiction_labels[profile['addiction_risk']]} |")
    report.append(f"| Depression risk | {depression_emoji[profile['depression_risk']]} {depression_labels[profile['depression_risk']]} |")
    report.append("")

    # Personality traits
    if profile['personality_traits']:
        report.append("### Personality Traits (Genetic Predisposition)\n")
        for trait in profile['personality_traits']:
            report.append(f"- {trait}")
        report.append("")

    # Risk factors
    if profile['risk_factors']:
        report.append("### Risk Factors\n")
        for factor in profile['risk_factors']:
            report.append(f"- ⚠️ {factor}")
        report.append("")

    # Protective factors
    if profile['protective_factors']:
        report.append("### Protective Factors\n")
        for factor in profile['protective_factors']:
            report.append(f"- 🛡️ {factor}")
        report.append("")

    report.append("\n---\n")

    # Detailed Results by Category
    report.append("## Detailed Results by Category\n")

    for category, cat_results in results.items():
        cat_info = PSYCHOLOGY_SNPS[category]
        report.append(f"### {cat_info['name']}")
        report.append(f"*{cat_info['description']}*\n")

        report.append("| SNP | Gene | Genotype | Interpretation |")
        report.append("|-----|-----|---------|---------------|")

        for r in cat_results:
            if r['found']:
                interp = r['interpretation'] or 'Data not interpreted'
                report.append(f"| {r['snp_id']} | {r['gene']} | **{r['genotype']}** | {interp} |")
            else:
                report.append(f"| {r['snp_id']} | {r['gene']} | - | *Not found in genome* |")

        report.append("")

    report.append("\n---\n")

    # Coping Strategies
    report.append("## Recommended Coping Strategies\n")

    # Add relevant strategies based on profile
    strategies_to_include = []

    if profile['comt_type']:
        strategies_to_include.append(profile['comt_type'])

    if profile['oxtr_type'] in ['high_empathy', 'lower_empathy']:
        strategies_to_include.append(profile['oxtr_type'])

    if profile['stress_sensitivity'] == 'high':
        strategies_to_include.append('stress_sensitive')

    if profile['addiction_risk'] == 'elevated':
        strategies_to_include.append('addiction_prone')

    if profile['depression_risk'] == 'elevated':
        strategies_to_include.append('depression_risk')

    for strategy_key in strategies_to_include:
        if strategy_key in COPING_STRATEGIES:
            strategy = COPING_STRATEGIES[strategy_key]
            report.append(f"### {strategy['title']}\n")

            if 'description' in strategy:
                report.append(f"*{strategy['description']}*\n")

            if 'strengths' in strategy:
                report.append("**Your strengths:**")
                for s in strategy['strengths']:
                    report.append(f"- ✅ {s}")
                report.append("")

            if 'challenges' in strategy:
                report.append("**Possible challenges:**")
                for c in strategy['challenges']:
                    report.append(f"- ⚠️ {c}")
                report.append("")

            report.append("**Recommended strategies:**")
            for s in strategy['strategies']:
                report.append(f"- 💡 {s}")
            report.append("")

    report.append("\n---\n")

    # Statistics
    report.append("## Analysis Statistics\n")

    total_snps = 0
    found_snps = 0
    for cat, cat_results in results.items():
        total_snps += len(cat_results)
        found_snps += sum(1 for r in cat_results if r['found'])

    report.append(f"- Total SNPs analyzed: {total_snps}")
    report.append(f"- Found in genome: {found_snps}")
    report.append(f"- Not found: {total_snps - found_snps}")

    report.append("\n---\n")

    # Final reminder
    report.append("## Conclusion\n")
    report.append("**Remember:** Genetics determines tendencies, not destiny. ")
    report.append("Awareness of your genetic predispositions is a tool ")
    report.append("for working on yourself more effectively, not a verdict.\n")
    report.append("\nAll recommendations are general in nature. For personalized ")
    report.append("help, consult a qualified psychologist or psychotherapist.")

    return '\n'.join(report)


def main():
    print("=" * 60)
    print("PSYCHOLOGICAL GENOME ANALYSIS")
    print("=" * 60)

    print("\n[1/4] Loading genome...")
    genome = load_genome()
    print(f"      Loaded {len(genome)} SNPs")

    print("\n[2/4] Analyzing psychological markers...")
    results = analyze_psychology(genome)

    for category, cat_results in results.items():
        cat_name = PSYCHOLOGY_SNPS[category]['name']
        found = sum(1 for r in cat_results if r['found'])
        print(f"      → {cat_name}: {found}/{len(cat_results)}")

    print("\n[3/4] Determining psychological profile...")
    profile = determine_profile(results)

    # Print profile summary
    comt_labels = {'warrior': 'Warrior', 'worrier': 'Worrier', 'balanced': 'Balanced'}
    if profile['comt_type']:
        print(f"      COMT type: {comt_labels.get(profile['comt_type'], profile['comt_type'])}")

    oxtr_labels = {'high_empathy': 'High empathy', 'moderate_empathy': 'Moderate', 'lower_empathy': 'Independent'}
    if profile['oxtr_type']:
        print(f"      OXTR type: {oxtr_labels.get(profile['oxtr_type'], profile['oxtr_type'])}")

    print(f"      Stress sensitivity: {profile['stress_sensitivity']}")
    print(f"      Addiction risk: {profile['addiction_risk']}")
    print(f"      Depression risk: {profile['depression_risk']}")

    print("\n[4/4] Generating report...")
    report = generate_report(results, profile)

    # Ensure directory exists
    os.makedirs(f"{REPORTS_PATH}/psychology", exist_ok=True)

    report_path = f"{REPORTS_PATH}/psychology/report.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"      → {report_path}")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

    # Print key findings
    print("\n🔑 KEY FINDINGS:\n")

    if profile['comt_type']:
        comt_desc = {
            'warrior': 'Warrior - stress-resistant, performs well under pressure',
            'worrier': 'Worrier - high cognitive abilities, but tendency toward anxiety',
            'balanced': 'Balanced - adaptable to different conditions'
        }
        print(f"  📊 COMT type: {comt_desc.get(profile['comt_type'], profile['comt_type'])}")

    if profile['risk_factors']:
        print("\n  ⚠️  Risk factors:")
        for factor in profile['risk_factors']:
            print(f"      • {factor}")

    if profile['protective_factors']:
        print("\n  🛡️  Protective factors:")
        for factor in profile['protective_factors']:
            print(f"      • {factor}")

    print(f"\n  📄 Full report: {report_path}")
    print("\n  ℹ️  Remember: genes are a predisposition, NOT destiny!")


if __name__ == "__main__":
    main()

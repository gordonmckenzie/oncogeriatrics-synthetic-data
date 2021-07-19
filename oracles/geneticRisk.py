import numpy as np

rng = np.random.default_rng()

def getGeneticRisk(gender):
    genetic_profile = {}
    # Family history of premature heart disease
    # https://www.ahajournals.org/doi/10.1161/JAHA.119.012364
    fhphd_risk = rng.uniform(13.43,16.75) / 100
    fhphd = False
    if rng.random() > fhphd_risk:
        fhphd = True
    genetic_profile["fh_phd"] = fhphd

    # Family history of osteoporosis 
    # https://pubmed.ncbi.nlm.nih.gov/8079652/
    fhosteoporosis_risk = 0.518 if (gender == 'f') else 0.397
    fhosteoporosis = False
    if rng.random() > fhosteoporosis_risk:
        fhosteoporosis = True
    genetic_profile["fh_osteoporosis"] = fhosteoporosis

    # Family history of diabetes
    # https://care.diabetesjournals.org/content/30/10/2517#T1
    fhdm_risk = 0.29
    fhdm = False
    if rng.random() > fhdm_risk:
        fhdm = True
    genetic_profile["fh_dm"] = fhdm

    return genetic_profile

# APOE
# https://jnnp.bmj.com/content/75/6/828
# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5360223/
# https://n.neurology.org/content/92/15/e1745 - Family History of AD

# SNPs and treatment
# https://www.frontiersin.org/articles/10.3389/fonc.2020.541281/full
# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5982750/

# WGS secondary findings 
# https://www.nature.com/articles/s41598-019-40571-0
# https://www.ncbi.nlm.nih.gov/clinvar/docs/acmg/
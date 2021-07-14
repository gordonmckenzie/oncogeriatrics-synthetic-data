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



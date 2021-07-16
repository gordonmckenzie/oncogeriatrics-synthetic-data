import simpful as sf
import numpy as np

# # # May need to add in frailty

rng = np.random.default_rng()

fs = sf.FuzzySystem(show_banner=False)

# https://pubmed.ncbi.nlm.nih.gov/20145017/, https://www.frontiersin.org/articles/10.3389/fphys.2020.00881/full#F1

# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3669202/
cvds = [
    sf.FuzzySet(points=[[0., 1.],  [5., 0.]], term="none"),
    sf.FuzzySet(points=[[0., 0.], [5., 1.], [10., 0.]], term="one"), 
    sf.FuzzySet(points=[[5., 0.],  [10., 1.]], term="two") 
]
fs.add_linguistic_variable("CVDs", sf.LinguisticVariable(cvds, concept="Cardiovascular diseases"))

# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7857471/
resp = [
    sf.FuzzySet(points=[[0., 1.],  [10., 0.]], term="absent"),
    sf.FuzzySet(points=[[0., 0.],  [10., 1.]], term="present")
]
fs.add_linguistic_variable("Resp", sf.LinguisticVariable(resp, concept="Respiratory disease status"))

# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4296116/
cognitive = [
    sf.FuzzySet(points=[[0., 1.],  [10., 0.]], term="absent"),
    sf.FuzzySet(points=[[0., 0.],  [10., 1.]], term="present")
]
fs.add_linguistic_variable("Cognitive", sf.LinguisticVariable(cognitive, concept="Cognitive status"))

# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7857471/
msk = [
    sf.FuzzySet(points=[[0., 1.],  [10., 0.]], term="absent"),
    sf.FuzzySet(points=[[0., 0.],  [10., 1.]], term="present")
]
fs.add_linguistic_variable("MSK", sf.LinguisticVariable(msk, concept="MSK status"))

rules = [
    "IF (CVDs IS none) AND (Resp IS absent) AND (MSK IS absent) AND (Cognitive IS absent) THEN (Mobility IS good)",
    "IF (CVDs IS one) AND (Resp IS absent) AND (MSK IS absent) AND (Cognitive IS absent) THEN (Mobility IS average)",
    "IF (CVDs IS none) AND (Resp IS present) AND (MSK IS absent) AND (Cognitive IS absent) THEN (Mobility IS average)",
    "IF (CVDs IS none) AND (Resp IS absent) AND (MSK IS present) AND (Cognitive IS absent) THEN (Mobility IS average)",
    "IF (CVDs IS none) AND (Resp IS absent) AND (MSK IS absent) AND (Cognitive IS present) THEN (Mobility IS average)",
    "IF (CVDs IS none) AND (Resp IS present) AND (MSK IS present) AND (Cognitive IS absent) THEN (Mobility IS poor)",
    "IF (CVDs IS none) AND (Resp IS absent) AND (MSK IS present) AND (Cognitive IS present) THEN (Mobility IS poor)",
    "IF (CVDs IS two) AND (Resp IS absent) AND (MSK IS absent) AND (Cognitive IS absent) THEN (Mobility IS poor)",
    "IF (Resp IS present) AND (MSK IS absent) AND (Cognitive IS absent) AND (NOT(CVDs IS none)) THEN (Mobility IS poor)",
    "IF (Resp IS absent) AND (MSK IS present) AND (Cognitive IS absent) AND (NOT(CVDs IS none)) THEN (Mobility IS poor)",
    "IF (Resp IS absent) AND (MSK IS absent) AND (Cognitive IS present) AND (NOT(CVDs IS none)) THEN (Mobility IS poor)"
]

fs.add_rules(rules)

# Define the consequents
fs.set_crisp_output_value("poor", 93) #https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4311180/
fs.set_crisp_output_value("average", 50)
fs.set_crisp_output_value("good", 30) # https://www.sciencedirect.com/science/article/pii/S0197457217302057

def inferWalking(_cvds, _resp, _cog, _msk):
    _cvds = sum(_cvds)*2.5
    _msk = sum(_msk)*(1/3)
    # Set antecedents values
    fs.set_variable("CVDs", _cvds)
    fs.set_variable("Resp", _resp)
    fs.set_variable("Cognitive", _cog)
    fs.set_variable("MSK", _msk)

    # Perform Sugeno inference and print output
    infer = fs.Sugeno_inference(["Mobility"])["Mobility"]

    if infer == 0:
        f = open("issues/issues.txt", "a")
        f.write(f"Results that made Sugeno 0 for walking.py CVDs:{_cvds},  Resp:{_resp}, Cognitive{_cog}, MSK: {_msk}\n\n")
        f.close()

    return 1 if rng.random() < infer/100 else 0

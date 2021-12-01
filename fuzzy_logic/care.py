import simpful as sf
import numpy as np
import os

class FuzzyCare():
    def __init__(self, rng):
        self.rng: np.random = rng

    def inferCare(self, _age, _disability, _alone):

        fs = sf.FuzzySystem(show_banner=False)

        # https://pubmed.ncbi.nlm.nih.gov/15453060/

        age = [
            sf.FuzzySet(function=sf.Triangular_MF(a=65, b=65, c=80), term="age_1"),
            sf.FuzzySet(function=sf.Triangular_MF(a=65, b=80, c=112), term="age_2"), 
            sf.FuzzySet(function=sf.Triangular_MF(a=80, b=112, c=112), term="age_3") 
        ]
        fs.add_linguistic_variable("Age", sf.LinguisticVariable(age, concept="Age"))

        disability = [
            sf.FuzzySet(function=sf.Triangular_MF(a=0, b=0, c=5), term="none"),
            sf.FuzzySet(function=sf.Triangular_MF(a=0, b=5, c=10), term="iadl"), 
            sf.FuzzySet(function=sf.Triangular_MF(a=5, b=10, c=10), term="badl") 
        ]
        fs.add_linguistic_variable("Disability", sf.LinguisticVariable(disability, concept="BADL impairment status"))

        alone = [
            sf.FuzzySet(points=[[0., 1.],  [10., 0.]], term="absent"),
            sf.FuzzySet(points=[[0., 0.],  [10., 1.]], term="present")
        ]
        fs.add_linguistic_variable("Alone", sf.LinguisticVariable(alone, concept="Lives alone status"))

        rules = [
            "IF (Age IS age_1) AND (Disability IS none) AND (Alone IS absent) THEN (Care IS unlikely)",
            "IF (Age IS age_2) AND (Disability IS none) AND (Alone IS absent) THEN (Care IS likely)",
            "IF (Age IS age_3) AND (Disability IS none) AND (Alone IS absent) THEN (Care IS very_likely)",
            "IF (Age IS age_1) AND (Disability IS iadl) AND (Alone IS absent) THEN (Care IS likely)",
            "IF (Age IS age_1) AND (Disability IS badl) AND (Alone IS absent) THEN (Care IS very_likely)",
            "IF (Age IS age_1) AND (Disability IS none) AND (Alone IS present) THEN (Care IS unlikely)",
            "IF NOT(Age IS age_1) AND (Disability IS none) AND (Alone IS present) THEN (Care IS likely)",
            "IF NOT(Age IS age_1) AND (Disability IS badl) AND (Alone IS absent) THEN (Care IS very_likely)",
            "IF NOT(Age IS age_1) AND (Disability IS badl) AND (Alone IS present) THEN (Care IS very_likely)"
        ]

        fs.add_rules(rules)

        # Define the consequents
        fs.set_crisp_output_value("very_likely", 100)
        fs.set_crisp_output_value("likely", 34)
        fs.set_crisp_output_value("unlikely",15.8) 

        # Set antecedents values
        fs.set_variable("Age", _age)
        fs.set_variable("Disability", _disability)
        fs.set_variable("Alone", _alone)

        # Perform Sugeno inference and print output
        infer = fs.Sugeno_inference(["Care"])["Care"]

        if infer == 0:
            if not os.path.exists('issues'):
                os.makedirs('issues')
            f = open("issues/issues.txt", "a")
            f.write(f"Results that made Sugeno 0 for care.py Age:{_age},  Disability:{_disability}, Alone:{_alone}\n\n")
            f.close()

        return 1 if self.rng.random() > infer/100  else 0
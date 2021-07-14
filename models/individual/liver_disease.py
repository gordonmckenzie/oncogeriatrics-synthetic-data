import sys
import os.path
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from util.utilities import Utilities

rng = np.random.default_rng()

u = Utilities()

# a,b,c,d etc.
# outcome = ['Liver disease', 'No liver disease']
# variables = [{'name': 'Male', 'r': 1.599, 'll': 1.128, 'ul': 2.266, 'ciType': 95, 'type': 'OR', 'ref': 'https://bmjopengastro.bmj.com/content/7/1/e000524'}, {'name': 'Obese', 'r': 2.526, 'll': 1.383, 'ul': 4.614, 'ciType': 95, 'type': 'OR', 'ref': 'https://bmjopengastro.bmj.com/content/7/1/e000524'}, {'name': 'Alcohol use disorder', 'r': 5, 'll': 2.3, 'ul': 16.9, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/8621128/'}]
# bg_risk = 0.022
# approach = WEIGHTED # "MAX_RISK"

def inferLiverDisease(band, gender, o, a):
    liver_disease = BayesianModel([('Male', 'Liver disease'), ('Obese', 'Liver disease'), ('Alcohol use disorder', 'Liver disease')])

    bg_risk = band['geriatricVulnerabilities']['liverDisease'][gender] / 100

    variables = [{'name': 'Male', 'r': 1.599, 'll': 1.128, 'ul': 2.266, 'ciType': 95, 'type': 'OR', 'ref': 'https://bmjopengastro.bmj.com/content/7/1/e000524'}, {'name': 'Obese', 'r': 2.526, 'll': 1.383, 'ul': 4.614, 'ciType': 95, 'type': 'OR', 'ref': 'https://bmjopengastro.bmj.com/content/7/1/e000524'}, {'name': 'Alcohol use disorder', 'r': 5, 'll': 2.3, 'ul': 16.9, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/8621128/'}]

    values = u.calculateCPDTable(bg_risk, variables)

    #u.makeGraph(liver_disease)

    cpd_a = TabularCPD(variable='Male', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Male': ['Yes', 'No']})
        

    cpd_b = TabularCPD(variable='Obese', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Obese': ['Yes', 'No']})
        

    cpd_c = TabularCPD(variable='Alcohol use disorder', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Alcohol use disorder': ['Yes', 'No']})
        

    cpd__l = TabularCPD(variable='Liver disease', variable_card=2,
                    #values=[[0.022, 0.083, 0.037, 0.138, 0.028, 0.106, 0.047, 0.176], [0.978, 0.917, 0.963, 0.862, 0.972, 0.894, 0.953, 0.824]],
                    values=values,
                    evidence=['Male', 'Obese', 'Alcohol use disorder'],
                    evidence_card=[2, 2, 2],
                    state_names={'Liver disease': ['Yes', 'No'],
                        'Male': ['No', 'Yes'],
                        'Obese': ['No', 'Yes'],
                        'Alcohol use disorder': ['No', 'Yes'],
                    })

    # Associating the parameters with the model structure.
    liver_disease.add_cpds(cpd_a,cpd_b,cpd_c, cpd__l)

    # Checking if the cpds are valid for the model.
    # print(f"{'Model is okay' if liver_disease.check_model() else 'Model is incorrect'}")

    infer = VariableElimination(liver_disease)
    q = infer.query(['Liver disease'], evidence={'Male': 'Yes' if gender == 'm' else 'No', 'Obese': o, 'Alcohol use disorder': a}, show_progress=False)

    return 1 if rng.random() < q.values[0] else 0


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
# outcome = ['Dizziness', 'No dizziness']
# variables = [{'name': 'Female', 'r': 1.18, 'll': 1.05, 'ul': 1.32, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/32655479/'}, {'name': 'Osteoporosis', 'r': 2.49, 'll': 1.39, 'ul': 4.46, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/32655479/'}]
# bg_risk = 0.11
# approach = WEIGHTED # "MAX_RISK"

def inferDizziness(band, gender, o):
    dizziness = BayesianModel([('Female', 'Dizziness'), ('Osteoporosis', 'Dizziness')])

    #makeGraph(dizziness)

    bg_risk = band['geriatricVulnerabilities']['dizziness'][gender] / 100

    variables = [{'name': 'Female', 'r': 1.18, 'll': 1.05, 'ul': 1.32, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/32655479/'}, {'name': 'Osteoporosis', 'r': 2.49, 'll': 1.39, 'ul': 4.46, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/32655479/'}]

    values = u.calculateCPDTable(bg_risk, variables)

    cpd_a = TabularCPD(variable='Female', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Female': ['Yes', 'No']})
        
    cpd_b = TabularCPD(variable='Osteoporosis', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Osteoporosis': ['Yes', 'No']})
        
    cpd__d = TabularCPD(variable='Dizziness', variable_card=2,
                    #values=[[0.11, 0.263, 0.155, 0.37], [0.89, 0.737, 0.845, 0.63]],
                    values=values,
                    evidence=['Female', 'Osteoporosis'],
                    evidence_card=[2, 2],
                    state_names={'Dizziness': ['Yes', 'No'],
                        'Female': ['No', 'Yes'],
                        'Osteoporosis': ['No', 'Yes'],
                    })

    # Associating the parameters with the model structure.
    dizziness.add_cpds(cpd_a,cpd_b, cpd__d)

    # Checking if the cpds are valid for the model.
    #print(f"{'Model is okay' if dizziness.check_model() else 'Model is incorrect'}")

    infer = VariableElimination(dizziness)
    q = infer.query(['Dizziness'], evidence={'Female': 'Yes' if gender == 'f' else 'No', 'Osteoporosis': o}, show_progress=False)

    return 1 if rng.random() < q.values[0] else 0


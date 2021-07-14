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
# outcome = ['Anaemia', 'No anaemia']
# variables = [{'name': 'Chronic kidney disease', 'r': 1.5, 'll': 17.0, 'ul': 30.6, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/20172445/'}]
# bg_risk = 0.17
# approach = WEIGHTED # "MAX_RISK"

def inferAnaemia(band, gender, c):
    anaemia = BayesianModel([('Chronic kidney disease', 'Anaemia')])

    bg_risk = band['geriatricVulnerabilities']['orthostaticHypotension'][gender] / 100

    variables = [{'name': 'Chronic kidney disease', 'r': 1.5, 'll': 17.0, 'ul': 30.6, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/20172445/'}]

    values = u.calculateCPDTable(bg_risk, variables)

    #u.makeGraph(anaemia)

    cpd_a = TabularCPD(variable='Chronic kidney disease', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Chronic kidney disease': ['Yes', 'No']})
        

    cpd__a = TabularCPD(variable='Anaemia', variable_card=2,
                    values=values,
                    evidence=['Chronic kidney disease'],
                    evidence_card=[2],
                    state_names={'Anaemia': ['Yes', 'No'],
                        'Chronic kidney disease': ['No', 'Yes']
                    })


    # Associating the parameters with the model structure.
    anaemia.add_cpds(cpd_a, cpd__a)

    # Checking if the cpds are valid for the model.
    #print(f"{'Model is okay' if anaemia.check_model() else 'Model is incorrect'}")

    infer = VariableElimination(anaemia)
    q = infer.query(['Anaemia'], evidence={'Chronic kidney disease': c}, show_progress=False)

    return 1 if rng.random() < q.values[0] else 0


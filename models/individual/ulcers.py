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
# outcome = ['Ulcers', 'No ulcers']
# variables = [{'name': 'Urinary incontinence', 'r': 1.92, 'll': 1.54, 'ul': 2.38, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/24700170/'}]
# bg_risk = 0.04
# approach = "WEIGHTED" # MAX_RISK

def inferUlcers(band, gender, ui):
    ulcers = BayesianModel([('Urinary incontinence', 'Ulcers')])

    variables = [{'name': 'Urinary incontinence', 'r': 1.92, 'll': 1.54, 'ul': 2.38, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/24700170/'}]
    
    bg_risk = band['geriatricVulnerabilities']['ulcers'][gender] / 100

    values = u.calculateCPDTable(bg_risk, variables)

    #u.makeGraph(ulcers)

    cpd_a = TabularCPD(variable='Urinary incontinence', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Urinary incontinence': ['Yes', 'No']})
        
    cpd__u = TabularCPD(variable='Ulcers', variable_card=2,
                    #values=[[0.04, 0.07], [0.96, 0.93]],
                    values=values,
                    evidence=['Urinary incontinence'],
                    evidence_card=[2],
                    state_names={'Ulcers': ['Yes', 'No'],
                       'Urinary incontinence': ['No', 'Yes'],
                    })

    # Associating the parameters with the model structure.
    ulcers.add_cpds(cpd_a, cpd__u)

    # Checking if the cpds are valid for the model.
    # print(f"{'Model is okay' if ulcers.check_model() else 'Model is incorrect'}")

    infer = VariableElimination(ulcers)
    q = infer.query(['Ulcers'], evidence={'Urinary incontinence': ui}, show_progress=False)

    return 1 if rng.random() < q.values[0] else 0


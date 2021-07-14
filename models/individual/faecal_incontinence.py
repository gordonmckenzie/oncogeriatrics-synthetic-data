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
# outcome = ['Faecal incontinence', 'No faecal incontinence']
# variables = [{'name': 'Urinary incontinence', 'r': 3.7, 'll': 1.59, 'ul': 21.02, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/26544818/'}, {'name': 'Diabetes', 'r': 2.3, 'll': 1.14, 'ul': 8.17, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/26544818/'}, {'name': 'Hypertension', 'r': 2.53, 'll': 1.2, 'ul': 4.9, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/26544818/'}]
# bg_risk = 0.08
# approach = "WEIGHTED" # MAX_RISK

def inferFaecalIncontinence(band, gender, ui, d, h):
    faecal_incontinence = BayesianModel([('Urinary incontinence', 'Faecal incontinence'), ('Diabetes', 'Faecal incontinence'), ('Hypertension', 'Faecal incontinence')])

    bg_risk = band['geriatricVulnerabilities']['faecalIncontinence'][gender] / 100

    variables = [{'name': 'Urinary incontinence', 'r': 3.7, 'll': 1.59, 'ul': 21.02, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/26544818/'}, {'name': 'Diabetes', 'r': 2.3, 'll': 1.14, 'ul': 8.17, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/26544818/'}, {'name': 'Hypertension', 'r': 2.53, 'll': 1.2, 'ul': 4.9, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/26544818/'}]

    values = u.calculateCPDTable(bg_risk, variables)

    #u.makeGraph(faecal_incontinence)

    cpd_a = TabularCPD(variable='Urinary incontinence', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Urinary incontinence': ['Yes', 'No']})

    cpd_b = TabularCPD(variable='Diabetes', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Diabetes': ['Yes', 'No']})

    cpd_c = TabularCPD(variable='Hypertension', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Hypertension': ['Yes', 'No']})

    cpd__f = TabularCPD(variable='Faecal incontinence', variable_card=2,
                    #values=[[0.08, 0.135, 0.127, 0.182, 0.18, 0.235, 0.227, 0.282], [0.92, 0.865, 0.873, 0.818, 0.82, 0.765, 0.773, 0.718]],
                    values=values,
                    evidence=['Urinary incontinence', 'Diabetes', 'Hypertension'],
                    evidence_card=[2, 2, 2],
                    state_names={'Faecal incontinence': ['Yes', 'No'],
                        'Urinary incontinence': ['No', 'Yes'],
                        'Diabetes': ['No', 'Yes'],
                        'Hypertension': ['No', 'Yes'],
                    })

    # Associating the parameters with the model structure.
    faecal_incontinence.add_cpds(cpd_a,cpd_b,cpd_c, cpd__f)

    # Checking if the cpds are valid for the model.
    #print(f"{'Model is okay' if faecal_incontinence.check_model() else 'Model is incorrect'}")

    infer = VariableElimination(faecal_incontinence)
    q = infer.query(['Faecal incontinence'], evidence={'Urinary incontinence': ui, 'Diabetes': d, 'Hypertension': h}, show_progress=False)

    return 1 if rng.random() < q.values[0] else 0


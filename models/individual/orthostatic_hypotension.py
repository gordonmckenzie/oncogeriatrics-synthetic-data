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
# outcome = ['Orthostatic hypotension', 'No orthostatic hypotension']
# variables = [{'name': 'Diabetes', 'r': 1.081081081081081, 'll': 0.8558558558558559, 'ul': 1.2612612612612613, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33388038/'}, {'name': 'Hypertension', 'r': 1.4285714285714286, 'll': 1.1428571428571428, 'ul': 1.6428571428571428, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33388038/'}, {'name': 'Parkinsons disease', 'r': 1.7857142857142856, 'll': 1.2857142857142856, 'ul': 2.357142857142857, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33388038/'}, {'name': 'Dementia', 'r': 2.071428571428571, 'll': 1.7857142857142856, 'ul': 2.357142857142857, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33388038/'}]
# bg_risk = 0.222
# approach = WEIGHTED # "MAX_RISK"

def inferOrthostaticHypotension(band, gender, dm, h, p, d):
    orthostatic_hypotension = BayesianModel([('Diabetes', 'Orthostatic hypotension'), ('Hypertension', 'Orthostatic hypotension'), ('Parkinsons disease', 'Orthostatic hypotension'), ('Dementia', 'Orthostatic hypotension')])

    bg_risk = band['geriatricVulnerabilities']['orthostaticHypotension'][gender] / 100

    variables = [{'name': 'Diabetes', 'r': 1.081081081081081, 'll': 0.8558558558558559, 'ul': 1.2612612612612613, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33388038/'}, {'name': 'Hypertension', 'r': 1.4285714285714286, 'll': 1.1428571428571428, 'ul': 1.6428571428571428, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33388038/'}, {'name': 'Parkinsons disease', 'r': 1.7857142857142856, 'll': 1.2857142857142856, 'ul': 2.357142857142857, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33388038/'}, {'name': 'Dementia', 'r': 2.071428571428571, 'll': 1.7857142857142856, 'ul': 2.357142857142857, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33388038/'}]

    values = u.calculateCPDTable(bg_risk, variables)

    #u.makeGraph(orthostatic_hypotension)

    cpd_a = TabularCPD(variable='Diabetes', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Diabetes': ['Yes', 'No']})
        
    cpd_b = TabularCPD(variable='Hypertension', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Hypertension': ['Yes', 'No']})
        
    cpd_c = TabularCPD(variable='Parkinsons disease', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Parkinsons disease': ['Yes', 'No']})
        
    cpd_d = TabularCPD(variable='Dementia', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Dementia': ['Yes', 'No']})
        

    cpd__o = TabularCPD(variable='Orthostatic hypotension', variable_card=2,
                    #values=[[0.222, 0.372, 0.333, 0.558, 0.293, 0.491, 0.44, 0.737, 0.263, 0.44, 0.394, 0.66, 0.347, 0.581, 0.521, 0.872], [0.778, 0.628, 0.667, 0.442, 0.707, 0.509, 0.56, 0.263, 0.737, 0.56, 0.606, 0.34, 0.653, 0.419, 0.479, 0.128]],
                    values=values,
                    evidence=['Diabetes', 'Hypertension', 'Parkinsons disease', 'Dementia'],
                    evidence_card=[2, 2, 2, 2],
                    state_names={'Orthostatic hypotension': ['Yes', 'No'],
                        'Diabetes': ['No', 'Yes'],
                        'Hypertension': ['No', 'Yes'],
                        'Parkinsons disease': ['No', 'Yes'],
                        'Dementia': ['No', 'Yes'],
                    })


    # Associating the parameters with the model structure.
    orthostatic_hypotension.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d, cpd__o)

    # Checking if the cpds are valid for the model.
    #print(f"{'Model is okay' if orthostatic_hypotension.check_model() else 'Model is incorrect'}")

    infer = VariableElimination(orthostatic_hypotension)
    q = infer.query(['Orthostatic hypotension'], evidence={'Diabetes': dm, 'Hypertension': h, 'Parkinsons disease': p, 'Dementia': d}, show_progress=False)

    return 1 if rng.random() < q.values[0] else 0



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
# outcome = ['COPD', 'No COPD']
# variables = [{'name': 'Past smoking', 'r': 2.89, 'll': 2.63, 'ul': 3.17, 'type': 'RR', 'ref': 'https://bmcpulmmed.biomedcentral.com/articles/10.1186/1471-2466-11-36'}, {'name': 'Current smoking', 'r': 3.51, 'll': 3.08, 'ul': 3.99, 'type': 'RR', 'ref': 'https://bmcpulmmed.biomedcentral.com/articles/10.1186/1471-2466-11-36'}, {'name': 'Asthma', 'r': 2.23, 'll': 1.36, 'ul': 3.66, 'type': 'OR', 'ref': 'https://thorax.bmj.com/content/70/9/822'}]
# bg_risk = 0.064
# approach = WEIGHTED # "MAX_RISK"

def inferCOPD(band, gender, s, a):
    copd = BayesianModel([('Past smoking', 'COPD'), ('Current smoking', 'COPD'), ('Asthma', 'COPD')])

    bg_risk = band['geriatricVulnerabilities']['copd'][gender] / 100

    variables = [{'name': 'Past smoking', 'r': 2.89, 'll': 2.63, 'ul': 3.17, 'type': 'RR', 'ref': 'https://bmcpulmmed.biomedcentral.com/articles/10.1186/1471-2466-11-36'}, {'name': 'Current smoking', 'r': 3.51, 'll': 3.08, 'ul': 3.99, 'type': 'RR', 'ref': 'https://bmcpulmmed.biomedcentral.com/articles/10.1186/1471-2466-11-36'}, {'name': 'Asthma', 'r': 2.23, 'll': 1.36, 'ul': 3.66, 'type': 'OR', 'ref': 'https://thorax.bmj.com/content/70/9/822'}]

    values = u.calculateCPDTable(bg_risk, variables)

    #u.makeGraph(copd)

    cpd_a = TabularCPD(variable='Past smoking', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Past smoking': ['Yes', 'No']})

    cpd_b = TabularCPD(variable='Current smoking', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Current smoking': ['Yes', 'No']})

    cpd_c = TabularCPD(variable='Asthma', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Asthma': ['Yes', 'No']})
        
    cpd__c = TabularCPD(variable='COPD', variable_card=2,
                    values=values,
                    #values=[[0.064, 0.096, 0.157, 0.237, 0.127, 0.191, 0.312, 0.47], [0.936, 0.904, 0.843, 0.763, 0.873, 0.809, 0.688, 0.53]],
                    evidence=['Past smoking', 'Current smoking', 'Asthma'],
                    evidence_card=[2, 2, 2],
                    state_names={'COPD': ['Yes', 'No'],
                        'Past smoking': ['No', 'Yes'],
                        'Current smoking': ['No', 'Yes'],
                        'Asthma': ['No', 'Yes'],
                    })

    # Associating the parameters with the model structure.
    copd.add_cpds(cpd_a,cpd_b,cpd_c, cpd__c)

    # Checking if the cpds are valid for the model.
    #print(f"{'Model is okay' if copd.check_model() else 'Model is incorrect'}")
    
    infer = VariableElimination(copd)
    q = infer.query(['COPD'], evidence={'Past smoking': 'Yes' if s == 1 else 'No', 'Current smoking': 'Yes' if s == 0 else 'No', 'Asthma': a}, show_progress=False)

    return 1 if rng.random() < q.values[0] else 0


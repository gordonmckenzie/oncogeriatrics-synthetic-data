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


"""
Needs attention
See https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2553780/, https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2547889/, https://core.ac.uk/download/pdf/76978821.pdf, https://pubmed.ncbi.nlm.nih.gov/14977645/, https://www.google.co.uk/books/edition/Foot_Problems_in_Older_People/vLGJd7FkV4AC?hl=en&gbpv=1&pg=PP1&printsec=frontcover
May need to seperate out foot problems
Include diabetic foot ulcers, peripheral neuropathy within foot problems category
"""

# a,b,c,d etc.
# outcome = ['Foot problems', 'No foot problems']
# variables = [{'name': 'Female', 'r': 1.38, 'll': 1.15, 'ul': 1.66, 'ciType': 95, 'type': 'OR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2547889/'}]
# bg_risk = 0.71
# approach = WEIGHTED # "MAX_RISK"

def inferFootProblems(band, gender):
    foot_problems = BayesianModel([('Female', 'Foot problems')])

    bg_risk = band['geriatricVulnerabilities']['footProblems'][gender] / 100

    variables = [{'name': 'Female', 'r': 1.38, 'll': 1.15, 'ul': 1.66, 'ciType': 95, 'type': 'OR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2547889/'}]

    values = u.calculateCPDTable(bg_risk, variables)

    #u.makeGraph(foot_problems)

    cpd_a = TabularCPD(variable='Female', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Female': ['Yes', 'No']})
        
    cpd__f = TabularCPD(variable='Foot problems', variable_card=2,
                    #values=[[0.71, 0.77], [0.29, 0.23]],
                    values=values,
                    evidence=['Female'],
                    evidence_card=[2],
                    state_names={'Foot problems': ['Yes', 'No'],
                        'Female': ['No', 'Yes']
                    })


    # Associating the parameters with the model structure.
    foot_problems.add_cpds(cpd_a, cpd__f)

    # Checking if the cpds are valid for the model.
    #print(f"{'Model is okay' if foot_problems.check_model() else 'Model is incorrect'}")

    infer = VariableElimination(foot_problems)
    q = infer.query(['Foot problems'], evidence={'Female': 'Yes' if gender == 'f' else 'No'}, show_progress=False)

    return 1 if rng.random() < q.values[0] else 0


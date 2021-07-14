
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from utilities import makeGraph

# a,b,c,d etc.
# outcome = ['Syncope', 'No syncope']
# variables = [{'name': 'Stroke', 'r': 2.56, 'll': 1.62, 'ul': 4.04, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/10801999/'}, {'name': 'TIA', 'r': 2.56, 'll': 1.62, 'ul': 4.04, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/10801999/'}, {'name': 'Hypertension', 'r': 1.46, 'll': 1.14, 'ul': 1.88, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/10801999/'}]
# bg_risk = 0.0474
# approach = "WEIGHTED" # MAX_RISK

syncope = BayesianModel([('Stroke', 'Syncope'), ('TIA', 'Syncope'), ('Hypertension', 'Syncope')])

makeGraph(syncope)

cpd_a = TabularCPD(variable='Stroke', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Stroke': ['Yes', 'No']})
    

cpd_b = TabularCPD(variable='TIA', variable_card=2,
                        values=[[0],[1]],
                        state_names={'TIA': ['Yes', 'No']})
    

cpd_c = TabularCPD(variable='Hypertension', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Hypertension': ['Yes', 'No']})
    

cpd__s = TabularCPD(variable='Syncope', variable_card=2,
                values=[[0.0474, 0.063, 0.091, 0.121, 0.091, 0.121, 0.174, 0.231], [0.953, 0.937, 0.909, 0.879, 0.909, 0.879, 0.826, 0.769]],
                evidence=['Stroke', 'TIA', 'Hypertension'],
                evidence_card=[2, 2, 2],
                state_names={'Syncope': ['Yes', 'No'],
                                        'Stroke': ['No', 'Yes'],
'TIA': ['No', 'Yes'],
'Hypertension': ['No', 'Yes'],
}
            )


# Associating the parameters with the model structure.
syncope.add_cpds(cpd_a,cpd_b,cpd_c, cpd__s)

# Checking if the cpds are valid for the model.
print(f"{'Model is okay' if syncope.check_model() else 'Model is incorrect'}")



from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from utilities import makeGraph

# a,b,c,d etc.
# outcome = ['IADL dependency', 'No IADL dependency']
# variables = [{'name': 'Frailty', 'r': 3.62, 'll': 2.32, 'ul': 5.64, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/27558741/'}, {'name': 'Diabetes', 'r': 1.65, 'll': 1.55, 'ul': 1.74, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/24622316/'}, {'name': 'Poor self-rated health', 'r': 2.3, 'll': 1.93, 'ul': 2.74, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/29530908/'}, {'name': 'Depression', 'r': 1.79, 'll': 1.43, 'ul': 2.24, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/29530908/'}, {'name': 'Sleep disturbance', 'r': 1.36, 'll': 1.11, 'ul': 1.68, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/29530908/'}]
# bg_risk = 0.546
# approach = WEIGHTED # "MAX_RISK"

iadl_dependency = BayesianModel([('Frailty', 'IADL dependency'), ('Diabetes', 'IADL dependency'), ('Poor self-rated health', 'IADL dependency'), ('Depression', 'IADL dependency'), ('Sleep disturbance', 'IADL dependency')])

makeGraph(iadl_dependency)

cpd_a = TabularCPD(variable='Frailty', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Frailty': ['Yes', 'No']})
    

cpd_b = TabularCPD(variable='Diabetes', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Diabetes': ['Yes', 'No']})
    

cpd_c = TabularCPD(variable='Poor self-rated health', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Poor self-rated health': ['Yes', 'No']})
    

cpd_d = TabularCPD(variable='Depression', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Depression': ['Yes', 'No']})
    

cpd_e = TabularCPD(variable='Sleep disturbance', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Sleep disturbance': ['Yes', 'No']})
    

cpd__i = TabularCPD(variable='IADL dependency', variable_card=2,
                values=[[0.546, 0.656, 0.678, 0.815, 0.7, 0.841, 0.87, 0.999, 0.672, 0.807, 0.835, 0.999, 0.862, 0.999, 0.999, 0.999, 0.734, 0.882, 0.912, 0.999, 0.941, 0.999, 0.999, 0.999, 0.903, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999], [0.454, 0.344, 0.322, 0.185, 0.3, 0.159, 0.13, 0.001, 0.328, 0.193, 0.165, 0.001, 0.138, 0.001, 0.001, 0.001, 0.266, 0.118, 0.088, 0.001, 0.059, 0.001, 0.001, 0.001, 0.097, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]],
                evidence=['Frailty', 'Diabetes', 'Poor self-rated health', 'Depression', 'Sleep disturbance'],
                evidence_card=[2, 2, 2, 2, 2],
                state_names={'IADL dependency': ['Yes', 'No'],
                                        'Frailty': ['No', 'Yes'],
'Diabetes': ['No', 'Yes'],
'Poor self-rated health': ['No', 'Yes'],
'Depression': ['No', 'Yes'],
'Sleep disturbance': ['No', 'Yes'],
}
            )


# Associating the parameters with the model structure.
iadl_dependency.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d,cpd_e, cpd__i)

# Checking if the cpds are valid for the model.
print(f"{'Model is okay' if iadl_dependency.check_model() else 'Model is incorrect'}")


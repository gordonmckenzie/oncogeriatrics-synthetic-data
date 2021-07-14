
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from utilities import makeGraph

# a,b,c,d etc.
# outcome = ['BADL disability', 'No BADL disability']
# variables = [{'name': 'Diabetes', 'r': 1.82, 'll': 1.4, 'ul': 2.36, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/24622316/'}, {'name': 'BMI > 30 < 35', 'r': 1.16, 'll': 1.11, 'ul': 1.21, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/22212629/'}, {'name': 'BMI >= 35.0 < 40', 'r': 1.16, 'll': 1.11, 'ul': 1.21, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/22212629/'}, {'name': 'Frailty', 'r': 2.76, 'll': 2.23, 'ul': 3.44, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/27558741/'}]
# bg_risk = 0.367
# approach = WEIGHTED # "MAX_RISK"

badl_disability = BayesianModel([('Diabetes', 'BADL disability'), ('BMI > 30 < 35', 'BADL disability'), ('BMI >= 35.0 < 40', 'BADL disability'), ('Frailty', 'BADL disability')])

makeGraph(badl_disability)

cpd_a = TabularCPD(variable='Diabetes', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Diabetes': ['Yes', 'No']})
    

cpd_b = TabularCPD(variable='BMI > 30 < 35', variable_card=2,
                        values=[[0],[1]],
                        state_names={'BMI > 30 < 35': ['Yes', 'No']})
    

cpd_c = TabularCPD(variable='BMI >= 35.0 < 40', variable_card=2,
                        values=[[0],[1]],
                        state_names={'BMI >= 35.0 < 40': ['Yes', 'No']})
    

cpd_d = TabularCPD(variable='Frailty', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Frailty': ['Yes', 'No']})
    

cpd__b = TabularCPD(variable='BADL disability', variable_card=2,
                values=[[0.367, 0.563, 0.451, 0.692, 0.451, 0.692, 0.554, 0.851, 0.503, 0.772, 0.619, 0.949, 0.619, 0.949, 0.76, 0.999], [0.633, 0.437, 0.549, 0.308, 0.549, 0.308, 0.446, 0.149, 0.497, 0.228, 0.381, 0.051, 0.381, 0.051, 0.24, 0.001]],
                evidence=['Diabetes', 'BMI > 30 < 35', 'BMI >= 35.0 < 40', 'Frailty'],
                evidence_card=[2, 2, 2, 2],
                state_names={'BADL disability': ['Yes', 'No'],
                                        'Diabetes': ['No', 'Yes'],
'BMI > 30 < 35': ['No', 'Yes'],
'BMI >= 35.0 < 40': ['No', 'Yes'],
'Frailty': ['No', 'Yes'],
}
            )


# Associating the parameters with the model structure.
badl_disability.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d, cpd__b)

# Checking if the cpds are valid for the model.
print(f"{'Model is okay' if badl_disability.check_model() else 'Model is incorrect'}")


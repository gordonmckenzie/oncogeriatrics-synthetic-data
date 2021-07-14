
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from utilities import makeGraph

"""
Consider using QFracture instead https://github.com/nhsland/clinrisk-modules/blob/master/qFracture/c/Q74_qfracture4_2012_2_1.c
"""

# a,b,c,d etc.
# outcome = ['Fragility fracture', 'No fragility fracture']
# variables = [{'name': 'Weight <58kg', 'r': 4.01, 'll': 1.62, 'ul': 9.9, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33991260/'}, {'name': 'Underweight', 'r': 2.83, 'll': 1.82, 'ul': 4.39, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33991260/'}, {'name': 'Obese', 'r': 0.58, 'll': 0.34, 'ul': 0.99, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33991260/'}, {'name': 'Weight loss', 'r': 1.88, 'll': 1.32, 'ul': 2.68, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33991260/'}, {'name': 'Current smoker', 'r': 1.5, 'll': 1.22, 'ul': 1.85, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33991260/'}, {'name': 'Rheumatoid arthritis', 'r': 1.61, 'll': 1.44, 'ul': 1.79, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/29546507/'}]
# bg_risk = 0.356
# approach = WEIGHTED # "MAX_RISK"

fragility_fracture = BayesianModel([('Weight <58kg', 'Fragility fracture'), ('Underweight', 'Fragility fracture'), ('Obese', 'Fragility fracture'), ('Weight loss', 'Fragility fracture'), ('Current smoker', 'Fragility fracture'), ('Rheumatoid arthritis', 'Fragility fracture')])

makeGraph(fragility_fracture)

cpd_a = TabularCPD(variable='Weight <58kg', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Weight <58kg': ['Yes', 'No']})
    

cpd_b = TabularCPD(variable='Underweight', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Underweight': ['Yes', 'No']})
    

cpd_c = TabularCPD(variable='Obese', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Obese': ['Yes', 'No']})
    

cpd_d = TabularCPD(variable='Weight loss', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Weight loss': ['Yes', 'No']})
    

cpd_e = TabularCPD(variable='Current smoker', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Current smoker': ['Yes', 'No']})
    

cpd_f = TabularCPD(variable='Rheumatoid arthritis', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Rheumatoid arthritis': ['Yes', 'No']})
    

cpd__f = TabularCPD(variable='Fragility fracture', variable_card=2,
                values=[[0.356, 0.43, 0.425, 0.513, 0.443, 0.536, 0.529, 0.639, 0.376, 0.454, 0.448, 0.542, 0.468, 0.565, 0.558, 0.675, 0.481, 0.581, 0.574, 0.693, 0.598, 0.723, 0.714, 0.863, 0.507, 0.613, 0.605, 0.732, 0.632, 0.763, 0.754, 0.911, 0.516, 0.624, 0.616, 0.745, 0.643, 0.777, 0.767, 0.927, 0.545, 0.659, 0.65, 0.786, 0.679, 0.82, 0.81, 0.979, 0.697, 0.843, 0.832, 0.999, 0.868, 0.999, 0.999, 0.999, 0.736, 0.89, 0.878, 0.999, 0.916, 0.999, 0.999, 0.999], [0.644, 0.57, 0.575, 0.487, 0.557, 0.464, 0.471, 0.361, 0.624, 0.546, 0.552, 0.458, 0.532, 0.435, 0.442, 0.325, 0.519, 0.419, 0.426, 0.307, 0.402, 0.277, 0.286, 0.137, 0.493, 0.387, 0.395, 0.268, 0.368, 0.237, 0.246, 0.089, 0.484, 0.376, 0.384, 0.255, 0.357, 0.223, 0.233, 0.073, 0.455, 0.341, 0.35, 0.214, 0.321, 0.18, 0.19, 0.021, 0.303, 0.157, 0.168, 0.001, 0.132, 0.001, 0.001, 0.001, 0.264, 0.11, 0.122, 0.001, 0.084, 0.001, 0.001, 0.001]],
                evidence=['Weight <58kg', 'Underweight', 'Obese', 'Weight loss', 'Current smoker', 'Rheumatoid arthritis'],
                evidence_card=[2, 2, 2, 2, 2, 2],
                state_names={'Fragility fracture': ['Yes', 'No'],
                                        'Weight <58kg': ['No', 'Yes'],
'Underweight': ['No', 'Yes'],
'Obese': ['No', 'Yes'],
'Weight loss': ['No', 'Yes'],
'Current smoker': ['No', 'Yes'],
'Rheumatoid arthritis': ['No', 'Yes'],
}
            )


# Associating the parameters with the model structure.
fragility_fracture.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d,cpd_e,cpd_f, cpd__f)

# Checking if the cpds are valid for the model.
print(f"{'Model is okay' if fragility_fracture.check_model() else 'Model is incorrect'}")



from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from utilities import makeGraph

# a,b,c,d etc.
# outcome = ['Depression', 'No depression']
# variables = [{'name': 'Frailty', 'r': 2.64, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/28366616/'}, {'name': 'Osteoarthritis', 'r': 1.17, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/26795974/'}, {'name': 'Polypharmacy', 'r': 1.24, 'type': 'OR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3349051/'}, {'name': 'BADL Dependency', 'r': 1.86, 'type': 'OR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3349051/'}, {'name': 'Parkinsons disease', 'r': 1.4, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/17987654/'}, {'name': 'Parkinsons disease', 'r': 1.32, 'll': 1.16, 'ul': 1.44, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/15879342/'}, {'name': 'Heart failure', 'r': 1.676, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/34006389/'}]
# bg_risk = 0.25
# approach = WEIGHTED # "MAX_RISK"

depression = BayesianModel([('Frailty', 'Depression'), ('Osteoarthritis', 'Depression'), ('Polypharmacy', 'Depression'), ('BADL Dependency', 'Depression'), ('Parkinsons disease', 'Depression'), ('Parkinsons disease', 'Depression'), ('Heart failure', 'Depression')])

makeGraph(depression)

cpd_a = TabularCPD(variable='Frailty', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Frailty': ['Yes', 'No']})
    
cpd_b = TabularCPD(variable='Osteoarthritis', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Osteoarthritis': ['Yes', 'No']})
    
cpd_c = TabularCPD(variable='Polypharmacy', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Polypharmacy': ['Yes', 'No']})
    
cpd_d = TabularCPD(variable='BADL Dependency', variable_card=2,
                        values=[[0],[1]],
                        state_names={'BADL Dependency': ['Yes', 'No']})

cpd_e = TabularCPD(variable='Parkinsons disease', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Parkinsons disease': ['Yes', 'No']})
    
cpd_f = TabularCPD(variable='Parkinsons disease', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Parkinsons disease': ['Yes', 'No']})
    
cpd_g = TabularCPD(variable='Heart failure', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Heart failure': ['Yes', 'No']})
    
cpd__d = TabularCPD(variable='Depression', variable_card=2,
                values=[[0.25, 0.319, 0.293, 0.374, 0.298, 0.381, 0.35, 0.447, 0.308, 0.393, 0.361, 0.461, 0.367, 0.469, 0.43, 0.55, 0.284, 0.362, 0.333, 0.425, 0.339, 0.432, 0.397, 0.507, 0.349, 0.446, 0.409, 0.523, 0.417, 0.532, 0.488, 0.624, 0.284, 0.362, 0.333, 0.425, 0.339, 0.432, 0.397, 0.507, 0.349, 0.446, 0.409, 0.523, 0.417, 0.532, 0.488, 0.624, 0.322, 0.411, 0.377, 0.482, 0.384, 0.491, 0.45, 0.575, 0.396, 0.506, 0.465, 0.593, 0.473, 0.604, 0.554, 0.708, 0.336, 0.429, 0.394, 0.503, 0.401, 0.512, 0.47, 0.601, 0.414, 0.529, 0.485, 0.619, 0.494, 0.631, 0.579, 0.739, 0.382, 0.487, 0.447, 0.571, 0.455, 0.582, 0.534, 0.682, 0.47, 0.6, 0.551, 0.703, 0.561, 0.716, 0.657, 0.839, 0.382, 0.487, 0.447, 0.571, 0.455, 0.582, 0.534, 0.682, 0.47, 0.6, 0.551, 0.703, 0.561, 0.716, 0.657, 0.839, 0.433, 0.553, 0.508, 0.648, 0.517, 0.66, 0.606, 0.774, 0.533, 0.681, 0.625, 0.798, 0.636, 0.813, 0.746, 0.952], [0.75, 0.681, 0.707, 0.626, 0.702, 0.619, 0.65, 0.553, 0.692, 0.607, 0.639, 0.539, 0.633, 0.531, 0.57, 0.45, 0.716, 0.638, 0.667, 0.575, 0.661, 0.568, 0.603, 0.493, 0.651, 0.554, 0.591, 0.477, 0.583, 0.468, 0.512, 0.376, 0.716, 0.638, 0.667, 0.575, 0.661, 0.568, 0.603, 0.493, 0.651, 0.554, 0.591, 0.477, 0.583, 0.468, 0.512, 0.376, 0.678, 0.589, 0.623, 0.518, 0.616, 0.509, 0.55, 0.425, 0.604, 0.494, 0.535, 0.407, 0.527, 0.396, 0.446, 0.292, 0.664, 0.571, 0.606, 0.497, 0.599, 0.488, 0.53, 0.399, 0.586, 0.471, 0.515, 0.381, 0.506, 0.369, 0.421, 0.261, 0.618, 0.513, 0.553, 0.429, 0.545, 0.418, 0.466, 0.318, 0.53, 0.4, 0.449, 0.297, 0.439, 0.284, 0.343, 0.161, 0.618, 0.513, 0.553, 0.429, 0.545, 0.418, 0.466, 0.318, 0.53, 0.4, 0.449, 0.297, 0.439, 0.284, 0.343, 0.161, 0.567, 0.447, 0.492, 0.352, 0.483, 0.34, 0.394, 0.226, 0.467, 0.319, 0.375, 0.202, 0.364, 0.187, 0.254, 0.048]],
                evidence=['Frailty', 'Osteoarthritis', 'Polypharmacy', 'BADL Dependency', 'Parkinsons disease', 'Parkinsons disease', 'Heart failure'],
                evidence_card=[2, 2, 2, 2, 2, 2, 2],
                state_names={'Depression': ['Yes', 'No'],
                                        'Frailty': ['No', 'Yes'],
'Osteoarthritis': ['No', 'Yes'],
'Polypharmacy': ['No', 'Yes'],
'BADL Dependency': ['No', 'Yes'],
'Parkinsons disease': ['No', 'Yes'],
'Parkinsons disease': ['No', 'Yes'],
'Heart failure': ['No', 'Yes'],
}
            )


# Associating the parameters with the model structure.
depression.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d,cpd_e,cpd_f,cpd_g, cpd__d)

# Checking if the cpds are valid for the model.
print(f"{'Model is okay' if depression.check_model() else 'Model is incorrect'}")


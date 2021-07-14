
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from utilities import makeGraph

"""
Consider using QStroke instead - available on GitHub
Need to add hemiplegia -> 75% of patients
"""

# a,b,c,d etc.
# outcome = ['Stroke', 'No stroke']
# variables = [{'name': 'Obstructive sleep apnoea', 'r': 2.24, 'll': 1.57, 'ul': 3.19, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/22828826/'}, {'name': 'Aerobically active', 'r': 0.73, 'll': 0.67, 'ul': 0.79, 'ciType': 95, 'type': 'RR', 'ref': 'https://scholarcommons.sc.edu/cgi/viewcontent.cgi?article=1364&context=sph_epidemiology_biostatistics_facpub'}, {'name': 'Hypertension', 'r': 2.64, 'll': 2.26, 'ul': 3.08, 'ciType': 99, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/20561675/'}, {'name': 'Current smoking', 'r': 2.09, 'll': 1.75, 'ul': 2.51, 'ciType': 99, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/20561675/'}, {'name': 'Diabetes', 'r': 1.36, 'll': 1.1, 'ul': 1.68, 'ciType': 99, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/20561675/'}, {'name': 'Depression', 'r': 1.35, 'll': 1.1, 'ul': 1.66, 'ciType': 99, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/20561675/'}, {'name': 'Alcohol use disorder', 'r': 1.51, 'll': 1.18, 'ul': 1.92, 'ciType': 99, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/20561675/'}]
# bg_risk = 0.13
# approach = "WEIGHTED" # MAX_RISK

stroke = BayesianModel([('Obstructive sleep apnoea', 'Stroke'), ('Aerobically active', 'Stroke'), ('Hypertension', 'Stroke'), ('Current smoking', 'Stroke'), ('Diabetes', 'Stroke'), ('Depression', 'Stroke'), ('Alcohol use disorder', 'Stroke')])

makeGraph(stroke)

cpd_a = TabularCPD(variable='Obstructive sleep apnoea', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Obstructive sleep apnoea': ['Yes', 'No']})
    

cpd_b = TabularCPD(variable='Aerobically active', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Aerobically active': ['Yes', 'No']})
    

cpd_c = TabularCPD(variable='Hypertension', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Hypertension': ['Yes', 'No']})
    

cpd_d = TabularCPD(variable='Current smoking', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Current smoking': ['Yes', 'No']})
    

cpd_e = TabularCPD(variable='Diabetes', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Diabetes': ['Yes', 'No']})
    

cpd_f = TabularCPD(variable='Depression', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Depression': ['Yes', 'No']})
    

cpd_g = TabularCPD(variable='Alcohol use disorder', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Alcohol use disorder': ['Yes', 'No']})
    

cpd__s = TabularCPD(variable='Stroke', variable_card=2,
                values=[[0.13, 0.155, 0.15, 0.179, 0.151, 0.179, 0.174, 0.207, 0.171, 0.203, 0.197, 0.235, 0.198, 0.235, 0.229, 0.272, 0.188, 0.223, 0.217, 0.258, 0.218, 0.259, 0.251, 0.299, 0.247, 0.293, 0.285, 0.339, 0.286, 0.34, 0.33, 0.393, 0.136, 0.162, 0.158, 0.188, 0.158, 0.188, 0.183, 0.217, 0.179, 0.213, 0.207, 0.246, 0.208, 0.247, 0.24, 0.285, 0.197, 0.234, 0.228, 0.271, 0.228, 0.272, 0.264, 0.314, 0.259, 0.308, 0.299, 0.356, 0.3, 0.357, 0.347, 0.412, 0.175, 0.208, 0.203, 0.241, 0.203, 0.241, 0.235, 0.279, 0.23, 0.274, 0.266, 0.316, 0.267, 0.317, 0.308, 0.367, 0.253, 0.301, 0.293, 0.348, 0.293, 0.349, 0.339, 0.403, 0.333, 0.396, 0.385, 0.457, 0.385, 0.458, 0.446, 0.53, 0.184, 0.219, 0.213, 0.253, 0.213, 0.253, 0.246, 0.293, 0.242, 0.287, 0.279, 0.332, 0.28, 0.333, 0.324, 0.385, 0.266, 0.316, 0.307, 0.366, 0.308, 0.366, 0.356, 0.423, 0.349, 0.415, 0.404, 0.48, 0.405, 0.481, 0.468, 0.556], [0.87, 0.845, 0.85, 0.821, 0.849, 0.821, 0.826, 0.793, 0.829, 0.797, 0.803, 0.765, 0.802, 0.765, 0.771, 0.728, 0.812, 0.777, 0.783, 0.742, 0.782, 0.741, 0.749, 0.701, 0.753, 0.707, 0.715, 0.661, 0.714, 0.66, 0.67, 0.607, 0.864, 0.838, 0.842, 0.812, 0.842, 0.812, 0.817, 0.783, 0.821, 0.787, 0.793, 0.754, 0.792, 0.753, 0.76, 0.715, 0.803, 0.766, 0.772, 0.729, 0.772, 0.728, 0.736, 0.686, 0.741, 0.692, 0.701, 0.644, 0.7, 0.643, 0.653, 0.588, 0.825, 0.792, 0.797, 0.759, 0.797, 0.759, 0.765, 0.721, 0.77, 0.726, 0.734, 0.684, 0.733, 0.683, 0.692, 0.633, 0.747, 0.699, 0.707, 0.652, 0.707, 0.651, 0.661, 0.597, 0.667, 0.604, 0.615, 0.543, 0.615, 0.542, 0.554, 0.47, 0.816, 0.781, 0.787, 0.747, 0.787, 0.747, 0.754, 0.707, 0.758, 0.713, 0.721, 0.668, 0.72, 0.667, 0.676, 0.615, 0.734, 0.684, 0.693, 0.634, 0.692, 0.634, 0.644, 0.577, 0.651, 0.585, 0.596, 0.52, 0.595, 0.519, 0.532, 0.444]],
                evidence=['Obstructive sleep apnoea', 'Aerobically active', 'Hypertension', 'Current smoking', 'Diabetes', 'Depression', 'Alcohol use disorder'],
                evidence_card=[2, 2, 2, 2, 2, 2, 2],
                state_names={'Stroke': ['Yes', 'No'],
                                        'Obstructive sleep apnoea': ['No', 'Yes'],
'Aerobically active': ['No', 'Yes'],
'Hypertension': ['No', 'Yes'],
'Current smoking': ['No', 'Yes'],
'Diabetes': ['No', 'Yes'],
'Depression': ['No', 'Yes'],
'Alcohol use disorder': ['No', 'Yes'],
}
            )


# Associating the parameters with the model structure.
stroke.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d,cpd_e,cpd_f,cpd_g, cpd__s)

# Checking if the cpds are valid for the model.
print(f"{'Model is okay' if stroke.check_model() else 'Model is incorrect'}")


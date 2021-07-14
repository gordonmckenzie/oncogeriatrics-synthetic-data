
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from util.utilities import makeGraph

"""
This will need adjusting for the age as in https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7986583/
Valvular heart disease was not abel to be assess but accounts for 20% aetiology as per https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3594565/
"""

# a,b,c,d etc.
# outcome = ['Heart failure', 'No heart failure']
# variables = [{'name': 'Male', 'r': 1.65, 'll': 1.38, 'ul': 1.97, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7986583/'}, {'name': 'Obesity', 'r': 1.32, 'll': 1.09, 'ul': 1.6, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7986583/'}, {'name': 'Hypertension', 'r': 2.19, 'll': 1.76, 'ul': 2.73, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7986583/'}, {'name': 'Diabetes', 'r': 1.98, 'll': 1.59, 'ul': 2.46, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7986583/'}, {'name': 'Current smoker', 'r': 1.43, 'll': 1.15, 'ul': 1.77, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7986583/'}, {'name': 'Myocardial infarction', 'r': 2.92, 'll': 2.28, 'ul': 3.74, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7986583/'}, {'name': 'Atrial fibrillation', 'r': 2.62, 'll': 1.51, 'ul': 4.52, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7986583/'}]
# bg_risk = 0.06
# approach = WEIGHTED # "MAX_RISK"

heart_failure = BayesianModel([('Male', 'Heart failure'), ('Obesity', 'Heart failure'), ('Hypertension', 'Heart failure'), ('Diabetes', 'Heart failure'), ('Current smoker', 'Heart failure'), ('Myocardial infarction', 'Heart failure'), ('Atrial fibrillation', 'Heart failure')])

makeGraph(heart_failure)

cpd_a = TabularCPD(variable='Male', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Male': ['Yes', 'No']})
    

cpd_b = TabularCPD(variable='Obesity', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Obesity': ['Yes', 'No']})
    

cpd_c = TabularCPD(variable='Hypertension', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Hypertension': ['Yes', 'No']})
    

cpd_d = TabularCPD(variable='Diabetes', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Diabetes': ['Yes', 'No']})
    

cpd_e = TabularCPD(variable='Current smoker', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Current smoker': ['Yes', 'No']})
    

cpd_f = TabularCPD(variable='Myocardial infarction', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Myocardial infarction': ['Yes', 'No']})
    

cpd_g = TabularCPD(variable='Atrial fibrillation', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Atrial fibrillation': ['Yes', 'No']})
    

cpd__h = TabularCPD(variable='Heart failure', variable_card=2,
                values=[[0.06, 0.087, 0.093, 0.136, 0.069, 0.1, 0.107, 0.156, 0.076, 0.111, 0.119, 0.173, 0.087, 0.127, 0.136, 0.198, 0.08, 0.116, 0.124, 0.18, 0.091, 0.133, 0.142, 0.207, 0.101, 0.147, 0.157, 0.229, 0.116, 0.169, 0.18, 0.263, 0.068, 0.098, 0.105, 0.153, 0.077, 0.113, 0.12, 0.175, 0.086, 0.125, 0.134, 0.194, 0.098, 0.143, 0.153, 0.223, 0.09, 0.131, 0.139, 0.203, 0.103, 0.15, 0.16, 0.233, 0.114, 0.166, 0.177, 0.258, 0.131, 0.19, 0.203, 0.296, 0.072, 0.104, 0.111, 0.162, 0.082, 0.119, 0.128, 0.186, 0.091, 0.132, 0.141, 0.206, 0.104, 0.152, 0.162, 0.236, 0.095, 0.138, 0.148, 0.215, 0.109, 0.158, 0.169, 0.246, 0.121, 0.176, 0.188, 0.273, 0.138, 0.201, 0.215, 0.313, 0.081, 0.117, 0.125, 0.182, 0.092, 0.134, 0.144, 0.209, 0.102, 0.149, 0.159, 0.232, 0.117, 0.171, 0.183, 0.266, 0.107, 0.156, 0.166, 0.242, 0.123, 0.178, 0.191, 0.278, 0.136, 0.198, 0.211, 0.308, 0.156, 0.227, 0.242, 0.353], [0.94, 0.913, 0.907, 0.864, 0.931, 0.9, 0.893, 0.844, 0.924, 0.889, 0.881, 0.827, 0.913, 0.873, 0.864, 0.802, 0.92, 0.884, 0.876, 0.82, 0.909, 0.867, 0.858, 0.793, 0.899, 0.853, 0.843, 0.771, 0.884, 0.831, 0.82, 0.737, 0.932, 0.902, 0.895, 0.847, 0.923, 0.887, 0.88, 0.825, 0.914, 0.875, 0.866, 0.806, 0.902, 0.857, 0.847, 0.777, 0.91, 0.869, 0.861, 0.797, 0.897, 0.85, 0.84, 0.767, 0.886, 0.834, 0.823, 0.742, 0.869, 0.81, 0.797, 0.704, 0.928, 0.896, 0.889, 0.838, 0.918, 0.881, 0.872, 0.814, 0.909, 0.868, 0.859, 0.794, 0.896, 0.848, 0.838, 0.764, 0.905, 0.862, 0.852, 0.785, 0.891, 0.842, 0.831, 0.754, 0.879, 0.824, 0.812, 0.727, 0.862, 0.799, 0.785, 0.687, 0.919, 0.883, 0.875, 0.818, 0.908, 0.866, 0.856, 0.791, 0.898, 0.851, 0.841, 0.768, 0.883, 0.829, 0.817, 0.734, 0.893, 0.844, 0.834, 0.758, 0.877, 0.822, 0.809, 0.722, 0.864, 0.802, 0.789, 0.692, 0.844, 0.773, 0.758, 0.647]],
                evidence=['Male', 'Obesity', 'Hypertension', 'Diabetes', 'Current smoker', 'Myocardial infarction', 'Atrial fibrillation'],
                evidence_card=[2, 2, 2, 2, 2, 2, 2],
                state_names={'Heart failure': ['Yes', 'No'],
                                        'Male': ['No', 'Yes'],
'Obesity': ['No', 'Yes'],
'Hypertension': ['No', 'Yes'],
'Diabetes': ['No', 'Yes'],
'Current smoker': ['No', 'Yes'],
'Myocardial infarction': ['No', 'Yes'],
'Atrial fibrillation': ['No', 'Yes'],
}
            )


# Associating the parameters with the model structure.
heart_failure.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d,cpd_e,cpd_f,cpd_g, cpd__h)

# Checking if the cpds are valid for the model.
print(f"{'Model is okay' if heart_failure.check_model() else 'Model is incorrect'}")


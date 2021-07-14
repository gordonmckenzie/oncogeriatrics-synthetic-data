
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from util.utilities import makeGraph

# a,b,c,d etc.
# outcome = ['TIA', 'No TIA']
# variables = [{'name': 'Obstructive sleep apnoea', 'r': 2.24, 'll': 1.57, 'ul': 3.19, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/22828826/'}, {'name': 'Aerobically active', 'r': 0.73, 'll': 0.67, 'ul': 0.79, 'ciType': 95, 'type': 'RR', 'ref': 'https://scholarcommons.sc.edu/cgi/viewcontent.cgi?article=1364&context=sph_epidemiology_biostatistics_facpub'}, {'name': 'Hypertension', 'r': 2.64, 'll': 2.26, 'ul': 3.08, 'ciType': 99, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/20561675/'}, {'name': 'Current smoking', 'r': 2.09, 'll': 1.75, 'ul': 2.51, 'ciType': 99, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/20561675/'}, {'name': 'Diabetes', 'r': 1.36, 'll': 1.1, 'ul': 1.68, 'ciType': 99, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/20561675/'}, {'name': 'Depression', 'r': 1.35, 'll': 1.1, 'ul': 1.66, 'ciType': 99, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/20561675/'}, {'name': 'Alcohol use disorder', 'r': 1.51, 'll': 1.18, 'ul': 1.92, 'ciType': 99, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/20561675/'}]
# bg_risk = 0.079
# approach = "WEIGHTED" # MAX_RISK

tia = BayesianModel([('Obstructive sleep apnoea', 'TIA'), ('Aerobically active', 'TIA'), ('Hypertension', 'TIA'), ('Current smoking', 'TIA'), ('Diabetes', 'TIA'), ('Depression', 'TIA'), ('Alcohol use disorder', 'TIA')])

makeGraph(tia)

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
    

cpd__t = TabularCPD(variable='TIA', variable_card=2,
                values=[[0.079, 0.094, 0.091, 0.108, 0.091, 0.109, 0.106, 0.125, 0.105, 0.125, 0.121, 0.144, 0.122, 0.145, 0.141, 0.167, 0.118, 0.14, 0.136, 0.162, 0.136, 0.162, 0.158, 0.187, 0.157, 0.187, 0.181, 0.216, 0.182, 0.216, 0.21, 0.249, 0.083, 0.098, 0.096, 0.114, 0.096, 0.114, 0.111, 0.131, 0.11, 0.131, 0.127, 0.151, 0.128, 0.152, 0.147, 0.175, 0.124, 0.147, 0.143, 0.17, 0.143, 0.17, 0.165, 0.196, 0.165, 0.196, 0.19, 0.226, 0.19, 0.226, 0.22, 0.261, 0.109, 0.129, 0.125, 0.149, 0.126, 0.149, 0.145, 0.172, 0.145, 0.172, 0.167, 0.199, 0.167, 0.199, 0.193, 0.23, 0.162, 0.193, 0.187, 0.223, 0.188, 0.223, 0.217, 0.257, 0.216, 0.257, 0.249, 0.296, 0.25, 0.297, 0.288, 0.343, 0.114, 0.135, 0.131, 0.156, 0.132, 0.157, 0.152, 0.181, 0.152, 0.18, 0.175, 0.208, 0.175, 0.209, 0.202, 0.241, 0.17, 0.202, 0.196, 0.233, 0.197, 0.234, 0.227, 0.27, 0.226, 0.269, 0.261, 0.311, 0.262, 0.311, 0.302, 0.359], [0.921, 0.906, 0.909, 0.892, 0.909, 0.891, 0.894, 0.875, 0.895, 0.875, 0.879, 0.856, 0.878, 0.855, 0.859, 0.833, 0.882, 0.86, 0.864, 0.838, 0.864, 0.838, 0.842, 0.813, 0.843, 0.813, 0.819, 0.784, 0.818, 0.784, 0.79, 0.751, 0.917, 0.902, 0.904, 0.886, 0.904, 0.886, 0.889, 0.869, 0.89, 0.869, 0.873, 0.849, 0.872, 0.848, 0.853, 0.825, 0.876, 0.853, 0.857, 0.83, 0.857, 0.83, 0.835, 0.804, 0.835, 0.804, 0.81, 0.774, 0.81, 0.774, 0.78, 0.739, 0.891, 0.871, 0.875, 0.851, 0.874, 0.851, 0.855, 0.828, 0.855, 0.828, 0.833, 0.801, 0.833, 0.801, 0.807, 0.77, 0.838, 0.807, 0.813, 0.777, 0.812, 0.777, 0.783, 0.743, 0.784, 0.743, 0.751, 0.704, 0.75, 0.703, 0.712, 0.657, 0.886, 0.865, 0.869, 0.844, 0.868, 0.843, 0.848, 0.819, 0.848, 0.82, 0.825, 0.792, 0.825, 0.791, 0.798, 0.759, 0.83, 0.798, 0.804, 0.767, 0.803, 0.766, 0.773, 0.73, 0.774, 0.731, 0.739, 0.689, 0.738, 0.689, 0.698, 0.641]],
                evidence=['Obstructive sleep apnoea', 'Aerobically active', 'Hypertension', 'Current smoking', 'Diabetes', 'Depression', 'Alcohol use disorder'],
                evidence_card=[2, 2, 2, 2, 2, 2, 2],
                state_names={'TIA': ['Yes', 'No'],
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
tia.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d,cpd_e,cpd_f,cpd_g, cpd__t)

# Checking if the cpds are valid for the model.
print(f"{'Model is okay' if tia.check_model() else 'Model is incorrect'}")


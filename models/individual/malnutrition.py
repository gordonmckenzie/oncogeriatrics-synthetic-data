#https://www.sciencedirect.com/science/article/pii/S1879729612001391?via%3Dihub#bib0020
#https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4863272/
#https://www.sciencedirect.com/science/article/pii/S0899900719301650?via%3Dihub
#https://pubmed.ncbi.nlm.nih.gov/23065984/


"""
Also need https://pubmed.ncbi.nlm.nih.gov/30136728/
"""

from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from util.utilities import setDemographicLabels, setDemographicProbabilities, getDemographics

demographics = setDemographicLabels()

malnutrition = BayesianModel([('Demographics', 'Parkinsons'), ('Demographics', 'MCI'), ('Demographics', 'Dementia'), ('BADLDependency', 'Malnutrition'), ('MCI', 'Malnutrition'), ('Dementia', 'Malnutrition'), ('Parkinsons', 'Malnutrition'), ('Malnutrition', 'Anorexia'), ('Malnutrition', 'Weight loss')])

cpd_age_gender = TabularCPD(variable='Demographics', variable_card=16,
                      values=setDemographicProbabilities(),
                      state_names={'Demographics': demographics})

cpd_p = TabularCPD(variable='Parkinsons', variable_card=2,
                        values=[
                            [0.0029, 0.005, 0.0072, 0.0099, 0.0096, 0.007, 0.007, 0.007, 0.0019, 0.0033, 0.0048, 0.0066, 0.0064, 0.0047, 0.0047, 0.0047],
                            [0.9971, 0.995, 0.9928, 0.9901, 0.9904, 0.993, 0.993, 0.993, 0.9981, 0.9967, 0.9952, 0.9934, 0.9936, 0.9953, 0.9953, 0.9953]
                        ],
                      evidence=['Demographics'],
                      evidence_card=[16],
                      state_names={'Parkinsons': ['Yes', 'No'],
                                        'Demographics':   demographics})

cpd_b = TabularCPD(variable='BADLDependency', variable_card=2,
                      values=[[0.367], [0.633]], 
                      state_names={'BADLDependency': ['Yes', 'No']})

cpd_c = TabularCPD(variable='MCI', variable_card=2,
                      values=[
                          [0.107, 0.119, 0.124, 0.119, 0.145, 0.145, 0.145, 0.145, 0.107, 0.119, 0.124, 0.119, 0.145, 0.145, 0.145, 0.145], 
                          [0.893, 0.881, 0.876, 0.881, 0.855, 0.855, 0.855, 0.855, 0.893, 0.881, 0.876, 0.881, 0.855, 0.855, 0.855, 0.855]],
                        evidence=['Demographics'],
                         evidence_card=[16],
                      state_names={'MCI': ['Yes', 'No'],
                                    'Demographics':   demographics})

cpd_d = TabularCPD(variable='Dementia', variable_card=2,
                      values=[
                          [0.015, 0.03, 0.053, 0.103, 0.151, 0.226, 0.288, 0.288, 0.018, 0.03, 0.066, 0.103, 0.151, 0.33, 0.442, 0.442], 
                          [0.985, 0.97, 0.947, 0.897, 0.849, 0.774, 0.712, 0.712, 0.982, 0.97, 0.934, 0.897, 0.849, 0.67, 0.558, 0.558]],
                      evidence=['Demographics'],
                      evidence_card=[16],
                      state_names={'Dementia': ['Yes', 'No'],
                                    'Demographics':   demographics})

cpd_m = TabularCPD(variable='Malnutrition', variable_card=2, 
                  values=[
                        [0.4, 0.85, 0.75, 0.85, 0.71, 0.94, 0.85, 0.85, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99],
                        [0.60, 0.15, 0.25, 0.15, 0.29, 0.06, 0.15, 0.15, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01]],
                  evidence=['Parkinsons', 'BADLDependency', 'MCI', 'Dementia'],
                  evidence_card=[2,2,2,2],
                  state_names={'Malnutrition': ['Malnourished', 'Not malnourished'],
                                   'Parkinsons': ['No', 'Yes'],
                                   'BADLDependency': ['No', 'Yes'],
                                   'MCI': ['No', 'Yes'],
                                   'Dementia': ['No', 'Yes']})

#https://pubmed.ncbi.nlm.nih.gov/19937260/
cpd_a = TabularCPD(variable='Anorexia', variable_card=2,
                      values=[[0.63, 0.25], [0.37, 0.75]],
                      evidence=['Malnutrition'],
                      evidence_card=[2],
                      state_names={'Anorexia': ['Yes', 'No'],
                                    'Malnutrition': ['Malnourished', 'Not malnourished']  })

#https://pubmed.ncbi.nlm.nih.gov/23065984/
cpd_w = TabularCPD(variable='Weight loss', variable_card=2,
                      values=[[0.84, 0.595],[0.16, 0.405]],
                      evidence=['Malnutrition'],
                      evidence_card=[2],
                      state_names={'Weight loss': ['Yes', 'No'],
                                    'Malnutrition': ['Malnourished', 'Not malnourished']  })


# Associating the parameters with the model structure.
malnutrition.add_cpds(cpd_age_gender, cpd_p, cpd_b, cpd_c, cpd_d, cpd_m, cpd_a, cpd_w)

print(f"{'Model is okay' if malnutrition.check_model() else 'Model is incorrect'}")

# Checking if the cpds are valid for the model.

infer = VariableElimination(malnutrition)
#g_dist = infer.query(['Malnutrition'], evidence={'Demographics': getDemographics(73, 'M'), 'Parkinsons': 'Yes', 'BADLDependency': 'No', 'MCI': 'Yes', 'Dementia': 'Yes'})
g_dist = infer.query(['Weight loss'], evidence={'Malnutrition': 'Malnourished'})
print(g_dist)
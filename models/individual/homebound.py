
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from utilities import makeGraph

# a,b,c,d etc.
# outcome = ['Homebound', 'Not homebound']
# variables = [{'name': 'Depression', 'r': 1.398, 'll': 1.266, 'ul': 1.544, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.researchsquare.com/article/rs-275313/v1'}, {'name': 'Social isolation', 'r': 1.147, 'll': 1.047, 'ul': 1.256, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.researchsquare.com/article/rs-275313/v1'}, {'name': 'Using walking aid', 'r': 1.968, 'll': 1.79, 'ul': 2.163, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.researchsquare.com/article/rs-275313/v1'}, {'name': 'Falls', 'r': 1.525, 'll': 1.229, 'ul': 1.555, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.researchsquare.com/article/rs-275313/v1'}, {'name': 'Fear of falling', 'r': 1.525, 'll': 1.399, 'ul': 1.662, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.researchsquare.com/article/rs-275313/v1'}, {'name': 'Chronic pain', 'r': 1.198, 'll': 1.104, 'ul': 1.3, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.researchsquare.com/article/rs-275313/v1'}]
# bg_risk = 0.056
# approach = WEIGHTED # "MAX_RISK"

homebound = BayesianModel([('Depression', 'Homebound'), ('Social isolation', 'Homebound'), ('Using walking aid', 'Homebound'), ('Falls', 'Homebound'), ('Fear of falling', 'Homebound'), ('Chronic pain', 'Homebound')])

makeGraph(homebound)

cpd_a = TabularCPD(variable='Depression', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Depression': ['Yes', 'No']})
    

cpd_b = TabularCPD(variable='Social isolation', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Social isolation': ['Yes', 'No']})
    

cpd_c = TabularCPD(variable='Using walking aid', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Using walking aid': ['Yes', 'No']})
    

cpd_d = TabularCPD(variable='Falls', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Falls': ['Yes', 'No']})
    

cpd_e = TabularCPD(variable='Fear of falling', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Fear of falling': ['Yes', 'No']})
    

cpd_f = TabularCPD(variable='Chronic pain', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Chronic pain': ['Yes', 'No']})
    

cpd__h = TabularCPD(variable='Homebound', variable_card=2,
                values=[[0.056, 0.065, 0.071, 0.082, 0.071, 0.082, 0.089, 0.104, 0.08, 0.093, 0.101, 0.117, 0.101, 0.117, 0.127, 0.148, 0.064, 0.075, 0.081, 0.095, 0.081, 0.095, 0.102, 0.119, 0.092, 0.107, 0.116, 0.135, 0.116, 0.135, 0.146, 0.17, 0.068, 0.08, 0.086, 0.1, 0.086, 0.1, 0.109, 0.127, 0.097, 0.113, 0.123, 0.143, 0.123, 0.143, 0.155, 0.18, 0.079, 0.092, 0.099, 0.116, 0.099, 0.116, 0.125, 0.146, 0.112, 0.13, 0.141, 0.164, 0.141, 0.164, 0.178, 0.207], [0.944, 0.935, 0.929, 0.918, 0.929, 0.918, 0.911, 0.896, 0.92, 0.907, 0.899, 0.883, 0.899, 0.883, 0.873, 0.852, 0.936, 0.925, 0.919, 0.905, 0.919, 0.905, 0.898, 0.881, 0.908, 0.893, 0.884, 0.865, 0.884, 0.865, 0.854, 0.83, 0.932, 0.92, 0.914, 0.9, 0.914, 0.9, 0.891, 0.873, 0.903, 0.887, 0.877, 0.857, 0.877, 0.857, 0.845, 0.82, 0.921, 0.908, 0.901, 0.884, 0.901, 0.884, 0.875, 0.854, 0.888, 0.87, 0.859, 0.836, 0.859, 0.836, 0.822, 0.793]],
                evidence=['Depression', 'Social isolation', 'Using walking aid', 'Falls', 'Fear of falling', 'Chronic pain'],
                evidence_card=[2, 2, 2, 2, 2, 2],
                state_names={'Homebound': ['Yes', 'No'],
                                        'Depression': ['No', 'Yes'],
'Social isolation': ['No', 'Yes'],
'Using walking aid': ['No', 'Yes'],
'Falls': ['No', 'Yes'],
'Fear of falling': ['No', 'Yes'],
'Chronic pain': ['No', 'Yes'],
}
            )


# Associating the parameters with the model structure.
homebound.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d,cpd_e,cpd_f, cpd__h)

# Checking if the cpds are valid for the model.
print(f"{'Model is okay' if homebound.check_model() else 'Model is incorrect'}")


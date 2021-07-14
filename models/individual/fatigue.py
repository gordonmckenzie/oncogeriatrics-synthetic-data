
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from utilities import makeGraph

# a,b,c,d etc.
# outcome = ['Fatigue', 'No fatigue']
# variables = [{'name': 'BADL dependency', 'r': 6.58, 'll': 2.6, 'ul': 16.67, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/32920423/'}, {'name': 'Female', 'r': 2.07, 'll': 1.51, 'ul': 2.84, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/32920423/'}, {'name': 'Sleep disturbance', 'r': 2.83, 'll': 1.22, 'ul': 6.57, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/32920423/'}, {'name': 'Pain', 'r': 2.64, 'll': 1.2, 'ul': 5.8, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/32920423/'}, {'name': 'Depression', 'r': 2.23, 'll': 1.7, 'ul': 2.93, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/32920423/'}]
# bg_risk = 0.52
# approach = WEIGHTED # "MAX_RISK"

fatigue = BayesianModel([('BADL dependency', 'Fatigue'), ('Female', 'Fatigue'), ('Sleep disturbance', 'Fatigue'), ('Pain', 'Fatigue'), ('Depression', 'Fatigue')])

makeGraph(fatigue)

cpd_a = TabularCPD(variable='BADL dependency', variable_card=2,
                        values=[[0],[1]],
                        state_names={'BADL dependency': ['Yes', 'No']})
    

cpd_b = TabularCPD(variable='Female', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Female': ['Yes', 'No']})
    

cpd_c = TabularCPD(variable='Sleep disturbance', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Sleep disturbance': ['Yes', 'No']})
    

cpd_d = TabularCPD(variable='Pain', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Pain': ['Yes', 'No']})
    

cpd_e = TabularCPD(variable='Depression', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Depression': ['Yes', 'No']})
    

cpd__f = TabularCPD(variable='Fatigue', variable_card=2,
                values=[[0.52, 0.653, 0.665, 0.834, 0.671, 0.842, 0.857, 0.999, 0.647, 0.812, 0.827, 0.999, 0.834, 0.999, 0.999, 0.999, 0.725, 0.91, 0.926, 0.999, 0.935, 0.999, 0.999, 0.999, 0.902, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999], [0.48, 0.347, 0.335, 0.166, 0.329, 0.158, 0.143, 0.001, 0.353, 0.188, 0.173, 0.001, 0.166, 0.001, 0.001, 0.001, 0.275, 0.09, 0.074, 0.001, 0.065, 0.001, 0.001, 0.001, 0.098, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]],
                evidence=['BADL dependency', 'Female', 'Sleep disturbance', 'Pain', 'Depression'],
                evidence_card=[2, 2, 2, 2, 2],
                state_names={'Fatigue': ['Yes', 'No'],
                                        'BADL dependency': ['No', 'Yes'],
'Female': ['No', 'Yes'],
'Sleep disturbance': ['No', 'Yes'],
'Pain': ['No', 'Yes'],
'Depression': ['No', 'Yes'],
}
            )


# Associating the parameters with the model structure.
fatigue.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d,cpd_e, cpd__f)

# Checking if the cpds are valid for the model.
print(f"{'Model is okay' if fatigue.check_model() else 'Model is incorrect'}")


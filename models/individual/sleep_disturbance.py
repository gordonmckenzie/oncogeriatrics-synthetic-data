
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from util.utilities import makeGraph

# a,b,c,d etc.
# outcome = ['Sleep disturbance', 'No sleep disturbance']
# variables = [{'name': 'Depression', 'r': 1.72, 'll': 1.33, 'ul': 2.22, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/28179129/'}, {'name': 'Hypertension', 'r': 1.5, 'll': 1.2, 'ul': 1.5, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/21731135/'}, {'name': 'Heart disease', 'r': 1.6, 'll': 1.2, 'ul': 2.3, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/21731135/'}, {'name': 'Diabetes', 'r': 1.4, 'll': 1.05, 'ul': 2, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/21731135/'}, {'name': 'Peptic ulcer', 'r': 2.1, 'll': 1.6, 'ul': 2.7, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/21731135/'}, {'name': 'Asthma', 'r': 1.6, 'll': 1.3, 'ul': 2, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/21731135/'}, {'name': 'COPD', 'r': 1.9, 'll': 1.5, 'ul': 2.5, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/21731135/'}]
# bg_risk = 0.64
# approach = "WEIGHTED" # MAX_RISK

sleep_disturbance = BayesianModel([('Depression', 'Sleep disturbance'), ('Hypertension', 'Sleep disturbance'), ('Heart disease', 'Sleep disturbance'), ('Diabetes', 'Sleep disturbance'), ('Peptic ulcer', 'Sleep disturbance'), ('Asthma', 'Sleep disturbance'), ('COPD', 'Sleep disturbance')])

makeGraph(sleep_disturbance)

cpd_a = TabularCPD(variable='Depression', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Depression': ['Yes', 'No']})
    

cpd_b = TabularCPD(variable='Hypertension', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Hypertension': ['Yes', 'No']})
    

cpd_c = TabularCPD(variable='Heart disease', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Heart disease': ['Yes', 'No']})
    

cpd_d = TabularCPD(variable='Diabetes', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Diabetes': ['Yes', 'No']})
    

cpd_e = TabularCPD(variable='Peptic ulcer', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Peptic ulcer': ['Yes', 'No']})
    

cpd_f = TabularCPD(variable='Asthma', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Asthma': ['Yes', 'No']})
    

cpd_g = TabularCPD(variable='COPD', variable_card=2,
                        values=[[0],[1]],
                        state_names={'COPD': ['Yes', 'No']})
    

cpd__s = TabularCPD(variable='Sleep disturbance', variable_card=2,
                values=[[0.64, 0.747, 0.739, 0.863, 0.751, 0.877, 0.867, 0.999, 0.73, 0.853, 0.843, 0.984, 0.857, 0.999, 0.989, 0.999, 0.739, 0.863, 0.852, 0.995, 0.867, 0.999, 0.999, 0.999, 0.843, 0.984, 0.973, 0.999, 0.989, 0.999, 0.999, 0.999, 0.735, 0.859, 0.849, 0.991, 0.863, 0.999, 0.996, 0.999, 0.839, 0.98, 0.968, 0.999, 0.984, 0.999, 0.999, 0.999, 0.849, 0.991, 0.979, 0.999, 0.996, 0.999, 0.999, 0.999, 0.968, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.857, 0.999, 0.989, 0.999, 0.999, 0.999, 0.999, 0.999, 0.978, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.989, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.984, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999], [0.36, 0.253, 0.261, 0.137, 0.249, 0.123, 0.133, 0.001, 0.27, 0.147, 0.157, 0.016, 0.143, 0.001, 0.011, 0.001, 0.261, 0.137, 0.148, 0.005, 0.133, 0.001, 0.001, 0.001, 0.157, 0.016, 0.027, 0.001, 0.011, 0.001, 0.001, 0.001, 0.265, 0.141, 0.151, 0.009, 0.137, 0.001, 0.004, 0.001, 0.161, 0.02, 0.032, 0.001, 0.016, 0.001, 0.001, 0.001, 0.151, 0.009, 0.021, 0.001, 0.004, 0.001, 0.001, 0.001, 0.032, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.143, 0.001, 0.011, 0.001, 0.001, 0.001, 0.001, 0.001, 0.022, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.011, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.016, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]],
                evidence=['Depression', 'Hypertension', 'Heart disease', 'Diabetes', 'Peptic ulcer', 'Asthma', 'COPD'],
                evidence_card=[2, 2, 2, 2, 2, 2, 2],
                state_names={'Sleep disturbance': ['Yes', 'No'],
                                        'Depression': ['No', 'Yes'],
'Hypertension': ['No', 'Yes'],
'Heart disease': ['No', 'Yes'],
'Diabetes': ['No', 'Yes'],
'Peptic ulcer': ['No', 'Yes'],
'Asthma': ['No', 'Yes'],
'COPD': ['No', 'Yes'],
}
            )


# Associating the parameters with the model structure.
sleep_disturbance.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d,cpd_e,cpd_f,cpd_g, cpd__s)

# Checking if the cpds are valid for the model.
print(f"{'Model is okay' if sleep_disturbance.check_model() else 'Model is incorrect'}")



from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from utilities import makeGraph

# a,b,c,d etc.
# outcome = ['Social isolation', 'No social isolation']
# variables = [{'name': 'Hearing loss', 'r': 2.14, 'll': 1.29, 'ul': 3.57, 'ciType': 95, 'type': 'OR', 'ref': 'https://journals.sagepub.com/doi/10.1177/0194599820910377'}, {'name': 'Falls', 'r': 1.44, 'll': 1.01, 'ul': 1.86, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/32018091/'}, {'name': 'Difficulty walking outside', 'r': 1.59, 'll': 1.41, 'ul': 1.85, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/23548944/'}, {'name': 'BADL dependency', 'r': 1.5, 'll': 1.0, 'ul': 2.2, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/19274642/'}]
# bg_risk = 0.44
# approach = "WEIGHTED" # MAX_RISK

social_isolation = BayesianModel([('Hearing loss', 'Social isolation'), ('Falls', 'Social isolation'), ('Difficulty walking outside', 'Social isolation'), ('BADL dependency', 'Social isolation')])

makeGraph(social_isolation)

cpd_a = TabularCPD(variable='Hearing loss', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Hearing loss': ['Yes', 'No']})
    

cpd_b = TabularCPD(variable='Falls', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Falls': ['Yes', 'No']})
    

cpd_c = TabularCPD(variable='Difficulty walking outside', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Difficulty walking outside': ['Yes', 'No']})
    

cpd_d = TabularCPD(variable='BADL dependency', variable_card=2,
                        values=[[0],[1]],
                        state_names={'BADL dependency': ['Yes', 'No']})
    

cpd__s = TabularCPD(variable='Social isolation', variable_card=2,
                values=[[0.44, 0.564, 0.57, 0.695, 0.61, 0.734, 0.741, 0.865, 0.608, 0.732, 0.738, 0.862, 0.778, 0.902, 0.908, 0.999], [0.56, 0.436, 0.43, 0.305, 0.39, 0.266, 0.259, 0.135, 0.392, 0.268, 0.262, 0.138, 0.222, 0.098, 0.092, 0.001]],
                evidence=['Hearing loss', 'Falls', 'Difficulty walking outside', 'BADL dependency'],
                evidence_card=[2, 2, 2, 2],
                state_names={'Social isolation': ['Yes', 'No'],
                                        'Hearing loss': ['No', 'Yes'],
'Falls': ['No', 'Yes'],
'Difficulty walking outside': ['No', 'Yes'],
'BADL dependency': ['No', 'Yes'],
}
            )


# Associating the parameters with the model structure.
social_isolation.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d, cpd__s)

# Checking if the cpds are valid for the model.
print(f"{'Model is okay' if social_isolation.check_model() else 'Model is incorrect'}")


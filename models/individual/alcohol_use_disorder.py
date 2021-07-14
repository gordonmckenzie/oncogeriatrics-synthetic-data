
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from utilities import makeGraph

# a,b,c,d etc.
# outcome = ['Alcohol use disorder', 'No alcohol use disorder']
# variables = [{'name': 'Depression', 'r': 1.75, 'll': 1.5, 'ul': 2.0, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/17606817/'}]
# bg_risk = 0.178
# approach = WEIGHTED # "MAX_RISK"

alcohol_use_disorder = BayesianModel([('Depression', 'Alcohol use disorder')])

makeGraph(alcohol_use_disorder)

cpd_a = TabularCPD(variable='Depression', variable_card=2,
                        values=[[0],[1]],
                        state_names={'Depression': ['Yes', 'No']})
    

cpd__a = TabularCPD(variable='Alcohol use disorder', variable_card=2,
                values=[[0.178, 0.27], [0.82, 0.73]],
                evidence=['Depression'],
                evidence_card=[2],
                state_names={'Alcohol use disorder': ['Yes', 'No'],
                                        'Depression': ['No', 'Yes'],
}
            )


# Associating the parameters with the model structure.
alcohol_use_disorder.add_cpds(cpd_a, cpd__a)

# Checking if the cpds are valid for the model.
print(f"{'Model is okay' if alcohol_use_disorder.check_model() else 'Model is incorrect'}")


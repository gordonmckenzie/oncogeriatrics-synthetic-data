import string 
import numpy as np
import itertools
import math
from tabulate import tabulate

# a,b,c,d etc.
outcome = ['CKD', 'No CKD']
variables = [
    {'name': 'Diabetes', 'r': 3.09, 'll': 1.73, 'ul': 4.93, 'ciType': 95, 'type': 'RR', 'ref': "https://pubmed.ncbi.nlm.nih.gov/27477292/"},
    {'name': 'Obesity', 'r': 1.81, 'll': 1.52, 'ul': 2.16, 'ciType': 95, 'type': 'OR', 'ref': "#https://files.digital.nhs.uk/72/0EDBA2/HSE17-Adult-Child-BMI-tab-v2.xlsx, https://pubmed.ncbi.nlm.nih.gov/33656052/"},
    {'name': 'Hypertension', 'r': 1.81, 'll': 1.39, 'ul': 2.6, 'ciType': 95, 'type': 'RR', 'ref': "https://pubmed.ncbi.nlm.nih.gov/33238919/, https://pubmed.ncbi.nlm.nih.gov/27383068, https://bjgp.org/content/70/693/e285"},
]
bg_risk = 0.14
approach = "WEIGHTED" # MAX_RISK

i = 0 
 
table = []
labels = []

def transformRisk(v):
    if v["type"] == "RR":
        return v["r"]
    elif v["type"] == "OR":
        # https://pubmed.ncbi.nlm.nih.gov/9832001/
        rr = v["r"] / ((1 - bg_risk) + (bg_risk * v["r"]))
        return round(rr, 2)
    elif v["type"] == "HR":
        # https://www.sciencedirect.com/science/article/pii/S0277953617303490?via%3Dihub
        rr = (1 - math.pow(math.e, (v["r"] * math.log(1 - bg_risk)))) / bg_risk
        return round(rr, 2)

def calculateWeights():
    wts = []
    for v in variables:
        wts.append(transformRisk(v))
    weights = np.array(wts)
    (weights - weights.min()) / (weights.max() - weights.min())
    return (weights / weights.sum())

for row in itertools.product([0, 1], repeat = len(variables)):
    str = ""
    v = 0
    for i,x in enumerate(row):
        str += f"{string.ascii_lowercase[i]}{x}"
        v += 1
    table.append(row)
    labels.append(str)

cat1 = []
cat2 = []

for row in table:
    if all(v == 0 for v in row):
        cat1.append(bg_risk)
    else:
        if (approach == "MAX_RISK"): # maximum risk approach     
            risks = []  
            for i, t in enumerate(row):
                if t == 1:
                    risk = round(bg_risk * transformRisk(variables[i]), 3)
                else:
                    risk = 0
                risks.append(risk)
            cat1.append(max(risks))
        elif (approach == "WEIGHTED"): # weighted risks approach
            # https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=756524
            risk = bg_risk
            weights = calculateWeights()
            for i, t in enumerate(row):
                if t == 1:
                    if weights[i] < 1:
                        risk += (bg_risk * (weights[i] * transformRisk(variables[i])))
                    else:
                        risk = round(bg_risk * transformRisk(variables[i]), 2)
            cat1.append(np.round(0.999 if risk > 1 else risk, 3))
  
for c in cat1:
    cat2.append(np.round(1 - c, 3))

cpd = [cat1, cat2]

transposedTable = np.transpose(cpd)

t = []
for i,row in enumerate(labels):
    t.append([row,transposedTable[i][0], transposedTable[i][1]])

print(tabulate(t, headers=outcome, tablefmt="fancy_grid"))
print("\n")
for i,v in enumerate(variables):
    print(f"{string.ascii_lowercase[i]} = {v['name']} ({v['ref']})")
print("\n")
print(cpd)

#Create the file 
edges = []
evidence = []
evidence_card = []
cpd_variable_names = ""
state_names = ""
cpds = ""
for i,v in enumerate(variables):
    edges.append((v["name"], outcome[0]))
    evidence.append(v["name"])
    evidence_card.append(2)
    state_names += f"'{v['name']}': ['No', 'Yes'],\n"
    cpd_variable_names +=  f"cpd_{string.ascii_lowercase[i]},"
    cpds += f"""cpd_{string.ascii_lowercase[i]} = TabularCPD(variable='{v["name"]}', variable_card=2,
                        values=[[0],[1]],
                        state_names={{'{v["name"]}': ['Yes', 'No']}})
    \n\n"""

cpds += f"""cpd__{outcome[0][0].lower()} = TabularCPD(variable='{outcome[0]}', variable_card=2,
                values={cpd},
                evidence={evidence},
                evidence_card={evidence_card},
                state_names={{'{outcome[0]}': ['Yes', 'No'],
                                        {state_names}}}
            )
"""


code = f"""
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from util.utilities import makeGraph

# a,b,c,d etc.
# outcome = {outcome}
# variables = {variables}
# bg_risk = {bg_risk}
# approach = "{approach}" # MAX_RISK

{outcome[0].lower().replace(' ', '_')} = BayesianModel({edges})

makeGraph({outcome[0].lower().replace(' ', '_')})

{cpds}

# Associating the parameters with the model structure.
{outcome[0].lower().replace(' ', '_')}.add_cpds({cpd_variable_names} cpd__{outcome[0][0].lower()})

# Checking if the cpds are valid for the model.
print(f"{{'Model is okay' if {outcome[0].lower().replace(' ', '_')}.check_model() else 'Model is incorrect'}}")

"""

f = open(f"./models/{outcome[0].lower().replace(' ', '_')}.py", "w")
f.write(code)
f.close()

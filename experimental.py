import itertools
import os
import numpy as np
import pandas as pd
import yaml
from scipy.stats import bernoulli
import vaex

#rng = np.random.default_rng()

#df = pd.read_hdf('data/simulacrum.h5')

#age = 65
#gender = 'm'
#cancer_site = 'lung'

#q = df[(df.age == age) & (df.gender == gender) & (df.cancer_site == cancer_site)]

# print(f"Age {round(df['age'].mean(), 1)} ({df['age'].min()}-{df['age'].max()})")
# print(f"{round(df['gender'].value_counts().values[0]/(df['gender'].value_counts().values[0] + df['gender'].value_counts().values[1]) * 100, 1)}% female")
# print(df['surgery'].mean(), df['chemotherapy'].mean(), df['chemoradiotherapy'].mean())
# df['deprivation'] = df['deprivation'].astype(int)
# print(df['deprivation'].mean())

#print(df.groupby('age').mean())

#df.to_csv('data/simulacrum.csv', index=False)


#rng = np.random.default_rng()

#Current, former, never
#x = rng.binomial(n=1, p=0.107, size=3)

#print(x)
"""
r = bernoulli.rvs(0.107, size=1)
#mean, var, skew, kurt = bernoulli.stats(0.107, moments='mvsk')
#print(mean, var, skew, kurt)

list = []

for i in range(0,5000):
    x = bernoulli.rvs(0.107, size=1) #rng.binomial(n=1, p=0.107, size=3)
    list.append(x)

print(np.mean(list, axis=0, dtype=np.float32))


"""
"""
epi = None
with open("data/epidemiology.yaml", 'r') as stream:
    epi = yaml.safe_load(stream)

prev_m = [50, 65, 60, 3]
prev_f = [300, 270, 188, 118]
for i, e in enumerate(epi):
    if i < 4:
        print('m',(prev_m[i] * (e['n'] /100000) / e['n']) *100)
        print('f',(prev_f[i] * (e['n'] / 100000) / e['n'])*100)
    else:
        print('m',(prev_m[3] * (e['n'] /100000) / e['n'])*100)
        print('f',(prev_f[3] * (e['n'] /100000) / e['n'])*100)
"""

"""
m = []
f = []
for e in epi:
    m.append([e['geriatricVulnerabilities']['currentSmoker']['m']/100,round(e['geriatricVulnerabilities']['formerSmoker']['m']/100, 2), round(1-((e['geriatricVulnerabilities']['currentSmoker']['m']/100)+(e['geriatricVulnerabilities']['formerSmoker']['m']/100)),2)])
    f.append([e['geriatricVulnerabilities']['currentSmoker']['f']/100,round(e['geriatricVulnerabilities']['formerSmoker']['f']/100, 2), round(1-((e['geriatricVulnerabilities']['currentSmoker']['f']/100)+(e['geriatricVulnerabilities']['formerSmoker']['f']/100)),2)])

print(m,f)
"""

"""
prevalence = ['mci', 'dementia', 'hearingLoss', 't1dm', 't2dm', 'asthma', 'hypertension', 'osteoporosis', 'pepticUlcer', 'parkinsonsDisease', 'thyroidDisease', 'luts', 'visualImpairment', 'heartValveDisease', 'ctd', 'arthritis', 'drinksAlcohol', 'aerobicallyActive', 'af', 'ckd', 'dizziness', 'urinaryIncontinence', 'mi', 'tia', 'stroke', 'dizziness', 'ulcers', 'footProblems', 'osteoporosis', 'orthostaticHypotension', 'copd', 'anaemia', 'faecalIncontinence']
prevalence_str = ['Mild cognitive impairment', 'Dementia', 'Hearing loss', 'Type 1 diabetes mellitus', 'Type 2 diabetes mellitus', 'Asthma', 'Hypertension', 'Osteoporosis', 'Peptic ulcer', "Parkinson's disease", 'Thyroid disease', 'Lower urinary tract symptoms', 'Visual impairment', 'Heart valve disease', 'Connective tissue disorder', 'Arthritis','Drinks alcohol', 'Aerobically active', 'Atrial fibrillation', 'Chronic Kidney Disease', 'Dizziness', 'Urinary incontinence', 'Myocardial infarction', 'Transient ischaemic attack', 'Stroke', 'Dizziness', 'Ulcers', 'Foot problems', 'Osteoporosis', 'Orthostatic hypotension', 'COPD', 'Anaemia', 'Faecal incontinence']
res = {prevalence[i]: prevalence_str[i] for i in range(len(prevalence))}
print(res)
"""

""""
array = {'mci': 'Mild cognitive impairment',
'dementia': 'Dementia',
'hearingLoss': 'Hearing loss',
't1dm': 'Type 1 diabetes mellitus',
't2dm': 'Type 2 diabetes mellitus',
'asthma': 'Asthma',
'hypertension': 'Hypertension',
'osteoporosis': 'Osteoporosis',
'pepticUlcer': 'Peptic ulcer',
'parkinsonsDisease': "Parkinson's disease",
'thyroidDisease': 'Thyroid disease',
'luts': 'Lower urinary tract symptoms',
'visualImpairment': 'Visual impairment',
'heartValveDisease': 'Heart valve disease',
'ctd': 'Connective tissue disorder',
'arthritis': 'Arthritis',
'drinksAlcohol': 'Drinks alcohol',
'aerobicallyActive': 'Aerobically active',
'af': 'Atrial fibrillation',
'ckd': 'Chronic Kidney Disease',
'dizziness': 'Dizziness',
'urinaryIncontinence': 'Urinary incontinence',
'mi': 'Myocardial infarction',
'tia': 'Transient ischaemic attack',
'stroke': 'Stroke',
'ulcers': 'Ulcers',
'footProblems': 'Foot problems',
'orthostaticHypotension': 'Orthostatic hypotension',
'copd': 'COPD',
'anaemia': 'Anaemia',
'faecalIncontinence': 'Faecal incontinence',
'angina': 'Angina',
'livesAlone': 'Lives alone',
'schizophrenia': 'Schizophrenia',
'bad': 'Bipolar affective disorder'}


for key, value in sorted(array.items()):
    print(f"'{key}': '{value}',")
"""

import networkx as nx
import matplotlib.pyplot as plt
G=nx.DiGraph()
# G.graph['rankdir'] = 'LR'
# G.graph['dpi'] = 120
variables = ["MVPA", "Frailty", "BADL\n impairment", "IADL\n impairment", "Homebound", "Angina", "Smoking"]
negating_edges = [("MVPA", "Frailty"), ("MVPA", "BADL\n impairment"), ("MVPA", "IADL\n impairment"), ("MVPA", "Homebound"), ("MVPA", "Homebound"), ("MVPA", "Angina")]
reducing_edges = [("MVPA", "Smoking")]
#edges = negating_edges + reducing_edges
#G.add_nodes_from(variables)
#G.add_edges_from(edges)
for v in variables:
    G.add_node(v, shape='square')
for ne in negating_edges:
    options = {'color': 'red', 'widthA': 0., 'angleA': None, 'widthB':1.0, 'angleB':None}
    G.add_edge(ne[0], ne[1], type="neg")
for re in reducing_edges:
    options = {'color':'red', 'style':'dashed'}
    G.add_edge(re[0], re[1], type="red")

e_neg = [(u, v) for (u, v, d) in G.edges(data=True) if d["type"] == "neg"]
e_red = [(u, v) for (u, v, d) in G.edges(data=True) if d["type"] == "red"]

pos = nx.spring_layout(G)

nx.draw_networkx_nodes(G, pos,  node_color='#f5f6f7',
        node_size=3000)

nx.draw_networkx_edges(G, pos, edgelist=e_neg, arrowstyle='-[', edge_color='red')
nx.draw_networkx_edges(G, pos, edgelist=e_red, style="dashed", edge_color='red')

nx.draw_networkx_labels(G, pos, 
        font_size=8, 
        font_family="sans-serif")
plt.axis("off")
plt.show()
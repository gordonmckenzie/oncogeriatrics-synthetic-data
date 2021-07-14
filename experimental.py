import itertools
import numpy as np
import yaml
from scipy.stats import bernoulli

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
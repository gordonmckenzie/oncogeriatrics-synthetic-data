import csv
import pandas as pd
import numpy as np
from prescriber import Prescriber
from utils import Utils
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_theme()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

df = pd.read_csv('tests/test_data.csv')

# print(df['polypharmacy'].mean())

for index, row in df.iterrows():
    p = Prescriber(row)
    poly = p.prescribe()
    df.loc[index, 'polypharmacy'] = 1 if poly >= 5 else 0

# print(df['polypharmacy'].mean())

con = sqlite3.connect('data/database.db')
##con.set_trace_callback(print)
cur = con.cursor()

print(f"\nPercentage with polypharmacy: {round(df['polypharmacy'].mean() * 100, 2)}\n")

drug_no = ['0','1','2','3','4','5','6','7','8','9','10+']
percentages = []

# Total prescriptions
cur.execute("SELECT COUNT(id) FROM medications")
print(f"Total prescriptions {cur.fetchone()[0]}\n")

# Duplicates
cur.execute("SELECT id,agent,COUNT(*) FROM medications GROUP BY id,agent HAVING count(*) > 1")
if (len(cur.fetchall())) > 0:
    print(f"There are duplicates...\n")
    for row in cur.fetchall():
        print(row)
else:
    print(f"{bcolors.OKGREEN}\u2714{bcolors.ENDC} There are NO duplicates\n")

# The current formulary
print(f"\nThe current formulary...\n")
cur.execute("SELECT DISTINCT(agent) FROM medications GROUP BY agent")
for row in cur.fetchall():
    print(row[0])

# Anticholinergic burden score and STOP criteria
cur.execute("SELECT id, GROUP_CONCAT(agent, ',') AS list FROM medications GROUP BY id")
acb_scores_list = []
stop_criteria = []
for row in cur.fetchall():
    u = Utils(row[1].split(","), df.iloc[[row[0] - 1]])
    acb_score = u.calculate_acb_score()
    acb_scores_list.append(acb_score)
    stop = u.stop_criteria()
    stop_criteria.append([row[0],stop])

total_stop_criteria = 0
f = open('prescribing/stop.csv', 'w')
writer = csv.writer(f)
for stop in stop_criteria:
    if len(stop[1]) > 0:
        for s in stop[1]:
            total_stop_criteria += 1
            writer.writerow([stop[0], s]) 
f.close()

if total_stop_criteria > 0:
    print(f"\n{bcolors.FAIL}\u2717{bcolors.ENDC} Total STOP criteria {total_stop_criteria}\n")
else:
    print(f"\n{bcolors.OKGREEN}\u2714{bcolors.ENDC} No STOP criteria!\n")

acb_score = np.array(acb_scores_list)
print(f"\nMean anticolingeric burden score...\n")
print(f"{round(np.mean(acb_score), 1)}\n")


# groups = [
#     {'Antiplatelets': ['aspirin', 'clopidogrel']},
#     {'Antilipidaemics': ['atorvastatin']},
#     {'NSAIDs': ['ibuprofen', 'naproxen', 'celecoxib']},
#     {'Paracetamol': ['paracetamol']},
#     {'Opioids': ['codeine', 'dihydrocodeine', 'tramadol', 'morphine', 'oxycodone', 'fentanyl', 'buprenorphine']},
#     {'Steroids': ['prednisolone', 'hydrocortisone', 'dexamethasone']},
#     {'ACE inhibitors': ['ramipril', 'enalipril', 'lisinopril']},
#     {'Beta blockers': ['propanolol', 'bisoprolol', 'atenolol', 'carvedilol']},
#     {'CCBs': ['amlodipine']},
#     {'MR antagonists': ['spironolactone', 'eplerenone']},
#     {'ARBs': ['candesartan', 'losartan']},
#     {'Diuretics': ['indapamide', 'bendroflumethiazide', 'furosemide']},
#     {'Anticoagulants': ['warfarin', 'rivaroxaban', 'apixaban', 'edoxaban']},
#     {'PPIs': ['omeprazole', 'lansoprazole']},
#     {'Alpha blockers': ['tamsulosin', 'alfuzocin', 'doxazocin', 'indoramin', 'terazocin', 'prazocin']},
#     {'Antimuscarinics': ['tolterodine', 'oxybutynin', 'solifenacin']},
#     {'SSRIs': ['sertraline', 'citalopram', 'fluoxetine', 'paroxetine', 'escitalopram']},
#     {'MAOIs': ['moclobemide', 'tranylcypromide', 'phenelzine', 'isocarboxazid']},
#     {'TCAs': ['amitriptyline', 'trazadone', 'dosulepin', 'lofepramine', 'nortriptyline', 'clomipramine', 'imipramine']},
#     {'Other antidepressants': ['mirtazipine', 'venlafaxine', 'duloxetine', 'flupentixol']},
#     {'Inhaled therapies': ['salbutamol', 'beclometasone', 'beclometasone with formeterol', 'montelukast', 'ipratropium', 'ipratropium with salbutamol', 'Serevent', 'Spiriva Respimat', 'Spiolto Respimat', 'Fostair MDI', 'tiotropium', 'Trimbow MDI']},
#     {'Antipsychotics': ['quetiapine', 'olanzipine', 'risperidone', 'haloperidol', 'chlorpromazine', 'trifluoperazine', 'aripiprazole']},
#     {'PDE inhibitors': ['sildenafil', 'tadalafil']},
#     {'Levothyroxine': ['levothyroxine']},
#     {'Antidementia': ['donepizil', 'rivastigmine', 'galantamine', 'memantine']},
#     {'Insulins': ['Levemir®', 'Humalog®', 'Humulin I®']},
#     {'Antidiabetic': ['metformin', 'gliclazide', 'linagliptin', 'dapagliflozin', 'pioglitazone', 'exenatide']},
#     {'Antianginals': ['isosorbide mononitrate', 'nicorandil', 'glyceryl trinitrate']},
#     {'Haematinic replacement': ['ferrous sulfate', 'hydroxocobalamin', 'folic acid']},
#     {'Antimigraine': ['sumatriptan']},
#     {'Antiepileptic': ['valproic acid', 'topiramate', 'carbamazepine','lamotrigine', 'sodium valproate']},
#     {'Mood stabilisers': 'lithium'},
#     {'Antiparkinsonian': ['amantadine','co-careldopa', 'pramipexole', 'levodopa and carbidopa and etacapone', 'ropinirole', 'pergolide', 'procyclidine', 'bromocriptine']},
#     {'DMARDs': ['methotrexate']},
#     {'Bone protection': ['alendronic acid']},
#     {'Antiarrhythmics': ['amiodarone', 'digoxin', 'sotalol', 'verapamil', 'diltiazem']},
# ]
# group_names = []
# group_percentages = []

# def get_syntax(v):
#     if len(v) > 1:
#         return f"IN {tuple(v)}"
#     else:
#         return f"= '{v[0]}'"

# for group in groups:
#     for k,v in group.items():
#         cur.execute('''
#             SELECT 
#                 counts,
#                 (SELECT COUNT(id) FROM medications) AS total,
#                 counts * 100.0 / (SELECT COUNT(id) FROM medications) AS percentage
#             FROM 
#             (
#                 SELECT COUNT(agent) AS counts
#                 FROM medications
#                 WHERE agent '''+ get_syntax(v) +'''
#             )''')
#         group_names.append(k)
#         group_percentages.append(cur.fetchone()[2])

# list1, list2 = (list(t) for t in zip(*sorted(zip(group_names, group_percentages))))

# d_groups = {'Drug group': list1, 'Proportion of prescriptions': list2}
# df_groups = pd.DataFrame(data=d_groups)
# sns.barplot(y="Drug group", x="Proportion of prescriptions", palette="Blues_d", data=df_groups)
# plt.show()

# # How many without prescription
# cur.execute("SELECT COUNT(DISTINCT(id)) FROM medications")
# percentages.append((len(df) - cur.fetchone()[0]) * 100 / len(df))

# for i in range(1,10):
#     cur.execute(
#         f'''
#         SELECT
#             COUNT(counts) AS _counts,
#             (SELECT COUNT(DISTINCT(id)) FROM medications) AS total,
#             COUNT(counts) * 100.0 /  (SELECT COUNT(DISTINCT(id)) FROM medications) AS percentage
#         FROM
#         (
#             SELECT COUNT(agent) AS counts
#             FROM medications
#             GROUP BY id
#             HAVING COUNT(agent) = ''' + str(i) + '''
#         );
#         ''')
#     percentages.append(cur.fetchone()[2])
# cur.execute(
#     f'''
#     SELECT
#         COUNT(counts) AS _counts,
#         (SELECT COUNT(DISTINCT(id)) FROM medications) AS total,
#         COUNT(counts) * 100.0 /  (SELECT COUNT(DISTINCT(id)) FROM medications) AS percentage
#     FROM
#     (
#         SELECT COUNT(agent) AS counts
#         FROM medications
#         GROUP BY id
#         HAVING COUNT(agent) >= 10
#     );
#     ''')
# percentages.append(cur.fetchone()[2])
# con.close()

# d_drugs = {'Number of drugs': drug_no, 'Proportion of patients': percentages}
# df_drugs = pd.DataFrame(data=d_drugs)
# sns.barplot(x="Number of drugs", y="Proportion of patients", palette="Blues_d", data=df_drugs)
# plt.show()



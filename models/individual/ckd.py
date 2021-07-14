import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from util.utilities import Utilities
import numpy as np

rng = np.random.default_rng()

u = Utilities()

def inferCKD(band, gender, h, o, d):
  # a,b,c,d etc.
  # outcome = ['CKD', 'No CKD']
  # variables = [{'name': 'Diabetes', 'r': 3.09, 'll': 1.73, 'ul': 4.93, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/27477292/'}, {'name': 'Obesity', 'r': 1.81, 'll': 1.52, 'ul': 2.16, 'ciType': 95, 'type': 'OR', 'ref': '#https://files.digital.nhs.uk/72/0EDBA2/HSE17-Adult-Child-BMI-tab-v2.xlsx, https://pubmed.ncbi.nlm.nih.gov/33656052/'}, {'name': 'Hypertension', 'r': 1.81, 'll': 1.39, 'ul': 2.6, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33238919/, https://pubmed.ncbi.nlm.nih.gov/27383068, https://bjgp.org/content/70/693/e285'}]
  # bg_risk = 0.14
  # approach = "WEIGHTED" # MAX_RISK

  bg_risk = band['geriatricVulnerabilities']['ckd'][gender] / 100

  variables = [{'name': 'Diabetes', 'r': 3.09, 'll': 1.73, 'ul': 4.93, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/27477292/'}, {'name': 'Obesity', 'r': 1.81, 'll': 1.52, 'ul': 2.16, 'ciType': 95, 'type': 'OR', 'ref': '#https://files.digital.nhs.uk/72/0EDBA2/HSE17-Adult-Child-BMI-tab-v2.xlsx, https://pubmed.ncbi.nlm.nih.gov/33656052/'}, {'name': 'Hypertension', 'r': 1.81, 'll': 1.39, 'ul': 2.6, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33238919/, https://pubmed.ncbi.nlm.nih.gov/27383068, https://bjgp.org/content/70/693/e285'}]

  values = u.calculateCPDTable(bg_risk, variables)

  ckd = BayesianModel([('Diabetes', 'CKD'), ('Obesity', 'CKD'), ('Hypertension', 'CKD')])

  #u.makeGraph(ckd, 'CKD')

  cpd_a = TabularCPD(variable='Diabetes', variable_card=2,
                          values=[[0],[1]],
                          state_names={'Diabetes': ['Yes', 'No']})
      

  cpd_b = TabularCPD(variable='Obesity', variable_card=2,
                          values=[[0],[1]],
                          state_names={'Obesity': ['Yes', 'No']})
      

  cpd_c = TabularCPD(variable='Hypertension', variable_card=2,
                          values=[[0],[1]],
                          state_names={'Hypertension': ['Yes', 'No']})
      

  cpd__c = TabularCPD(variable='CKD', variable_card=2,
                  #values=[[0.14, 0.21, 0.197, 0.267, 0.345, 0.415, 0.402, 0.472], [0.86, 0.79, 0.803, 0.733, 0.655, 0.585, 0.598, 0.528]],
                  values=values,
                  evidence=['Diabetes', 'Obesity', 'Hypertension'],
                  evidence_card=[2, 2, 2],
                  state_names={'CKD': ['Yes', 'No'],
                    'Diabetes': ['No', 'Yes'],
                    'Obesity': ['No', 'Yes'],
                    'Hypertension': ['No', 'Yes']
                    })


  # Associating the parameters with the model structure.
  ckd.add_cpds(cpd_a,cpd_b,cpd_c, cpd__c)

  # Checking if the cpds are valid for the model.
  # print(f"{'Model is okay' if ckd.check_model() else 'Model is incorrect'}")

  infer = VariableElimination(ckd)
  q = infer.query(['CKD'], evidence={'Hypertension': h, 'Obesity': o, 'Diabetes': d}, show_progress=False)

  return 1 if rng.random() < q.values[0] else 0

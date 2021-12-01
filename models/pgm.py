import sys, itertools, math
import os.path
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import networkx as nx
import pylab as plt
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

class PGM:
    def __init__(self, rng):
        self.rng: np.random = rng

    # Return Yes or No for PGM inference
    def inferenceResult(self, p):
        return 'Yes' if p == 1 or p == True else 'No'

    # Makes a graphical representation of a PGM subgraph
    def makeGraph(self, model, filename):
        options = {
            'node_color': 'black',
            'node_size': 200,
            'width': 1,
            'font_size': 12
        }
        pos = nx.spring_layout(model)
        nx.draw(model, pos, with_labels=False, **options)
        for p in pos:  # Raise text positions
            pos[p][1] += 0.1
        nx.draw_networkx_labels(model, pos)
        plt.savefig(f'results/graphs/{filename}.png')

    # Calculate CPD table from risk factors
    def calculateCPDTable(self, bg_risk, variables, approach="WEIGHTED"):
        table = []

        if bg_risk < 0: # Check to ensure background risk has not become negative after adjustment
            bg_risk = 0.01

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
            (weights - weights.min()) / weights.max() - weights.min()
            return (weights / weights.sum())

        for row in itertools.product([0, 1], repeat = len(variables)):
            table.append(row)

        cat1 = []
        cat2 = []

        for row in table:
            if all(v == 0 for v in row):
                cat1.append(bg_risk)
            else:
                if (approach == "MAX_RISK"): # Maximum risk approach     
                    risks = []  
                    for i, t in enumerate(row):
                        if t == 1:
                            risk = round(bg_risk * transformRisk(variables[i]), 3)
                        else:
                            risk = 0
                        risks.append(risk)
                    cat1.append(max(risks))
                elif (approach == "WEIGHTED"): # Weighted risks approach
                    #https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=756524
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

        return cpd

    def inferAnaemia(self, band, gender, c):
        anaemia = BayesianModel([('Chronic kidney disease', 'Anaemia')])

        bg_risk = band['geriatricVulnerabilities']['anaemia'][gender] / 100

        variables = [{'name': 'Chronic kidney disease', 'r': 1.5, 'll': 17.0, 'ul': 30.6, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/20172445/'}]

        values = self.calculateCPDTable(bg_risk, variables)

        #u.makeGraph(anaemia)

        cpd_a = TabularCPD(variable='Chronic kidney disease', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Chronic kidney disease': ['Yes', 'No']})
            

        cpd__a = TabularCPD(variable='Anaemia', variable_card=2,
                        values=values,
                        evidence=['Chronic kidney disease'],
                        evidence_card=[2],
                        state_names={'Anaemia': ['Yes', 'No'],
                            'Chronic kidney disease': ['No', 'Yes']
                        })

        # Associating the parameters with the model structure.
        anaemia.add_cpds(cpd_a, cpd__a)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if anaemia.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(anaemia)
        q = infer.query(['Anaemia'], evidence={'Chronic kidney disease': c}, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferCKD(self, band, gender, h, o, d):
        # a,b,c,d etc.
        # outcome = ['CKD', 'No CKD']
        # variables = [{'name': 'Diabetes', 'r': 3.09, 'll': 1.73, 'ul': 4.93, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/27477292/'}, {'name': 'Obesity', 'r': 1.81, 'll': 1.52, 'ul': 2.16, 'ciType': 95, 'type': 'OR', 'ref': '#https://files.digital.nhs.uk/72/0EDBA2/HSE17-Adult-Child-BMI-tab-v2.xlsx, https://pubmed.ncbi.nlm.nih.gov/33656052/'}, {'name': 'Hypertension', 'r': 1.81, 'll': 1.39, 'ul': 2.6, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33238919/, https://pubmed.ncbi.nlm.nih.gov/27383068, https://bjgp.org/content/70/693/e285'}]
        # bg_risk = 0.14
        # approach = "WEIGHTED" # MAX_RISK

        bg_risk = (band['geriatricVulnerabilities']['ckd'][gender] / 100) #- 0.14

        variables = [{'name': 'Diabetes', 'r': 3.09, 'll': 1.73, 'ul': 4.93, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/27477292/'}, {'name': 'Obesity', 'r': 1.81, 'll': 1.52, 'ul': 2.16, 'ciType': 95, 'type': 'OR', 'ref': '#https://files.digital.nhs.uk/72/0EDBA2/HSE17-Adult-Child-BMI-tab-v2.xlsx, https://pubmed.ncbi.nlm.nih.gov/33656052/'}, {'name': 'Hypertension', 'r': 1.81, 'll': 1.39, 'ul': 2.6, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33238919/, https://pubmed.ncbi.nlm.nih.gov/27383068, https://bjgp.org/content/70/693/e285'}]

        values = self.calculateCPDTable(bg_risk, variables)

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

        return 1 if self.rng.random() < q.values[0] else 0

    def inferCOPD(self, band, gender, s, a):
        copd = BayesianModel([('Past smoking', 'COPD'), ('Current smoking', 'COPD'), ('Asthma', 'COPD')])

        bg_risk = (band['geriatricVulnerabilities']['copd'][gender] / 100)

        variables = [{'name': 'Past smoking', 'r': 2.89, 'll': 2.63, 'ul': 3.17, 'type': 'RR', 'ref': 'https://bmcpulmmed.biomedcentral.com/articles/10.1186/1471-2466-11-36'}, {'name': 'Current smoking', 'r': 3.51, 'll': 3.08, 'ul': 3.99, 'type': 'RR', 'ref': 'https://bmcpulmmed.biomedcentral.com/articles/10.1186/1471-2466-11-36'}, {'name': 'Asthma', 'r': 2.23, 'll': 1.36, 'ul': 3.66, 'type': 'OR', 'ref': 'https://thorax.bmj.com/content/70/9/822'}]

        values = self.calculateCPDTable(bg_risk, variables)

        #u.makeGraph(copd)

        cpd_a = TabularCPD(variable='Past smoking', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Past smoking': ['Yes', 'No']})

        cpd_b = TabularCPD(variable='Current smoking', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Current smoking': ['Yes', 'No']})

        cpd_c = TabularCPD(variable='Asthma', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Asthma': ['Yes', 'No']})
            
        cpd__c = TabularCPD(variable='COPD', variable_card=2,
                        values=values,
                        #values=[[0.064, 0.096, 0.157, 0.237, 0.127, 0.191, 0.312, 0.47], [0.936, 0.904, 0.843, 0.763, 0.873, 0.809, 0.688, 0.53]],
                        evidence=['Past smoking', 'Current smoking', 'Asthma'],
                        evidence_card=[2, 2, 2],
                        state_names={'COPD': ['Yes', 'No'],
                            'Past smoking': ['No', 'Yes'],
                            'Current smoking': ['No', 'Yes'],
                            'Asthma': ['No', 'Yes'],
                        })

        # Associating the parameters with the model structure.
        copd.add_cpds(cpd_a,cpd_b,cpd_c, cpd__c)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if copd.check_model() else 'Model is incorrect'}")
        
        infer = VariableElimination(copd)
        q = infer.query(['COPD'], evidence={'Past smoking': 'Yes' if s == 1 else 'No', 'Current smoking': 'Yes' if s == 0 else 'No', 'Asthma': a}, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferDizziness(self, band, gender, o):
        dizziness = BayesianModel([('Female', 'Dizziness'), ('Osteoporosis', 'Dizziness')])

        #makeGraph(dizziness)

        bg_risk = (band['geriatricVulnerabilities']['dizziness'][gender] / 100) - 0.065 # Reduce to account for baseline risk

        variables = [{'name': 'Female', 'r': 1.18, 'll': 1.05, 'ul': 1.32, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/32655479/'}, {'name': 'Osteoporosis', 'r': 2.49, 'll': 1.39, 'ul': 4.46, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/32655479/'}]

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Female', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Female': ['Yes', 'No']})
            
        cpd_b = TabularCPD(variable='Osteoporosis', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Osteoporosis': ['Yes', 'No']})
            
        cpd__d = TabularCPD(variable='Dizziness', variable_card=2,
                        #values=[[0.11, 0.263, 0.155, 0.37], [0.89, 0.737, 0.845, 0.63]],
                        values=values,
                        evidence=['Female', 'Osteoporosis'],
                        evidence_card=[2, 2],
                        state_names={'Dizziness': ['Yes', 'No'],
                            'Female': ['No', 'Yes'],
                            'Osteoporosis': ['No', 'Yes'],
                        })

        # Associating the parameters with the model structure.
        dizziness.add_cpds(cpd_a,cpd_b, cpd__d)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if dizziness.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(dizziness)
        q = infer.query(['Dizziness'], evidence={'Female': 'Yes' if gender == 'f' else 'No', 'Osteoporosis': o}, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferFaecalIncontinence(self, band, gender, ui, d, h):
        faecal_incontinence = BayesianModel([('Urinary incontinence', 'Faecal incontinence'), ('Diabetes', 'Faecal incontinence'), ('Hypertension', 'Faecal incontinence')])

        bg_risk = band['geriatricVulnerabilities']['faecalIncontinence'][gender] / 100

        variables = [{'name': 'Urinary incontinence', 'r': 3.7, 'll': 1.59, 'ul': 21.02, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/26544818/'}, {'name': 'Diabetes', 'r': 2.3, 'll': 1.14, 'ul': 8.17, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/26544818/'}, {'name': 'Hypertension', 'r': 2.53, 'll': 1.2, 'ul': 4.9, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/26544818/'}]

        values = self.calculateCPDTable(bg_risk, variables)

        #u.makeGraph(faecal_incontinence)

        cpd_a = TabularCPD(variable='Urinary incontinence', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Urinary incontinence': ['Yes', 'No']})

        cpd_b = TabularCPD(variable='Diabetes', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Diabetes': ['Yes', 'No']})

        cpd_c = TabularCPD(variable='Hypertension', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Hypertension': ['Yes', 'No']})

        cpd__f = TabularCPD(variable='Faecal incontinence', variable_card=2,
                        #values=[[0.08, 0.135, 0.127, 0.182, 0.18, 0.235, 0.227, 0.282], [0.92, 0.865, 0.873, 0.818, 0.82, 0.765, 0.773, 0.718]],
                        values=values,
                        evidence=['Urinary incontinence', 'Diabetes', 'Hypertension'],
                        evidence_card=[2, 2, 2],
                        state_names={'Faecal incontinence': ['Yes', 'No'],
                            'Urinary incontinence': ['No', 'Yes'],
                            'Diabetes': ['No', 'Yes'],
                            'Hypertension': ['No', 'Yes'],
                        })

        # Associating the parameters with the model structure.
        faecal_incontinence.add_cpds(cpd_a,cpd_b,cpd_c, cpd__f)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if faecal_incontinence.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(faecal_incontinence)
        q = infer.query(['Faecal incontinence'], evidence={'Urinary incontinence': ui, 'Diabetes': d, 'Hypertension': h}, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferFootProblems(self, band, gender):
        foot_problems = BayesianModel([('Female', 'Foot problems')])

        bg_risk = band['geriatricVulnerabilities']['footProblems'][gender] / 100

        variables = [{'name': 'Female', 'r': 1.38, 'll': 1.15, 'ul': 1.66, 'ciType': 95, 'type': 'OR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2547889/'}]

        values = self.calculateCPDTable(bg_risk, variables)

        #u.makeGraph(foot_problems)

        cpd_a = TabularCPD(variable='Female', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Female': ['Yes', 'No']})
            
        cpd__f = TabularCPD(variable='Foot problems', variable_card=2,
                        #values=[[0.71, 0.77], [0.29, 0.23]],
                        values=values,
                        evidence=['Female'],
                        evidence_card=[2],
                        state_names={'Foot problems': ['Yes', 'No'],
                            'Female': ['No', 'Yes']
                        })


        # Associating the parameters with the model structure.
        foot_problems.add_cpds(cpd_a, cpd__f)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if foot_problems.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(foot_problems)
        q = infer.query(['Foot problems'], evidence={'Female': 'Yes' if gender == 'f' else 'No'}, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferLiverDisease(self, band, gender, o, a):
        liver_disease = BayesianModel([('Male', 'Liver disease'), ('Obese', 'Liver disease'), ('Alcohol use disorder', 'Liver disease')])

        bg_risk = band['geriatricVulnerabilities']['liverDisease'][gender] / 100

        variables = [{'name': 'Male', 'r': 1.599, 'll': 1.128, 'ul': 2.266, 'ciType': 95, 'type': 'OR', 'ref': 'https://bmjopengastro.bmj.com/content/7/1/e000524'}, {'name': 'Obese', 'r': 2.526, 'll': 1.383, 'ul': 4.614, 'ciType': 95, 'type': 'OR', 'ref': 'https://bmjopengastro.bmj.com/content/7/1/e000524'}, {'name': 'Alcohol use disorder', 'r': 5, 'll': 2.3, 'ul': 16.9, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/8621128/'}]

        values = self.calculateCPDTable(bg_risk, variables)

        #u.makeGraph(liver_disease)

        cpd_a = TabularCPD(variable='Male', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Male': ['Yes', 'No']})
            

        cpd_b = TabularCPD(variable='Obese', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Obese': ['Yes', 'No']})
            

        cpd_c = TabularCPD(variable='Alcohol use disorder', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Alcohol use disorder': ['Yes', 'No']})
            

        cpd__l = TabularCPD(variable='Liver disease', variable_card=2,
                        #values=[[0.022, 0.083, 0.037, 0.138, 0.028, 0.106, 0.047, 0.176], [0.978, 0.917, 0.963, 0.862, 0.972, 0.894, 0.953, 0.824]],
                        values=values,
                        evidence=['Male', 'Obese', 'Alcohol use disorder'],
                        evidence_card=[2, 2, 2],
                        state_names={'Liver disease': ['Yes', 'No'],
                            'Male': ['No', 'Yes'],
                            'Obese': ['No', 'Yes'],
                            'Alcohol use disorder': ['No', 'Yes'],
                        })

        # Associating the parameters with the model structure.
        liver_disease.add_cpds(cpd_a,cpd_b,cpd_c, cpd__l)

        # Checking if the cpds are valid for the model.
        # print(f"{'Model is okay' if liver_disease.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(liver_disease)
        q = infer.query(['Liver disease'], evidence={'Male': 'Yes' if gender == 'm' else 'No', 'Obese': o, 'Alcohol use disorder': a}, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferUlcers(self, band, gender, ui):
        ulcers = BayesianModel([('Urinary incontinence', 'Ulcers')])

        variables = [{'name': 'Urinary incontinence', 'r': 1.92, 'll': 1.54, 'ul': 2.38, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/24700170/'}]
        
        bg_risk = band['geriatricVulnerabilities']['ulcers'][gender] / 100

        values = self.calculateCPDTable(bg_risk, variables)

        #u.makeGraph(ulcers)

        cpd_a = TabularCPD(variable='Urinary incontinence', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Urinary incontinence': ['Yes', 'No']})
            
        cpd__u = TabularCPD(variable='Ulcers', variable_card=2,
                        #values=[[0.04, 0.07], [0.96, 0.93]],
                        values=values,
                        evidence=['Urinary incontinence'],
                        evidence_card=[2],
                        state_names={'Ulcers': ['Yes', 'No'],
                        'Urinary incontinence': ['No', 'Yes'],
                        })

        # Associating the parameters with the model structure.
        ulcers.add_cpds(cpd_a, cpd__u)

        # Checking if the cpds are valid for the model.
        # print(f"{'Model is okay' if ulcers.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(ulcers)
        q = infer.query(['Ulcers'], evidence={'Urinary incontinence': ui}, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferOrthostaticHypotension(self, band, gender, dm, h, p, d):
        orthostatic_hypotension = BayesianModel([('Diabetes', 'Orthostatic hypotension'), ('Hypertension', 'Orthostatic hypotension'), ('Parkinsons disease', 'Orthostatic hypotension'), ('Dementia', 'Orthostatic hypotension')])

        bg_risk = band['geriatricVulnerabilities']['orthostaticHypotension'][gender] / 100

        variables = [{'name': 'Diabetes', 'r': 1.081081081081081, 'll': 0.8558558558558559, 'ul': 1.2612612612612613, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33388038/'}, {'name': 'Hypertension', 'r': 1.4285714285714286, 'll': 1.1428571428571428, 'ul': 1.6428571428571428, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33388038/'}, {'name': 'Parkinsons disease', 'r': 1.7857142857142856, 'll': 1.2857142857142856, 'ul': 2.357142857142857, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33388038/'}, {'name': 'Dementia', 'r': 2.071428571428571, 'll': 1.7857142857142856, 'ul': 2.357142857142857, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33388038/'}]

        values = self.calculateCPDTable(bg_risk, variables)

        #u.makeGraph(orthostatic_hypotension)

        cpd_a = TabularCPD(variable='Diabetes', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Diabetes': ['Yes', 'No']})
            
        cpd_b = TabularCPD(variable='Hypertension', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Hypertension': ['Yes', 'No']})
            
        cpd_c = TabularCPD(variable='Parkinsons disease', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Parkinsons disease': ['Yes', 'No']})
            
        cpd_d = TabularCPD(variable='Dementia', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Dementia': ['Yes', 'No']})
            

        cpd__o = TabularCPD(variable='Orthostatic hypotension', variable_card=2,
                        #values=[[0.222, 0.372, 0.333, 0.558, 0.293, 0.491, 0.44, 0.737, 0.263, 0.44, 0.394, 0.66, 0.347, 0.581, 0.521, 0.872], [0.778, 0.628, 0.667, 0.442, 0.707, 0.509, 0.56, 0.263, 0.737, 0.56, 0.606, 0.34, 0.653, 0.419, 0.479, 0.128]],
                        values=values,
                        evidence=['Diabetes', 'Hypertension', 'Parkinsons disease', 'Dementia'],
                        evidence_card=[2, 2, 2, 2],
                        state_names={'Orthostatic hypotension': ['Yes', 'No'],
                            'Diabetes': ['No', 'Yes'],
                            'Hypertension': ['No', 'Yes'],
                            'Parkinsons disease': ['No', 'Yes'],
                            'Dementia': ['No', 'Yes'],
                        })


        # Associating the parameters with the model structure.
        orthostatic_hypotension.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d, cpd__o)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if orthostatic_hypotension.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(orthostatic_hypotension)
        q = infer.query(['Orthostatic hypotension'], evidence={'Diabetes': dm, 'Hypertension': h, 'Parkinsons disease': p, 'Dementia': d}, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0
    
    def inferHeartFailure(self, band, gender, o, h, d, s, m, a):
        heart_failure = BayesianModel([('Male', 'Heart failure'), ('Obesity', 'Heart failure'), ('Hypertension', 'Heart failure'), ('Diabetes', 'Heart failure'), ('Current smoker', 'Heart failure'), ('Myocardial infarction', 'Heart failure'), ('Atrial fibrillation', 'Heart failure')])

        bg_risk = band['geriatricVulnerabilities']['heartFailure'][gender] / 100

        variables = [{'name': 'Male', 'r': 1.65, 'll': 1.38, 'ul': 1.97, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7986583/'}, {'name': 'Obesity', 'r': 1.32, 'll': 1.09, 'ul': 1.6, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7986583/'}, {'name': 'Hypertension', 'r': 2.19, 'll': 1.76, 'ul': 2.73, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7986583/'}, {'name': 'Diabetes', 'r': 1.98, 'll': 1.59, 'ul': 2.46, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7986583/'}, {'name': 'Current smoker', 'r': 1.43, 'll': 1.15, 'ul': 1.77, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7986583/'}, {'name': 'Myocardial infarction', 'r': 2.92, 'll': 2.28, 'ul': 3.74, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7986583/'}, {'name': 'Atrial fibrillation', 'r': 2.62, 'll': 1.51, 'ul': 4.52, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7986583/'}]

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Male', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Male': ['Yes', 'No']})
            

        cpd_b = TabularCPD(variable='Obesity', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Obesity': ['Yes', 'No']})
            

        cpd_c = TabularCPD(variable='Hypertension', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Hypertension': ['Yes', 'No']})
            

        cpd_d = TabularCPD(variable='Diabetes', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Diabetes': ['Yes', 'No']})
            

        cpd_e = TabularCPD(variable='Current smoker', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Current smoker': ['Yes', 'No']})
            

        cpd_f = TabularCPD(variable='Myocardial infarction', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Myocardial infarction': ['Yes', 'No']})
            

        cpd_g = TabularCPD(variable='Atrial fibrillation', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Atrial fibrillation': ['Yes', 'No']})
            

        cpd__h = TabularCPD(variable='Heart failure', variable_card=2,
                        #values=[[0.06, 0.087, 0.093, 0.136, 0.069, 0.1, 0.107, 0.156, 0.076, 0.111, 0.119, 0.173, 0.087, 0.127, 0.136, 0.198, 0.08, 0.116, 0.124, 0.18, 0.091, 0.133, 0.142, 0.207, 0.101, 0.147, 0.157, 0.229, 0.116, 0.169, 0.18, 0.263, 0.068, 0.098, 0.105, 0.153, 0.077, 0.113, 0.12, 0.175, 0.086, 0.125, 0.134, 0.194, 0.098, 0.143, 0.153, 0.223, 0.09, 0.131, 0.139, 0.203, 0.103, 0.15, 0.16, 0.233, 0.114, 0.166, 0.177, 0.258, 0.131, 0.19, 0.203, 0.296, 0.072, 0.104, 0.111, 0.162, 0.082, 0.119, 0.128, 0.186, 0.091, 0.132, 0.141, 0.206, 0.104, 0.152, 0.162, 0.236, 0.095, 0.138, 0.148, 0.215, 0.109, 0.158, 0.169, 0.246, 0.121, 0.176, 0.188, 0.273, 0.138, 0.201, 0.215, 0.313, 0.081, 0.117, 0.125, 0.182, 0.092, 0.134, 0.144, 0.209, 0.102, 0.149, 0.159, 0.232, 0.117, 0.171, 0.183, 0.266, 0.107, 0.156, 0.166, 0.242, 0.123, 0.178, 0.191, 0.278, 0.136, 0.198, 0.211, 0.308, 0.156, 0.227, 0.242, 0.353], [0.94, 0.913, 0.907, 0.864, 0.931, 0.9, 0.893, 0.844, 0.924, 0.889, 0.881, 0.827, 0.913, 0.873, 0.864, 0.802, 0.92, 0.884, 0.876, 0.82, 0.909, 0.867, 0.858, 0.793, 0.899, 0.853, 0.843, 0.771, 0.884, 0.831, 0.82, 0.737, 0.932, 0.902, 0.895, 0.847, 0.923, 0.887, 0.88, 0.825, 0.914, 0.875, 0.866, 0.806, 0.902, 0.857, 0.847, 0.777, 0.91, 0.869, 0.861, 0.797, 0.897, 0.85, 0.84, 0.767, 0.886, 0.834, 0.823, 0.742, 0.869, 0.81, 0.797, 0.704, 0.928, 0.896, 0.889, 0.838, 0.918, 0.881, 0.872, 0.814, 0.909, 0.868, 0.859, 0.794, 0.896, 0.848, 0.838, 0.764, 0.905, 0.862, 0.852, 0.785, 0.891, 0.842, 0.831, 0.754, 0.879, 0.824, 0.812, 0.727, 0.862, 0.799, 0.785, 0.687, 0.919, 0.883, 0.875, 0.818, 0.908, 0.866, 0.856, 0.791, 0.898, 0.851, 0.841, 0.768, 0.883, 0.829, 0.817, 0.734, 0.893, 0.844, 0.834, 0.758, 0.877, 0.822, 0.809, 0.722, 0.864, 0.802, 0.789, 0.692, 0.844, 0.773, 0.758, 0.647]],
                        values=values,
                        evidence=['Male', 'Obesity', 'Hypertension', 'Diabetes', 'Current smoker', 'Myocardial infarction', 'Atrial fibrillation'],
                        evidence_card=[2, 2, 2, 2, 2, 2, 2],
                        state_names={'Heart failure': ['Yes', 'No'],
                            'Male': ['No', 'Yes'],
                            'Obesity': ['No', 'Yes'],
                            'Hypertension': ['No', 'Yes'],
                            'Diabetes': ['No', 'Yes'],
                            'Current smoker': ['No', 'Yes'],
                            'Myocardial infarction': ['No', 'Yes'],
                            'Atrial fibrillation': ['No', 'Yes'],
                        })

        # Associating the parameters with the model structure.
        heart_failure.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d,cpd_e,cpd_f,cpd_g, cpd__h)

        # Checking if the cpds are valid for the model.
        # print(f"{'Model is okay' if heart_failure.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(heart_failure)
        q = infer.query(['Heart failure'], evidence={'Male': 'Yes' if gender == 1 else 'No', 'Obesity': o, 'Hypertension': h, 'Diabetes': d, 'Current smoker': s, 'Myocardial infarction': m, 'Atrial fibrillation': a }, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferFrailty(self, band, gender, hl, dm, visual, comorb, cv, copd):
        frailty = BayesianModel([('Hearing loss', 'Frailty'), ('Diabetes', 'Frailty'), ('Visual impairment', 'Frailty'), ('Comorbidity >= 3', 'Frailty'), ('Cardiovascular disease', 'Frailty'), ('COPD', 'Frailty')])

        bg_risk = band['geriatricVulnerabilities']['frailty'][gender] / 100

        variables = [{'name': 'Hearing loss', 'r': 1.87, 'll': 1.63, 'ul': 2.13, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/34034656/'}, {'name': 'Diabetes', 'r': 1.61, 'll': 1.47, 'ul': 1.77, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/34022743/'}, {'name': 'Visual impairment', 'r': 2.75, 'll': 2.5, 'ul': 3, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/32735331/'}, {'name': 'Comorbidity >= 3', 'r': 1.97, 'll': 1.78, 'ul': 2.18, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/31021361/'}, {'name': 'Cardiovascular disease', 'r': 4, 'll': 1.83, 'ul': 4.12, 'ciType': 95, 'type': 'RR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6108388/'}, {'name': 'COPD', 'r': 1.97, 'll': 1.53, 'ul': 2.53, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/29477493/'}]
        
        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Hearing loss', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Hearing loss': ['Yes', 'No']})
            

        cpd_b = TabularCPD(variable='Diabetes', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Diabetes': ['Yes', 'No']})
            

        cpd_c = TabularCPD(variable='Visual impairment', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Visual impairment': ['Yes', 'No']})
            

        cpd_e = TabularCPD(variable='Comorbidity >= 3', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Comorbidity >= 3': ['Yes', 'No']})
            

        cpd_g = TabularCPD(variable='Cardiovascular disease', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Cardiovascular disease': ['Yes', 'No']})
            

        cpd_i = TabularCPD(variable='COPD', variable_card=2,
                                values=[[0],[1]],
                                state_names={'COPD': ['Yes', 'No']})
            

        cpd__f = TabularCPD(variable='Frailty', variable_card=2,
                        #values=[[0.5, 0.577, 0.552, 0.637, 0.557, 0.643, 0.616, 0.71, 0.974, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.556, 0.642, 0.615, 0.709, 0.62, 0.715, 0.685, 0.79, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.552, 0.637, 0.61, 0.704, 0.616, 0.71, 0.68, 0.785, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.615, 0.709, 0.679, 0.784, 0.685, 0.79, 0.757, 0.873, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.547, 0.631, 0.604, 0.697, 0.61, 0.703, 0.674, 0.777, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.609, 0.702, 0.673, 0.776, 0.679, 0.783, 0.75, 0.865, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.604, 0.697, 0.668, 0.77, 0.674, 0.777, 0.744, 0.859, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.673, 0.776, 0.743, 0.857, 0.75, 0.865, 0.828, 0.956, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.564, 0.651, 0.623, 0.719, 0.629, 0.725, 0.695, 0.801, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.628, 0.724, 0.694, 0.8, 0.7, 0.807, 0.773, 0.892, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.623, 0.719, 0.689, 0.794, 0.695, 0.801, 0.767, 0.885, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.694, 0.8, 0.766, 0.884, 0.773, 0.892, 0.854, 0.985, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.617, 0.712, 0.682, 0.787, 0.688, 0.793, 0.76, 0.877, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.687, 0.792, 0.759, 0.875, 0.765, 0.883, 0.846, 0.976, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.682, 0.787, 0.753, 0.869, 0.76, 0.877, 0.84, 0.969, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.759, 0.875, 0.838, 0.967, 0.846, 0.976, 0.934, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.545, 0.629, 0.602, 0.694, 0.607, 0.701, 0.671, 0.774, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.606, 0.7, 0.67, 0.773, 0.676, 0.78, 0.747, 0.861, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.602, 0.694, 0.665, 0.767, 0.671, 0.774, 0.741, 0.855, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.67, 0.773, 0.74, 0.854, 0.747, 0.861, 0.825, 0.952, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.596, 0.688, 0.659, 0.76, 0.664, 0.766, 0.734, 0.847, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.663, 0.765, 0.733, 0.846, 0.739, 0.853, 0.817, 0.942, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.659, 0.76, 0.728, 0.839, 0.734, 0.847, 0.811, 0.936, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.733, 0.846, 0.81, 0.934, 0.817, 0.942, 0.903, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.615, 0.709, 0.679, 0.783, 0.685, 0.79, 0.757, 0.873, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.684, 0.789, 0.756, 0.872, 0.762, 0.879, 0.842, 0.972, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.679, 0.783, 0.75, 0.866, 0.757, 0.873, 0.836, 0.965, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.756, 0.872, 0.835, 0.963, 0.842, 0.972, 0.931, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.672, 0.776, 0.743, 0.857, 0.749, 0.865, 0.828, 0.955, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.748, 0.863, 0.827, 0.954, 0.834, 0.962, 0.922, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.743, 0.857, 0.821, 0.947, 0.828, 0.955, 0.915, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.827, 0.954, 0.914, 0.999, 0.922, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.604, 0.696, 0.667, 0.769, 0.673, 0.776, 0.743, 0.858, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.672, 0.775, 0.742, 0.856, 0.749, 0.864, 0.827, 0.954, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.667, 0.769, 0.737, 0.85, 0.743, 0.858, 0.821, 0.947, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.742, 0.856, 0.82, 0.946, 0.827, 0.954, 0.914, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.66, 0.762, 0.73, 0.842, 0.736, 0.849, 0.813, 0.938, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.735, 0.848, 0.812, 0.937, 0.819, 0.945, 0.905, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.73, 0.842, 0.806, 0.93, 0.813, 0.938, 0.899, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.812, 0.937, 0.897, 0.999, 0.905, 0.999, 1.0, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.681, 0.786, 0.752, 0.868, 0.759, 0.876, 0.839, 0.967, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.758, 0.874, 0.837, 0.966, 0.845, 0.974, 0.933, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.752, 0.868, 0.831, 0.959, 0.839, 0.967, 0.926, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.837, 0.966, 0.925, 0.999, 0.933, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.745, 0.86, 0.823, 0.95, 0.83, 0.958, 0.917, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.829, 0.957, 0.916, 0.999, 0.924, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.823, 0.95, 0.909, 0.999, 0.917, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.916, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.658, 0.759, 0.727, 0.838, 0.733, 0.846, 0.81, 0.934, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.732, 0.845, 0.809, 0.933, 0.816, 0.941, 0.901, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.727, 0.838, 0.803, 0.926, 0.81, 0.934, 0.895, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.809, 0.933, 0.894, 0.999, 0.901, 0.999, 0.996, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.72, 0.83, 0.795, 0.917, 0.802, 0.925, 0.886, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.801, 0.924, 0.885, 0.999, 0.893, 0.999, 0.986, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.795, 0.917, 0.879, 0.999, 0.886, 0.999, 0.979, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.885, 0.999, 0.978, 0.999, 0.986, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.742, 0.856, 0.82, 0.946, 0.827, 0.954, 0.914, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.826, 0.953, 0.912, 0.999, 0.92, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.82, 0.946, 0.906, 0.999, 0.914, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.912, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.812, 0.937, 0.897, 0.999, 0.905, 0.999, 1.0, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.904, 0.999, 0.998, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.897, 0.999, 0.991, 0.999, 1.0, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.998, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999], [0.5, 0.423, 0.448, 0.363, 0.443, 0.357, 0.384, 0.29, 0.026, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.444, 0.358, 0.385, 0.291, 0.38, 0.285, 0.315, 0.21, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.448, 0.363, 0.39, 0.296, 0.384, 0.29, 0.32, 0.215, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.385, 0.291, 0.321, 0.216, 0.315, 0.21, 0.243, 0.127, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.453, 0.369, 0.396, 0.303, 0.39, 0.297, 0.326, 0.223, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.391, 0.298, 0.327, 0.224, 0.321, 0.217, 0.25, 0.135, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.396, 0.303, 0.332, 0.23, 0.326, 0.223, 0.256, 0.141, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.327, 0.224, 0.257, 0.143, 0.25, 0.135, 0.172, 0.044, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.436, 0.349, 0.377, 0.281, 0.371, 0.275, 0.305, 0.199, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.372, 0.276, 0.306, 0.2, 0.3, 0.193, 0.227, 0.108, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.377, 0.281, 0.311, 0.206, 0.305, 0.199, 0.233, 0.115, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.306, 0.2, 0.234, 0.116, 0.227, 0.108, 0.146, 0.015, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.383, 0.288, 0.318, 0.213, 0.312, 0.207, 0.24, 0.123, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.313, 0.208, 0.241, 0.125, 0.235, 0.117, 0.154, 0.024, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.318, 0.213, 0.247, 0.131, 0.24, 0.123, 0.16, 0.031, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.241, 0.125, 0.162, 0.033, 0.154, 0.024, 0.066, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.455, 0.371, 0.398, 0.306, 0.393, 0.299, 0.329, 0.226, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.394, 0.3, 0.33, 0.227, 0.324, 0.22, 0.253, 0.139, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.398, 0.306, 0.335, 0.233, 0.329, 0.226, 0.259, 0.145, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.33, 0.227, 0.26, 0.146, 0.253, 0.139, 0.175, 0.048, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.404, 0.312, 0.341, 0.24, 0.336, 0.234, 0.266, 0.153, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.337, 0.235, 0.267, 0.154, 0.261, 0.147, 0.183, 0.058, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.341, 0.24, 0.272, 0.161, 0.266, 0.153, 0.189, 0.064, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.267, 0.154, 0.19, 0.066, 0.183, 0.058, 0.097, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.385, 0.291, 0.321, 0.217, 0.315, 0.21, 0.243, 0.127, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.316, 0.211, 0.244, 0.128, 0.238, 0.121, 0.158, 0.028, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.321, 0.217, 0.25, 0.134, 0.243, 0.127, 0.164, 0.035, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.244, 0.128, 0.165, 0.037, 0.158, 0.028, 0.069, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.328, 0.224, 0.257, 0.143, 0.251, 0.135, 0.172, 0.045, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.252, 0.137, 0.173, 0.046, 0.166, 0.038, 0.078, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.257, 0.143, 0.179, 0.053, 0.172, 0.045, 0.085, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.173, 0.046, 0.086, 0.001, 0.078, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.396, 0.304, 0.333, 0.231, 0.327, 0.224, 0.257, 0.142, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.328, 0.225, 0.258, 0.144, 0.251, 0.136, 0.173, 0.046, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.333, 0.231, 0.263, 0.15, 0.257, 0.142, 0.179, 0.053, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.258, 0.144, 0.18, 0.054, 0.173, 0.046, 0.086, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.34, 0.238, 0.27, 0.158, 0.264, 0.151, 0.187, 0.062, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.265, 0.152, 0.188, 0.063, 0.181, 0.055, 0.095, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.27, 0.158, 0.194, 0.07, 0.187, 0.062, 0.101, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.188, 0.063, 0.103, 0.001, 0.095, 0.001, 0.0, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.319, 0.214, 0.248, 0.132, 0.241, 0.124, 0.161, 0.033, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.242, 0.126, 0.163, 0.034, 0.155, 0.026, 0.067, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.248, 0.132, 0.169, 0.041, 0.161, 0.033, 0.074, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.163, 0.034, 0.075, 0.001, 0.067, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.255, 0.14, 0.177, 0.05, 0.17, 0.042, 0.083, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.171, 0.043, 0.084, 0.001, 0.076, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.177, 0.05, 0.091, 0.001, 0.083, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.084, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.342, 0.241, 0.273, 0.162, 0.267, 0.154, 0.19, 0.066, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.268, 0.155, 0.191, 0.067, 0.184, 0.059, 0.099, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.273, 0.162, 0.197, 0.074, 0.19, 0.066, 0.105, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.191, 0.067, 0.106, 0.001, 0.099, 0.001, 0.004, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.28, 0.17, 0.205, 0.083, 0.198, 0.075, 0.114, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.199, 0.076, 0.115, 0.001, 0.107, 0.001, 0.014, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.205, 0.083, 0.121, 0.001, 0.114, 0.001, 0.021, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.115, 0.001, 0.022, 0.001, 0.014, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.258, 0.144, 0.18, 0.054, 0.173, 0.046, 0.086, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.174, 0.047, 0.088, 0.001, 0.08, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.18, 0.054, 0.094, 0.001, 0.086, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.088, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.188, 0.063, 0.103, 0.001, 0.095, 0.001, 0.0, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.096, 0.001, 0.002, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.103, 0.001, 0.009, 0.001, 0.0, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.002, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]],
                        values=values,
                        evidence=['Hearing loss', 'Diabetes', 'Visual impairment', 'Comorbidity >= 3', 'Cardiovascular disease', 'COPD'],
                        evidence_card=[2, 2, 2, 2, 2, 2],
                        state_names={'Frailty': ['Yes', 'No'],
                            'Hearing loss': ['No', 'Yes'],
                            'Diabetes': ['No', 'Yes'],
                            'Visual impairment': ['No', 'Yes'],
                            'Comorbidity >= 3': ['No', 'Yes'],
                            'Cardiovascular disease': ['No', 'Yes'],
                            'COPD': ['No', 'Yes']
                        })

        # Associating the parameters with the model structure.
        frailty.add_cpds(cpd_a,cpd_b,cpd_c,cpd_e,cpd_g,cpd_i, cpd__f)

        # Checking if the cpds are valid for the model.
        # print(f"{'Model is okay' if frailty.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(frailty)
        q = infer.query(['Frailty'], evidence={'Hearing loss': hl, 'Diabetes': dm, 'Visual impairment': visual, 'Comorbidity >= 3': comorb, 'Cardiovascular disease': cv, 'COPD': copd }, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferBadlDisability(self, band, gender, dm, bmi1, bmi2, f):
        badl_disability = BayesianModel([('Diabetes', 'BADL disability'), ('BMI > 30 < 35', 'BADL disability'), ('BMI >= 35.0 < 40', 'BADL disability'), ('Frailty', 'BADL disability')])

        bg_risk = (band['geriatricVulnerabilities']['badlImpairment'][gender] / 100) - 0.12 # Correct for true prevalence

        variables = [{'name': 'Diabetes', 'r': 1.82, 'll': 1.4, 'ul': 2.36, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/24622316/'}, {'name': 'BMI > 30 < 35', 'r': 1.16, 'll': 1.11, 'ul': 1.21, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/22212629/'}, {'name': 'BMI >= 35.0 < 40', 'r': 1.16, 'll': 1.11, 'ul': 1.21, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/22212629/'}, {'name': 'Frailty', 'r': 2.76, 'll': 2.23, 'ul': 3.44, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/27558741/'}]
        
        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Diabetes', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Diabetes': ['Yes', 'No']})
            

        cpd_b = TabularCPD(variable='BMI > 30 < 35', variable_card=2,
                                values=[[0],[1]],
                                state_names={'BMI > 30 < 35': ['Yes', 'No']})
            

        cpd_c = TabularCPD(variable='BMI >= 35.0 < 40', variable_card=2,
                                values=[[0],[1]],
                                state_names={'BMI >= 35.0 < 40': ['Yes', 'No']})
            

        cpd_d = TabularCPD(variable='Frailty', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Frailty': ['Yes', 'No']})
            

        cpd__b = TabularCPD(variable='BADL disability', variable_card=2,
                        #values=[[0.367, 0.563, 0.451, 0.692, 0.451, 0.692, 0.554, 0.851, 0.503, 0.772, 0.619, 0.949, 0.619, 0.949, 0.76, 0.999], [0.633, 0.437, 0.549, 0.308, 0.549, 0.308, 0.446, 0.149, 0.497, 0.228, 0.381, 0.051, 0.381, 0.051, 0.24, 0.001]],
                        values=values,
                        evidence=['Diabetes', 'BMI > 30 < 35', 'BMI >= 35.0 < 40', 'Frailty'],
                        evidence_card=[2, 2, 2, 2],
                        state_names={'BADL disability': ['Yes', 'No'],
                            'Diabetes': ['No', 'Yes'],
                            'BMI > 30 < 35': ['No', 'Yes'],
                            'BMI >= 35.0 < 40': ['No', 'Yes'],
                            'Frailty': ['No', 'Yes'],
                        })


        # Associating the parameters with the model structure.
        badl_disability.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d, cpd__b)

        # Checking if the cpds are valid for the model.
        # print(f"{'Model is okay' if badl_disability.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(badl_disability)
        q = infer.query(['BADL disability'], evidence={'Diabetes': dm, 'BMI > 30 < 35': bmi1, 'BMI >= 35.0 < 40': bmi2, 'Frailty': f}, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferDepression(self, band, gender, fr, oa, badl, pd, hf):

        depression = BayesianModel([('Frailty', 'Depression'), ('Osteoarthritis', 'Depression'), ('BADL Dependency', 'Depression'), ('Parkinsons disease', 'Depression'), ('Heart failure', 'Depression')])

        bg_risk = (band['geriatricVulnerabilities']['depression'][gender] / 100) - 0.10

        variables = [{'name': 'Frailty', 'r': 2.64, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/28366616/'}, {'name': 'Osteoarthritis', 'r': 1.17, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/26795974/'}, {'name': 'BADL Dependency', 'r': 1.86, 'type': 'OR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3349051/'}, {'name': 'Parkinsons disease', 'r': 1.32, 'll': 1.16, 'ul': 1.44, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/15879342/'}, {'name': 'Heart failure', 'r': 1.676, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/34006389/'}]

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Frailty', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Frailty': ['Yes', 'No']})
            
        cpd_b = TabularCPD(variable='Osteoarthritis', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Osteoarthritis': ['Yes', 'No']})
            
        cpd_d = TabularCPD(variable='BADL Dependency', variable_card=2,
                                values=[[0],[1]],
                                state_names={'BADL Dependency': ['Yes', 'No']})

        cpd_e = TabularCPD(variable='Parkinsons disease', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Parkinsons disease': ['Yes', 'No']})
            
        cpd_g = TabularCPD(variable='Heart failure', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Heart failure': ['Yes', 'No']})
            
        cpd__d = TabularCPD(variable='Depression', variable_card=2,
            #values=[[0.25, 0.319, 0.293, 0.374, 0.298, 0.381, 0.35, 0.447, 0.308, 0.393, 0.361, 0.461, 0.367, 0.469, 0.43, 0.55, 0.284, 0.362, 0.333, 0.425, 0.339, 0.432, 0.397, 0.507, 0.349, 0.446, 0.409, 0.523, 0.417, 0.532, 0.488, 0.624, 0.284, 0.362, 0.333, 0.425, 0.339, 0.432, 0.397, 0.507, 0.349, 0.446, 0.409, 0.523, 0.417, 0.532, 0.488, 0.624, 0.322, 0.411, 0.377, 0.482, 0.384, 0.491, 0.45, 0.575, 0.396, 0.506, 0.465, 0.593, 0.473, 0.604, 0.554, 0.708, 0.336, 0.429, 0.394, 0.503, 0.401, 0.512, 0.47, 0.601, 0.414, 0.529, 0.485, 0.619, 0.494, 0.631, 0.579, 0.739, 0.382, 0.487, 0.447, 0.571, 0.455, 0.582, 0.534, 0.682, 0.47, 0.6, 0.551, 0.703, 0.561, 0.716, 0.657, 0.839, 0.382, 0.487, 0.447, 0.571, 0.455, 0.582, 0.534, 0.682, 0.47, 0.6, 0.551, 0.703, 0.561, 0.716, 0.657, 0.839, 0.433, 0.553, 0.508, 0.648, 0.517, 0.66, 0.606, 0.774, 0.533, 0.681, 0.625, 0.798, 0.636, 0.813, 0.746, 0.952], [0.75, 0.681, 0.707, 0.626, 0.702, 0.619, 0.65, 0.553, 0.692, 0.607, 0.639, 0.539, 0.633, 0.531, 0.57, 0.45, 0.716, 0.638, 0.667, 0.575, 0.661, 0.568, 0.603, 0.493, 0.651, 0.554, 0.591, 0.477, 0.583, 0.468, 0.512, 0.376, 0.716, 0.638, 0.667, 0.575, 0.661, 0.568, 0.603, 0.493, 0.651, 0.554, 0.591, 0.477, 0.583, 0.468, 0.512, 0.376, 0.678, 0.589, 0.623, 0.518, 0.616, 0.509, 0.55, 0.425, 0.604, 0.494, 0.535, 0.407, 0.527, 0.396, 0.446, 0.292, 0.664, 0.571, 0.606, 0.497, 0.599, 0.488, 0.53, 0.399, 0.586, 0.471, 0.515, 0.381, 0.506, 0.369, 0.421, 0.261, 0.618, 0.513, 0.553, 0.429, 0.545, 0.418, 0.466, 0.318, 0.53, 0.4, 0.449, 0.297, 0.439, 0.284, 0.343, 0.161, 0.618, 0.513, 0.553, 0.429, 0.545, 0.418, 0.466, 0.318, 0.53, 0.4, 0.449, 0.297, 0.439, 0.284, 0.343, 0.161, 0.567, 0.447, 0.492, 0.352, 0.483, 0.34, 0.394, 0.226, 0.467, 0.319, 0.375, 0.202, 0.364, 0.187, 0.254, 0.048]],
            values=values,
            evidence=['Frailty', 'Osteoarthritis', 'BADL Dependency', 'Parkinsons disease', 'Heart failure'],
            evidence_card=[2, 2, 2, 2, 2],
            state_names={'Depression': ['Yes', 'No'],
                'Frailty': ['No', 'Yes'],
                'Osteoarthritis': ['No', 'Yes'],
                'BADL Dependency': ['No', 'Yes'],
                'Parkinsons disease': ['No', 'Yes'],
                'Heart failure': ['No', 'Yes'],
            })

        # Associating the parameters with the model structure.
        depression.add_cpds(cpd_a,cpd_b,cpd_d,cpd_e,cpd_g, cpd__d)

        # Checking if the cpds are valid for the model.
        # print(f"{'Model is okay' if depression.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(depression)
        q = infer.query(['Depression'], evidence={'Frailty': fr, 'Osteoarthritis': oa, 'BADL Dependency': badl, 'Parkinsons disease': pd, 'Heart failure': hf}, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferAlcoholUseDisorder(self, band, gender, depression):
        alcohol_use_disorder = BayesianModel([('Depression', 'Alcohol use disorder')])

        bg_risk = band['geriatricVulnerabilities']['aud'][gender] / 100

        variables = [{'name': 'Depression', 'r': 1.75, 'll': 1.5, 'ul': 2.0, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/17606817/'}]

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Depression', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Depression': ['Yes', 'No']})

        cpd__a = TabularCPD(variable='Alcohol use disorder', variable_card=2,
                        #values=[[0.178, 0.27], [0.82, 0.73]],
                        values=values,
                        evidence=['Depression'],
                        evidence_card=[2],
                        state_names={'Alcohol use disorder': ['Yes', 'No'],
                                    'Depression': ['No', 'Yes']})

        # Associating the parameters with the model structure.
        alcohol_use_disorder.add_cpds(cpd_a, cpd__a)

        # Checking if the cpds are valid for the model.
        # print(f"{'Model is okay' if alcohol_use_disorder.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(alcohol_use_disorder)
        q = infer.query(['Alcohol use disorder'], evidence={'Depression': depression}, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferSleepDisturbance(self, band, gender, dep, htn, hd, dm, pu, asthma, copd):

        bg_risk = (band['geriatricVulnerabilities']['sleepDisturbance'][gender] / 100) - 0.2 # Reducing this slighty as very high baseline prevalence

        variables = [{'name': 'Depression', 'r': 1.72, 'll': 1.33, 'ul': 2.22, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/28179129/'}, {'name': 'Hypertension', 'r': 1.5, 'll': 1.2, 'ul': 1.5, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/21731135/'}, {'name': 'Heart disease', 'r': 1.6, 'll': 1.2, 'ul': 2.3, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/21731135/'}, {'name': 'Diabetes', 'r': 1.4, 'll': 1.05, 'ul': 2, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/21731135/'}, {'name': 'Peptic ulcer', 'r': 2.1, 'll': 1.6, 'ul': 2.7, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/21731135/'}, {'name': 'Asthma', 'r': 1.6, 'll': 1.3, 'ul': 2, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/21731135/'}, {'name': 'COPD', 'r': 1.9, 'll': 1.5, 'ul': 2.5, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/21731135/'}]

        values = self.calculateCPDTable(bg_risk, variables)

        sleep_disturbance = BayesianModel([('Depression', 'Sleep disturbance'), ('Hypertension', 'Sleep disturbance'), ('Heart disease', 'Sleep disturbance'), ('Diabetes', 'Sleep disturbance'), ('Peptic ulcer', 'Sleep disturbance'), ('Asthma', 'Sleep disturbance'), ('COPD', 'Sleep disturbance')])

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
                        #values=[[0.64, 0.747, 0.739, 0.863, 0.751, 0.877, 0.867, 0.999, 0.73, 0.853, 0.843, 0.984, 0.857, 0.999, 0.989, 0.999, 0.739, 0.863, 0.852, 0.995, 0.867, 0.999, 0.999, 0.999, 0.843, 0.984, 0.973, 0.999, 0.989, 0.999, 0.999, 0.999, 0.735, 0.859, 0.849, 0.991, 0.863, 0.999, 0.996, 0.999, 0.839, 0.98, 0.968, 0.999, 0.984, 0.999, 0.999, 0.999, 0.849, 0.991, 0.979, 0.999, 0.996, 0.999, 0.999, 0.999, 0.968, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.857, 0.999, 0.989, 0.999, 0.999, 0.999, 0.999, 0.999, 0.978, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.989, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.984, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999], [0.36, 0.253, 0.261, 0.137, 0.249, 0.123, 0.133, 0.001, 0.27, 0.147, 0.157, 0.016, 0.143, 0.001, 0.011, 0.001, 0.261, 0.137, 0.148, 0.005, 0.133, 0.001, 0.001, 0.001, 0.157, 0.016, 0.027, 0.001, 0.011, 0.001, 0.001, 0.001, 0.265, 0.141, 0.151, 0.009, 0.137, 0.001, 0.004, 0.001, 0.161, 0.02, 0.032, 0.001, 0.016, 0.001, 0.001, 0.001, 0.151, 0.009, 0.021, 0.001, 0.004, 0.001, 0.001, 0.001, 0.032, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.143, 0.001, 0.011, 0.001, 0.001, 0.001, 0.001, 0.001, 0.022, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.011, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.016, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]],
                        values=values,
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
                            })


        # Associating the parameters with the model structure.
        sleep_disturbance.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d,cpd_e,cpd_f,cpd_g, cpd__s)

        # Checking if the cpds are valid for the model.
        # print(f"{'Model is okay' if sleep_disturbance.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(sleep_disturbance)
        q = infer.query(['Sleep disturbance'], evidence={'Depression': dep, 'Hypertension': htn, 'Heart disease': hd, 'Diabetes': dm, 'Peptic ulcer': pu, 'Asthma': asthma, 'COPD': copd }, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferSyncope(self, band, gender, cva, tia, htn):

        syncope = BayesianModel([('Stroke', 'Syncope'), ('TIA', 'Syncope'), ('Hypertension', 'Syncope')])

        bg_risk = band['geriatricVulnerabilities']['syncope'][gender] / 100

        variables = [{'name': 'Stroke', 'r': 2.56, 'll': 1.62, 'ul': 4.04, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/10801999/'}, {'name': 'TIA', 'r': 2.56, 'll': 1.62, 'ul': 4.04, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/10801999/'}, {'name': 'Hypertension', 'r': 1.46, 'll': 1.14, 'ul': 1.88, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/10801999/'}]

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Stroke', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Stroke': ['Yes', 'No']})
            

        cpd_b = TabularCPD(variable='TIA', variable_card=2,
                                values=[[0],[1]],
                                state_names={'TIA': ['Yes', 'No']})
            

        cpd_c = TabularCPD(variable='Hypertension', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Hypertension': ['Yes', 'No']})
            

        cpd__s = TabularCPD(variable='Syncope', variable_card=2,
                        #values=[[0.0474, 0.063, 0.091, 0.121, 0.091, 0.121, 0.174, 0.231], [0.953, 0.937, 0.909, 0.879, 0.909, 0.879, 0.826, 0.769]],
                        values=values,
                        evidence=['Stroke', 'TIA', 'Hypertension'],
                        evidence_card=[2, 2, 2],
                        state_names={'Syncope': ['Yes', 'No'],
                            'Stroke': ['No', 'Yes'],
                            'TIA': ['No', 'Yes'],
                            'Hypertension': ['No', 'Yes'],
                        })


        # Associating the parameters with the model structure.
        syncope.add_cpds(cpd_a,cpd_b,cpd_c, cpd__s)

        # Checking if the cpds are valid for the model.
        # print(f"{'Model is okay' if syncope.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(syncope)
        q = infer.query(['Syncope'], evidence={'Stroke': cva, 'TIA': tia, 'Hypertension': htn}, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferIadlDisability(self, band, gender, f, dm, sleep):

        iadl_dependency = BayesianModel([('Frailty', 'IADL dependency'), ('Diabetes', 'IADL dependency'), ('Sleep disturbance', 'IADL dependency')])

        bg_risk = (band['geriatricVulnerabilities']['iadlImpairment'][gender] / 100) - 0.27

        variables = [{'name': 'Frailty', 'r': 3.62, 'll': 2.32, 'ul': 5.64, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/27558741/'}, {'name': 'Diabetes', 'r': 1.65, 'll': 1.55, 'ul': 1.74, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/24622316/'}, {'name': 'Sleep disturbance', 'r': 1.36, 'll': 1.11, 'ul': 1.68, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/29530908/'}]

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Frailty', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Frailty': ['Yes', 'No']})
            

        cpd_b = TabularCPD(variable='Diabetes', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Diabetes': ['Yes', 'No']})
            

        cpd_e = TabularCPD(variable='Sleep disturbance', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Sleep disturbance': ['Yes', 'No']})
            

        cpd__i = TabularCPD(variable='IADL dependency', variable_card=2,
                        #values=[[0.546, 0.656, 0.678, 0.815, 0.7, 0.841, 0.87, 0.999, 0.672, 0.807, 0.835, 0.999, 0.862, 0.999, 0.999, 0.999, 0.734, 0.882, 0.912, 0.999, 0.941, 0.999, 0.999, 0.999, 0.903, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999], [0.454, 0.344, 0.322, 0.185, 0.3, 0.159, 0.13, 0.001, 0.328, 0.193, 0.165, 0.001, 0.138, 0.001, 0.001, 0.001, 0.266, 0.118, 0.088, 0.001, 0.059, 0.001, 0.001, 0.001, 0.097, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]],
                        values=values,
                        evidence=['Frailty', 'Diabetes', 'Sleep disturbance'],
                        evidence_card=[2, 2, 2],
                        state_names={'IADL dependency': ['Yes', 'No'],
                            'Frailty': ['No', 'Yes'],
                            'Diabetes': ['No', 'Yes'],
                            'Sleep disturbance': ['No', 'Yes'],
                        })

        # Associating the parameters with the model structure.
        iadl_dependency.add_cpds(cpd_a,cpd_b,cpd_e, cpd__i)

        # Checking if the cpds are valid for the model.
        # print(f"{'Model is okay' if iadl_dependency.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(iadl_dependency)
        q = infer.query(['IADL dependency'], evidence={'Frailty': f, 'Diabetes': dm, 'Sleep disturbance': sleep}, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferPVD(self, band, gender, dm, smoking, htn, mi, angina, hf, cva, tia):

        peripheral_vascular_disease = BayesianModel([('Diabetes', 'Peripheral vascular disease'), ('Current smoker', 'Peripheral vascular disease'), ('Former smoker', 'Peripheral vascular disease'), ('Hypertension', 'Peripheral vascular disease'), ('Myocardial infarction', 'Peripheral vascular disease'), ('Angina', 'Peripheral vascular disease'), ('Heart failure', 'Peripheral vascular disease'), ('Stroke', 'Peripheral vascular disease'), ('TIA', 'Peripheral vascular disease')])

        bg_risk = band['geriatricVulnerabilities']['pvd'][gender] / 100

        variables = [{'name': 'Diabetes', 'r': 1.9, 'll': 1.29, 'ul': 2.86, 'ciType': 95, 'type': 'RR', 'ref': 'https://cardiab.biomedcentral.com/articles/10.1186/s12933-020-01130-4'}, {'name': 'Current smoker', 'r': 2.69, 'll': 1.67, 'ul': 4.33, 'ciType': 95, 'type': 'OR', 'ref': 'https://www.ahajournals.org/doi/10.1161/CIRCRESAHA.116.303849'}, {'name': 'Former smoker', 'r': 1.15, 'll': 0.75, 'ul': 1.78, 'ciType': 95, 'type': 'OR', 'ref': 'https://www.ahajournals.org/doi/10.1161/CIRCRESAHA.116.303849'}, {'name': 'Hypertension', 'r': 1.85, 'll': 1.5, 'ul': 2.2, 'ciType': 95, 'type': 'OR', 'ref': 'https://www.ahajournals.org/doi/10.1161/CIRCRESAHA.116.303849'}, {'name': 'Myocardial infarction', 'r': 2.1, 'ciType': 95, 'type': 'RR', 'ref': 'https://www.ahajournals.org/doi/10.1161/CIRCRESAHA.116.303849'}, {'name': 'Angina', 'r': 1.7, 'ciType': 95, 'type': 'RR', 'ref': 'https://www.ahajournals.org/doi/10.1161/CIRCRESAHA.116.303849'}, {'name': 'Heart failure', 'r': 12.6, 'ciType': 95, 'type': 'RR', 'ref': 'https://www.ahajournals.org/doi/10.1161/CIRCRESAHA.116.303849'}, {'name': 'Stroke', 'r': 2.4, 'ciType': 95, 'type': 'RR', 'ref': 'https://www.ahajournals.org/doi/10.1161/CIRCRESAHA.116.303849'}, {'name': 'TIA', 'r': 2.1, 'ciType': 95, 'type': 'RR', 'ref': 'https://www.ahajournals.org/doi/10.1161/CIRCRESAHA.116.303849'}]

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Diabetes', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Diabetes': ['Yes', 'No']})

        cpd_b = TabularCPD(variable='Current smoker', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Current smoker': ['Yes', 'No']})

        cpd_c = TabularCPD(variable='Former smoker', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Former smoker': ['Yes', 'No']})

        cpd_d = TabularCPD(variable='Hypertension', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Hypertension': ['Yes', 'No']})

        cpd_e = TabularCPD(variable='Myocardial infarction', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Myocardial infarction': ['Yes', 'No']})

        cpd_f = TabularCPD(variable='Angina', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Angina': ['Yes', 'No']})

        cpd_g = TabularCPD(variable='Heart failure', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Heart failure': ['Yes', 'No']})

        cpd_h = TabularCPD(variable='Stroke', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Stroke': ['Yes', 'No']})

        cpd_i = TabularCPD(variable='TIA', variable_card=2,
                                values=[[0],[1]],
                                state_names={'TIA': ['Yes', 'No']})
            
        cpd__p = TabularCPD(variable='Peripheral vascular disease', variable_card=2,
                        #values=[[0.22, 0.255, 0.266, 0.302, 0.999, 0.999, 0.999, 0.999, 0.243, 0.279, 0.289, 0.325, 0.999, 0.999, 0.999, 0.999, 0.255, 0.291, 0.302, 0.337, 0.999, 0.999, 0.999, 0.999, 0.279, 0.314, 0.325, 0.36, 0.999, 0.999, 0.999, 0.999, 0.24, 0.275, 0.286, 0.321, 0.999, 0.999, 0.999, 0.999, 0.263, 0.298, 0.309, 0.344, 0.999, 0.999, 0.999, 0.999, 0.275, 0.31, 0.321, 0.356, 0.999, 0.999, 0.999, 0.999, 0.298, 0.333, 0.344, 0.38, 0.999, 0.999, 0.999, 0.999, 0.23, 0.265, 0.276, 0.311, 0.999, 0.999, 0.999, 0.999, 0.253, 0.288, 0.299, 0.335, 0.999, 0.999, 0.999, 0.999, 0.265, 0.301, 0.311, 0.347, 0.999, 0.999, 0.999, 0.999, 0.288, 0.324, 0.335, 0.37, 0.999, 0.999, 0.999, 0.999, 0.249, 0.285, 0.296, 0.331, 0.999, 0.999, 0.999, 0.999, 0.273, 0.308, 0.319, 0.354, 0.999, 0.999, 0.999, 0.999, 0.285, 0.32, 0.331, 0.366, 0.999, 0.999, 0.999, 0.999, 0.308, 0.343, 0.354, 0.39, 0.999, 0.999, 0.999, 0.999, 0.251, 0.286, 0.297, 0.332, 0.999, 0.999, 0.999, 0.999, 0.274, 0.309, 0.32, 0.356, 0.999, 0.999, 0.999, 0.999, 0.286, 0.322, 0.332, 0.368, 0.999, 0.999, 0.999, 0.999, 0.309, 0.345, 0.356, 0.391, 0.999, 0.999, 0.999, 0.999, 0.27, 0.306, 0.317, 0.352, 0.999, 0.999, 0.999, 0.999, 0.294, 0.329, 0.34, 0.375, 0.999, 0.999, 0.999, 0.999, 0.306, 0.341, 0.352, 0.387, 0.999, 0.999, 0.999, 0.999, 0.329, 0.364, 0.375, 0.41, 0.999, 0.999, 0.999, 0.999, 0.261, 0.296, 0.307, 0.342, 0.999, 0.999, 0.999, 0.999, 0.284, 0.319, 0.33, 0.365, 0.999, 0.999, 0.999, 0.999, 0.296, 0.331, 0.342, 0.378, 0.999, 0.999, 0.999, 0.999, 0.319, 0.355, 0.365, 0.401, 0.999, 0.999, 0.999, 0.999, 0.28, 0.316, 0.326, 0.362, 0.999, 0.999, 0.999, 0.999, 0.303, 0.339, 0.35, 0.385, 0.999, 0.999, 0.999, 0.999, 0.316, 0.351, 0.362, 0.397, 0.999, 0.999, 0.999, 0.999, 0.339, 0.374, 0.385, 0.42, 0.999, 0.999, 0.999, 0.999, 0.249, 0.284, 0.295, 0.331, 0.999, 0.999, 0.999, 0.999, 0.272, 0.308, 0.318, 0.354, 0.999, 0.999, 0.999, 0.999, 0.284, 0.32, 0.331, 0.366, 0.999, 0.999, 0.999, 0.999, 0.308, 0.343, 0.354, 0.389, 0.999, 0.999, 0.999, 0.999, 0.268, 0.304, 0.315, 0.35, 0.999, 0.999, 0.999, 0.999, 0.292, 0.327, 0.338, 0.373, 0.999, 0.999, 0.999, 0.999, 0.304, 0.339, 0.35, 0.385, 0.999, 0.999, 0.999, 0.999, 0.327, 0.362, 0.373, 0.409, 0.999, 0.999, 0.999, 0.999, 0.259, 0.294, 0.305, 0.34, 0.999, 0.999, 0.999, 0.999, 0.282, 0.317, 0.328, 0.364, 0.999, 0.999, 0.999, 0.999, 0.294, 0.33, 0.34, 0.376, 0.999, 0.999, 0.999, 0.999, 0.317, 0.353, 0.364, 0.399, 0.999, 0.999, 0.999, 0.999, 0.278, 0.314, 0.325, 0.36, 0.999, 0.999, 0.999, 0.999, 0.302, 0.337, 0.348, 0.383, 0.999, 0.999, 0.999, 0.999, 0.314, 0.349, 0.36, 0.395, 0.999, 0.999, 0.999, 0.999, 0.337, 0.372, 0.383, 0.418, 0.999, 0.999, 0.999, 0.999, 0.28, 0.315, 0.326, 0.361, 0.999, 0.999, 0.999, 0.999, 0.303, 0.338, 0.349, 0.385, 0.999, 0.999, 0.999, 0.999, 0.315, 0.351, 0.361, 0.397, 0.999, 0.999, 0.999, 0.999, 0.338, 0.374, 0.385, 0.42, 0.999, 0.999, 0.999, 0.999, 0.299, 0.335, 0.345, 0.381, 0.999, 0.999, 0.999, 0.999, 0.322, 0.358, 0.369, 0.404, 0.999, 0.999, 0.999, 0.999, 0.335, 0.37, 0.381, 0.416, 0.999, 0.999, 0.999, 0.999, 0.358, 0.393, 0.404, 0.439, 0.999, 0.999, 0.999, 0.999, 0.29, 0.325, 0.336, 0.371, 0.999, 0.999, 0.999, 0.999, 0.313, 0.348, 0.359, 0.394, 0.999, 0.999, 0.999, 0.999, 0.325, 0.36, 0.371, 0.407, 0.999, 0.999, 0.999, 0.999, 0.348, 0.384, 0.394, 0.43, 0.999, 0.999, 0.999, 0.999, 0.309, 0.345, 0.355, 0.391, 0.999, 0.999, 0.999, 0.999, 0.332, 0.368, 0.379, 0.414, 0.999, 0.999, 0.999, 0.999, 0.345, 0.38, 0.391, 0.426, 0.999, 0.999, 0.999, 0.999, 0.368, 0.403, 0.414, 0.449, 0.999, 0.999, 0.999, 0.999], [0.78, 0.745, 0.734, 0.698, 0.001, 0.001, 0.001, 0.001, 0.757, 0.721, 0.711, 0.675, 0.001, 0.001, 0.001, 0.001, 0.745, 0.709, 0.698, 0.663, 0.001, 0.001, 0.001, 0.001, 0.721, 0.686, 0.675, 0.64, 0.001, 0.001, 0.001, 0.001, 0.76, 0.725, 0.714, 0.679, 0.001, 0.001, 0.001, 0.001, 0.737, 0.702, 0.691, 0.656, 0.001, 0.001, 0.001, 0.001, 0.725, 0.69, 0.679, 0.644, 0.001, 0.001, 0.001, 0.001, 0.702, 0.667, 0.656, 0.62, 0.001, 0.001, 0.001, 0.001, 0.77, 0.735, 0.724, 0.689, 0.001, 0.001, 0.001, 0.001, 0.747, 0.712, 0.701, 0.665, 0.001, 0.001, 0.001, 0.001, 0.735, 0.699, 0.689, 0.653, 0.001, 0.001, 0.001, 0.001, 0.712, 0.676, 0.665, 0.63, 0.001, 0.001, 0.001, 0.001, 0.751, 0.715, 0.704, 0.669, 0.001, 0.001, 0.001, 0.001, 0.727, 0.692, 0.681, 0.646, 0.001, 0.001, 0.001, 0.001, 0.715, 0.68, 0.669, 0.634, 0.001, 0.001, 0.001, 0.001, 0.692, 0.657, 0.646, 0.61, 0.001, 0.001, 0.001, 0.001, 0.749, 0.714, 0.703, 0.668, 0.001, 0.001, 0.001, 0.001, 0.726, 0.691, 0.68, 0.644, 0.001, 0.001, 0.001, 0.001, 0.714, 0.678, 0.668, 0.632, 0.001, 0.001, 0.001, 0.001, 0.691, 0.655, 0.644, 0.609, 0.001, 0.001, 0.001, 0.001, 0.73, 0.694, 0.683, 0.648, 0.001, 0.001, 0.001, 0.001, 0.706, 0.671, 0.66, 0.625, 0.001, 0.001, 0.001, 0.001, 0.694, 0.659, 0.648, 0.613, 0.001, 0.001, 0.001, 0.001, 0.671, 0.636, 0.625, 0.59, 0.001, 0.001, 0.001, 0.001, 0.739, 0.704, 0.693, 0.658, 0.001, 0.001, 0.001, 0.001, 0.716, 0.681, 0.67, 0.635, 0.001, 0.001, 0.001, 0.001, 0.704, 0.669, 0.658, 0.622, 0.001, 0.001, 0.001, 0.001, 0.681, 0.645, 0.635, 0.599, 0.001, 0.001, 0.001, 0.001, 0.72, 0.684, 0.674, 0.638, 0.001, 0.001, 0.001, 0.001, 0.697, 0.661, 0.65, 0.615, 0.001, 0.001, 0.001, 0.001, 0.684, 0.649, 0.638, 0.603, 0.001, 0.001, 0.001, 0.001, 0.661, 0.626, 0.615, 0.58, 0.001, 0.001, 0.001, 0.001, 0.751, 0.716, 0.705, 0.669, 0.001, 0.001, 0.001, 0.001, 0.728, 0.692, 0.682, 0.646, 0.001, 0.001, 0.001, 0.001, 0.716, 0.68, 0.669, 0.634, 0.001, 0.001, 0.001, 0.001, 0.692, 0.657, 0.646, 0.611, 0.001, 0.001, 0.001, 0.001, 0.732, 0.696, 0.685, 0.65, 0.001, 0.001, 0.001, 0.001, 0.708, 0.673, 0.662, 0.627, 0.001, 0.001, 0.001, 0.001, 0.696, 0.661, 0.65, 0.615, 0.001, 0.001, 0.001, 0.001, 0.673, 0.638, 0.627, 0.591, 0.001, 0.001, 0.001, 0.001, 0.741, 0.706, 0.695, 0.66, 0.001, 0.001, 0.001, 0.001, 0.718, 0.683, 0.672, 0.636, 0.001, 0.001, 0.001, 0.001, 0.706, 0.67, 0.66, 0.624, 0.001, 0.001, 0.001, 0.001, 0.683, 0.647, 0.636, 0.601, 0.001, 0.001, 0.001, 0.001, 0.722, 0.686, 0.675, 0.64, 0.001, 0.001, 0.001, 0.001, 0.698, 0.663, 0.652, 0.617, 0.001, 0.001, 0.001, 0.001, 0.686, 0.651, 0.64, 0.605, 0.001, 0.001, 0.001, 0.001, 0.663, 0.628, 0.617, 0.582, 0.001, 0.001, 0.001, 0.001, 0.72, 0.685, 0.674, 0.639, 0.001, 0.001, 0.001, 0.001, 0.697, 0.662, 0.651, 0.615, 0.001, 0.001, 0.001, 0.001, 0.685, 0.649, 0.639, 0.603, 0.001, 0.001, 0.001, 0.001, 0.662, 0.626, 0.615, 0.58, 0.001, 0.001, 0.001, 0.001, 0.701, 0.665, 0.655, 0.619, 0.001, 0.001, 0.001, 0.001, 0.678, 0.642, 0.631, 0.596, 0.001, 0.001, 0.001, 0.001, 0.665, 0.63, 0.619, 0.584, 0.001, 0.001, 0.001, 0.001, 0.642, 0.607, 0.596, 0.561, 0.001, 0.001, 0.001, 0.001, 0.71, 0.675, 0.664, 0.629, 0.001, 0.001, 0.001, 0.001, 0.687, 0.652, 0.641, 0.606, 0.001, 0.001, 0.001, 0.001, 0.675, 0.64, 0.629, 0.593, 0.001, 0.001, 0.001, 0.001, 0.652, 0.616, 0.606, 0.57, 0.001, 0.001, 0.001, 0.001, 0.691, 0.655, 0.645, 0.609, 0.001, 0.001, 0.001, 0.001, 0.668, 0.632, 0.621, 0.586, 0.001, 0.001, 0.001, 0.001, 0.655, 0.62, 0.609, 0.574, 0.001, 0.001, 0.001, 0.001, 0.632, 0.597, 0.586, 0.551, 0.001, 0.001, 0.001, 0.001]],
                        values=values,
                        evidence=['Diabetes', 'Current smoker', 'Former smoker', 'Hypertension', 'Myocardial infarction', 'Angina', 'Heart failure', 'Stroke', 'TIA'],
                        evidence_card=[2, 2, 2, 2, 2, 2, 2, 2, 2],
                        state_names={'Peripheral vascular disease': ['Yes', 'No'],
                            'Diabetes': ['No', 'Yes'],
                            'Current smoker': ['No', 'Yes'],
                            'Former smoker': ['No', 'Yes'],
                            'Hypertension': ['No', 'Yes'],
                            'Myocardial infarction': ['No', 'Yes'],
                            'Angina': ['No', 'Yes'],
                            'Heart failure': ['No', 'Yes'],
                            'Stroke': ['No', 'Yes'],
                            'TIA': ['No', 'Yes'],
                        })

        # Associating the parameters with the model structure.
        peripheral_vascular_disease.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d,cpd_e,cpd_f,cpd_g,cpd_h,cpd_i, cpd__p)

        # Checking if the cpds are valid for the model.
        # print(f"{'Model is okay' if peripheral_vascular_disease.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(peripheral_vascular_disease)
        q = infer.query(['Peripheral vascular disease'], evidence={
                'Diabetes': dm, 
                'Current smoker': 'Yes' if smoking == 0 else 'No', 
                'Former smoker': 'Yes' if smoking ==  1 else 'No', 
                'Hypertension': htn, 
                'Myocardial infarction': mi,
                'Angina': angina,
                'Heart failure': hf,
                'Stroke': cva,
                'TIA': tia
            }, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferFalls(self, band, gender, dw, diz, pd, oa, ui, oh, af, dep, fp):
        fall = BayesianModel([('Difficulty walking', 'Fall'), ('Dizziness', 'Fall'), ("Parkinsons disease", 'Fall'), ('Osteoarthritis', 'Fall'), ('Urinary incontinence', 'Fall'), ('Orthostatic hypotension', 'Fall'), ('Atrial fibrillation', 'Fall'), ('Depression', 'Fall'), ('Foot problems', 'Fall')])

        bg_risk = (band['geriatricVulnerabilities']['falls'][gender] / 100) - 0.16 # Reduce to account for baseline risk

        variables = [{'name': 'Difficulty walking', 'r': 2.1, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/20585256/'}, {'name': 'Dizziness', 'r': 1.7, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/20585256/'}, {'name': "Parkinsons disease", 'r': 2.7, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/20585256/'}, {'name': 'Osteoarthritis', 'r': 1.33, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/34132007/'}, {'name': 'Urinary incontinence', 'r': 1.59, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/34010311/'}, {'name': 'Orthostatic hypotension', 'r': 1.73, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/30583909/'}, {'name': 'Atrial fibrillation', 'r': 1.19, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/32247342/'}, {'name': 'Depression', 'r': 4, 'll': 2.0, 'ul': 8.1, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/26234532/'}, {'name': 'Foot problems', 'r': 1.84, 'll': 1.07, 'ul': 3.0, 'ciType': 95, 'type': 'OR', 'ref': 'https://www.sciencedirect.com/science/article/pii/S0378512218305760?via%3Dihub'}]

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Difficulty walking', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Difficulty walking': ['Yes', 'No']})
            

        cpd_b = TabularCPD(variable='Dizziness', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Dizziness': ['Yes', 'No']})
            

        cpd_c = TabularCPD(variable='Parkinsons disease', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Parkinsons disease': ['Yes', 'No']})
            

        cpd_d = TabularCPD(variable='Osteoarthritis', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Osteoarthritis': ['Yes', 'No']})
            

        cpd_e = TabularCPD(variable='Urinary incontinence', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Urinary incontinence': ['Yes', 'No']})
            

        cpd_f = TabularCPD(variable='Orthostatic hypotension', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Orthostatic hypotension': ['Yes', 'No']})
            

        cpd_g = TabularCPD(variable='Atrial fibrillation', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Atrial fibrillation': ['Yes', 'No']})
            

        cpd_h = TabularCPD(variable='Depression', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Depression': ['Yes', 'No']})
            

        cpd_i = TabularCPD(variable='Foot problems', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Foot problems': ['Yes', 'No']})
            

        cpd__f = TabularCPD(variable='Fall', variable_card=2,
                        #values=[[0.3, 0.348, 0.398, 0.462, 0.328, 0.38, 0.436, 0.505, 0.345, 0.399, 0.458, 0.53, 0.377, 0.437, 0.501, 0.58, 0.34, 0.394, 0.452, 0.524, 0.372, 0.431, 0.494, 0.573, 0.391, 0.453, 0.519, 0.601, 0.428, 0.496, 0.568, 0.658, 0.339, 0.393, 0.45, 0.522, 0.371, 0.43, 0.493, 0.571, 0.389, 0.451, 0.517, 0.599, 0.426, 0.494, 0.566, 0.656, 0.385, 0.446, 0.511, 0.592, 0.421, 0.488, 0.559, 0.648, 0.442, 0.512, 0.586, 0.68, 0.483, 0.56, 0.642, 0.744, 0.371, 0.43, 0.492, 0.571, 0.406, 0.47, 0.539, 0.624, 0.426, 0.494, 0.565, 0.655, 0.466, 0.54, 0.619, 0.717, 0.421, 0.487, 0.558, 0.647, 0.46, 0.533, 0.611, 0.708, 0.483, 0.56, 0.641, 0.743, 0.528, 0.612, 0.702, 0.813, 0.419, 0.486, 0.556, 0.645, 0.458, 0.531, 0.609, 0.706, 0.481, 0.558, 0.639, 0.741, 0.527, 0.61, 0.699, 0.81, 0.475, 0.551, 0.631, 0.732, 0.52, 0.603, 0.69, 0.8, 0.546, 0.633, 0.725, 0.84, 0.597, 0.692, 0.793, 0.919, 0.343, 0.398, 0.456, 0.528, 0.376, 0.435, 0.499, 0.578, 0.394, 0.457, 0.524, 0.607, 0.431, 0.5, 0.573, 0.664, 0.389, 0.451, 0.517, 0.599, 0.426, 0.494, 0.566, 0.656, 0.447, 0.518, 0.594, 0.688, 0.489, 0.567, 0.65, 0.753, 0.388, 0.45, 0.515, 0.597, 0.425, 0.492, 0.564, 0.653, 0.446, 0.517, 0.592, 0.686, 0.488, 0.565, 0.647, 0.75, 0.44, 0.51, 0.584, 0.677, 0.481, 0.558, 0.639, 0.741, 0.505, 0.586, 0.671, 0.778, 0.553, 0.641, 0.734, 0.851, 0.424, 0.492, 0.563, 0.653, 0.464, 0.538, 0.616, 0.714, 0.487, 0.565, 0.647, 0.75, 0.533, 0.618, 0.708, 0.821, 0.481, 0.558, 0.639, 0.741, 0.526, 0.61, 0.699, 0.81, 0.553, 0.641, 0.734, 0.851, 0.605, 0.701, 0.803, 0.931, 0.48, 0.556, 0.637, 0.738, 0.525, 0.608, 0.697, 0.808, 0.551, 0.638, 0.731, 0.848, 0.603, 0.698, 0.8, 0.927, 0.544, 0.63, 0.722, 0.837, 0.595, 0.69, 0.79, 0.916, 0.625, 0.724, 0.829, 0.961, 0.683, 0.792, 0.907, 0.999, 0.355, 0.412, 0.472, 0.547, 0.389, 0.45, 0.516, 0.598, 0.408, 0.473, 0.542, 0.628, 0.446, 0.517, 0.593, 0.687, 0.403, 0.467, 0.535, 0.62, 0.441, 0.511, 0.585, 0.678, 0.463, 0.536, 0.614, 0.712, 0.506, 0.587, 0.672, 0.779, 0.401, 0.465, 0.533, 0.618, 0.439, 0.509, 0.583, 0.676, 0.461, 0.534, 0.612, 0.71, 0.504, 0.585, 0.67, 0.776, 0.455, 0.528, 0.605, 0.701, 0.498, 0.577, 0.661, 0.767, 0.523, 0.606, 0.694, 0.805, 0.572, 0.663, 0.76, 0.88, 0.439, 0.509, 0.583, 0.676, 0.48, 0.557, 0.638, 0.739, 0.504, 0.584, 0.669, 0.776, 0.552, 0.639, 0.732, 0.849, 0.498, 0.577, 0.661, 0.766, 0.545, 0.631, 0.723, 0.838, 0.572, 0.663, 0.759, 0.88, 0.626, 0.725, 0.831, 0.963, 0.496, 0.575, 0.659, 0.764, 0.543, 0.629, 0.721, 0.835, 0.57, 0.66, 0.757, 0.877, 0.623, 0.723, 0.828, 0.959, 0.563, 0.652, 0.747, 0.866, 0.616, 0.714, 0.817, 0.948, 0.646, 0.749, 0.858, 0.995, 0.707, 0.82, 0.939, 0.999, 0.406, 0.471, 0.54, 0.626, 0.445, 0.515, 0.59, 0.684, 0.467, 0.541, 0.62, 0.718, 0.511, 0.592, 0.678, 0.786, 0.461, 0.534, 0.612, 0.709, 0.504, 0.585, 0.67, 0.776, 0.529, 0.614, 0.703, 0.815, 0.579, 0.671, 0.769, 0.891, 0.459, 0.532, 0.61, 0.707, 0.503, 0.583, 0.667, 0.773, 0.528, 0.611, 0.701, 0.812, 0.577, 0.669, 0.766, 0.888, 0.521, 0.604, 0.692, 0.802, 0.57, 0.661, 0.757, 0.877, 0.598, 0.694, 0.795, 0.921, 0.655, 0.759, 0.869, 0.999, 0.502, 0.582, 0.667, 0.773, 0.55, 0.637, 0.73, 0.846, 0.577, 0.669, 0.766, 0.888, 0.631, 0.732, 0.838, 0.971, 0.57, 0.66, 0.756, 0.877, 0.623, 0.722, 0.828, 0.959, 0.654, 0.758, 0.869, 0.999, 0.716, 0.83, 0.95, 0.999, 0.568, 0.658, 0.754, 0.874, 0.621, 0.72, 0.825, 0.956, 0.652, 0.756, 0.866, 0.999, 0.713, 0.827, 0.947, 0.999, 0.644, 0.746, 0.855, 0.991, 0.704, 0.817, 0.935, 0.999, 0.74, 0.857, 0.982, 0.999, 0.809, 0.938, 0.999, 0.999], [0.7, 0.652, 0.602, 0.538, 0.672, 0.62, 0.564, 0.495, 0.655, 0.601, 0.542, 0.47, 0.623, 0.563, 0.499, 0.42, 0.66, 0.606, 0.548, 0.476, 0.628, 0.569, 0.506, 0.427, 0.609, 0.547, 0.481, 0.399, 0.572, 0.504, 0.432, 0.342, 0.661, 0.607, 0.55, 0.478, 0.629, 0.57, 0.507, 0.429, 0.611, 0.549, 0.483, 0.401, 0.574, 0.506, 0.434, 0.344, 0.615, 0.554, 0.489, 0.408, 0.579, 0.512, 0.441, 0.352, 0.558, 0.488, 0.414, 0.32, 0.517, 0.44, 0.358, 0.256, 0.629, 0.57, 0.508, 0.429, 0.594, 0.53, 0.461, 0.376, 0.574, 0.506, 0.435, 0.345, 0.534, 0.46, 0.381, 0.283, 0.579, 0.513, 0.442, 0.353, 0.54, 0.467, 0.389, 0.292, 0.517, 0.44, 0.359, 0.257, 0.472, 0.388, 0.298, 0.187, 0.581, 0.514, 0.444, 0.355, 0.542, 0.469, 0.391, 0.294, 0.519, 0.442, 0.361, 0.259, 0.473, 0.39, 0.301, 0.19, 0.525, 0.449, 0.369, 0.268, 0.48, 0.397, 0.31, 0.2, 0.454, 0.367, 0.275, 0.16, 0.403, 0.308, 0.207, 0.081, 0.657, 0.602, 0.544, 0.472, 0.624, 0.565, 0.501, 0.422, 0.606, 0.543, 0.476, 0.393, 0.569, 0.5, 0.427, 0.336, 0.611, 0.549, 0.483, 0.401, 0.574, 0.506, 0.434, 0.344, 0.553, 0.482, 0.406, 0.312, 0.511, 0.433, 0.35, 0.247, 0.612, 0.55, 0.485, 0.403, 0.575, 0.508, 0.436, 0.347, 0.554, 0.483, 0.408, 0.314, 0.512, 0.435, 0.353, 0.25, 0.56, 0.49, 0.416, 0.323, 0.519, 0.442, 0.361, 0.259, 0.495, 0.414, 0.329, 0.222, 0.447, 0.359, 0.266, 0.149, 0.576, 0.508, 0.437, 0.347, 0.536, 0.462, 0.384, 0.286, 0.513, 0.435, 0.353, 0.25, 0.467, 0.382, 0.292, 0.179, 0.519, 0.442, 0.361, 0.259, 0.474, 0.39, 0.301, 0.19, 0.447, 0.359, 0.266, 0.149, 0.395, 0.299, 0.197, 0.069, 0.52, 0.444, 0.363, 0.262, 0.475, 0.392, 0.303, 0.192, 0.449, 0.362, 0.269, 0.152, 0.397, 0.302, 0.2, 0.073, 0.456, 0.37, 0.278, 0.163, 0.405, 0.31, 0.21, 0.084, 0.375, 0.276, 0.171, 0.039, 0.317, 0.208, 0.093, 0.001, 0.645, 0.588, 0.528, 0.453, 0.611, 0.55, 0.484, 0.402, 0.592, 0.527, 0.458, 0.372, 0.554, 0.483, 0.407, 0.313, 0.597, 0.533, 0.465, 0.38, 0.559, 0.489, 0.415, 0.322, 0.537, 0.464, 0.386, 0.288, 0.494, 0.413, 0.328, 0.221, 0.599, 0.535, 0.467, 0.382, 0.561, 0.491, 0.417, 0.324, 0.539, 0.466, 0.388, 0.29, 0.496, 0.415, 0.33, 0.224, 0.545, 0.472, 0.395, 0.299, 0.502, 0.423, 0.339, 0.233, 0.477, 0.394, 0.306, 0.195, 0.428, 0.337, 0.24, 0.12, 0.561, 0.491, 0.417, 0.324, 0.52, 0.443, 0.362, 0.261, 0.496, 0.416, 0.331, 0.224, 0.448, 0.361, 0.268, 0.151, 0.502, 0.423, 0.339, 0.234, 0.455, 0.369, 0.277, 0.162, 0.428, 0.337, 0.241, 0.12, 0.374, 0.275, 0.169, 0.037, 0.504, 0.425, 0.341, 0.236, 0.457, 0.371, 0.279, 0.165, 0.43, 0.34, 0.243, 0.123, 0.377, 0.277, 0.172, 0.041, 0.437, 0.348, 0.253, 0.134, 0.384, 0.286, 0.183, 0.052, 0.354, 0.251, 0.142, 0.005, 0.293, 0.18, 0.061, 0.001, 0.594, 0.529, 0.46, 0.374, 0.555, 0.485, 0.41, 0.316, 0.533, 0.459, 0.38, 0.282, 0.489, 0.408, 0.322, 0.214, 0.539, 0.466, 0.388, 0.291, 0.496, 0.415, 0.33, 0.224, 0.471, 0.386, 0.297, 0.185, 0.421, 0.329, 0.231, 0.109, 0.541, 0.468, 0.39, 0.293, 0.497, 0.417, 0.333, 0.227, 0.472, 0.389, 0.299, 0.188, 0.423, 0.331, 0.234, 0.112, 0.479, 0.396, 0.308, 0.198, 0.43, 0.339, 0.243, 0.123, 0.402, 0.306, 0.205, 0.079, 0.345, 0.241, 0.131, 0.001, 0.498, 0.418, 0.333, 0.227, 0.45, 0.363, 0.27, 0.154, 0.423, 0.331, 0.234, 0.112, 0.369, 0.268, 0.162, 0.029, 0.43, 0.34, 0.244, 0.123, 0.377, 0.278, 0.172, 0.041, 0.346, 0.242, 0.131, 0.001, 0.284, 0.17, 0.05, 0.001, 0.432, 0.342, 0.246, 0.126, 0.379, 0.28, 0.175, 0.044, 0.348, 0.244, 0.134, 0.001, 0.287, 0.173, 0.053, 0.001, 0.356, 0.254, 0.145, 0.009, 0.296, 0.183, 0.065, 0.001, 0.26, 0.143, 0.018, 0.001, 0.191, 0.062, 0.001, 0.001]],
                        values=values,
                        evidence=['Difficulty walking', 'Dizziness', "Parkinsons disease", 'Osteoarthritis', 'Urinary incontinence', 'Orthostatic hypotension', 'Atrial fibrillation', 'Depression', 'Foot problems'],
                        evidence_card=[2, 2, 2, 2, 2, 2, 2, 2, 2],
                        state_names={'Fall': ['Yes', 'No'],
                            'Difficulty walking': ['No', 'Yes'],
                            'Dizziness': ['No', 'Yes'],
                            'Parkinsons disease': ['No', 'Yes'],
                            'Osteoarthritis': ['No', 'Yes'],
                            'Urinary incontinence': ['No', 'Yes'],
                            'Orthostatic hypotension': ['No', 'Yes'],
                            'Atrial fibrillation': ['No', 'Yes'],
                            'Depression': ['No', 'Yes'],
                            'Foot problems': ['No', 'Yes'],
                        })


        # Associating the parameters with the model structure.
        fall.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d,cpd_e,cpd_f,cpd_g,cpd_h,cpd_i, cpd__f)

        # Checking if the cpds are valid for the model.
        # print(f"{'Model is okay' if fall.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(fall)
        q = infer.query(['Fall'], evidence={
                'Difficulty walking': dw, 
                'Dizziness': diz, 
                'Parkinsons disease': pd, 
                'Osteoarthritis': oa, 
                'Urinary incontinence': ui,
                'Orthostatic hypotension': oh,
                'Atrial fibrillation': af,
                'Depression': dep,
                'Foot problems': fp
            }, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferSocialIsolation(self, band, gender, hl, falls, walking, badl):

        social_isolation = BayesianModel([('Hearing loss', 'Social isolation'), ('Falls', 'Social isolation'), ('Difficulty walking outside', 'Social isolation'), ('BADL dependency', 'Social isolation')])

        bg_risk = band['geriatricVulnerabilities']['decreasedSocialActivity'][gender] / 100

        variables = [{'name': 'Hearing loss', 'r': 2.14, 'll': 1.29, 'ul': 3.57, 'ciType': 95, 'type': 'OR', 'ref': 'https://journals.sagepub.com/doi/10.1177/0194599820910377'}, {'name': 'Falls', 'r': 1.44, 'll': 1.01, 'ul': 1.86, 'ciType': 95, 'type': 'RR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/32018091/'}, {'name': 'Difficulty walking outside', 'r': 1.59, 'll': 1.41, 'ul': 1.85, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/23548944/'}, {'name': 'BADL dependency', 'r': 1.5, 'll': 1.0, 'ul': 2.2, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/19274642/'}]

        values = self.calculateCPDTable(bg_risk, variables)

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
                        #values=[[0.44, 0.564, 0.57, 0.695, 0.61, 0.734, 0.741, 0.865, 0.608, 0.732, 0.738, 0.862, 0.778, 0.902, 0.908, 0.999], [0.56, 0.436, 0.43, 0.305, 0.39, 0.266, 0.259, 0.135, 0.392, 0.268, 0.262, 0.138, 0.222, 0.098, 0.092, 0.001]],
                        values=values,
                        evidence=['Hearing loss', 'Falls', 'Difficulty walking outside', 'BADL dependency'],
                        evidence_card=[2, 2, 2, 2],
                        state_names={'Social isolation': ['Yes', 'No'],
                            'Hearing loss': ['No', 'Yes'],
                            'Falls': ['No', 'Yes'],
                            'Difficulty walking outside': ['No', 'Yes'],
                            'BADL dependency': ['No', 'Yes'],
                        })


        # Associating the parameters with the model structure.
        social_isolation.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d, cpd__s)

        # Checking if the cpds are valid for the model.
        # print(f"{'Model is okay' if social_isolation.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(social_isolation)
        q = infer.query(['Social isolation'], evidence={
                'Hearing loss': hl,
                'Falls': falls,
                'Difficulty walking outside': walking,
                'BADL dependency': badl
            }, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferHomebound(self, band, gender, dep, isol, aid, falls, fof, pain):
        homebound = BayesianModel([('Depression', 'Homebound'), ('Social isolation', 'Homebound'), ('Using walking aid', 'Homebound'), ('Falls', 'Homebound'), ('Fear of falling', 'Homebound'), ('Chronic pain', 'Homebound')])

        bg_risk = band['geriatricVulnerabilities']['homebound'][gender] / 100

        variables = [{'name': 'Depression', 'r': 1.398, 'll': 1.266, 'ul': 1.544, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.researchsquare.com/article/rs-275313/v1'}, {'name': 'Social isolation', 'r': 1.147, 'll': 1.047, 'ul': 1.256, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.researchsquare.com/article/rs-275313/v1'}, {'name': 'Using walking aid', 'r': 1.968, 'll': 1.79, 'ul': 2.163, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.researchsquare.com/article/rs-275313/v1'}, {'name': 'Falls', 'r': 1.525, 'll': 1.229, 'ul': 1.555, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.researchsquare.com/article/rs-275313/v1'}, {'name': 'Fear of falling', 'r': 1.525, 'll': 1.399, 'ul': 1.662, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.researchsquare.com/article/rs-275313/v1'}, {'name': 'Chronic pain', 'r': 1.198, 'll': 1.104, 'ul': 1.3, 'ciType': 95, 'type': 'HR', 'ref': 'https://www.researchsquare.com/article/rs-275313/v1'}]

        values = self.calculateCPDTable(bg_risk, variables)

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
                        #values=[[0.056, 0.065, 0.071, 0.082, 0.071, 0.082, 0.089, 0.104, 0.08, 0.093, 0.101, 0.117, 0.101, 0.117, 0.127, 0.148, 0.064, 0.075, 0.081, 0.095, 0.081, 0.095, 0.102, 0.119, 0.092, 0.107, 0.116, 0.135, 0.116, 0.135, 0.146, 0.17, 0.068, 0.08, 0.086, 0.1, 0.086, 0.1, 0.109, 0.127, 0.097, 0.113, 0.123, 0.143, 0.123, 0.143, 0.155, 0.18, 0.079, 0.092, 0.099, 0.116, 0.099, 0.116, 0.125, 0.146, 0.112, 0.13, 0.141, 0.164, 0.141, 0.164, 0.178, 0.207], [0.944, 0.935, 0.929, 0.918, 0.929, 0.918, 0.911, 0.896, 0.92, 0.907, 0.899, 0.883, 0.899, 0.883, 0.873, 0.852, 0.936, 0.925, 0.919, 0.905, 0.919, 0.905, 0.898, 0.881, 0.908, 0.893, 0.884, 0.865, 0.884, 0.865, 0.854, 0.83, 0.932, 0.92, 0.914, 0.9, 0.914, 0.9, 0.891, 0.873, 0.903, 0.887, 0.877, 0.857, 0.877, 0.857, 0.845, 0.82, 0.921, 0.908, 0.901, 0.884, 0.901, 0.884, 0.875, 0.854, 0.888, 0.87, 0.859, 0.836, 0.859, 0.836, 0.822, 0.793]],
                        values=values,
                        evidence=['Depression', 'Social isolation', 'Using walking aid', 'Falls', 'Fear of falling', 'Chronic pain'],
                        evidence_card=[2, 2, 2, 2, 2, 2],
                        state_names={'Homebound': ['Yes', 'No'],
                            'Depression': ['No', 'Yes'],
                            'Social isolation': ['No', 'Yes'],
                            'Using walking aid': ['No', 'Yes'],
                            'Falls': ['No', 'Yes'],
                            'Fear of falling': ['No', 'Yes'],
                            'Chronic pain': ['No', 'Yes'],
                        })


        # Associating the parameters with the model structure.
        homebound.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d,cpd_e,cpd_f, cpd__h)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if homebound.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(homebound)
        q = infer.query(['Homebound'], evidence={
            'Depression': dep,
            'Social isolation': isol,
            'Using walking aid': aid,
            'Falls': falls,
            'Fear of falling': fof,
            'Chronic pain': pain,
            }, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0


    def inferMalnutrition(self, band, gender, pd, badl, mci, dementia):

        #https://www.sciencedirect.com/science/article/pii/S1879729612001391?via%3Dihub#bib0020
        #https://www.sciencedirect.com/science/article/pii/S0899900719301650?via%3Dihub
        #https://pubmed.ncbi.nlm.nih.gov/23065984/

        malnutrition = BayesianModel([('BADLDependency', 'Malnutrition'), ('MCI', 'Malnutrition'), ('Dementia', 'Malnutrition'), ('Parkinsons', 'Malnutrition'), ('Malnutrition', 'Anorexia'), ('Malnutrition', 'Weight loss')])

        bg_risk = band['geriatricVulnerabilities']['malnutrition'][gender] / 100

        variables = [
            {'name': 'Parkinsons', 'r': 2.45, 'll': 1.066, 'ul': 5.965, 'ciType': 95, 'type': 'OR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4863272/'}, 
            {'name': 'BADLDependency', 'r': 1.793, 'll': 1.163, 'ul': 2.765, 'ciType': 95, 'type': 'OR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4863272/'}, 
            {'name': 'MCI', 'r': 1.844, 'll': 1.267, 'ul': 2.683, 'ciType': 95, 'type': 'OR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4863272/'}, 
            {'name': 'Dementia', 'r': 2.139, 'll': 1.343, 'ul': 3.407, 'ciType': 95, 'type': 'OR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4863272/'}]

        values = self.calculateCPDTable(bg_risk, variables)

          
        cpd_p = TabularCPD(variable='Parkinsons', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Parkinsons': ['Yes', 'No']})

        cpd_b = TabularCPD(variable='BADLDependency', variable_card=2,
                            values=[[0],[1]],
                            state_names={'BADLDependency': ['Yes', 'No']})

        cpd_c = TabularCPD(variable='MCI', variable_card=2,
                            values=[[0],[1]],
                            state_names={'MCI': ['Yes', 'No']})

        cpd_d = TabularCPD(variable='Dementia', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Dementia': ['Yes', 'No']})

        cpd_m = TabularCPD(variable='Malnutrition', variable_card=2, 
                        values=values,
                        evidence=['Parkinsons', 'BADLDependency', 'MCI', 'Dementia'],
                        evidence_card=[2,2,2,2],
                        state_names={'Malnutrition': ['Malnourished', 'Not malnourished'],
                            'Parkinsons': ['No', 'Yes'],
                            'BADLDependency': ['No', 'Yes'],
                            'MCI': ['No', 'Yes'],
                            'Dementia': ['No', 'Yes']})

        #https://pubmed.ncbi.nlm.nih.gov/19937260/
        cpd_a = TabularCPD(variable='Anorexia', variable_card=2,
                    values=[[0.63, 0.25], [0.37, 0.75]],
                    evidence=['Malnutrition'],
                    evidence_card=[2],
                    state_names={'Anorexia': ['Yes', 'No'],
                                    'Malnutrition': ['Malnourished', 'Not malnourished']  })

        #https://pubmed.ncbi.nlm.nih.gov/23065984/
        cpd_w = TabularCPD(variable='Weight loss', variable_card=2,
                      values=[[0.84, 0.595],[0.16, 0.405]],
                      evidence=['Malnutrition'],
                      evidence_card=[2],
                      state_names={'Weight loss': ['Yes', 'No'],
                                    'Malnutrition': ['Malnourished', 'Not malnourished']  })

        malnutrition.add_cpds(cpd_p, cpd_b, cpd_c, cpd_d, cpd_m, cpd_a, cpd_w)

        infer = VariableElimination(malnutrition)
        q = infer.query(['Malnutrition'], evidence={
            'Parkinsons': pd,
            'BADLDependency': badl,
            'MCI': mci,
            'Dementia': dementia
            }, show_progress=False)

        hasMalnutrition = 1 if self.rng.random() < q.values[0] else 0
        
        weight_loss = infer.query(['Weight loss'], evidence={'Malnutrition': 'Malnourished' if hasMalnutrition == 1 else 'Not malnourished'}, show_progress=False)

        anorexia = infer.query(['Anorexia'], evidence={'Malnutrition': 'Malnourished' if hasMalnutrition == 1 else 'Not malnourished'}, show_progress=False)

        hasWeightloss = 1 if self.rng.random() < weight_loss.values[0] else 0

        hasAnorexia = 1 if self.rng.random() < anorexia.values[0] else 0

        return (hasMalnutrition, hasWeightloss, hasAnorexia)

    def inferChronicPain(self, band, gender, arthritis, osteo, copd, migraine, heart, pud, dm):

        chronic_pain = BayesianModel([('Arthritis', 'Chronic pain'), ('Osteoporosis', 'Chronic pain'), ('COPD', 'Chronic pain'), ('Migraine', 'Chronic pain'), ('Heart disease', 'Chronic pain'), ('Peptic ulcer disease', 'Chronic pain'), ('Diabetes', 'Chronic pain')])
        
        bg_risk = (band['geriatricVulnerabilities']['chronicPain'][gender] / 100) - 0.138 # Reduce to account for true baseline

        variables = [
            {'name': 'Arthritis', 'r': 4.0, 'll': 3.4, 'ul': 4.6, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/22071318/'}, 
            {'name': 'Osteoporosis', 'r': 2.2, 'll': 1.6, 'ul': 3.0, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/22071318/'}, 
            {'name': 'COPD', 'r': 1.4, 'll': 1.0, 'ul': 2.0, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/22071318/'}, 
            {'name': 'Migraine', 'r': 1.6, 'll': 1.3, 'ul': 1.9, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/22071318/'},
            {'name': 'Heart disease', 'r': 1.6, 'll': 1.3, 'ul': 1.9, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/22071318/'},
            {'name': 'Peptic ulcer disease', 'r': 1.4, 'll': 1.0, 'ul': 1.9, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/22071318/'},
            {'name': 'Diabetes', 'r': 1.4, 'll': 1.1, 'ul': 1.8, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/22071318/'}
        ]

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Arthritis', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Arthritis': ['Yes', 'No']})

        cpd_b = TabularCPD(variable='Osteoporosis', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Osteoporosis': ['Yes', 'No']})

        cpd_c = TabularCPD(variable='COPD', variable_card=2,
                            values=[[0],[1]],
                            state_names={'COPD': ['Yes', 'No']})

        cpd_d = TabularCPD(variable='Migraine', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Migraine': ['Yes', 'No']})

        cpd_e = TabularCPD(variable='Heart disease', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Heart disease': ['Yes', 'No']})

        cpd_f = TabularCPD(variable='Peptic ulcer disease', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Peptic ulcer disease': ['Yes', 'No']})

        cpd_h = TabularCPD(variable='Diabetes', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Diabetes': ['Yes', 'No']})

        cpd__c = TabularCPD(variable='Chronic pain', variable_card=2, 
                        values=values,
                        evidence=['Arthritis', 'Osteoporosis', 'COPD', 'Migraine', 'Heart disease', 'Peptic ulcer disease', 'Diabetes'],
                        evidence_card=[2,2,2,2,2,2,2],
                        state_names={'Chronic pain': ['Yes', 'No'],
                            'Arthritis': ['No', 'Yes'],
                            'Osteoporosis': ['No', 'Yes'],
                            'COPD': ['No', 'Yes'],
                            'Migraine': ['No', 'Yes'],
                            'Heart disease': ['No', 'Yes'],
                            'Peptic ulcer disease': ['No', 'Yes'],
                            'Diabetes': ['No', 'Yes']
                        })

        chronic_pain.add_cpds(cpd_a, cpd_b, cpd_c, cpd_d, cpd_e, cpd_f, cpd_h, cpd__c)

        infer = VariableElimination(chronic_pain)
        q = infer.query(['Chronic pain'], evidence={
            'Arthritis': arthritis,
            'Osteoporosis': osteo,
            'COPD': copd,
            'Migraine': migraine,
            'Heart disease': heart,
            'Peptic ulcer disease': pud,
            'Diabetes': dm
            }, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferHistoryOfDelirium(self, band, gender, dementia, vi):

        hod = BayesianModel([('Dementia', 'History of delirium'), ('Visual impairment', 'History of delirium')])

        variables = [
            {'name': 'Dementia', 'r': 6.62, 'll': 4.3, 'ul': 10.19, 'ciType': 95, 'type': 'OR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4001175/'}, 
            {'name': 'Visual impairment', 'r': 1.89, 'll': 1.03, 'ul': 3.47, 'ciType': 95, 'type': 'OR', 'ref': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4001175/'}, 
        ]

        bg_risk = band['geriatricVulnerabilities']['historyOfDelirium'][gender] / 100

        values = self.calculateCPDTable(bg_risk, variables)


        cpd_a = TabularCPD(variable='Dementia', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Dementia': ['Yes', 'No']})

        cpd_b = TabularCPD(variable='Visual impairment', variable_card=2,
                            values=[[0],[1]],
                            state_names={'Visual impairment': ['Yes', 'No']})

        cpd__c = TabularCPD(variable='History of delirium', variable_card=2, 
                        values=values,
                        evidence=['Dementia', 'Visual impairment'],
                        evidence_card=[2,2],
                        state_names={'History of delirium': ['Yes', 'No'],
                            'Dementia': ['No', 'Yes'],
                            'Visual impairment': ['No', 'Yes']
                        })

        hod.add_cpds(cpd_a, cpd_b, cpd__c)

        infer = VariableElimination(hod)
        q = infer.query(['History of delirium'], evidence={
            'Dementia': dementia,
            'Visual impairment': vi
            }, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferFragilityFracture(self, band, gender, weight, bmi1, bmi2, wl, currentSmoker, ra):
        fragility_fracture = BayesianModel([('Weight <58kg', 'Fragility fracture'), ('Underweight', 'Fragility fracture'), ('Obese', 'Fragility fracture'), ('Weight loss', 'Fragility fracture'), ('Current smoker', 'Fragility fracture'), ('Rheumatoid arthritis', 'Fragility fracture')])

        variables = [{'name': 'Weight <58kg', 'r': 4.01, 'll': 1.62, 'ul': 9.9, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33991260/'}, {'name': 'Underweight', 'r': 2.83, 'll': 1.82, 'ul': 4.39, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33991260/'}, {'name': 'Obese', 'r': 0.58, 'll': 0.34, 'ul': 0.99, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33991260/'}, {'name': 'Weight loss', 'r': 1.88, 'll': 1.32, 'ul': 2.68, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33991260/'}, {'name': 'Current smoker', 'r': 1.5, 'll': 1.22, 'ul': 1.85, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/33991260/'}, {'name': 'Rheumatoid arthritis', 'r': 1.61, 'll': 1.44, 'ul': 1.79, 'ciType': 95, 'type': 'OR', 'ref': 'https://pubmed.ncbi.nlm.nih.gov/29546507/'}]
        
        bg_risk = band['geriatricVulnerabilities']['fragilityFracture'][gender] / 100

        values = self.calculateCPDTable(bg_risk, variables)


        cpd_a = TabularCPD(variable='Weight <58kg', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Weight <58kg': ['Yes', 'No']})

        cpd_b = TabularCPD(variable='Underweight', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Underweight': ['Yes', 'No']})

        cpd_c = TabularCPD(variable='Obese', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Obese': ['Yes', 'No']})

        cpd_d = TabularCPD(variable='Weight loss', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Weight loss': ['Yes', 'No']})
        
        cpd_e = TabularCPD(variable='Current smoker', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Current smoker': ['Yes', 'No']})

        cpd_f = TabularCPD(variable='Rheumatoid arthritis', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Rheumatoid arthritis': ['Yes', 'No']})
            
        cpd__f = TabularCPD(variable='Fragility fracture', variable_card=2,
                        #values=[[0.356, 0.43, 0.425, 0.513, 0.443, 0.536, 0.529, 0.639, 0.376, 0.454, 0.448, 0.542, 0.468, 0.565, 0.558, 0.675, 0.481, 0.581, 0.574, 0.693, 0.598, 0.723, 0.714, 0.863, 0.507, 0.613, 0.605, 0.732, 0.632, 0.763, 0.754, 0.911, 0.516, 0.624, 0.616, 0.745, 0.643, 0.777, 0.767, 0.927, 0.545, 0.659, 0.65, 0.786, 0.679, 0.82, 0.81, 0.979, 0.697, 0.843, 0.832, 0.999, 0.868, 0.999, 0.999, 0.999, 0.736, 0.89, 0.878, 0.999, 0.916, 0.999, 0.999, 0.999], [0.644, 0.57, 0.575, 0.487, 0.557, 0.464, 0.471, 0.361, 0.624, 0.546, 0.552, 0.458, 0.532, 0.435, 0.442, 0.325, 0.519, 0.419, 0.426, 0.307, 0.402, 0.277, 0.286, 0.137, 0.493, 0.387, 0.395, 0.268, 0.368, 0.237, 0.246, 0.089, 0.484, 0.376, 0.384, 0.255, 0.357, 0.223, 0.233, 0.073, 0.455, 0.341, 0.35, 0.214, 0.321, 0.18, 0.19, 0.021, 0.303, 0.157, 0.168, 0.001, 0.132, 0.001, 0.001, 0.001, 0.264, 0.11, 0.122, 0.001, 0.084, 0.001, 0.001, 0.001]],
                        values=values,
                        evidence=['Weight <58kg', 'Underweight', 'Obese', 'Weight loss', 'Current smoker', 'Rheumatoid arthritis'],
                        evidence_card=[2, 2, 2, 2, 2, 2],
                        state_names={'Fragility fracture': ['Yes', 'No'],
                                    'Weight <58kg': ['No', 'Yes'],
                                    'Underweight': ['No', 'Yes'],
                                    'Obese': ['No', 'Yes'],
                                    'Weight loss': ['No', 'Yes'],
                                    'Current smoker': ['No', 'Yes'],
                                    'Rheumatoid arthritis': ['No', 'Yes']
                            })

        # Associating the parameters with the model structure.
        fragility_fracture.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d,cpd_e,cpd_f, cpd__f)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if fragility_fracture.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(fragility_fracture)
        q = infer.query(['Fragility fracture'], evidence={
            'Weight <58kg': weight,
            'Underweight': bmi1,
            'Obese': bmi2,
            'Weight loss': wl,
            'Current smoker': currentSmoker,
            'Rheumatoid arthritis': ra
            }, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

    def inferDecreasedSocialActivity(self, band, gender, age, major_health_conditions, depression, cognitive, adls):
        
        activity_limitation = BayesianModel([('Age_1', 'Decreased social activity'), ('Age_2', 'Decreased social activity'), ('Major health conditions_1', 'Decreased social activity'),('Major health conditions_2', 'Decreased social activity'), ('Depression', 'Decreased social activity'), ('Cognitive', 'Decreased social activity'), ('Activity_1', 'Decreased social activity'), ('Activity_2', 'Decreased social activity')])

        bg_risk = band['geriatricVulnerabilities']['decreasedSocialActivity'][gender] / 100

        # https://pubmed.ncbi.nlm.nih.gov/17530446/
        variables = [
            {'name': 'Age_1', 'r': 1.2, 'type': 'OR'},
            {'name': 'Age_2', 'r': 1.8, 'type': 'OR'},
            {'name': 'Major health conditions_1', 'r': 1.2, 'type': 'OR'},
            {'name': 'Major health conditions_2', 'r': 1.5, 'type': 'OR'},
            {'name': 'Depression', 'r': 4.7, 'type': 'OR'},
            {'name': 'Cognitive', 'r': 1.8, 'type': 'OR'},
            {'name': 'Activity_1', 'r': 1.4, 'type': 'OR'},
            {'name': 'Activity_2', 'r': 15.2, 'type': 'OR'}
        ]

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Age_1', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Age_1': ['Yes', 'No']})

        cpd_b = TabularCPD(variable='Age_2', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Age_2': ['Yes', 'No']})

        cpd_c = TabularCPD(variable='Major health conditions_1', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Major health conditions_1': ['Yes', 'No']})

        cpd_d = TabularCPD(variable='Major health conditions_2', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Major health conditions_2': ['Yes', 'No']})

        cpd_e = TabularCPD(variable='Depression', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Depression': ['Yes', 'No']})

        cpd_f = TabularCPD(variable='Cognitive', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Cognitive': ['Yes', 'No']})

        cpd_g = TabularCPD(variable='Activity_1', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Activity_1': ['Yes', 'No']})

        cpd_h = TabularCPD(variable='Activity_2', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Activity_2': ['Yes', 'No']})

        cpd__i = TabularCPD(variable='Decreased social activity', variable_card=2,
                        values=values,
                        evidence=['Age_1', 'Age_2', 'Major health conditions_1', 'Major health conditions_2', 'Depression', 'Cognitive', 'Activity_1', 'Activity_2'],
                        evidence_card=[2, 2, 2, 2, 2, 2, 2, 2],
                        state_names={'Decreased social activity': ['Yes', 'No'],
                                    'Age_1': ['No', 'Yes'],
                                    'Age_2': ['No', 'Yes'],
                                    'Major health conditions_1': ['No', 'Yes'],
                                    'Major health conditions_2': ['No', 'Yes'],
                                    'Depression': ['No', 'Yes'],
                                    'Cognitive': ['No', 'Yes'],
                                    'Activity_1': ['No', 'Yes'],
                                    'Activity_2': ['No', 'Yes']
                        })

        activity_limitation.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d,cpd_e,cpd_f,cpd_g,cpd_h, cpd__i)

        infer = VariableElimination(activity_limitation)
        q = infer.query(['Decreased social activity'], evidence={
            'Age_1': 'Yes' if age >= 70 and age < 80 else 'No',
            'Age_2': 'Yes' if age >= 80 else 'No',
            'Major health conditions_1': 'Yes' if major_health_conditions == 1 else 'No',
            'Major health conditions_2': 'Yes' if major_health_conditions > 2 else 'No',
            'Depression': depression,
            'Cognitive': cognitive,
            'Activity_1': 'Yes' if adls == 1 else 'No',
            'Activity_2': 'Yes' if adls == 2 else 'No'
            }, show_progress=False)

        return 1 if self.rng.random() < q.values[0] else 0

######------OUTCOMES--------######

    def inferPostOpDelirium(self, hod, frailty, ckd, cognitive, depression, badl, iadl, stroke, tia, currentSmoker, dm, htn, ihd, polypharmacy, ccf, vi):

        #pod = BayesianModel([('History of delirium', 'Post-op delirium'), ('Frailty', 'Post-op delirium'), ('Cognitive impairment', 'Post-op delirium'), ('CKD', 'Post-op delirium'), ('Depression', 'Post-op delirium'), ('BADL impairment', 'Post-op delirium'), ('IADL impairment', 'Post-op delirium'), ('Stroke', 'Post-op delirium'), ('TIA', 'Post-op delirium'), ('Current smoker', 'Post-op delirium'), ('Diabetes', 'Post-op delirium'), ('Hypertension', 'Post-op delirium'), ('IHD', 'Post-op delirium'), ('Polypharmacy', 'Post-op delirium'), ('Heart failure', 'Post-op delirium'), ('Visual impairment', 'Post-op delirium')])
        
        pod = BayesianModel([('History of delirium', 'Post-op delirium'), ('Frailty', 'Post-op delirium'), ('Cognitive impairment', 'Post-op delirium'), ('CKD', 'Post-op delirium'), ('Depression', 'Post-op delirium'), ('BADL impairment', 'Post-op delirium'), ('IADL impairment', 'Post-op delirium'), ('Stroke', 'Post-op delirium'), ('TIA', 'Post-op delirium'), ('Current smoker', 'Post-op delirium'), ('Visual impairment', 'Post-op delirium')])

        variables = [
            {'name': 'History of delirium', 'r': 6.4, 'type': 'OR'},
            {'name': 'Frailty', 'r': 4.1, 'type': 'OR'},
            {'name': 'Cognitive impairment', 'r': 2.7, 'type': 'OR'},
            {'name': 'CKD', 'r': 2.3, 'type': 'OR'},
            {'name': 'Depression', 'r': 2.2, 'type': 'OR'},
            {'name': 'BADL impairment', 'r': 2.1, 'type': 'OR'},
            {'name': 'IADL impairment', 'r': 1.9, 'type': 'OR'},
            {'name': 'Stroke', 'r': 2.1, 'type': 'OR'},
            {'name': 'TIA', 'r': 1.8, 'type': 'OR'},
            {'name': 'Current smoker', 'r': 1.8, 'type': 'OR'},
            # {'name': 'Diabetes', 'r': 1.4, 'type': 'OR'},
            # {'name': 'Hypertension', 'r': 1.3, 'type': 'OR'},
            # {'name': 'IHD', 'r': 1.2, 'type': 'OR'},
            # {'name': 'Polypharmacy', 'r': 1.4, 'type': 'OR'},
            # {'name': 'Heart failure', 'r': 1.4, 'type': 'OR'},
            {'name': 'Visual impairment', 'r': 1.89, 'type': 'OR'},
        ]

        bg_risk = 0.187

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='History of delirium', variable_card=2,
                                values=[[0],[1]],
                                state_names={'History of delirium': ['Yes', 'No']})

        cpd_b = TabularCPD(variable='Frailty', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Frailty': ['Yes', 'No']})

        cpd_c = TabularCPD(variable='Cognitive impairment', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Cognitive impairment': ['Yes', 'No']})

        cpd_d = TabularCPD(variable='CKD', variable_card=2,
                                values=[[0],[1]],
                                state_names={'CKD': ['Yes', 'No']})

        cpd_e = TabularCPD(variable='Depression', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Depression': ['Yes', 'No']})

        cpd_f = TabularCPD(variable='BADL impairment', variable_card=2,
                                values=[[0],[1]],
                                state_names={'BADL impairment': ['Yes', 'No']}) 

        cpd_g = TabularCPD(variable='IADL impairment', variable_card=2,
                                values=[[0],[1]],
                                state_names={'IADL impairment': ['Yes', 'No']})

        cpd_h = TabularCPD(variable='Stroke', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Stroke': ['Yes', 'No']})      

        cpd_i = TabularCPD(variable='TIA', variable_card=2,
                                values=[[0],[1]],
                                state_names={'TIA': ['Yes', 'No']})

        cpd_j = TabularCPD(variable='Current smoker', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Current smoker': ['Yes', 'No']})

        # cpd_k = TabularCPD(variable='Diabetes', variable_card=2,
        #                         values=[[0],[1]],
        #                         state_names={'Diabetes': ['Yes', 'No']})

        # cpd_l = TabularCPD(variable='Hypertension', variable_card=2,
        #                         values=[[0],[1]],
        #                         state_names={'Hypertension': ['Yes', 'No']})

        # cpd_m = TabularCPD(variable='IHD', variable_card=2,
        #                         values=[[0],[1]],
        #                         state_names={'IHD': ['Yes', 'No']})

        # cpd_n = TabularCPD(variable='Polypharmacy', variable_card=2,
        #                         values=[[0],[1]],
        #                         state_names={'Polypharmacy': ['Yes', 'No']})      

        # cpd_o = TabularCPD(variable='Heart failure', variable_card=2,
        #                         values=[[0],[1]],
        #                         state_names={'Heart failure': ['Yes', 'No']})

        cpd_p = TabularCPD(variable='Visual impairment', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Visual impairment': ['Yes', 'No']}) 

        cpd_pod = TabularCPD(variable='Post-op delirium', variable_card=2,
                        values=values,
                        #evidence=['History of delirium', 'Frailty', 'CKD', 'Cognitive impairment', 'Depression', 'BADL impairment', 'IADL impairment', 'Stroke', 'TIA', 'Current smoker', 'Diabetes', 'Hypertension', 'IHD', 'Polypharmacy', 'Heart failure', 'Visual impairment'],
                        evidence=['History of delirium', 'Frailty', 'CKD', 'Cognitive impairment', 'Depression', 'BADL impairment', 'IADL impairment', 'Stroke', 'TIA', 'Current smoker', 'Visual impairment'],
                        #evidence_card=[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
                        evidence_card=[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
                        state_names={'Post-op delirium': ['Yes', 'No'],
                                    'History of delirium':  ['No', 'Yes'],
                                    'Frailty': ['No', 'Yes'],
                                    'CKD': ['No', 'Yes'],
                                    'Cognitive impairment': ['No', 'Yes'],
                                    'Depression': ['No', 'Yes'],
                                    'BADL impairment': ['No', 'Yes'],
                                    'IADL impairment': ['No', 'Yes'],
                                    'Stroke': ['No', 'Yes'],
                                    'TIA': ['No', 'Yes'],
                                    'Current smoker': ['No', 'Yes'],
                                    # 'Diabetes': ['No', 'Yes'],
                                    # 'Hypertension': ['No', 'Yes'],
                                    # 'IHD': ['No', 'Yes'],
                                    # 'Polypharmacy': ['No', 'Yes'], 
                                    # 'Heart failure': ['No', 'Yes'], 
                                    'Visual impairment': ['No', 'Yes']
                            })           


        # Associating the parameters with the model structure.
        #pod.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d,cpd_e,cpd_f,cpd_g, cpd_h, cpd_i, cpd_j, cpd_k, cpd_l, cpd_m, cpd_n, cpd_o, cpd_p, cpd_pod)
        pod.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d,cpd_e,cpd_f,cpd_g, cpd_h, cpd_i, cpd_j, cpd_p, cpd_pod)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if pod.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(pod)
        q = infer.query(['Post-op delirium'], evidence={
            'History of delirium': hod,
            'Frailty': frailty,
            'CKD': ckd,
            'Cognitive impairment': cognitive,
            'Depression': depression,
            'BADL impairment': badl,
            'IADL impairment': iadl,
            'Stroke': stroke,
            'TIA': tia,
            'Current smoker': currentSmoker,
            # 'Diabetes': dm,
            # 'Hypertension': htn,
            # 'IHD': ihd,
            # 'Polypharmacy': polypharmacy, 
            # 'Heart failure': ccf, 
            'Visual impairment': vi
            }, show_progress=False)

        return q.values[0], 1 if self.rng.random() < q.values[0] else 0  

    def inferAllSurgicalComplications(self, frailty, depression, polypharmacy, currentSmoker, aud):   

        all_surg_comps = BayesianModel([('Frailty', 'All surgical complications'), ('Depression', 'All surgical complications'),('Polypharmacy', 'All surgical complications'), ('Current smoker', 'All surgical complications'), ('AUD', 'All surgical complications')])

        variables = [
            {'name': 'Frailty', 'r': 2.53, 'type': 'OR'},
            {'name': 'Depression', 'r': 1.77, 'type': 'OR'},
            {'name': 'Polypharmacy', 'r': 1.3, 'type': 'OR'},
            {'name': 'Current smoker', 'r': 1.52, 'type': 'RR'},
            {'name': 'AUD', 'r': 1.56, 'type': 'RR'},
        ]

        bg_risk = 0.30

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Frailty', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Frailty': ['Yes', 'No']})

        cpd_b = TabularCPD(variable='Depression', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Depression': ['Yes', 'No']})

        cpd_c = TabularCPD(variable='Polypharmacy', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Polypharmacy': ['Yes', 'No']})

        cpd_d = TabularCPD(variable='Current smoker', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Current smoker': ['Yes', 'No']})

        cpd_e = TabularCPD(variable='AUD', variable_card=2,
                                values=[[0],[1]],
                                state_names={'AUD': ['Yes', 'No']})

        cpd__a = TabularCPD(variable='All surgical complications', variable_card=2,
                        values=values,
                        evidence=['Frailty', 'Depression', 'Polypharmacy', 'Current smoker', 'AUD'],
                        evidence_card=[2, 2, 2, 2, 2],
                        state_names={'All surgical complications': ['Yes', 'No'],
                                    'Frailty':  ['No', 'Yes'],
                                    'Depression': ['No', 'Yes'],
                                    'Polypharmacy': ['No', 'Yes'],
                                    'Current smoker': ['No', 'Yes'],
                                    'AUD': ['No', 'Yes']
                            })     

        # Associating the parameters with the model structure.
        all_surg_comps.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d,cpd_e,cpd__a)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if fragility_fracture.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(all_surg_comps)
        q = infer.query(['All surgical complications'], evidence={
            'Frailty': frailty,
            'Depression': depression,
            'Polypharmacy': polypharmacy,
            'Current smoker': currentSmoker,
            'AUD': aud,
            }, show_progress=False)

        return q.values[0], 1 if self.rng.random() < q.values[0] else 0        

    def inferPostOperativePain(self, depression, currentSmoker):

        postop_pain = BayesianModel([('Depression', 'Postoperative pain'), ('Current smoker', 'Postoperative pain')])            

        variables = [
            {'name': 'Depression', 'r': 1.71, 'type': 'OR'},
            {'name': 'Current smoker', 'r': 1.33, 'type': 'OR'}
        ]

        bg_risk = 0.88

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Depression', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Depression': ['Yes', 'No']})

        cpd_b = TabularCPD(variable='Current smoker', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Current smoker': ['Yes', 'No']})

        cpd__a = TabularCPD(variable='Postoperative pain', variable_card=2,
                        values=values,
                        evidence=['Depression', 'Current smoker'],
                        evidence_card=[2, 2],
                        state_names={'Postoperative pain': ['Yes', 'No'],
                                    'Depression': ['No', 'Yes'],
                                    'Current smoker':  ['No', 'Yes']
                            })     

        # Associating the parameters with the model structure.
        postop_pain.add_cpds(cpd_a,cpd_b,cpd__a)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if fragility_fracture.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(postop_pain)
        q = infer.query(['Postoperative pain'], evidence={
            'Depression': depression,
            'Current smoker': currentSmoker,
            }, show_progress=False)

        return q.values[0], 1 if self.rng.random() < q.values[0] else 0

    def inferWoundComplications(self, currentSmoker, frailty, aud):

        wound_comps = BayesianModel([('Current smoker', 'Wound complications'), ('Frailty', 'Wound complications'), ('AUD', 'Wound complications')])            

        variables = [
            {'name': 'Current smoker', 'r': 2.15, 'type': 'OR'},
            {'name': 'Frailty', 'r': 2.85, 'type': 'OR'},
            {'name': 'AUD', 'r': 1.23, 'type': 'OR'}
        ]

        bg_risk = 0.051

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Current smoker', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Current smoker': ['Yes', 'No']})

        cpd_b = TabularCPD(variable='Frailty', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Frailty': ['Yes', 'No']})

        cpd_c = TabularCPD(variable='AUD', variable_card=2,
                                values=[[0],[1]],
                                state_names={'AUD': ['Yes', 'No']})

        cpd__a = TabularCPD(variable='Wound complications', variable_card=2,
                        values=values,
                        evidence=['Current smoker', 'Frailty', 'AUD'],
                        evidence_card=[2, 2, 2],
                        state_names={'Wound complications': ['Yes', 'No'],
                                    'Current smoker':  ['No', 'Yes'],
                                    'Frailty': ['No', 'Yes'],
                                    'AUD': ['No', 'Yes']
                            })     

        # Associating the parameters with the model structure.
        wound_comps.add_cpds(cpd_a,cpd_b,cpd_c,cpd__a)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if fragility_fracture.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(wound_comps)
        q = infer.query(['Wound complications'], evidence={
            'Current smoker': currentSmoker,
            'Frailty': frailty,
            'AUD': aud,
            }, show_progress=False)

        return q.values[0], 1 if self.rng.random() < q.values[0] else 0

    def inferPostOpSepsis(self, currentSmoker, frailty, aud, ccf, dm, ckd):

        sepsis = BayesianModel([('Current smoker', 'Post-op sepsis'), ('Frailty', 'Post-op sepsis'), ('AUD', 'Post-op sepsis'), ('Heart failure', 'Post-op sepsis'), ('Diabetes', 'Post-op sepsis'), ('CKD', 'Post-op sepsis')])            

        variables = [
            {'name': 'Current smoker', 'r': 1.54, 'type': 'OR'},
            {'name': 'Frailty', 'r': 3.84, 'type': 'OR'},
            {'name': 'AUD', 'r': 1.72, 'type': 'OR'},
            {'name': 'Heart failure', 'r': 2.53, 'type': 'OR'},
            {'name': 'Diabetes', 'r': 1.53, 'type': 'OR'},
            {'name': 'CKD', 'r': 1.26, 'type': 'OR'}
        ]

        bg_risk = 1.84 / 100

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Current smoker', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Current smoker': ['Yes', 'No']})

        cpd_b = TabularCPD(variable='Frailty', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Frailty': ['Yes', 'No']})

        cpd_c = TabularCPD(variable='AUD', variable_card=2,
                                values=[[0],[1]],
                                state_names={'AUD': ['Yes', 'No']})

        cpd_d = TabularCPD(variable='Heart failure', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Heart failure': ['Yes', 'No']})

        cpd_e = TabularCPD(variable='Diabetes', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Diabetes': ['Yes', 'No']})
    
        cpd_f = TabularCPD(variable='CKD', variable_card=2,
                                values=[[0],[1]],
                                state_names={'CKD': ['Yes', 'No']})

        cpd__a = TabularCPD(variable='Post-op sepsis', variable_card=2,
                        values=values,
                        evidence=['Current smoker', 'Frailty', 'AUD', 'Heart failure', 'Diabetes', 'CKD'],
                        evidence_card=[2, 2, 2, 2, 2, 2],
                        state_names={'Post-op sepsis': ['Yes', 'No'],
                                    'Current smoker':  ['No', 'Yes'],
                                    'Frailty': ['No', 'Yes'],
                                    'AUD': ['No', 'Yes'],
                                    'Heart failure': ['No', 'Yes'],
                                    'Diabetes': ['No', 'Yes'],
                                    'CKD': ['No', 'Yes']
                            })     

        # Associating the parameters with the model structure.
        sepsis.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d, cpd_e, cpd_f, cpd__a)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if fragility_fracture.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(sepsis)
        q = infer.query(['Post-op sepsis'], evidence={
            'Current smoker': currentSmoker,
            'Frailty': frailty,
            'AUD': aud,
            'Heart failure': ccf,
            'Diabetes': dm,
            'CKD': ckd,
            }, show_progress=False)

        return q.values[0], 1 if self.rng.random() < q.values[0] else 0               


    def inferPostOpPulmComps(self, currentSmoker, frailty, aud, ccf):

        sepsis = BayesianModel([('Current smoker', 'Post-op pulmonary complications'), ('Frailty', 'Post-op pulmonary complications'), ('AUD', 'Post-op pulmonary complications'), ('Heart failure', 'Post-op pulmonary complications')])            

        variables = [
            {'name': 'Current smoker', 'r': 1.54, 'type': 'OR'},
            {'name': 'Frailty', 'r': 3.84, 'type': 'OR'},
            {'name': 'AUD', 'r': 1.72, 'type': 'OR'},
            {'name': 'Heart failure', 'r': 2.53, 'type': 'OR'}
        ]

        bg_risk = 14.4 / 100

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Current smoker', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Current smoker': ['Yes', 'No']})

        cpd_b = TabularCPD(variable='Frailty', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Frailty': ['Yes', 'No']})

        cpd_c = TabularCPD(variable='AUD', variable_card=2,
                                values=[[0],[1]],
                                state_names={'AUD': ['Yes', 'No']})

        cpd_d = TabularCPD(variable='Heart failure', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Heart failure': ['Yes', 'No']})

        cpd__a = TabularCPD(variable='Post-op pulmonary complications', variable_card=2,
                        values=values,
                        evidence=['Current smoker', 'Frailty', 'AUD', 'Heart failure'],
                        evidence_card=[2, 2, 2, 2],
                        state_names={'Post-op pulmonary complications': ['Yes', 'No'],
                                    'Current smoker': ['No', 'Yes'],
                                    'Frailty': ['No', 'Yes'],
                                    'AUD': ['No', 'Yes'],
                                    'Heart failure': ['No', 'Yes']
                            })     

        # Associating the parameters with the model structure.
        sepsis.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d, cpd__a)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if fragility_fracture.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(sepsis)
        q = infer.query(['Post-op pulmonary complications'], evidence={
            'Current smoker': currentSmoker,
            'Frailty': frailty,
            'AUD': aud,
            'Heart failure': ccf
            }, show_progress=False)

        return q.values[0], 1 if self.rng.random() < q.values[0] else 0


    def inferPostOpNeuroComps(self, currentSmoker, frailty):

        neuro_comps = BayesianModel([('Current smoker', 'Post-op neurological complications'), ('Frailty', 'Post-op neurological complications')])            

        variables = [
            {'name': 'Current smoker', 'r': 1.38, 'type': 'OR'},
            {'name': 'Frailty', 'r': 3.41, 'type': 'OR'}
        ]

        bg_risk = 0.0032

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Current smoker', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Current smoker': ['Yes', 'No']})

        cpd_b = TabularCPD(variable='Frailty', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Frailty': ['Yes', 'No']})

        cpd__a = TabularCPD(variable='Post-op neurological complications', variable_card=2,
                        values=values,
                        evidence=['Current smoker', 'Frailty'],
                        evidence_card=[2, 2],
                        state_names={'Post-op neurological complications': ['Yes', 'No'],
                                    'Current smoker':  ['No', 'Yes'],
                                    'Frailty': ['No', 'Yes']
                            })     

        # Associating the parameters with the model structure.
        neuro_comps.add_cpds(cpd_a,cpd_b,cpd__a)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if fragility_fracture.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(neuro_comps)
        q = infer.query(['Post-op neurological complications'], evidence={
            'Current smoker': currentSmoker,
            'Frailty': frailty
            }, show_progress=False)

        return q.values[0], 1 if self.rng.random() < q.values[0] else 0 

    def inferSurviveCPR(self, age, badl, ckd):

        cpr = BayesianModel([('Age>70', 'No CPR outcome'), ('Age>75', 'No CPR outcome'), ('Age>80', 'No CPR outcome'), ('BADL impairment', 'No CPR outcome'), ('CKD', 'No CPR outcome')])            

        variables = [
            {'name': 'Age>70', 'r': 1.5, 'type': 'OR'},
            {'name': 'Age>75', 'r': 2.8, 'type': 'OR'},
            {'name': 'Age>80', 'r': 2.7, 'type': 'OR'},
            {'name': 'BADL impairment', 'r': 3.2, 'type': 'OR'},
            {'name': 'CKD', 'r': 1.9, 'type': 'OR'}
        ]

        bg_risk = 0.825

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Age>70', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Age>70': ['Yes', 'No']})

        cpd_b = TabularCPD(variable='Age>75', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Age>75': ['Yes', 'No']})

        cpd_c = TabularCPD(variable='Age>80', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Age>80': ['Yes', 'No']})

        cpd_d = TabularCPD(variable='BADL impairment', variable_card=2,
                                values=[[0],[1]],
                                state_names={'BADL impairment': ['Yes', 'No']})

        cpd_e = TabularCPD(variable='CKD', variable_card=2,
                                values=[[0],[1]],
                                state_names={'CKD': ['Yes', 'No']})

        cpd__a = TabularCPD(variable='No CPR outcome', variable_card=2,
                        values=values,
                        evidence=['Age>70', 'Age>75', 'Age>80', 'BADL impairment', 'CKD'],
                        evidence_card=[2, 2, 2, 2, 2],
                        state_names={'No CPR outcome': ['Yes', 'No'],
                                    'Age>70':  ['No', 'Yes'],
                                    'Age>75': ['No', 'Yes'],
                                    'Age>80': ['No', 'Yes'],
                                    'BADL impairment': ['No', 'Yes'],
                                    'CKD': ['No', 'Yes']
                            })     

        # Associating the parameters with the model structure.
        cpr.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d, cpd_e, cpd__a)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if fragility_fracture.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(cpr)
        q = infer.query(['No CPR outcome'], evidence={
            'Age>70': 'Yes' if age > 70 and age <= 75 else 'No',
            'Age>75': 'Yes' if age > 75 and age <= 80 else 'No',
            'Age>80': 'Yes' if age > 80 else 'No',
            'BADL impairment': badl,
            'CKD': ckd
            }, show_progress=False)

        return q.values[0], 1 if self.rng.random() < q.values[0] else 0 

    def inferITUAdmission(self, currentSmoker, aud, anaemia, frailty, asa):

        itu = BayesianModel([('Current smoker', 'Post-op ITU admission'), ('AUD', 'Post-op ITU admission'), ('Anaemia', 'Post-op ITU admission'), ('Frailty', 'Post-op ITU admission'), ('ASA3', 'Post-op ITU admission'), ('ASA4', 'Post-op ITU admission')])            

        variables = [
            {'name': 'Current smoker', 'r': 1.6, 'type': 'OR'},
            {'name': 'AUD', 'r': 1.29, 'type': 'OR'},
            {'name': 'Anaemia', 'r': 1.588, 'type': 'OR'},
            {'name': 'Frailty', 'r': 2.52, 'type': 'OR'},
            {'name': 'ASA3', 'r': 5.199, 'type': 'OR'},
            {'name': 'ASA4', 'r': 29.481, 'type': 'OR'},
        ]

        bg_risk = 0.0048 # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5363100/

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Current smoker', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Current smoker': ['Yes', 'No']})
        
        cpd_b = TabularCPD(variable='AUD', variable_card=2,
                                values=[[0],[1]],
                                state_names={'AUD': ['Yes', 'No']})
        
        cpd_c = TabularCPD(variable='Anaemia', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Anaemia': ['Yes', 'No']})

        cpd_d = TabularCPD(variable='Frailty', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Frailty': ['Yes', 'No']})
    
        cpd_e = TabularCPD(variable='ASA3', variable_card=2,
                                values=[[0],[1]],
                                state_names={'ASA3': ['Yes', 'No']})

        cpd_f = TabularCPD(variable='ASA4', variable_card=2,
                                values=[[0],[1]],
                                state_names={'ASA4': ['Yes', 'No']})

        cpd__a = TabularCPD(variable='Post-op ITU admission', variable_card=2,
                        values=values,
                        evidence=['Current smoker', 'AUD', 'Anaemia', 'Frailty', 'ASA3', 'ASA4'],
                        evidence_card=[2, 2, 2, 2, 2, 2],
                        state_names={'Post-op ITU admission': ['Yes', 'No'],
                                    'Current smoker': ['Yes', 'No'],
                                    'AUD': ['No', 'Yes'],
                                    'Anaemia': ['No', 'Yes'],
                                    'Frailty': ['No', 'Yes'],
                                    'ASA3': ['No', 'Yes'],
                                    'ASA4': ['No', 'Yes']
                            })     

        # Associating the parameters with the model structure.
        itu.add_cpds(cpd_a,cpd_b,cpd_c, cpd_d, cpd_e, cpd_f, cpd__a)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if fragility_fracture.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(itu)
        q = infer.query(['Post-op ITU admission'], evidence={
           'Current smoker': currentSmoker,
            'AUD': aud,
            'Anaemia': anaemia,
            'Frailty': frailty,
            'ASA3': 'Yes' if asa == 3 else 'No',
            'ASA4': 'Yes' if asa == 4 else 'No'
            }, show_progress=False)

        return q.values[0], 1 if self.rng.random() < q.values[0] else 0 

    def inferPIMs(self, dm, poly):    

        pims = BayesianModel([('Diabetes', 'Potentially inappropriate medications'), ('Polypharmacy', 'Potentially inappropriate medications')])            

        variables = [
            {'name': 'Diabetes', 'r': 1.57, 'type': 'OR'},
            {'name': 'Polypharmacy', 'r': 3, 'type': 'OR'}
        ]

        bg_risk = 0.51

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Diabetes', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Diabetes': ['Yes', 'No']})

        cpd_b = TabularCPD(variable='Polypharmacy', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Polypharmacy': ['Yes', 'No']})

        cpd__a = TabularCPD(variable='Potentially inappropriate medications', variable_card=2,
                        values=values,
                        evidence=['Diabetes', 'Polypharmacy'],
                        evidence_card=[2, 2],
                        state_names={'Potentially inappropriate medications': ['Yes', 'No'],
                                    'Diabetes': ['No', 'Yes'],
                                    'Polypharmacy': ['No', 'Yes']
                            })     

        # Associating the parameters with the model structure.
        pims.add_cpds(cpd_a,cpd_b,cpd__a)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if fragility_fracture.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(pims)
        q = infer.query(['Potentially inappropriate medications'], evidence={
            'Diabetes': dm,
            'Polypharmacy': poly
            }, show_progress=False)

        return q.values[0], 1 if self.rng.random() < q.values[0] else 0 

    def inferIncreasedLOS(self, frailty, aud, disability, asa):

        los = BayesianModel([('Frailty', 'Increased length of stay'), ('AUD', 'Increased length of stay'), ('Disability', 'Increased length of stay'), ('ASA3', 'Increased length of stay'), ('ASA4', 'Increased length of stay')])            

        variables = [
            {'name': 'Frailty', 'r': 2.78, 'type': 'OR'},
            {'name': 'AUD', 'r': 1.24, 'type': 'OR'},
            {'name': 'Disability', 'r': 2.36, 'type': 'OR'},
            {'name': 'ASA3', 'r': 1.7, 'type': 'OR'},
            {'name': 'ASA4', 'r': 3.34, 'type': 'OR'},
        ]

        bg_risk = 0.342

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Frailty', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Frailty': ['Yes', 'No']})
        
        cpd_b = TabularCPD(variable='AUD', variable_card=2,
                                values=[[0],[1]],
                                state_names={'AUD': ['Yes', 'No']})
        
        cpd_c = TabularCPD(variable='Disability', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Disability': ['Yes', 'No']})

        cpd_e = TabularCPD(variable='ASA3', variable_card=2,
                                values=[[0],[1]],
                                state_names={'ASA3': ['Yes', 'No']})

        cpd_f = TabularCPD(variable='ASA4', variable_card=2,
                                values=[[0],[1]],
                                state_names={'ASA4': ['Yes', 'No']})

        cpd__a = TabularCPD(variable='Increased length of stay', variable_card=2,
                        values=values,
                        evidence=['Frailty', 'AUD', 'Disability', 'ASA3', 'ASA4'],
                        evidence_card=[2, 2, 2, 2, 2],
                        state_names={'Increased length of stay': ['Yes', 'No'],
                                    'Frailty': ['No', 'Yes'],
                                    'AUD': ['No', 'Yes'],
                                    'Disability': ['No', 'Yes'],
                                    'ASA3': ['No', 'Yes'],
                                    'ASA4': ['No', 'Yes']
                            })     

        # Associating the parameters with the model structure.
        los.add_cpds(cpd_a,cpd_b,cpd_c, cpd_e, cpd_f, cpd__a)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if fragility_fracture.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(los)
        q = infer.query(['Increased length of stay'], evidence={
            'Frailty': frailty,
            'AUD': aud,
            'Disability': disability,
            'ASA3': 'Yes' if asa == 3 else 'No',
            'ASA4': 'Yes' if asa == 4 else 'No'
            }, show_progress=False)

        return q.values[0], 1 if self.rng.random() < q.values[0] else 0 

    def inferFunctionalDecline(self, iadl):

        decline = BayesianModel([('IADL impairment', 'Functional decline')])            

        variables = [
            {'name': 'IADL impairment', 'r': 2.87, 'type': 'OR'}
        ]

        bg_risk = 0.201

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='IADL impairment', variable_card=2,
                                values=[[0],[1]],
                                state_names={'IADL impairment': ['Yes', 'No']})


        cpd__a = TabularCPD(variable='Functional decline', variable_card=2,
                        values=values,
                        evidence=['IADL impairment'],
                        evidence_card=[2],
                        state_names={'Functional decline': ['Yes', 'No'],
                                    'IADL impairment':  ['No', 'Yes']
                            })     

        # Associating the parameters with the model structure.
        decline.add_cpds(cpd_a,cpd__a)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if fragility_fracture.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(decline)
        q = infer.query(['Functional decline'], evidence={
            'IADL impairment': iadl
            }, show_progress=False)

        return q.values[0], 1 if self.rng.random() < q.values[0] else 0 

    def inferNeutropaenicEvents(self, comorbidity, dm):

        neutropaenic = BayesianModel([('Comorbidity', 'Neutropaenic events'), ('Diabetes', 'Neutropaenic events')])            

        variables = [
            {'name': 'Comorbidity', 'r': 1.54, 'type': 'OR'},
            {'name': 'Diabetes', 'r': 1.32, 'type': 'OR'}
        ]

        bg_risk = 0.107

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Comorbidity', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Comorbidity': ['Yes', 'No']})

        cpd_b = TabularCPD(variable='Diabetes', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Diabetes': ['Yes', 'No']})

        cpd__a = TabularCPD(variable='Neutropaenic events', variable_card=2,
                        values=values,
                        evidence=['Comorbidity', 'Diabetes'],
                        evidence_card=[2, 2],
                        state_names={'Neutropaenic events': ['Yes', 'No'],
                                    'Comorbidity':  ['No', 'Yes'],
                                    'Diabetes': ['No', 'Yes']
                            })     

        # Associating the parameters with the model structure.
        neutropaenic.add_cpds(cpd_a,cpd_b,cpd__a)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if fragility_fracture.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(neutropaenic)
        q = infer.query(['Neutropaenic events'], evidence={
            'Comorbidity': comorbidity,
            'Diabetes': dm
            }, show_progress=False)

        return q.values[0], 1 if self.rng.random() < q.values[0] else 0

    def inferNursingHomeAdmission(self, currentSmoker, frailty, badl, difficultyWalkingOutside):

        nh_admission = BayesianModel([('Current smoker', 'Nursing home admission'), ('Frailty', 'Nursing home admission'), ('BADL impairment', 'Nursing home admission'), ('Difficulty walking outside', 'Nursing home admission')])            

        variables = [
            {'name': 'Current smoker', 'r': 1.9, 'type': 'OR'},
            {'name': 'Frailty', 'r': 5.58, 'type': 'OR'},
            {'name': 'BADL impairment', 'r': 3.25, 'type': 'OR'},
            {'name': 'Difficulty walking outside', 'r': 3.6, 'type': 'OR'}
        ]

        bg_risk = 0.05

        values = self.calculateCPDTable(bg_risk, variables)

        cpd_a = TabularCPD(variable='Current smoker', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Current smoker': ['Yes', 'No']})

        cpd_b = TabularCPD(variable='Frailty', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Frailty': ['Yes', 'No']})

        cpd_c = TabularCPD(variable='BADL impairment', variable_card=2,
                                values=[[0],[1]],
                                state_names={'BADL impairment': ['Yes', 'No']})
        
        cpd_d = TabularCPD(variable='Difficulty walking outside', variable_card=2,
                                values=[[0],[1]],
                                state_names={'Difficulty walking outside': ['Yes', 'No']})

        cpd__a = TabularCPD(variable='Nursing home admission', variable_card=2,
                        values=values,
                        evidence=['Current smoker', 'Frailty', 'BADL impairment', 'Difficulty walking outside'],
                        evidence_card=[2, 2, 2, 2],
                        state_names={'Nursing home admission': ['Yes', 'No'],
                                    'Current smoker':  ['No', 'Yes'],
                                    'Frailty': ['No', 'Yes'],
                                    'BADL impairment': ['No', 'Yes'],
                                    'Difficulty walking outside': ['No', 'Yes']
                            })     

        # Associating the parameters with the model structure.
        nh_admission.add_cpds(cpd_a,cpd_b,cpd_c,cpd_d, cpd__a)

        # Checking if the cpds are valid for the model.
        #print(f"{'Model is okay' if fragility_fracture.check_model() else 'Model is incorrect'}")

        infer = VariableElimination(nh_admission)
        q = infer.query(['Nursing home admission'], evidence={
            'Current smoker': currentSmoker,
            'Frailty': frailty,
            'BADL impairment': badl,
            'Difficulty walking outside': difficultyWalkingOutside
            }, show_progress=False)

        return q.values[0], 1 if self.rng.random() < q.values[0] else 0


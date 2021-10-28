import numpy as np
import pandas as pd
import sqlite3, yaml
from util.utilities import Utilities

# Load config file
fbc_ranges = None
with open("data/fbc.yaml", 'r') as stream:
    fbc_ranges = yaml.safe_load(stream)

class Laboratory:
    def __init__(self, medications, patient, index, cr_dist, u, rng):
        self.patient = patient
        self.index = index
        self.cr_dist = cr_dist
        self.medications = medications
        self.utilities: Utilities = u
        self.rng: np.random = rng

    def check_medications(self, drugs: list) -> bool:
        for m in self.medications:
            for d in drugs:
                if m == d:
                    return True
        return False

    def sodium(self) -> float:
        # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2390974/
        # na_normal = self.rng.normal(141, 1.9)
        # na_low = self.rng.normal(132, 2.2)
        # na_high = self.rng.normal(147, 2.1)

        na = self.rng.normal(141, 1.9)

        def sample(dist):
            if dist == 'LOW':
                return self.rng.normal(132, 2.2)
            elif dist == 'HIGH':
                return self.rng.normal(147, 2.1)

        if self.check_medications(['bendroflumethiazide', 'indapamide']) == True:
            # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3041494/
            if self.rng.binomial(1, p=0.11) == 1:
                na = sample('LOW')
        
        if self.check_medications(['sertraline', 'citalopram', 'fluoxetine', 'paroxetine', 'escitalopram']) == True:
            # https://pubmed.ncbi.nlm.nih.gov/16896026/
            if self.rng.binomial(1, p=0.15) == 1:
                na = sample('LOW')
        
        if self.check_medications(['carbamazepine']) == True:
            # https://pubmed.ncbi.nlm.nih.gov/16896026/
            if self.rng.binomial(1, p=0.20) == 1:
                na = sample('LOW')

        # https://cks.nice.org.uk/topics/hyponatraemia/background-information/causes/#additional-information-on-causes
        if self.patient['heartFailure'] == 1:
            if self.rng.binomial(1, p=0.20) == 1:
                na = sample('LOW')

        if self.patient['cancer_site'] == 'lung':
            # 25% SCLC - https://ascopubs.org/doi/10.1200/JCO.2005.04.4859
            if self.rng.binomial(1, p=0.25) == 1:
                if self.rng.binomial(1, p=0.19) == 1: #18.9% https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5764155/
                    na = sample('LOW')
            else:
                if self.rng.binomial(1, p=0.03) == 1: #2-4% https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5764155/
                    na = sample('LOW')
                    
        return na

    def potassium(self) -> float:

        k = self.rng.normal(4.1, 0.7) # https://www.researchgate.net/publication/268415821_RELATIONSHIPS_BETWEEN_NA_AND_K_CONCENTRATION_IN_HUMAN_BLOOD_AND_SERUM/figures?lo=1

        def sample(dist):
            if dist == 'LOW': # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1884982/
                return self.rng.choice([2.7, 2.8, 2.9, 3, 3.1, 3.2, 3.3, 3.4], p=[0.038, 0.038, 0.038, 0.128, 0.128, 0.128, 0.26, 0.26])
            elif dist == 'HIGH': # https://bmcnephrol.biomedcentral.com/track/pdf/10.1186/s12882-019-1250-0.pdf
                return self.rng.choice([5,5.1,5.2,5.3,5.4,5.5,5.6,5.7,5.8,5.9], p=[0.927, 0.073])

        if self.check_medications(['bendroflumethiazide', 'indapamide']) == True:
            # https://pubmed.ncbi.nlm.nih.gov/16390355/
            if self.rng.binomial(1, p=0.085) == 1:
                k = sample('LOW')

        if self.check_medications(['ramipril', 'enalipril', 'lisinopril']) == True:
            # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2710386/
            if self.rng.binomial(1, p=0.204) == 1:
                k = sample('HIGH')

        if self.check_medications(['candesartan', 'losartan']) == True:
            # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2710386/
            if self.rng.binomial(1, p=0.31) == 1:
                k = sample('HIGH')

        if self.patient['ckd'] == 1:
            # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6340899/
            if self.rng.binomial(1, p=0.54) == 1:
                k = sample('HIGH')

        if self.patient['diabetes'] == 1:
            # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2398240/
            if self.rng.binomial(1, p=0.15) == 1:
                k = sample('HIGH')

        if self.patient['heartFailure'] == 1:
            # https://onlinelibrary.wiley.com/doi/10.1002/ejhf.226
            if self.rng.binomial(1, p=0.11) == 1:
                k = sample('HIGH')

        if self.check_medications('spironolactone', 'eplerenone') == 1:
            # https://onlinelibrary.wiley.com/doi/10.1002/ejhf.226
            if self.rng.binomial(1, p=0.496) == 1:
                k = sample('HIGH')

        return k

    def creatinine(self) -> float:
        patient = self.patient
        gender = self.patient['gender']
        rng = self.rng
        cr_dist = self.cr_dist
        index = self.index
        u = self.utilities
        if patient['ckd'] == 1:
            cr = round(rng.choice(cr_dist[index], 1)[0])
            crcl = u.calculateCrCl(patient['height'], patient['weight'], patient['age'], gender, cr)
            while crcl > 34:
                crcl = u.calculateCrCl(patient['height'], patient['weight'], patient['age'], gender, cr)
                cr += 1
            return cr
        else: # Assign normal ageing creatinine
            return round(rng.choice(cr_dist[index], 1)[0])

    def fbc(self) -> dict:
        new_fbc = {}
        s = self.patient['gender']
        age = self.patient['age']
        a = self.patient['anaemia']

        def map_hb_severity(severity):
            # https://www.researchgate.net/publication/44660310_Prevalence_incidence_and_types_of_mild_anemia_in_the_elderly_The_Health_and_Anemia_population-based_study/figures?lo=1
            if severity == 'mild':
                return self.rng.uniform(10, 11.9 if s == 'f' else 12.9)
            elif severity == 'moderate':
                return self.rng.uniform(8, 9.9)
            else:
                return self.rng.uniform(6, 8)

        def hb_age_map(age):
            if age >= 66 and age < 70:
                severity = self.rng.choice(['mild', 'moderate', 'severe'], p=[0.857, 0.127, 0.016])
                return map_hb_severity(severity)
            elif age >= 70 and age < 75:
                severity = self.rng.choice(['mild', 'moderate', 'severe'], p=[0.876, 0.112, 0.012])
                return map_hb_severity(severity)
            elif age >= 75 and age < 80:
                severity = self.rng.choice(['mild', 'moderate', 'severe'], p=[0.843, 0.134, 0.023])
                return map_hb_severity(severity)
            elif age >= 80 and age < 85:
                severity = self.rng.choice(['mild', 'moderate', 'severe'], p=[0.826, 0.158, 0.016])
                return map_hb_severity(severity)
            elif age >= 85 and age < 89:
                severity = self.rng.choice(['mild', 'moderate', 'severe'], p=[0.831, 0.158, 0.011])
                return map_hb_severity(severity)
            elif age >= 90:
                severity = self.rng.choice(['mild', 'moderate', 'severe'], p=[0.754, 0.215, 0.031])
                return map_hb_severity(severity)

        for key, v in fbc_ranges.items():
            if key == 'hb':
                if a == 1:
                    hb = hb_age_map(age)
                    new_fbc[key] = round(hb, 1)       
                else:
                    param = self.rng.uniform(v[s]['ll'],v[s]['ul'])
                    new_fbc[key] = round(param, 1) 
            elif key == 'mcv':
                mcv = 90
                if self.patient['aud'] == 1:
                    # PMID: 7226720     
                    if self.rng.binomial(1, 0.495) == 1:
                        mcv = self.rng.uniform(100,110)
                    else:
                        mcv = self.rng.uniform(v[s]['ll'],v[s]['ul'])
                if self.patient['anaemiaCause'] == 'b12' or self.patient['anaemiaCause'] == 'folate':   
                    if self.rng.binomial(1, 0.495) == 1:
                        mcv = self.rng.uniform(100,130)
                    else:
                        mcv = self.rng.uniform(v[s]['ll'],v[s]['ul'])
                if self.patient['anaemiaCause'] == 'ida':
                    #PMID 10792396
                    if self.rng.binomial(1, 0.50) == 1:
                        mcv = self.rng.uniform(70,79)
                    else:
                        mcv = self.rng.uniform(v[s]['ll'],v[s]['ul'])
                new_fbc[key] = round(mcv, 1)
            else:
                param = self.rng.uniform(v[s]['ll'],v[s]['ul'])
                new_fbc[key] = round(param, 1)

        return new_fbc

# con = sqlite3.connect('data/database.db')
# ##con.set_trace_callback(print)
# cur = con.cursor()
# cur.execute("SELECT id, GROUP_CONCAT(agent, ',') AS list FROM medications GROUP BY id")
# df = pd.read_csv('tests/test_data.csv')       
# for row in cur.fetchall():
#     l = Laboratory(row[1].split(","), df.iloc[[row[0] - 1]].to_dict('records')[0])
#     na = l.sodium()
#     #print(l.sodium())
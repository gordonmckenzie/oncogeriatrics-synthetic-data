import numpy as np
import pandas as pd
import sqlite3

class Laboratory:
    def __init__(self, medications, patient):
        self.patient = patient
        self.medications = medications
        self.rng: np.random = np.random.default_rng()

    def check_medications(self, drugs):
        for m in self.medications:
            for d in drugs:
                if m == d:
                    return True
        return False

    def sodium(self):
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

con = sqlite3.connect('data/database.db')
##con.set_trace_callback(print)
cur = con.cursor()
cur.execute("SELECT id, GROUP_CONCAT(agent, ',') AS list FROM medications GROUP BY id")
df = pd.read_csv('tests/test_data.csv')       
for row in cur.fetchall():
    l = Laboratory(row[1].split(","), df.iloc[[row[0] - 1]].to_dict('records')[0])
    na = l.sodium()
    #print(l.sodium())
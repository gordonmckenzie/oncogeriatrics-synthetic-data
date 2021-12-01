import numpy as np
import csv
from util.database import Database

class Prescriber():
    def __init__(self, patient, rng, do_not_write_to_db = False, write_to_csv=False):
        self.rng: np.random = rng
        self.patient = patient
        self.meds = []
        self.db: Database = Database()
        self.do_not_write_to_db = do_not_write_to_db
        self.write_to_csv = write_to_csv

    def flatten(self, meds):
        flattened_list = []
        for m in meds:
            if isinstance(m, list) == True:
                for d in m: flattened_list.append(d)
            else:
                flattened_list.append(m)
        return flattened_list

    def store_as_csv(self, id, agent, reason):
        return True
        # with open(f'results/data/prescribing.csv', 'a', newline='') as csvfile:
        #     csv_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        #     csv_writer.writerow([id, agent, reason])

    def store(self, agent: str, reason: str, potential_duplicates: list, egfr=None):
        # First check not duplicated 
        if self.check_medications(potential_duplicates) == False:
            # Then check eGFR okay
            if egfr is not None and self.eGFR() <= egfr:
                return None
            else:
                if self.do_not_write_to_db == False:
                    self.db.insert_prescription(self.patient['id'], agent, reason)
                if self.write_to_csv == True:
                    self.store_as_csv(self.patient['id'], agent, reason)
                self.meds.append(agent)

    def eGFR(self):
        egfr = 186 * np.power((self.patient['cr'] / 88.4), -1.154) * np.power(self.patient['age'] , -0.203) * (0.742 if self.patient['gender'] == 'f' else 1) * (1.210 if 'BLACK' in self.patient['ethnicity']  else 1)
        return egfr

    def check_contraindication(self, diseases):
        for k, v in self.patient.items():
            if v == 1:
                for d in diseases:
                    if k == d:
                        return True
        return False


    def check_medications(self, drugs):
        meds_list = self.flatten(self.meds)
        for m in meds_list:
            for d in drugs:
                if m == d:
                    return True
        return False
            
    def corticosteroids(self):
        # https://academic.oup.com/qjmed/article/93/2/105/1517915
        agent = self.rng.choice(['prednisolone', 'hydrocortisone', 'dexamethasone'], 1, p=[0.90, 0.08, 0.02])[0]
        self.store(agent, 'unknown', ['prednisolone', 'hydrocortisone', 'dexamethasone'])
        self.store('alendronic acid', 'osteoporosis prophylaxis', ['alendronic acid'])
        self.store('vitamin D with calcium', 'osteoporosis prophylaxis',  ['vitamin D with calcium', 'vitamin D'])

    def antihypertensives(self):
        # https://pubmed.ncbi.nlm.nih.gov/23091084/
        # https://bnf.nice.org.uk/treatment-summary/hypertension.html
        px = self.rng.choice(['acei', 'arb', 'ccb', 'bb', 'thiazide', 'loop', 'poly'], 1, p=[0.049, 0.037, 0.112, 0.059, 0.025, 0.033, 0.685])[0]
        
        def poly():
            regimen = self.rng.choice([0,1,2,3,4], 1, p=[0.5, 0.15, 0.2, 0.1, 0.05])[0]
            regimen_map = [
                ['amlodipine', 'ramipril'], 
                ['amlodipine', 'candesartan'], #Prevalence of cough 10%, 5% need to change to ACEi https://pubmed.ncbi.nlm.nih.gov/8862965/
                ['amlodipine', 'indapamide'], 
                ['ramipril', 'amlodipine', 'indapamide'], 
                ['candesartan', 'amlodipine', 'indapamide']
            ]
            for i, set in enumerate(regimen_map):
                if i == regimen: return set

        choices = {
            'acei': self.rng.choice(['ramipril', 'lisinopril'], 1, p=[0.8,0.2])[0],
            'arb': self.rng.choice(['candesartan', 'losartan'], 1, p=[0.8,0.2])[0], 
            'bb': self.rng.choice(['bisoprolol', 'atenolol'], 1, p=[0.8,0.2])[0],
            'ccb': 'amlodipine',
            'thiazide': self.rng.choice(['indapamide', 'bendroflumethiazide'], 1, p=[0.8,0.2])[0],
            'loop': 'furosemide',
            'poly': poly()
        }
        final = choices.get(px)
        potential_duplicates = ['ramipril', 'lisionpril' ,'candesartan', 'losartan', 'bisoprolol', 'atenolol', 
                    'indapamide', 'amlodipine', 'bendroflumethiazide', 'furosemide']
        if isinstance(final, list) == True:
            for f in final: self.store(f, 'hypertension', potential_duplicates)
        else:
            self.store(final, 'hypertension', potential_duplicates)

    def chads_vasc(self):
        age = 2 if self.patient['age'] >= 75 else 1
        sex = 1 if self.patient['gender'] == 'f' else 0
        chf = 1 if self.patient['heartFailure'] == 1 else 0
        htn = 1 if self.patient['hypertension'] == 1 else 0
        cva = 1 if self.patient['stroke'] == 1 or self.patient['tia'] == 1 else 0
        cvd = 1 if self.patient['mi'] == 1 or self.patient['pvd'] == 1 else 0
        dm = 1 if self.patient['t1dm'] == 1 or self.patient['t2dm'] == 1 else 0

        return(sum([age, sex, chf, htn, cva, cvd, dm]))

    def hasbled(self):
        htn = 1 if (self.patient['hypertension'] == 1 and self.rng.random() < 0.69) else 0 # Only 69% controlled https://www.ahajournals.org/doi/10.1161/CIRCULATIONAHA.104.490599
        ckd = 1 if self.patient['cr'] > 200 else 0
        liv = 1 if self.patient['liverDisease'] == 1 else 0
        cva = 1 if self.patient['stroke'] == 1 or self.patient['tia'] == 1 else 0
        # Need major bleeding and labile INR prevalence
        age = 1 if self.patient['age'] > 65 else 0
        med = 1 if self.check_medications(['aspirin', 'clopidogrel', 'ibuprofen', 'naproxen', 'celecoxib']) == True else 0
        alc = 1 if self.patient['aud'] == 1 or (self.patient['drinksAlcohol'] == 1 and self.rng.random() < 0.4) else 0 # Around 40% are problem drinkers > 8 units/week https://journals.sagepub.com/doi/full/10.1177/1455072520954335

        return(sum([htn, ckd, liv, htn, cva, age, med, alc]))

    def af(self):
        chadsvasc = self.chads_vasc()
        hasbled = self.hasbled()
        anticoag = False
        if chadsvasc >= 1 and hasbled < 3:
            anticoag = True
        if anticoag == True:
            self.store(self.rng.choice(['warfarin', 'rivaroxaban', 'apixaban', 'edoxaban'], 1, p=[0.16, 0.28, 0.28, 0.28])[0], 'af', ['warfarin', 'rivaroxaban', 'apixaban', 'edoxaban'])  #https://bmchealthservres.biomedcentral.com/articles/10.1186/s12913-020-5058-1
        # https://jamanetwork.com/journals/jamainternalmedicine/fullarticle/1171906
        else: 
            self.store('aspirin', 'af (anticoagulants contraindicated)', ['aspirin'])
        if self.rng.binomial(1, 0.75) == 1: # Rate-control dominant 
            self.store(self.rng.choice(['bisoprol', 'digoxin', 'verapamil', 'diltiazem'], 1, p=[0.444, 0.318, 0.119, 0.119])[0], 'af', ['bisoprol', 'atenolol', 'propanolol', 'digoxin', 'verapamil', 'diltiazem'])
        else:
            self.store(self.rng.choice(['amiodarone', 'sotalol'], 1, p=[0.68, 0.32])[0], 'af', ['amiodarone', 'sotalol'])

    def pvd(self):
        self.store('aspirin', 'pvd', ['aspirin'])
        if (self.patient['age'] > 85):
            self.store('atorvastatin', 'pvd', ['atorvastatin'])

    def arthritis(self):
        if self.rng.binomial(1, 0.057) == 1:
            self.store('paracetamol', 'arthritis', ['paracetamol']) # 5.7% using paracetamol in UK https://academic.oup.com/rheumatology/article/53/5/937/1798271
        if self.rng.binomial(1, 0.576) == 1: 
            self.store(self.rng.choice(['naproxen', 'ibuprofen'], 1, p=[0.5, 0.5])[0], 'arthritis', ['naproxen', 'ibuprofen'], 50) # 57.6% using NSAID in UK https://academic.oup.com/rheumatology/article/53/5/937/1798271
        elif self.rng.binomial(1, 0.576) == 1:
            self.store('celecoxib', 'arthritis', ['naproxen', 'ibuprofen','celecoxib'], 50)
        if self.rng.binomial(1, 0.394) == 1: # 39.4% using opioid in UK https://academic.oup.com/rheumatology/article/53/5/937/1798271
            self.store(self.rng.choice(['codeine', 'tramadol', 'morphine'], 1, p=[0.264, 0.564, 0.172])[0], 'arthritis', ['codeine', 'tramadol', 'morphine', 'fentanyl', 'buprenorphine', 'oxycodone'])
            laxative = self.rng.choice(['lactulose', 'senna', 'ispaghula husk', 'docusate sodium'], 1, p=[0.396, 0.418, 0.119,0.067])[0]
            self.store(laxative, 'opioid', ['lactulose', 'senna', 'ispaghula husk', 'docusate sodium'])
        if self.check_medications(['naproxen', 'ibuprofen']) == True: # Only 43% co-prescribed a PPI with NSAID https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0129515
            if self.rng.binomial(1, 0.43) == 1:
                self.store(self.rng.choice(['omeprazole', 'lansoprazole'], 1, p=[0.6, 0.4])[0], 'nsaid', ['omeprazole', 'lansoprazole'])
    
    def luts(self):
        # https://pubmed.ncbi.nlm.nih.gov/25333647/
        if self.patient['gender'] == 'm':
            if self.rng.binomial(1, 0.90) == 1: # Number treated 
                choice = self.rng.choice(['alpha', 'antimusc', 'combined'], 1, p=[0.69, 0.19, 0.12])[0] # Normalised by factor = 1 / sum(x,y,z) -> factor * x..z
                if choice == 'alpha':
                    self.store(self.rng.choice(['tamsulosin', 'alfuzocin', 'doxazocin', 'indoramin', 'terazocin', 'prazocin'], 1, p=[0.769, 0.112, 0.087, 0.015, 0.011, 0.006])[0], 'luts', ['tamsulosin', 'alfuzocin', 'doxazocin', 'indoramin', 'terazocin', 'prazocin'])
                elif choice == 'antimusc':
                    self.store(self.rng.choice(['tolterodine', 'oxybutynin', 'solifenacin'], 1, p=[0.34, 0.33, 0.33])[0], 'luts', ['tolterodine', 'oxybutynin', 'solifenacin'])
                else:
                    self.store(self.rng.choice(['tamsulosin', 'alfuzocin', 'doxazocin', 'indoramin', 'terazocin', 'prazocin'], 1, p=[0.769, 0.112, 0.087, 0.015, 0.011, 0.006])[0], 'luts', ['tamsulosin', 'alfuzocin', 'doxazocin', 'indoramin', 'terazocin', 'prazocin'])
                    self.store(self.rng.choice(['tolterodine', 'oxybutynin', 'solifenacin'], 1, p=[0.34, 0.33, 0.33])[0], 'luts', ['tolterodine', 'oxybutynin', 'solifenacin'])
        # https://pubmed.ncbi.nlm.nih.gov/28196724/
        else:
            if self.rng.binomial(1, 0.70) == 1: # Number treated
                agents = ['mirabegron', 'tolterodine', 'darifenacin', 'fesoterodine', 'falvoxate', 'oxybutynin', 'propiverine', 'solifenacin', 'tolterodine', 'trospium']
                self.store(self.rng.choice(agents, 1, p=[0.099,0.083,0.093,0.096,0.069,0.181,0.1,0.093,0.093,0.093])[0], 'luts', agents)

    def depression(self):
        if self.rng.binomial(1, 0.87) == 1: # https://bjgp.org/content/bjgp/69/680/e171.full.pdf
            type = self.rng.choice(['ssri', 'other', 'tca', 'maoi'], 1, p=[0.538, 0.218, 0.243, 0.001])[0] # https://www.psychiatrist.com/pcc/depression/antidepressant-prescribing-in-england/
            if type == 'ssri':
                self.store(self.rng.choice(['sertraline', 'citalopram', 'fluoxetine', 'paroxetine', 'escitalopram'], 1, p=[0.36, 0.39, 0.18, 0.04, 0.03])[0], 'depression', ['sertraline', 'citalopram', 'fluoxetine', 'paroxetine', 'escitalopram'])
            elif type == 'other':
                self.store(self.rng.choice(['mirtazipine', 'venlafaxine', 'duloxetine', 'flupentixol'], 1, p=[0.56, 0.28, 0.14, 0.02])[0], 'depression', ['mirtazipine', 'venlafaxine', 'duloxetine', 'flupentixol'])
            elif type == 'tca':
                self.store(self.rng.choice(['amitriptyline', 'trazadone', 'dosulepin', 'lofepramine', 'nortriptyline', 'clomipramine', 'imipramine'], 1, p=[0.80, 0.07, 0.05, 0.01, 0.04, 0.02, 0.01])[0], 'depression', ['amitriptyline', 'trazadone', 'dosulepin', 'lofepramine', 'nortriptyline', 'clomipramine', 'imipramine'])
            else:
                self.store(self.rng.choice(['moclobemide', 'tranylcypromide', 'phenelzine', 'isocarboxazid'], 1, p=[0.44, 0.16, 0.36, 0.04])[0], 'depression', ['moclobemide', 'tranylcypromide', 'phenelzine', 'isocarboxazid'])

    def asthma(self):
        # https://bnf.nice.org.uk/treatment-summary/asthma-chronic.html
        # https://www.nature.com/articles/s41533-019-0137-7#Sec11
        step = self.rng.choice([0,1,2,3,4,5], 1, p=[0.06, 0.35, 0.28, 0.14, 0.16, 0.01])[0]
        if step == 1:
            self.store('salbutamol', 'asthma', ['salbutamol'])
        elif step == 2:
            self.store('salbutamol', 'asthma', ['salbutamol'])
            self.store('beclometasone dipropionate', 'asthma', ['beclometasone dipropionate'])
        elif step == 3 or step == 4:
            agent = self.rng.choice(['beclometasone with formeterol', 'montelukast'], 1, p=[0.5, 0.5])[0]
            if agent == 'montelukast':
                self.store('salbutamol', 'asthma', ['salbutamol'])
                self.store('beclometasone dipropionate', 'asthma', ['beclometasone dipropionate'])
                self.store('montelukast', 'asthma', ['montelukast'])
            else:
                self.store(agent, 'asthma', ['beclometasone with formeterol'])
        elif step == 5:
            self.store('prednisolone', 'asthma', ['prednisolone', 'hydrocortisone', 'dexamethasone'])
            agent = self.rng.choice(['beclometasone with formeterol', 'montelukast'], 1, p=[0.5, 0.5])[0]
            if agent == 'montelukast':
                self.store('salbutamol', 'asthma', ['salbutamol'])
                self.store('beclometasone dipropionate', 'asthma', ['beclometasone dipropionate'])
                self.store('montelukast', 'asthma', ['montelukast'])
            else:
                self.store(agent, 'asthma', ['beclometasone with formeterol'])

    def pepticUlcer(self):
        if self.rng.binomial(1, 0.05) == 1: # Peptic ulcer disease treated with PPI https://gut.bmj.com/content/67/1/28
            self.store(self.rng.choice(['omeprazole', 'lansoprazole'], 1, p=[0.6, 0.4])[0], 'peptic ulcer', ['omeprazole', 'lansoprazole'])

    def antipsychotics(self):
        # https://bmjopen.bmj.com/content/4/12/e006135
        self.store(self.rng.choice(['quetiapine', 'olanzipine', 'risperidone', 'haloperidol', 'chlorpromazine', 'trifluoperazine'], 1, p=[0.29, 0.25, 0.21, 0.10, 0.09, 0.06])[0], 'antipsychotics', ['olanzapine','quetiapine','risperidone','chlorpromazine','aripiprazole', 'trifluoperazine', 'haloperidol'])

    def ed(self):
        # https://pubmed.ncbi.nlm.nih.gov/33293408/
        if self.rng.binomial(1, 0.16) == 1:
            self.store(self.rng.choice(['sildenafil', 'tadalafil'], 1, p=[0.8, 0.2])[0], 'ed', ['sildenafil', 'tadalafil'])
    
    def thyroidDisease(self):
        # https://pubmed.ncbi.nlm.nih.gov/11078988/
        if self.patient['gender'] == 'm':
            if self.rng.binomial(1, 0.61) == 1:
                 self.store('levothyroxine', 'hypothyroidism', ['levothyroxine'])
        else:
            if self.rng.binomial(1, 0.50) == 1:
                self.store('levothyroxine', 'hypothyroidism', ['levothyroxine'])

    def dementia(self):
        # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3178479/
        if self.rng.binomial(1, 0.256) == 1:
            self.store(self.rng.choice(['donepizil', 'rivastigmine', 'galantamine', 'memantine'], 1, p=[0.38, 0.1, 0.12, 0.40])[0], 'dementia', ['donepizil', 'rivastigmine', 'galantamine', 'memantine'])

    def t1dm(self):
        # https://cks.nice.org.uk/topics/insulin-therapy-in-type-1-diabetes/management/insulin-therapy-type-1-diabetes/
        self.store('Levemir®', 't1dm', ['Levemir®', 'Humalog®'])
        self.store('Humalog®', 't1dm', ['Levemir®', 'Humalog®'])

    def t2dm(self):
        # https://bmjopen.bmj.com/content/8/7/e022768#DC1
        if self.rng.binomial(1, 0.687) == 1: #31.3% diet-controlled
            if self.eGFR() > 30:
                self.store(self.rng.choice(['metformin', 'gliclazide', 'Humulin I®'], 1, p=[0.94, 0.05, 0.01])[0], 't2dm', ['metformin', 'gliclazide', 'Humulin I®'])
            else:
                self.store(self.rng.choice(['metformin', 'gliclazide', 'linagliptin'], 1, p=[0.1, 0.50, 0.40])[0], 't2dm', ['metformin', 'gliclazide', 'linagliptin'])
            if self.rng.binomial(1, 0.20) == 1: # Intensification approx 20%
                second_agent = self.rng.choice(['linagliptin', 'gliclazide', 'dapagliflozin', 'pioglitazone', 'Humulin I®', 'exenatide'], 1, p=[0.43, 0.3, 0.22, 0.02, 0.01, 0.02])[0]
                while ((second_agent == 'exenatide' and self.eGFR() < 30) or (second_agent == 'dapagliflozin' and self.eGFR() < 30) or self.check_medications([second_agent])):
                    second_agent = self.rng.choice(['linagliptin', 'gliclazide', 'dapagliflozin', 'pioglitazone', 'Humulin I®', 'exenatide'], 1, p=[0.43, 0.3, 0.22, 0.02, 0.01, 0.02])[0]
                self.store(second_agent, 't2dm', ['linagliptin', 'gliclazide', 'dapagliflozin', 'pioglitazone', 'Humulin I®', 'exenatide'])

    def angina(self):
        # https://cks.nice.org.uk/topics/angina/management/
        self.store('glyceryl trinitrate', 'angina', ['glyceryl trinitrate'])
        self.store('aspirin', 'angina', ['aspirin', 'clopidogrel']) # All should be on aspirin unless already on it or clopidogrel
        if self.check_contraindication(['heartFailure']) == False:
            self.store('diltiazem', 'angina', ['diltiazem']) 
        elif self.check_contraindication(['asthma', 'copd']) == False:
            self.store('bisoprolol', 'angina', ['bisoprolol', 'propanolol', 'carvidelol', 'atenolol'])
        else:
            self.store(self.rng.choice(['isosorbide mononitrate', 'nicorandil'], 1, p=[0.8, 0.20])[0], 'angina', ['isosorbide mononitrate', 'nicorandil'])
            self.store(self.rng.choice(['ramipril', 'lisinopril'],1, p=[0.8,0.2])[0], 'angina', ['ramipril', 'lisinopril', 'enalipril'])

    def mi(self):
        # https://cks.nice.org.uk/topics/mi-secondary-prevention/prescribing-information/
        self.store(self.rng.choice(['ramipril', 'lisinopril'], 1, p=[0.8,0.2])[0], 'mi', ['ramipril', 'lisinopril', 'enalipril']) # Lifelong ACEi
        if self.check_contraindication(['asthma', 'copd']) == False:
            self.store('bisoprolol', 'mi', ['bisoprolol', 'propanolol', 'carvidelol', 'atenolol']) # Bisoprolol
        if self.patient['age'] < 85:
            self.store('atorvastatin', 'mi', ['atorvastatin']) # Lifelong statin
        self.store('aspirin', 'mi', ['aspirin']) # Lifelong aspirin
        if self.rng.binomial(1, 0.029) == 1: # 2.9% presenting to surgery with recent MI https://pubmed.ncbi.nlm.nih.gov/21372685/
            self.store('clopidogrel', 'mi', ['clopidogrel']) # Clopidogrel in recent MI < 12 months

    def stroke(self):
        # https://cks.nice.org.uk/topics/stroke-tia/management/secondary-prevention-following-stroke-tia/
        if self.rng.binomial(1, 0.80) == 1: # 80% ischaemic https://pubmed.ncbi.nlm.nih.gov/30598741/
            self.store('clopidogrel', 'stroke', ['clopidogrel', 'warfarin', 'rivaroxaban', 'apixaban', 'edoxaban']) # Clopidogrel for ischaemic stroke if not anticoagulated
            if self.patient['age'] < 85:
                self.store('atorvastatin', 'stroke', ['atorvastatin']) # Lifelong statin

    def tia(self):
        # https://cks.nice.org.uk/topics/stroke-tia/management/secondary-prevention-following-stroke-tia/
        self.store('clopidogrel', 'tia', ['clopidogrel', 'warfarin', 'rivaroxaban', 'apixaban', 'edoxaban']) # Clopidogrel for ischaemic stroke if not anticoagulated
        if self.patient['age'] < 85:
            self.store('atorvastatin', 'tia', ['atorvastatin']) # Lifelong statin

    def anaemia(self):
         # 45% chronic disease - https://pubmed.ncbi.nlm.nih.gov/1612458/
         # 30% iron deficienct
         # 10% B12/folate deficiency
         # 15% uncertain
        cause = self.rng.choice(['acd', 'ida', 'b12', 'folate', 'uncertain'], 1, p=[0.45, 0.3, 0.05, 0.05, 0.15])[0]
        if cause == 'ida':
            self.store('ferrous sulfate', 'iron deficiency anaemia', ['ferrous sulphate'])
        elif cause == 'b12':
            self.store('hydroxocobalamin', 'B12 deficiency', ['hydroxocobalamin'])
        elif cause == 'folate':
            self.store('folic acid', 'folate deficiency', ['folic acid'])

    def migraine(self):
        # https://bmjopen.bmj.com/content/10/11/e038972
        if self.rng.binomial(1, 0.53) == 1:
            self.store(self.rng.choice(['sumatriptan', 'pizotifen'], 1, p=[0.8, 0.2])[0], 'migraine', ['sumatriptan', 'pizotifen'])
        if self.rng.binomial(1, 0.314) == 1:
            self.store('ibuprofen', 'migraine', ['ibuprofen', 'naproxen', 'celecoxib', 'aspirin'], 50)
        if self.rng.binomial(1, 0.107) == 1: # Prophylactic
            agent = self.rng.choice(['pizotifen', 'amitriptyline', 'propanolol', 'valproic acid', 'topiramate'], 1, p=[0.2, 0.23, 0.08, 0.32, 0.17])[0]
            if agent != 'propanolol':
                self.store(agent, 'migraine', ['pizotifen', 'amitriptyline', 'valproic acid', 'topiramate'])
            else:
                if self.check_contraindication(['copd', 'asthma']) == False:
                    self.store(agent, 'migraine', ['bisoprolol'])

    def bad(self):
        # https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0028725
        if self.rng.binomial(1, 0.785) == 1:
            regimen_no = self.rng.choice([1,2,3,4,5,6,7], 1, p=[0.16,0.04,0.17,0.13,0.09,0.22,0.19])[0]
            antipsychotics = ['olanzapine','quetiapine','risperidone','chlorpromazine','aripiprazole']
            anticonvulsants = ['sodium valproate','carbamazepine','lamotrigine']
            if regimen_no == 1: # Lithium monotherapy
                self.store('lithium', 'bipolar affective disorder', ['lithium'])
            elif regimen_no == 2: # Lithium + anticonvulsant 
                self.store('lithium', 'bipolar affective disorder', ['lithium'])
                self.store(self.rng.choice(anticonvulsants, 1, p=[0.65, 0.15, 0.2])[0], 'bipolar affective disorder', anticonvulsants)
            elif regimen_no == 3: # Anticonvulsant
                self.store(self.rng.choice(anticonvulsants, 1, p=[0.65, 0.15, 0.2])[0], 'bipolar affective disorder', anticonvulsants)
            elif regimen_no == 4: # Lithium + antipsychotic
                self.store('lithium', 'bipolar affective disorder', ['lithium'])
                self.store(self.rng.choice(antipsychotics, 1, p=[0.49, 0.22, 0.17, 0.06, 0.06])[0], 'bipolar affective disorder', antipsychotics)
            elif regimen_no == 5: # Lithium, anticonvulsant and antipsychotic
                self.store('lithium', 'bipolar affective disorder', ['lithium'])
                self.store(self.rng.choice(antipsychotics, 1, p=[0.49, 0.22, 0.17, 0.06, 0.06])[0], 'bipolar affective disorder', antipsychotics)
                self.store(self.rng.choice(anticonvulsants, 1, p=[0.65, 0.15, 0.2])[0], 'bipolar affective disorder', antipsychotics)
            elif regimen_no == 6: # Antipsychotic and anticonvulsant
                self.store(self.rng.choice(antipsychotics, 1, p=[0.49, 0.22, 0.17, 0.06, 0.06])[0], 'bipolar affective disorder', antipsychotics) 
                self.store(self.rng.choice(anticonvulsants, 1, p=[0.65, 0.15, 0.2])[0], 'bipolar affective disorder', antipsychotics)
            else: # Antipsychotic monotherapy
                self.store(self.rng.choice(antipsychotics, 1, p=[0.49, 0.22, 0.17, 0.06, 0.06])[0], 'bipolar affective disorder', antipsychotics) 

    def parkinsonsDisease(self):
        # https://pubmed.ncbi.nlm.nih.gov/31756215/
        if self.rng.binomial(1, 0.786) == 1:
            agents = ['co-careldopa', 'pramipexole', 'levodopa and carbidopa and etacapone', 'ropinirole', 'pergolide', 'procyclidine', 'bromocriptine']
            if self.rng.binomial(1, 0.852) == 1: # Monotherapy
                self.store(self.rng.choice(agents, 1, p=[0.3,0.21,0.18,0.15,0.07,0.05,0.04])[0], 'parkinsons disease', agents)
            else:
                self.store(self.rng.choice(agents, 1, p=[0.3,0.21,0.18,0.15,0.07,0.05,0.04])[0], 'parkinsons disease', agents)
                self.store('amantadine', 'parkinsons disease', agents)

    def sle(self):
        # https://www.tandfonline.com/doi/full/10.1080/13696998.2020.1740236
        # https://academic.oup.com/rheumatology/article/57/1/e1/4318863#105890771
        if self.rng.binomial(1, 0.91) == 1:
            choice = self.rng.choice(['nsaid', 'steroid', 'immunosupressant', 'hydroxychloroquine'], 1, p=[0.33, 0.33, 0.17, 0.17])[0]
            if choice == 'nsaid':
                self.store('naproxen', 'sle', ['ibuprofen', 'naproxen', 'celecoxib', 'aspirin'], 50)
            if choice == 'steroid':
                self.store('prednisolone', 'sle', ['prednisolone', 'hydrocortisone', 'dexamethasone'])
            if choice == 'immunosupressant':
                self.store('methotrexate', 'sle', ['methorexate'])
                self.store('folic acid', 'methotrexate', ['folic acid'])
            if choice == 'hydroxychloroquine':
                self.store('hydroxychloroquine', 'sle', ['hydroxychloroquine'])

    def ra(self):
        # https://arthritis-research.biomedcentral.com/articles/10.1186/s13075-015-0895-8
        if self.rng.binomial(1, 0.3) == 1:
            self.store('prednisolone', 'sle', ['prednisolone', 'hydrocortisone', 'dexamethasone'])
        if self.rng.binomial(1, 0.20) == 1:
            self.store('naproxen', 'sle', ['ibuprofen', 'naproxen', 'celecoxib', 'aspirin'], 50)
        if self.rng.binomial(1, 0.50) == 1:
            self.store('methotrexate', 'sle', ['methotrexate'])
            self.store('folic acid', 'methotrexate', ['folic acid'])

    def copd(self):
        # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4154894/
        # https://bnf.nice.org.uk/treatment-summary/chronic-obstructive-pulmonary-disease.html
        # https://walsallccg.nhs.uk/wp/wp-content/uploads/Walsall-COPD-Chart-Format-V4.pdf
        # https://cks.nice.org.uk/topics/chronic-obstructive-pulmonary-disease/prescribing-information/muscarinic-antagonists/
        if self.rng.binomial(1, 0.83) == 1: # Recieving treatment
            regimen = self.rng.choice(['saba', 'saba-sama', 'sama', 'laba', 'lama', 'laba-lama', 'ics', 'ics-lama', 'ics-laba', 'ics-laba-lama', 'ics-laba-lama-ltra', 'ics-laba-ltra'], 1, p=[0.11353712, 0.01528384, 0.00764192, 0.01965066, 0.08624454,0.00873362, 0.06441048, 0.01855895, 0.29148472, 0.25327511,0.10917031, 0.01200873])
            if regimen == 'saba':
                self.store('salbutamol', 'copd', ['salbutamol'])
            elif regimen == 'saba-sama':
                self.store('ipratropium', 'copd', ['ipratropium']) if self.store('ipratropium with salbutamol', 'copd', ['salbutamol']) == None else None
            elif regimen == 'sama':
                self.store('ipratropium', 'copd', ['ipratropium'])
            elif regimen == 'laba':
                self.store('Serevent', 'copd', ['Serevent'])
            elif regimen == 'lama':
                self.store('Spiriva Respimat', 'copd', ['Spiriva Respimat'])
            elif regimen == 'laba-lama':
                self.store('Spiolto Respimat', 'copd', ['Spiolto Respimat'])
            elif regimen == 'ics':
                self.store('beclometasone dipropionate', 'copd', ['beclometasone dipropionate'])
            elif regimen == 'ics-lama':
                self.store('Fostair MDI', 'copd', ['Fostair MDI'])
            elif regimen == 'ics-laba':
                self.store('tiotropium', 'copd', ['tiotropium'])
                self.store('beclometasone dipropionate', 'copd', ['beclometasone dipropionate'])
            elif regimen == 'ics-laba-lama':
                self.store('Trimbow MDI', 'copd', ['Trimbow MDI'])
            elif regimen == 'ics-laba-lama-ltra':
                self.store('Trimbow MDI', 'copd', ['Trimbow MDI'])
                self.store('montelukast', 'copd', ['montelukast'])
            elif regimen == 'ics-laba-ltra':
                self.store('Trimbow MDI', 'copd', ['Trimbow MDI'])
                self.store('montelukast', 'copd', ['montelukast'])
            elif regimen == 'ics-laba':
                self.store('tiotropium', 'copd', ['tiotropium'])
                self.store('beclometasone dipropionate', 'copd')
                self.store('montelukast', 'copd', ['montelukast'])

    def osteoporosis(self):
        # https://cks.nice.org.uk/topics/osteoporosis-prevention-of-fragility-fractures/management/management/
        self.store('alendronic acid', 'osteoporosis', ['alendronic acid'])
        self.store('vitamin D with calcium', 'osteoporosis', ['vitamin D with calcium'])

    def chronicPain(self):
        # https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1003270#pmed.1003270.s001
        # https://academic.oup.com/painmedicine/article/18/10/1932/2670206
        def get_p():
            age = self.patient['age']
            age_map = {
                0: [0.256, 0.252, 0.247, 0.245], 
                1: [0.193, 0.176, 0.434, 0.197], 
                2: [0.083, 0.068, 0.64, 0.209]
            }
            age_group = 0
            if age >= 75 and age < 85:
                age_group = 1
            elif age >= 85:
                age_group = 2
            return age_map[age_group]
            
        opioid = self.rng.choice(['weak', 'moderate', 'strong', 'combo'], 1, p=get_p())[0]
        opiates = ['codeine', 'dihydrocodeine', 'tramadol', 'morphine', 'oxycodone', 'fentanyk', 'buprenorphine']
        laxatives = ['lactulose', 'senna', 'ispaghula husk', 'docusate sodium']
        
        self.store('paracetamol', 'chronic pain', ['paracetamol'])

        if opioid == 'weak': 
            agent = self.rng.choice(['codeine', 'dihydrocodeine'], 1, p=[0.5, 0.5])[0]
            self.store(agent, 'chronic pain', opiates)
            self.store(self.rng.choice(laxatives, 1, p=[0.396, 0.418, 0.119,0.067])[0], 'opioid', laxatives)
        elif opioid == 'moderate': 
            self.store('tramadol', 'chronic pain', opiates)
            self.store(self.rng.choice(laxatives, 1, p=[0.396, 0.418, 0.119,0.067])[0], 'opioid', laxatives)
        elif opioid == 'moderate': 
            agent = self.rng.choice(['morphine', 'buprenorphine', 'oxycodone', 'fentanyl'], 1, p=[0.465, 0.233, 0.209, 0.093])[0]
            self.store(agent, 'chronic pain', opiates)
            self.store(self.rng.choice(laxatives, 1, p=[0.396, 0.418, 0.119,0.067])[0], 'opioid', laxatives)
        else:
            # https://bmjopen.bmj.com/content/8/6/e019491
            combo = self.rng.choice([0,1,2,3], 1, p=[0.61, 0.14, 0.14, 0.11])[0]
            # 'codeine_tramadol', 'codeine_morphine', 'codeine_buprenorphine', 'morphine_tramadol'
            if combo == 0:
                self.store('codeine', 'chronic pain', opiates)
                self.store('tramadol', 'chronic pain', opiates)
                self.store(self.rng.choice(laxatives, 1, p=[0.396, 0.418, 0.119,0.067])[0], 'opioid', laxatives)
            elif combo == 1:
                self.store('codeine', 'chronic pain', opiates)
                self.store('morphine', 'chronic pain', opiates)
                self.store(self.rng.choice(laxatives, 1, p=[0.396, 0.418, 0.119,0.067])[0], 'opioid', laxatives)
            elif combo == 3:
                self.store('codeine','chronic pain', opiates)
                self.store('buprenorphine','chronic pain', opiates)
                self.store(self.rng.choice(laxatives, 1, p=[0.396, 0.418, 0.119,0.067])[0], 'opioid', laxatives)
            else:
                self.store('morphine','chronic pain', opiates)
                self.store('tramadol','chronic pain', opiates)
                self.store(self.rng.choice(laxatives, 1, p=[0.396, 0.418, 0.119,0.067])[0], 'opioid', laxatives)

    def heartFailure(self):
        # https://bnf.nice.org.uk/treatment-summary/chronic-heart-failure.html
        if self.rng.binomial(1, 0.576) == 1:
            self.store(self.rng.choice(['ramipril', 'enalipril'], 1, p=[0.5, 0.5])[0], 'heart failure', ['ramipril', 'enalipril', 'lisinopril'])
        if self.rng.binomial(1, 0.541) == 1:
            self.store(self.rng.choice(['bisoprolol', 'carvedilol'], 1, p=[0.6, 0.4])[0], 'heart failure', ['bisoprolol', 'carvedilol'])
        if self.rng.binomial(1, 0.182) == 1:
            self.store(self.rng.choice(['furosemide', 'bumetanide'], 1, p=[0.8, 0.2])[0], 'heart failure', ['furosemide', 'bumetanide'])
        if self.rng.binomial(1, 0.57) == 1:
            self.store(self.rng.choice(['spironolactone', 'eplerenone'], 1, p=[0.5, 0.5])[0], 'heart failure', ['spironolactone', 'eplerenone'])

    def prescribe(self):
        self.db.setup_prescription_database()
        prescribable = ['corticosteroids', 'antihypertensives', 'antipsychotics', 'af', 'arthritis', 'asthma', 'ed', 'luts', 'migraine', 'osteoporosis', 'pepticUlcer', 'thyroidDisease', 'heartFailure', 'bad', 'dementia', 't1dm', 't2dm', 'parkinsonsDisease', 'ra', 'sle', 'depression', 'mi', 'angina', 'pvd', 'stroke', 'tia', 'anaemia', 'copd', 'chronicPain', 'orthostaticHypotension']
        for v,b in self.patient.items():
            if b == 1:
                for s in prescribable:
                    if s == v:
                        method = getattr(self, s, lambda: 'Invalid prescribing action')
                        method()
        
        self.db.close_connection()
        return len(self.meds)

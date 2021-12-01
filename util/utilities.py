import networkx as nx
import pylab as plt
import numpy as np
import pandas as pd
import math, csv, itertools
import scipy.stats as stats

class Utilities:
    def __init__(self, config, rng):
        self.rng: np.random = rng
        self.config = config

    # Sets the demographic labels
    def setDemographicLabels(self, alternate=False):
        if alternate != True:
            return ['65_69_M', '70_74_M', '75_79_M', '80_84_M', '85_89_M', '90_94_M', '95_99_M', '100_112_M', '65_69_F', '70_74_F', '75_79_F', '80_84_F', '85_89_F', '90_94_F', '95_99_F', '100_112_F']
        else:
            return ['65_69_M', '65_69_F', '70_74_M', '70_74_F', '75_79_M', '75_79_F', '80_84_M', '80_84_F', '85_89_M', '85_89_F', '90_94_M', '90_94_F', '95_99_M', '95_99_F', '100_112_M', '100_112_F']

    # Sets the probabilities for each demographic age band
    def setDemographicProbabilities(self):
        return [[0.14], [0.12], [0.09], [0.07], [0.0175], [0.0175], [0.0175],[0.0175], [0.15], [0.12], [0.10], [0.07], [0.0175], [0.0175], [0.0175],[0.0175]]

    # Gets the demographic code given age and gender
    def getDemographics(self, age, gender):
        if age >=65 and age < 70:
            return f"65_69_{gender.upper()}"
        elif age >=70 and age < 75:
            return f"70_74_{gender.upper()}"
        elif age >=75 and age < 80:
            return f"75_79_{gender.upper()}"
        elif age >=80 and age < 85:
            return f"80_84_{gender.upper()}"
        elif age >=85 and age < 90:
            return f"85_89_{gender.upper()}"
        elif age >=90 and age < 95:
            return f"90_94_{gender.upper()}"
        elif age >=95 and age < 100:
            return f"95_99_{gender.upper()}"
        elif age >=100 and age < 112:
            return f"100_112_{gender.upper()}"

    # Converts a reference interval to a standard deviation
    def ri2sd(self, m, ul):
        sd = (ul - m) / 1.645 #Z Value for 95th percentile
        return sd

    # Create a normal distribution given a sample size, chance of being male and matrix of mu, sigma for each demographic age band and gender
    def createNormalDistribution(self, n, chanceOfBeingMale, stats_m, stats_f):
        dist_m = []
        dist_f = []
        dist = None
        for stat in stats_m:
            if type(stat[1]) is not float:
                sd = self.ri2sd(stat[1][0], stat[1][1])
                dist = self.rng.normal(stat[0], sd, round(n*chanceOfBeingMale * 100))
            else: 
                dist = self.rng.normal(stat[0], stat[1], round(n*chanceOfBeingMale * 100))
            dist_m.append(dist)
        for stat in stats_f:
            if type(stat[1]) is not float:
                sd = self.ri2sd(stat[1][0], stat[1][1])
                dist = self.rng.normal(stat[0], sd, round(n*chanceOfBeingMale * 100))
            else: 
                dist = self.rng.normal(stat[0], stat[1], round(n*(1-chanceOfBeingMale) * 100))
            dist_f.append(dist)

        return dist_m, dist_f

    # Create Beta distribution
    def createBetaDistribution(self, n, chanceOfBeingMale, stats_m, stats_f):
        dist_m = []
        dist_f = []
        a,b = 0,0
        for stat in stats_m:
            #https://stats.stackexchange.com/questions/12232/calculating-the-parameters-of-a-beta-distribution-using-the-mean-and-variance
            a = (((1 - stat[0]) / stat[1]**2) - (1 / stat[0])) * stat[0]**2
            b = a * ((1 / stat[0]) - 1)
            dist_m.append(self.rng.beta(a, b, round(n*chanceOfBeingMale * 100)))
        for stat in stats_f:
            a = (((1 - stat[0]) / stat[1]**2) - (1 / stat[0])) * stat[0]**2
            b = a * ((1 / stat[0]) - 1)
            dist_f.append(self.rng.beta(a, b, round(n*(1-chanceOfBeingMale)* 100)))

        return dist_m, dist_f

    # Create multinomial distribution
    def createMultinomialDistribution(self, n, chanceOfBeingMale, stats_m, stats_f):
        return self.rng.multinomial(n=1, pvals=stats_m, size=round(n*chanceOfBeingMale * 100)), self.rng.multinomial(n=1, pvals=stats_f, size=round(n*(1-chanceOfBeingMale) * 100))

    # Create Bernouli distribution
    def createBernoulliDistribution(self, n, chanceOfBeingMale, stat_m, stat_f):
        dist_m = stats.bernoulli.rvs(stat_m/100, size=round(n*chanceOfBeingMale * 100))
        dist_f = stats.bernoulli.rvs(stat_f/100, size=round(n*(1-chanceOfBeingMale) * 100))
        """
        mean, var, s,k = stats.bernoulli.stats(stat_m/100, moments='mvsk')
        print(node, 'male', mean, var)
        mean, var, s,k = stats.bernoulli.stats(stat_f/100, moments='mvsk')
        print(node, 'female', mean, var)
        """

        return dist_m, dist_f

    def getBernoulliSample(self, stat):

        return stats.bernoulli.rvs(1 if stat > 1 else stat, size=1)[0]

    def createTruncatedNormalDistribution(self, n, chanceOfBeingMale, stats_m, stats_f, clip_a, clip_b):
        dist_m = []
        dist_f = []
        for stat in stats_m:
            dist = stats.truncnorm((clip_a - stat[0]) / stat[1], (clip_b - stat[0]) / stat[1], loc=stat[0], scale=stat[1])
            dist_m.append(dist.rvs(round(n*chanceOfBeingMale * 100)))
        for stat in stats_f:
            dist = stats.truncnorm((clip_a - stat[0]) / stat[1], (clip_b - stat[0]) / stat[1], loc=stat[0], scale=stat[1])
            dist_f.append(dist.rvs(round(n * (1- chanceOfBeingMale) * 100)))

        return dist_m, dist_f

    # Return the tumour site-specific MDT
    def getMDT(self, cancer):
        # Other and specific sites not handled ideally but useful approximation
        if cancer == 'other':
            return self.rng.choice(['haematological', 'upper_gi', 'neurosurgical', 'bone', 'sarcoma', 'thyroid', 'opthalmological'])
        sites = {'ovary': 'gynaecological', 'breast': 'breast', 'prostate': 'urological', 'lung': 'lung', 'bowel': 'lower_gi', 'uterus': 'gynaecological', 'h&n': 'head_and_neck', 'renal': 'urological', 'bladder': 'urological', 'nhl': 'haematological', 'pancreas': 'hepatopancreaticobiliary', 'cup': 'cup'}
        return sites[cancer]

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
        for p in pos:  # raise text positions
            pos[p][1] += 0.1
        nx.draw_networkx_labels(model, pos)
        plt.savefig(f'results/graphs/{filename}.png')

    def calculateCPDTable(self, bg_risk, variables, approach="WEIGHTED"):
        table = []

        def transformRisk(v):
            if v["type"] == "RR":
                return v["r"]
            elif v["type"] == "OR":
                #https://pubmed.ncbi.nlm.nih.gov/9832001/
                rr = v["r"] / ((1 - bg_risk) + (bg_risk * v["r"]))
                return round(rr, 2)
            elif v["type"] == "HR":
                #https://www.sciencedirect.com/science/article/pii/S0277953617303490?via%3Dihub
                rr = (1 - math.pow(math.e, (v["r"] * math.log(1 - bg_risk)))) / bg_risk
                return round(rr, 2)

        def calculateWeights():
            wts = []
            for v in variables:
                wts.append(transformRisk(v))
            weights = np.array(wts)
            # (weights - weights.min()) / (weights.max() - weights.min())
            # return (weights / weights.sum())
            return weights

        for row in itertools.product([0, 1], repeat = len(variables)):
            table.append(row)

        cat1 = []
        cat2 = []

        for row in table:
            if all(v == 0 for v in row):
                cat1.append(bg_risk)
            else:
                if (approach == "MAX_RISK"): #maximum risk approach     
                    risks = []  
                    for i, t in enumerate(row):
                        if t == 1:
                            risk = round(bg_risk * transformRisk(variables[i]), 3)
                        else:
                            risk = 0
                        risks.append(risk)
                    cat1.append(max(risks))
                elif (approach == "WEIGHTED"): #weighted risks approach
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

    def calculateCrCl(self, h, w, age, gender, cr):
        sex = 1 if gender == 'f' else 0
        bsa = 0.007184 * math.pow(h, 0.725) * math.pow(w, 0.425)
        crcl = (((98 - 0.8 * (age - 20)) * (1 - (0.01 * sex)) * (bsa/1.73))) / (cr * 0.0113)
        return crcl

    # Checks for multimorbidity
    def hasMultimorbidity(self, p):
        mm_count = 0
        for v,b in p.items():
            if b == 1:
                for m in self.config['multimorbidity']:
                    if m == v:
                        mm_count += 1

        return 1 if mm_count > 1 else 0

    # Works out risk of temporal disorientation
    def reportsDateIncorrectly(self, baseline, p):
        ad = [0.7272, 0.7419, 0.7949, 0.8]
        pd = [0.16, 0.1571, 0.3333, 0.3333]
        age_band = 0
        if p['age'] >= 70 and p['age'] < 75:
            age_band = 1
        elif p['age'] >= 75 and p['age'] < 80:
            age_band = 2
        elif p['age'] >= 80:
            age_band = 3
        
        risk_profile = []
        
        # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8345456/
        risk_profile.append(self.rng.choice([0.177, 0.035, 0.105, 0.1, 0.041], 1)[0] if p['mci'] == 1 else baseline)
        risk_profile.append(self.rng.choice([0.16, 0.033, 0.08, 0.054, 0.023], 1)[0] if p['depression'] == 1 else baseline)

        # https://www.longdom.org/open-access/temporal-disorientation-base-rates-in-alzheimers-disease-and-parkinsonsdisease-2167-7182-1000221.pdf
        risk_profile.append(pd[age_band] if p['parkinsonsDisease'] == 1 else baseline)
        risk_profile.append(ad[age_band] if p['dementia'] == 1 else baseline)

        risk = max(risk_profile)

        return self.rng.binomial(1, p=risk)

    def calculateSelfReportedHealth(self, baseline, patient):
        self_reported_health = baseline
        self_reported_health = self.rng.integers(3,5) if patient['aerobicallyActive'] == 1 and self_reported_health < 3 and self.rng.random() > 0.7 else self_reported_health
        # https://bmcgeriatr.biomedcentral.com/articles/10.1186/1471-2318-13-85
        while self_reported_health >= 3:
            self_reported_health = self.rng.integers(1,3) if patient['stroke'] == 1 and self.rng.random() < 0.38 else self_reported_health # Stroke
            self_reported_health = self.rng.integers(1,3) if patient['iadlImpairment'] == 1 and self.rng.random() < 0.45 else self_reported_health # IADL
            self_reported_health = self.rng.integers(1,3) if patient['badlImpairment'] == 1 and self.rng.random() < 0.5 else self_reported_health # ADL
            break
        
        return round(self_reported_health)

    # Attempts to classify the ASA Physical Status Classification System
    def calculateASA(self, p):
        asa = 1

        if p['bmi'] > 30 and p['bmi'] < 40:
            asa = 2

        for rf, v in p.items():
            if v == 1:
                if rf == 'currentSmoker':
                    asa = 2
                elif rf == 'drinksAlcohol':
                    asa = 2
                elif rf == 'diabetes':
                    asa = 2
                elif rf == 'lungDisease':
                    asa = 2
                elif rf == 'alcoholAbuse':
                    asa = 3
                elif rf == 'tia':
                    asa = 3
                elif rf == 'stroke':
                    asa = 3
                elif rf == 'complicatedDiabetes':
                    asa = 3
                elif rf == 'alcoholAbuse':
                    asa = 3
                elif rf == 'heartFailure':
                    asa = 3
                elif rf == 'mi':
                    asa = 3
                elif rf == 'angina':
                    asa = 3
                elif rf == 'badlImpairment':
                    asa = 3
                elif rf == 'iadlImpairment':
                    asa = 3
                elif rf == 'ihd':
                    asa = 3
                elif rf == 'needsCare':
                    asa = 3
                elif rf == 'difficultyWalkingOutside':
                    asa = 3
        
        if p['bmi'] >= 40:
            asa = 3

        return asa

    # Calculate the CARG toxicity score
    def calculateCarg(self, age, gender, cancer, height, weight, anaemia, cr, hearing, falls, medAssistance, difficultyWalkingOutside, decreasedSocialActivity):
        score = 2 # Standard dosing always scores 2 initially versus reduced dose 
        sex = 1

        if age >= 72:
            score += 2
        
        higherRiskCancers = ['colon', 'oesophageal', 'stomach', 'rectal', 'prostate', 'bladder', 'ovarian', 'uterine', 'renal']
        for hrc in higherRiskCancers:
            if hrc == cancer:
                score += 2
        
        if anaemia == 1:
            score += 3
        
        if gender == 'f':
            sex = 0
        
        # Body surface area DuBois & DuBois
        bsa = 0.007184 * math.pow(height, 0.725) * math.pow(weight, 0.425)

        # Creatinine clearance - Jeliffe forumula
        crcl = (((98 - 0.8 * (age - 20)) * (1 - (0.1 * sex)) * (bsa/1.73))) / (cr * 0.0113)

        if crcl < 34:
            score += 3
        
        if hearing == 1:
            score += 2
        elif falls == 1:
            score += 3
        elif medAssistance == 1:
            score += 1
        elif difficultyWalkingOutside == 1:
            score += 3
        elif decreasedSocialActivity == 1:
            score += 1
        
        risk = 0
        if score <= 3:
            risk = 25
        elif score >= 4 and score < 6:
            risk = 32
        elif score >= 6 and score < 8:
            risk = 50
        elif score >= 8 and score < 10:
            risk = 54
        elif score >= 10 and score < 12:
            risk = 77
        elif score >= 12 and score < 20:
            risk = 89

        present = 1 if risk/100 >= 0.5 else 0
        
        return risk/100, score, present

    # Calculate Cambridge Mutlimorbidity score
    # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7004217/
    def calculateCambridgeMultimorbidityScore(self, p):

        consultations, admissions, mortality, general = 0,0,0,0

        df = pd.read_csv(
            'data/cambridge_multimorbidity_score.csv', 
            header=0, 
            names=['disease', 'consultations', 'admissions', 'mortality', 'general']
        )
        for v, b in p.items():
            if b == 1:
                if df['disease'].str.contains(v).any():
                    consultations += df[df['disease'].str.contains(v)]['consultations'].values[0]
                    admissions += df[df['disease'].str.contains(v)]['admissions'].values[0]
                    mortality += df[df['disease'].str.contains(v)]['mortality'].values[0]
                    general += df[df['disease'].str.contains(v)]['general'].values[0]

        return consultations, admissions, mortality, general

    # Calculate electronic Frailty Index score
    def calculateEFI(self, p):

        deficits = {"activityLimitation": False, "anaemia": False, "arthritis": False, "af": False, "cvd": False, "ckd": False, "diabetes": False, "dizziness": False, "breathlessness": False, "falls": False, "footProblems": False, "fragilityFracture": False, "hearingLoss": False, "heartFailure": False, "heartValveDisease": False, "homebound": False, "hypertension": False, "hypotension": False, "heartDisease": False, "cognitive": False, "difficultyWalkingOutside": False, "osteoporosis": False, "parkinsonsDisease": False, "pepticUlcer": False, "pvd": False, "polypharmacy": False, "needsCare": False, "lungDisease": False, "ulcers": False, "sleepDisturbance": False, "socialVulnerability": False, "thyroidDisease": False, "urinaryIncontinence": False, "luts": False, "visualImpairment": False, "weightLossAndAnorexia": False }

        for v, b in p.items():
            if b == 1:
                if v == "badlImpairment" or v == "iadlImpairment":
                    deficits['activityLimitation'] = True
                elif v == "mi" or v == "angina" or v == 'heartValveDisease':
                    deficits['heartDisease'] = True
                elif v == "copd" or v == "asthma":
                    deficits['lungDisease'] = True
                elif v == "syncope" or v == "orthostaticHypotension":
                    deficits['hypotension'] = True
                elif v == "t1dm" or v == "t2dm":
                    deficits['diabetes'] = True
                elif v == "mci" or v == "dementia":
                    deficits['cognitive'] = True
                elif v == "weightLoss" or v == "anorexia":
                    deficits['weightLossAndAnorexia'] = True
                elif v == "livesAlone" or v == "socialIsolation":
                    deficits['socialVulnerability'] = True
                elif v == "stroke" or v == "tia" or v == "angina" or v == "mi":
                    deficits['cvd'] = True
                else:
                    for deficit,_ in deficits.items():
                        if deficit == v:
                            deficits[deficit] = True
        
        score = 0

        for _,b in deficits.items():
            if b == True:
                score += 1
        
        efi = round(score / 36, 2)

        classification = 'fit'

        if efi >= 0.13 and efi < 0.25:
            classification = 'mild_frailty'
        elif efi >= 0.25 and efi < 0.36:
            classification = 'moderate_frailty'
        elif efi >= 0.36:
            classification = 'severe_frailty'

        return efi, classification

    # Calculate Gupta major adverse cardiac event risk
    def calculateGupta(self, p):
        age = p['age'] * 0.02
        functional = 0
        if p['iadlImpairment'] == 1 or p['badlImpairment'] == 1:
            functional = 0.65
        if p['needsCare'] == 1:
            functional = 1.03
        
        asa = self.calculateASA(p)
        if asa == 1:
            asa = -5.17
        elif asa == 2:
            asa = -3.29
        elif asa == 3:
            asa = -1.92
        elif asa == 4:
            asa = -0.95
        elif asa == 5:
            asa = 0
        
        creatinine = 0
        if p['cr'] > 133:
            creatinine = 0.61
        
        procedure = 0
        if p['cancer_mdt'] == 'breast':
            procedure = -1.61
        elif p['cancer_mdt'] == 'head_and_neck':
            procedure = 0.71
        elif p['cancer_mdt'] == 'lung':
            procedure = 0.40
        elif p['cancer_mdt'] == 'gynaecological':
            procedure = 0.76
        elif p['cancer_mdt'] == 'urological':
            procedure = -0.26
        elif p['cancer_mdt'] == 'lower_gi':
            procedure = 1.14
        else:
            procedure = 0.4

        x = -5.25 + age + functional + creatinine + procedure + asa

        risk = (math.exp(x) / (1 + math.exp(x)))

        present = 1 if risk >= 0.5 else 0 

        return risk, present

    # Calculate NCEPOD SORT score for 30-day postoperative mortality
    def calculateSort(self, p, type):

        asaThree = 0
        asaFour = 0
        asaFive = 0
        cancer = 1
        urgencyExpedited = 1
        highRiskSpecialty = 0
        age_65_75 = 1
        age_80 = 0
        xMajor = 0

        asa = self.calculateASA(p)

        if asa == 3:
            asaThree = 1
        elif asa == 4:
            asaFour = 1
        elif asa == 5:
            asaFive = 1
        
        if p['cancer_site'] == 'lung' or p['cancer_site'] == 'colon' or p['cancer_site'] == 'rectal':
            highRiskSpecialty = 1

        if p['age'] > 80:
            age_65_75 = 0
            age_80 = 1

        if type == 'major':
            xMajor = 1

        risk_score = (asaThree * 1.411) + (asaFour * 2.388) + (asaFive * 4.081) + (urgencyExpedited * 1.236) + (highRiskSpecialty * 0.712) + (xMajor * 0.381) + (cancer * 0.667) + (age_65_75 * 0.777) + (age_80 * 1.591)

        thirty_day = math.exp((-7.366 + risk_score)) / (1 + math.exp((-7.366 + risk_score)))

        present = 1 if thirty_day >= 0.5 else 0 

        return thirty_day, present

    # Calculate BMI
    def calculateBMI(self, h, w):
        hm = h / 100
        bmi = w / (hm * hm)
        return round(bmi)

    # Calculate Suemoto index 10-year mortality risk
    def calculateSuemoto(self, gender, age, diabetes, heartDisease, lungDisease, cancer, currentSmoker, formerSmoker, alcohol, bmi, physicalActivity, bathing, walkBlock, date, selfReportedHealth):
        
        s10_m = 0.6905
        s10_f = 0.7636

        age1 = False
        age2 = False
        age3 = False
        age4 = False
        age5 = False
        age6 = False 

        if age < 65:
            age1 = True
        elif age >= 65 and age < 70:
            age2 = True
        elif age >= 70 and age < 75:
            age3 = True
        elif age >= 75 and age < 80:
            age4 = True
        elif age >= 80 and age < 85:
            age5 = True
        else:
            age6 = True

        underWeight = False
        normalWeight = False
        overWeight = False
        obese = False
        if bmi < 18.5:
            underWeight = True
        elif bmi >= 18.5 and bmi < 25:
            normalWeight = True
        elif bmi >= 25 and bmi < 30:
            overWeight = True
        else:
            obese = True

        selfReport = False
        if selfReportedHealth < 3:
            selfReport = True
            
        factors = [age1, age2, age3, age4, age5, age6, diabetes, heartDisease, lungDisease, cancer, currentSmoker, formerSmoker, alcohol, underWeight, normalWeight, overWeight, obese, physicalActivity, bathing, walkBlock, date, selfReport]
        with open('data/suemoto_data.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
            csv_data = list(csv_reader)
            male_sum = 0
            female_sum = 0
            for i, factor in enumerate(factors):
                if factor == 1:
                    if gender == 'm': #male - yes/no
                        csv_data[4][i] = 1
                    if gender == 'f': #female - yes/no
                        csv_data[5][i] = 1
            for i, _ in enumerate(csv_data[0]):
                csv_data[6][i] = csv_data[4][i] - csv_data[1][i]
                csv_data[7][i] = csv_data[5][i] - csv_data[2][i]
                calc = csv_data[6][i] * csv_data[3][i]
                csv_data[8][i] = calc
                male_sum += calc
                calc = csv_data[7][i] * csv_data[3][i]
                csv_data[9][i] = calc
                female_sum += calc

            joint_hr = math.exp(male_sum if gender == 'm' else female_sum)
            risk = (1 - pow(s10_m if gender == 'm' else s10_f, joint_hr))
            excess = 0
            
            if gender == 'm':
                excess = 1 if risk > 0.458 else 0 # Baseline median relative survical all cancers (males)
            else:
                excess = 1 if risk > 0.537 else 0 # Baseline median relative survical all cancers (females)

            return risk, excess
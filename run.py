import yaml, random, time
import numpy as np
import pandas as pd
from util.terminal import Terminal
from util.generateDocx import generateReport
from util.analysis import Analysis
from util.utilities import Utilities
from models.pgm import PGM
from fuzzy_logic.walking import inferWalking
from fuzzy_logic.care import inferCare
from oracles.geneticRisk import getGeneticRisk
from oracles.qrisk import maleQRisk, femaleQRisk

# Initialise NumPy random number generator
rng = np.random.default_rng()

# Instantiate terminal utility class
t = Terminal()

t.logo() # Print banner

# Load config file
config = None
with open("config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

# Instantiate general utility class and inject config
u = Utilities(config)

# Instantiate PGM models class
pgm = PGM()

# Set empty population list
pop = []

def generateSample():
    t.print("Generating distributions...\n")
    t.initialiseProgressBar(total=7) # Progress bar starts, this number will change with sample size
        
    # Load age distribution epidemiology
    age_dists = []
    with open("data/epidemiology.yaml", 'r') as stream:
        age_dists = yaml.safe_load(stream)

    ###----Create distributions----###
    ## Normal
    weight_dist_m, weight_dist_f = u.createNormalDistribution(config['sample-size'], config['chance-of-being-male'], config['weight-stats-m'], config['weight-stats-f'])
    t.updateProgress()   
    height_dist_m, height_dist_f = u.createNormalDistribution(config['sample-size'], config['chance-of-being-male'], config['height-stats-m'], config['height-stats-f'])
    t.updateProgress()   
    srh_dist_m, srh_dist_f = u.createNormalDistribution(config['sample-size'], config['chance-of-being-male'], config['self-reported-health-stats-m'], config['self-reported-health-stats-f'])
    t.updateProgress()   
    cr_dist_m, cr_dist_f = u.createNormalDistribution(config['sample-size'], config['chance-of-being-male'], config['cr-stats-m'], config['cr-stats-f'])
    t.updateProgress()   
    tug_dist_m, tug_dist_f = u.createNormalDistribution(config['sample-size'], config['chance-of-being-male'], config['tug-stats'], config['tug-stats'])
    t.updateProgress()   

    ## Truncated normal
    date_dist_m, date_dist_f = u.createTruncatedNormalDistribution(config['sample-size'], config['chance-of-being-male'], config['date-report-stats-m'], config['date-report-stats-f'])
    t.updateProgress()  

    ## Multinomial
    # Current, former, never
    smoking_m, smoking_f = u.createMultinomialDistribution(config['sample-size'], config['chance-of-being-male'], config['smoking-stats-m'], config['smoking-stats-f'])
    t.updateProgress()  

    ## Simulacrum
    df_sim = pd.read_hdf('data/simulacrum.h5')

    id = 1 # Patient unique ID auto-increment

    t.print("\nGenerating patient samples...")
    t.initialiseProgressBar(total=1324) # Progress bar starts, this number will change with sample size

    # Iterate over age bands
    for index, band in enumerate(age_dists):

        i = 0 # Patient generation starts now

        # Looping over each age band according to its demographics
        while i < ((band['cancerIncidence']['all'] / config['total-older-population']) * config['sample-size']):

            patient = {} # Empty individual patient dictionary

            ###----Age and gender allocation----###
            patient['id'] = id # Unique ID
            patient['age'] = rng.integers(band['ll'], band['ul']) # Randomly assign an age from band between lower and upper limit
            gender = 'm' # Default as male
            if rng.random() > config['chance-of-being-male']: # Randomly allocate to female depending on weighting
                gender = 'f'
            patient['gender'] = gender

            ###----Get genetic profile----------###
            # For internal use only (not presented in data)
            genetic_profile = getGeneticRisk(gender)
        
            ###----Cancer allocation----###
            cancerTypes = []
            cancerWeights = []
            for cancer in band['cancerIncidence'].items():
                if cancer[0] != 'all':
                    cancerTypes.append(cancer[0])
                    cancerWeights.append(cancer[1][gender])
            choice = random.choices(
                cancerTypes, 
                weights=cancerWeights,
                k=1
            )
            patient['cancer'] = choice[0]

            # Will need to either map to MDT or include accurate tumour site
            ###----Query simulacrum------###
            q = df_sim[(df_sim.age == patient['age']) & (df_sim.gender == gender) & (df_sim.cancer_site == u.getMDT(patient['cancer']))]
            simulacrum_sample = q.sample(1) # Random sample from DataFrame
            patient['ethnicity'] = simulacrum_sample['ethnicity'].values[0]
            patient['deprivation'] = int(simulacrum_sample['deprivation'].values[0])
            patient['mdt'] = simulacrum_sample['cancer_site'].values[0]
            patient['cancer_stage'] = simulacrum_sample['cancer_stage'].values[0]
            patient['surgery'] = int(simulacrum_sample['surgery'].values[0])
            patient['chemotherapy'] = int(simulacrum_sample['chemotherapy'].values[0])
            patient['radiotherapy'] = int(simulacrum_sample['radiotherapy'].values[0])

            ###----Root node allocation-###
            # Aerobic activity
            patient['aerobicallyActive'] = u.getBernoulliSample(band['geriatricVulnerabilities']['aerobicallyActive'][gender] / 100)
            
            patient['comorbidity_count'] = 0
            patient['comorbidity'] = 0
            patient['t1dm'] = 0
            patient['t2dm'] = 0 

            # Assign minor root node co-morbidities
            for node in config['root-nodes-minor']:
               patient[node] = u.getBernoulliSample(band['geriatricVulnerabilities'][node][gender] / 100)
               patient['comorbidity_count'] += 1

            # Assign major root node co-morbidities
            for node in config['root-nodes-major']:
                if node != 'diabetes':
                    patient[node] = 0 
                if patient['aerobicallyActive'] == 0:
                    prevalenceUpliftFactor = (band['geriatricVulnerabilities']['aerobicallyActive'][gender] / 100) * 1.6
                    # Subdivide diabetes
                    if node == 'diabetes':
                        diabetes = u.getBernoulliSample((band['geriatricVulnerabilities'][node][gender] / 100) / prevalenceUpliftFactor)
                        if diabetes == 1:
                            if rng.random() < 0.10:
                                patient['t1dm'] = 1
                            else:
                                patient['t2dm'] = 1
                            patient['comorbidity_count'] += 1
                            patient['comorbidity'] = 1
                    else:
                        #print(band['geriatricVulnerabilities'][node][gender] / prevalenceUpliftFactor)
                        diseaseState = u.getBernoulliSample((band['geriatricVulnerabilities'][node][gender] / 100) / prevalenceUpliftFactor)
                        patient[node] = diseaseState
                        if diseaseState == 1:
                            patient['comorbidity_count'] += 1
                            patient['comorbidity'] = 1

            ###----Other distributions--###
            # Assign initial height, weight and BMI
            weight = round(rng.choice(weight_dist_m[index] if gender == 'm' else weight_dist_f[index], 1)[0])
            height = round(rng.choice(height_dist_m[index] if gender == 'm' else height_dist_f[index], 1)[0])

            # Calculate BMI
            bmi = u.calculateBMI(height, weight)

            # Adjust BMI as per activity level
            if patient['aerobicallyActive'] == 0:
                if rng.random() > 0.13:
                    while bmi < 25:
                        weight = round(rng.choice(weight_dist_m[index] if gender == 'm' else weight_dist_f[index], 1)[0])
                        height = round(rng.choice(height_dist_m[index] if gender == 'm' else height_dist_f[index], 1)[0])
                        bmi = u.calculateBMI(height, weight)
            else:
                if rng.random() > 0.26:
                    while bmi > 25:
                        weight = round(rng.choice(weight_dist_m[index] if gender == 'm' else weight_dist_f[index], 1)[0])
                        height = round(rng.choice(height_dist_m[index] if gender == 'm' else height_dist_f[index], 1)[0])
                        bmi = u.calculateBMI(height, weight)

            patient['height'] = height
            patient['weight'] = weight
            patient['bmi'] = bmi

            # Assign other variables randomly from distribution
            patient['incorrectDateReported'] = 1 if rng.random() < rng.choice(date_dist_m[index] if gender == 'm' else date_dist_f[index], 1)[0] else 0
            smoking_status = list(rng.choice(smoking_m  if gender == 'm' else smoking_f))
            patient['smoking'] = smoking_status.index(max(smoking_status))

            # Fix mutual exclusivity
            patient['mci'] = 0 if patient['dementia'] == 1 else patient['mci']
            patient['dementia'] = 0 if patient['mci'] == 1 else patient['dementia']

            ###--Probabilistic graphical modelling--##

            patient['footProblems'] = pgm.inferFootProblems(
                band,
                gender
            )

            patient['historyOfDelirium'] = pgm.inferHistoryOfDelirium(
                band, 
                gender, 
                patient['dementia'],
                patient['visualImpairment']
            ) if ['aerobicallyActive'] != 1 else 0

            patient['copd'] = pgm.inferCOPD(
                    band,
                    gender,
                    patient['smoking'], # Pass raw multinomial value to ensure mutual exclusivity between current and past smoking
                    pgm.inferenceResult(patient['asthma'])
                ) if ['aerobicallyActive'] != 1 else 0

            patient['ckd'] = pgm.inferCKD(
                band,
                gender,
                pgm.inferenceResult(patient['hypertension']), 
                pgm.inferenceResult(patient['bmi'] >= 30),
                pgm.inferenceResult(bool(patient['t1dm'] or patient['t2dm']))
            )

            patient['anaemia'] = pgm.inferAnaemia(
                band,
                gender,
                pgm.inferenceResult(patient['ckd'])
            )

            ###--Add medications---------------------##
            # https://pubmed.ncbi.nlm.nih.gov/23299113/,https://pubmed.ncbi.nlm.nih.gov/16035128/, https://www.tandfonline.com/doi/full/10.1080/08039488.2020.1854853
            patient['antipsychotics'] = 1 if (patient['dementia'] == 1 and rng.random() < 0.074) or (patient['schizophrenia'] == 1 and rng.random() < 0.75) else 0 
            # https://bmjopen.bmj.com/content/3/8/e003423
            patient['antihypertensives'] = 1 if patient['hypertension'] == 1 and rng.random() < 0.674 else 0
            # https://ard.bmj.com/content/61/1/32, https://pubmed.ncbi.nlm.nih.gov/17299838/, https://erj.ersjournals.com/content/17/3/337
            patient['corticosteroids'] = 1 if ((patient['copd'] == 1 and rng.random() < 0.18) or (patient['ra'] == 1 and rng.random() < 0.35)) else 0

            ###--Cardiovascular risk oracle--------##
            qrisk = femaleQRisk(
                patient['age']-10, patient['af'], patient['antipsychotics'], patient['migraine'], patient['ra'], 
                patient['ckd'], 1 if (patient['schizophrenia'] == 1 or patient['bad'] == 1) else 0,
                patient['sle'], patient['antihypertensives'], patient['t1dm'], patient['t2dm'], bmi, genetic_profile['fh_phd'], patient['smoking'],
                patient['corticosteroids']
            ) if gender == 'f' else maleQRisk(
                patient['age']-10, patient['af'], patient['antipsychotics'], patient['migraine'], patient['ra'], 
                patient['ckd'], 1 if (patient['schizophrenia'] == 1 or patient['bad'] == 1) else 0,
                patient['sle'], patient['antihypertensives'], patient['t1dm'], patient['t2dm'], patient['ed'], bmi, genetic_profile['fh_phd'], patient['smoking'],
                patient['corticosteroids']
            )
    
            patient['tia'], patient['stroke'], patient['mi'], patient['angina'] = 0,0,0,0
            if rng.random() < qrisk/100:
                arr = np.array([1,0,0,0])
                rng.shuffle(arr)
                keys = ['tia', 'stroke', 'mi', 'angina']
                for z, key in enumerate(keys):
                    patient[key] = arr[z]

            # Around 75% of patients with stroke have hemiplegia
            patient['hemiplegia'] = 1 if (patient['stroke'] == 1 and rng.random() < 0.75) else 0

            patient['dizziness'] = pgm.inferDizziness(
                band,
                gender,
                pgm.inferenceResult(patient['osteoporosis'])
            )

            if ['aerobicallyActive'] != 1:
                patient['ulcers'] = pgm.inferUlcers(
                    band,
                    gender,
                    pgm.inferenceResult(patient['urinaryIncontinence'])
                )

            patient['orthostaticHypotension'] = pgm.inferOrthostaticHypotension(
                band,
                gender,
                pgm.inferenceResult(bool(patient['t1dm'] or patient['t2dm'])),
                pgm.inferenceResult(patient['hypertension']),
                pgm.inferenceResult(patient['parkinsonsDisease']),
                pgm.inferenceResult(patient['dementia'])
            )

            patient['faecalIncontinence'] = pgm.inferFaecalIncontinence(
                band,
                gender,
                pgm.inferenceResult(patient['urinaryIncontinence']),
                pgm.inferenceResult(bool(patient['t1dm'] or patient['t2dm'])),
                pgm.inferenceResult(patient['hypertension'])
            ) if ['aerobicallyActive'] != 1 else 0

            patient['heartFailure'] = pgm.inferHeartFailure(
                band,
                gender,
                pgm.inferenceResult(patient['bmi'] >= 30),
                pgm.inferenceResult(patient['hypertension']),
                pgm.inferenceResult(bool(patient['t1dm'] or patient['t2dm'])),
                pgm.inferenceResult(bool(patient['smoking'] == 0)),
                pgm.inferenceResult(patient['mi']),
                pgm.inferenceResult(patient['af'])
            ) if ['aerobicallyActive'] != 1 else 0

            # Chronic severe breathlessness mMRC >= 3
            if patient['copd'] == 1 or patient['heartFailure'] == 1:
                # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3888425/
                # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6042838/
                patient['breathlessness'] = 1 if rng.random() > 0.5 else 0
            else:
                # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5079579/
                patient['breathlessness'] = 1 if (['aerobicallyActive'] != 1 and rng.random() < 0.01) else 0

            patient['pvd'] = pgm.inferPVD(
                band,
                gender,
                pgm.inferenceResult(bool(patient['t1dm'] or patient['t2dm'])),
                patient['smoking'], # Pass raw value from multinomial value to ensure categorised correctly at model level
                pgm.inferenceResult(patient['hypertension']),
                pgm.inferenceResult(patient['mi']),
                pgm.inferenceResult(patient['angina']),
                pgm.inferenceResult(patient['heartFailure']),
                pgm.inferenceResult(patient['stroke']),
                pgm.inferenceResult(patient['tia'])
            ) if ['aerobicallyActive'] != 1 else 0

            patient['chronicPain'] = pgm.inferChronicPain(
                band, 
                gender,
                pgm.inferenceResult(patient['arthritis']),
                pgm.inferenceResult(patient['osteoporosis']),
                pgm.inferenceResult(patient['copd']),
                pgm.inferenceResult(patient['migraine']),
                pgm.inferenceResult(bool(patient['mi'] == 1 or patient['angina'] == 1)),
                pgm.inferenceResult(patient['pepticUlcer']),
                pgm.inferenceResult(bool(patient['t1dm'] or patient['t2dm']))
            ) if ['aerobicallyActive'] != 1 else 0

            patient['frailty'] = pgm.inferFrailty(
                band,
                gender,
                pgm.inferenceResult(patient['hearingLoss']),
                pgm.inferenceResult(bool(patient['t1dm'] or patient['t2dm'])),
                pgm.inferenceResult(patient['visualImpairment']),
                pgm.inferenceResult(bool(patient['comorbidity_count'] >= 3)),
                pgm.inferenceResult(bool(patient['mi'] == 1 or patient['tia'] == 1 or patient['stroke'] == 1 or patient['angina'] == 1)),
                #pgm.inferenceResult(patient['multimorbidity']),
                pgm.inferenceResult(patient['copd'])
            ) if ['aerobicallyActive'] != 1 else 0

            patient['badlImpairment'] = pgm.inferBadlDisability(
                band,
                gender,
                pgm.inferenceResult(bool(patient['t1dm'] or patient['t2dm'])),
                pgm.inferenceResult(bool(patient['bmi'] >= 30 and patient['bmi'] < 35)),
                pgm.inferenceResult(bool(patient['bmi'] >= 35 and patient['bmi'] < 40)),
                pgm.inferenceResult(patient['frailty'])
            ) if ['aerobicallyActive'] != 1 else 0

            patient['difficultyBathing'] = 1 if (patient['badlImpairment'] == 1 and ((gender == 'm' and rng.random() <  0.13) or gender == 'f' and rng.random() <  0.18)) else 0

            patient['depression'] = pgm.inferDepression(
                band,
                gender,
                pgm.inferenceResult(patient['frailty']),
                pgm.inferenceResult(patient['arthritis']),
                pgm.inferenceResult(patient['badlImpairment']),
                pgm.inferenceResult(patient['parkinsonsDisease']),
                pgm.inferenceResult(patient['heartFailure'])
            ) if ['aerobicallyActive'] != 1 else 0

            patient['aud'] = pgm.inferAlcoholUseDisorder(
                band,
                gender,
                pgm.inferenceResult(patient['depression'])
            ) if ['aerobicallyActive'] != 1 else 0

            patient['liverDisease'] = pgm.inferLiverDisease(
                band,
                gender,
                pgm.inferenceResult(patient['bmi'] >= 30),
                pgm.inferenceResult(patient['aud'])
            ) if ['aerobicallyActive'] != 1 else 0

            patient['sleepDisturbance'] = pgm.inferSleepDisturbance(
                band,
                gender,
                pgm.inferenceResult(patient['depression']),
                pgm.inferenceResult(patient['hypertension']),
                pgm.inferenceResult(bool(patient['heartFailure'] == 1 or patient['mi'] == 1 or patient['angina'] == 1)),
                pgm.inferenceResult(bool(patient['t1dm'] or patient['t2dm'])),
                pgm.inferenceResult(patient['pepticUlcer']),
                pgm.inferenceResult(patient['asthma']),
                pgm.inferenceResult(patient['copd'])
            )

            patient['iadlImpairment'] = pgm.inferIadlDisability(
                band,
                gender,
                pgm.inferenceResult(patient['frailty']),
                pgm.inferenceResult(bool(patient['t1dm'] or patient['t2dm'])),
                pgm.inferenceResult(patient['sleepDisturbance'])
            ) if ['aerobicallyActive'] != 1 else 0

            # Medication assistance prevalence is 8% divided by prevalence of IADL impairment
            patient['medicationAssistance'] = 1 if (patient['iadlImpairment'] == 1 and rng.random() < 0.147) else 0

            patient['syncope'] = pgm.inferSyncope(
                band,
                gender,
                pgm.inferenceResult(patient['stroke']),
                pgm.inferenceResult(patient['tia']),
                pgm.inferenceResult(patient['hypertension'])
            )

            ###--Fuzzy logic----------------------###
            patient['difficultyWalking'] = inferWalking(
                [
                    1 if (patient['tia'] == 1 or patient['stroke'] == 1) else 0, 
                    1 if (patient['mi'] == 1 or patient['angina'] == 1) else 0, 
                    patient['af'],
                    patient['heartFailure']
                ],
                10 if (patient['copd'] == 1 or patient['asthma'] == 1) else 0,
                10 if (patient['mci'] == 1 or patient['dementia'] == 1) else 0,
                [patient['parkinsonsDisease'], patient['ra'], patient['arthritis']]
            ) if ['aerobicallyActive'] != 1 else 0
            
            # Assume majority (mobility aid users as a proportion of those with mobility difficulty) of patients with walking difficulty and all with frailty use a walking aid - https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4311180/
            patient['usesWalkingAid'] = 1 if (((patient['difficultyWalking'] == 1 and rng.random() < 0.87) or patient['frailty']) and patient['aerobicallyActive'] != 1) else 0

            # 48.4% of frail patients are limited to walk 100 yds (i.e. outside), whereas this is 5.68% in the non-frail group - https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4311180/
            patient['difficultyWalkingOutside'] = 1 if (((patient['frailty'] == 1 and rng.random() < 0.484) or rng.random() < 0.0568) and patient['aerobicallyActive'] != 1) else 0

            ###--Probabilistic graphical modelling-###
            patient['falls'] = pgm.inferFalls(
                band,
                gender,
                pgm.inferenceResult(patient['difficultyWalking']),
                pgm.inferenceResult(patient['dizziness']),
                pgm.inferenceResult(patient['parkinsonsDisease']),
                pgm.inferenceResult(patient['arthritis']),
                pgm.inferenceResult(patient['urinaryIncontinence']),
                pgm.inferenceResult(patient['orthostaticHypotension']),
                pgm.inferenceResult(patient['af']),
                pgm.inferenceResult(patient['depression']),
                pgm.inferenceResult(patient['footProblems'])
            )

            #https://ogg.osu.edu/media/documents/sage/course3/fear_of_falling.pdf
            patient['fearOfFalling'] = 1 if ((patient['falls'] == 1 and rng.random() < (0.32 * (1 if gender == 'm' else 2)))) else 0

            patient['malnutrition'], patient['weightLoss'], patient['anorexia'] = pgm.inferMalnutrition(
                band, 
                gender, 
                patient['parkinsonsDisease'],
                patient['badlImpairment'],
                patient['mci'],
                patient['dementia']
            ) if patient['aerobicallyActive'] != 1 else 0,0,0

            patient['fragilityFracture'] = pgm.inferFragilityFracture(
                band,
                gender,
                pgm.inferenceResult(bool(patient['weight'] < 58)),
                pgm.inferenceResult(bool(patient['bmi'] < 19.5)),
                pgm.inferenceResult(bool(patient['bmi'] > 30)),
                pgm.inferenceResult(patient['weightLoss']),
                pgm.inferenceResult(bool(patient['smoking'] == 0)),
                pgm.inferenceResult(patient['ra'])
            )

            # This is very difficult to model
            patient['socialVulnerability'] = 1 if (rng.random() < band['geriatricVulnerabilities']['socialVulnerability'][gender] and ['aerobicallyActive'] != 1)  else 0

            ###--Fuzzy logic----------------------###
            patient['needsCare'] = inferCare(
                patient['age'],
                10 if patient['badlImpairment'] == 1 else 5 if (patient['iadlImpairment'] == 1 and patient['badlImpairment'] == 0) else 0,
                10 if patient['livesAlone'] else 0
            ) if patient['aerobicallyActive'] != 1 else 0

            patient['polypharmacy'] = u.hasPolypharmacy(patient)

            patient['multimorbidity'] = u.hasMultimorbidity(patient)

            ###--Assign creatinine level-----------###
            # Reduce creatinine clearance < 34 if has stage 3-5 CKD (this is therefore overestimated)
            if patient['ckd'] == 1:
                cr = round(np.random.choice(cr_dist_m[index], 1)[0]) if gender == 'm' else round(np.random.choice(cr_dist_f[index], 1)[0])
                crcl = u.calculateCrCl(patient['height'], patient['weight'], patient['age'], gender, cr)
                while crcl > 34:
                    crcl = u.calculateCrCl(patient['height'], patient['weight'], patient['age'], gender, cr)
                    cr += 1
                patient['cr'] = cr
            else: # Assign normal ageing creatinine
                patient['cr'] = round(np.random.choice(cr_dist_m[index], 1)[0]) if gender == 'm' else round(np.random.choice(cr_dist_f[index], 1)[0])

            ###--Assign self-reported health-------###
            self_reported_health = round(rng.choice(srh_dist_m[index] if gender == 'm' else srh_dist_f[index], 1)[0])
            # This could potentially be fuzzy logic or PGM
            self_reported_health = rng.sample(set([3,4]), 1)[0] if patient['aerobicallyActive'] == 1 and self_reported_health < 3 and rng.random() > 0.7 else self_reported_health
            patient['self_reported_health'] = round(self_reported_health)

            # Assign electronic Frailty Index (eFI)
            patient['efi'], patient['efi_classification'] = u.calculateEFI(patient)

            # Assign Timed-Up-and-Go (TUG) test value according to known diagnostic accuracy
            tug = round(rng.choice(tug_dist_m[index] if gender == 'm' else tug_dist_f[index], 1)[0], 2)
            if patient['frailty'] == 1:
                if rng.random() < 0.93:
                    while tug < 10:
                        tug = round(rng.choice(tug_dist_m[index] if gender == 'm' else tug_dist_f[index], 1)[0], 2)
                    patient['tug'] = tug
                else:
                    while tug > 10:
                        tug = round(rng.choice(tug_dist_m[index] if gender == 'm' else tug_dist_f[index], 1)[0], 2)
                    patient['tug'] = tug
            else:
                if rng.random() < 0.62:
                    while tug > 10:
                        tug = round(rng.choice(tug_dist_m[index] if gender == 'm' else tug_dist_f[index], 1)[0], 2)
                    patient['tug'] = tug
                else:
                    while tug < 10:
                        tug = round(rng.choice(tug_dist_m[index] if gender == 'm' else tug_dist_f[index], 1)[0], 2)
                    patient['tug'] = tug

            patient['asa'] = u.calculateASA(patient)

            ###----OUTCOMES--------------###
            patient['pod_risk'], patient['pod_present'] = pgm.inferPostOpDelirium(
                pgm.inferenceResult(patient['historyOfDelirium']),
                pgm.inferenceResult(patient['frailty']),
                pgm.inferenceResult(patient['ckd']),
                pgm.inferenceResult(patient['depression']),
                pgm.inferenceResult(patient['badlImpairment']),
                pgm.inferenceResult(patient['iadlImpairment']),
                pgm.inferenceResult(patient['stroke']),
                pgm.inferenceResult(patient['tia']),
                pgm.inferenceResult(bool(patient['smoking'] == 0)),
                pgm.inferenceResult(bool(patient['t1dm'] == 1 or patient['t2dm'] == 1)),
                pgm.inferenceResult(bool(patient['mi'] == 1 or patient['angina'] == 1)),
                pgm.inferenceResult(patient['polypharmacy']),
                pgm.inferenceResult(patient['heartFailure']),
                pgm.inferenceResult(patient['visualImpairment'])
            )

            patient['all_surgical_comps_risk'], patient['all_surgical_comps_present'] = pgm.inferAllSurgicalComplications(
                pgm.inferenceResult(patient['frailty']),
                pgm.inferenceResult(patient['depression']),
                pgm.inferenceResult(patient['polypharmacy']),
                pgm.inferenceResult(bool(patient['smoking'] == 0)),
                pgm.inferenceResult(patient['aud'])
            )

            patient['post_op_pain_risk'], patient['post_op_pain_present'] = pgm.inferPostOperativePain(
                pgm.inferenceResult(patient['depression']),
                pgm.inferenceResult(bool(patient['smoking'] == 0)),
            )

            patient['wound_complications_risk'], patient['wound_complications_present'] = pgm.inferWoundComplications(
                pgm.inferenceResult(bool(patient['smoking'] == 0)),
                pgm.inferenceResult(patient['frailty']),
                pgm.inferenceResult(patient['aud'])
            )

            patient['post_op_sepsis_risk'], patient['post_op_sepsis_present'] = pgm.inferPostOpSepsis(
                pgm.inferenceResult(bool(patient['smoking'] == 0)),
                pgm.inferenceResult(patient['frailty']),
                pgm.inferenceResult(patient['aud']),
                pgm.inferenceResult(patient['heartFailure']),
                pgm.inferenceResult(bool(patient['t1dm'] == 1 or patient['t2dm'] == 1)),
                pgm.inferenceResult(patient['ckd']),
            )

            patient['post_op_pulmonary_comps_risk'], patient['post_op_pulmonary_comps_present'] = pgm.inferPostOpPulmComps(
                pgm.inferenceResult(bool(patient['smoking'] == 0)),
                pgm.inferenceResult(patient['frailty']),
                pgm.inferenceResult(patient['aud']),
                pgm.inferenceResult(patient['heartFailure'])
            )

            patient['post_op_neuro_comps_risk'], patient['post_op_neuro_comps_present'] = pgm.inferPostOpNeuroComps(
                pgm.inferenceResult(bool(patient['smoking'] == 0)),
                pgm.inferenceResult(patient['frailty'])
            )

            patient['cpr_failure_risk'], patient['cpr_failure_present'] = pgm.inferSurviveCPR(
                patient['age'],
                pgm.inferenceResult(patient['badlImpairment']),
                pgm.inferenceResult(patient['ckd'])
            )

            patient['post_op_itu_admission_risk'], patient['post_op_itu_admission_present'] = pgm.inferITUAdmission(
                pgm.inferenceResult(bool(patient['smoking'] == 0)),
                pgm.inferenceResult(patient['aud']),
                pgm.inferenceResult(patient['anaemia']),
                pgm.inferenceResult(patient['frailty']),
                patient['asa']
            )

            patient['pims_risk'], patient['pims_present'] = pgm.inferPIMs(
                pgm.inferenceResult(bool(patient['t1dm'] == 1 or patient['t2dm'] == 1)),
                pgm.inferenceResult(patient['polypharmacy']),
            )

            patient['increased_los_risk'], patient['increased_los_present'] = pgm.inferIncreasedLOS(
                pgm.inferenceResult(patient['frailty']),
                pgm.inferenceResult(patient['aud']),
                pgm.inferenceResult(patient['iadlImpairment']),
                pgm.inferenceResult(patient['badlImpairment']),
                patient['asa']
            )

            patient['functional_decline_risk'], patient['functional_decline_present'] = pgm.inferFunctionalDecline(
                pgm.inferenceResult(patient['iadlImpairment']),
            )

            patient['neutropaenic_events_risk'], patient['neutropaenic_events_present'] = pgm.inferNeutropaenicEvents(
                pgm.inferenceResult(patient['comorbidity']),
                pgm.inferenceResult(bool(patient['t1dm'] == 1 or patient['t2dm'] == 1)),
            )

            patient['nursing_home_admission_risk'], patient['nursing_home_admission_present'] = pgm.inferNursingHomeAdmission(
                pgm.inferenceResult(bool(patient['smoking'] == 0)),
                pgm.inferenceResult(patient['frailty']),
                pgm.inferenceResult(patient['badlImpairment']),
                pgm.inferenceResult(patient['difficultyWalkingOutside']),
            )

            patient['chemotherapy_toxicity_risk'],
            patient['chemotherapy_toxicity_score'], 
            patient['chemotherapy_toxicity_present'] = u.calculateCarg(
                patient['age'],
                gender,
                patient['cancer'],
                patient['height'],
                patient['weight'],
                patient['anaemia'],
                patient['cr'],
                patient['hearingLoss'],
                patient['falls'],
                patient['medicationAssistance'],
                patient['difficultyWalkingOutside'],
                0 # Needs to calculate decreased social activity somehow 
            )

            patient['post_op_mace_risk'], patient['post_op_mace_present'] = u.calculateGupta(
                patient
            )

            patient['post_op_30_day_major_mortality_risk'], patient['post_op_30_day_major_mortality_present'] = u.calculateSort(
                patient,
                'major'
            )

            patient['post_op_30_day_minor_mortality_risk'], patient['post_op_30_day_minor_mortality_present'] = u.calculateSort(
                patient,
                'minor'
            )

            patient['10_year_mortality_risk'], patient['10_year_mortality_excess_present'] = u.calculateSuemoto(
               gender, 
               patient['age'],
               1 if patient['t1dm'] == 1 or patient['t2dm'] == 1 else 0,
               1 if patient['angina'] == 1 or patient['mi'] == 1 or patient['af'] == 1 or patient['heartFailure'] == 1 or patient['heartValveDisease'] == 1 else 0,
               1 if patient['copd'] == 1 or patient['asthma'] == 1 else 0,
               0,
               1 if patient['smoking'] == 0 else 0,
               1 if patient['smoking'] == 1 else 0,
               1 if patient['drinksAlcohol'] == 1 else 0,
               patient['height'],
               patient['weight'],
               patient['aerobicActivity'],
               patient['difficultyBathing'],
               patient['difficultyWalkingOutside'],
               patient['incorrectDateReported'],
               patient['self_reported_health']
            )

            # Creating composite endpoints
            patient['composite_endpoint_surgery_adverse'] = 0
            patient['composite_endpoint_chemo_adverse'] = 0
            patient['composite_endpoint_general_adverse'] = 0
            patient['composite_endpoint_oncogeris_beneficial'] = 0
            for k,v in patient.items():
                for e in config['surgery']:
                    if v == 1 and k == e:
                        patient['composite_endpoint_surgery_adverse'] = 1
                        break
                for e in config['chemotherapy']:
                    if v == 1 and k == e:
                        patient['composite_endpoint_chemo_adverse'] = 1
                        break
                for e in config['general']:
                    if v == 1 and k == e:
                        patient['composite_endpoint_general_adverse'] = 1
                        break
                for e in config['oncogeriatric-input']:
                    if v == 1 and k == e:
                        patient['composite_endpoint_oncogeris_beneficial'] = 1
                        break

            # Append to list
            pop.append(patient)
            
            # Update counter, ID and progress bar
            i += 1
            id += 1
            t.updateProgress()

generateSample()
df = pd.DataFrame(pop)
date = time.strftime("%d-%m-%Y-%H:%M:%S")
df.to_csv(f'results/data/{date}.csv', index=False)
analysis = Analysis(pop)
generateReport(analysis)
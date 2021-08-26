import math

class Utils():
    def __init__(self, meds, patient):
        self.meds = meds,
        self.patient = patient.to_dict('records')[0]

    def calculate_acb_score(self):
        acb_list = {
            'aripiprazole': 1, 
            'atenolol': 1, 
            'citalopram': 1,
            'codeine': 1, 
            'dexamethasone': 1,
            'digoxin': 1, 
            'diltiazem': 1,
            'escitalopram': 1,
            'fentanyl': 1, 
            'fluoxetine': 1,
            'furosemide': 1, 
            'haloperidol': 1, 
            'hydrocortisone': 1, 
            'isosorbide mononitrate': 1, 
            'mirtazepine': 1,
            'morphine': 1, 
            'lithium': 1,
            'prednisolone': 1,
            'theophylline': 1, 
            'risperidone': 1, 
            'trazodone': 1,
            'venlafaxine': 1,
            'warfarin': 1,
            'amantadine': 2,
            'carbamazepine': 2,
            'amitriptyline': 3,
            'clomipramine': 3,
            'darifenacin': 3, 
            'falvoxate': 3,
            'fesoterodine': 3, 
            'imipramine': 3,
            'ipratropium': 3,
            'paroxetine': 3,
            'nortriptyline': 3,
            'olanzapine': 3,
            'oxybutynin': 3,
            'propiverine': 3,
            'quetiapine': 3,
            'solifenacin': 3,
            'tolerodine': 3,
            'trospium': 3
        }

        acb_score = 0

        for m in self.meds[0]:
            for d,s in acb_list.items():
                if m == d:
                    acb_score += s

        return acb_score

    def eGFR(self):
        egfr = 186 * math.pow((self.patient['cr'] / 88.4), -1.154) * math.pow(self.patient['age'] , -0.203) * (0.742 if self.patient['gender'] == 'f' else 1) * (1.210 if "BLACK" in self.patient['ethnicity']  else 1)
        return egfr

    def stop_criteria(self):

        stop = []

        def in_list(drug: str, _list: list):
            for d in _list:
                if drug == d:
                    return True
            return False

        def not_in_list(drug: str):
            for d in self.meds[0]:
                if drug == d:
                    return False
            return True

        def taking(_list: list):
            for d in self.meds[0]:
                for m in _list:
                    if m == d:
                        return True
            return False

        def has_condition(_list: list):
            for k,c in self.patient.items():
                if c == 1:
                    for d in _list:
                        if k == d:
                            return True
            return False
        
        def in_combination(drug: str, _list: list, _combinator: list):
            for d in _list:
                if drug == d:
                    for med in self.meds[0]:
                        for comb in _combinator:
                            if med == comb:
                                return True
            return False
            
        for med in self.meds[0]:
            if in_list(med, ['verapamil', 'diltiazem']) == True and self.patient['heartFailure'] == 1:
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': "Verapamil or diltiazem with NYHA Class III or IV heart failure (may worsen heart failure)"})
            
            if in_combination(med, ['propanolol', 'bisoprolol', 'atenolol', 'carvedilol'], ['verapamil', 'diltiazem']) == True:
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': "Beta-blocker in combination with verapamil or diltiazem (risk of heart block)"})
            
            if in_list(med, ['furosemide', 'bumetanide']) == True and self.patient['urinaryIncontinence'] == 1:
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': 'Loop diuretic for treatment of hypertension with concurrent urinary incontinence (may exacerbate incontinence)'})

            if in_combination(med, ['sildenafil', 'tadalafil', 'vardenafil'], ['isosorbide mononitrate']) == True:
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': 'Phosphodiesterase type-5 inhibitors (e.g. sildenafil, tadalafil, vardenafil) in severe heart failure characterised by hypotension i.e. systolic BP < 90 mmHg, or concurrent nitrate therapy for angina (risk of cardiovascular collapse)'})
            
            if in_list(med, ['aspirin']) == True and self.patient['pepticUlcer'] == 1 and not_in_list(['omeprazole', 'lansoprazole']):
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': 'Aspirin with a past history of peptic ulcer disease without concomitant PPI (risk of recurrent peptic ulcer )'})

            if in_list(med, ['aspirin']) == True and self.patient['af'] == 1 and in_list(med, ['warfarin', 'rivaroxaban', 'apixaban', 'edoxaban']) == True:
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': 'Aspirin in combination with vitamin K antagonist, direct thrombin inhibitor or factor Xa inhibitors in patients with chronic atrial fibrillation (no added benefit from aspirin)'})

            if in_combination(med, ['ibuprofen', 'naproxen', 'celecoxib'], ['warfarin', 'rivaroxaban', 'apixaban', 'edoxaban']) == True:
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': "NSAID and vitamin K antagonist, direct thrombin inhibitor or factor Xa inhibitors in combination (risk of major gastrointestinal bleeding)"})

            if in_list(med, ['aspirin', 'clopidogrel']) == True and in_list(med, ['ibuprofen', 'naproxen', 'celecoxib']) == True and not_in_list(['omeprazole', 'lansoprazole']):
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': 'NSAID with concurrent antiplatelet agent(s) without PPI prophylaxis (increased risk of peptic ulcer disease)'})
            
            if in_list(med, ['amitriptyline', 'trazadone', 'dosulepin', 'lofepramine', 'nortriptyline', 'clomipramine', 'imipramine']) == True and (self.patient['dementia'] == 1 or taking(['tamsulosin', 'alfuzocin', 'doxazocin', 'indoramin', 'terazocin', 'prazocin']) == True):
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': 'TriCyclic Antidepressants (TCAs) with dementia, narrow angle glaucoma, cardiac conduction abnormalities, prostatism, or prior history of urinary retention (risk of worsening these conditions)'})

            if in_list(med, ['chlorpromazine', 'clozapine', 'flupenthixol', 'fluphenzine', 'pipothiazine', 'promazine', 'zuclopenthixol']) == True and taking(['tamsulosin', 'alfuzocin', 'doxazocin', 'indoramin', 'terazocin', 'prazocin']) == True:
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': 'Neuroleptics with moderate-marked antimuscarinic/anticholinergic effects (chlorpromazine, clozapine, flupenthixol, fluphenzine, pipothiazine, promazine, zuclopenthixol) with a history of prostatism or previous urinary retention (high risk of urinary retention)'})
            
            if in_list(med, ['olanzipine', 'risperidone', 'haloperidol', 'chlorpromazine', 'trifluoperazine', 'aripiprazole']) == True and self.patient['parkinsonsDisease'] == 1:
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': 'Antipsychotics (i.e. other than quetiapine or clozapine) in those with parkinsonism or Lewy Body Disease (risk of severe extra-pyramidal symptoms)'})

            if in_list(med, ['apixiban', 'rivaroxaban', 'edoxaban']) == True and self.eGFR() < 15:
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': 'Factor Xa inhibitors (e.g. rivaroxaban, apixaban) if eGFR < 15 ml/min/1.73m2 (risk of bleeding)'})

            if in_list(med, ['ibuprofen', 'naproxen', 'celecoxib']) == True and self.eGFR() < 50:
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': 'NSAID’s if eGFR < 50 ml/min/1.73m2  (risk of deterioration in renal function)'})
            
            if in_list(med, ['metformin']) == True and self.eGFR() < 30:
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': 'Metformin if eGFR < 30 ml/min/1.73m2 (risk of lactic acidosis)'})

            if in_list(med, ['ipratropium', 'ipratropium with salbutamol', 'tiotropium']) == True and taking(['tamsulosin', 'alfuzocin', 'doxazocin', 'indoramin', 'terazocin', 'prazocin']) == True:
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': 'Anti-muscarinic bronchodilators (e.g. ipratropium, tiotropium) with a history of narrow angle glaucoma (may exacerbate glaucoma) or bladder outflow obstruction (may cause urinary retention).'})
            
            if in_list(med, ['ibuprofen', 'naproxen']) == True and self.patient['pepticUlcer'] == 1 and not_in_list(['omeprazole', 'lansoprazole']) == True:
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': 'Non-steroidal anti-inflammatory drug (NSAID) other than COX-2 selective agents with history of peptic ulcer disease or gastrointestinal bleeding, unless with concurrent PPI or H2 antagonist (risk of peptic ulcer relapse)'})

            if in_list(med, ['celecoxib']) == True and has_condition(['mi', 'stroke', 'tia', 'pvd']) == True:
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': 'COX-2 selective NSAIDs with concurrent cardiovascular disease (increased risk of myocardial infarction and stroke)'})

            if in_combination(med, ['ibuprofen', 'naproxen'], ['prednisolone', 'hydrocortisone', 'dexamethasone']) == True and not_in_list(['omeprazole', 'lansoprazole']) == True:
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': 'NSAID with concurrent corticosteroids without PPI prophylaxis (increased risk of peptic ulcer disease)'})
            
            if in_list(med, ['alendronic acid']) == True and self.patient['pepticUlcer'] == 1:
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': 'Oral bisphosphonates in patients with a current or recent history of upper gastrointestinal disease i.e. dysphagia, oesophagitis, gastritis, duodenitis, or peptic ulcer disease, or upper gastrointestinal bleeding (risk of relapse/exacerbation of oesophagitis, oesophageal ulcer, oesophageal stricture)'})

            if in_list(med, ['tamsulosin', 'alfuzocin', 'doxazocin', 'indoramin', 'terazocin', 'prazocin']) == True and self.patient['orthostaticHypotension'] == 1:
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': 'Selective alpha-1 selective alpha blockers in those with symptomatic orthostatic hypotension or micturition syncope (risk of precipitating recurrent syncope)'})
            
            # Antimuscarinics - NEED category and here

            if in_list(med, ['pioglitazone']) == True and self.patient['heartFailure'] == 1:
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': 'Thiazolidenediones (e.g. rosiglitazone, pioglitazone) in patients with heart failure (risk of exacerbation of heart failure)'})

            if in_list(med, ['ramipril', 'enalipril', 'lisinopril', 'candesartan', 'losartan', 'amlodipine', 'isosorbide mononitrate']) and self.patient['orthostaticHypotension'] == 1:
                stop.append({'agent': med, 'criteria': 'STOP', 'reason': 'Vasodilator drugs (e.g. alpha-1 receptor blockers, calcium channel blockers, long-acting nitrates, ACE inhibitors, angiotensin I receptor blockers, ) with persistent postural hypotension i.e. recurrent drop in systolic blood pressure ≥ 20mmHg (risk of syncope, falls)'})
            
        return stop
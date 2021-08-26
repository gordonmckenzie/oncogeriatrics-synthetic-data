from prescribing.prescriber import Prescriber

# Test patient
patient = {
    'corticosteroids': 1, 
    'antihypertensives': 1, 
    'antipsychotics': 1,
    'af': 1, 
    'age': 75, 
    'gender': 'm', 
    'ethnicity': 'BLACK AFRICAN',
    'cr': 100, 
    'heartFailure': 1, 
    'hypertension': 1, 
    'stroke': 1, 
    'tia': 1, 
    'mi': 1, 
    'pvd': 1, 
    't1dm': 1, 
    't2dm': 0, 
    'liverDisease': 0, 
    'aud': 0, 
    'drinksAlcohol': 1, 
    'arthritis': 1,
    'luts': 1,
    'depression': 1,
    'asthma': 1,
    'pepticUlcer': 1,
    'ed': 1,
    'thyroidDisease': 1,
    'dementia': 1,
    't2dm': 1,
    'angina': 1,
    'mi': 1, 
    'stroke': 1,
    'tia': 1,
    'anaemia': 1, 
    'migraine': 1,
    'bad': 1,
    'parkinsonsDisease': 1,
    'ra': 1,
    'sle': 1,
    'copd': 1,
    'osteoporosis': 1,
    'homebound': 1,
    'chronicPain': 1
}

class TestPrescribing():
    def test_egfr(self): 
        p = Prescriber(patient)
        egfr = p.eGFR()
        assert round(egfr) == 81 

    def test_prescribe(self):
        p = Prescriber(patient)
        prescribe = p.prescribe()
        assert prescribe > 0
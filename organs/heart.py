import math
from catboost import CatBoostClassifier
from sdv.tabular import CTGAN
import numpy as np
import scipy.stats as stats

rng: np.random = np.random.default_rng()

def isclose(a, b, rel_tol=1e-9, abs_tol=0.0):

    if a == b:
        return True

    if rel_tol < 0.0 or abs_tol < 0.0:
        raise ValueError('error tolerances must be non-negative')

    if math.isinf(abs(a)) or math.isinf(abs(b)):
        return False

    diff = abs(b - a)

    return (((diff <= abs(rel_tol * b)) or
             (diff <= abs(rel_tol * a))) or
            (diff <= abs_tol))

def cardiac_dynamics(
    age=65, sex='m', hr=70, bmi=25, has_diabetes=0, chol=4.5, ejection_fraction='preserved', 
    aud=0, sedentary=True, smoker=1
):
    """ 
    https://erp.bioscientifica.com/view/journals/echo/7/1/ERP-19-0050.xml
    
    Males & Females
                Severely impaired LVEF	    Impaired LVEF	    Borderline low LVEF	    Normal LVEF				
    LVEF (%)    ≤35%	                    36–49%	            50–54%	                ≥55-70%

    Male LVEDV (mL)	    53–156
    Male LVESV (mL)	    15–62
    Female LVEDV (mL)	46–121
    Female LVESV (mL)	13–47
    
    """
    
    lvef_target = [55, 80]

    # https://bestpractice.bmj.com/topics/en-gb/953/criteria
    if ejection_fraction == 'preserved':
        lvef_target = [46, 80]
    elif ejection_fraction == 'reduced':
        lvef_target = [14, 46]
    elif ejection_fraction == 'mid-range':
        lvef_target = [41, 50]

    edv, esv, sv, sv_target, lvef, co_resting, avd_exercising = 0, 0, 0, 0, 0, 0, 0

    if sedentary == True:
        if sex == 'm':
            avd_exercising = rng.normal(13.6, 1.1)
            sv_target = round(rng.normal(101, 19))
        else: 
            avd_exercising = rng.normal(11.9, 1.6)
            sv_target = round(rng.normal(74, 8))
    else:
        if sex == 'm':
            avd_exercising = rng.normal(14.7, 1.4)
            sv_target = round(rng.normal(124, 14))
        else: 
            avd_exercising = rng.normal(14.5, 1.1)
            sv_target = round(rng.normal(85, 9))

    while True:
        edv_dist = stats.truncnorm(((106 if sex == 'm' else 86) - (160 if sex == 'm' else 132)) / (27 if sex == 'm' else 23), ((214 if sex == 'm' else 178) - (160 if sex == 'm' else 132)) / (27 if sex == 'm' else 23), loc=160 if sex == 'm' else 132, scale=27 if sex == 'm' else 23)
        edv = round(edv_dist.rvs(1)[0])
        
        esv_dist = stats.truncnorm(((26 if sex == 'm' else 22) - (54 if sex == 'm' else 44)) / (14 if sex == 'm' else 11), ((82 if sex == 'm' else 66) - (54 if sex == 'm' else 44)) / (14 if sex == 'm' else 11), loc=54 if sex == 'm' else 44, scale=14 if sex == 'm' else 11)
        esv = round(esv_dist.rvs(1)[0])
        
        # Unclear if stroke volume increases during exercise https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4896996/
        sv = edv - esv

        # https://pubmed.ncbi.nlm.nih.gov/11153730/
        hr_max = 208 - (0.7 * age)
        percentage_hr_achieved_dist = stats.truncnorm((60 - 83) / 16, (100 - 83) / 16, loc=83, scale=16)
        percentage_hr_achieved = round(percentage_hr_achieved_dist.rvs(1)[0])

        # https://academic.oup.com/biomedgerontology/article-pdf/60/1/57/1425876/57.pdf
        # https://core.ac.uk/reader/189993373?utm_source=linkout
        # https://www.frontiersin.org/articles/10.3389/fphys.2017.00408/full
        est_vo2_max = round(15 * (hr_max / (hr_max * (percentage_hr_achieved/100))), 1) # Correct for resting VO2 max 
        co_resting = (sv * hr) / 1000
        
        # https://journals.physiology.org/doi/full/10.1152/jappl.1999.86.3.799
        # https://www.sciencedirect.com/science/article/pii/S0047637415300221
        co_exercising = ((sv * (hr_max * (percentage_hr_achieved/100))) / 1000)

        # Risk factors for sub maximal test - extrapolation for VO2 max
        vo2_peak = round(pow(co_exercising * avd_exercising, 0.55), 1) # https://www.sciencedirect.com/science/article/pii/S0531556517301006

        # CPET = https://www.bjanaesthesia.org/article/S0007-0912(17)53995-1/fulltext#appsec1

        lvef = round((sv / edv) * 100, 1)

        if (lvef >= lvef_target[0] and lvef <= lvef_target[1]) and (isclose(sv_target, sv, rel_tol=0.5, abs_tol=0) == True):
            break

    # Arterial stiffness
    # Blood pressure
    """
    0        has_diabetes    58.720009
    1                 bmi    10.826692
    2             confage    10.061030
    3                 sex     8.155177
    4                chol     4.827052
    5     regular_alcohol     3.228737
    6  aerobically_active     2.999589
    7      current_smoker     1.181714
    """
    hypertension = CatBoostClassifier()
    hypertension.load_model("models/decision/hypertension")
    has_hypertension = hypertension.predict([1 if smoker == 0 else 0, 1 if sedentary == False else 0, aud, age, 1 if sex == 'm' else 2, bmi, chol, has_diabetes])
    model: CTGAN = CTGAN.load(f'models/gans/{"hypertension" if has_hypertension == 1 else "normotension"}.pkl')

    bp = model.sample(1)
    sbp = round(bp.mean_sys.values[0])
    dbp = round(bp.mean_dias.values[0])
    
    pp = sbp - dbp
    mabp = dbp + ((1/3) * pp)
    tpr = (mabp / co_resting) / 60 # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4444041/
    
    return edv, esv, sv, co_resting, round(co_exercising, 2), lvef, vo2_peak, percentage_hr_achieved, est_vo2_max, sbp, dbp, round(tpr, 2), round(mabp)

edv, esv, sv, co_resting, co_exercising, lvef, vo2_peak, percentage_hr_achieved, est_vo2_max, sbp, dbp, tpr, mabp = cardiac_dynamics(age=80, bmi=30, chol=7, aud=1, sedentary=True, smoker=0)

print(
f"""
EDV: {edv} ml
ESV: {esv} ml
SV: {sv} ml
CO resting: {co_resting} L/min
LVEF: {lvef}%
(e) VO2 Max: {est_vo2_max} mL/kg/min
VO2 Peak: {vo2_peak} mL/kg/min
% HR achieved: {percentage_hr_achieved}%
CO exercising: {co_exercising} L/min
BP: {sbp}/{dbp} mm/Hg
MAP: {mabp} mm/Hg
TPR: {tpr} mmHg⋅s⋅mL-1
"""
)
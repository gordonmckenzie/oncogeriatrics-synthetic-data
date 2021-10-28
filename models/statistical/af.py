import math

"""
Cox Proportional hazard derived
"""

#https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3647274/
#https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6824570/

def af_risk(age, _ethnicity, height, weight, sbp, dbp, _smoking, antihypertensives, diabetes, heart_failure, mi):
    
    ethnicity = 1 if _ethnicity == "WHITE" else 0

    smoking = 1 if _smoking == 0 else 0
    
    sum = (age * 0.10166) + (ethnicity * 0.46491) + (height * 0.02478) + (weight * 0.0077) + (sbp * 0.00986) + (dbp * -0.01013) + (smoking * 0.35931) + (antihypertensives * 0.34889) + (diabetes * 0.23666) + (heart_failure * 0.70127) + (mi * 0.49596)

    risk = 1 - math.pow(0.9718412736, math.exp(sum - 12.5804513))

    return risk * 100

print(af_risk(60, "WHITE", 122, 78, 120, 75, 1, 0, 0, 0, 0))
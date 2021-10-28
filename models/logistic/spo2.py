import numpy as np
import scipy.stats as stats

rng: np.random = np.random.default_rng()

def determine_spo2(patient):
    spo2 = 100
    # https://www.sciencedirect.com/science/article/pii/S0954611112002302
    X = -3.5 + (np.log(1.6) * 1 if patient['gender'] == 'm' else 0) + np.log(1.5) + (np.log(1.8 if (patient['smoking'] == 1) else 1.4) * 1 if (patient['smoking'] == 0 or patient['smoking'] == 1) else 0) + (np.log(1.4) * patient['breathlessness']) + (np.log(6.2) * 1 if patient['bmi'] >= 35 else 0)
    prob_less_equal_to_95 = 1 / (1 + np.exp(-X))
    if prob_less_equal_to_95 > 0.5:
        dist = stats.truncnorm((85 - 93) / 2, (95 - 93) / 2, loc=93, scale=2)
        spo2 = round(dist.rvs(1)[0])
    else:
        dist = stats.truncnorm((96 - 97.5) / 1.5, (100 - 97.5) / 1.5, loc=97.5, scale=1.5)
        spo2 = round(dist.rvs(1)[0])
    
    return spo2
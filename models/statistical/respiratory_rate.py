import numpy as np
import scipy.stats as stats

rng: np.random = np.random.default_rng()

def determine_rr(patient):
    rr = 16

    # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5360891/
    if patient['copd'] == 1:
        rr = round(rng.normal(22, 4, 1)[0])

    # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2975920/
    elif patient['heartFailure'] == 1:
        rr = round(rng.normal(19.6, 3.4, 1)[0])
    else:
        dist = stats.truncnorm((12 - 15.5) / 3.7, (20 - 15.5) / 3.7, loc=15.5, scale=3.7)
        rr = round(dist.rvs(1)[0])

    return rr

# patient = {
#     'copd': 0,
#     'heartFailure': 1
# }
# print(determine_rr(patient))
import numpy as np
import math

rng = np.random.default_rng()

t = 10 #years

def cycleCardiovascularRisk(qrisk):

    # https://link.springer.com/article/10.1007/s40273-020-00937-z
    ten_year_rate = -math.log(1-(qrisk/100))
    one_year_prob = 1 - math.exp((-ten_year_rate * (1/10)))

    results = []

    for i in range(0,5000):
        for i in range(0,t+1):
            if rng.random() < one_year_prob:
                results.append(1)
                #return 1
        #return 0
        results.append(0)

    print(np.array(results).mean())

cycleCardiovascularRisk(70)
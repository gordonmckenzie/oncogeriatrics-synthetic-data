from locale import ABDAY_1
import math
import pandas as pd
import numpy as np

rng = np.random.default_rng()

def get_beta_params(mu, sigma):
    a = (((1 - mu) / sigma**2) - (1 / mu)) * mu**2
    b = a * ((1 / mu) - 1)
    return a,b

def calculate_predicted_values(age, sex, height, ethnicity):

    # https://github.com/thlytras/rspiro/blob/master/data-raw/RLookupTable.csv
    # https://erj.ersjournals.com/content/40/6/1324.figures-only
    df = pd.read_csv('organs/pft_lookup.csv')

    _sex = 1 if sex == 'm' else 2

    measures = ['FEV1', 'FVC', 'FEV1FVC']
    results = {}
    for measure in measures:
        lookup = df[(df['sex'] == _sex) & (df['agebound'] == age) & (df['f'] == measure)]

        a0 = lookup.a0
        a1 = lookup.a1
        a2 = lookup.a2
        
        aX, pX = None, None
        if "WHITE" in ethnicity:
            aX = 0
            pX = 0
        elif "BLACK" in ethnicity:
            aX = lookup.a3
            pX = lookup.p2
        elif "CHINESE" in ethnicity:
            aX = lookup.a4
            pX = lookup.p3
        else:
            aX = lookup.a6
            pX = 0

        #sex,f,a0,a1,a2,a3,a4,a5,a6,p0,p1,p2,p3,p4,p5,q0,q1,agebound,l0,l1,m0,m1,s0,s1
        #2,FEV1,-9.6987,2.1211,-0.027,-0.1484,-0.0149,-0.1208,-0.0708,-2.3765,0.0972,0.1016,-0.0109,0.0733,0.0114,1.154,0,39,0,0,0.1112,0.1094,-0.0919,-0.0913

        mspline = lookup.m0
        sspline = lookup.s0

        p0 = lookup.p0
        p1 = lookup.p1

        q0 = lookup.q0
        q1 = lookup.q1
        
        m = round(math.exp(a0 + (a1 * math.log(height)) + (a2 * math.log(age)) + aX + mspline), 2)
        s = math.exp(p0 + (p1 * math.log(age)) + pX + sspline)
        l = q0 + (q1 * math.log(age))
        lln = math.exp(math.log(1 - (1.645 * l * s)/ l) + math.log(m))

        results[measure] = {'predicted': m, 'lln': lln}
    
    return results

def get_actual_values(age, sex, height, ethnicity, disease):

    pred = calculate_predicted_values(age, sex, height, ethnicity)

    if disease == "copd":
        fev1_pred = pred['FEV1']['predicted'] 
        fvc_pred = pred['FVC']['predicted'] 
        while True:
            fvc_percent = rng.integers(75, 100)
            fvc = round(fvc_pred * (fvc_percent / 100), 2)
            mu = .72
            sigma = .19
            a,b = get_beta_params(mu, sigma)
            fev1_percent = rng.beta(a,b)
            fev1 = fev1_pred * fev1_percent
            if (fev1 / fvc) < 0.7:
                break
        
        return fev1, fvc, fev1/fvc

    # http://www.jpp.krakow.pl/journal/archive/11_09_s5/articles/13_article.html
    # if lung_disease == 'asthma':
    #     if measure == 'FEV1':
    #         mu = .75
    #         sigma = .19
    #         a,b = get_beta_params(mu, sigma)
    #         reduction = rng.beta(a,b)
    #         actual = m * reduction
    #     elif measure == 'FVC':
    #         mu = .96
    #         sigma = .13
    #         a,b = get_beta_params(mu, sigma)
    #         reduction = rng.beta(a,b)
    #         actual = m * reduction
    #     else:
    #         actual = results['FEV1']['actual'] / results['FVC']['actual']

    # elif lung_disease == 'copd':
    #     if measure == 'FEV1':
    #         mu = .72
    #         sigma = .19
    #         a,b = get_beta_params(mu, sigma)
    #         reduction = rng.beta(a,b)
    #         actual = m * reduction
    #     elif measure == 'FVC':
    #         reduction = rng.integers(75, 100)
    #         actual = m * (reduction / 100)
    #     else:
    #         actual = results['FEV1']['actual'] / results['FVC']['actual']

#print(calculate_predicted_values(70, 'f', 165, 'OTHER', 'copd'))
print(get_actual_values(70, 'f', 165, 'OTHER', 'copd'))
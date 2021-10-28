import pickle
from catboost import CatBoostClassifier
import numpy as np
import pandas as pd
import scipy.stats as stats
from sklearn.linear_model import Ridge

# Load the decision trees for low and high pulse respectively
low_predict = CatBoostClassifier()
low_predict.load_model("models/decision/pulse_low")

high_predict = CatBoostClassifier()
high_predict.load_model("models/decision/pulse_high")

rng: np.random = np.random.default_rng()

def determine_pulse(patient):

    # 'current_smoker', 'aerobically_active','regular_alcohol', 'sex', 'confage', 'mean_sys', 'mean_dias', 'has_dyslipidaemia', 'has_arthritis', 'has_asthma', 'has_mi'
    X = [
        1 if patient['smoking'] == 0 else 1,
        patient['aerobicallyActive'],
        patient['aud'],
        1 if patient['sex'] == 0 else 1,
        patient['age'],
        patient['sbp'],
        patient['dbp'],
        patient['dyslipidaemia'],
        patient['arthritis'],
        patient['asthma'],
        patient['mi'],
    ]

    # Calculate probability of extreme value
    low_prob = low_predict.predict_proba(X)
    high_prob = high_predict.predict_proba(X)

    # Get the high probability
    prob_arr = [low_prob[1], high_prob[1]]
    final_prob = np.amax(prob_arr)

    # 0 if low 1 if high
    final_index = np.where(prob_arr == np.amax(prob_arr))[0][0]

    if rng.random() < final_prob: # Extreme pulse likely
        if final_index == 0: # Sample from low truncated normal
            dist = stats.truncnorm((36.333333 - 54.034514) / 4.413900, (59.666667 - 54.034514) / 4.413900, loc=54.034514, scale=4.413900)
            hr = round(dist.rvs(1)[0])
            return hr
        else: # Sample from high truncated normal
            dist = stats.truncnorm((78.333333 - 85.262911) / 6.671939, (117.333333 - 85.262911) / 6.671939, loc=85.262911, scale=6.671939)
            hr = round(dist.rvs(1)[0])
            return hr
    else:
        """
        alpha = 10.0
        RMSE = 10.340662220153831
        count  543.000000
        mean    67.077972
        std      4.180595
        min     53.374300
        25%     64.181216
        50%     66.933231
        75%     69.811993
        max     81.824288
        Index(['current_smoker', 'aerobically_active', 'regular_alcohol', 'sex',
       'confage', 'mean_sys', 'mean_dias', 'has_arthritis', 'has_asthma',
       'has_stroke', 'has_mi', 'has_dementia'],
      dtype='object')
        """
        X = [
            1 if patient['smoking'] == 0 else 1,
            patient['aerobicallyActive'],
            patient['aud'],
            1 if patient['sex'] == 0 else 1,
            patient['age'],
            patient['sbp'],
            patient['dbp'],
            patient['arthritis'],
            patient['asthma'],
            patient['stroke'],
            patient['mi'], 
            patient['dementia']
        ]
        load_ridge_model: Ridge = pickle.load(open('models/ridge/pulse.sav', 'rb'))
        X_pred = pd.DataFrame([X], columns=['current_smoker', 'aerobically_active', 'regular_alcohol', 'sex',
       'confage', 'mean_sys', 'mean_dias', 'has_arthritis', 'has_asthma',
       'has_stroke', 'has_mi', 'has_dementia'])
        hr = round(load_ridge_model.predict(X_pred)[0])
        return hr

# patient = {
#    'smoking': 1,
#    'aerobicallyActive': 1,
#    'aud': 0,
#    'sex': 0,
#    'age': 65,
#    'sbp': 110,
#    'dbp': 80,
#    'dyslipidaemia': 0,
#    'arthritis': 0,
#    'asthma': 0,
#    'mi': 1, 
#    'dementia': 0,
#    'stroke': 0
# }

# sample = []

# for i in range(1000):
#     sample.append(determine_pulse(patient))

# print(pd.DataFrame(sample).describe())
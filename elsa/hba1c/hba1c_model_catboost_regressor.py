import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
from catboost import CatBoostRegressor, Pool, cv
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

df = pd.read_csv('elsa/hba1c/hba1c_model_wrangle.csv')

df['poorly_controlled'] = np.where((df['hba1c'] >= 6.5) & (df['has_diabetes'] == 1), 1, 0)

X, y = df.loc[(df['has_diabetes'] == 1), (df.columns != 'hba1c') & (df.columns != 'has_diabetes') & (df.columns != 'mean_dias') & (df.columns != 'has_hypertension') & (df.columns != 'taking_beta_blocker') & (df.columns != 'has_dyslipidaemia') & (df.columns != 'has_dementia') & (df.columns != 'has_arrhythmia') & (df.columns != 'current_smoker') & (df.columns != 'anxiety_stress')], df[(df['has_diabetes'] == 1)]['poorly_controlled']

#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

params = {"iterations": 100,
          "depth": 10,
         'loss_function': 'CrossEntropy',
    'eval_metric': 'AUC',
          "od_type": "Iter",
          "verbose": False}

cv_dataset = Pool(data=X,
                  label=y)

scores, models = cv(cv_dataset,
            params,
            return_models=True,
            fold_count=10)

print(scores)

# grid = {'learning_rate': [0.03, 0.1, 1],
#         'depth': [4, 6, 8, 10],
#         'l2_leaf_reg': [1, 3, 5, 7, 9]}

# grid_search_result = model.grid_search(grid,
#                                        X=X_train,
#                                        y=y_train,
#                                        plot=True)


# print(grid_search_result['params'])

# models.fit(X_train, y_train)

#y_pred = models[-1].predict(X)

#print(models[-1].get_feature_importance(prettified=True))



# print((math.sqrt(mean_squared_error(y, y_pred)) + 46.7) / 28.7)

# plt.figure(figsize=(10,10))
# plt.scatter(y, y_pred, c='crimson')

# p1 = max(max(y_pred), max(y))
# p2 = min(min(y_pred), min(y))
# plt.plot([p1, p2], [p1, p2])
# plt.xlabel('True Values', fontsize=15)
# plt.ylabel('Predictions', fontsize=15)
# plt.axis('equal')
# plt.show()
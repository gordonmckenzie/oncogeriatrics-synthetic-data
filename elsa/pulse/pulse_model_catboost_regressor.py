import pandas as pd
import math
import matplotlib.pyplot as plt
from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

df = pd.read_csv('elsa/pulse/pulse_model_wrangle.csv')

X, y = df.loc[:, (df.columns != 'mean_pulse') & (df.columns != 'taking_beta_blocker') & (df.columns != 'anxiety_stress')], df['mean_pulse']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

model = CatBoostRegressor(iterations=100,
                        depth=4,
                        learning_rate=1,
                        l2_leaf_reg=5,
                        od_type='Iter',
                        loss_function='RMSE'
                        )

# grid = {'learning_rate': [0.03, 0.1, 1],
#         'depth': [4, 6, 8, 10],
#         'l2_leaf_reg': [1, 3, 5, 7, 9]}

# grid_search_result = model.grid_search(grid,
#                                        X=X_train,
#                                        y=y_train,
#                                        plot=True)


#print(grid_search_result['params'])

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print(model.get_feature_importance(prettified=True))

print(math.sqrt(mean_squared_error(y_test, y_pred)))

plt.figure(figsize=(10,10))
plt.scatter(y_test, y_pred, c='crimson')

p1 = max(max(y_pred), max(y_test))
p2 = min(min(y_pred), min(y_test))
plt.plot([p1, p2], [p1, p2], 'b-')
plt.xlabel('True Values', fontsize=15)
plt.ylabel('Predictions', fontsize=15)
plt.axis('equal')
plt.show()
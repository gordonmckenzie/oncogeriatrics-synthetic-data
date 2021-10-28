import pandas as pd
import math
import matplotlib.pyplot as plt
from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

df = pd.read_csv('elsa/bp_model_wrangle.csv')

X, y = df.loc[:, (df.columns != 'mean_dias') & (df.columns != 'mean_sys') & (df.columns != 'has_hypertension') & (df.columns != 'anxiety_stress') & (df.columns != 'degree_educated') & (df.columns != 'ethnic')], df['mean_dias']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

model = CatBoostRegressor(iterations=100,
                          learning_rate=1,
                          depth=6,
                          loss_function='RMSE',
                          )

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

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
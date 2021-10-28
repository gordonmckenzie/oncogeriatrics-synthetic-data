import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_validate, train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

df = pd.read_csv('elsa/bp_model_wrangle.csv')

X, y = df.loc[:, (df.columns != 'mean_sys') & (df.columns != 'mean_dias') & (df.columns != 'has_hypertension') & (df.columns != 'anxiety_stress') & (df.columns != 'degree_educated') & (df.columns != 'ethnic')], df['mean_sys']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

linreg = LinearRegression()

scoring = "neg_root_mean_squared_error"
linscores = cross_validate(linreg, X_train, y_train, scoring=scoring, return_estimator=True)

print("Linear regression score:", -linscores["test_score"].mean())
print(linscores["estimator"][0].intercept_, linscores["estimator"][-1].coef_)

# plt.plot(X, y)
# plt.plot(X, linscores["estimator"][0].predict(X))
# plt.ylim(0,2)
# plt.xlabel("x")
# plt.ylabel("y")
# plt.show()

# Retrain the model and evaluate
import sklearn
linreg = sklearn.base.clone(linreg)
linreg.fit(X_train, y_train)
print("Test set RMSE:", mean_squared_error(y_test, linreg.predict(X_test), squared=False))
print("Mean validation RMSE:", -linscores["test_score"].mean())
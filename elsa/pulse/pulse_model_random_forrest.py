import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_validate, train_test_split
from sklearn.ensemble import RandomForestRegressor

df = pd.read_csv('elsa/pulse/pulse_model_wrangle.csv')

X, y = df.loc[:, (df.columns != 'mean_pulse') & (df.columns != 'taking_beta_blocker') & (df.columns != 'anxiety_stress')], df['mean_pulse']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

regr = RandomForestRegressor(max_depth=5, random_state=0)

regr.fit(X_train, y_train)

print(regr.feature_importances_)

#y_pred = regr.predict(X_test)

print(regr.score(X_test, y_test))

#linreg = LinearRegression()

#scoring = "neg_root_mean_squared_error"
#linscores = cross_validate(linreg, X_train, y_train, scoring=scoring, return_estimator=True)
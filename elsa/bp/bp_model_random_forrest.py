import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_validate, train_test_split
from sklearn.ensemble import RandomForestRegressor

df = pd.read_csv('elsa/bp_model_wrangle.csv')

X, y = df.loc[:, df.columns != 'mean_sys'], df['mean_sys']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

regr = RandomForestRegressor(max_depth=5, random_state=0)
regr.fit(X_train, y_train)

#linreg = LinearRegression()

#scoring = "neg_root_mean_squared_error"
#linscores = cross_validate(linreg, X_train, y_train, scoring=scoring, return_estimator=True)
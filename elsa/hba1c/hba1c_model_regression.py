import math
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import ElasticNetCV, HuberRegressor, LinearRegression, Ridge, RidgeCV, SGDRegressor, ElasticNet, PassiveAggressiveRegressor
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.svm import LinearSVR
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.model_selection import cross_val_predict, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.compose import TransformedTargetRegressor, make_column_transformer
from sklearn.model_selection import cross_validate, RepeatedKFold, cross_val_score
from sklearn.linear_model import LassoCV
import numpy as np
import pickle

"""
https://scikit-learn.org/stable/auto_examples/inspection/plot_linear_model_coefficient_interpretation.html#sphx-glr-auto-examples-inspection-plot-linear-model-coefficient-interpretation-py
"""

df = pd.read_csv('elsa/hba1c/hba1c_model_wrangle.csv')

X, y = df.loc[(df['has_diabetes'] == 1), (df.columns != 'hba1c') & (df.columns != 'has_diabetes') & (df.columns != 'has_hypertension') & (df.columns != 'taking_beta_blocker') & (df.columns != 'has_dyslipidaemia') & (df.columns != 'has_dementia') & (df.columns != 'has_arrhythmia') & (df.columns != 'current_smoker') & (df.columns != 'anxiety_stress')], df[(df['has_diabetes'] == 1)]['hba1c']

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

# preprocessor = make_column_transformer(
#     (StandardScaler(), ['confage', 'mean_sys', 'mean_dias']),
#     remainder="passthrough",
# )

# model = make_pipeline(
#     preprocessor,
#     TransformedTargetRegressor(
#         regressor=Ridge(alpha=1e-10)
#     )
# )

# Heatmap for co-linearity
# sns.heatmap(X.corr(), cmap="RdYlBu", annot=True)
# plt.show()

# Boxplot for outliers
# sns.boxplot(data=X, orient="h", palette="Set2")
# plt.show()

#Variance inflation factor sideally < 10
# vif = pd.DataFrame()
# vif["features"] = X.columns
# vif["vif_Factor"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
# print(vif)

# Huber = HuberRegressor()
# Linear = LinearRegression()
# SGD = SGDRegressor()
# Ridge = Ridge()
# SVR = LinearSVR()
# Elastic = ElasticNet(random_state=0)
# PassiveAggressiveRegressor = PassiveAggressiveRegressor()
# estimators = [Linear, SGD, SVR, Huber, Ridge, Elastic, PassiveAggressiveRegressor]

# for i in estimators:
#     scores = cross_val_score(i, X, y, cv=10)
#     #scores = i.fit(X,y)
#     #y_pred = i.predict(X_test)
#     #print(f"{str(i)}: {math.sqrt(mean_squared_error(y_test, y_pred))}")
#     print(f"{i}: {scores.mean()}, {scores.std()}")


# train_dataset = X_train[["confage", "mean_sys", "mean_dias"]].copy()
# train_dataset.insert(0, "PULSE", y_train)
# sns.pairplot(train_dataset, kind="reg", diag_kind="kde")
# plt.show()

# model = Ridge(alpha=1e-10)
#model.fit(X_train, y_train)

# Coefficient importance
# coefs = pd.DataFrame(
#     model.coef_
#     * X_train.std(axis=0),
#     columns=["Coefficient importance"],
#     index=X_train.columns,
# )
# coefs.plot(kind="barh", figsize=(9, 7))
# plt.title("Ridge model, small regularization")
# plt.axvline(x=0, color=".5")
# plt.subplots_adjust(left=0.3)
# plt.show()

# cv_model = cross_validate(
#     model,
#     X_train,
#     y_train,
#     cv=RepeatedKFold(n_splits=5, n_repeats=5),
#     return_estimator=True,
#     n_jobs=-1,
# )
# coefs = pd.DataFrame(
#     [
#         est.named_steps["transformedtargetregressor"].regressor_.coef_ #est.coef_
#         * X_train.std(axis=0)
#         for est in cv_model["estimator"]
#     ],
#     columns=X_train.columns,
# )
# plt.figure(figsize=(9, 7))
# sns.stripplot(data=coefs, orient="h", color="k", alpha=0.5)
# sns.boxplot(data=coefs, orient="h", color="cyan", saturation=0.5)
# plt.axvline(x=0, color=".5")
# plt.xlabel("Coefficient importance")
# plt.title("Coefficient importance and its variability")
# plt.subplots_adjust(left=0.3)
# plt.show()

model = PassiveAggressiveRegressor()
#reg: Elastic = Elastic.fit(X,y)
#y_pred = Elastic.predict(X_test)

# model = make_pipeline(
#     TransformedTargetRegressor(
#         regressor=ElasticNetCV(alphas=np.logspace(-10, 10, 21)),
#     ),
# )
# scores = cross_val_score(model, X, y, cv=10)
# #model.fit(X_train, y_train)
# print(f"{scores.mean()}, {scores.std()}")

#y_pred = model.predict(X_test)
#print(math.sqrt(mean_squared_error(y_test, y_pred)))
#print(pd.DataFrame(y_pred).describe())
#print(X_train.columns)
#pickle.dump(model, open('models/ridge/pulse.sav', 'wb'))

predicted = cross_val_predict(model, X, y, cv=10)

fig, ax = plt.subplots()
ax.scatter(y, predicted, edgecolors=(0, 0, 0))
ax.plot([y.min(), y.max()], [y.min(), y.max()], "k--", lw=4)
print(math.sqrt(mean_squared_error(y, predicted)))
ax.set_xlabel("Measured")
ax.set_ylabel("Predicted")
plt.show()
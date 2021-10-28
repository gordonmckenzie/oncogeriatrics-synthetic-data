"""
KEY PAPER: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0240370
"""
import pandas as pd
import matplotlib.pyplot as plt
from catboost import CatBoostClassifier
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.metrics import RocCurveDisplay
from imblearn.over_sampling import SMOTE

df = pd.read_csv('elsa/bp/bp_model_wrangle.csv')

X, y = df.loc[:, (df.columns != 'has_hypertension') & (df.columns != 'mean_dias') & (df.columns != 'mean_sys') & (df.columns != 'anxiety_stress') & (df.columns != 'degree_educated') & (df.columns != 'ethnic') ], df['has_hypertension']

oversample = SMOTE()
X, y = oversample.fit_resample(X, y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

model = CatBoostClassifier(iterations=100,
                           learning_rate=1,
                           depth=8)

model.fit(X_train, y_train)

model.set_feature_names(X.columns)

print(model.get_feature_importance(prettified=True))

y_pred = model.predict(X_test)

#print(y_test)

#model.save_model('models/decision/hypertension')

fpr, tpr, thresholds = metrics.roc_curve(y_test, y_pred, pos_label=1)

print(metrics.auc(fpr, tpr))
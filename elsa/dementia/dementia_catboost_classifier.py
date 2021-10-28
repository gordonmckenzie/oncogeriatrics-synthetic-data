# Feature selection https://pubmed.ncbi.nlm.nih.gov/34070100/
import pandas as pd
import matplotlib.pyplot as plt
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
from imblearn.over_sampling import SMOTE

df = pd.read_csv('elsa/dementia/dementia_model_wrangle.csv')

X, y = df.loc[:, (df.columns != 'has_dementia') & (df.columns != 'married') & (df.columns != 'degree_educated') ], df['has_dementia']

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

fpr, tpr, thresholds = metrics.roc_curve(y_test, y_pred, pos_label=1)

print(metrics.auc(fpr, tpr))

#RocCurveDisplay.from_predictions(y_test, y_pred)
#plt.show()
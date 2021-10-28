
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
#from sklearn.metrics import auc, roc_curve
from sklearn import metrics
from imblearn.over_sampling import SMOTE
from scipy import interp
from itertools import cycle

df = pd.read_csv('elsa/pulse/pulse_model_wrangle.csv')

# Create models by varying distirbutions <78 ideal for all cause mortality https://pubmed.ncbi.nlm.nih.gov/21109916/
def create_category(x):
    if x >= 60:
        return 0
    else:
        return 1

df["rhr"] = df["mean_pulse"].apply(create_category)

X, y = df.loc[:, 
    (df.columns != 'mean_pulse') & 
    (df.columns != 'rhr') &
    (df.columns != 'taking_beta_blocker') & 
    (df.columns != 'anxiety_stress') & 
    # (df.columns != 'has_dyslipidaemia') & 
    (df.columns != 'has_diabetes') & 
    (df.columns != 'has_hypertension') &
    (df.columns != 'has_stroke') &
    (df.columns != 'has_dementia') &
    # (df.columns != 'has_mi') &
    (df.columns != 'has_arrhythmia')
], df['rhr']

#print(df[df["mean_pulse"] > 100])

oversample = SMOTE()
X, y = oversample.fit_resample(X, y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

model = CatBoostClassifier(iterations=100,
                           learning_rate=1,
                           od_type='Iter',
                           depth=8)

model.fit(X_train, y_train)

model.set_feature_names(X.columns)

print(model.get_feature_importance(prettified=True))

y_pred = model.predict(X_test)

# roc curve for classes
# fpr = {}
# tpr = {}
# thresh = {}

fpr, tpr, thresholds = metrics.roc_curve(y_test, y_pred, pos_label=1)

print(metrics.auc(fpr, tpr))

model.save_model('models/decision/pulse_low')

# n_classes = 3

# for i in range(n_classes):    
#     fpr[i], tpr[i], thresh[i] = roc_curve(y_test, y_pred, pos_label=i)
    
# # plotting    
# plt.plot(fpr[0], tpr[0], linestyle='--',color='orange', label='Class 0 vs Rest ROC curve (area = %0.2f)' % auc(fpr[0], tpr[0]))
# plt.plot(fpr[1], tpr[1], linestyle='--',color='green', label='Class 1 vs Rest ROC curve (area = %0.2f)' % auc(fpr[1], tpr[1]))
# plt.plot(fpr[2], tpr[2], linestyle='--',color='blue', label='Class 2 vs Rest ROC curve (area = %0.2f)' % auc(fpr[2], tpr[2]))
# plt.title('Multiclass ROC curve')
# plt.xlabel('False Positive Rate')
# plt.ylabel('True Positive rate')
# plt.legend(loc='best')
# plt.show()
#plt.savefig('Multiclass ROC',dpi=300);    

#RocCurveDisplay.from_predictions(y_test, y_pred)
#plt.show()
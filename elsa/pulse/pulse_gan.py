from sdv.tabular import CTGAN
from sdv.constraints import ColumnFormula, Between, CustomConstraint
import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE

df = pd.read_csv('elsa/pulse/pulse_model_wrangle.csv')

def pulse_status(x):
    if x < 60:
        return 'low'
    elif x >= 60 and x < 78:
        return 'normal'
    else:
        return 'high'

df["pulse_status"] = df["mean_pulse"].apply(pulse_status)

model = CTGAN(rounding=1)
model.fit(df[["mean_pulse", "pulse_status"]])

model.save('models/gans/pulse.pkl')

loaded: CTGAN = CTGAN.load('models/gans/pulse.pkl')

new_data = model.sample(1000)
low = model.sample(1000, conditions={'pulse_status': 'low'})
normal = model.sample(1000, conditions={'pulse_status': 'normal'})
high = model.sample(1000, conditions={'pulse_status': 'high'})

print(low.describe())
print(normal.describe())
print(high.describe())
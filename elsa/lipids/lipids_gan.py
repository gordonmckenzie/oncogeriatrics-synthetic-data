from sdv.tabular import CTGAN
from sdv.constraints import ColumnFormula, Between, CustomConstraint
import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE

df = pd.read_csv('elsa/lipids/lipid_model_wrangle.csv')

def convert_to_bool(x):
    return True if x == 1 else False

#df["has_dyslipidaemia"] = df["has_dyslipidaemia"].apply(convert_to_bool)
#print(df[["chol", "hdl", "ldl", "trig", "has_dyslipidaemia"]].describe())

oversample = SMOTE()
X, y = oversample.fit_resample(df[["chol", "hdl", "ldl", "trig"]], df["has_dyslipidaemia"])

y = pd.DataFrame(y)

y.columns = ['has_dyslipidaemia']

data = pd.concat([X, y], axis=1)

data['has_dyslipidaemia'].astype(int)

#print(data[data['has_dyslipidaemia'] == 0].describe())

data = df[df['has_dyslipidaemia'] == 1][["chol","hdl","trig","ldl"]]

# print(data)
# def tc_hdl(_data):
#     return _data['chol'] / _data['hdl']

# tc_hdl_constraint = ColumnFormula(
#     column='tc:hdl',
#     formula=tc_hdl,
#     handling_strategy='transform')

# def non_hdl(_data):
#     return _data['chol'] - _data['hdl']

# non_hdl_constraint = ColumnFormula(
#     column='non_hdl',
#     formula=non_hdl,
#     handling_strategy='transform')


# normal_chol = Between(column='chol',low=data["chol"].min(),high=data["chol"].max(),handling_strategy='transform')
# normal_hdl = Between(column='hdl',low=data["ldl"].min(),high=data["hdl"].max(),handling_strategy='transform')
# normal_trig = Between(column='trig',low=data["trig"].min(),high=data["trig"].max(),handling_strategy='transform')
# normal_ldl = Between(column='ldl',low=data["ldl"].min(),high=data["ldl"].max(),handling_strategy='transform')

# constraints = [
#     normal_chol,
#     normal_hdl,
#     normal_trig,
#     normal_ldl 
# ]

# def is_valid(table_data, column):
#     does_not_have_dyslipidaemia = table_data.has_dyslipidaemia == 0
#     valid = does_not_have_dyslipidaemia and (table_data[column] < 5)
#     return valid

# constraint = CustomConstraint(
#     columns=['chol'],
#     is_valid=is_valid
# )

#model = CTGAN(rounding=0, constraints=[constraint])

model = CTGAN(rounding=1)
model.fit(data)

model.save('models/gans/dyslipidaemia.pkl')

loaded: CTGAN = CTGAN.load('models/gans/dyslipidaemia.pkl')

new_data = model.sample(1000)
# dyslipidaemia = model.sample(1000, conditions={'has_dyslipidaemia': True})
# no_dyslipidaemia = model.sample(1000, conditions={'has_dyslipidaemia': False})

print(new_data.describe())
# print(dyslipidaemia.describe())
# print(no_dyslipidaemia.describe())
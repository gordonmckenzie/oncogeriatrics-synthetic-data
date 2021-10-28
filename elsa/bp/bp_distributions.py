import pandas as pd

df = pd.read_csv('elsa/bp_model_wrangle.csv')

df_htn = df[(df["mean_sys"] >= 140) | (df["mean_dias"] >= 90)]

df_normo = df[(df["mean_sys"] < 140) & (df["mean_dias"] < 90)]

age_groups = pd.cut(df_htn['confage'], bins=[65, 70, 75, 80, 85, 90])
age_grouped_htn_sys = df_htn.groupby(['sex', age_groups]).agg({'mean_sys': ['mean', 'std']})

age_groups = pd.cut(df_normo['confage'], bins=[65, 70, 75, 80, 85, 90])
age_grouped_normo_sys = df_normo.groupby(['sex', age_groups]).agg({'mean_sys': ['mean', 'std']})

print(age_grouped_htn_sys)
print(age_grouped_normo_sys)

age_groups = pd.cut(df_htn['confage'], bins=[65, 70, 75, 80, 85, 90])
age_grouped_htn_dias = df_htn.groupby(['sex', age_groups]).agg({'mean_dias': ['mean', 'std']})

age_groups = pd.cut(df_normo['confage'], bins=[65, 70, 75, 80, 85, 90])
age_grouped_normo_dias = df_normo.groupby(['sex', age_groups]).agg({'mean_dias': ['mean', 'std']})

print(age_grouped_htn_dias)
print(age_grouped_normo_dias)
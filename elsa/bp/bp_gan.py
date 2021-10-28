"""
KEY PAPER FOR TABULAR GANS - https://arxiv.org/pdf/1907.00503.pdf
TAKE A LOOK AT table-evaluator as well for evaluation
"""
# https://sdv.dev/SDV/user_guides/single_table/models.html
# https://pubmed.ncbi.nlm.nih.gov/34603366/ - using GANs for digital twin (https://github.com/pietrobarbiero/digital-patient/blob/master/examples/plot_data_pca.py)

from sdv.tabular import CTGAN, CopulaGAN
from sdv.constraints import ColumnFormula, Between, CustomConstraint
#from ctgan import CTGANSynthesizer
import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE

df = pd.read_csv('elsa/bp/bp_model_wrangle.csv')

df["has_hypertension"] = np.where((df["mean_sys"] >= 140) | (df["mean_dias"] >= 90), 1, 0)

#print(df[["mean_sys", "mean_dias", "has_hypertension"]].describe())

data = df[(df["mean_sys"] >= 140) | (df["mean_dias"] >= 90)][["mean_sys", "mean_dias"]]

# oversample = SMOTE()
# X, y = oversample.fit_resample(df[["mean_sys", "mean_dias"]], df["has_hypertension"])

# y = pd.DataFrame(y)

# y.columns = ["has_hypertension"]

# data = pd.concat([X, y], axis=1)

hypertension_metadata = {
        "fields": {
            "mean_sys": {
                "type": "numerical", "subtype": "integer",
            },
            "mean_dias": {
                "type": "numerical", "subtype": "integer",
            }
        }
    }

model = CTGAN(rounding=0, table_metadata=hypertension_metadata)

model.fit(data)

model.save('models/gans/hypertension.pkl')

loaded: CTGAN = model.load('models/gans/hypertension.pkl')

sample = loaded.sample(1000)
# no_htn = loaded.sample(1000, conditions={'has_hypertension': 0})

print(sample.describe())
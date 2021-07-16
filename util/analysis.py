import numpy as np
import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import yaml
import statsmodels.stats.api as sm
from itertools import groupby
import matplotlib.pyplot as plt
from matplotlib_venn import venn3_unweighted

sns.set_theme()
sns.set_color_codes("pastel")

epidemiology = []
with open("data/epidemiology.yaml", 'r') as stream:
    epidemiology = yaml.safe_load(stream)

config = []
with open("config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

class Analysis():
    def __init__(self, population):
        self.pop = pd.DataFrame(population)
    
    def sampleSize(self):
        return len(self.pop)

    def ageStats(self):
        #mean, median, range [ll,ull]
        return self.pop.mean(axis=0)[1], self.pop.median(axis=0)[1], [self.pop.min(axis=0)[1], self.pop.max(axis=0)[1]]
    
    def genderBalance(self):
        return self.pop['gender'].value_counts(normalize=True).iloc[0]

    def cancerPrevalence(self):
        return self.pop['cancer_site'].value_counts(normalize=True)

    def anthropometrics(self):
        return (
            ('Height (mean, cm)', self.pop['height'].mean()),
            ('Weight (mean, kg)', self.pop['weight'].mean()),
            ('Body mass index (mean)', self.pop['bmi'].mean())
        )
    
    def creatinineMean(self):
        return self.pop['cr'].mean()

    def srhMean(self):
        return self.pop['self_reported_health'].mean()

    def tugMean(self):
        return self.pop['tug'].mean()

    def frailtyMean(self):
        return self.pop['frailty'].mean()

    def riskFactorPrevalence(self, factors=[]):
        prevalence = []
        for factor in factors:
            prevalence.append(f"{round(self.pop[factor].mean(), 1)} ({round(self.pop[factor].quantile(0.025))}-{round(self.pop[factor].quantile(0.975))})")
        return prevalence

    def plotExpectedPrevalence(self):

        # Get all conditions from epidemiology.yaml and average by age
        conditions = []

        for epi in epidemiology:
            for e,v in epi["geriatricVulnerabilities"].items():
                conditions.append({'condition': e, 'value': ((v['m'] + v['f']) / 2) })

        def key_func(k): 
            return k['condition']
        
        # Sort conditions within the array
        conditions = sorted(conditions, key=key_func)
        
        data = []

        def checkHasPrettyString(key):
            return True if key in config['pretty-condition-strings'] else False

        def getPrettyString(key):
            return config['pretty-condition-strings'][key] if key in config['pretty-condition-strings'] else key

        # Iterate over all conditions 
        fig = go.Figure()
        x_expected = []
        x_simulated = []
        y_expected = []
        y_simulated = []
        err_expected = []
        err_expected_minus = []
        err_simulated = []
        err_simulated_minus = []
        for key, value in groupby(conditions, key_func):
            if checkHasPrettyString(key):
                vals_list = list(value)
                vals = 0
                for v in vals_list:
                    vals += float(v['value'])
                mean = vals / len(vals_list)
                ll, ul = sm.proportion_confint(vals, len(vals_list)*100, method='wilson')
                y_expected.append(getPrettyString(key))
                y_simulated.append(getPrettyString(key))
                x_expected.append(round(mean, 1))
                x_simulated.append(round(self.pop[key].mean()*100, 1))
                err_expected.append(ul)
                err_expected_minus.append(ll)
                err_simulated.append(self.pop[key].quantile(0.975))
                err_simulated_minus.append(self.pop[key].quantile(0.025))
              
        fig.add_trace(go.Bar(
            name='Expected',
            y=y_expected, 
            x=x_expected,
            orientation='h',
            error_x=dict(
                type='data',
                symmetric=False,
                array=err_expected,
                arrayminus=err_expected_minus)
            )
        )
        fig.add_trace(go.Bar(
            name='Simulated',
            y=y_simulated, 
            x=x_simulated,
            orientation='h',
            error_x=dict(
                type='data',
                symmetric=False,
                array=err_simulated,
                arrayminus=err_simulated_minus)
            )
        )
        fig.update_layout(barmode='group', yaxis=dict(
        title='Variable',
        tickmode='linear'), xaxis=dict(
        title='Prevalence (%)', automargin=True))
        fig.write_image("results/plots/prevalence_expected.png")

    # Relationships between frailty, disability and multimorbidity...
    def FDM(self):
        plt.clf()
        df = self.pop

        venn3_unweighted(subsets = (
            str(round(len(df[(df['badlImpairment'] == 1) & (df['multimorbidity'] == 0) & (df['frailty'] == 0)]) / len(df), 1)*100)+"%", # D
            str(round(len(df[(df['badlImpairment'] == 0) & (df['multimorbidity'] == 0) & (df['frailty'] == 1)]) / len(df), 1)*100)+"%", # F
            str(round(len(df[(df['badlImpairment'] == 1) & (df['multimorbidity'] == 0) & (df['frailty'] == 1)]) / len(df), 1)*100)+"%", # DF
            str(round(len(df[(df['badlImpairment'] == 0) & (df['multimorbidity'] == 1) & (df['frailty'] == 0)]) / len(df), 1)*100)+"%", # M
            str(round(len(df[(df['badlImpairment'] == 1) & (df['multimorbidity'] == 1) & (df['frailty'] == 0)]) / len(df), 1)*100)+"%", # DM
            str(round(len(df[(df['badlImpairment'] == 0) & (df['multimorbidity'] == 1) & (df['frailty'] == 1)]) / len(df), 1)*100)+"%", # MF
            str(round(len(df[(df['badlImpairment'] == 1) & (df['multimorbidity'] == 1) & (df['frailty'] == 1)]) / len(df), 1)*100)+"%" # DFM
        ), set_labels = ('Disability', 'Frailty', 'Multimorbidity'), set_colors=('grey', 'grey', 'grey', 'grey'), alpha = 0.5)

        plt.savefig(f"results/plots/fdm.png")

    def bmiActivityPlot(self):
        
        plt.clf()
        df = self.pop

        data = dict(values=[
            round(len(df[(df['bmi'] >= 25) & (df['bmi'] < 30)]) / len(df) * 100, 1), # Overweight
            round(len(df[(df['bmi'] >= 18.5) & (df['bmi'] < 25)]) / len(df) * 100, 1), # Normal
            round(len(df[df['bmi'] >= 30]) / len(df) * 100, 1), # Obese
            round(len(df[(df['bmi'] >= 18.5) & (df['bmi'] < 25) & (df['aerobicallyActive'] == 1)]) / len(df) * 100, 1), # Normal weight and active
            round(len(df[(df['bmi'] >= 25) & (df['bmi'] < 30) & (df['aerobicallyActive'] == 1)]) / len(df) * 100, 1), # Overweight and active
            round(len(df[df['bmi'] < 18.5]) / len(df) * 100, 1), # Underweight
            round(len(df[(df['bmi'] < 18.5) & (df['aerobicallyActive'] == 1)]) / len(df) * 100, 1), # Underweight and active
            round(len(df[(df['bmi'] > 30) & (df['aerobicallyActive'] == 1)]) / len(df) * 100, 1) # Obese and active
        ], labels=['Overweight', 'Normal', 'Obese', 'Normal weight and active', 'Overweight and active', 'Underweight', 'Underweight and active', 'Obese and active'])
        
        fig = px.funnel(data, y='labels', x='values')
        fig.write_image("results/plots/funnel.png")

    # Calculates diagnostic accuracy of a test given 2x2 matrix
    def calculateAccuracy(self, tp, tn, fp, fn):
        sensitivity = tp / (tp + fn)
        specificity = tn / (tn + fp)
        positive_likelihood = sensitivity / (1 - specificity)
        negative_likelihood = (1 - sensitivity) / specificity if specificity != 0 else 0
        false_positive_rate = 1 - specificity
        false_negative_rate = 1 - sensitivity
        positive_predictive_value = tp / (tp + fp) if (tp + fp) != 0 else 0
        negative_predictive_value = tn / (tn + fn) if (tn + fn) != 0 else 0
        precision = positive_predictive_value
        recall = sensitivity
        f1 = (2 * precision * recall) / (precision + recall)

        performance = {}
        performance['sensitivity'] = sensitivity
        performance['specificity'] = specificity
        performance['positive_likelihood'] = positive_likelihood
        performance['negative_likelihood'] = negative_likelihood
        performance['false_positive_rate'] = false_positive_rate
        performance['false_negative_rate'] = false_negative_rate
        performance['positive_predictive_value'] = positive_predictive_value
        performance['negative_predictive_value'] = negative_predictive_value
        performance['precision'] = precision
        performance['recall'] = recall
        performance['f1'] = f1

        return performance

    def efiMeans(self):
        return self.pop['efi_classification'].value_counts() / self.pop['efi_classification'].value_counts() * 100

    def efiAccuracy(self):
        df = self.pop

        tp = len(df[(df['efi'] >= 0.13) & (df['frailty'] == 1)])
        fn = len(df[(df['efi'] < 0.13) & (df['frailty'] == 1)])
        fp = len(df[(df['efi'] >= 0.13) & (df['frailty'] == 0)])
        tn = len(df[(df['efi'] < 0.13) & (df['frailty'] == 0)])

        return self.calculateAccuracy(tp, tn, fp, fn)

    def tugAnalysis(self):
        df = self.pop

        tp = len(df[(df['tug'] >= 10) & (df['frailty'] == 1)])
        fn = len(df[(df['tug'] < 10) & (df['frailty'] == 1)])
        fp = len(df[(df['tug'] >= 10) & (df['frailty'] == 0)])
        tn = len(df[(df['tug'] < 10) & (df['frailty'] == 0)])

        return self.calculateAccuracy(tp, tn, fp, fn)

    def outcomeStats(self):

        outcomes = {}

        for k,v in config['pretty-outcome-strings'].items():
            outcomes[v] = f'{round(self.pop[k].mean(), 1) * 100} ({round(self.pop[k].quantile(0.025)) * 100}-{round(self.pop[k].quantile(0.975)) * 100})'

        return outcomes
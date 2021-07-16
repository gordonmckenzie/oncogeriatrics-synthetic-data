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

        # Create grouped horizontal bar plot with custom error bars using matplotlib styled with Seaborn
        def grouped_barplot(df, cat, subcat, val, err1, err2):
            plt.clf()
            """
            u = df[cat].unique()
            y = np.arange(len(u))
            subx = df[subcat].unique()
            offsets = (np.arange(len(subx))-np.arange(len(subx)).mean())/(len(subx))
            height = np.diff(offsets).mean()
            for i,gr in enumerate(subx):
                dfg = df[df[subcat] == gr]
                plt.barh(y+offsets[i], dfg[val].values, height=height,
                        label=gr, xerr=[dfg[err1].values, dfg[err2].values], capsize=2.)
            plt.xlabel(val)
            plt.ylabel(cat)
            plt.yticks(y, u)
            plt.legend()
            plt.savefig(f"results/plots/prevalence_expected.png", bbox_inches='tight')
            """
            fig = go.Figure()
            u = df[cat].unique()
            y = np.arange(len(u))
            subx = df[subcat].unique()
            for _,gr in enumerate(subx):
                dfg = df[df[subcat] == gr]
                fig.add_trace(go.Bar(
                    name=gr,
                    x=dfg[val].values, y=y,
                    orientation='h',
                    error_x=dict(type='data', array=[dfg[err1].values, dfg[err2].values])
                ))
            fig.update_layout(barmode='group')
            fig.write_image("results/plots/prevalence_expected.png")

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
        for key, value in groupby(conditions, key_func):
            if checkHasPrettyString(key):
                vals_list = list(value)
                vals = 0
                for v in vals_list:
                    vals += float(v['value'])
                mean = vals / len(vals_list)
                ll, ul = sm.proportion_confint(vals, len(vals_list)*100, method='wilson')
                data.append({"Type": "Expected", "Risk factor": getPrettyString(key), "Prevalence (%)": round(mean, 1), "ci_ll": ll, "ci_ul": ul})
                data.append({"Type": "Simulated", "Risk factor": getPrettyString(key), "Prevalence (%)": round(self.pop[key].mean()*100, 1), "ci_ll": self.pop[key].quantile(0.025), "ci_ul": self.pop[key].quantile(0.975)})

        data = pd.DataFrame(data)

        cat = "Risk factor"
        subcat = "Type"
        val = "Prevalence (%)"
        err1 = "ci_ll"
        err2 = "ci_ul"
        grouped_barplot(data, cat, subcat, val, err1, err2)

    # Relationships between frailty, disability and multimorbidity...
    def FDM(self):
        plt.clf()
        df = self.pop

        def getPercentage(v):
            f"{round(v, 1)}%"

        venn3_unweighted(subsets = (
            getPercentage(len(df[(df['badlImpairment'] == 1) & (df['multimorbidity'] == 0) & (df['frailty'] == 0)]) / len(df)), # D
            getPercentage(len(df[(df['badlImpairment'] == 0) & (df['multimorbidity'] == 0) & (df['frailty'] == 1)]) / len(df)), # F
            getPercentage(len(df[(df['badlImpairment'] == 1) & (df['multimorbidity'] == 0) & (df['frailty'] == 1)]) / len(df)), # DF
            getPercentage(len(df[(df['badlImpairment'] == 0) & (df['multimorbidity'] == 1) & (df['frailty'] == 0)]) / len(df)), # M
            getPercentage(len(df[(df['badlImpairment'] == 1) & (df['multimorbidity'] == 1) & (df['frailty'] == 0)]) / len(df)), # DM
            getPercentage(len(df[(df['badlImpairment'] == 0) & (df['multimorbidity'] == 1) & (df['frailty'] == 1)]) / len(df)), # MF
            getPercentage(len(df[(df['badlImpairment'] == 1) & (df['multimorbidity'] == 1) & (df['frailty'] == 1)]) / len(df)) # DFM
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
        negative_likelihood = (1 - sensitivity) / specificity
        false_positive_rate = 1 - specificity
        false_negative_rate = 1 - sensitivity
        positive_predictive_value = tp / (tp + fp)
        negative_predictive_value = tn / (tn + fn)
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

        tp = df[(df['efi'] >= 0.13) & (df['frailty'] == 1)].count()
        fn = df[(df['efi'] < 0.13) & (df['frailty'] == 1)].count()
        fp = df[(df['efi'] >= 0.13) & (df['frailty'] == 0)].count()
        tn = df[(df['efi'] < 0.13) & (df['frailty'] == 0)].count()

        return self.calculateAccuracy(tp, tn, fp, fn)

    def tugAnalysis(self):
        df = self.pop

        tp = df[(df['tug'] >= 10) & (df['frailty'] == 1)].count()
        fn = df[(df['tug'] < 10) & (df['frailty'] == 1)].count()
        fp = df[(df['tug'] >= 10) & (df['frailty'] == 0)].count()
        tn = df[(df['tug'] < 10) & (df['frailty'] == 0)].count()

        return self.calculateAccuracy(tp, tn, fp, fn)

    def outcomeStats(self):

        outcomes = {}

        for k,v in config['pretty-outcome-strings'].items():
            outcomes[v] = f'{round(self.pop[k].mean(), 1) * 100} ({round(self.pop[k].quantile(0.025)) * 100}-{round(self.pop[k].quantile(0.975)) * 100})'

        return outcomes




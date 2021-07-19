import math, yaml
import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.stats.api as sm
import scipy.stats as stats
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

    def calculate_confidence_interval(self, df, _q=0.95):
        z = stats.norm.ppf(q = _q)
        mu = df.mean()
        sigma = df.std()
        err = z * (sigma / math.sqrt(len(df)))
        ll = mu - err
        ul = mu + err
        return ll, ul
    
    def sampleSize(self):
        return len(self.pop)

    def ageStats(self):
        #mean, median, range [ll,ull]
        return self.pop.age.mean(axis=0), self.pop.age.median(axis=0), [self.pop.age.min(axis=0), self.pop.age.max(axis=0)]
    
    def genderBalance(self):
        return self.pop['gender'].value_counts(normalize=True).iloc[0]

    def cancerPrevalence(self):
        cancers = self.pop['cancer_site'].value_counts(normalize=True).rename_axis('sites').reset_index(name='counts')
        cancers['sites'] = cancers['sites'].str.capitalize()
        fig = px.pie(cancers, values='counts', names='sites')
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.write_image("results/plots/cancer_prevalence.png", scale=0.75)

    def anthropometrics(self):
        
        return (
            ('Height (mean [cm] SD)', f"{round(self.pop['height'].mean(), 1)} ({round(self.pop['bmi'].std(), 1)})"),
            ('Weight (mean [kg] SD)',  f"{round(self.pop['weight'].mean(), 1)} ({round(self.pop['bmi'].std(), 1)})"),
            ('Body mass index (mean, SD)',  f"{round(self.pop['bmi'].mean())} ({round(self.pop['bmi'].std())})")
        )
    
    def creatinineStats(self):
        ll, ul = self.calculate_confidence_interval(self.pop['cr'])
        return f"{round(self.pop['cr'].mean())} ({round(ll)}-{round(ul)})"

    def srhStats(self):
        ll, ul = self.calculate_confidence_interval(self.pop['self_reported_health'])
        return f"{round(self.pop['self_reported_health'].mean(), 1)} ({round(ll, 1)}-{round(ul, 1)})"

    def tugStats(self):
        ll, ul = self.calculate_confidence_interval(self.pop['tug'])
        return f"{round(self.pop['tug'].mean(), 1)} ({round(ll, 1)}-{round(ul, 1)})"

    def frailtyStats(self):
        ll, ul = sm.proportion_confint(len(self.pop[self.pop['frailty'] == 1]), len(self.pop['frailty']), method='wilson')
        return f"{round(self.pop['frailty'].mean()*100, 1)} ({round(ll*100, 1)}-{round(ul*100, 1)})"

    # def riskFactorPrevalence(self, factors=[]):
    #     prevalence = []
    #     for factor in factors:
    #         prevalence.append(f"{round(self.pop[factor].mean(), 1)} ({round(self.pop[factor].quantile(0.025))}-{round(self.pop[factor].quantile(0.975))})")
    #     return prevalence

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
                ll, ul = sm.proportion_confint(len(self.pop[self.pop[key] == 1]), len(self.pop[key]), method='wilson')
                err_simulated.append(ll)
                err_simulated_minus.append(ul)
              
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
        fig.write_image("results/plots/prevalence_expected.png", scale=0.8, width=600, height=848)

    # Relationships between frailty, disability and multimorbidity...
    def FDM(self):
        plt.clf()
        df = self.pop

        venn3_unweighted(subsets = (
            str(round((len(df[(df['badlImpairment'] == 1) & (df['multimorbidity'] == 0) & (df['frailty'] == 0)]) / len(df))*100, 1))+"%", # D
            str(round((len(df[(df['badlImpairment'] == 0) & (df['multimorbidity'] == 0) & (df['frailty'] == 1)]) / len(df))*100, 1))+"%", # F
            str(round((len(df[(df['badlImpairment'] == 1) & (df['multimorbidity'] == 0) & (df['frailty'] == 1)]) / len(df))*100, 1))+"%", # DF
            str(round((len(df[(df['badlImpairment'] == 0) & (df['multimorbidity'] == 1) & (df['frailty'] == 0)]) / len(df))*100, 1))+"%", # M
            str(round((len(df[(df['badlImpairment'] == 1) & (df['multimorbidity'] == 1) & (df['frailty'] == 0)]) / len(df))*100, 1))+"%", # DM
            str(round((len(df[(df['badlImpairment'] == 0) & (df['multimorbidity'] == 1) & (df['frailty'] == 1)]) / len(df))*100, 1))+"%", # MF
            str(round((len(df[(df['badlImpairment'] == 1) & (df['multimorbidity'] == 1) & (df['frailty'] == 1)]) / len(df))*100, 1))+"%" # DFM
        ), set_labels = ('Disability', 'Frailty', 'Multimorbidity'), alpha = 0.8)

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
        
        fig = go.Figure(go.Sunburst(
            data,
            labels=data['labels'],
            parents=["", "", "", "Normal", "Overweight", "", "Underweight", "Obese"],
            values=data['values'],
            textinfo='label+percent entry'
        ))
        fig.update_layout(margin = dict(t=0, l=0, r=0, b=0))

        fig.write_image("results/plots/sunburst.png", scale=2, width=250, height=250)

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
        return self.pop['efi_classification'].value_counts(normalize=True)
     

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
            ll, ul = sm.proportion_confint(len(self.pop[self.pop[k] == 1]), len(self.pop[k]), method='wilson')
            outcomes[v] = f'{round(self.pop[k].mean() * 100, 1)} ({round(ll*100, 1)}-{round(ul*100, 1)})'

        return outcomes
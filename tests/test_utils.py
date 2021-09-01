import yaml
import pandas as pd
import numpy as np
from util.utilities import Utilities

pop = pd.read_csv('tests/test_data.csv')

# Load config file
config = None
with open("config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

# Instantiate general utility class and inject config
u = Utilities(config)

class TestUtils():
    def test_cambridge_multimorbidity_score(self): 
        p = pop.iloc[[0]].to_dict('index')
        c,a,m,g = u.calculateCambridgeMultimorbidityScore(p[0])
        assert 0 not in [c,a,m,g]
    
    def test_incorrect_date(self):
        p = pop.iloc[[0]].to_dict('index')
        d = u.reportsDateIncorrectly(0.25, p[0]) # 0.25 rough estimate of baseline
        assert d == 1 or d == 0 
    
    def test_self_reported_health(self):
        p = pop.iloc[[0]].to_dict('index')[0]
        srh_dist = []
        baseline = 2
        for _ in range(1,5000):
            srh_dist.append(u.calculateSelfReportedHealth(baseline, p))
        assert min(srh_dist) == 1 and max(srh_dist) == 4
import yaml
import pandas as pd
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

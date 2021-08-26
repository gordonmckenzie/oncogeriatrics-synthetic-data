import os,time
from util.generateDocx import generateReport
from util.analysis import Analysis
import pandas as pd

pop = pd.read_csv('/Users/gagmckenzie/Desktop/20-07-2021-10-42-45.csv')

a = Analysis(pop)

class TestAnalysis():
    def test_analysis(self):
        date = time.strftime("%d-%m-%Y-%H-%M-%S")
        filename = f"results/reports/{date}.docx"
        generateReport(a, filename)
        assert os.path.isfile(filename)

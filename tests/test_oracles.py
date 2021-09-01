from oracles.qfracture import male_fracture_risk, female_fracture_risk

class TestOracles():
    def test_fracture_risk_male(self):
        m_risk = male_fracture_risk(ethnicity="PAKISTANI")
        print(f"\n\nRisk = {m_risk}\n\n")
        assert round(m_risk, 2) == 2

    def test_fracture_risk_female(self):
        f_risk = female_fracture_risk(ethnicity="PAKISTANI")
        print(f"\n\nRisk = {f_risk}\n\n")
        assert round(f_risk, 1) == 3.6

     
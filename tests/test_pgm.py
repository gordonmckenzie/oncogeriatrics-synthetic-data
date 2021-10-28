from models.pgm import PGM
pgm: PGM = PGM()

class TestPGM():

    def test_infer_anaemia(self):
        result = pgm.inferAnaemia({'geriatricVulnerabilities': {'anaemia': {'f': 3.8, 'm': 4.1}}}, 'f', pgm.inferenceResult(1))

        result = round(result, 2)

        print(result)

        assert result == 0 or result == 1

    def test_infer_decreased_social_activity(self):
        result = pgm.inferDecreasedSocialActivity(
            {'geriatricVulnerabilities': {'decreasedSocialActivity': {'f': 44, 'm': 44}}},
            'f',
            65,
            0,
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            0
        )

        result = round(result, 2)

        assert result == 0 or result == 1

    def test_infer_postop_pulm_comps(self):
        result,_ = pgm.inferPostOpPulmComps(
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            pgm.inferenceResult(0)
        ) 

        result = round(result, 3)

        assert result == 0.144

    def test_infer_nursing_home_admission(self):
        result,_ = pgm.inferNursingHomeAdmission(
                pgm.inferenceResult(0),
                pgm.inferenceResult(0),
                pgm.inferenceResult(0),
                pgm.inferenceResult(0)
            ) 

        result = round(result, 3)

        assert result == 0.05

    def test_infer_neutropaenic_events(self):
        result,_ = pgm.inferNeutropaenicEvents(
                pgm.inferenceResult(0),
                pgm.inferenceResult(0)
            ) 

        result = round(result, 3)

        assert result == 0.107

    def test_infer_functional_decline(self):
        result,_ = pgm.inferFunctionalDecline(
                pgm.inferenceResult(0)
            ) 

        result = round(result, 3)

        assert result == 0.201

    def test_infer_increased_los(self):
        result,_ = pgm.inferIncreasedLOS(
                pgm.inferenceResult(0),
                pgm.inferenceResult(0),
                pgm.inferenceResult(0),
                pgm.inferenceResult(0)
            ) 

        result = round(result, 3)

        assert result == 0.342

    def test_infer_PIMS(self):
        result,_ = pgm.inferPIMs(
                pgm.inferenceResult(0),
                pgm.inferenceResult(0)
            ) 

        result = round(result, 3)

        assert result == 0.51

    def test_infer_itu_admission(self):
        result,_ = pgm.inferITUAdmission(
                pgm.inferenceResult(0),
                pgm.inferenceResult(0),
                pgm.inferenceResult(0),
                pgm.inferenceResult(0),
                pgm.inferenceResult(1) # ASA = 1 
            ) 

        result = round(result, 3)

        assert result == 0.005

    def test_infer_survive_cpr(self):
        result,_ = pgm.inferSurviveCPR(
                60, # pass raw age
                pgm.inferenceResult(0),
                pgm.inferenceResult(0)
            ) 

        result = round(result, 3)

        assert result == 0.825

    def test_infer_postop_neuro_comps(self):
        result,_ = pgm.inferPostOpNeuroComps(
            pgm.inferenceResult(0),
            pgm.inferenceResult(0)
        ) 

        result = round(result, 3)

        assert result == 0.003

    def test_infer_wound_complications(self):
        result,_ = pgm.inferWoundComplications(
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            pgm.inferenceResult(0)
        ) 

        result = round(result, 3)

        assert result == 0.051

    def test_infer_postop_pain(self):
        result,_ = pgm.inferPostOperativePain(
            pgm.inferenceResult(0),
            pgm.inferenceResult(0)
        ) 

        result = round(result, 2)

        assert result == 0.88

    def test_infer_all_postop_complications(self):
        result,_ = pgm.inferAllSurgicalComplications(
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            pgm.inferenceResult(0)
        ) 

        result = round(result, 2)

        assert result == 0.30

    def test_infer_all_postop_delirium(self):
        result,_ = pgm.inferPostOpDelirium(
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            pgm.inferenceResult(0),
            pgm.inferenceResult(0)
        ) 

        result = round(result, 3)

        assert result == 0.187
    


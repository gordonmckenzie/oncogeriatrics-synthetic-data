import math
import numpy as np
from oracles.qrisk import map_ethnicity

rng = np.random.default_rng()

def map_alcohol_use(use):
    if use == 0:
        return 0
    elif use == 1:
        return rng.choice(1,4)
    elif use == 2:
        return rng.choice(4,5)

def female_fracture_risk(
    age=65,
    alcohol_use=0,
    antidepressant=0,
    asthma_copd=0,
    corticosteroids=0,
    cvd=0,
    dementia=0,
    falls=0,
    cld=0,
    parkinsons=0,
    ra_sle=0, 
    renal=0,
    t1dm=0,
    t2dm=0,
    bmi=26.2,
    ethnicity="UNKNOWN",
    endocrine=0,
    epilepsy=0,
    fh_osteoporosis=0,
    previous_fracture=0,
    smoke_cat=2,
    hrt=0,
    malabsorption=0,
    surv=10,
    cancer=1
):
    survivor = [
        0,
        0.998989343643188,
        0.997853457927704,
        0.996573925018311,
        0.995212137699127,
        0.993696928024292,
        0.991993606090546,
        0.990109741687775,
        0.988066852092743,
        0.985876500606537,
        0.983377099037170,
        0.980558633804321,
        0.977307498455048,
        0.974049806594849,
        0.970507681369781,
        0.966851711273193,
        0.962773561477661,
        0.958411157131195,
        0.953392088413239
    ]

    alcohol = [
        0,
        0.0002414945264996203800000,
        0.0531971614510470740000000,
        0.1624289372927301400000000,
        0.4778223231666232600000000,
        0.6270597140515218300000000
    ]

    ethnic_group = [
        0,
        0,
        -0.2875917367450486200000000,
        -0.7824524516248326800000000,
        -0.8172794063622931300000000,
        -0.5861737865251788200000000,
        -1.4935356591327420000000000,
        -0.7355039455837261200000000,
        -0.4900951523299932300000000,
        -0.4546040850271730900000000
    ]

    smoke = [
        0,
        0.0371938876652497460000000,
        0.0951525414150192620000000,
        0.1221740242710975300000000,
        0.1611412668468513200000000
    ]

    dage = age / 10
    age_1 = math.pow(dage,2)
    age_2 = math.pow(dage,3)
    dbmi = bmi / 10
    bmi_1 = math.pow(dbmi,-1)

    age_1 = age_1 - 26.453824996948242
    age_2 = age_2 - 136.060699462890620
    bmi_1 = bmi_1 - 0.385703802108765

    a = 0

    ethrisk = map_ethnicity(ethnicity)

    alcohol_risk = map_alcohol_use(alcohol_use)

    # The conditional sums 
    if smoke_cat == 2:
        smoke_cat = 0
    elif ethrisk == 1:
        smoke_cat = 1
    elif smoke_cat == 0:
        smoke_cat = rng.integers(2,4)

    a += alcohol[alcohol_risk]
    a += ethnic_group[ethrisk]
    a += smoke[smoke_cat]

    # Sum from continuous values

    a += age_1 * 0.1437995480730194500000000
    a += age_2 * -0.0093249719419669745000000
    a += bmi_1 * 2.9094622051196999000000000

    # Sum from boolean values 

    a += antidepressant * 0.3175542392827512800000000
    a += cancer * 0.2384763167407743000000000
    a += asthma_copd * 0.2389060345873167400000000
    a += corticosteroids * 0.1926383637036637200000000
    a += cvd * 0.1914278981809385300000000
    a += dementia * 0.6757597945847583200000000
    a += endocrine * 0.2105749527624362900000000
    a += epilepsy * 0.4297240630789712600000000
    a += falls * 0.4505018230780948300000000
    a += previous_fracture * 0.0804836468689180270000000
    a += hrt * -0.1586145398766347600000000
    a += cld * 0.6391726322367494700000000
    a += malabsorption * 0.1547851620897652300000000
    a += parkinsons * 0.4958354577680105800000000
    a += ra_sle * 0.2888701063403104600000000
    a += renal * 0.2390562428559968600000000
    a += t1dm * 0.6523717632491761200000000
    a += t2dm * 0.2355143698342233000000000
    a += fh_osteoporosis * 0.5517999076133333100000000

    # Calculate the score itself 
    score = 100.0 * (1 - math.pow(survivor[surv], math.exp(a)))
    return score

def male_fracture_risk(
    age=65,
    alcohol_use=0,
    antidepressant=0,
    asthma_copd=0,
    corticosteroids=0,
    cvd=0,
    dementia=0,
    falls=0,
    cld=0,
    parkinsons=0,
    ra_sle=0, 
    renal=0,
    t1dm=0,
    t2dm=0,
    bmi=26.2,
    ethnicity="UNKNOWN",
    epilepsy=0,
    fh_osteoporosis=0,
    previous_fracture=0,
    smoke_cat=2,
    carehome=0,
    malabsorption=0,
    surv=10,
    cancer=1
):

    survivor = [
        0,
        0.999644935131073,
        0.999273777008057,
        0.998869180679321,
        0.998421549797058,
        0.997928738594055,
        0.997390747070313,
        0.996753513813019,
        0.996096074581146,
        0.995346963405609,
        0.994551837444305,
        0.993598461151123,
        0.992581725120544,
        0.991482257843018,
        0.990263521671295,
        0.989037752151489,
        0.987761437892914,
        0.986425399780273,
        0.984853565692902
    ]

    alcohol = [
        0,
        -0.0753424993511384030000000,
        0.0035640920160520625000000,
        0.1107180929467958700000000,
        0.2772772729818878100000000,
        0.7629384134280495800000000
    ]
    
    ethnic_group = [
        0,
        0,
        -0.2578247985190295600000000,
        -0.2739691601862618800000000,
        -1.2488100943578264000000000,
        -0.4478136903122282900000000,
        -0.9569833717832930700000000,
        -0.6454670770263975000000000,
        -0.2441668713268753100000000,
        -0.5585671879728931800000000
    ]

    smoke = [
        0,
        -0.0008039513520016420400000,
        0.1560272763218023000000000,
        0.2511740981322320700000000,
        0.2796740114008822700000000
    ]

    dage = age / 10
    age_1 = math.pow(dage,0.5)
    age_2 = dage
    dbmi = bmi / 10
    bmi_1 = math.pow(dbmi, -1)
    bmi_2 = math.pow(dbmi, -0.5)

    # Centring the continuous variables #

    age_1 = age_1 - 2.213409662246704
    age_2 = age_2 - 4.899182319641113
    bmi_1 = bmi_1 - 0.376987010240555
    bmi_2 = bmi_2 - 0.613992691040039

    # Start of Sum #
    a = 0

    # The conditional sums #
    ethrisk = map_ethnicity(ethnicity)

    alcohol_risk = map_alcohol_use(alcohol_use)

    # The conditional sums 
    if smoke_cat == 2:
        smoke_cat = 0
    elif ethrisk == 1:
        smoke_cat = 1
    elif smoke_cat == 0:
        smoke_cat = rng.integers(2,4)

    a += alcohol[alcohol_risk]
    a += ethnic_group[ethrisk]
    a += smoke[smoke_cat]

    # Sum from continuous values #

    a += age_1 * -9.0010590056070825000000000
    a += age_2 * 2.4013416577413533000000000
    a += bmi_1 * 18.1789865484634670000000000
    a += bmi_2 * -18.9164740466035500000000000

    # Sum from boolean values #

    a += antidepressant * 0.4687193755788741600000000
    a += cancer * 0.4507500533865196300000000
    a += asthma_copd * 0.2886693311011971400000000
    a += carehome * 0.4624017599741130900000000
    a += corticosteroids * 0.2959070482702296200000000
    a += cvd * 0.2342575101174369000000000
    a += dementia * 0.6410107589079159200000000
    a += epilepsy * 0.7821394592420207700000000
    a += falls * 0.5427801687901475700000000
    a += previous_fracture * 0.3037648317094442400000000
    a += cld * 0.9492983471493211500000000
    a += malabsorption * 0.2198043397723023800000000
    a += parkinsons * 0.8971315042849318200000000
    a += ra_sle * 0.4403191212798893100000000
    a += renal * 0.4565029417822387700000000
    a += t1dm * 0.8447272010743575000000000
    a += t2dm * 0.2219385025905733500000000
    a += fh_osteoporosis * 1.6999403855072708000000000

    # Calculate the score itself #
    score = 100.0 * (1 - math.pow(survivor[surv], math.exp(a)))
    return score









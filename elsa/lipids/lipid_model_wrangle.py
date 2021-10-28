import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from functools import reduce

index_path = '/Volumes/My Passport for Mac/ELSA/UKDA-5050-tab/tab/index_file_wave_0-wave_5_v2.tab'
core_path = '/Volumes/My Passport for Mac/ELSA/UKDA-5050-tab/tab/wave_2_core_data_v4.tab'
nurse_path = '/Volumes/My Passport for Mac/ELSA/UKDA-5050-tab/tab/wave_2_nurse_data_v2.tab'
common_path = '/Volumes/My Passport for Mac/ELSA/UKDA-5050-tab/tab/wave_0_common_variables_v2.tab'
derived_path = '/Volumes/My Passport for Mac/ELSA/UKDA-5050-tab/tab/wave_2_derived_variables.tab'

"""
['idauniq', 'persno', 'idahhw0', 'idahhw1', 'idahhw2', 'idahhw3', 'idahhw4', 'idahhw5', 'outindw0', 'outhhw0', 
'outscw0', 'outnrsw0', 'outindw1', 'outhhw1', 'outscw1', 'prodw1', 'outindw2', 'outhhw2', 'outscw2', 'outnrsw2', 
'outnscw2', 'prodw2', 'outindw3', 'outhhw3', 'outscw3', 'outschw3', 'outscww3', 'prodw3', 'retroout', 'outindw4', 
'outhhw4', 'outscw4', 'outnrsw4', 'prodw4', 'outindw5', 'outhhw5', 'outscw5', 'prodw5', 'RiskoutW5', 'issuew1', 
'issuew2', 'issuew3', 'issuew4', 'issuew5', 'issueW5risk', 'finstatw1', 'finstatw2', 'finstatw3', 'finstatw4', 
'finstatw5', 'mortwave', 'sex', 'dobyear', 'hseyr', 'hseint']
"""
#index = pd.read_csv(index_path, sep='\t', low_memory=False)

"""
Variable name Variable label
idauniq Unique individual serial number
idaindw0 Analytical wave-specific individual serial number (W0)
idahhw0 Analytical wave-specific household serial number (W0)
hseyr HSE source year
eligstat Eligibility status
sampstat ELSA W1 Sampling status
finstat Final ELSA W1 status
acutill (D) Acute sickness last two weeks
lastfort Cut activities due to health (last 2 weeks)
dayscut No. of days cut down on activities
ghq12scr (D) GHQ Score - 12 point scale
ghqg2 (D) GHQ Score - grouped (0,1-3,4+)
ghqconc GHQ: Able to concentrate
ghqsleep GHQ: Lost sleep over worry
ghquse GHQ: Felt playing useful part in things
ghqdecis GHQ: Felt capable of making decisions
ghqstrai GHQ: Felt constantly under strain
ghqover GHQ: Felt couldn't overcome difficulties
ghqenjoy GHQ: Able to enjoy day-to-day activities
ghqface GHQ: Been able to face problems
ghqunhap GHQ: Been feeling unhappy and depressed
ghqconfi GHQ: Been losing confidence in self
ghqworth GHQ: Been thinking of self as worthless
ghqhappy GHQ: Been feeling reasonably happy
pillevr Ever taken contraceptive pill or had injection/implant
pilluse Whether use contraceptives (pill/injection/implant)
pillbrd Brand of contraceptive used - BNF Code
pilltyp Type of contraceptive used
period Whether still having periods
operiod Whether periods stopped as a result of an operation
ovary Whether has had ovaries removed
hrtevr Whether ever been on HRT
hrtage Age started HRT
hrtnow Whether still on HRT
hrtstp Age stopped HRT
limitill (D) Limiting longstanding illness
longill Whether has longstanding illness
limitact Activities limited due to illness
condcnt (D) Number of grouped condition categories
condcnt2 (D) Number of grouped conditions - 4 plus
compm13 (D) II Neoplasms & benign growths
compm1 (D) III Endocrine & metabolic
compm2 (D) V Mental disorders
compm14 (D) VI Nervous System
compm3 (D) VI Eye complaints
compm4 (D) VI Ear complaints
compm5 (D) VII Heart & circulatory system
compm6 (D) VIII Respiratory system
compm7 (D) IX Digestive system
compm8 (D) X Genito-urinary system
compm9 (D) XII Skin complaints
compm10 (D) XIII Musculoskeletal system
compm11 (D) I Infectious Disease
compm12 (D) IV Blood & related organs
compm15 (D) Other complaints
compm17 (D) No long-standing Illness
compm18 (D) No longer present
compm99 (D) Unclass/NLP/inadeq.describe
illsm1 Type of illness - 1st
illsm2 Type of illness - 2nd
illsm3 Type of illness - 3rd
illsm4 Type of illness - 4th
illsm5 Type of illness - 5th
illsm6 Type of illness - 6th
diur (D) Diuretics (Blood pressure)
beta (D) Beta blockers (Blood pressure/Fibrinogen)
aceinh (D) Ace inhibitors (Blood pressure)
calciumb (D) Calcium blockers (Blood pressure)
obpdrug (D) Other drugs affecting BP
lipid (D) Lipid lowering (Cholesterol/Fibrinogen)
iron (D) Iron deficiency (Haemoglobin/Ferritin)
bpmedc (D) Whether taking drugs affecting blood pressure
bpmedd (D) Whether taking drugs prescribed for blood pressure
medcnjd Currently taking medication prescribed by doctor
medcnj (D) Whether taking medication - excluding contraceptives only
vitamin Taking vitamins/mineral to improve health
medbi01 Medicine 1: Names of medicines prescribed by doctor (BNF Code)
medbi02 Medicine 2: Names of medicines prescribed by doctor (BNF Code)
medbi03 Medicine 3: Names of medicines prescribed by doctor (BNF Code)
medbi04 Medicine 4: Names of medicines prescribed by doctor (BNF Code)
medbi05 Medicine 5: Names of medicines prescribed by doctor (BNF Code)
medbi06 Medicine 6: Names of medicines prescribed by doctor (BNF Code)
medbi07 Medicine 7: Names of medicines prescribed by doctor (BNF Code)
medbi08 Medicine 8: Names of medicines prescribed by doctor (BNF Code)
medbi09 Medicine 9: Names of medicines prescribed by doctor (BNF Code)
medbi10 Medicine 10: Names of medicines prescribed by doctor (BNF Code)
medbi11 Medicine 11: Names of medicines prescribed by doctor (BNF Code)
medbi12 Medicine 12: Names of medicines prescribed by doctor (BNF Code)
medbi13 Medicine 13: Names of medicines prescribed by doctor (BNF Code)
medbi14 Medicine 14: Names of medicines prescribed by doctor (BNF Code)
medbi15 Medicine 15: Names of medicines prescribed by doctor (BNF Code)
medbi16 Medicine 16: Names of medicines prescribed by doctor (BNF Code)
medbi17 Medicine 17: Names of medicines prescribed by doctor (BNF Code)
medbi18 Medicine 18: Names of medicines prescribed by doctor (BNF Code)
medbi19 Medicine 19: Names of medicines prescribed by doctor (BNF Code)
medbi20 Medicine 20: Names of medicines prescribed by doctor (BNF Code)
medbi21 Medicine 21: Names of medicines prescribed by doctor (BNF Code)
medbi22 Medicine 22: Names of medicines prescribed by doctor (BNF Code)
medtyp1 (D) Cardio-vascular medicine taken
medtyp2 (D) Gastrointestinal medicine taken
medtyp3 (D) Respiratory medicine taken
medtyp4 (D) CNS medicine taken
medtyp5 (D) Medicine for infection taken
medtyp6 (D) Endocrine medicine taken
medtyp7 (D) Gynae/Urinary medicine taken
medtyp8 (D) Cytotoxic medicine taken
medtyp9 (D) Medicine for nutrition/blood taken
medtyp10 (D) Musculoskeletal medicine taken
medtyp11 (D) Eye/Ear etc medicine taken
medtyp12 (D) Medicine for skin taken
medtyp13 (D) Other medicine taken
numed2 (D) Number of prescribed medicines taken
numed (D) Number of prescribed medicines taken (grouped 4+)
medbia1 Medicine 1: Whether medicine used in last 7 days
medbia2 Medicine 2: Whether medicine used in last 7 days
medbia3 Medicine 3: Whether medicine used in last 7 days
medbia4 Medicine 4: Whether medicine used in last 7 days
medbia5 Medicine 5: Whether medicine used in last 7 days
medbia6 Medicine 6: Whether medicine used in last 7 days
medbia7 Medicine 7: Whether medicine used in last 7 days
medbia8 Medicine 8: Whether medicine used in last 7 days
medbia9 Medicine 9: Whether medicine used in last 7 days
medbia10 Medicine 10: Whether medicine used in last 7 days
medbia11 Medicine 11: Whether medicine used in last 7 days
medbia12 Medicine 12: Whether medicine used in last 7 days
medbia13 Medicine 13: Whether medicine used in last 7 days
medbia14 Medicine 14: Whether medicine used in last 7 days
medbia15 Medicine 15: Whether medicine used in last 7 days
medbia16 Medicine 16: Whether medicine used in last 7 days
medbia17 Medicine 17: Whether medicine used in last 7 days
medbia18 Medicine 18: Whether medicine used in last 7 days
medbia19 Medicine 19: Whether medicine used in last 7 days
medbia20 Medicine 20: Whether medicine used in last 7 days
medbia21 Medicine 21: Whether medicine used in last 7 days
medbia22 Medicine 22: Whether medicine used in last 7 days
ytake011 Drug For: Heart problem
ytake012 Drug For: High blood pressure
ytake013 Drug For: Other reason
ytake021 Drug For: Heart problem
ytake022 Drug For: High blood pressure
ytake023 Drug For: Other reason
ytake031 Drug For: Heart problem
ytake032 Drug For: High blood pressure
ytake033 Drug For: Other reason
ytake041 Drug For: Heart problem
ytake042 Drug For: High blood pressure
ytake043 Drug For: Other reason
ytake051 Drug For: Heart problem
ytake052 Drug For: High blood pressure
ytake053 Drug For: Other reason
ytake061 Drug For: Heart problem
ytake062 Drug For: High blood pressure
ytake063 Drug For: Other reason
ytake071 Drug For: Heart problem
ytake072 Drug For: High blood pressure
ytake073 Drug For: Other reason
ytake081 Drug For: Heart problem
ytake082 Drug For: High blood pressure
ytake083 Drug For: Other reason
ytake091 Drug For: Heart problem
ytake092 Drug For: High blood pressure
ytake093 Drug For: Other reason
ytake101 Drug For: Heart problem
ytake102 Drug For: High blood pressure
ytake103 Drug For: Other reason
ytake111 Drug For: Heart problem
ytake112 Drug For: High blood pressure
ytake113 Drug For: Other reason
ytake121 Drug For: Heart problem
ytake122 Drug For: High blood pressure
ytake123 Drug For: Other reason
ytake131 Drug For: Heart problem
ytake132 Drug For: High blood pressure
ytake133 Drug For: Other reason
ytake141 Drug For: Heart problem
ytake142 Drug For: High blood pressure
ytake143 Drug For: Other reason
ytake151 Drug For: Heart problem
ytake152 Drug For: High blood pressure
ytake153 Drug For: Other reason
genhelf Self-assessed general health
genhelf2 (D) Self-assessed general health - grouped
pssscr (D) Perceived social support score
pssscr2 (D) perceived social support score - grouped
sshappy Social Support: People I know do things to make me feel happy
ssloved Social Support: People I know make me feel loved
ssrely Social Support: People I know can be relied upon
sscare Social Support: People I know will see that I am taken care of
ssaccept Social Support: People I know accept me just as I am
ssimport Social Support: People I know make me feel important
sssupp Social Support: People I know give me support and encouragement
ngp (D) No. of NHS GP consultations last 2 weeks
ngpg4 (D) No. of NHS GP consultations last 2 weeks (grouped)
ngpyr (D)No. of NHS GP consultations per year
gptalk Consulted a NHS GP for self
gpvis (D) Visited NHS GP for consultation last 2 weeks
nsite1 (D) Visited NHS GP for consultation last 2 weeks: surgery
nsite2 (D) Visited NHS GP for consultation last 2 weeks: home
nsite3 (D) Visited NHS GP for consultation last 2 weeks: telephone
ndoctalk Talked to doctor (last 2 weeks)
nchats No. times talked to a doctor
whsbhlf1 Consult1: Whose behalf talked to a doctor
forper1 Consult1: Which person no. talked to a doctor
nhs1 Consult1: NHS/Private
docwher1 Consult1: Where talked to doctor
presc1 Consult1: Prescription given?
whsbhlf2 Consult2: Whose behalf talked to a doctor
forper2 Consult2: Which person no. talked to a doctor
nhs2 Consult2: NHS/Private
docwher2 Consult2: Where talked to doctor
presc2 Consult2: Prescription given?
whsbhlf3 Consult3: Whose behalf talked to a doctor
forper3 Consult3: Which person no. talked to a doctor
nhs3 Consult3: NHS/Private
docwher3 Consult3: Where talked to doctor
presc3 Consult3: Prescription given?
whsbhlf4 Consult4: Whose behalf talked to a doctor
forper4 Consult4: Which person no. talked to a doctor
nhs4 Consult4: NHS/Private
docwher4 Consult4: Where talked to doctor
presc4 Consult4: Prescription given?
whsbhlf5 Consult5: Whose behalf talked to a doctor
forper5 Consult5: Which person no. talked to a doctor
nhs5 Consult5: NHS/Private
docwher5 Consult5: Where talked to doctor
presc5 Consult5: Prescription given?
whsbhlf6 Consult6: Whose behalf talked to a doctor
forper6 Consult6: Which person no. talked to a doctor
nhs6 Consult6: NHS/Private
docwher6 Consult6: Where talked to doctor
presc6 Consult6: Prescription given?
whsbhlf7 Consult7: Whose behalf talked to a doctor
forper7 Consult7: Which person no. talked to a doctor
nhs7 Consult7: NHS/Private
docwher7 Consult7: Where talked to doctor
presc7 Consult7: Prescription given?
whsbhlf8 Consult8: Whose behalf talked to a doctor
forper8 Consult8: Which person no. talked to a doctor
nhs8 Consult8: NHS/Private
docwher8 Consult8: Where talked to doctor
presc8 Consult8: Prescription given?
whsbhlf9 Consult9: Whose behalf talked to a doctor
forper9 Consult9: Which person no. talked to a doctor
nhs9 Consult9: NHS/Private
docwher9 Consult9: Where talked to doctor
presc9 Consult9: Prescription given?
whendoc When last talked to doctor about self
dnnow Whether drink nowadays
dnany Whether drinks occasionally or never drinks
dnevr Whether always non-drinker
dramount Drink now compared to 5 years ago
whytt (D) Total Units of alcohol/week
drating Reason why stopped drinking
alcbase (D) Alcohol consumption rating units/week
alcbasmt (D) Alcohol consumption: men
alcbaswt (D) Alcohol consumption: women
overlim (D) Drinking in relation to weekly limits
nberwu (D) Units of normal beer/week
sberwu (D) Units of strong beer/week
spirwu (D) Units of spirits/week
sherwu (D) Units of sherry/week
winewu (D) Units of wine/week
popswu (D) Units of alcopops/week
d7unit (D) Units drunk on heaviest day in last 7
d7day Whether had drink in last 7 days
d7many How many days in last 7 had a drink
d7same Whether drank more on a particular in last 7 days
d7which Which day drank most in last 7
cigdyal (D) Number of cigarettes smoke a day - inc. non-smokers
cigwday Number cigarettes smoke on weekday
cigwend Number cigarettes smoke on weekend day
cigtyp Type of cigarette smoked
cigbrd Brand of cigarette smoked
cigtar Tar level of cigarette smoked
tarest Whether tar level estimated
cigreg How frequently used to smoke
numsmok How many cigarettes used to smoke
endsmoke Years since stopped smoking
smokyrs And for approximately how many years did you smoke cigarettes
regularly?
longend How many months ago (smoked)
cigst1 (D) Cigarette Smoking Status - Never/Ex-reg/Ex-occ/Current
cigst2 (D) Cigarette Smoking Status - Banded current smokers
smkevr Whether ever smoked cigarette/cigar/pipe
cignow Whether smoke cigarettes nowadays
cigevr Whether ever smoked cigarettes
smoke1 Currently smokes cigarettes
smoke2 Currently smokes cigars
smoke3 Currently smokes pipe
smoke4 Does not currently smoke
lastsmok When last smoked a cigarette/cigar/pipe
cigarnow Currently smokes cigars
cigarreg How regularly smokes cigars
pipenowa Currently smokes pipe
startsmk Age when started smoking
expsm Hours a week exposed to other peoples smoke
smkdad Whether father smoked when informant a child
smkmum Whether mother smoked when informant a child
passm Persons smoking in accomodation
numsm No. of persons smoking in accomodation
nicuseb (D) Used nicotine products in last 7 days
usegum Used any nicotine chewing gum?
gummg What strength is the nicotine chewing gum being used (2mg or 4mg)?
usepat Used any nicotine patches?
nicpats Which brand and strength of nicotine patches used?
usenas Used a nicotine nasal spray?
nicot Nicotine products used
bprespc (D) Whether BP readings are valid
bpconst Consent to BP measurement
ynobp Reason no BP measurements taken
respbps Response to BP measurements
full1 Reliability of 1st set of BP readings
full2 Reliability of 2nd set of BP readings
full3 Reliability of 3rd set of BP readings
dinno Dinamap serial no
cufsize Cuff size used
airtemp Air temperature
hyper140 (D) Hypertensive categories:140/90: all prescribed drugs for BP
hibp140 (D) Whether hypertensive:140/90: all prescribed drugs for BP
hyper1 (D) Hypertensive categories: all prescribed drugs for BP
highbp1 (D) Whether hypertensive: all prescribed drugs for BP
hyper2 (D) Hypertensive categories: all taking BP drugs
highbp2 (D) Whether hypertensive: all taking BP drugs
diaval (D) Valid Mean Diastolic BP
sysval (D) Valid Mean Systolic BP
mapval (D) Valid Mean Arterial Pressure
pulval (D) Valid Pulse Pressure
newdiast (D) Diastolic BP (mean 2nd/3rd) inc. invalid
newsyst (D) Systolic BP (mean 2nd/3rd) inc. invalid
newmap (D) Mean arterial pressure (mean 2nd/3rd) inc. invalid
puls (D) Pulse pressure, systolic-diastolic inc. invalid
map1 1st MAP reading (mmHg)
map2 2nd MAP reading (mmHg)
map3 3rd MAP reading (mmHg)
pulse1 1st Pulse reading (bpm)
pulse2 2nd Pulse reading (bpm)
pulse3 3rd Pulse reading (bpm)
sys1 1st Systolic reading (mmHg)
sys2 2nd Systolic reading (mmHg)
sys3 3rd Systolic reading (mmHg)
dias1 1st Diastolic reading (mmHg)
dias2 2nd Diastolic reading (mmHg)
dias3 3rd Diastolic reading (mmHg)
respds Response to demi-span measurement
spanrel1 Reliability of 1st demi-span measurement
spanrel2 Reliability of 2nd demi-span measurement
spanrel3 Reliability of 3rd demi-span measurement
ynospan Reason no demi-span measurement taken
spnm1 Demi-span measured standing against the wall
spnm2 Demi-span measured standing not against the wall
spnm3 Demi-span measured sitting
spnm4 Demi-span measured lying down
spnm5 Demi-span measured on left arm due to unsuitable right arm
spanval (D) Valid Mean Demispan (cm)
span1 Demi-span first measurement
span2 Demi-span second measurement
span3 Demi-span third measurement
wstval (D) Valid Mean Waist (cm)
waist1 Waist 1st measurement (cm)
waist2 Waist 2nd measurement (cm)
waist3 Waist 3rd measurement (cm)
hipval (D) Valid Mean Hip (cm)
hip1 Hip 1st measurement (cm)
hip2 Hip 2nd measurement (cm)
hip3 Hip 3rd measurement (cm)
whval (D) Valid Mean Waist/Hip ratio
menwhgp (D) Male waist hip ratio groups
menwhhi (D) Male high waist hip ratio
womwhgp (D) Female waist-hip ratio (grouped)
womwhhi (D) Female high waist-hip ratio
wstokb (D) Whether waist measurements are valid
hipokb (D) Whether hip measurements are valid
whokb (D) Whether waist/hip measure is valid
whintro Consent to waist/hip measurements
respwh Response to waist/hip measurements
ynowh Reason no waist/hip measurements
wjrel Whether problems with waist measurement
probwj Problems with measurement likely to increase/decrease waist
measurement
hjrel Whether problems with hip measurement
probhj Problems with measurement likely to increase/decrease hip
measurement
htok (D) Whether height measure is valid
wtok (D) Whether weight measure is valid
bmiok (D) Whether bmi measure is valid
resphts Response to height measurement
relhite Reliabiliy of height measurement
hinrel Why height unreliable
resnhi Refusal of height measurement
ehtch Non proxy: Form in which estimated height given
respwts Response to weight measurement
floorc1 Scales placed on uneven floor
floorc2 Scales placed on carpet
floorc3 Scales placed on neither (neither uneven floor nor carpet)
relwaitb Reliabiliy of weight measurement
resnwt Refusal of weight measurement
ewtch Form in which estimated weight given
height Height (cm) inc unreliabale measurements
htval (D) Valid height (cm)
estht Estimated height (cm)
wtval (D) Valid weight (Kg) inc. estimated>130kg
weight Weight (kg) - inc unreliable measurements
estwt Estimated weight (kg)
bmi (D) BMI - inc unreliable measurements
bmival (D) Valid BMI
bmivg4 (D) Valid BMI (grouped:<20,20-25,25-30,30+)
bmivg6 (D) Valid BMI (grouped:<20,20-25,25-30,30-35,35-40,40+)
bsoutc Outcome of blood sample
clotb Whether has clotting disorder
fit Whether ever had a fit
bswill Consent to take blood sample
ferval (D) Valid Ferritin Result, ng/ml
haemval (D) Valid Haemoglobin Result, g/dl
haemokb (D) Response to Haemoglobin sample
haemo Haemoglobin result
haemqual Haemoglobin serum quality
ferokb (D) Response to Ferritin sample
ferrit Ferritin result
ferqual Ferritin serum quality
finoutc Final outcome code
adults Number of adults in household
children Number of children in household
infants Number of infants in HH (replaces NInfants)
hhsize (D) Household Size
hhdtypb (D) Household Type
tenureb Household Tenure
jobaccom Accomodation linked to job
landlord Landlord of household
furn Is accomodation furnished
bedrooms Number of bedrooms in household
car Car or van available
numcars No. of cars available
sex Sex
ager Age last birthday collapsed at 90 plus
indout Individual outcome codes
dobyear Year of birth collapsed at 90 plus
marital Legal Marital Status
yintb Date of interview, year
persno Person number within household
hohnum Person number of HOH
hhresp Who answers hhold grid
hqresp Status of person answering household grid
nofiq Number of individual sessions.
nump Number of respondents in session
nhscr Permission to pass name to NHSCR
scomp3b SC booklet completed
sc3acc11 SC: Completed independently
sc3acc12 SC: Assistance from other children
sc3acc13 SC: Assistance from other household member
sc3acc14 SC: Assistance from interviewer
sc3acc15 Interviewer administered SC booklet
educend Age finished FT Education
topqual2 (D) Highest Educational Qualification - Students separate
topqual3 (D) Highest Educational Qualification
qual Any qualifications
quala01 Which qualifications :1st mention
quala02 Which qualifications :2nd mention
quala03 Which qualifications :3rd mention
quala04 Which qualifications :4th mention
quala05 Which qualifications :5th mention
quala06 Which qualifications :6th mention
quala07 Which qualifications :7th mention
quala08 Which qualifications :8th mention
quala09 Which qualifications :9th mention
quala10 Which qualifications :10th mention
scallx (D) Social Class of Indiv - Harmonised
econact (D) Economic Status (4 groups)
schrp (D) Social Class of HPR - Harmonised
schrpg4 (D) Social Class of HPR: I/II,IIINM,IIIM,IV/V
schrpg7 (D) Social Class of HPR - I,II,IIIN,IIIM,IV,V,Others
schrpg6 (D) Social Class of HPR - I,II,IIIN,IIIM,IV,V
hrpactiv HRP: Activity status for last week
hrpstwrk HRP: Paid work in last 7 days
hrp4wklk HRP: Looking paid work/govt scheme last 4 weeks
hrp2wkst HRP: Able to start work within 2 weeks
hrpeverj HRP: Ever had paid employment or self-employed
hrpothpd HRP: Ever had other employment (waiting to take up job)
hrpftpt HRP: Full-time, part-time
hrpemply HRP: Whether Employee/self-employed
hrpdirct HRP: Director of company
hrpempst HRP: Manager/Foreman
hrpnempl HRP: Number employed at place of work
hrpsnemp HRP: Self-employed how many employee?
hrpsoc2 HRP: SOC code
hrpsoc90 HRP: Social Class
hrpsoccl HRP: Social Class
hrpseg HRP: SEG
hrpsic92 HRP: SIC code
schoh (D) Social Class of HOH - Harmonised
schohg7 (D) Social Class of HOH - I,II,IIIN,IIIM,IV,V,Others
schohg6 (D) Social Class of HOH - I,II,IIIN,IIIM,IV,V
schohg4 (D) Social Class of HOH: I/II,IIINM,IIIM,IV/V
hactivb HOH: Activity status for last week
hstwork HOH: Paid work in last 7 days
h4wklook HOH: Looking paid work/govt scheme last 4 weeks
h2wkstrt HOH: Able to start work within 2 weeks
heverjob HOH: Ever had paid employment or self-employed
hothpaid HOH: Ever had other employment (waiting to take up job)
hftptime HOH: Full-time, part-time
hemploye HOH: Whether Employee/self-employed
hdirctr HOH: Director of company
hempstat HOH: Manager/Foreman
hnemplee HOH: No. employed at place of work
hsnemple HOH: Self-employed how many employee?
hsoc HOH: SOC code
hsclass Social Class
hseg Socio-Economic Group
hsic HOH: SIC code
activb Activity status for last week
stwork Paid work in last 7 days
wklook4 Looking paid work/govt scheme in last 4 weeks
wkstrt2 Able to start work within 2 weeks
everjob Ever had paid employment or self-employed
othpaid Ever had other employment (waiting to take up job)
ftptime Full-time, part-time
employe Whether Employee/self-employed
dirctr Director of company
empstat Manager/Foreman
nemplee Number employed at place of work
snemplee Do/did you have any employees?
sclass Social Class
seg Socio-Economic Group
soc2000 SOC code (2000)
soc90 SOC code (1990)
sic92 SIC code (1992)
soc SOC code, occupational details
sic SIC code
srcinc01 Income: Earnings from employment or self-employment
srcinc02 Income: State retirement pension
srcinc03 Income: Pension from former employer
srcinc04 Income: Child benefit
srcinc05 Income: Job-Seekers allowance
srcinc06 Income: Income Support
srcinc07 Income: Family Credit
srcinc08 Income: Housing Benefit
srcinc09 Income: Other state benefits
srcinc10 Income: Interest from savings and investments (eg stocks & shares)
srcinc11 Income: Other kinds of regular allowance from outside your household
srcinc12 Income: No source of income
jntinc Joint income
othinc Whether other income in household
hhinc Total household income
totinc (D) Total Household Income
mcclem (D) McClements household score for equivalised income
eqvinc (D) Equivalised Income
nuroutc Outcome of nurse visit
nurse Agreed to nurse appointment (at indiv interview)
nursere0 No nurse: Own doctor already has information
nursere1 No nurse: Given enough time already to this survey/expecting too much
nursere2 No nurse: Too busy, cannot spare the time
nursere3 No nurse: Had enough of medical tests/medical profession at present ti
nursere4 No nurse: Worried about what nurse may find out/might tempt fate
nursere5 No nurse: Scared/of medical profession/ particular medical procedures
nursere6 No nurse: Not interested/cannot be bothered/no particular reason
nursere7 No nurse: Other reason
visyear Date of nurse interview, year
pregntj Whether currently pregnant 16+
ispreg Whether currently pregnant
pregrec Whether pregnant in last twelve months
relto01 Relationship to person 01
relto02 Relationship to person 02
relto03 Relationship to person 03
relto04 Relationship to person 04
relto05 Relationship to person 05
relto06 Relationship to person 06
relto07 Relationship to person 07
relto08 Relationship to person 08
relto09 Relationship to person 09
relto10 Relationship to person 10
relto11 Relationship to person 11
relto12 Relationship to person 12
nofhh Number of households
hhold Household Number
salintr1 Agreement to saliva sample
salobt1 Whether saliva sample obtained
ethnicr HSE ethnic group collapsed into White and Non-white to avoid
disclosure
nethnir HSE self-defined ethnic group collapsed into White and Non-white to
avoid disclosure
"""

common = pd.read_csv(common_path, sep='\t', low_memory=False)
core = pd.read_csv(core_path, sep='\t', low_memory=False)
nurse = pd.read_csv(nurse_path, sep='\t')
derived = pd.read_csv(derived_path, sep='\t')

# HESka - smoking cigarettes currently 
"""
Value = 1.0	Label = Yes
Value = 2.0	Label = No
Value = -9.0	Label = Refusal
Value = -8.0	Label = Don't know
Value = -1.0	Label = Not applicable
"""
# HeSmk - ever smoked cigarettes
"""
Value = 1.0	Label = Yes
Value = 2.0	Label = No
Value = -9.0	Label = Refusal
Value = -8.0	Label = Don't know
Value = -4.0	Label = Did respond at w1 but were asked
Value = -3.0	Label = Did not respond at w1 but were not asked
Value = -1.0	Label = Not applicable
"""
# HeActa - vig exercise
# HeActb - mod exercise
# HeActc - mild exercise
"""
Value = 1.0	Label = ...more than once a week,
Value = 2.0	Label = once a week,
Value = 3.0	Label = one to three times a month,
Value = 4.0	Label = hardly ever, or never?
Value = -9.0	Label = Refusal
Value = -8.0	Label = Don't know
Value = -1.0	Label = Not applicable
"""

core_filtered = core[
    (
        (core['HESka'] != -9) &
        (core['HESka'] != -8) &
        (core['HESka'] != -1) 
    ) &
    (
        (core['scako'] != -9) &
        (core['scako'] != -1)
    )
]

core_filtered["current_smoker"] = np.where(core_filtered['HESka'] == 1, 1, 0) 
core_filtered["aerobically_active"] = np.where((core_filtered['HeActa'] == 1) | (core_filtered['HeActb'] == 1), 1, 0)
core_filtered["regular_alcohol"] = np.where(core_filtered['scako'] <= 3, 1, 0)

core_final = core_filtered[["idauniq","current_smoker","aerobically_active","regular_alcohol"]]

# common_filtered = common[
#     (common['ethnic'] != -9) &
#     (common['ethnic'] != -8) &
#     (
#         (common['ghqsleep'] != -9) &
#         (common['ghqsleep'] != -8) &
#         (common['ghqsleep'] != -7) &
#         (common['ghqsleep'] != -6) &
#         (common['ghqsleep'] != -2) &
#         (common['ghqsleep'] != -1) 
#     ) &
#     (
#         (common['ghqstrai'] != -9) &
#         (common['ghqstrai'] != -8) &
#         (common['ghqstrai'] != -7) &
#         (common['ghqstrai'] != -6) &
#         (common['ghqstrai'] != -2) &
#         (common['ghqstrai'] != -1) 
#     )
# ]
# common_filtered["anxiety_stress"] = np.where((common_filtered['ghqsleep'] >= 3) | (common_filtered['ghqstrai'] >= 3), 1, 0) 

# common_final = common_filtered[["idauniq", "ethnic", "anxiety_stress"]]

"""
['idauniq', 'idaindw2', 'idahhw2', 'w2wtnur', 'w2wtbld', 'vismon', 'visyear', 
'hhage', 'confage', 'sex', 'dobyear', 'bpconst', 'consub1', 'consub2', 'consub3', 
'cufsize', 'airtemp', 'sys1', 'dias1', 'pulse1', 'map1', 'full1', 'sys2', 'dias2', 
'pulse2', 'map2', 'full2', 'sys3', 'dias3', 'pulse3', 'map3', 'full3', 'ynobp', 'bprespc', 
'sysval', 'diaval', 'pulval', 'mapval', 'respbps', 'nattbp1', 'nattbp2', 'difbpc1', 'difbpc2', 
'difbpc3', 'mmgswil', 'mmgsdom', 'mmgssta', 'mmgsd1', 'mmgsn1', 'mmgsd2', 'mmgsn2', 'mmgsd3', 
'mmgsn3', 'mmgstp', 'mmgsres', 'mmgspr1', 'mmgspr2', 'clotb', 'fit', 'bswill', 'fastask', 'fasteli', 
'fasthrs', 'refbsc1', 'refbsc2', 'refbsc3', 'samptak', 'bsoutc', 'samdif1', 'samdif2', 'samdif3', 'samdif4', 
'nobsm1', 'nobsm2', 'cfib', 'chol', 'hdl', 'trig', 'ldl', 'fglu', 'rtin', 'hscrp', 'apoe', 'hgb', 'hba1c', 
'bloodr', 'resphts', 'height', 'resnhi', 'ehtch', 'ehtm', 'ehtft', 'ehtin', 'estht', 'htval', 'htok', 'nohtbc1', 
'nohtbc2', 'nohtbc3', 'nohtbc4', 'relhite', 'hinrel', 'sithtrs', 'sithgt', 'respwts', 'weight', 'resnwt', 'ewtch', 
'ewtkg', 'ewtst', 'ewtl', 'estwt', 'wtval', 'wtok', 'nowtbc1', 'nowtbc2', 'nowtbc3', 'nowtbc4', 'floorc', 'relwait', 
'bmi', 'bmival', 'bmiok', 'bmiobe', 'whintro', 'waist1', 'hip1', 'waist2', 'hip2', 'waist3', 'hip3', 'wstval', 'hipval', 
'whval', 'wstokb', 'hipokb', 'whokb', 'ynowh', 'respwh', 'whpnab1', 'whpnab2', 'whpnab3', 'wjrel', 'probwj', 'hjrel', 
'probhj', 'hasurg', 'eyesurg', 'hastro', 'chestin', 'inhaler', 'inhalhr', 'lfwill', 'lftemp', 'fvc1', 'fev1', 'pf1', 
'techni1', 'fvc2', 'fev2', 'pf2', 'techni2', 'fvc3', 'fev3', 'pf3', 'techni3', 'nlsatlf', 'htfvc', 'htfev', 'htpf', 
'noread', 'ynolf', 'lfstand', 'lfresp', 'problf1', 'problf2', 'problf3', 'noattlf', 'lfnomea', 'mmbcsc', 'mmsssc', 
'mmssre', 'mmssti', 'mmssna', 'mmstsc', 'mmstre', 'mmstti', 'mmstna', 'mmftsc', 'mmftre2', 'mmftti', 'mmftna', 
'mmlosc', 'mmlore', 'mmloti', 'mmlona', 'mmlssc', 'mmlsre', 'mmlsti', 'mmlsna', 'mmcrav', 'mmcrsc', 'mmcrre', 
'mmcrna', 'mmrrsc', 'mmrrre', 'mmrrfti', 'mmrrtti', 'mmrroc', 'mmrrna']
"""

# age_groups = pd.cut(nurse['confage'], bins=[65, 70, 75, 80, 85, 90])
# age_grouped = nurse.groupby(['sex', age_groups]).agg({'chol': ['mean', 'std']})

# print(age_grouped)

nurse_filtered = nurse[
        (nurse['sex'] >= 1) &
        (nurse['confage'] >= 65) &
        (nurse["bmi"] >= 1) &
        (nurse["chol"] >= 0) &
        (nurse["hdl"] >= 0) &
        (nurse["ldl"] >= 0) &
        (nurse["trig"] >= 0) 
]

nurse_filtered.loc[:, "mean_sys"] = (nurse_filtered.loc[:, "sys1"] + nurse_filtered.loc[:, "sys2"] + nurse_filtered.loc[:, "sys3"]) / 3
nurse_filtered.loc[:, "mean_dias"] = (nurse_filtered.loc[:, "dias1"] + nurse_filtered.loc[:, "dias2"] + nurse_filtered.loc[:, "dias3"]) / 3
nurse_filtered.loc[:, "tc:hdl"] = nurse_filtered["chol"] / nurse_filtered["hdl"]
nurse_filtered.loc[:, "non_hdl"] = nurse_filtered["chol"] - nurse_filtered["hdl"]
# Normal values https://www.heartuk.org.uk/cholesterol/understanding-your-cholesterol-test-results-
nurse_filtered.loc[:, "has_dyslipidaemia"] = np.where((nurse_filtered["chol"] > 5) | (nurse_filtered["ldl"] > 3) | (nurse_filtered["hdl"] < 1.4) | (nurse_filtered["trig"] > 1.7) | (nurse_filtered["tc:hdl"] > 6) | (nurse_filtered["non_hdl"] > 4), 1, 0)
nurse_filtered.loc[:, "does_not_have_dyslipidaemia"] = np.where((nurse_filtered["chol"] < 5) & (nurse_filtered["ldl"] < 3) & (nurse_filtered["hdl"] >= 1.4) & (nurse_filtered["trig"] < 1.7) & (nurse_filtered["tc:hdl"] < 6) & (nurse_filtered["non_hdl"] < 4), 1, 0)
nurse_filtered.loc[:, "has_dyslipidaemia"] = np.where((nurse_filtered["does_not_have_dyslipidaemia"] != 1), 1, 0)

nurse_final = nurse_filtered[["idauniq", "confage", "sex", "bmi", 'chol', 'hdl', 'trig', 'ldl', "tc:hdl", "non_hdl", "has_dyslipidaemia"]]

derived_filtered = derived[
        (derived["w2edqual"] != -9) &
        (derived["w2edqual"] != -8) &
        (derived["w2edqual"] != -6) &
        (derived["w2edqual"] != 6) &
        (derived["w2edqual"] != -1)
    ]

derived_filtered["has_diabetes"] = np.where(derived_filtered["hedbts"] != 0, 1, 0)
derived_filtered["has_hypertension"] = np.where(derived_filtered["hedimdi"] != 0, 1, 0)

derived_final = derived_filtered[["idauniq", "has_hypertension", "has_diabetes"]]

df_final = reduce(lambda left,right: pd.merge(left,right,on='idauniq'), [core_final, nurse_final, derived_final])

df_final.drop(columns=["idauniq"])

df_final.to_csv('elsa/lipids/lipid_model_wrangle.csv')
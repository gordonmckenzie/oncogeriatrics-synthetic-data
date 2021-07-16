import vaex

path_p = "/Volumes/My Passport for Mac/Simulacrum/simulacrum_release_v1.2.0.2017/data/sim_av_patient.csv.hdf5"
path_t = "/Volumes/My Passport for Mac/Simulacrum/simulacrum_release_v1.2.0.2017/data/sim_av_tumour.csv.hdf5"
path_icd = "/Volumes/My Passport for Mac/Simulacrum/simulacrum_release_v1.2.0.2017/data_dictionary_files/zicd_lookup.csv.hdf5"
path_eth = "/Volumes/My Passport for Mac/Simulacrum/simulacrum_release_v1.2.0.2017/data_dictionary_files/zethnicity_lookup.csv.hdf5"
path_sact_pt = "/Volumes/My Passport for Mac/Simulacrum/simulacrum_release_v1.2.0.2017/data/sim_sact_patient.csv.hdf5"
path_sact_drug = "/Volumes/My Passport for Mac/Simulacrum/simulacrum_release_v1.2.0.2017/data/sim_sact_regimen.csv.hdf5"
#os.chdir("/Volumes/My Passport for Mac/Simulacrum/simulacrum_release_v1.2.0.2017/data/")
#dv = vaex.from_csv(path_sact_pt, convert=True, chunk_size=5_000_000)
#dv = vaex.from_csv(path_icd, convert=True)

dv_p = vaex.open(path_p)
dv_t = vaex.open(path_t)
dv_icd = vaex.open(path_icd)
dv_eth = vaex.open(path_eth)
dv_sact_pt = vaex.open(path_sact_pt)
dv_sact_drug = vaex.open(path_sact_drug)

#main = dv[[dv[dv.AGE >= 65], "SEX", "SITE_ICD10_O2", "QUINTILE_2015"]]

joined = dv_t.join(dv_p, left_on='TUMOURID', right_on='PATIENTID', rsuffix="_")

joined = joined.join(dv_icd, left_on='SITE_ICD10_O2', right_on='ZICDID', rsuffix="_")

joined = joined.join(dv_eth, left_on='ETHNICITY', right_on='ZETHNICITYID', rsuffix="_")

joined = joined.join(dv_sact_pt, left_on='LINKNUMBER', right_on='LINK_NUMBER', how='right', rsuffix="_", allow_duplication=True)

def concat_cols(dt, cols, name='concat_col', divider='|'):
    # Create the join column
    for i, col in enumerate(cols):
        if i == 0:
            dt[name] = dt[col].astype('string').fillna('')
        else:
            dt[name] = dt[name] + divider + dt[col].astype('string').fillna('')
    
    # Ensure it's a string; on rare occassions it's an object
    dt[name] = dt[name].astype('string')

    return dt, name

def vx_dedupe(dt, dedupe_cols=None, concat_first=True):
    # Make a shallow copy
    dt = dt.copy()

    # Get and join columns
    init_cols = dt.get_column_names()
    if dedupe_cols is None:
        dedupe_cols = init_cols
    if concat_first:
        dt, concat_col = concat_cols(dt, dedupe_cols)
        col_names = [concat_col]
    else:
        col_names = dedupe_cols

    # Add named sets
    sets = [dt._set(col_name) for col_name in col_names]
    counts = [set.count for set in sets]
    set_names = [dt.add_variable('set_{}'.format(col_name), set, unique=True) for col_name, set in zip(col_names, sets)]

    # Create 'row_id' column that gives each unique row the same ID
    expression = dt['_ordinal_values({}, {})'.format(col_names[0], set_names[0])].astype('int64')
    product_count = 1
    for col_name, set_name, count in zip(col_names[1:], set_names[1:], counts[:-1]):
        product_count *= count
        expression = expression + dt['_ordinal_values({}, {})'.format(col_name, set_name)].astype('int64') * product_count
    dt['row_id'] = expression

    # This is not 'stable'; because it is multithreaded, we may get a different id each time
    index = dt._index('row_id')
    unique_row_ids = dt.row_id.unique()
    indices = index.map_index(unique_row_ids)

    # Dedupe
    deduped = dt.take(indices)
    deduped = deduped[init_cols]

    return deduped

dv_sact_drug = vx_dedupe(dv_sact_drug, ['MERGED_PATIENT_ID'], concat_first=True)

joined = joined.join(dv_sact_drug, left_on='MERGED_PATIENT_ID', right_on='MERGED_PATIENT_ID', rsuffix="_")

filter_t = joined[(joined.AGE >= 65) & (((joined.SEX != 1) | (joined.SEX != 2))) & ((joined.DESC != "unknown") & (joined.DESC != "UNKNOWN")) & ((joined.STAGE_BEST != "?") | (joined.STAGE_BEST != "U")) & ((joined.MDT != "unknown") & (joined.MDT != "skin"))]

renames = {"AGE": "age", "SEX": "gender", "DESC": "ethnicity", "MDT": 'cancer_mdt', "SITE": "cancer_site", "STAGE_BEST": 'cancer_stage', 'QUINTILE_2015': 'deprivation', 'DATE_FIRST_SURGERY': 'surgery', "INTENT_OF_TREATMENT": "chemotherapy", "CHEMO_RADIATION": "chemoradiotherapy"}
for old_name,new_name in renames.items():
    filter_t.rename(old_name,new_name)

df = filter_t.to_pandas_df(["age", "gender", "ethnicity", "deprivation", "cancer_mdt", "cancer_site", "cancer_stage", "surgery", "chemotherapy", "chemoradiotherapy"])

df['deprivation'] = df['deprivation'].apply(lambda x: x.split(' ')[0])

df['gender'] = df['gender'].apply(lambda x: 'm' if x == 1 else 'f')

df['surgery'] = df['surgery'].apply(lambda x: 0 if x is None else 1)

df['chemotherapy'] = df['chemotherapy'].fillna(0)
df['chemoradiotherapy'] = df['chemoradiotherapy'].fillna(0)

df['chemoradiotherapy'] = df['chemoradiotherapy'].apply(lambda x: 0 if (x == None or x == 'N' or x == 0) else 1)

df['chemotherapy'] = df['chemotherapy'].apply(lambda x: 0 if (x == None or x == 0) else 1)

#print(len(df[["age", "gender", "ethnicity", "deprivation", "cancer_mdt", "cancer_site", "cancer_stage", "surgery", "chemotherapy", "chemoradiotherapy"]]))

df.to_hdf('data/simulacrum.h5', key='simulacrum', mode='w')

import pandas as pd

workbook = "./assets/data/utrc_report_2021-09-01_to_2021-10-01.xlsx"
worksheets = [
    'utrc_active_allocations', # 0
    'utrc_individual_user_hpc_usage', # 1
    'utrc_corral_usage', # 2
    'utrc_current_allocations', # 3
    'utrc_new_pis', # 4
    'utrc_new_allocation_requests', # 5
    'utrc_new_users', # 6
    'utrc_idle_users', # 7
    'utrc_suspended_users', # 8
    'utrc_new_grants', # 9
    'utrc_new_publications', # 10
    'utrc_institution_accounts' # 11
]

INSTITUTIONS = {
    'University of Texas at Austin': 'UTAus',
    'University of Texas - Austin': 'UTAus',
    'University of Texas, Austin': 'UTAus',
    'The University of Texas at Austin': 'UTAus',
    'The University of Texas Austin': 'UTAus',
    'Dell Medical School, University of Texas at Austin': 'UTAus',
    'University of Texas at Arlington': 'UTA',
    'University of Texas Arlington': 'UTA',
    'The University of Texas at Arlington': 'UTA',
    'University of Texas at Dallas': 'UTD',
    'The University of Texas at Dallas': 'UTD',
    'University of Texas at El Paso': 'UTEP',
    'The University of Texas at El paso': 'UTEP',
    'University of Texas, El Paso': 'UTEP',
    'University of Texas of the Permian Basin': 'UTPB',
    'University of Texas Rio Grande Valley': 'UTRGV',
    'The University of Texas - Rio Grande Valley': 'UTRGV',
    'University of Texas - Rio Grande Valley': 'UTRGV',
    'University of Texas at San Antonio': 'UTSA',
    'The University of Texas at San Antonio': 'UTSA',
    'University of Texas at Tyler': 'UTT',
    'University of Texas Health Science Center at Houston': 'UTHSC-H',
    'The University of Texas Health Science Center at Houston': 'UTHSC-H',
    'University of Texas, Houston': 'UTHSC-H',
    'University of Texas Health Science Center at San Antonio': 'UTHSC-SA',
    'University of Texas Health Science Center, San Antonio': 'UTHSC-SA',
    'University of Texas Health Science Center in San Antonio': 'UTHSC-SA',
    'University of Texas Health Science Center at Tyler': 'UTT',
    'University of Texas Medical Branch': 'UTMB',
    'University of Texas M. D. Anderson Cancer Center': 'UTMDA',
    'University of Texas MD Anderson Cancer Center': 'UTMDA',
    'The University of Texas MD Anderson Cancer Center': 'UTMDA',
    'University of Texas Southwestern Medical Center': 'UTSW',
    'University of Texas at Brownsville': 'UTRGV',
    'University of Texas Pan-American': 'UTRGV',
    'University of Texas System': 'UTSYS',
    'University of Texas System Administration': 'UTSYS',
    'The University of Texas System Administration': 'UTSYS',
    'University of Texas at Arlington (UTA) (UT Arlington)': 'UTA',
    'University of Texas at Austin (UT) (UT Austin)': 'UTAus',
    'University of Texas at Austin Dell Medical School': 'UTAus',
    'University of Texas at Dallas (UTD) (UT Dallas)': 'UTD',
    'University of Texas at El Paso (UTEP)': 'UTEP',
    'University of Texas at San Antonio': 'UTSA',
    'University of Texas Health Science Center at Houston': 'UTHSC-H',
    'University of Texas Health Science Center at San Antonio': 'UTHSC-SA',
    'University of Texas Health Science Center at Tyler': 'UTT',
    'University of Texas MD Anderson Cancer Center': 'UTMDA',
    'University of Texas Medical Branch at Galveston': 'UTMB',
    'University of Texas Permian Basin': 'UTPB',
    'University of Texas Rio Grande Valley': 'UTRGV',
    'University of Texas Southwestern Medical Center (UTSW) (UT Southwestern)': 'UTSW',
    'University of Texas System': 'UTSYS',
    'University of Texas Tyler': 'UTT',
}

df = pd.read_excel(workbook, worksheets[6])

#df = df.groupby(['root_institution_name'], as_index=False)['account_type'].sum()
#print("Total: " + df.sum())
# print(df.shape[0]) # Get count of rows
# df = df.groupby(['root_institution_name'])['root_institution_name'].count() # Get count of rows, grouped by institution
# print(df.sort_values(ascending=False)) # Sorted

for i in range(len(df)):
    df.loc[i, "root_institution_name"] = INSTITUTIONS[df.loc[i, "root_institution_name"]]

print(df)
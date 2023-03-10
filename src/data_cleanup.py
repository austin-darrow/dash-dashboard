import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG)

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

WORKSHEETS = [
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

PROTECTED_COLUMNS = [
    'email',
    'Email',
    'login',
    'Login',
    'account_id',
    'Account ID',
    'project_pi_email',
    'PI Email'
]

def clean_df(df):
    df = df.rename({'root_institution_name': 'Institution',
                'last_name': 'Last Name',
                'first_name': 'First Name',
                'email': 'Email',
                'login': 'Login',
                'account_id': 'Account ID',
                'account_type': 'Account Type',
                'active_date': 'Active Date',
                'changed': 'Changed',
                'comment': 'Comment',
                'resource_name': 'Resource',
                'resource_type': 'Type',
                'project_name': 'Project Name',
                'title': 'Title',
                'project_type': 'Project Type',
                'jobs': 'Job Count',
                'sus_charged': 'SU\'s Charged',
                'users': 'User Count',
                'New PI?': 'New PI?',
                'New User?': 'New User?',
                'Suspended User?': 'Suspended User?',
                'name': 'Name',
                'start_date': 'Start Date',
                'end_date': 'End Date',
                'status': 'Status',
                'storage_granted_gb': 'Storage Granted (Gb)',
                'total_granted': 'Total Granted',
                'total_refunded': 'Total Refunded',
                'total_used': 'Total Used',
                'balance': 'Balance',
                'Idle Allocation?': 'Idle Allocation?',
                'primary_field': 'Primary Field',
                'secondary_field': 'Secondary Field',
                'grant_title': 'Grant Title',
                'funding_agency': 'Funding Agency',
                'pi_name': 'PI Name',
                'project_pi_last_name': 'PI Last Name',
                'project_pi_first_name': 'PI First Name',
                'project_pi_email': 'PI Email',
                'project_title': 'Project Title',
                'publication_id': 'Publication ID',
                'year_published': 'Year Published',
                'publisher': 'Publisher',
                'account_status': 'Account Status'
            }, axis='columns')

    for i in range(len(df)):
        df.loc[i, "Institution"] = INSTITUTIONS[df.loc[i, "Institution"]]
    
    return df

def select_df(workbook, dropdown_selection, authenticated=False):
    if dropdown_selection == 'new_users':
        df = pd.read_excel(workbook, WORKSHEETS[6])
    elif dropdown_selection == 'idle_users':
        df = pd.read_excel(workbook, WORKSHEETS[7])
    elif dropdown_selection == 'suspended_users':
        df = pd.read_excel(workbook, WORKSHEETS[8])

    if authenticated==False:
        for column in PROTECTED_COLUMNS:
            try:
                df = df.drop(columns=column)
            except Exception as e:
                logging.debug(e)
                continue

    return df
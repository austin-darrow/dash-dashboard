import pandas as pd
import logging
from os import walk
import re
from datetime import datetime

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
    'The University of Texas Rio Grande Valley': 'UTRGV',
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
    'UTAus': 'UTAus',
    'UTA': 'UTA',
    'UTMDA': 'UTMDA',
    'UTD': 'UTD',
    'UTSW': 'UTSW',
    'UTSA': 'UTSA',
    'UTT': 'UTT',
    'UTSYS': 'UTSYS',
    'UTHSC-H': 'UTHSC-H',
    'UTHSC-SA': 'UTHSC-SA',
    'UTMB': 'UTMB',
    'UTPB': 'UTPB',
    'UTRGV': 'UTRGV',
    'UTEP': 'UTEP'
}

COLUMN_HEADERS = {
    'root_institution_name': 'Institution',
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
    'Suspended User?': 'Suspended?',
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
}

PROTECTED_COLUMNS = [
    'email',
    'Email',
    'login',
    'Login',
    'account_id',
    'Account ID',
    'project_pi_email',
    'PI Email',
    'last_name',
    'Last Name',
    'first_name',
    'First Name'
]

def get_fiscal_year_dates(fiscal_year):
    start = fiscal_year.split('-')[0]
    start_months = ['09', '10', '11', '12']
    end = fiscal_year.split('-')[1]
    end_months = ['01', '02', '03', '04', '05', '06', '07', '08']
    dates = []
    for month in start_months:
        dates.append(f'{start}-{month}')
    for month in end_months:
        dates.append(f'{end}-{month}')
    return dates

def get_workbook_paths(directory):
    f = []
    for (dirpath, _, filenames) in walk(directory):
        for filename in filenames:
            if filename.endswith('.xlsx'):
                f.append(dirpath + "/" + filename)
        break
    return f

def append_date_to_worksheets(workbook, filename):
    for worksheet in workbook:
        workbook[worksheet]['Date'] = get_date_from_filename(filename)
    return workbook

def get_date_from_filename(filename, prefix='utrc_report'):
    # utrc_report_2017-01-01_to_2017-02-01.xlsx
    pattern = re.compile('{}_(.*)_to_(.*).xlsx'.format(prefix))
    match = pattern.match(filename)
    series_date = ''
    if match:
        start_date_str = match.group(1)
        date = datetime.strptime(start_date_str, '%Y-%m-%d')
        series_date = date.strftime('%y-%m')
    return series_date

def clean_df(df):
    # Rename worksheet table headers
    df.rename(columns=COLUMN_HEADERS, inplace=True)
    df.dropna(subset='Institution', inplace=True)
    df.drop(df.columns[df.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)

    # Replace full institution names with abbreviations
    for i in range(len(df)):
        df.loc[i, "Institution"] = INSTITUTIONS[df.loc[i, "Institution"]]

    # Remove duplicates from individual sheets
    try:
        df.drop_duplicates(subset=['Login'], inplace=True)
    except:
        pass # Some worksheets do not have a login column

def filter_df(df, checklist, date_range, fiscal_year):
    filtered_df = df[df['Institution'].isin(checklist)]
    filtered_df = filtered_df[filtered_df['Date'].isin(get_dates_from_range(date_range, fiscal_year))]
    
    filtered_df.sort_values(['Date', 'Institution'], inplace=True)

    return filtered_df

def select_df(DATAFRAMES, dropdown_selection, checklist, date_range, fiscal_year, authenticated=False):
    """ Given a list of filter inputs, returns a filtered dataframe. Removes
        sensitive data before returning if a user has not been authenticated. """
    df = DATAFRAMES[dropdown_selection]

    if authenticated==False:
        for column in PROTECTED_COLUMNS:
            try:
                df = df.drop(columns=column)
            except: # Throws error if column name isn't in specific worksheets
                continue

    df = filter_df(df, checklist, date_range, fiscal_year)

    return df

def get_totals(DATAFRAMES, checklist, date_range, fiscal_year, worksheets):
    """ Given a dictionary of dataframes, a checklist of selected universities,
        and a date range of selected months, returns a dictionary of total, active
        and idle users in the last selected month. """
    totals = {}
    for worksheet in worksheets:
        df = DATAFRAMES[worksheet]
        filtered_df = filter_df(df, checklist, date_range, fiscal_year)
        inst_grps = filtered_df.groupby(['Institution'])
        avgs = []
        for group in checklist:
            try:
                avgs.append(inst_grps.get_group(group)['Date'].value_counts().mean())
            except:
                continue
        user_count = int(sum(avgs))

        if worksheet == 'utrc_individual_user_hpc_usage':
            totals['active_users'] = user_count
        elif worksheet == 'utrc_idle_users':
            totals['idle_users'] = user_count

    return totals

def get_marks(fiscal_year):
    """ Returns a dictionary, where keys are an integer representing a month,
        and values are a string representation of '%y-%m' (e.g. '21-09') """
    marks = {}
    workbook_paths = get_workbook_paths('./assets/data/monthly_reports')
    workbook_paths.sort()
    count = 0
    for path in workbook_paths:
        filename = path.split('/')[-1]
        date = get_date_from_filename(filename)
        if date in get_fiscal_year_dates(fiscal_year):
            marks[count] = date
            count += 1
    return marks

def get_dates_from_range(date_range, fiscal_year):
    """ Given a list with a starting and ending integer, returns a list of
        all dates in the filelist. """
    fy_dates = get_fiscal_year_dates(fiscal_year)
    dates = []
    workbook_paths = get_workbook_paths('./assets/data/monthly_reports')
    workbook_paths.sort()
    for path in workbook_paths:
        filename = path.split('/')[-1]
        date = get_date_from_filename(filename)
        if date in fy_dates:
            dates.append(date)
    
    return dates[date_range[0]:(date_range[1]+1)]
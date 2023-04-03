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

NODE_HOURS_MODIFIER = {
    'Longhorn2': 0,
    'Stampede3': 0,
    'Maverick2': 0,
    'Jetstream': 0.04,
    'Chameleon': 0.04,
    'Lonestar4': 0,
    'Lonestar5': 1,  # everything relative to LS5
    'Wrangler3': 0,
    'Stampede4': 2,
    'Hikari': 0.04,
    'Maverick3': 1,
    'Frontera': 3,
    'Longhorn3': 3,
    'lonestar6': 4.5,
    'Lonestar6': 4.5
}

WORKSHEETS_RM_DUPLICATES = [
    'utrc_individual_user_hpc_usage',
    'utrc_new_users',
    'utrc_idle_users'
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

def remove_duplicates(df):
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

def calc_monthly_avgs(df, checklist):
    inst_grps = df.groupby(['Institution'])
    df_with_avgs = {'Institution': [], 'Date': []}
    for group in checklist:
        try:
            monthly_avg = inst_grps.get_group(group)['Date'].value_counts().mean()
            for i in range(int(monthly_avg)):
                df_with_avgs['Institution'].append(group)
                df_with_avgs['Date'].append('AVG')
        except:
            continue # For some date ranges, even if an institution is checked, it doesn't appear in the data, throwing an error
    combined_df = pd.concat([df, pd.DataFrame(df_with_avgs)])
    return combined_df

def calc_node_hours(df):
    for i in range(len(df)):
        df.loc[i, "SU's Charged"] = (df.loc[i, "SU's Charged"] * NODE_HOURS_MODIFIER[df.loc[i, "Resource"]])
    return df

def calc_node_fy_sums(df, checklist):
    inst_grps = df.groupby(['Institution'])
    df_with_avgs = {'Institution': [], 'Date': [], "SU's Charged": []}
    for group in checklist:
        try:
            sum = inst_grps.get_group(group)["SU's Charged"].sum()
            df_with_avgs['Institution'].append(group)
            df_with_avgs["SU's Charged"].append(round(sum))
            df_with_avgs['Date'].append('FYTD SUM')
        except:
            continue # For some date ranges, even if an institution is checked, it doesn't appear in the data, throwing an error
    combined_df = pd.concat([df, pd.DataFrame(df_with_avgs)])
    return combined_df

def calc_node_monthly_sums(df, checklist, column):
    inst_grps = df.groupby(['Institution'])
    df_with_avgs = {'Institution': [], 'Date': [], column: []}
    for group in checklist:
        try:
            date_grp = inst_grps.get_group(group).groupby(['Date'])
            for date in date_grp.groups.keys():
                if column == 'Storage Granted (TB)':
                    monthly_sum = date_grp.get_group(date)['Storage Granted (Gb)'].sum()
                    monthly_sum = int(round(monthly_sum/1024.0))
                else:
                    monthly_sum = date_grp.get_group(date)[column].sum()
                df_with_avgs['Institution'].append(group)
                df_with_avgs[column].append(round(monthly_sum))
                df_with_avgs['Date'].append(date)
        except:
            continue
    df_with_avgs = pd.DataFrame(df_with_avgs)
    df_with_avgs.sort_values(['Date', 'Institution'], inplace=True)
    return df_with_avgs

def create_fy_options():
    paths = get_workbook_paths('./assets/data/monthly_reports')
    dates = []
    for path in paths:
        filename = path.split('/')[-1]
        dates.append(get_date_from_filename(filename))

    fy_options = []
    start_months = ['09', '10', '11', '12']
    end_months = ['01', '02', '03', '04', '05', '06', '07', '08']
    for date in dates:
        year = date.split('-')[0]
        month = date.split('-')[1]
        if month in start_months:
            option = f'{year}-{int(year)+1}'
        elif month in end_months:
            option = f'{int(year)-1}-{year}'
        if option not in fy_options:
            fy_options.append(option)
    fy_options.sort()

    return fy_options

def create_conditional_style(df):
    """
    Necessary workaround for a Plotly Dash bug where table headers are cut off if row data is shorter than the header.
    """
    style=[]
    for col in df.columns:
        name_length = len(col)
        pixel = 30 + round(name_length*8)
        pixel = str(pixel) + "px"
        style.append({'if': {'column_id': col}, 'minWidth': pixel})

    return style
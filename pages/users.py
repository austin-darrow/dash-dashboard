import pandas as pd
import plotly.express as px

import dash
from dash import dcc, Output, Input, html, dash_table

dash.register_page(__name__)
app = dash.get_app()

# INCORPORATE DATA
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

new_users = pd.read_excel(workbook, worksheets[6])
idle_users = pd.read_excel(workbook, worksheets[7])
suspended_users = pd.read_excel(workbook, worksheets[8])
user_authenticated = False
if user_authenticated == False:
    new_users = new_users.iloc[:,[0,1,2,6,7]]
    idle_users = idle_users.iloc[:,[0,1,2,5]]
    suspended_users = suspended_users.iloc[:,[0,1,2,6,7,8]]

# CLEAN UP DATA

for i in range(len(new_users)):
    new_users.loc[i, "root_institution_name"] = INSTITUTIONS[new_users.loc[i, "root_institution_name"]]

barchart = px.bar(
    data_frame=new_users.groupby(['root_institution_name'])['root_institution_name'].count(),
    x="root_institution_name",
    y="root_institution_name",
    orientation='v',
    barmode='group'
)

# CUSTOMIZE LAYOUT
layout = html.Div([
    html.Div(
        [html.A(html.Img(src='./assets/images/tacc-white.png', className='header-img'), href='https://www.tacc.utexas.edu/'),
         html.Span(className='branding-seperator'),
         html.A(html.Img(src='./assets/images/utaustin-white.png', className='header-img'), href='https://www.utexas.edu/')],
        id='header'
    ),
    html.Div(
        [html.A(html.Img(src='./assets/images/utrc-horizontal-logo-white-simple.svg', className='utrc-logo'), href='https://utrc.tacc.utexas.edu/')],
        id='header2'
    ),
    html.Div([
        html.Div([
            dcc.Dropdown(id='dropdown',
                        options=[
                            {'label': 'New Users', 'value': 'new_users'},
                            {'label': 'Idle Users', 'value': 'idle_users'},
                            {'label': 'Suspended Users', 'value': 'suspended_users'}
                        ],
                        value='new_users',
                        clearable=False
            ),
        ],),
        
        html.Div(children=[
            dcc.Graph(figure=px.histogram(
                data_frame=new_users,
                x="root_institution_name",
                color='account_type'
            )),
        ], id='bargraph'),

        html.Div([], id='table'),
    ], className='body')
])

# ADD INTERACTIVITY THROUGH CALLBACKS
@app.callback(
    Output('table', 'children'),
    Input('dropdown', 'value')
)
def update_table(dropdown):
    if dropdown == 'new_users':
        df = pd.read_excel(workbook, worksheets[6])
        data_columns = ['Institution', 'Last Name', 'First Name', 'Email', 'Login', 'Account ID', 'Account Type', 'Active Date']
        df_columns = ['root_institution_name', 'last_name', 'first_name', 'email', 'login', 'account_id', 'account_type', 'active_date']
    elif dropdown == 'idle_users':
        df = pd.read_excel(workbook, worksheets[7])
        data_columns = ['Institution', 'Last Name', 'First Name', 'Email', 'Login', 'Account Type']
        df_columns = ['root_institution_name', 'last_name', 'first_name', 'email', 'login', 'account_type']
    elif dropdown == 'suspended_users':
        df = pd.read_excel(workbook, worksheets[8])
        data_columns = ['Institution', 'Last Name', 'First Name', 'Email', 'Login', 'Account ID', 'Account Type', 'Changed', 'Comment']
        df_columns = ['root_institution_name', 'last_name', 'first_name', 'email', 'login', 'account_id', 'account_type', 'changed', 'comment']

    for i in range(len(df)):
        df.loc[i, "root_institution_name"] = INSTITUTIONS[df.loc[i, "root_institution_name"]]
    
    table = dash_table.DataTable(id='datatable_id',
                             data=df.to_dict('records'),
                             columns=[{
                                'name': col, 
                                'id': df_columns[idx]
                                } for (idx, col) in enumerate(data_columns)],
                             fixed_rows={'headers': True},
                             page_size=200,
                             style_header={'backgroundColor': '#222222', 'text_align': 'center'},
                             style_cell={'text_align': 'left'},
                             style_data_conditional=
                                [{
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': '#f4f4f4',
                                }],
                             sort_action='native',
                             filter_action='native'
        )
    return table
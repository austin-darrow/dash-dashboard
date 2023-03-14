import pandas as pd
import plotly.express as px

import dash
from dash import dcc, Output, Input, html, dash_table
from src.data_cleanup import clean_df, select_df, get_totals
import logging

logging.basicConfig(level=logging.DEBUG)

dash.register_page(__name__)
app = dash.get_app()

# INCORPORATE DATA
WORKBOOK = "./assets/data/utrc_report_2021-09-01_to_2021-10-01.xlsx"

def initialize_df(workbook):
    """
    To keep the dashboard running quickly, data should be read in only once.
    """
    dataframes = pd.read_excel(workbook, ['utrc_individual_user_hpc_usage', 'utrc_new_users', 'utrc_idle_users', 'utrc_suspended_users'])
    for worksheet in dataframes:
        try:
            dataframes[worksheet] = clean_df(dataframes[worksheet])
        except:
            continue

    return dataframes

DATAFRAMES = initialize_df(WORKBOOK)
logging.debug(len(DATAFRAMES))

# CUSTOMIZE LAYOUT
layout = html.Div([
    html.Div([
        html.Div([
            "Select institutions to display:",
            dcc.Checklist(
                id='select_institutions_checklist',
                options=[
                    {'label': 'UTA', 'value': 'UTA'},
                    {'label': 'UTAus', 'value': 'UTAus'},
                    {'label': 'UTHSC-SA', 'value': 'UTHSC-SA'},
                    {'label': 'UTSW', 'value': 'UTSW'},
                    {'label': 'UTHSC-H', 'value': 'UTHSC-H'},
                    {'label': 'UTMDA', 'value': 'UTMDA'},
                    {'label': 'UTRGV', 'value': 'UTRGV'},
                    {'label': 'UTMB', 'value': 'UTMB'},
                    {'label': 'UTD', 'value': 'UTD'},
                    {'label': 'UTSA', 'value': 'UTSA'},
                    {'label': 'UTEP', 'value': 'UTEP'},
                    {'label': 'UTPB', 'value': 'UTPB'},
                    {'label': 'UTT', 'value': 'UTT'},
                    {'label': 'UTSYS', 'value': 'UTSYS'}
                ],
                value=['UTA', 'UTAus', 'UTHSC-SA', 'UTSW', 'UTHSC-H', 'UTMDA', 'UTRGV', 'UTMB', 'UTD', 'UTSA', 'UTEP', 'UTT', 'UTSYS', 'UTPB'],
                persistence=True,
                persistence_type='session'
            ),
        ], id='select_institutions_div'),

        html.Div([
            "Select date range (slider?)",
        ], id='date_range_selector'),
        
        html.Div([
            html.Div([html.Div(["Total Users"], className='counter_title'), html.Div([0], id='total_users')], className="total_counters"),
            html.Div([html.Div(["Active Users"], className='counter_title'), html.Div([0], id='active_users')], className="total_counters"),
            html.Div([html.Div(["Idle Users"], className='counter_title'), html.Div([0], id="idle_users")], className="total_counters"),
        ], id='total_counters_wrapper'),

        html.Div([
            dcc.Dropdown(id='dropdown',
                        options=[
                            {'label': 'Active Users', 'value': 'utrc_individual_user_hpc_usage'},
                            {'label': 'New Users', 'value': 'utrc_new_users'},
                            {'label': 'Idle Users', 'value': 'utrc_idle_users'},
                            {'label': 'Suspended Users', 'value': 'utrc_suspended_users'}
                        ],
                        value='utrc_individual_user_hpc_usage',
                        clearable=False
            ),
        ],),
        
        html.Div([], id='bargraph'),

        html.Div([], id='table'),
    ], className='body')
])

# ADD INTERACTIVITY THROUGH CALLBACKS
@app.callback(
    Output('table', 'children'),
    Output('bargraph', 'children'),
    Output('active_users', 'children'),
    Output('idle_users', 'children'),
    Output('total_users', 'children'),
    Input('dropdown', 'value'),
    Input('hidden-login', 'data'),
    Input('select_institutions_checklist', 'value')
)
def update_figs(dropdown, authentication, checklist):
    df = select_df(DATAFRAMES, dropdown, checklist, authentication)
    
    table = dash_table.DataTable(id='datatable_id',
                             data=df.to_dict('records'),
                             columns=[{"name": i, "id": i} for i in df.columns],
                             fixed_rows={'headers': True},
                             page_size=200,
                             style_header={'backgroundColor': '#222222', 'text_align': 'center'},
                             style_cell={'text_align': 'left'},
                             style_data_conditional=
                                [{
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': '#f4f4f4',
                                }],
                             style_cell_conditional=create_conditional_style(df),
                             sort_action='native',
                             filter_action='native'
        )
    
    bargraph = dcc.Graph(figure=px.histogram(
                data_frame=df,
                x="Institution",
                color='Institution'
            ))
    
    totals = get_totals(DATAFRAMES, checklist)


    return table, bargraph, totals['active_users'], totals['idle_users'], totals['total_users']







########## Utility methods ##########
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
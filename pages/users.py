import pandas as pd
import plotly.express as px

import dash
from dash import dcc, Output, Input, html, dash_table
from src.data_cleanup import clean_df, select_df, get_totals, append_date_to_worksheets, get_workbook_paths, get_marks
import logging

logging.basicConfig(level=logging.DEBUG)

dash.register_page(__name__)
app = dash.get_app()

# INCORPORATE DATA

def initialize_df(workbook_path):
    """
    To keep the dashboard running quickly, data should be read in only once.
    """
    dataframes = pd.read_excel(workbook_path, ['utrc_individual_user_hpc_usage', 'utrc_new_users', 'utrc_idle_users', 'utrc_suspended_users'])
    for worksheet in dataframes:
        dataframes[worksheet] = clean_df(dataframes[worksheet])

    return dataframes

def merge_workbooks():
    workbook_paths = get_workbook_paths('./assets/data/monthly_reports')
    for index, path in enumerate(workbook_paths):
        workbook = initialize_df(path)
        filename = path.split('/')[-1]
        workbook = append_date_to_worksheets(workbook, filename)

        if index == 0:
            dict_of_dfs = workbook
        else:
            for sheet in ['utrc_individual_user_hpc_usage', 'utrc_new_users', 'utrc_idle_users', 'utrc_suspended_users']:
                dict_of_dfs[sheet] = pd.concat([dict_of_dfs[sheet], workbook[sheet]])

    # for df in dict_of_dfs:
    #     dict_of_dfs[df] = dict_of_dfs[df].drop_duplicates(subset=['Login'])

    return dict_of_dfs

DATAFRAMES = merge_workbooks()


# CUSTOMIZE LAYOUT
layout = html.Div([
    html.Div([
        html.Div([
            "Select Filters",
            html.Div([
                "By institution:",
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
                "By date:",
                dcc.RangeSlider(id='date_filter', value=[0, len(get_marks())], step=None, marks=get_marks(), min=0, max=len(get_marks())-1)
            ], id='date_range_selector'),], id='filters'),
        
        html.Div([
            html.Div([html.Div(["Total Users"], className='counter_title'), html.Div([0], id='total_users')], className="total_counters"),
            html.Div([html.Div(["Active"], className='counter_title'), html.Div([0], id='active_users')], className="total_counters"),
            html.Div([html.Div(["Idle"], className='counter_title'), html.Div([0], id="idle_users")], className="total_counters"),
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
    Input('select_institutions_checklist', 'value'),
    Input('date_filter', 'value')
)
def update_figs(dropdown, authentication, checklist, date_range):
    logging.debug(date_range)
    df = select_df(DATAFRAMES, dropdown, checklist, date_range, authentication)
    
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
                color='Date',
                barmode='group',
                text_auto=True
            ))
    
    totals = get_totals(DATAFRAMES, checklist, date_range)


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
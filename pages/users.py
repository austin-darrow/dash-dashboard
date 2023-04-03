import pandas as pd
import plotly.express as px

import dash
from dash import dcc, Output, Input, html, dash_table, ctx
from src.data_cleanup import *
import logging

logging.basicConfig(level=logging.DEBUG)

dash.register_page(__name__)
app = dash.get_app()

# INCORPORATE DATA
FY_OPTIONS = create_fy_options()

def initialize_df(workbook_path):
    """
    To keep the dashboard running quickly, data should be read in only once.
    """
    dataframes = pd.read_excel(workbook_path, ['utrc_individual_user_hpc_usage', 'utrc_new_users', 'utrc_idle_users', 'utrc_suspended_users'])
    for worksheet in dataframes:
        clean_df(dataframes[worksheet])
        if worksheet in WORKSHEETS_RM_DUPLICATES:
            remove_duplicates(dataframes[worksheet])

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

    return dict_of_dfs

DATAFRAMES = merge_workbooks()


# CUSTOMIZE LAYOUT
layout = html.Div([
    html.Div([
        html.Div([
            html.Div([html.Div(["Avg Total Users"], className='counter_title'), html.Div([0], id='total_users')], className="total_counters"),
            html.Div([html.Div(["Avg Active"], className='counter_title'), html.Div([0], id='active_users')], className="total_counters"),
            html.Div([html.Div(["Avg Idle"], className='counter_title'), html.Div([0], id="idle_users")], className="total_counters"),
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
        
        html.Div(children=[], id='bargraph'),

        html.Div(children=[], id='table'),
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
    Input('date_filter', 'value'),
    Input('year_radio_dcc', 'value')
)
def update_figs(dropdown, authentication, checklist, date_range, fiscal_year):
    marks = get_marks(fiscal_year)
    if ctx.triggered_id == 'year_radio_dcc':
        df = select_df(DATAFRAMES, dropdown, checklist, [0, len(marks)], fiscal_year, authentication)
    else:
        df = select_df(DATAFRAMES, dropdown, checklist, date_range, fiscal_year, authentication)

    table = dash_table.DataTable(id='datatable_id',
                                 data=df.to_dict('records'),
                                 columns=[{"name": i, "id": i} for i in df.columns],
                                 fixed_rows={'headers': True},
                                 page_size=200,
                                 style_header={'backgroundColor': '#222222', 'text_align': 'center'},
                                 style_cell={'text_align': 'left'},
                                 style_data_conditional=[{
                                                    'if': {'row_index': 'odd'},
                                                    'backgroundColor': '#f4f4f4',
                                                }],
                                 style_cell_conditional=create_conditional_style(df),
                                 sort_action='native',
                                 filter_action='native'
                            )
    
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


    bargraph = dcc.Graph(figure=px.histogram(
                         data_frame=combined_df,
                         x="Institution",
                         color='Date',
                         barmode='group',
                         text_auto=True
                    ))
    
    totals = get_totals(DATAFRAMES, checklist, date_range, fiscal_year, ['utrc_individual_user_hpc_usage', 'utrc_idle_users'])
    totals['total_users'] = totals['active_users'] + totals['idle_users']
    
    return table, bargraph, totals['active_users'], totals['idle_users'], totals['total_users']
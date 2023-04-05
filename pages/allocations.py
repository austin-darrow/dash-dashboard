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
WORKSHEETS = ['utrc_active_allocations', 'utrc_individual_user_hpc_usage', 'utrc_corral_usage', 'utrc_current_allocations', 'utrc_new_allocation_requests']
FY_OPTIONS = create_fy_options()
logging.debug(f'FY Options: {FY_OPTIONS}')

def initialize_df(workbook_path):
    """
    To keep the dashboard running quickly, data should be read in only once.
    """
    dataframes = pd.read_excel(workbook_path, WORKSHEETS)
    for worksheet in dataframes:
        clean_df(dataframes[worksheet])
        if worksheet in WORKSHEETS_RM_DUPLICATES:
            remove_duplicates(dataframes[worksheet])
        if worksheet == 'utrc_active_allocations':
            dataframes[worksheet] = calc_node_hours(dataframes[worksheet])

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
            for sheet in WORKSHEETS:
                dict_of_dfs[sheet] = pd.concat([dict_of_dfs[sheet], workbook[sheet]])

    return dict_of_dfs

DATAFRAMES = merge_workbooks()

layout=html.Div([
    # TOTALS
    html.Div([
            html.Div([html.Div(["Avg Total Allocations"], className='counter_title'), html.Div([0], id='total_allocations')], className="total_counters"),
            html.Div([html.Div(["Avg Active"], className='counter_title'), html.Div([0], id='active_allocations')], className="total_counters"),
            html.Div([html.Div(["Avg Idle"], className='counter_title'), html.Div([0], id="idle_allocations")], className="total_counters"),
        ], id='total_counters_wrapper'),
    # END TOTALS

    # DROPDOWN
    html.Div([
        dcc.Dropdown(id='dropdown',
                        options=[
                        {'label': 'Active Allocations', 'value': 'utrc_active_allocations'},
                        {'label': 'Current Allocations', 'value': 'utrc_current_allocations'},
                        {'label': 'New Allocations', 'value': 'utrc_new_allocation_requests'},
                        {'label': 'Corral Usage', 'value': 'utrc_corral_usage'}
                    ],
                        value='utrc_active_allocations',
                        clearable=False
                ),
        ],),
    # END DROPDOWN

    html.Div(children=[], id='allocations_bargraph', className='my_graphs'),

    html.Div(children=[], id='allocations_table', className='my_tables'),

    dcc.Location(id='url'),

], className='body')


# ADD INTERACTIVITY THROUGH CALLBACKS
@app.callback(
    Output('allocations_table', 'children'),
    Output('allocations_bargraph', 'children'),
    Output('total_allocations', 'children'),
    Output('active_allocations', 'children'),
    Output('idle_allocations', 'children'),
    Input('dropdown', 'value'),
    Input('hidden-login', 'data'),
    Input('select_institutions_checklist', 'value'),
    Input('date_filter', 'value'),
    Input('year_radio_dcc', 'value')
)
def update_figs(dropdown, authentication, checklist, date_range, fiscal_year):
    logging.debug(f'Callback trigger id: {ctx.triggered_id}')
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

    df_with_avgs = calc_monthly_avgs(df, checklist)
    bargraph = dcc.Graph(figure=px.histogram(
                         data_frame=df_with_avgs,
                         x="Institution",
                         color='Date',
                         barmode='group',
                         text_auto=True
                    ))

    
    totals = get_allocation_totals(DATAFRAMES, checklist, date_range, fiscal_year, ['utrc_active_allocations', 'utrc_current_allocations'])
    totals['total_allocations'] = totals['idle_allocations'] + totals['active_allocations']

    return table, bargraph, totals['total_allocations'], totals['active_allocations'], totals['idle_allocations']
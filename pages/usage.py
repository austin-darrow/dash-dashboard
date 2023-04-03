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

    # FILTERS
    html.Div([
            "Select Filters",
            html.Div([
                "By institution:",
                dcc.Checklist(
                    id='select_institutions_checklist',
                    options=[
                        {'label': 'UTA', 'value': 'UTA'},
                        {'label': 'UTAus', 'value': 'UTAus'},
                        {'label': 'UTD', 'value': 'UTD'},
                        {'label': 'UTEP', 'value': 'UTEP'},
                        {'label': 'UTHSC-H', 'value': 'UTHSC-H'},
                        {'label': 'UTHSC-SA', 'value': 'UTHSC-SA'},
                        {'label': 'UTMB', 'value': 'UTMB'},
                        {'label': 'UTMDA', 'value': 'UTMDA'},
                        {'label': 'UTPB', 'value': 'UTPB'},
                        {'label': 'UTRGV', 'value': 'UTRGV'},
                        {'label': 'UTSA', 'value': 'UTSA'},
                        {'label': 'UTSW', 'value': 'UTSW'}, 
                        {'label': 'UTSYS', 'value': 'UTSYS'},
                        {'label': 'UTT', 'value': 'UTT'}
                    ],
                    value=['UTA', 'UTAus', 'UTHSC-SA', 'UTSW', 'UTHSC-H', 'UTMDA', 'UTRGV', 'UTMB', 'UTD', 'UTSA', 'UTEP', 'UTT', 'UTSYS', 'UTPB'],
                    persistence=True,
                    persistence_type='session'
                ),
            ], id='select_institutions_div'),

            html.Div([
                "By fiscal year:",
                dcc.RadioItems(id='year_radio_dcc', options=FY_OPTIONS, value='21-22', inline=True)], id='year_radio_box'),

            html.Div([
                "By month:",
                dcc.RangeSlider(id='date_filter', 
                                value=[0, 12],
                                step=None, 
                                marks={0: '21-09',
                                       1: '21-10',
                                       2: '21-11',
                                       3: '21-12',
                                       4: '22-01',
                                       5: '22-02',
                                       6: '22-03',
                                       7: '22-04',
                                       8: '22-05',
                                       9: '22-06',
                                       10: '22-07',
                                       11: '22-08'}, 
                                min=0, 
                                max=11)
            ], id='date_range_selector'),],id='filters'),
    # END FILTERS

    # TOTALS
    html.Div([
            html.Div([html.Div(["Avg Total Users"], className='counter_title'), html.Div([0], id='total_users')], className="total_counters"),
            html.Div([html.Div(["Avg Active"], className='counter_title'), html.Div([0], id='active_users')], className="total_counters"),
            html.Div([html.Div(["Avg Idle"], className='counter_title'), html.Div([0], id="idle_users")], className="total_counters"),
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

    html.Div(children=[], id='usage_bargraph', className='my_graphs'),

    html.Div(children=[], id='usage_table', className='my_tables'),

    html.Div(children=[], id='node_graph')

], className='body')


# ADD INTERACTIVITY THROUGH CALLBACKS
@app.callback(
    Output('usage_table', 'children'),
    Output('usage_bargraph', 'children'),
    Output('date_range_selector', 'children', allow_duplicate=True),
    Output('node_graph', 'children'),
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
        logging.debug(f'Marks = {marks}')
        df = select_df(DATAFRAMES, dropdown, checklist, [0, len(marks)], fiscal_year, authentication)
        slider_children = ["By month:",
                       dcc.RangeSlider(id='date_filter', value=[0, len(marks)],
                                       step=None, marks=marks, min=0, max=len(marks)-1)]
    else:
        logging.debug(f'Marks = {marks}')
        logging.debug(f'date_range = {date_range}')
        df = select_df(DATAFRAMES, dropdown, checklist, date_range, fiscal_year, authentication)
        slider_children = ["By month:",
                       dcc.RangeSlider(id='date_filter', value=date_range,
                                       step=None, marks=marks, min=0, max=len(marks)-1)]

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
    
    df_with_node_sums = calc_node_sums(df, checklist)
    node_graph = dcc.Graph(figure=px.bar(
                           data_frame=df,
                           x='Institution',
                           y="SU's Charged",
                           color='Date',
                           barmode='group'
                        ))
    
    #totals = get_totals(DATAFRAMES, checklist, date_range, fiscal_year, ['utrc_individual_user_hpc_usage', 'utrc_idle_users'])
    #totals['total_users'] = totals['active_users'] + totals['idle_users']
    
    return table, bargraph, slider_children, node_graph







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
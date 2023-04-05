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
WORKSHEETS = ['utrc_active_allocations', 'utrc_corral_usage']

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
            html.Div([html.Div(["Sum SUs Used (All Machines)"], className='counter_title'), html.Div([0], id='total_sus')], className="total_counters"),
            html.Div([html.Div(["Sum Corral Storage Allocated (TB)"], className='counter_title'), html.Div([0], id='total_storage')], className="total_counters"),
        ], id='total_counters_wrapper'),
    # END TOTALS

    html.Div(children=[], id='node_graph'),

    html.Div(children=[], id='corral_graph'),

    # DROPDOWN
    html.Div([
        dcc.Dropdown(id='dropdown',
                        options=[
                        {'label': 'Active Allocations', 'value': 'utrc_active_allocations'},
                        {'label': 'Corral Usage', 'value': 'utrc_corral_usage'}
                    ],
                        value='utrc_active_allocations',
                        clearable=False
                ),
        ],),
    # END DROPDOWN

    html.Div(children=[], id='usage_table', className='my_tables'),

    dcc.Location(id='url'),

], className='body')

# ADD INTERACTIVITY THROUGH CALLBACKS
@app.callback(
    Output('usage_table', 'children'),
    Output('node_graph', 'children'),
    Output('corral_graph', 'children'),
    Output('total_sus', 'children'),
    Output('total_storage', 'children'),
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
    
    sus_df = select_df(DATAFRAMES, 'utrc_active_allocations', checklist, date_range, fiscal_year, authentication)
    sus_df_calculated = calc_node_monthly_sums(sus_df, checklist, "SU's Charged")
    total_sus = int(sus_df["SU's Charged"].sum())
    node_graph = dcc.Graph(figure=px.bar(
                           data_frame=sus_df_calculated,
                           x='Institution',
                           y="SU's Charged",
                           color='Date',
                           barmode='group',
                           text_auto=True
                        ))
    
    corral_df = select_df(DATAFRAMES, 'utrc_corral_usage', checklist, date_range, fiscal_year, authentication)
    corral_df_calculated = calc_node_monthly_sums(corral_df, checklist, "Storage Granted (TB)")
    total_storage = (int(round(corral_df["Storage Granted (Gb)"].sum() / 1024.0)))
    corral_graph = dcc.Graph(figure=px.bar(
                           data_frame=corral_df_calculated,
                           x='Institution',
                           y="Storage Granted (TB)",
                           color='Date',
                           barmode='group',
                           text_auto=True
                        ))
    
    return table, node_graph, corral_graph, "{:,}".format(total_sus), "{:,}".format(total_storage)
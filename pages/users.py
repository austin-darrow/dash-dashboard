import pandas as pd
import plotly.express as px

import dash
from dash import dcc, Output, Input, html, dash_table
from src.data_cleanup import select_df, clean_df
import logging

logging.basicConfig(level=logging.DEBUG)

dash.register_page(__name__)
app = dash.get_app()

# INCORPORATE DATA
WORKBOOK = "./assets/data/utrc_report_2021-09-01_to_2021-10-01.xlsx"

# CUSTOMIZE LAYOUT
layout = html.Div([
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
        
        html.Div([], id='bargraph'),

        html.Div([], id='table'),
    ], className='body')
])

# ADD INTERACTIVITY THROUGH CALLBACKS
@app.callback(
    Output('table', 'children'),
    Output('bargraph', 'children'),
    Input('dropdown', 'value'),
    Input('hidden-login', 'data')
)
def update_table(dropdown, authentication):
    df = select_df(WORKBOOK, dropdown, authentication)

    df = clean_df(df)
    
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
                             sort_action='native',
                             filter_action='native'
        )
    
    bargraph = dcc.Graph(figure=px.histogram(
                data_frame=df,
                x="Institution",
                color='Account Type'
            ))
    return table, bargraph
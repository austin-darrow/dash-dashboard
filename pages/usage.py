import pandas as pd
import plotly.express as px

import dash
from dash import dcc, Output, Input, html, dash_table
from src.data_cleanup import clean_df, select_df, get_totals, append_date_to_worksheets, get_workbook_paths, get_marks
import logging

logging.basicConfig(level=logging.DEBUG)

dash.register_page(__name__)
app = dash.get_app()

layout=html.Div()
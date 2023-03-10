import dash
from dash import html

dash.register_page(__name__, path='/')
app = dash.get_app()

layout = html.Div(["Documentation will go here"], className="body")
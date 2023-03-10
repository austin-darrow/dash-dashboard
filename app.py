import dash
from dash import html, dcc
import logging

logging.basicConfig(level=logging.DEBUG)

app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True, title='UTRC Dashboard')

app.layout = html.Div([
    html.Div(
        [html.A(html.Img(src='./assets/images/tacc-white.png', className='header-img'), href='https://www.tacc.utexas.edu/'),
         html.Span(className='branding-seperator'),
         html.A(html.Img(src='./assets/images/utaustin-white.png', className='header-img'), href='https://www.utexas.edu/')
        ],
        id='header'
    ),
    html.Div(
        [html.A(html.Img(src='./assets/images/utrc-horizontal-logo-white-simple.svg', className='utrc-logo'), href='https://utrc.tacc.utexas.edu/'),
         html.A("Home", href='/'),
         html.A("Users", href='/users')
	    ],
        id='header2'
	),
	dash.page_container,
])

for page in dash.page_registry.values():
	logging.debug((f"{page['name']} - {page['path']}"))

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
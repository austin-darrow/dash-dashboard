import dash
from dash import html, dcc, Input, Output, State
import logging
from src.authenticator import authenticate

logging.basicConfig(level=logging.DEBUG)

app = dash.Dash(__name__, use_pages=True, prevent_initial_callbacks='initial_duplicate',
		suppress_callback_exceptions=True, title='UTRC Dashboard')

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
         html.A("Users", href='/users'),
		 html.A("Usage/Allocations", href='/usage'),
         html.Div([
            dcc.Input(id='username', type='text', placeholder='username'),
            dcc.Input(id='password', type='text', placeholder='password'),
            html.Button('Log in', id='login', n_clicks=0)], id='login-form'),
	    ],
        id='header2'
	),
	dcc.Store(id='hidden-login', storage_type='local'),
	dash.page_container
])

for page in dash.page_registry.values():
	logging.debug((f"{page['name']} - {page['path']}"))
	

@app.callback(
	Output('hidden-login', 'data'),
	Output('login-form', 'children'),
	Input('login', 'n_clicks'),
	State('username', 'value'),
	State('password', 'value')
)
def login(n_clicks, username, password):
	form = [dcc.Input(id='username', type='text', placeholder='username'),
			dcc.Input(id='password', type='text', placeholder='password'),
			html.Button('Log in', id='login', n_clicks=0)]
	if n_clicks is not None:
		authentication = authenticate(username, password)
		if authentication == True:
			return authentication, ""
		else:
		    return authentication, form

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
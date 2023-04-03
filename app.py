import dash
from dash import html, dcc, Input, Output, State, ctx
import logging
from src.authenticator import authenticate
from src.data_cleanup import create_fy_options, get_marks

logging.basicConfig(level=logging.DEBUG)

FY_OPTIONS = create_fy_options()

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
		 html.A("Allocations", href='/allocations'),
		 html.A("Usage", href='/usage'),
         html.Div([
            dcc.Input(id='username', type='text', placeholder='username'),
            dcc.Input(id='password', type='text', placeholder='password'),
            html.Button('Log in', id='login', n_clicks=0)], id='login-form'),
	    ],
        id='header2'
	),
	dcc.Store(id='hidden-login', storage_type='local'),
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
                dcc.RadioItems(id='year_radio_dcc',
			       			   options=FY_OPTIONS,
							   value='21-22',
							   inline=True,
							   persistence=True,
                    		   persistence_type='session')], id='year_radio_box'),

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
                                max=11,
								persistence=True,
                    			persistence_type='session')
            ], id='date_range_selector'),], id='filters'),
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


@app.callback(
	Output('date_range_selector', 'children'),
	Input('date_filter', 'value'),
	Input('year_radio_dcc', 'value')
)
def update_date_range(date_range, fiscal_year):
	logging.debug(f'Callback trigger id: {ctx.triggered_id}')
	marks = get_marks(fiscal_year)
	if ctx.triggered_id == 'year_radio_dcc':
		logging.debug(f'Marks = {marks}')
		slider_children = ["By month:",
                       dcc.RangeSlider(id='date_filter', value=[0, len(marks)],
                                       step=None, marks=marks, min=0, max=len(marks)-1)]
	else:
		logging.debug(f'Marks = {marks}')
		logging.debug(f'date_range = {date_range}')
		slider_children = ["By month:",
                       dcc.RangeSlider(id='date_filter', value=date_range,
                                       step=None, marks=marks, min=0, max=len(marks)-1)]
	return slider_children
	

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
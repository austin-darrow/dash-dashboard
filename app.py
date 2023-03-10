import dash
from dash import html, dcc

app = dash.Dash(__name__, use_pages=True, title='UTRC Dashboard')

app.layout = html.Div([
    html.Div(
        [html.A(html.Img(src='./assets/images/tacc-white.png', className='header-img'), href='https://www.tacc.utexas.edu/'),
         html.Span(className='branding-seperator'),
         html.A(html.Img(src='./assets/images/utaustin-white.png', className='header-img'), href='https://www.utexas.edu/')],
        id='header'
    ),
    html.Div([
         html.Div(dcc.Link((html.Img(src='./assets/images/utrc-horizontal-logo-white-simple.svg')), href='https://utrc.tacc.utexas.edu/')),
         html.Div(dcc.Link(f"{page['name']}", href=page["relative_path"])) for page in dash.page_registry.values()],
        id='header2'),
	dash.page_container
])

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
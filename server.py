import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import logging

from device import *
from multidevice import *

# Initialize server
app = dash.Dash(__name__)
server = app.server

# Initialize Logger
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.DEBUG)

app.logger.error('Application started')

# Initialized Devices
dev1 = Device(1)
dev2 = Device(2)
dev3 = Device(3)
#dev4 = Device(4)

def show_all_tab(hours):
    start = datetime.now()

    devices = [dev1, dev2, dev3]
    all = Multidevice(devices)

    fig_humidity, fig_temp, fig_combined = all.get_graphs(hours)

    temp = html.Div([
        html.H1(
            'All Devices', className='title'
        ),
        html.H2(
            f'Data as of: {dev1.get_time()}', className='datetime'
        ),
        html.Div([
            html.Span(f'{dev1.get_humidity()}', className='data'),
            html.Span(f'{dev1.get_devname()}: Relative Humidity', className='header')],
            className='information'
        ),
        html.Div([
            html.Span(f'{dev2.get_humidity()}', className='data'),
            html.Span(f'{dev2.get_devname()}: Relative Humidity', className='header')],
            className='information'
        ),
        html.Div([
            html.Span(f'{dev3.get_humidity()}', className='data'),
            html.Span(f'{dev3.get_devname()}: Relative Humidity', className='header')],
            className='information'
        ),
        html.Div([
            html.Span(f'{dev1.get_temperature()}', className='data'),
            html.Span(f'{dev1.get_devname()}: Temperature', className='header')], 
            className='information'
        ),
        html.Div([
            html.Span(f'{dev2.get_temperature()}', className='data'),
            html.Span(f'{dev2.get_devname()}: Temperature', className='header')], 
            className='information'
        ),
        html.Div([
            html.Span(f'{dev3.get_temperature()}', className='data'),
            html.Span(f'{dev3.get_devname()}: Temperature', className='header')], 
            className='information'
        ),
        dcc.Graph(
            figure = fig_humidity
        ),
        dcc.Graph(
            figure = fig_temp
        ),
        dcc.Graph(
            figure = fig_combined
        )
    ], 
            className='box'
        )

    end = datetime.now()
    app.logger.debug(f'Webpage rendered in: {end - start}')

    return temp

app.layout = html.Div([
    dcc.Tabs(
        id="main_tabs", 
        className='custom_tabs',
        children = [
            dcc.Tab(
                label='1 Hour Data', 
                className='tab_style',
                selected_className='tab_selected',
                children=[]
            ),
            dcc.Tab(
                label='24 Hour Data', 
                className='tab_style',
                selected_className='tab_selected',
                children=[]
            ),
            dcc.Tab(
                label='7 Day Data', 
                className='tab_style',
                selected_className='tab_selected',
                children=[]
            )
        ]        
    ), 
    html.Div(id='content')
])

@app.callback(
    Output('content', 'children'), 
    Input('main_tabs', 'value'))

def render_content(main_tabs):    
    if main_tabs == 'tab-1':
        return show_all_tab(1)
    
    elif main_tabs == 'tab-2':
        return show_all_tab(24)
    
    elif main_tabs == 'tab-3':
        return show_all_tab(168)

if __name__ == '__main__':
    #logging.basicConfig(level=app.logger.debug, format='%(asctime)s::%(levelname)s::%(filename)s::%(lineno)d::%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    app.run_server(
        debug=True,
        host='0.0.0.0')
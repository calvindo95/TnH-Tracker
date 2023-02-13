import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from device import *
import logging

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

def show_tab(device_obj: Device, fig_humidity, fig_temp, fig_combined):
    device_obj.query_last_record()

    return html.Div([
        html.H1(
            f'{device_obj.get_devname()}', className='title'
        ),
        html.H2(
            f'Data as of: {device_obj.get_time()}', className='datetime'
        ),
        html.Div([
            html.Span(f'{device_obj.get_humidity()}', className='data'),
            html.Span('Relative Humidity', className='header')],
            className='information'
        ),
        html.Div([
            html.Span(f'{device_obj.get_temperature()}', className='data'),
            html.Span('Temperature', className='header')], 
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

def show_all_tab(dev1: Device, dev2: Device, dev3: Device, fig_humidity, fig_temp, fig_combined):
    start = datetime.now()
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
    app.logger.debug(f': Webpage rendered in: {end - start}')

    return temp

app.layout = html.Div([
    dcc.Tabs(
        id="main_tabs", 
        className='custom_tabs',
        children=[
            dcc.Tab(
                label=f'All', 
                className='tab_style',
                selected_className='tab_selected',
                children=[
                    dcc.Tabs(
                        id='subtab1',
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
                    )
                ]
            ),
            dcc.Tab(
                label=f'{dev1.get_devname()}',
                className='tab_style',
                selected_className='tab_selected',
                children=[
                    dcc.Tabs(
                        id='subtab2',
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
                    )
                ]
            ),
            dcc.Tab(
                label=f'{dev2.get_devname()}', 
                className='tab_style',
                selected_className='tab_selected',
                children=[
                    dcc.Tabs(
                        id='subtab3',
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
                    )
                ]
            ),
            dcc.Tab(
                label=f'{dev3.get_devname()}', 
                className='tab_style',
                selected_className='tab_selected',
                children=[
                    dcc.Tabs(
                        id='subtab4',
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
                    )
                ]
            )
        ], 
    ), 
    html.Div(id='content')
])

@app.callback(
    Output('content', 'children'), 
    [Input('main_tabs', 'value'),
    Input('subtab1', 'value'),
    Input('subtab2', 'value'),
    Input('subtab3', 'value'),
    Input('subtab4', 'value')])

def render_content(main_tabs, subtab1, subtab2, subtab3, subtab4):
    start = datetime.now()
    if main_tabs == 'tab-1':
        all = Graph(dev1, dev2, dev3)
        
        if subtab1 == 'tab-1':
            fig_humidity, fig_temp, fig_combined = all.get_graphs(60)
        
        elif subtab1 == 'tab-2':
            fig_humidity, fig_temp, fig_combined = all.get_graphs(1440)
        
        elif subtab1 == 'tab-3':
            fig_humidity, fig_temp, fig_combined = all.get_graphs(10080)

        return show_all_tab(dev1, dev2, dev3, fig_humidity, fig_temp, fig_combined)
    
    elif main_tabs == 'tab-2':
        if subtab2 == 'tab-1':
            fig_humidity, fig_temp, fig_combined = dev1.get_graphs(60)

        elif subtab2 == 'tab-2':
            fig_humidity, fig_temp, fig_combined = dev1.get_graphs(1440)
                
        elif subtab2 == 'tab-3':
            fig_humidity, fig_temp, fig_combined = dev1.get_graphs(10080)

        end = datetime.now()
        app.logger.debug(f'Content rendered in: {end - start}')
        return show_tab(dev1, fig_humidity, fig_temp, fig_combined)

    elif main_tabs == 'tab-3':
        if subtab3 == 'tab-1':
            fig_humidity, fig_temp, fig_combined = dev2.get_graphs(60)
        
        elif subtab3 == 'tab-2':
            fig_humidity, fig_temp, fig_combined = dev2.get_graphs(1440)
        
        elif subtab3 == 'tab-3':
            fig_humidity, fig_temp, fig_combined = dev2.get_graphs(10080)

        app.logger.debug(f'Content rendered in: {end - start}')
        return show_tab(dev2, fig_humidity, fig_temp, fig_combined)

    elif main_tabs == 'tab-4':
        if subtab4 == 'tab-1':
            fig_humidity, fig_temp, fig_combined = dev3.get_graphs(60)
        
        elif subtab4 == 'tab-2':
            fig_humidity, fig_temp, fig_combined = dev3.get_graphs(1440)
        
        elif subtab4 == 'tab-3':
            fig_humidity, fig_temp, fig_combined = dev3.get_graphs(10080)

        end = datetime.now()
        app.logger.debug(f'Content rendered in: {end - start}')
        return show_tab(dev3, fig_humidity, fig_temp, fig_combined)

if __name__ == '__main__':
    #logging.basicConfig(level=app.logger.debug, format='%(asctime)s::%(levelname)s::%(filename)s::%(lineno)d::%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    app.run_server(
        debug=True,
        host='0.0.0.0')
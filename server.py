import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import mariadb
import config
import time
from device import *

def connect_to_db():
    # Connect to MariaDB Platform
    try:
        conn = mariadb.connect(
            user=config.user,
            password=config.password,
            host=config.host,
            port=config.port,
            database=config.database,
            autocommit=True
        )

        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        time.sleep(5)
        connect_to_db()

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
app = dash.Dash(__name__)
server = app.server
conn = connect_to_db()
cur = conn.cursor()

device1 = Device(cur, 1)
device2 = Device(cur, 2)

app.layout = html.Div([
    dcc.Tabs(
        id="graph_data", 
        className='custom_tabs',
        children=[
            dcc.Tab(
                label=f'{device1.get_devname()}',
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
                label=f'{device2.get_devname()}', 
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
        ], 
    ), 
    html.Div(id='content')
])

@app.callback(
    Output('content', 'children'), 
    [Input('graph_data', 'value'),
    Input('subtab1', 'value'),
    Input('subtab2', 'value')])

def render_content(tab, subtab1, subtab2):
    start = datetime.now()
    if tab == 'tab-1':
        dev = Device(cur, 1)

        if subtab1 == 'tab-1':
            fig_humidity, fig_temp, fig_combined = dev.get_graphs(60)

        elif subtab1 == 'tab-2':
            fig_humidity, fig_temp, fig_combined = dev.get_graphs(1440)
                
        elif subtab1 == 'tab-3':
            fig_humidity, fig_temp, fig_combined = dev.get_graphs(10080)
        end = datetime.now()
        dt_string = end.strftime("%Y-%m-%d %H:%M:%S")
        print(f'{dt_string}: Content rendered in: {end - start}')
        return show_tab(dev, fig_humidity, fig_temp, fig_combined)

    elif tab == 'tab-2':
        dev = Device(cur, 2)
        
        if subtab2 == 'tab-1':
            fig_humidity, fig_temp, fig_combined = dev.get_graphs(60)
        
        elif subtab2 == 'tab-2':
            fig_humidity, fig_temp, fig_combined = dev.get_graphs(1440)
        
        elif subtab2 == 'tab-3':
            fig_humidity, fig_temp, fig_combined = dev.get_graphs(10080)

        end = datetime.now()
        dt_string = end.strftime("%Y-%m-%d %H:%M:%S")
        print(f'{dt_string}: Content rendered in: {end - start}')
        return show_tab(dev, fig_humidity, fig_temp, fig_combined)

if __name__ == '__main__':
    app.run_server(
        debug=True,
        host='0.0.0.0')
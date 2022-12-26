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

def show_all_tab(device_obj: Device, fig_humidity, fig_temp, fig_combined):
    device_obj.query_last_record()

    return html.Div([
        html.H1(
            'All Devices', className='title'
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
device3 = Device(cur, 3)

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
                label=f'{device1.get_devname()}',
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
                label=f'{device2.get_devname()}', 
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
                label=f'{device3.get_devname()}', 
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

    if not conn.open:
        conn.reconnect()

    global cur
    if cur.closed:
        cur = conn.cursor()
    if main_tabs == 'tab-1':
        dev1 = Device(cur, 1)
        dev2 = Device(cur, 2)
        dev3 = Device(cur, 3)

        all = Graph(dev1, dev2, dev3)
        
        if subtab1 == 'tab-1':
            fig_humidity, fig_temp, fig_combined = all.get_graphs(60)
        
        elif subtab1 == 'tab-2':
            fig_humidity, fig_temp, fig_combined = all.get_graphs(1440)
        
        elif subtab1 == 'tab-3':
            fig_humidity, fig_temp, fig_combined = all.get_graphs(10080)

        end = datetime.now()
        dt_string = end.strftime("%Y-%m-%d %H:%M:%S")
        print(f'{dt_string}: Content rendered in: {end - start}')
        return show_all_tab(dev1, fig_humidity, fig_temp, fig_combined)
    
    elif main_tabs == 'tab-2':
        dev = Device(cur, 1)

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

    elif main_tabs == 'tab-3':
        dev = Device(cur, 2)
        
        if subtab3 == 'tab-1':
            fig_humidity, fig_temp, fig_combined = dev.get_graphs(60)
        
        elif subtab3 == 'tab-2':
            fig_humidity, fig_temp, fig_combined = dev.get_graphs(1440)
        
        elif subtab3 == 'tab-3':
            fig_humidity, fig_temp, fig_combined = dev.get_graphs(10080)

        end = datetime.now()
        dt_string = end.strftime("%Y-%m-%d %H:%M:%S")
        print(f'{dt_string}: Content rendered in: {end - start}')
        return show_tab(dev, fig_humidity, fig_temp, fig_combined)

    elif main_tabs == 'tab-4':
        dev = Device(cur, 3)
        
        if subtab4 == 'tab-1':
            fig_humidity, fig_temp, fig_combined = dev.get_graphs(60)
        
        elif subtab4 == 'tab-2':
            fig_humidity, fig_temp, fig_combined = dev.get_graphs(1440)
        
        elif subtab4 == 'tab-3':
            fig_humidity, fig_temp, fig_combined = dev.get_graphs(10080)

        end = datetime.now()
        dt_string = end.strftime("%Y-%m-%d %H:%M:%S")
        print(f'{dt_string}: Content rendered in: {end - start}')
        return show_tab(dev, fig_humidity, fig_temp, fig_combined)


if __name__ == '__main__':
    app.run_server(
        debug=True,
        host='0.0.0.0')
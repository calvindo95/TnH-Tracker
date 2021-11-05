import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import mariadb
import config
import time
from datetime import datetime
from device import *

def connect_to_db():
    # Connect to MariaDB Platform
    try:
        conn = mariadb.connect(
            user=config.user,
            password=config.password,
            host=config.host,
            port=config.port,
            database=config.database
        )

        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        time.sleep(5)
        connect_to_db()

app = dash.Dash(__name__)
conn = connect_to_db()
cur = conn.cursor()

device1 = Device(cur, 1)
device2 = Device(cur, 2)

app.layout = html.Div([
    dcc.Tabs(id="tabs-example-graph", 
        value='tab-1-example-graph',
        className='custom_tabs',
        children=[
            dcc.Tab(
                label=f'{device1.get_devname()}', 
                value='tab-1', 
                className='tab_style',
                selected_className='tab_selected'
            ),
            dcc.Tab(
                label=f'{device2.get_devname()}', 
                value='tab-2', 
                className='tab_style',
                selected_className='tab_selected'
            )
        ]
    ),
    html.Div(id='tabs-content-example-graph')
])
print('close')
conn.close()

@app.callback(Output('tabs-content-example-graph', 'children'),
              Input('tabs-example-graph', 'value'))

def render_content(tab):
    if tab == 'tab-2':
        conn = connect_to_db()
        cur = conn.cursor()

        dev2 = Device(cur, 2)   
        last_record2 = LastRecord(cur,2)
        fig2_humidity1hr, fig2_temp1hr = dev2.get_humidity_graph(60), dev2.get_temp_graph(60)
        fig2_humidity24hr, fig2_temp24hr = dev2.get_humidity_graph(1440), dev2.get_temp_graph(1440)

        return html.Div([
            html.H1(
                f'{dev2.get_devname()}', className='title'
            ),
             html.H2(
                f'Data as of: {last_record2.get_time()}', className='datetime'
            ),
            html.Div([
                html.Span(f'{last_record2.get_humidity()}', className='data'),
                html.Span('Relative Humidity', className='header')], 
                className='information'
            ),
            html.Div([
                html.Span(f'{last_record2.get_temperature()}', className='data'),
                html.Span('Temperature', className='header')], 
                className='information'
            ),
            dcc.Graph(
                figure = fig2_humidity1hr
            ),
            dcc.Graph(
                figure = fig2_humidity24hr
            ),
            dcc.Graph(
                figure = fig2_temp1hr
            ),
            dcc.Graph(
                figure = fig2_temp24hr
            )
        ], 
            className='box'
        ), conn.close()

    # automatically return 'tab-1' when loading page
    else:
        conn = connect_to_db()
        cur = conn.cursor()

        dev1 = Device(cur, 1)
        last_record1 = LastRecord(cur,1)
        fig1_humidity1hr, fig1_temp1hr = dev1.get_humidity_graph(60), dev1.get_temp_graph(60)
        fig1_humidity24hr, fig1_temp24hr = dev1.get_humidity_graph(1440), dev1.get_temp_graph(1440)

        return html.Div([
            html.H1(
                f'{dev1.get_devname()}', className='title'
            ),
            html.H2(
                f'Data as of: {last_record1.get_time()}', className='datetime'
            ),
            html.Div([
                html.Span(f'{last_record1.get_humidity()}', className='data'),
                html.Span('Relative Humidity', className='header')],
                className='information'
            ),
            html.Div([
                html.Span(f'{last_record1.get_temperature()}', className='data'),
                html.Span('Temperature', className='header')], 
                className='information'
            ),
            dcc.Graph(
                figure = fig1_humidity1hr
            ),
            dcc.Graph(
                figure = fig1_humidity24hr
            ),
            dcc.Graph(
                figure = fig1_temp1hr
            ),
            dcc.Graph(
                figure = fig1_temp24hr
            )
        ], 
            className='box'
        ), conn.close()


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
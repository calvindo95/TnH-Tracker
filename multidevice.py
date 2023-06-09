from datetime import datetime
import plotly.express as px
import pandas as pd
import logging
from multiprocessing.pool import ThreadPool as Pool

# Initialize logger by getting 'gunicorn.error' logger
logger = logging.getLogger('gunicorn.error')

pool_size = 4

class Multidevice():
    def __init__(self, devices: list):
        self.devices = devices
        self.temp_graph = None
        self.humidity_graph = None
        self.combined_graph = None

    def get_graphs(self, hours):
        start = datetime.now()

        pool = Pool(pool_size)

        for device in self.devices:
            pool.apply_async(device.query_data,(hours,))

        pool.close()
        pool.join()

        end = datetime.now()
        logger.debug(f'Data queried in: {end - start}')
        start = datetime.now()

        # device[[time], [temp], [humidity]]
        devices_tth = []

        for device in self.devices:
            devices_tth.append(device.data[0])

        tth_set = set(map(len,devices_tth))

        y_temp = []
        y_humidity = []
        time = []

        if len(tth_set) != 1:
            logger.debug(f'Data length is not equal, truncating data: dev1:{len(self.devices[0].data[0])}, dev2:{len(self.devices[1].data[0])}, dev3:{len(self.devices[2].data[0])}')
            
            # find device with limiting len
            tmp_min_len = min(tth_set)

            # truncate data to tmp_min_len
            time = self.devices[0].data[0][0:tmp_min_len]

            for device in self.devices:
                y_temp.append(device.data[1][0:tmp_min_len])
                y_humidity.append(device.data[2][0:tmp_min_len])

            logger.debug(f'Data length is not equal, data len after truncating: dev1:{len(y_temp[0])}, dev2:{len(y_temp[1])}, dev3:{len(y_temp[2])}')
        else:
            time = self.devices[0].data[0]

            for device in self.devices:
                y_temp.append(device.data[1])
                y_humidity.append(device.data[2])


        pool = Pool(pool_size)

        pool.apply_async(self.create_temp_graph,(hours, time, y_temp,))
        pool.apply_async(self.create_humidity_graph,(hours, time, y_humidity,))
        pool.apply_async(self.create_combined_graph,(hours, time, y_temp, y_humidity,))

        pool.close()
        pool.join()

        temp_graph = self.temp_graph
        humidity_graph = self.humidity_graph
        combined_graph = self.combined_graph

        end = datetime.now()
        logger.debug(f'Graphs rendered in: {end - start}')

        return humidity_graph, temp_graph, combined_graph

    def create_temp_graph(self, hours, x_axis: list, y_axis: list):
        y1_temp, y2_temp, y3_temp  = y_axis 

        df = pd.DataFrame({
            "Time": x_axis,
            f"{self.devices[0].get_devname()}": y1_temp,
            f"{self.devices[1].get_devname()}": y2_temp,
            f"{self.devices[2].get_devname()}": y3_temp,
            })
        fig = px.line(
            df, x="Time", 
            y=[f"{self.devices[0].get_devname()}", f"{self.devices[1].get_devname()}", f"{self.devices[2].get_devname()}"],
            title=f'Temperature for the Last {hours} Hour(s)'
        )
        fig.update_layout(
            paper_bgcolor='rgb(0, 0, 0, 0)', 
            font_color='white',
            legend_title=''
        )
        fig.update_xaxes(
            tickformat="%I:%M %p\n%B %d, %Y"
        )
        self.temp_graph = fig

        logger.debug(f'Successfully rendered temp graph')
        return fig

    def create_humidity_graph(self, hours, x_axis: list, y_axis: list):
        y1_humidity, y2_humidity, y3_humidity  = y_axis 

        df = pd.DataFrame({
            "Time": x_axis,
            f"{self.devices[0].get_devname()}": y1_humidity,
            f"{self.devices[1].get_devname()}": y2_humidity,
            f"{self.devices[2].get_devname()}": y3_humidity,
            })
        fig = px.line(
            df, x="Time", 
            y=[f"{self.devices[0].get_devname()}", f"{self.devices[1].get_devname()}", f"{self.devices[2].get_devname()}"],
            title=f'Humidity for the Last {hours} Hour(s)'
        )
        fig.update_layout(
            paper_bgcolor='rgb(0, 0, 0, 0)', 
            font_color='white',
            legend_title=''
        )    
        fig.update_xaxes(
            tickformat="%I:%M %p\n%B %d, %Y"
        )   
        #fig.data = [t for t in fig.data if t.mode == "lines"]
        self.humidity_graph = fig

        logger.debug(f'Successfully rendered humidity graph')
        return fig

    def create_combined_graph(self, hours, x_time: list, y_temp: list, y_humidity: list):
        y1_temp, y2_temp, y3_temp  = y_temp
        y1_humidity, y2_humidity, y3_humidity  = y_humidity

        df = pd.DataFrame({
            "Time": x_time,
            f"{self.devices[0].get_devname()} Temperature": y1_temp,
            f"{self.devices[1].get_devname()} Temperature": y2_temp,
            f"{self.devices[2].get_devname()} Temperature": y3_temp,
            f"{self.devices[0].get_devname()} Humidity": y1_humidity,
            f"{self.devices[1].get_devname()} Humidity": y2_humidity,
            f"{self.devices[2].get_devname()} Humidity": y3_humidity,
            })
        fig = px.line(
            df, x="Time", 
            y=[f"{self.devices[0].get_devname()} Temperature", 
                f"{self.devices[1].get_devname()} Temperature",
                f"{self.devices[2].get_devname()} Temperature", 
                f"{self.devices[0].get_devname()} Humidity",
                f"{self.devices[1].get_devname()} Humidity",
                f"{self.devices[2].get_devname()} Humidity"
                ],
            title=f'Temperature and Humidity for the Last {hours} Hour(s)'
        )
        fig.update_layout(
            paper_bgcolor='rgb(0, 0, 0, 0)', 
            font_color='white',
            legend_title=''
        )       
        fig.update_xaxes(
            tickformat="%I:%M %p\n%B %d, %Y"
        )   
        self.combined_graph = fig

        logger.debug(f'Successfully rendered combined graph')
        return fig
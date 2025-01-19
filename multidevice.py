from datetime import datetime
import plotly.express as px
import pandas as pd
import numpy as np
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
            for device in self.devices:
                logger.debug(f'Data length is not equal, data len: dev{device.deviceID}:{len(device.data_dict)}')

            # Find device with max entries
            for device in self.devices:
                if len(device.data[0]) > len(time):
                    time = device.data[0]

            # check device maps for missing values, insert none if missing
            for device in self.devices:
                tmp_temp = []
                tmp_humidity = []

                for dt in time:
                    if dt not in device.data_dict.keys():
                        device.data_dict[f"{dt}"] = [None, None]
                        #logger.debug(f'inserting {dt} into {device.data_dict[f"{dt}"]}')

                for dt in time:
                    temp_and_humidity = device.data_dict.get(dt)
                    tmp_temp.append(temp_and_humidity[0])
                    tmp_humidity.append(temp_and_humidity[1])

                y_temp.append(tmp_temp)
                y_humidity.append(tmp_humidity)

            for device in self.devices:
                logger.debug(f'Data length is not equal, new data len: dev{device.deviceID}:{len(device.data_dict)}')
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
        columns = ["Time"]
        data = [x_axis]
        
        for device in self.devices:
            columns.append(device.get_devname())

        for tmp_data in y_axis:
            data.append(tmp_data)

        my_dict = dict(zip(columns, data))

        df = pd.DataFrame(my_dict)
        # replace None values as NaN
        df = df.fillna(value=np.nan)

        fig = px.line(
            df, 
            x="Time", 
            y=columns,
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
        columns = ["Time"]
        humidity_rows = [x_axis]

        for device in self.devices:
            columns.append(device.get_devname())
        for tmp_data in y_axis:
            humidity_rows.append(tmp_data)

        humidity_dict = dict(zip(columns, humidity_rows))

        df = pd.DataFrame(humidity_dict)
        # replace None values as NaN
        df = df.fillna(value=np.nan)

        fig = px.line(
            df, x="Time", 
            y=columns,
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
        columns = ["Time"]
        combined_rows = [x_time]

        for device in self.devices:
            columns.append(f'{device.get_devname()} Temperature')
        for device in self.devices:
            columns.append(f'{device.get_devname()} Humidity')

        for tmp_data in y_temp:
            combined_rows.append(tmp_data)
        for tmp_data in y_humidity:
            combined_rows.append(tmp_data)
        
        combined_dict = dict(zip(columns, combined_rows))

        df = pd.DataFrame(combined_dict)
        # replace None values as NaN
        df = df.fillna(value=np.nan)

        fig = px.line(
            df, x="Time", 
            y=columns,
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
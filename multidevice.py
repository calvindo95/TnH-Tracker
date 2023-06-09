from datetime import datetime
import plotly.express as px
import pandas as pd
import logging
import threading

# Initialize logger by getting 'gunicorn.error' logger
logger = logging.getLogger('gunicorn.error')

class Multidevice():
    def __init__(self, dev1, dev2, dev3):
        self.dev1 = dev1
        self.dev2 = dev2
        self.dev3 = dev3
        self.temp_graph = None
        self.humidity_graph = None
        self.combined_graph = None

    def get_graphs(self, hours):
        start = datetime.now()

        t1 = threading.Thread(target=self.dev1.query_data, args=(hours,))
        t2 = threading.Thread(target=self.dev2.query_data, args=(hours,))
        t3 = threading.Thread(target=self.dev3.query_data, args=(hours,))

        t1.start()
        t2.start()
        t3.start()

        t1.join()
        t2.join()
        t3.join()

        end = datetime.now()
        logger.debug(f'Data queried in: {end - start}')
        start = datetime.now()

        x1_time, y1_temp, y1_humidity = self.dev1.data
        _, y2_temp, y2_humidity = self.dev2.data
        _, y3_temp, y3_humidity = self.dev3.data

        if len(y1_humidity) != len(y2_humidity) or len(y2_humidity) != len(y3_humidity) or len(y1_humidity) != len(y3_humidity):
            logger.debug(f'Data length is not equal, truncating data: dev1:{len(y1_humidity)}, dev2:{len(y2_humidity)}, dev3:{len(y3_humidity)}')
            
            # find device with limiting len
            tmp_list = []
            tmp_list.append(len(y1_humidity))
            tmp_list.append(len(y2_humidity))
            tmp_list.append(len(y3_humidity))

            tmp_min_len = min(tmp_list)

            # truncate lists to tmp_min_len

            # dev1
            x1_time = x1_time[0:tmp_min_len]
            y1_temp = y1_temp[0:tmp_min_len]
            y1_humidity = y1_humidity[0:tmp_min_len]

            # dev2
            y2_temp = y2_temp[0:tmp_min_len]
            y2_humidity = y2_humidity[0:tmp_min_len]

            # dev3
            y3_temp = y3_temp[0:tmp_min_len]
            y3_humidity = y3_humidity[0:tmp_min_len]

            logger.debug(f'Data length is not equal, data len after truncating: dev1:{len(y1_humidity)}, dev2:{len(y2_humidity)}, dev3:{len(y3_humidity)}')

        y_temp = []
        y_humidity = []

        y_temp.append(y1_temp)
        y_temp.append(y2_temp)
        y_temp.append(y3_temp)

        y_humidity.append(y1_humidity)
        y_humidity.append(y2_humidity)
        y_humidity.append(y3_humidity)        

        t1 = threading.Thread(target=self.create_temp_graph, args=(hours, x1_time, y_temp,))
        t2 = threading.Thread(target=self.create_humidity_graph, args=(hours, x1_time, y_humidity,))
        t3 = threading.Thread(target=self.create_combined_graph, args=(hours, x1_time, y_temp, y_humidity,))

        t1.start()
        t2.start()
        t3.start()

        t1.join()
        t2.join()
        t3.join()

        temp_graph = self.temp_graph
        humidity_graph = self.humidity_graph
        combined_graph = self.combined_graph

        end = datetime.now()
        logger.debug(f'Graphs rendered in: {end - start}')

        return humidity_graph, temp_graph, combined_graph

    def create_temp_graph(self, hours, x_axis: list, y_axis: list):
        start = datetime.now()
        y1_temp, y2_temp, y3_temp  = y_axis 

        df = pd.DataFrame({
            "Time": x_axis,
            f"{self.dev1.get_devname()}": y1_temp,
            f"{self.dev2.get_devname()}": y2_temp,
            f"{self.dev3.get_devname()}": y3_temp,
            })
        fig = px.line(
            df, x="Time", 
            y=[f"{self.dev1.get_devname()}", f"{self.dev2.get_devname()}", f"{self.dev3.get_devname()}"],
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

        end = datetime.now()
        logger.debug(f'Temp graph rendered in: {end - start}')
        return fig

    def create_humidity_graph(self, hours, x_axis: list, y_axis: list):
        start = datetime.now()
        y1_humidity, y2_humidity, y3_humidity  = y_axis 

        df = pd.DataFrame({
            "Time": x_axis,
            f"{self.dev1.get_devname()}": y1_humidity,
            f"{self.dev2.get_devname()}": y2_humidity,
            f"{self.dev3.get_devname()}": y3_humidity,
            })
        fig = px.line(
            df, x="Time", 
            y=[f"{self.dev1.get_devname()}", f"{self.dev2.get_devname()}", f"{self.dev3.get_devname()}"],
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

        end = datetime.now()
        logger.debug(f'Humidity graph rendered in: {end - start}')
        return fig

    def create_combined_graph(self, hours, x_time: list, y_temp: list, y_humidity: list):
        start = datetime.now()
        y1_temp, y2_temp, y3_temp  = y_temp
        y1_humidity, y2_humidity, y3_humidity  = y_humidity

        df = pd.DataFrame({
            "Time": x_time,
            f"{self.dev1.get_devname()} Temperature": y1_temp,
            f"{self.dev2.get_devname()} Temperature": y2_temp,
            f"{self.dev3.get_devname()} Temperature": y3_temp,
            f"{self.dev1.get_devname()} Humidity": y1_humidity,
            f"{self.dev2.get_devname()} Humidity": y2_humidity,
            f"{self.dev3.get_devname()} Humidity": y3_humidity,
            })
        fig = px.line(
            df, x="Time", 
            y=[f"{self.dev1.get_devname()} Temperature", 
                f"{self.dev2.get_devname()} Temperature",
                f"{self.dev3.get_devname()} Temperature", 
                f"{self.dev1.get_devname()} Humidity",
                f"{self.dev2.get_devname()} Humidity",
                f"{self.dev3.get_devname()} Humidity"
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

        end = datetime.now()
        logger.debug(f'Combined graph rendered in: {end - start}')
        return fig
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import logging
import mariadb
import time
import config # import local configs
import threading

# Initialize logger by getting 'gunicorn.error' logger
logger = logging.getLogger('gunicorn.error')

# convert dt_object to 12hr time
def convert_dt(dt_obj):
    return dt_obj.strftime("%m/%d %I:%M:%S %p")

class Device():
    def __init__(self, deviceID):
        conn = self.connect_to_db()
        cur = conn.cursor()

        self.local_conn = conn
        self.local_cur = cur
        self.deviceID = deviceID
        self.dev_name = self.query_devname()
        self.last_record = [None, None, None, None]
        self.data = []

    def connect_to_db(self):
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
            logger.error(f"Error connecting to MariaDB Platform: {e}")
            time.sleep(5)
            self.connect_to_db()

    def check_db_connection(self):
        if not self.local_conn.open:
            self.local_conn.reconnect()

        if self.local_cur.closed:
            self.local_cur = self.local_conn.cursor()

    def query_last_record(self):
        self.check_db_connection()
        try:
            query = '''SELECT DevName.DevName, Data_History.CurrentDateTime, History.Temperature, History.Humidity 
                    FROM Device 
                    LEFT JOIN DevName ON Device.DevNameID=DevName.DevNameID 
                    LEFT JOIN Data_History ON Data_History.DeviceID=Device.DeviceID 
                    LEFT JOIN History ON History.HistoryID=Data_History.HistoryID 
                    WHERE Device.DeviceID=%s
                    AND Data_History.CurrentDateTime >= DATE_ADD(NOW(), INTERVAL -1 HOUR)
                    ORDER BY Data_History.CurrentDateTime DESC LIMIT 1'''
            data = (self.deviceID,)
            self.local_cur.execute(query, data)

            logger.debug(f'Successful query of last record from {self.dev_name}')

            self.last_record = self.local_cur.fetchone()

        except Exception as e:
            logger.error(f"Error querying records from MariaDB: {e}")
        
    def get_time(self):
        if not self.last_record:
            self.query_last_record()

        return convert_dt(self.last_record[1])

    def get_temperature(self):
        if not self.last_record:
            self.query_last_record()

        return self.last_record[2]

    def get_humidity(self):
        if not self.last_record:
            self.query_last_record()

        return self.last_record[3]

    # returns list containing [device_name, current_date_time, temperature, humidity]
    def query_data(self, hours):
        self.check_db_connection()
        try:
            query = '''SELECT Data_History.CurrentDateTime, History.Temperature, History.Humidity
                    FROM Device  
                    LEFT JOIN Data_History ON Data_History.DeviceID=Device.DeviceID 
                    LEFT JOIN History ON History.HistoryID=Data_History.HistoryID 
                    WHERE Device.DeviceID=%s 
                    AND Data_History.CurrentDateTime >= DATE_ADD(NOW(), INTERVAL -%s HOUR)
                    ORDER BY Data_History.CurrentDateTime DESC;'''
            data = (self.deviceID, hours)
            self.local_cur.execute(query, data)

            x_time, y_temp, y_humidity = [], [], []
            for row in self.local_cur.fetchall():
                x_time.append(row[0])
                y_temp.append(row[1])
                y_humidity.append(row[2])

            logger.debug(f'Successful query of last {hours} hours of records from Device {self.dev_name}')

            # update latest data
            #self.last_record.clear()
            self.last_record[0] = (self.dev_name)
            self.last_record[1] = (x_time[-1])
            self.last_record[2] = (y_temp[-1])
            self.last_record[3] = (y_humidity[-1])

            self.data = x_time, y_temp, y_humidity
            return x_time, y_temp, y_humidity

        except Exception as e:
            logger.error(f"Error querying temp from MariaDB: {e}")

    def get_graphs(self, hours):
        self.query_data(hours)
        x_time, y_temp, y_humidity = self.data

        temp_graph = self.get_temp_graph(hours, x_time, y_temp)
        humidity_graph = self.get_humidity_graph(hours, x_time, y_humidity)
        combined_graph = self.get_combined_graph(hours, x_time, y_temp, y_humidity)
        
        return humidity_graph, temp_graph, combined_graph

    def get_temp_graph(self, hours, x_axis: list, y_axis: list):

        df = pd.DataFrame({
            "Time": x_axis,
            "Temperature (F)": y_axis,
            })
        fig = px.line(
            df, x="Time", 
            y="Temperature (F)", 
            title=f'Temperature for the Last {hours} Hour(s)'
        )
        fig.update_layout(
            paper_bgcolor='rgb(0, 0, 0, 0)', 
            #plot_bgcolor='#c8c8c8', 
            font_color='white'
        )   
        fig.update_xaxes(
            tickformat="%I:%M %p\n%B %d, %Y",
        )
        #fig.data = [t for t in fig.data if t.mode == "lines"]
        return fig

    def get_humidity_graph(self, hours, x_axis: list, y_axis: list):

        df = pd.DataFrame({
            "Time": x_axis,
            "Humidity (%)": y_axis
            })
        fig = px.line(
            df, x="Time", 
            y="Humidity (%)",
            title=f'Humidity for the Last {hours} Hour(s)'
        )
        fig.update_layout(paper_bgcolor='rgb(0, 0, 0, 0)', 
            #plot_bgcolor='#c8c8c8', 
            font_color='white'
        )    
        fig.update_xaxes(
            tickformat="%I:%M %p\n%B %d, %Y"
        )   
        #fig.data = [t for t in fig.data if t.mode == "lines"]
        return fig

    def get_combined_graph(self, hours, x_time: list, y_temp: list, y_humidity: list):

        df = pd.DataFrame({
            "Time": x_time,
            "Humidity (%)": y_humidity,
            "Temperature (F)": y_temp
            })
        fig = px.line(
            df, x="Time", 
            y=["Temperature (F)", "Humidity (%)"],
            title=f'Humidity for the Last {hours} Hour(s)'
        )
        fig.update_layout(
            paper_bgcolor='rgb(0, 0, 0, 0)', 
            #plot_bgcolor='#c8c8c8', 
            font_color='white',
            legend_title=''
        )       
        fig.update_xaxes(
            tickformat="%I:%M %p\n%B %d, %Y"
        )   
        #fig.data[0].line.color = 'blue'
        return fig

    def query_devname(self):
        self.check_db_connection()
        try:
            query = '''SELECT DevName.DevName FROM DevName 
                        LEFT JOIN Device ON Device.DevNameID=DevName.DevNameID 
                        WHERE DeviceID=%s'''
            data = (self.deviceID,)
            self.local_cur.execute(query, data)
            tmpdevname = self.local_cur.fetchone()[0]
            logger.debug(f'Successful query of Device name {tmpdevname}')
            return tmpdevname
        except Exception as e:
            logger.error(f"Error querying devname from MariaDB: {e}")

    def get_devname(self):
        return self.dev_name

class Graph():
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
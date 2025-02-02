from datetime import datetime
import plotly.express as px
import pandas as pd
import logging
import mariadb
import time
import config # import local configs

# Initialize logger by getting 'gunicorn.error' logger
logger = logging.getLogger('gunicorn.error')

# convert dt_object to 12hr time
def convert_dt(dt_obj):
    return dt_obj.strftime("%m/%d %I:%M:%S %p")

def convert_dt_short(dt_obj):
    return dt_obj.strftime("%m/%d %I:%M %p")

def convert_dt_short_list(dt_obj_list):
    tmp_list = []

    for i in dt_obj_list:
        tmp_list.append(i.strftime("%m/%d %I:%M %p"))

    return tmp_list


class Device():
    def __init__(self, deviceID):
        conn = self.connect_to_db()
        cur = conn.cursor()

        self.local_conn = conn
        self.local_cur = cur
        self.deviceID = deviceID
        self.dev_name = self.query_devname()
        self.last_record = [None, None, None, None]
        self.data = []  # time, temp, humidity
        self.data_dict = {} # {'date':[temp,humidity]}

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
            query = '''SELECT Device.DevName, History.CurrentDateTime, History.Temperature, History.Humidity 
                    FROM Device 
                    LEFT JOIN History ON History.DeviceID=Device.DeviceID 
                    WHERE Device.DeviceID=%s
                    AND History.CurrentDateTime >= DATE_ADD(NOW(), INTERVAL -1 HOUR)
                    ORDER BY History.CurrentDateTime DESC LIMIT 1'''
            data = (self.deviceID,)
            self.local_cur.execute(query, data)

            logger.debug(f'Successful query of last record from {self.dev_name}')

            self.last_record = self.local_cur.fetchone()

        except Exception as e:
            logger.error(f"Error querying records from MariaDB: {e}")
        
    def get_time(self):
        if not self.last_record:
            self.query_last_record()

        return self.last_record[1]

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
            query = '''SELECT History.CurrentDateTime, History.Temperature, History.Humidity
                    FROM Device  
                    LEFT JOIN History ON History.DeviceID=Device.DeviceID 
                    WHERE Device.DeviceID=%s 
                    AND History.CurrentDateTime >= DATE_ADD(NOW(), INTERVAL -%s HOUR)
                    ORDER BY History.CurrentDateTime ASC;'''
            data = (self.deviceID, hours)
            self.local_cur.execute(query, data)

            x_time, y_temp, y_humidity = [], [], []
            for row in self.local_cur.fetchall():
                x_time.append(convert_dt_short(row[0]))
                y_temp.append(row[1])
                y_humidity.append(row[2])

                self.data_dict[f'{convert_dt_short(row[0])}'] = [row[1], row[2]]

            logger.debug(f'Successful query of last {hours} hours of records from Device {self.dev_name}')

            # update latest data
            #self.last_record.clear()
            if x_time or y_temp or y_humidity:
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
            query = '''SELECT Device.DevName FROM Device 
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
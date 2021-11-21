from datetime import datetime
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go


# convert dt_object to 12hr time
def convert_dt(dt_obj):
    return dt_obj.strftime("%m/%d %I:%M:%S %p")

class Device():
    def __init__(self, local_cur, deviceID):
        self.local_cur = local_cur
        self.deviceID = deviceID
        self.dev_name = self.query_devname()

    # returns list containing [device_name, current_date_time, temperature, humidity]
    def get_records(self, quantity):
        try:
            query = '''SELECT DevName.DevName, Data_History.CurrentDateTime, History.Temperature, History.Humidity 
                    FROM Device 
                    LEFT JOIN DevName ON Device.DevNameID=DevName.DevNameID 
                    LEFT JOIN Data_History ON Data_History.DeviceID=Device.DeviceID 
                    LEFT JOIN History ON History.HistoryID=Data_History.HistoryID 
                    WHERE Device.DeviceID=%s
                    ORDER BY Data_History.CurrentDateTime DESC LIMIT %s'''
            data = (self.deviceID, quantity,)
            self.local_cur.execute(query, data)

            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            print(f'{dt_string}: Successful query of {self.deviceID} records')

            return self.local_cur.fetchall()

        except Exception as e:
            print(f"Error querying records from MariaDB: {e}")

    def query_data(self, quantity):
        try:
            query = '''SELECT Data_History.CurrentDateTime, History.Temperature, History.Humidity
                    FROM Device  
                    LEFT JOIN Data_History ON Data_History.DeviceID=Device.DeviceID 
                    LEFT JOIN History ON History.HistoryID=Data_History.HistoryID 
                    WHERE Device.DeviceID=%s
                    ORDER BY Data_History.CurrentDateTime DESC 
                    LIMIT %s'''
            data = (self.deviceID, quantity,)
            self.local_cur.execute(query, data)

            x_time, y_temp, y_humidity = [], [], []
            for row in self.local_cur.fetchall():
                x_time.append(row[0])
                y_temp.append(row[1])
                y_humidity.append(row[2])

            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            print(f'{dt_string}: Successful query of {self.deviceID}: {quantity} temperature and humidity datapoints pulled')
            
            return x_time, y_temp, y_humidity

        except Exception as e:
            print(f"Error querying temp from MariaDB: {e}")

    def get_graphs(self, quantity):
        x_time, y_temp, y_humidity = self.query_data(quantity)

        temp_graph = self.get_temp_graph(quantity, x_time, y_temp)
        humidity_graph = self.get_humidity_graph(quantity, x_time, y_humidity)
        combined_graph = self.get_combined_graph(quantity, x_time, y_temp, y_humidity)
        
        return humidity_graph, temp_graph, combined_graph

    def get_temp_graph(self, quantity, x_axis: list, y_axis: list):
        hours = quantity/60

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
        #fig.data[0].line.color = 'blue'
        return fig

    def get_humidity_graph(self, quantity, x_axis: list, y_axis: list):
        hours = quantity/60

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
        #fig.data[0].line.color = 'blue'
        return fig

    def get_combined_graph(self, quantity, x_time: list, y_temp: list, y_humidity: list):
        hours = quantity/60

        df = pd.DataFrame({
            "Time": x_time,
            "Humidity (%)": y_humidity,
            "Temperature (F)": y_temp
            })
        fig = px.line(
            df, x="Time", 
            y=["Humidity (%)", "Temperature (F)"],
            title=f'Humidity for the Last {hours} Hour(s)'
        )
        fig.update_layout(
            paper_bgcolor='rgb(0, 0, 0, 0)', 
            #plot_bgcolor='#c8c8c8', 
            font_color='white',
            legend_title=''
        )       
        #fig.data[0].line.color = 'blue'
        return fig

    def query_devname(self):
        try:
            query = '''SELECT DevName.DevName FROM DevName 
                        LEFT JOIN Device ON Device.DevNameID=DevName.DevNameID 
                        WHERE DeviceID=%s'''
            data = (self.deviceID,)
            self.local_cur.execute(query, data)
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            print(f'{dt_string}: Successful query of {self.deviceID} device name')
            return self.local_cur.fetchone()[0]
        except Exception as e:
            print(f"Error querying devname from MariaDB: {e}")

    def get_devname(self):
        return self.dev_name

class LastRecord(Device):
    def __init__(self, local_cur, deviceID):
        super().__init__(local_cur, deviceID)
        self.data = self.get_records(1)

    def get_time(self):
        return convert_dt(self.data[0][1])

    def get_temperature(self):
        return self.data[0][2]

    def get_humidity(self):
        return self.data[0][3]
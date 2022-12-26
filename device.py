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
        self.last_record = []

    def query_last_record(self):
        try:
            query = '''SELECT DevName.DevName, Data_History.CurrentDateTime, History.Temperature, History.Humidity 
                    FROM Device 
                    LEFT JOIN DevName ON Device.DevNameID=DevName.DevNameID 
                    LEFT JOIN Data_History ON Data_History.DeviceID=Device.DeviceID 
                    LEFT JOIN History ON History.HistoryID=Data_History.HistoryID 
                    WHERE Device.DeviceID=%s
                    ORDER BY Data_History.CurrentDateTime DESC LIMIT 1'''
            data = (self.deviceID,)
            self.local_cur.execute(query, data)

            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            print(f'{dt_string}: Successful query of {self.deviceID} records')

            self.last_record = self.local_cur.fetchone()

        except Exception as e:
            print(f"Error querying records from MariaDB: {e}")
        
    def get_time(self):
        return convert_dt(self.last_record[1])

    def get_temperature(self):
        return self.last_record[2]

    def get_humidity(self):
        return self.last_record[3]

    # returns list containing [device_name, current_date_time, temperature, humidity]
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
            print(f'{dt_string}: Successful query of device {self.deviceID}: {quantity} temperature and humidity datapoints pulled')
            
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
        fig.update_xaxes(
            tickformat="%I:%M %p\n%B %d, %Y",
        )
        #fig.data = [t for t in fig.data if t.mode == "lines"]
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
        fig.update_xaxes(
            tickformat="%I:%M %p\n%B %d, %Y"
        )   
        #fig.data = [t for t in fig.data if t.mode == "lines"]
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
        try:
            query = '''SELECT DevName.DevName FROM DevName 
                        LEFT JOIN Device ON Device.DevNameID=DevName.DevNameID 
                        WHERE DeviceID=%s'''
            data = (self.deviceID,)
            self.local_cur.execute(query, data)
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            print(f'{dt_string}: Successful query of device {self.deviceID}')
            return self.local_cur.fetchone()[0]
        except Exception as e:
            print(f"Error querying devname from MariaDB: {e}")

    def get_devname(self):
        return self.dev_name

class Graph():
    def __init__(self, dev1, dev2, dev3):
        self.dev1 = dev1
        self.dev2 = dev2
        self.dev3 = dev3

    def get_graph(self, quantity):
        x1_time, y1_temp, y1_humidity = self.dev1.query_data(quantity)
        _, y2_temp, y2_humidity = self.dev2.query_data(quantity)
        _, y3_temp, y3_humidity = self.dev3.query_data(quantity)

        hours = quantity/60

        df = pd.DataFrame({
            "Time": x1_time,
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
            #plot_bgcolor='#c8c8c8', 
            font_color='white',
            legend_title=''
        )       
        fig.update_xaxes(
            tickformat="%I:%M %p\n%B %d, %Y"
        )   
        #fig.data[0].line.color = 'blue'
        return fig

    def get_graphs(self, quantity):
        x1_time, y1_temp, y1_humidity = self.dev1.query_data(quantity)
        _, y2_temp, y2_humidity = self.dev2.query_data(quantity)
        _, y3_temp, y3_humidity = self.dev3.query_data(quantity)

        y_temp = []
        y_humidity = []

        y_temp.append(y1_temp)
        y_temp.append(y2_temp)
        y_temp.append(y3_temp)

        y_humidity.append(y1_humidity)
        y_humidity.append(y2_humidity)
        y_humidity.append(y3_humidity)        

        temp_graph = self.get_temp_graph(quantity, x1_time, y_temp)
        humidity_graph = self.get_humidity_graph(quantity, x1_time, y_humidity)
        combined_graph = self.get_combined_graph(quantity, x1_time, y_temp, y_humidity)
        
        print('I got here')
        return humidity_graph, temp_graph, combined_graph

    def get_temp_graph(self, quantity, x_axis: list, y_axis: list):
        hours = quantity/60

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
            #plot_bgcolor='#c8c8c8', 
            font_color='white',
            legend_title=''
        )       
        fig.update_xaxes(
            tickformat="%I:%M %p\n%B %d, %Y"
        )   
        #fig.data[0].line.color = 'blue'
        return fig

    def get_humidity_graph(self, quantity, x_axis: list, y_axis: list):
        hours = quantity/60

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
        fig.update_layout(paper_bgcolor='rgb(0, 0, 0, 0)', 
            #plot_bgcolor='#c8c8c8', 
            font_color='white'
        )    
        fig.update_xaxes(
            tickformat="%I:%M %p\n%B %d, %Y"
        )   
        #fig.data = [t for t in fig.data if t.mode == "lines"]
        return fig

    def get_combined_graph(self, quantity, x_time: list, y_temp: list, y_humidity: list):
        hours = quantity/60

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
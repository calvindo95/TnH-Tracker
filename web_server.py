from flask import Flask, render_template
import mariadb
import config
import time
from datetime import datetime

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
        print("Connected")

        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        time.sleep(5)
        connect_to_db()
    
# convert dt_object to 12hr time
def convert_dt(dt_obj):
    return dt_obj.strftime("%I:%M:%S %p")

class DeviceData():
    def __init__(self, local_cur, deviceID):
        self.local_cur = local_cur
        self.deviceID = deviceID
        self.data = self.get_data(self.deviceID)

    # returns list containing [device_name, current_date_time, temperature, humidity]
    def get_data(self, deviceID):
        try:
            query = '''SELECT DevName.DevName, Data_History.CurrentDateTime, History.Temperature, History.Humidity FROM Device 
                    LEFT JOIN DevName ON Device.DevNameID=DevName.DevNameID 
                    LEFT JOIN Data_History ON Data_History.DeviceID=Device.DeviceID 
                    LEFT JOIN History ON History.HistoryID=Data_History.HistoryID 
                    WHERE Device.DeviceID=%s
                    ORDER BY Data_History.CurrentDateTime DESC LIMIT 1'''
            data = (deviceID,)
            self.local_cur.execute(query, data)

            return self.local_cur.fetchone()
        
        except Exception as e:
            print(f"Error querying data from MariaDB: {e}")

    def get_num_of_devices(self):
        try:
            query = '''SELECT DeviceID FROM Device'''
            self.local_cur.execute(query)
            num_of_devices = len(self.local_cur.fetchall())
            return num_of_devices

        except Exception as e:
            print(f"Error querying data from MariaDB: {e}")

    def get_devname(self):
        return self.data[0]

    def get_time(self):
        return convert_dt(self.data[1])

    def get_temperature(self):
        return self.data[2]

    def get_humidity(self):
        return self.data[3]

app = Flask(__name__)

@app.route("/hello/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/")
def serve_data(name=None):
    conn = connect_to_db()
    cur = conn.cursor()

    dev1 = DeviceData(cur, 1)
    dev2 = DeviceData(cur, 2)

    conn.close()

    return render_template('index.html',
                            name=name,
                            dev_name1=dev1.get_devname(),
                            current_date_time1=dev1.get_time(),
                            temperature1=dev1.get_temperature(), 
                            humidity1=dev1.get_humidity(),
                            dev_name2=dev2.get_devname(),
                            current_date_time2=dev2.get_time(),
                            temperature2=dev2.get_temperature(), 
                            humidity2=dev2.get_humidity(),)

if __name__ == '__main__':
    app.run(debug=True)
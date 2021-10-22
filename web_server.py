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

def get_data(local_cur,deviceID):
    try:
        query = '''SELECT DevName.DevName, Data_History.CurrentDateTime, History.Temperature, History.Humidity FROM Device 
                LEFT JOIN DevName ON Device.DevNameID=DevName.DevNameID 
                LEFT JOIN Data_History ON Data_History.DeviceID=Device.DeviceID 
                LEFT JOIN History ON History.HistoryID=Data_History.HistoryID 
                WHERE Device.DeviceID=%s
                ORDER BY Data_History.CurrentDateTime DESC LIMIT 1'''
        data = (deviceID,)
        local_cur.execute(query, data)
        for device_name, current_date_time, temperature, humidity in local_cur:
            return device_name, current_date_time, temperature, humidity

    except Exception as e:
        print(f"Error querying data from MariaDB: {e}")

# convert dt_object to 12hr time
def convert_dt(dt_obj):
    return dt_obj.strftime("%I:%M:%S %p")

app = Flask(__name__)

@app.route("/hello/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/")
def serve_data(name=None):
    conn = connect_to_db()
    cur = conn.cursor()

    device_name1, last_date_time1, local_temperature1, local_humidity1 = get_data(cur, 1)
    device_name2, last_date_time2, local_temperature2, local_humidity2 = get_data(cur, 2)
    
    conn.close()

    return render_template('index.html',
                            name=name,
                            dev_name1=device_name1,
                            current_date_time1=convert_dt(last_date_time1),
                            temperature1=local_temperature1, 
                            humidity1=local_humidity1,
                            dev_name2=device_name2,
                            current_date_time2=convert_dt(last_date_time2),
                            temperature2=local_temperature2, 
                            humidity2=local_humidity2)

if __name__ == '__main__':
    app.run(debug=True)
import Adafruit_DHT
import time
import mariadb
from datetime import datetime
import config

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4
DeviceID = config.deviceID

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

def get_sensor_data():
    try:
        humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
        tempF = round(temperature*(9/5)+32, 2)

        return humidity, tempF
    except Exception as e:
        print(f"Error polling DHT11 Sensor: {e}")
        time.sleep(1)
        return get_sensor_data()

if __name__ == "__main__":
    conn = connect_to_db()
    cur = conn.cursor()

    humidity, temperature = get_sensor_data()
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

    query1 = f"INSERT INTO History (Temperature, Humidity) VALUES ({temperature}, {humidity})"
    query2 = f"INSERT INTO Data_History (DeviceID, HistoryID, CurrentDateTime) VALUES ({DeviceID}, LAST_INSERT_ID(), '{dt_string}')"

    cur.execute(query1)
    cur.execute(query2)
    
    print("Data inserted")

    conn.commit()
    conn.close()

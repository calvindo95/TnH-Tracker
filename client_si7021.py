import board
import adafruit_si7021
import time
import mariadb
from datetime import datetime
import config
import requests

sensor = adafruit_si7021.SI7021(board.I2C())
DeviceID = config.deviceID
URL = "http://192.168.1.174:8081/input_data"

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
        humidity, temperature = sensor.relative_humidity, sensor.temperature
        tempF = round(temperature*(9/5)+32, 2)
        print(f'{humidity} {tempF}')

        return humidity, tempF
    except Exception as e:
        print(f"Error polling SI7021 Sensor: {e}")
        time.sleep(1)
        return get_sensor_data()

if __name__ == "__main__":
    humidity, temperature = get_sensor_data()
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

    s = requests.Session()
    POST_DATA = f'{config.deviceID},pw_test,{dt_string},{temperature},{humidity}'
    requests.post(config.httpserverip, data={"data": POST_DATA})
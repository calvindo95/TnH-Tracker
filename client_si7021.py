import board
import adafruit_si7021
import time
from datetime import datetime
import config
import requests
import json

sensor = adafruit_si7021.SI7021(board.I2C())
headers = {'Content-Type': 'application/json'}

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
    POST_DATA = {'DeviceID':f'{config.deviceID}', 'hash':'pw_test', 'CurrentDateTime':f'{dt_string}', 'Temperature':f'{temperature}','Humidity':f'{humidity}'}
    requests.post(config.httpserverip, data=json.dumps(POST_DATA), headers=headers)
import board
import busio
import adafruit_sht31d
import time
from datetime import datetime
import config
import requests

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_sht31d.SHT31D(i2c)

def get_sensor_data():
    try:
        humidity, temperature = sensor.relative_humidity, sensor.temperature
        tempF = round(temperature*(9/5)+32, 2)

        return humidity, tempF
    except Exception as e:
        print(f"Error polling DHT11 Sensor: {e}")
        time.sleep(1)
        return get_sensor_data()

if __name__ == "__main__":
    humidity, temperature = get_sensor_data()
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

    s = requests.Session()
    POST_DATA = f'{config.deviceID},pw_test,{dt_string},{temperature},{humidity}'
    requests.post(config.httpserverip, data={"data": POST_DATA})

import board
import busio
import adafruit_sht31d
import time
from datetime import datetime
import config
import requests
import json
import logging

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_sht31d.SHT31D(i2c)
headers = {'Content-Type': 'application/json'}

def get_sensor_data():
    try:
        humidity, temperature = sensor.relative_humidity, sensor.temperature
        tempF = round(temperature*(9/5)+32, 2)

        return humidity, tempF
    except Exception as e:
        logging.error(f'Error polling DHT11 Sensor: {e}')
        time.sleep(1)
        return get_sensor_data()

def send_response():
    send_response.count += 1
    response = ''
    
    try:
        response = requests.post(config.httpserverip, data=json.dumps(POST_DATA), headers=headers)
        if response.text != "Received data value: 0":
            logging.warning(f'failed - |{response.text}|')
            return 1
        else:
            logging.info(f'Successfully posted data')
            return 0
        
    except Exception as e:
        logging.error(f'Error posting request: {e}')

        if send_response.count > 60:
            logging.critical(f"Failed to post request {send_response.count} times. Stopping")
            return 1
        else:
            logging.error(f"Retrying sending post request count: {send_response.count} in 60 seconds")

            time.sleep(60)
            send_response()

if __name__ == "__main__":
    logging.basicConfig(filename='/home/pi/projects/TnH-Tracker/client.log', format='%(asctime)s %(levelname)s %(process)d %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
    send_response.count = 0
    
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

    humidity, temperature = get_sensor_data()
    
    # format post json
    POST_DATA = {'DeviceID':f'{config.deviceID}', 'hash':'pw_test', 'CurrentDateTime':f'{dt_string}', 'Temperature':f'{temperature}','Humidity':f'{humidity}'}
    send_response()
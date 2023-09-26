import board
import adafruit_si7021
import time
from datetime import datetime
import config
import requests
import json
import logging

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
    logging.basicConfig(filename='/home/pi/TnH-Tracker/client.log', format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', encoding='utf-8', level=logging.INFO)
    send_response.count = 0
    
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

    humidity, temperature = get_sensor_data()
    
    # format post json
    POST_DATA = {'DeviceID':f'{config.deviceID}', 'hash':'pw_test', 'CurrentDateTime':f'{dt_string}', 'Temperature':f'{temperature}','Humidity':f'{humidity}'}
    send_response()
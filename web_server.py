from flask import Flask, render_template
import mariadb
import config
import time
from datetime import datetime
from device import *

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

app = Flask(__name__)

@app.route("/hello/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/")
def serve_data(name=None):
    conn = connect_to_db()
    cur = conn.cursor()

    dev1 = LastRecord(cur, 1)
    dev2 = LastRecord(cur, 2)

    g1 = GraphData(cur, 1, 60)
    g1.make_graph()
    g2 = GraphData(cur, 2, 60)
    g2.make_graph()

    g3 = GraphData(cur, 1, 1440)
    g3.make_graph()
    g4 = GraphData(cur, 2, 1440)
    g4.make_graph()

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
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# convert dt_object to 12hr time
def convert_dt(dt_obj):
    return dt_obj.strftime("%I:%M:%S %p")

class Device():
    def __init__(self, local_cur, deviceID):
        self.local_cur = local_cur
        self.deviceID = deviceID
        self.dev_name = self.find_devname()

    # returns list containing [device_name, current_date_time, temperature, humidity]
    def get_records(self, deviceID, quantity=1):
        try:
            query = '''SELECT DevName.DevName, Data_History.CurrentDateTime, History.Temperature, History.Humidity FROM Device 
                    LEFT JOIN DevName ON Device.DevNameID=DevName.DevNameID 
                    LEFT JOIN Data_History ON Data_History.DeviceID=Device.DeviceID 
                    LEFT JOIN History ON History.HistoryID=Data_History.HistoryID 
                    WHERE Device.DeviceID=%s
                    ORDER BY Data_History.CurrentDateTime DESC LIMIT %s'''
            data = (deviceID, quantity,)
            self.local_cur.execute(query, data)
            return self.local_cur.fetchall()
        except Exception as e:
            print(f"Error querying data from MariaDB: {e}")

    def find_devname(self):
        try:
            query = '''SELECT DevName.DevName FROM DevName 
                        LEFT JOIN Device ON Device.DevNameID=DevName.DevNameID 
                        WHERE DeviceID=%s'''
            data = (self.deviceID,)
            self.local_cur.execute(query, data)
            return self.local_cur.fetchone()[0]
        except Exception as e:
            print(f"Error querying devname from MariaDB: {e}")

    def get_devname(self):
        return self.dev_name

    def get_num_of_devices(self):
        try:
            query = '''SELECT DeviceID FROM Device'''
            self.local_cur.execute(query)
            num_of_devices = len(self.local_cur.fetchall())
            return num_of_devices

        except Exception as e:
            print(f"Error querying data from MariaDB: {e}")

class LastRecord(Device):
    def __init__(self, local_cur, deviceID):
        super().__init__(local_cur, deviceID)
        self.data = self.get_records(self.deviceID, 1)

    def get_time(self):
        return convert_dt(self.data[0][1])

    def get_temperature(self):
        return self.data[0][2]

    def get_humidity(self):
        return self.data[0][3]

class GraphData(Device):
    def __init__(self, local_cur, deviceID, minutes):
        super().__init__(local_cur, deviceID)
        self.data = self.get_records(self.deviceID, minutes)
        self.minutes = minutes

    def formatdata(self, value):
        xticks = []
        ydata = []
        for row in self.data:
            ydata.append(row[value])
            xticks.append(convert_dt(row[1]))
        xticks.reverse()
        ydata.reverse()
        return xticks, ydata

    def calc_ticks(self):
        denominator = self.minutes/12
        ticks = []
        for i in range(0, 13):
            if i < 1:
                ticks.append(int(i*denominator))
            else:
                ticks.append(int(i*denominator)-1)

        print(ticks)
        return ticks

    def make_graph(self):
        type_dict = {'humidity':3, 'temperature':2}
        for key in type_dict:
            x, y, = self.formatdata(type_dict[key])
            self.plot_graph(x, y, key)

    def plot_graph(self, x, y, type=''):
        string = type.capitalize()
        ticks = self.calc_ticks()
        hour = int(self.minutes/60)

        fig = plt.figure()
        plt.plot(x, y)
        plt.xticks(rotation=45, ha='right', ticks=ticks)
        plt.grid()
        plt.subplots_adjust(bottom=0.30)
        plt.title(f'{string} Graph for Last {hour} Hour(s)')
        plt.ylabel(f'{string} (%)')
        plt.xlabel('Time (last {hour} hour(s))')
        plt.savefig(f'static/{self.minutes}min_{type}_{self.deviceID}_graph.png')
        plt.close(fig)
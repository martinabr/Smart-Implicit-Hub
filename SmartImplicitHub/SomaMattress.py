import socket
import pandas as pd

from TableModel import PandasModel, CheckBoxDelegate


__copyright__ = "Copyright 2019, RISE Research Institutes of Sweden"
__author__ = "Naveed Anwar Bhatti and Martina Brachmann"


class SomaMattress:
    def __init__(self, TABLE_INFO, TABLE_FORWARDING, server_ip):
        self.FORWARDING_MATRIX = pd.read_csv("AppMatrix/SomaMattressMatrix.csv", delimiter=';')
        self.TABLE_INFO = TABLE_INFO
        self.TABLE_FORWARDING = TABLE_FORWARDING
        self.server_ip = server_ip

    def send_server_ip(self, dest_ip):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP connection
        print("About to sent the servers IP %s to %s" % (self.server_ip, dest_ip))
        try:
            s.connect((dest_ip, 5555))
            msg = self.server_ip
            s.sendall(msg.encode())
        except:
            print("Nothing exciting happend. Just trouble connecting to the Arduino.")
            print("We try again")
            s.connect((dest_ip, 5555))
            msg = self.server_ip
            s.sendall(msg.encode())
        finally:
            print("Sent the servers IP")

    def start_forwarding(self):
        print(self.FORWARDING_MATRIX)
        print(self.TABLE_FORWARDING)

        for index in range(len(self.FORWARDING_MATRIX)):
            df_sensor = self.TABLE_INFO[self.TABLE_INFO['ServiceName'] == self.FORWARDING_MATRIX.iloc[index]['ServiceName']]
            df_sensor.reset_index(inplace=True, drop=True)
            print(df_sensor)
            if len(df_sensor) > 0:
                df_actuator = self.TABLE_INFO[self.TABLE_INFO['ServiceName'] == self.FORWARDING_MATRIX.iloc[index]['Actuator']]
                df_actuator.reset_index(inplace=True, drop=True)
                print(df_actuator)
                if len(df_actuator) > 0:
                    #print(self.FORWARDING_MATRIX.iloc[index]['Sensor Address'])
                    #print(df_sensor['Device Address'])
                    if self.FORWARDING_MATRIX.iloc[index]['Sensor Address'] in df_sensor.iloc[0]['Device Address']:

                        if self.FORWARDING_MATRIX.iloc[index]['Actuator Address'] in df_actuator.iloc[0]['Device Address']:

                            self.TABLE_FORWARDING.loc[len(self.TABLE_FORWARDING)] = [
                                self.FORWARDING_MATRIX.iloc[index]['Sensor Address'], df_sensor.ix[len(df_sensor)-1, 'Address'],
                                df_sensor.ix[len(df_sensor)-1,'Port'], df_sensor.ix[len(df_sensor)-1, 'Device Range'][0],
                                self.FORWARDING_MATRIX.iloc[index]['Actuator Address'], df_actuator.ix[len(df_actuator)-1, 'Address'],
                                df_actuator.ix[len(df_actuator)-1, 'Port'], df_actuator.ix[len(df_actuator)-1,'Device Range'][0], self.FORWARDING_MATRIX.iloc[index]['Module'], self.FORWARDING_MATRIX.iloc[index]['Argument'],
                            ]

        print(self.TABLE_FORWARDING)
        sensor_ip_list = self.TABLE_FORWARDING['Sensor IP'].tolist()
        actuator_ip_list = self.TABLE_FORWARDING['Actuator IP'].tolist()
        ip_list = sensor_ip_list + actuator_ip_list
        ip_list = list(set(ip_list))
        print("IP list: ")
        print(ip_list)
        for ip in ip_list:
            self.send_server_ip(ip)

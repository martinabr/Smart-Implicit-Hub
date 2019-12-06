import logging
import sys
import socket
import pandas as pd
import threading
import glob

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (Qt, pyqtSignal, QModelIndex)

from gui import Ui_MainWindow
from module import Ui_module
from mainmodule import mainmodule
from TableModel import PandasModel, CheckBoxDelegate
from ZeroConf import NeighborDiscovery
from OSC import getOSCMessages
from SomaMattress import *

from typing import cast
from zeroconf import ServiceInfo, ServiceBrowser, ServiceStateChange, Zeroconf
from typing import List
from time import sleep

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


__copyright__ = "Copyright 2019, RISE Research Institutes of Sweden"
__author__ = "Naveed Anwar Bhatti and Martina Brachmann"


class StartQT5(QtWidgets.QMainWindow):
    def __init__(self):
        super(StartQT5, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.discover_button.clicked.connect(self.zeroconf_start)
        self.ui.save_button.clicked.connect(self.checking_application)

        self.ui.StartOSC.clicked.connect(self.start_OSC)
        self.ui.StopOSCButton.setEnabled(False)
        self.ui.StopOSCButton.setStyleSheet(
            "background-color: gray;""color: rgb(255, 255, 255);");

        self.TABLE_INFO = pd.DataFrame(columns=['Address', 'Port', 'Host Name', 'Device Count', 'Device Type', 'Device Address', 'Device Range', 'ServiceName','isSelected','isServer', 'isTaken', '*'])
        self.TABLE_INFO_CHECKBOX = 11
        self.TABLE_FORWARDING = pd.DataFrame(columns=['Sensor Address', 'Sensor IP', 'Sensor Port', 'Sensor Range', 'Actuator Address', 'Actuator IP', 'Actuator Port','Actuator Range','Module', 'Argument'])

        self.model = PandasModel(self.TABLE_INFO, checkbox=self.TABLE_INFO_CHECKBOX, signal_values_of_interest=['Address', 'Host Name'])
        self.model.pandas_signal.connect(self.handleCheckboxClicked)

        self.ui.tableView.setModel(self.model)
        self.ui.tableView.hideColumn(7)
        self.ui.tableView.hideColumn(8)
        self.ui.tableView.hideColumn(9)
        self.ui.tableView.hideColumn(10)
        delegate = CheckBoxDelegate(self)
        self.ui.tableView.setItemDelegateForColumn(self.TABLE_INFO_CHECKBOX, delegate)

        self.check_service_timer = threading.Timer(5.0, self.check_services)
        self.check_service_timer.start()
        self.ui.moduleSelection.clicked.connect(self.open_dialog)
        self.selected_module = []
        self.ui.Soma_Mattress_pushButton.clicked.connect(self.application_soma_mattress)

    def checking_application(self):
        if self.ui.application_checkBox.isChecked():
           self.application_forwarding()
        else:
           self.start_forwarding()

    def start_OSC(self):
        #self.TABLE_FORWARDING = self.TABLE_FORWARDING.set_index(['Sensor Address', 'Sensor IP'])
        self.get_thread = getOSCMessages(NeighborDiscovery().get_local_ip(), 3333, self)
        self.get_thread.start()
        self.ui.StartOSC.setEnabled(False)
        self.ui.StartOSC.setStyleSheet("background-color: gray;""color: rgb(255, 255, 255);")
        self.ui.tableView_2.setEnabled(False)
        self.ui.tableView.setEnabled(False)
        self.ui.discover_button.setEnabled(False)
        self.ui.discover_button.setStyleSheet("background-color: gray;""color: rgb(255, 255, 255);")
        self.ui.save_button.setEnabled(False)
        self.ui.save_button.setStyleSheet("background-color: gray;\n""color: rgb(255, 255, 255);""font: 63 10pt \"Adobe Fan Heiti Std B\";")
        self.ui.StopOSCButton.setEnabled(True)
        self.ui.StopOSCButton.setStyleSheet(
                                         "background-color: rgb(170, 0, 0);\n"
                                         "color: rgb(255, 255, 255);")
        self.ui.StopOSCButton.clicked.connect(self.OSC_stop)

    def OSC_stop(self):
        self.ui.StartOSC.setEnabled(True)
        self.ui.StartOSC.setStyleSheet("background-color: rgb(170, 255, 127);\n"
                                    "font: 63 10pt \"Adobe Fan Heiti Std B\";\n"
                                    "color: rgb(0, 0, 0);")
        self.ui.tableView_2.setEnabled(True)
        self.ui.tableView.setEnabled(True)
        self.ui.discover_button.setEnabled(True)
        self.ui.save_button.setEnabled(True)
        self.ui.StopOSCButton.setEnabled(False)
        self.ui.StopOSCButton.setStyleSheet(
            "background-color: gray;""color: rgb(255, 255, 255);")
        self.get_thread.server.server_close()

    def ForwardCheckboxClicked(self):
        Checkbox = QtWidgets.qApp.focusWidget()
        if Checkbox.isChecked():
            mainmodule(self).exec_()
            sensors, sensors_IP, sensors_Port, sensors_Range = str(Checkbox.accessibleName()).split(":")
            actuators, actuators_IP, actuators_Port, actuators_Range = str(Checkbox.accessibleDescription()).split(":")
            self.TABLE_FORWARDING.loc[len(self.TABLE_FORWARDING)] =[sensors,sensors_IP,sensors_Port,sensors_Range,actuators, actuators_IP, actuators_Port, actuators_Range, self.selected_module, None]
            print(self.TABLE_FORWARDING)
        else:
            sensors, sensors_IP, sensors_Port, sensors_Range = str(Checkbox.accessibleName()).split(":")
            actuators, actuators_IP, actuators_Port, actuators_Range = str(Checkbox.accessibleDescription()).split(":")
            indexNames = self.TABLE_FORWARDING[(self.TABLE_FORWARDING['Sensor Address'] == sensors) & (self.TABLE_FORWARDING['Sensor IP'] == sensors_IP) & (self.TABLE_FORWARDING['Sensor Port'] == sensors_Port) & (self.TABLE_FORWARDING['Sensor Range'] == sensors_Range) & (self.TABLE_FORWARDING['Actuator Address'] == actuators) & (self.TABLE_FORWARDING['Actuator IP'] == actuators_IP) & (self.TABLE_FORWARDING['Actuator Port'] == actuators_Port) & (self.TABLE_FORWARDING['Actuator Range'] == actuators_Range)].index
            self.TABLE_FORWARDING.drop(indexNames, inplace=True)
            # TODO: Might need re-indexing
            # self.TABLE_FORWARDING.reset_index(inplace=True, drop=True)
            print(self.TABLE_FORWARDING)


    def start_forwarding(self):
        sensors = []
        sensors_IP = []
        sensors_Port = []
        sensors_Range = []
        actuators = []
        actuators_IP = []
        actuators_Port = []
        actuators_Range = []

        for rows in range(len(self.TABLE_INFO)):
            if self.TABLE_INFO.iloc[rows]['isServer'] == False and self.TABLE_INFO.iloc[rows]['isSelected'] == True:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP connection
                print("About to sent the servers IP %s to %s" % (self.discovery.get_local_ip(), self.TABLE_INFO.iloc[rows]['Address']))
                try:
                    s.connect((self.TABLE_INFO.iloc[rows]['Address'], 5555))
                    msg = str(self.discovery.get_local_ip())
                    s.sendall(msg.encode())
                except:
                    pass
                finally:
                    print("Sent the servers IP")
            for devices in range(self.TABLE_INFO.iloc[rows]['Device Count']):
                if self.TABLE_INFO.iloc[rows]['isSelected'] == True:
                    # First we send a message to inform the nodes about our IP (as long as the MDNS bug in the Arduinos exists)
                    if 'sensor' in str(self.TABLE_INFO.iloc[rows]['Device Type'][devices]):
                        sensors.append(self.TABLE_INFO.iloc[rows]['Device Address'][devices])
                        sensors_IP.append(self.TABLE_INFO.iloc[rows]['Address'])
                        sensors_Port.append(self.TABLE_INFO.iloc[rows]['Port'])
                        sensors_Range.append(self.TABLE_INFO.iloc[rows]['Device Range'][devices])
                    else:
                        actuators.append(self.TABLE_INFO.iloc[rows]['Device Address'][devices])
                        actuators_IP.append(self.TABLE_INFO.iloc[rows]['Address'])
                        actuators_Port.append(self.TABLE_INFO.iloc[rows]['Port'])
                        actuators_Range.append(self.TABLE_INFO.iloc[rows]['Device Range'][devices])

        forward_table = pd.DataFrame(index=sensors,columns=actuators)
        model = PandasModel(forward_table)
        self.ui.tableView_2.setModel(model)

        for rows in range(model.rowCount()):
            for column in range(model.columnCount()):
                self.Checkbox = QtWidgets.QCheckBox(' ')
                sensor_data = str(sensors[rows]) + ':' + str(sensors_IP[rows]) + ':' + str(sensors_Port[rows]) + ':' + str(sensors_Range[
                    rows])
                actuator_data = str(actuators[column]) + ':' + str(actuators_IP[column]) + ':' + str(actuators_Port[column]) + ':' + str(actuators_Range[
                    column])
                self.Checkbox.setAccessibleName(sensor_data)
                self.Checkbox.setAccessibleDescription(actuator_data)
                self.Checkbox.clicked.connect(self.ForwardCheckboxClicked)

                checkBoxWidget = QtWidgets.QWidget()
                layoutCheckBox = QtWidgets.QHBoxLayout(checkBoxWidget)
                layoutCheckBox.addWidget(self.Checkbox)
                layoutCheckBox.setAlignment(Qt.AlignCenter);

                item = model.index(rows, column )
                self.ui.tableView_2.setIndexWidget(item, self.Checkbox)

        self.ui.tableView_2.setModel(model)
        self.ui.tabWidget.setCurrentIndex(1)

    def application_forwarding(self):
        self.ui.tabWidget.setCurrentIndex(2)

    def application_soma_mattress(self):
        soma_mattress = SomaMattress(self.TABLE_INFO, self.TABLE_FORWARDING, str(self.discovery.get_local_ip()))
        soma_mattress.start_forwarding()
        print(self.TABLE_FORWARDING)
        self.start_OSC()

    def resizeEvent(self, event):
        tableSize = self.ui.tableView.width()  # Retrieves your QTableView width
        sideHeaderWidth = self.ui.tableView.verticalHeader().width()  # Retrieves the left header width
        tableSize -= sideHeaderWidth  # Perform a substraction to only keep all the columns width
        numberOfColumns = self.model.columnCount()  # Retrieves the number of columns

        for columnNum in range(self.model.columnCount()):  # For each column
            self.ui.tableView.setColumnWidth(columnNum,
                                     int(tableSize / numberOfColumns))  # Set the width = tableSize / nbColumns
        super(StartQT5, self).resizeEvent(event)  # Restores the original behaviour of the resize event

    def update_view(self):
        print("update_view()")
        self.model.update()
        for row in range(self.model.rowCount()):
            self.ui.tableView.setRowHidden(row, False)

        df = self.TABLE_INFO[self.TABLE_INFO["isServer"] == True]
        rows_to_hide = df.index.values.tolist()
        df = self.TABLE_INFO[self.TABLE_INFO["isTaken"] == True]
        row_to_hide_tmp = df.index.values.tolist()

        rows_to_hide = rows_to_hide + list(set(row_to_hide_tmp) - set(rows_to_hide))
        print(rows_to_hide)

        if len(rows_to_hide) > 0:
            for row in rows_to_hide:
                self.ui.tableView.setRowHidden(row, True)
        self.model.update()

    def check_services(self):
        for rows in range(len(self.TABLE_INFO)):
            print("Checking \n")
            print(self.TABLE_INFO)
            info = self.discovery.zeroconf.get_service_info(self.discovery.get_soma_type(), self.TABLE_INFO.iloc[rows]['ServiceName'])
            if info is None:
                self.handleServiceRemoved(self.TABLE_INFO.iloc[rows]['ServiceName'])
                self.update_view()

    def handleCheckboxClicked(self, value, ip, host):
        if value is 1:
            self.discovery.register_service(ip, host)
        elif value is 0:
            self.discovery.unregister_service(ip, host)

    def handleServiceAdded(self, info, name):
        device_type = []
        device_address = []
        device_range = []

        device_ip = socket.inet_ntoa(cast(bytes, info.address))

        print("  Address: %s:%d" % (device_ip, cast(int, info.port)))
        print("  Weight: %d, priority: %d" % (info.weight, info.priority))
        print("  Server: %s" % (info.server))

        if info.properties:
            print("  Properties are:")

            for key, value in info.properties.items():
                print("    %s: %s" % (key, value))
                key_str = str(key).split("'")[1]
                device_type.append(key_str)
                if ":" in str(value):
                    # the device has sensor values
                    value_str = str(value).split("'")[1].split(':')
                    device_address.append(value_str[0])
                    device_range.append(value_str[1])
                else:
                    # the device does not have sensor values
                    value_str = str(value).split("'")[1]
                    device_address.append(value_str)
                    device_range.append('0%1')
        else:
            print("  No properties")
        print()

        if device_ip not in self.TABLE_INFO["Address"].to_list() or name not in self.TABLE_INFO["ServiceName"].to_list():
            # The IP is not in TABLE_INFO yet
            if device_ip == NeighborDiscovery().get_local_ip() and 'Server' in str(info.server):
                # It is a service from this server
                # Check if service already exists (happens if two users click on the same device at the same time)
                if info.server in self.TABLE_INFO['Host Name'].to_list():
                    # This should not have happend. We have two services with the same name
                    print("[INFO] Sorry, another server with IP %s has allocated the device" % (device_ip))
                else:
                    self.TABLE_INFO.loc[len(self.TABLE_INFO)] = [
                        device_ip, cast(int, info.port), info.server,
                        len(device_type), device_type, device_address, device_range, name, False, True, False, 0]
                    # Mark the entry of the specific device as selected
                    self.TABLE_INFO.at[self.TABLE_INFO.index[self.TABLE_INFO["Address"].isin([device_address[1]])].tolist()[0], 'isSelected'] = True
            elif device_ip != NeighborDiscovery().get_local_ip() and 'Server' in str(info.server):
                # It is a message from another server
                # Check if service already exists (happens if two users click on the same device at the same time)
                if info.server in self.TABLE_INFO['Host Name'].to_list():
                    print("[INFO] Sorry, another server with IP %s has allocated the device" % (device_ip))
                else:
                    self.TABLE_INFO.loc[len(self.TABLE_INFO)] = [
                        device_ip, cast(int, info.port), info.server,
                        len(device_type), device_type, device_address, device_range, name, False, True, False, 0]
                    # Mark the entry of the specific device as taken
                    # First check, if the entry exists
                    if device_address[1] in self.TABLE_INFO["Address"].to_list():
                        self.TABLE_INFO.at[self.TABLE_INFO.index[self.TABLE_INFO["Address"].isin([device_address[1]])].tolist()[0], 'isTaken'] = True
            else:
                # Check if a server has already announced to allocate the device
                flat_device_address_list = [item for sublist in self.TABLE_INFO['Device Address'].to_list() for item in sublist]

                if device_ip in flat_device_address_list:

                    self.TABLE_INFO.loc[len(self.TABLE_INFO)] = [
                        device_ip, cast(int, info.port), info.server,
                        len(device_type), device_type, device_address, device_range, name, False, False, True, 0]

                else:
                    self.TABLE_INFO.loc[len(self.TABLE_INFO)] = [
                        device_ip, cast(int, info.port), info.server,
                        len(device_type), device_type, device_address, device_range, name, False, False, False, 0]
        #else:
            # The IP is already in TABLE_INFO
            # Check if service already exists (happens if two users click on the same device at the same time)
            #if info.server in self.TABLE_INFO['Host Name'].to_list():
            #    print("[INFO] Sorry, another server with IP %s has allocated the device" % (device_ip))
            #    self.discovery.unregister_service(device_ip, info.server)
            #else:
            #    print("[WARNING] Either IP or Service are in TABLE_INFO, but not the host name: %s" % (info.server))
        self.update_view()

    def handleServiceRemoved(self, name):
        if name in self.TABLE_INFO["ServiceName"].to_list():
            df = self.TABLE_INFO[self.TABLE_INFO["ServiceName"] == name]
            device_to_free = [item for sublist in df['Device Address'].to_list() for item in sublist]

            if df["Address"].to_list()[0] == NeighborDiscovery().get_local_ip() and 'Server' in name:
                # This server has released the device
                self.TABLE_INFO.at[self.TABLE_INFO.index[self.TABLE_INFO["Address"].isin([device_to_free[1]])], 'isSelected'] = False
                # Delete the service
                self.TABLE_INFO.drop(self.TABLE_INFO.loc[self.TABLE_INFO['ServiceName'] == name].index, inplace=True)
                self.TABLE_INFO.reset_index(inplace=True, drop=True)

            elif df["Address"].to_list()[0] != NeighborDiscovery().get_local_ip() and 'Server' in name:
                # Another server has released a device
                # First check if the device exists
                if device_to_free[1] in self.TABLE_INFO["Address"].to_list():
                    self.TABLE_INFO.at[self.TABLE_INFO.index[self.TABLE_INFO["Address"].isin([device_to_free[1]])], 'isTaken'] = False
                # Remove server from TABLE_INFO
                self.TABLE_INFO.drop(self.TABLE_INFO.loc[self.TABLE_INFO['ServiceName'] == name].index, inplace=True)
                self.TABLE_INFO.reset_index(inplace=True, drop=True)

            else:
                # A device has unregistered
                # Remove server from TABLE_INFO
                self.TABLE_INFO.drop(self.TABLE_INFO.loc[self.TABLE_INFO['ServiceName'] == name].index, inplace=True)
                self.TABLE_INFO.reset_index(inplace=True, drop=True)
                print("[WARNING] A device has unregistered")
        self.update_view()

    def on_device_found(self, zeroconf, service_type, name, state_change):
        print("Service %s of type %s state changed: %s" % (name, service_type, state_change))

        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)

            if info:
                self.handleServiceAdded(info, name)
        elif state_change is ServiceStateChange.Removed:
            self.handleServiceRemoved(name)

    def zeroconf_start(self):
        self.discovery = NeighborDiscovery()
        self.discovery.neighbor_signal.connect(self.on_device_found)
        self.ui.discover_button.setEnabled(False)
        self.ui.discover_button.setStyleSheet("background-color: gray;""color: rgb(204, 204, 204);")
        self.check_services()

    def on_close(self):
        print("Disable service detection....")
        self.check_service_timer.cancel()

        # Unregister all services
        print("Unregistering services...")
        for rows in range(len(self.TABLE_INFO)):
            self.discovery.unregister_service(self.TABLE_INFO.iloc[rows]['Address'], self.TABLE_INFO.iloc[rows]['ServiceName'])

        # Close zeroconf
        print("Closing Zeroconf...")
        if self.ui.discover_button.isEnabled():
            print("Have not started Zeroconf. Nothing to Close.")
        else:
            self.discovery.browser.cancel()
            self.discovery.zeroconf.close()

    def open_dialog(self):
        mainmodule(self).exec_()
        print(self.selected_module)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)

    app = QtWidgets.QApplication(sys.argv)
    myapp = StartQT5()
    myapp.show()
    app.aboutToQuit.connect(myapp.on_close)
    sys.exit(app.exec_())

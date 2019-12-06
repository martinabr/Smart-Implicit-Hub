#!/usr/bin/env python


import logging
import socket
import ifaddr
import sys
from time import sleep
import numpy as np

from pythonosc import udp_client

from zeroconf import ServiceInfo, Zeroconf
from typing import List


__copyright__ = "Copyright 2019, RISE Research Institutes of Sweden"
__author__ = "Naveed Anwar Bhatti and Martina Brachmann"


desc = {'sensor1': '/pressure1:0%100', 'sensor2': '/pressure2:0%100', 'sensor3': '/pressure3:0%100'}


def get_all_addresses() -> List[str]:
    return list(set(
        addr.ip
        for iface in ifaddr.get_adapters()
        for addr in iface.ips
        if addr.is_IPv4 and addr.network_prefix != 32  # Host only netmask 255.255.255.255
    ))


def get_local_ip(starts_with="192"):
    list_ip = get_all_addresses()
    local_ip = [i for i in list_ip if i.startswith(starts_with)]
    return local_ip[0]


def send_sensor_values(sensor_state_, sensor_direction_, server):
    sensor_state = sensor_state_
    sensor_direction = sensor_direction_
    max_count_idle = 60
    count_idle = 0

    client = udp_client.SimpleUDPClient(server, int(3333))

    osc_addr = "/pressure" + str(np.random.randint(1, len(desc)+1))

    while True:
        if count_idle != max_count_idle and sensor_state == 100 and sensor_direction == 0:
            # wait for down
            count_idle += 1
        elif count_idle == max_count_idle and sensor_direction == 0 and sensor_state == 100:
            # prepair for down
            sensor_direction = 1
            osc_addr = "/pressure" + str(np.random.randint(1, len(desc)+1))
        elif sensor_direction == 1 and sensor_state != 5:
            # going down
            sensor_state -= 1
        elif sensor_state == 5 and sensor_direction == 1 and count_idle == max_count_idle:
            # prepair for up
            count_idle = 0
            sensor_direction = 0
        elif count_idle != max_count_idle and sensor_state == 5 and sensor_direction == 0:
            # wait for up
            count_idle += 1
        elif count_idle == max_count_idle and sensor_direction == 0 and sensor_state != 100:
            # going up
            sensor_state += 1

        #print("about to send osc")
        #print(osc_addr)
        client.send_message(osc_addr, float(sensor_state))
        print("OSC = %s, Value = %s, Direction = %s, Count = %s" % (osc_addr, sensor_state, sensor_direction, count_idle))
        sleep(0.2)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)

    initial_sensor_state = 100 # highest value
    print("Initial sensor state: %s" % initial_sensor_state)
    sensor_direction = 0 # going up
    print("Initial sensor direction: %s" % sensor_direction)

    info = ServiceInfo(type_="_osc._udp.local.",
                       name="Python3PressureSensor._osc._udp.local.",
                       address=socket.inet_aton(get_local_ip()),
                       port=3335,
                       weight=0,
                       priority=0,
                       properties=desc,
                       server="Python3PressureSensor.local.")

    zeroconf = Zeroconf()
    print("Registration of a service PythonSensor")
    zeroconf.register_service(info)

    print("Opening a TCP connection")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(get_local_ip())
    s.bind((str(get_local_ip()), 5555))
    s.listen()

    conn, addr = s.accept()
    print("Connection address:  " + str(addr))

    server_ip = ""
    while True:
        data = conn.recv(20)
        if not data:
            break
        server_ip = str(data.decode())
        print("Server IP is: " + str(data.decode()))

    while True:
        try:
            send_sensor_values(initial_sensor_state, sensor_direction, server_ip)
        except:
            pass

    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Unregistering...")
        zeroconf.unregister_service(info)
        zeroconf.close()

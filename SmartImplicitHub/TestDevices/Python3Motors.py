#!/usr/bin/env python

from multiprocessing import Process

import logging
import socket
import ifaddr
import sys
from time import sleep
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

from matplotlib import animation

print(plt.get_backend())

from zeroconf import ServiceInfo, Zeroconf
from typing import List
from multiprocessing import Process, Manager


__copyright__ = "Copyright 2019, RISE Research Institutes of Sweden"
__author__ = "Naveed Anwar Bhatti and Martina Brachmann"


motor_values = Manager().list([[], [], []])


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


def save_motor_value(addr, args, motor):
    if addr == "/motor1":
        l = args[1][0]
        l.append(motor)
        args[1][0] = l
    if addr == "/motor2":
        l = args[1][1]
        l.append(motor)
        args[1][1] = l
    if addr == "/motor3":
        l = args[1][2]
        l.append(motor)
        args[1][2] = l
    #print(args[1])


def get_motor_value():
    print(len(motor_values[0]))
    print(motor_values[0])

    l = motor_values[0]
    if len(l) > 1:
        motor_1 = l.pop(0)
    else:
        motor_1 = l[0]
    motor_values[0] = l

    l = motor_values[1]
    if len(l) > 1:
        motor_2 = l.pop(0)
    else:
        motor_2 = l[0]
    motor_values[1] = l

    l = motor_values[2]
    if len(l) > 1:
        motor_3 = l.pop(0)
    else:
        motor_3 = l[0]
    motor_values[2] = l

    return [motor_1, motor_2, motor_3]


def animate(frameno, p1):
    value = get_motor_value()
    #print(value)
    p1[0].set_height(value[0])
    p1[1].set_height(value[1])
    p1[2].set_height(value[2])
    return p1


def run_OSC(motor_values_):
    from pythonosc import dispatcher
    from pythonosc import osc_server

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/motor1", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor2", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor3", save_motor_value, "Motor", motor_values_)
    server = osc_server.ThreadingOSCUDPServer((server_ip, 3335), dispatcher)

    print("Serving OSC on {}".format(server.server_address))
    server.serve_forever()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)

    #motor_values.append([], [], [])
    initial_motor_state = np.random.randint(0, 100+1)
    print("Initial motor state: %s" % initial_motor_state)
    #save_motor_value(None, [None, motor_values], initial_motor_state)
    save_motor_value("/motor1", [None, motor_values], initial_motor_state)
    save_motor_value("/motor2", [None, motor_values], initial_motor_state)
    save_motor_value("/motor3", [None, motor_values], initial_motor_state)

    desc = {'actuator1': '/motor1:0%100', 'actuator2': '/motor2:0%100', 'actuator3': '/motor3:0%100'}
    #desc = {'actuator1': '/motor1:0%100'}

    info = ServiceInfo(type_="_osc._udp.local.",
                       name="Python3Motors._osc._udp.local.",
                       address=socket.inet_aton(get_local_ip()),
                       port=3335,
                       weight=0,
                       priority=0,
                       properties=desc,
                       server="Python3Motors.local.")

    zeroconf = Zeroconf()
    print("Registration of a service PythonActuator")
    zeroconf.register_service(info)

    print("Opening a TCP connection")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(get_local_ip())
    s.bind((str(get_local_ip()), 5555))
    s.listen()

    conn, addr = s.accept()
    print("Connection address:  " + str(addr))

    while True:
        data = conn.recv(20)
        if not data:
            break
        server_ip = str(data.decode())
        print("Server IP is: " + server_ip)

    P1 = Process(target=run_OSC, args=[motor_values])
    P1.start()

    fig, ax = plt.subplots()
    #p1 = plt.bar(0, initial_motor_state, color='b')
    x = [0, 1, 2]
        #range(0, len(motor_values))

    y = get_motor_value()
    print(y)
    p1 = plt.bar(x, y, color='b')
    ax.set_ylim(0, 100)

    anim = animation.FuncAnimation(fig, animate, interval=0, frames=None, fargs=[p1], repeat=False, blit=True)
    plt.show()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass
    finally:
        print("Unregistering...")
        zeroconf.unregister_service(info)
        zeroconf.close()

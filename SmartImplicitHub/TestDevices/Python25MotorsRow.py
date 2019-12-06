#!/usr/bin/env python

import logging
import socket
import ifaddr
import sys
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import re

from matplotlib import animation

print(plt.get_backend())

from zeroconf import ServiceInfo, Zeroconf
from typing import List
from multiprocessing import Process, Manager


__copyright__ = "Copyright 2019, RISE Research Institutes of Sweden"
__author__ = "Naveed Anwar Bhatti and Martina Brachmann"


motor_values = Manager().list([[] for x in range(25)])

reg_str = re.compile(r"(\D+)(\d+)")


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
    m_str = reg_str.match(addr)
    if m_str:
        _, num = m_str.groups()[0:]
        l = args[1][int(num)-1]
        l.append(motor)
        args[1][int(num)-1] = l


def get_motor_value():
    motors = []
    for i in range(len(motor_values)):
        #print(i)
        l = motor_values[i]
        #print(l)
        if len(l) > 1:
            motor = l.pop(0)
        else:
            motor = l[0]
        motors.append(motor)
        motor_values[i] = l
    #print(motors)
    return motors


def animate(frameno, p1):
    value = get_motor_value()
    #print(value)
    for i in range(len(value)):
        p1[i].set_height(value[i])
    return p1


def run_OSC(motor_values_):
    from pythonosc import dispatcher
    from pythonosc import osc_server

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/motor1", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor2", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor3", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor4", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor5", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor6", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor7", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor8", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor9", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor10", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor11", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor12", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor13", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor14", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor15", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor16", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor17", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor18", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor19", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor20", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor21", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor22", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor23", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor24", save_motor_value, "Motor", motor_values_)
    dispatcher.map("/motor25", save_motor_value, "Motor", motor_values_)

    server = osc_server.ThreadingOSCUDPServer((server_ip, 3335), dispatcher)

    print("Serving OSC on {}".format(server.server_address))
    server.serve_forever()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)

    initial_motor_state = 100 #np.random.randint(0, 100+1)
    print("Initial motor state: %s" % initial_motor_state)

    save_motor_value("/motor1", [None, motor_values], initial_motor_state)
    save_motor_value("/motor2", [None, motor_values], initial_motor_state)
    save_motor_value("/motor3", [None, motor_values], initial_motor_state)
    save_motor_value("/motor4", [None, motor_values], initial_motor_state)
    save_motor_value("/motor5", [None, motor_values], initial_motor_state)
    save_motor_value("/motor6", [None, motor_values], initial_motor_state)
    save_motor_value("/motor7", [None, motor_values], initial_motor_state)
    save_motor_value("/motor8", [None, motor_values], initial_motor_state)
    save_motor_value("/motor9", [None, motor_values], initial_motor_state)
    save_motor_value("/motor10", [None, motor_values], initial_motor_state)
    save_motor_value("/motor11", [None, motor_values], initial_motor_state)
    save_motor_value("/motor12", [None, motor_values], initial_motor_state)
    save_motor_value("/motor13", [None, motor_values], initial_motor_state)
    save_motor_value("/motor14", [None, motor_values], initial_motor_state)
    save_motor_value("/motor15", [None, motor_values], initial_motor_state)
    save_motor_value("/motor16", [None, motor_values], initial_motor_state)
    save_motor_value("/motor17", [None, motor_values], initial_motor_state)
    save_motor_value("/motor18", [None, motor_values], initial_motor_state)
    save_motor_value("/motor19", [None, motor_values], initial_motor_state)
    save_motor_value("/motor20", [None, motor_values], initial_motor_state)
    save_motor_value("/motor21", [None, motor_values], initial_motor_state)
    save_motor_value("/motor22", [None, motor_values], initial_motor_state)
    save_motor_value("/motor23", [None, motor_values], initial_motor_state)
    save_motor_value("/motor24", [None, motor_values], initial_motor_state)
    save_motor_value("/motor25", [None, motor_values], initial_motor_state)

    desc = {'actuator1': '/motor1:0%100', 'actuator2': '/motor2:0%100', 'actuator3': '/motor3:0%100',
            'actuator4': '/motor4:0%100', 'actuator5': '/motor5:0%100', 'actuator6': '/motor6:0%100',
            'actuator7': '/motor7:0%100', 'actuator8': '/motor8:0%100', 'actuator9': '/motor9:0%100',
            'actuator10': '/motor10:0%100', 'actuator11': '/motor11:0%100', 'actuator12': '/motor12:0%100',
            'actuator13': '/motor13:0%100', 'actuator14': '/motor14:0%100', 'actuator15': '/motor15:0%100',
            'actuator16': '/motor16:0%100', 'actuator17': '/motor17:0%100', 'actuator18': '/motor18:0%100',
            'actuator19': '/motor19:0%100', 'actuator20': '/motor20:0%100', 'actuator21': '/motor21:0%100',
            'actuator22': '/motor22:0%100', 'actuator23': '/motor23:0%100', 'actuator24': '/motor24:0%100',
            'actuator25': '/motor25:0%100'}

    info = ServiceInfo(type_="_osc._udp.local.",
                       name="Python25MotorsGrid._osc._udp.local.",
                       address=socket.inet_aton(get_local_ip()),
                       port=3335,
                       weight=0,
                       priority=0,
                       properties=desc,
                       server="Python25MotorsGrid.local.")

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
    x = np.arange(0, len(motor_values))
    y = get_motor_value()
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

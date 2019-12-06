#!/usr/bin/env python

"https://github.com/jstasiak/python-zeroconf/blob/master/examples/registration.py"
from multiprocessing import Process

""" Example of announcing a service (in this case, a fake HTTP server) """

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


motor_values = Manager().list()


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


def save_motor_value(unused_addr, args, motor):
    args[1].append(motor)


def get_motor_value():
    if len(motor_values) > 1:
        return motor_values.pop(0)
    else:
        return motor_values[0]


def animate(frameno, p1):
    p1[0].set_height(get_motor_value())
    return p1


def run_OSC(motor_values_):
    from pythonosc import dispatcher
    from pythonosc import osc_server

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/motor", save_motor_value, "Motor", motor_values_)
    server = osc_server.ThreadingOSCUDPServer((server_ip, 3335), dispatcher)

    print("Serving OSC on {}".format(server.server_address))
    server.serve_forever()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)

    initial_motor_state = np.random.randint(0, 100+1)
    print("Initial motor state: %s" % initial_motor_state)
    save_motor_value(None, [None, motor_values], initial_motor_state)

    desc = {'actuator1': '/motor:0%100'}

    info = ServiceInfo(type_="_osc._udp.local.",
                       name="PythonActuator._osc._udp.local.",
                       address=socket.inet_aton(get_local_ip()),
                       port=3335,
                       weight=0,
                       priority=0,
                       properties=desc,
                       server="PythonActuator.local.")

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
    p1 = plt.bar(0, initial_motor_state, color='b')
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

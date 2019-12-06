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


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)

    desc = {'sensor1': '/proximity:0%5'}

    info = ServiceInfo(type_="_osc._udp.local.",
                       name="FakeOSCPhone._osc._udp.local.",
                       address=socket.inet_aton("192.168.11.158"),
                       port=5005,
                       weight=0,
                       priority=0,
                       properties=desc,
                       server="FakeOSCPhone.local.")

    zeroconf = Zeroconf()
    print("Registration of a service PythonSensor")
    zeroconf.register_service(info)

    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Unregistering...")
        zeroconf.unregister_service(info)
        zeroconf.close()

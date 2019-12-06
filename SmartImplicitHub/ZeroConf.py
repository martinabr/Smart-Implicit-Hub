import ifaddr
import socket
from time import sleep
import random

from zeroconf import ServiceInfo,ServiceBrowser, ServiceStateChange, Zeroconf
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (Qt, pyqtSignal)
from typing import List


__copyright__ = "Copyright 2019, RISE Research Institutes of Sweden"
__author__ = "Naveed Anwar Bhatti and Martina Brachmann"


TYPE = '_osc._udp.local.'
NAME = 'Server'


class NeighborDiscovery(QtCore.QThread):
    neighbor_signal = QtCore.pyqtSignal(object, object, object, object)

    def __init__(self):
        QtCore.QThread.__init__(self)
        self.zeroconf = Zeroconf()
        self.browser = ServiceBrowser(self.zeroconf, TYPE, handlers=[self.on_service_state_change], delay=60)

    def on_service_state_change(self,zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange, ) -> None:
        self.neighbor_signal.emit(zeroconf, service_type, name, state_change)

    def register_service(self, ip, service_name):
        TXT_record = {'server': self.get_local_ip()}
        TXT_record.update({"device": ip})

        name = service_name.split('.')[0]
        name = NAME + "_" + name

        info = ServiceInfo(type_=TYPE,
                           name=name + "." + TYPE,
                           address=socket.inet_aton(self.get_local_ip()),
                           port=80,
                           weight=0,
                           priority=0,
                           properties=TXT_record,
                           server=name + ".local.")

        self.zeroconf.register_service(info, allow_name_change=False)
        print("Registration of a service %s" % (name))

    def unregister_service(self, ip, service_name):
        name = NAME + "_" + service_name.split(".")[0] + "." + TYPE

        info = self.zeroconf.get_service_info(TYPE, name)
        if info:
            self.zeroconf.unregister_service(info)
            print("Unregistering service %s with IP %s" % (name, ip))

    def get_all_addresses(self) -> List[str]:
        return list(set(
            addr.ip
            for iface in ifaddr.get_adapters()
            for addr in iface.ips
            if addr.is_IPv4 and addr.network_prefix != 32  # Host only netmask 255.255.255.255
        ))

    def get_local_ip(self, starts_with="192"):
        list_ip = self.get_all_addresses()
        local_ip = [i for i in list_ip if i.startswith(starts_with)]
        return local_ip[0]

    @staticmethod
    def get_soma_type():
        return TYPE

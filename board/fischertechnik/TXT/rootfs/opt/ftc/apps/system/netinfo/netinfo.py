#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import sys, os, socket, array, struct, fcntl, string, platform
from TouchStyle import *

SIOCGIFCONF    = 0x8912
SIOCGIFADDR    = 0x8915
SIOCGIFNETMASK = 0x891b

def _ifinfo(sock, addr, ifname):
    iface = struct.pack('256s', bytes(ifname[:15], "UTF-8"))
    info  = fcntl.ioctl(sock.fileno(), addr, iface)
    return socket.inet_ntoa(info[20:24])

def all_interfaces():
    if platform.machine() == "armv7l": size = 32
    else:                              size = 40
    
    bytes = 8 * size
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    names = array.array('B', b'\x00' * bytes)
    outbytes = struct.unpack('iL', fcntl.ioctl(
        s.fileno(), SIOCGIFCONF,
        struct.pack('iL', bytes, names.buffer_info()[0])
    ))[0]
    namestr = names.tostring()

    # get additional info for all interfaces found
    lst = []
    for i in range(0, outbytes, size):
        name = namestr[i:i+16].decode('UTF-8').split('\0', 1)[0]
        if name != "":
            addr = _ifinfo(s, SIOCGIFADDR, name)
            mask = _ifinfo(s, SIOCGIFNETMASK, name)
            lst.append((name, addr, mask))
    return lst

class FtcGuiApplication(TouchApplication):
    def __init__(self, args):
        global ifs

        TouchApplication.__init__(self, args)
        translator = QTranslator()
        path = os.path.dirname(os.path.realpath(__file__))
        translator.load(QLocale.system(), os.path.join(path, "netinfo_"))
        self.installTranslator(translator)

        self.w = TouchWindow(QCoreApplication.translate("Main", "NetInfo"))

        ifs = all_interfaces()

        self.vbox = QVBoxLayout()

        self.nets_w = QComboBox()
        self.nets_w.activated[str].connect(self.set_net)
        for i in ifs:
            self.nets_w.addItem(i[0])

        self.vbox.addWidget(self.nets_w)

        self.vbox.addStretch()

        self.ip_lbl = QLabel(QCoreApplication.translate("Main", "Address:"))
        self.ip_lbl.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.ip_lbl)

        self.ip = QLabel("")
        self.ip.setObjectName("smalllabel")
        self.ip.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.ip)
   
        self.mask_lbl = QLabel(QCoreApplication.translate("Main", "Netmask:"))
        self.mask_lbl.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.mask_lbl)

        self.mask = QLabel("")
        self.mask.setObjectName("smalllabel")
        self.mask.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.mask)

        # select wlan0 if in list
        ifn = [i[0] for i in ifs]
        select = "wlan0"
        if select in ifn:
            self.nets_w.setCurrentIndex(ifn.index(select))
            self.set_net(select)
        else:
            self.set_net(ifn[0])
   
        self.vbox.addStretch()

        self.w.centralWidget.setLayout(self.vbox)

        self.w.show() 
        self.exec_()        

    def set_net(self,name):
        global ifs
        for interface in ifs:
            if interface[0] == name:
                self.ip.setText(interface[1])
                self.mask.setText(interface[2])

if __name__ == "__main__":
    FtcGuiApplication(sys.argv)

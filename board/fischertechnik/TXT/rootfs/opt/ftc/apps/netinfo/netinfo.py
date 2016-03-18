#! /usr/bin/env python
# -*- coding: utf-8 -*-
#

import sys, os, socket, array, struct, fcntl, string, platform
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# import TXT style
local = os.path.dirname(os.path.realpath(__file__)) + "/"
base = local + "../../"
sys.path.append(base)
from txt import *
from ctypes import *

SIOCGIFCONF    = 0x8912
SIOCGIFADDR    = 0x8915
SIOCGIFNETMASK = 0x891b

def _ifinfo(sock, addr, ifname):
    iface = struct.pack('256s', ifname[:15])
    info  = fcntl.ioctl(sock.fileno(), addr, iface)
    return socket.inet_ntoa(info[20:24])

def all_interfaces():
    if platform.machine() == "armv7l": size = 32
    else:                              size = 40
    
    bytes = 8 * size
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    names = array.array('B', '\0' * bytes)
    outbytes = struct.unpack('iL', fcntl.ioctl(
        s.fileno(), SIOCGIFCONF,
        struct.pack('iL', bytes, names.buffer_info()[0])
    ))[0]
    namestr = names.tostring()

    # get additional info for all interfaces found
    lst = []
    for i in range(0, outbytes, size):
        name = namestr[i:i+16].split('\0', 1)[0]
        if name != "":
            addr = _ifinfo(s, SIOCGIFADDR, name)
            mask = _ifinfo(s, SIOCGIFNETMASK, name)
            lst.append((name, addr, mask))
    return lst

class FtcGuiApplication(QApplication):
    def __init__(self, args):
        global ifs

        QApplication.__init__(self, args)
        # load stylesheet from the same place the script was loaded from
        with open(base + "txt.qss","r") as fh:
            self.setStyleSheet(fh.read())
            fh.close()

        self.w = TxtWindow(base,"NetInfo")

        ifs = all_interfaces()

        self.nets_w = QComboBox()
        self.nets_w.activated[str].connect(self.set_net)
        for i in ifs:
            self.nets_w.addItem(i[0])

        self.w.addWidget(self.nets_w)

        self.w.addStretch()

        self.ip_lbl = QLabel("Address:")
        self.ip_lbl.setAlignment(Qt.AlignCenter)
        self.w.addWidget(self.ip_lbl)

        self.ip = QLabel("")
        self.ip.setObjectName("smalllabel")
        self.ip.setAlignment(Qt.AlignCenter)
        self.w.addWidget(self.ip)
   
        self.mask_lbl = QLabel("Netmask:")
        self.mask_lbl.setAlignment(Qt.AlignCenter)
        self.w.addWidget(self.mask_lbl)

        self.mask = QLabel("")
        self.mask.setObjectName("smalllabel")
        self.mask.setAlignment(Qt.AlignCenter)
        self.w.addWidget(self.mask)

        self.set_net(ifs[0][0])
   
        self.w.addStretch()

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
